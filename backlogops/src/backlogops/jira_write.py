#! /usr/local/bin/python3
"""Add backlog items to Jira from an internal backlog.

:func:`add_backlog_to_jira` creates one Jira issue per backlog item that
is not already present. Before creating anything it checks every item's
issue type is valid in the project (raising when one is not) and looks up
every item's key in Jira; in ``RAISE`` mode it raises before creating
anything when a key already exists, and in ``SKIP`` mode it leaves the
already-present items alone. An item whose creation Jira refuses (such as
a sub-task, which needs a parent that is not written yet) is collected in
the result's ``failed`` list with a concise reason, and the remaining
items are still added. The payload for each new issue is built by
inverting the preset's write
backlog column map: a plain field such as the summary is set directly, a
nested field such as the issue type is wrapped by its path steps, a list
field such as the fix versions is wrapped as named objects, and a custom
field is set by its resolved field id. The issue is first created with
the fields a create screen accepts (project, summary, issue type) and the
remaining fields are then set through an update, because a create screen
often omits fields such as the story points that an edit screen accepts.

The item key is assigned by Jira, the status needs a workflow transition,
and the parent and dependency links are updated in a later batch, so
those fields are not written here. The argument backlog is never modified;
each added item is copied and the copy carries the key Jira assigned.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import copy
import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import NamedTuple, Optional, TextIO
from jira import JIRA, JIRAError
from backlogops.backlog import Backlog, BacklogItem, DEPENDENCY_FIELDS
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType, JiraColumnMap
from backlogops.jira_read import _custom_ids, _field_id
from backlogops.levels import DEFAULT_LEVELS, Levels, level_name

_SKIP_WRITE_FIELDS = frozenset({'key', 'status', 'parent_key'}) | \
    frozenset(DEPENDENCY_FIELDS)
"""Internal fields not written when creating an issue in this batch.

The key is assigned by Jira, the status needs a workflow transition, and
the parent and dependency links are updated in a later batch.
"""

_JIRA_LIST_FIELDS = frozenset({'fixVersions', 'versions', 'components'})
"""Jira issue fields whose create value is a list of named objects."""

_CREATE_FIELD_NAMES = frozenset({'project', 'summary', 'issuetype'})
"""Jira fields set while creating an issue; the rest are set by an update.

A Jira create screen often omits fields such as the story points, the
team or the fix versions, so those are set through an update once the
issue exists, where the edit screen usually accepts them.
"""


class ExistsInJiraError(ValueError):
    """Raised when a backlog key to add already exists in Jira.

    It carries the sorted keys that already exist, so a caller can report
    them. It derives from :class:`ValueError`, so a handler that catches
    ``ValueError`` still catches it.
    """

    def __init__(self, keys: list[str]) -> None:
        """Store the already-present keys and build the message."""
        self.keys = keys
        super().__init__(
            'Backlog keys already exist in Jira: ' + ', '.join(keys) + '.')


class UnknownIssueTypeError(ValueError):
    """Raised when a backlog item's issue type is not valid in the project.

    It carries the invalid issue type names mapped to the item keys that
    use them, and the sorted valid type names, so a caller can report
    them. It derives from :class:`ValueError`.
    """

    def __init__(self, bad: dict[str, list[str]], valid: list[str]) -> None:
        """Store the bad and valid type names and build the message."""
        self.bad = bad
        self.valid = valid
        parts = '; '.join(f'{name!r} (for {", ".join(keys)})'
                          for name, keys in sorted(bad.items()))
        super().__init__(f'Invalid Jira issue type(s): {parts}. Valid '
                         f'types: {", ".join(valid)}.')


class OnExistingKey(Enum):
    """What to do when a backlog item's key already exists in Jira."""

    RAISE = auto()
    SKIP = auto()


class FailedItem(NamedTuple):
    """A backlog item that could not be added, with the failure reason."""

    item: BacklogItem
    reason: str


class AddedToJira(NamedTuple):
    """The result of adding a backlog to Jira.

    Fields:
        stored: Copies of the added items, each carrying the key Jira
            assigned to the created issue.
        already_present: Copies of the items whose key already existed in
            Jira and were therefore not added, with their original key.
        failed: Items whose creation Jira refused, each with a concise
            reason; the argument backlog is not changed by a failure.
        key_map: For each stored item, its original key mapped to the key
            Jira assigned. Used later to update parent and dependency keys.
    """

    stored: Backlog
    already_present: Backlog
    failed: list[FailedItem]
    key_map: dict[str, str]


