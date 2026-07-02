#! /usr/local/bin/python3
"""Add backlog items to Jira from an internal backlog.

:func:`add_backlog_to_jira` creates one Jira issue per backlog item that
is not already present. It first looks up every item's key in Jira; in
``RAISE`` mode it raises before creating anything when a key already
exists, and in ``SKIP`` mode it leaves the already-present items alone.
The create payload for each new issue is built by inverting the write
preset's backlog column map: a plain field such as the summary is set
directly, a nested field such as the issue type is wrapped by its path
steps, a list field such as the fix versions is wrapped as named objects,
and a custom field is set by its resolved field id.

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


class OnExistingKey(Enum):
    """What to do when a backlog item's key already exists in Jira."""

    RAISE = auto()
    SKIP = auto()


class AddedToJira(NamedTuple):
    """The result of adding a backlog to Jira.

    Fields:
        stored: Copies of the added items, each carrying the key Jira
            assigned to the created issue.
        already_present: Copies of the items whose key already existed in
            Jira and were therefore not added, with their original key.
        key_map: For each stored item, its original key mapped to the key
            Jira assigned. Used later to update parent and dependency keys.
    """

    stored: Backlog
    already_present: Backlog
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


def _write_new_items(ctx: _WriteContext, backlog: Backlog,
                     existing: set[str]) -> AddedToJira:
    """Create every not-yet-present item and collect the two backlogs."""
    stored: Backlog = []
    already: Backlog = []
    key_map: dict[str, str] = {}
    for item in backlog:
        if item.key in existing:
            already.append(copy.deepcopy(item))
            continue
        issue = ctx.client.create_issue(fields=_create_fields(ctx, item))
        new_key = _issue_key(issue)
        stored.append(_stored_copy(item, new_key))
        key_map[item.key] = new_key
    return AddedToJira(stored, already, key_map)


# pylint: disable-next=too-many-arguments
def add_backlog_to_jira(connections: JiraConnections, preset_name: str,
                        backlog: Backlog, *, on_existing_key: OnExistingKey,
                        levels: Optional[Levels] = None,
                        stderr_file: TextIO = sys.stderr) -> AddedToJira:
    """Add the backlog items to Jira, one created issue per new item.

    Every item's key is first looked up in Jira. In ``RAISE`` mode, if any
    key already exists the function raises before creating anything. In
    ``SKIP`` mode the already-present items are left untouched. Each added
    item is created from the write preset's backlog column map and default
    project, and a copy of it carrying the key Jira assigned is collected.
    The argument backlog is never modified.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the write preset, connection and backlog column map.
        preset_name: The name of the to-Jira write preset to use.
        backlog: The backlog items to add. Not modified.
        on_existing_key: Whether to raise or skip when a key already
            exists in Jira.
        levels: The levels used to resolve the issue type from the item
            level, or None for the default levels.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The stored items with their Jira keys, the already-present items,
        and the map from each stored item's original key to its Jira key.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        ExistsInJiraError: In ``RAISE`` mode, if any key already exists in
            Jira.
    """
    jira_config = connections.jira_config
    preset = jira_config.get_write_preset(preset_name)
    client = connections.client(preset.connection_name)
    column_map = jira_config.backlog_column_maps[
        preset.backlog_column_map_name]
    ctx = _WriteContext(client=client, column_map=column_map,
                        project=preset.def_project,
                        custom_ids=_custom_ids(client.fields()),
                        levels=DEFAULT_LEVELS if levels is None else levels)
    existing = _existing_keys(client, backlog)
    if on_existing_key is OnExistingKey.RAISE and existing:
        _raise_existing(existing, stderr_file)
    return _write_new_items(ctx, backlog, existing)


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
    return '\n'.join(lines)


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