@dataclass(frozen=True)
class _WriteContext:
    """The resolved Jira target and mapping for creating issues."""

    client: JIRA
    column_map: JiraColumnMap
    project: str
    custom_ids: dict[str, str]
    levels: Levels


def _nest(path: tuple[str, ...], value: object) -> dict[str, object]:
    """Return ``value`` wrapped in nested dicts named by the path steps."""
    result: object = value
    for step in reversed(path):
        result = {step: result}
    assert isinstance(result, dict)
    return result


def _field_payload(path: tuple[str, ...], value: object) -> dict[str, object]:
    """Return the create-fields entry for a plain or list issue field."""
    if path[0] in _JIRA_LIST_FIELDS:
        inner = _nest(path[1:], value) if len(path) > 1 else {'name': value}
        return {path[0]: [inner]}
    return _nest(path, value)


def _place_value(fields: dict[str, object], attr: JiraAttrPath, value: object,
                 custom_ids: dict[str, str]) -> None:
    """Place one field value into the Jira create-fields dict by kind."""
    if attr.kind is JiraAttrType.CUSTOM_FIELD:
        field_id = _field_id(attr.path[0], custom_ids)
        if field_id is not None:
            fields[field_id] = value
    elif attr.kind is JiraAttrType.FIELD:
        fields.update(_field_payload(attr.path, value))


def _internal_value(name: str, item: BacklogItem, levels: Levels) -> object:
    """Return the value to write for one internal field, or None."""
    if name == 'level':
        return level_name(item.level, levels)
    try:
        return item[name]
    except KeyError:
        return None


def _create_fields(ctx: _WriteContext, item: BacklogItem) -> dict[str, object]:
    """Build the Jira create-issue fields for one backlog item."""
    fields: dict[str, object] = {'project': {'key': ctx.project}}
    for name, attrs in ctx.column_map.items():
        if name in _SKIP_WRITE_FIELDS or not attrs:
            continue
        value = _internal_value(name, item, ctx.levels)
        if value not in (None, ''):
            _place_value(fields, attrs[0], value, ctx.custom_ids)
    return fields


def _issue_exists(client: JIRA, key: str) -> bool:
    """Return whether an issue with this key exists in Jira."""
    try:
        client.issue(key)
        return True
    except JIRAError:
        return False


def _existing_keys(client: JIRA, backlog: Backlog) -> set[str]:
    """Return the backlog item keys that already exist in Jira."""
    return {item.key for item in backlog if _issue_exists(client, item.key)}


def _raise_existing(existing: set[str], stderr_file: TextIO) -> None:
    """Report and raise for backlog keys that already exist in Jira."""
    error = ExistsInJiraError(sorted(existing))
    print(str(error), file=stderr_file)
    raise error


def _names_from_dicts(items: object) -> set[str]:
    """Return the string ``name`` values from a list of dicts."""
    names: set[str] = set()
    if isinstance(items, list):
        for item in items:
            name = item.get('name') if isinstance(item, dict) else None
            if isinstance(name, str):
                names.add(name)
    return names


def _types_from_issuetypes(client: JIRA, project: str) -> set[str]:
    """Return creatable issue type names via the createmeta issuetypes API."""
    meta = client.createmeta_issuetypes(project)
    values = meta.get('values', []) if isinstance(meta, dict) else []
    return _names_from_dicts(values)


def _types_from_createmeta(client: JIRA, project: str) -> set[str]:
    """Return creatable issue type names via the older createmeta API."""
    meta = client.createmeta(projectKeys=project, expand='projects.issuetypes')
    projects = meta.get('projects', []) if isinstance(meta, dict) else []
    names: set[str] = set()
    for proj in projects:
        if isinstance(proj, dict):
            names |= _names_from_dicts(proj.get('issuetypes', []))
    return names


def _valid_issue_types(client: JIRA, project: str) -> set[str]:
    """Return the project's creatable issue type names, best-effort.

    Different Jira versions expose the create metadata through different
    endpoints and reject the other, so both are tried; when neither works
    the result is empty and issue-type validation is skipped, leaving each
    issue type to be checked by Jira at create time instead.
    """
    for reader in (_types_from_issuetypes, _types_from_createmeta):
        try:
            names = reader(client, project)
        except JIRAError:
            continue
        if names:
            return names
    return set()


def _validate_issue_types(client: JIRA, project: str, backlog: Backlog,
                          levels: Levels) -> None:
    """Raise when an item's issue type is not valid in the project.

    The valid type names are read from the project's create metadata. When
    that returns nothing (an unexpected response), the check is skipped and
    each issue type is left to fail at create time instead.
    """
    valid = _valid_issue_types(client, project)
    if not valid:
        return
    bad: dict[str, list[str]] = {}
    for item in backlog:
        name = level_name(item.level, levels) or f'level {item.level}'
        if name not in valid:
            bad.setdefault(name, []).append(item.key)
    if bad:
        raise UnknownIssueTypeError(bad, sorted(valid))


def _issue_key(issue: object) -> str:
    """Return the key Jira assigned to a created issue."""
    key = getattr(issue, 'key', None)
    assert isinstance(key, str)
    return key


def _stored_copy(item: BacklogItem, new_key: str) -> BacklogItem:
    """Return a deep copy of the item carrying its new Jira key."""
    copied = copy.deepcopy(item)
    copied.key = new_key
    return copied


def _editable_field_ids(client: JIRA, issue_key: str) -> set[str]:
    """Return the field ids the issue's edit screen accepts."""
    meta = client.editmeta(issue_key)
    fields = meta.get('fields', {})
    return {str(name) for name in fields}


def _create_issue(ctx: _WriteContext,
                  item: BacklogItem) -> tuple[str, list[str]]:
    """Create the issue and set the fields its edit screen offers.

    The issue is created with the create-screen fields, then the remaining
    mapped fields are set through an update, limited to the fields the
    issue's edit screen offers. Mapped fields the edit screen does not
    offer (such as story points on an issue type without them) are
    returned as skipped so the caller can report them.
    """
    fields = _create_fields(ctx, item)
    create = {name: value for name, value in fields.items()
              if name in _CREATE_FIELD_NAMES}
    update = {name: value for name, value in fields.items()
              if name not in _CREATE_FIELD_NAMES}
    issue = ctx.client.create_issue(fields=create)
    new_key = _issue_key(issue)
    if not update:
        return new_key, []
    editable = _editable_field_ids(ctx.client, new_key)
    allowed = {name: value for name, value in update.items()
               if name in editable}
    if allowed:
        issue.update(fields=allowed)
    return new_key, sorted(set(update) - editable)


def _report_skipped(orig_key: str, new_key: str, skipped: list[str],
                    stderr_file: TextIO) -> None:
    """Report mapped fields the issue's edit screen did not offer."""
    names = ', '.join(skipped)
    print(f'WARNING: {new_key} (added from {orig_key}) has no edit-screen '
          f'field for {names}; those values were not set.', file=stderr_file)


def _jira_reason(error: JIRAError) -> str:
    """Return a concise reason from a Jira error, not the full dump."""
    status = getattr(error, 'status_code', None)
    text = getattr(error, 'text', None) or 'Jira rejected the request'
    return f'HTTP {status}: {text}' if status else str(text)


def _write_new_items(ctx: _WriteContext, backlog: Backlog, existing: set[str],
                     stderr_file: TextIO) -> AddedToJira:
    """Create the not-yet-present items, reporting the ones that fail."""
    stored: Backlog = []
    already: Backlog = []
    failed: list[FailedItem] = []
    key_map: dict[str, str] = {}
    for item in backlog:
        if item.key in existing:
            already.append(copy.deepcopy(item))
            continue
        try:
            new_key, skipped = _create_issue(ctx, item)
        except JIRAError as error:
            failed.append(FailedItem(copy.deepcopy(item), _jira_reason(error)))
            continue
        if skipped:
            _report_skipped(item.key, new_key, skipped, stderr_file)
        stored.append(_stored_copy(item, new_key))
        key_map[item.key] = new_key
    return AddedToJira(stored, already, failed, key_map)


# pylint: disable-next=too-many-arguments
def add_backlog_to_jira(connections: JiraConnections, preset_name: str,
                        backlog: Backlog, *, on_existing_key: OnExistingKey,
                        levels: Optional[Levels] = None,
                        stderr_file: TextIO = sys.stderr) -> AddedToJira:
    """Add the backlog items to Jira, one created issue per new item.

    Before creating anything the issue types are validated against the
    project and every item's key is looked up in Jira. In ``RAISE`` mode,
    if any key already exists the function raises before creating anything.
    In ``SKIP`` mode the already-present items are left untouched. Each
    added item is created from the preset's write backlog column map and
    default project, and a copy of it carrying the key Jira assigned is
    collected. Each issue is created with the fields a create screen
    accepts and the remaining mapped fields are then set through an update.
    An item whose creation Jira refuses is collected in ``failed`` with a
    concise reason, and the other items are still added. The argument
    backlog is never modified.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset, connection and backlog column map.
        preset_name: The name of the Jira preset to use.
        backlog: The backlog items to add. Not modified.
        on_existing_key: Whether to raise or skip when a key already
            exists in Jira.
        levels: The levels used to resolve the issue type from the item
            level, or None for the default levels.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The stored items with their Jira keys, the already-present items,
        the items whose creation failed with a reason, and the map from
        each stored item's original key to its Jira key.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        UnknownIssueTypeError: If an item's issue type is not valid in the
            project.
        ExistsInJiraError: In ``RAISE`` mode, if any key already exists in
            Jira.
    """
    jira_config = connections.jira_config
    preset = jira_config.get_preset(preset_name)
    client = connections.client(preset.connection_name)
    column_map = jira_config.backlog_column_maps[
        preset.write_backlog_map_name()]
    ctx = _WriteContext(client=client, column_map=column_map,
                        project=preset.def_project,
                        custom_ids=_custom_ids(client.fields()),
                        levels=DEFAULT_LEVELS if levels is None else levels)
    _validate_issue_types(client, ctx.project, backlog, ctx.levels)
    existing = _existing_keys(client, backlog)
    if on_existing_key is OnExistingKey.RAISE and existing:
        _raise_existing(existing, stderr_file)
    return _write_new_items(ctx, backlog, existing, stderr_file)


def _result_section(heading: str, backlog: Backlog) -> list[str]:
    """Return the heading and the key-and-title lines for one backlog."""
    lines = [f'{heading} ({len(backlog)}):']
    if not backlog:
        lines.append('  (none)')
    else:
        lines.extend(f'  {item.key}  {item.title}' for item in backlog)
    return lines


def format_add_result(result: AddedToJira) -> str:
    """Return a two-section listing of added and already-present items.

    Each section has a heading with its count, then one ``key  title`` line
    per item, or a ``(none)`` line when the section is empty. The CLI
    prints this text and the GUI shows it in a copy-pasteable pop-up.
    """
    lines = _result_section('Added to Jira', result.stored)
    lines.append('')
    lines.extend(_result_section('Already in Jira', result.already_present))
    lines.append('')
    lines.extend(_failed_section('Failed to add', result.failed))
    return '\n'.join(lines)


def _failed_section(heading: str, failed: list[FailedItem]) -> list[str]:
    """Return the heading and the key, title and reason of each failure."""
    lines = [f'{heading} ({len(failed)}):']
    if not failed:
        lines.append('  (none)')
    else:
        lines.extend(f'  {entry.item.key}  {entry.item.title}  - '
                     f'{entry.reason}' for entry in failed)
    return lines


def apply_jira_keys(backlog: Backlog, key_map: dict[str, str]) -> None:
    """Rekey each backlog item in place using the original-to-Jira map.

    An item whose key is a key of ``key_map`` gets that mapped Jira key; an
    item not in the map is left unchanged, and the order is preserved. Only
    the item key is changed; parent and dependency keys are updated in a
    later batch.
    """
    for item in backlog:
        new_key = key_map.get(item.key)
        if new_key is not None:
            item.key = new_key


def jira_custom_fields(connections: JiraConnections,
                       preset_name: str) -> list[tuple[str, str]]:
    """Return (field id, display name) pairs for the Jira custom fields.

    This is the map the reader uses internally to resolve a custom field
    named in a column map (such as 'Story point estimate') to its field
    id. Printing it confirms what a mapped name resolves to.
    """
    preset = connections.jira_config.get_preset(preset_name)
    client = connections.client(preset.connection_name)
    ids = _custom_ids(client.fields())
    return sorted((field_id, name) for name, field_id in ids.items())


def jira_editable_fields(connections: JiraConnections, preset_name: str,
                         issue_key: str) -> list[tuple[str, str]]:
    """Return (field id, display name) pairs an issue's edit screen offers.

    A field missing from the returned list is not on the issue's edit
    screen for its issue type, so it cannot be set through the issue edit
    REST endpoint. This explains why a mapped field is skipped on write.
    """
    preset = connections.jira_config.get_preset(preset_name)
    client = connections.client(preset.connection_name)
    meta = client.editmeta(issue_key)
    fields = meta.get('fields', {})
    return sorted((str(field_id), str(info.get('name', '')))
                  for field_id, info in fields.items())
