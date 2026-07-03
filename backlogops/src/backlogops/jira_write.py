#! /usr/local/bin/python3
"""Add backlog items to Jira from an internal backlog.

:func:`add_backlog_to_jira` creates one Jira issue per backlog item that
is not already present. Before creating anything it checks every item's
issue type is valid in the project (raising when one is not) and looks up
every item's key in Jira; in ``RAISE`` mode it raises before creating
anything when a key already exists, and in ``SKIP`` mode it leaves the
already-present items alone. Sub-tasks are created last, after their
parents exist, and each sub-task is created with its parent issue key,
which Jira requires at create time; the parent key is the one Jira
assigned to a parent created in this run, or the item's parent key when
the parent already exists in Jira. An item whose creation Jira still
refuses is collected in the result's ``failed`` list with a concise
reason, and the remaining items are still added. The payload for each
new issue is built by
inverting the preset's write
backlog column map: a plain field such as the summary is set directly, a
nested field such as the issue type is wrapped by its path steps, a list
field such as the fix versions is wrapped as named objects, and a custom
field is set by its resolved field id. The issue type written for an item
comes from the preset's level-to-issue-type map (falling back to the
level name), so a Jira that renamed a type (such as a Swedish
``Deluppgift`` sub-task) still gets a valid issue type. The issue is
first created with the fields a create screen accepts (project, summary,
issue type) and the remaining fields are then set through an update,
because a create screen often omits fields such as the story points that
an edit screen accepts.

The item key is assigned by Jira, so it is not written; instead each
added item is copied and the copy carries the key Jira assigned. Once
every issue exists, the parent and dependency keys of the stored copies
are remapped from the internal keys to the assigned Jira keys, so the
returned backlog of stored items is internally consistent. The status of
a created issue is set by a workflow transition to a Jira status that
maps to the item's status, trying the matching transitions in turn; when
none succeeds the remaining mismatch is reported. A sub-task's parent is
set at create time as above. The argument backlog is never modified.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import copy
import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import NamedTuple, Optional, TextIO
from config_as_json import string_to_enum_best_match
from jira import JIRA, JIRAError
from backlogops.backlog import Backlog, BacklogItem, DEPENDENCY_FIELDS, Status
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType, \
    JiraColumnMap, JiraIssueTypeMap
from backlogops.jira_read import _coerce, _custom_ids, _field_id, _resolve
from backlogops.levels import DEFAULT_LEVELS, Levels, level_name

_SKIP_WRITE_FIELDS = frozenset({'key', 'status', 'parent_key'}) | \
    frozenset(DEPENDENCY_FIELDS)
"""Internal fields not set from the column map when creating an issue.

The key is assigned by Jira, the status needs a workflow transition, and
the parent and dependency links are updated in a later batch. A
sub-task's parent is the exception: it is set at create time by a
dedicated path, because Jira requires it, not from the column map.
"""

_JIRA_LIST_FIELDS = frozenset({'fixVersions', 'versions', 'components'})
"""Jira issue fields whose create value is a list of named objects."""

_CREATE_FIELD_NAMES = frozenset({'project', 'summary', 'issuetype', 'parent'})
"""Jira fields set while creating an issue; the rest are set by an update.

A Jira create screen often omits fields such as the story points, the
team or the fix versions, so those are set through an update once the
issue exists, where the edit screen usually accepts them. The ``parent``
of a sub-task is set here because Jira requires it at create time.
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


class ItemNotInJiraError(RuntimeError):
    """Raised when an item to update is not present in Jira.

    It carries the sorted identifiers that are missing (release names or
    backlog keys) so a caller can report them, and a noun naming what they
    are. It derives from :class:`RuntimeError`, so a handler that catches
    ``RuntimeError`` still catches it. It is shared by the release-update
    and backlog-update paths.
    """

    def __init__(self, names: list[str], noun: str = 'Items') -> None:
        """Store the missing identifiers and build the message."""
        self.names = names
        super().__init__(f'{noun} not present in Jira: '
                         + ', '.join(names) + '.')


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


class OnMissingKey(Enum):
    """What to do when an item to update is not present in Jira."""

    RAISE = auto()
    IGNORE = auto()
    ADD = auto()


class FailedItem(NamedTuple):
    """A backlog item that could not be added, with the failure reason."""

    item: BacklogItem
    reason: str


class StatusMismatch(NamedTuple):
    """A created issue whose Jira status could not be matched.

    Fields:
        item: The stored copy of the item, carrying its new Jira key.
        expected: The internal status the item carries.
        actual: The Jira status name the created issue ended up in, or
            None when the status could not be read.
    """

    item: BacklogItem
    expected: Status
    actual: Optional[str]


class AddedToJira(NamedTuple):
    """The result of adding a backlog to Jira.

    Fields:
        stored: Copies of the added items, each carrying the key Jira
            assigned to the created issue, with parent and dependency
            keys remapped to the assigned Jira keys.
        already_present: Copies of the items whose key already existed in
            Jira and were therefore not added, with their original key.
        failed: Items whose creation Jira refused, each with a concise
            reason; the argument backlog is not changed by a failure.
        key_map: For each stored item, its original key mapped to the key
            Jira assigned.
        status_mismatch: The stored items whose created issue could not be
            transitioned to a Jira status matching the item's status.
    """

    stored: Backlog
    already_present: Backlog
    failed: list[FailedItem]
    key_map: dict[str, str]
    status_mismatch: list[StatusMismatch]


@dataclass(frozen=True)
class _TypeInfo:
    """The level and issue-type resolution used when creating issues.

    ``subtask_types`` holds the Jira issue type names that are sub-tasks,
    or None when the create metadata did not reveal them, in which case a
    sub-task is detected by the lowest configured level instead.
    """

    levels: Levels
    issue_type_map: JiraIssueTypeMap
    subtask_types: Optional[frozenset[str]]


@dataclass(frozen=True)
class _WriteContext:
    """The resolved Jira target and mapping for creating issues.

    ``custom_ids`` maps a custom field display name to its id and
    ``custom_names`` is its inverse, used to report a skipped custom field
    by name. ``types`` resolves an item's level to its Jira issue type.
    ``status_map`` maps a Jira status name to an internal status when
    reconciling a created issue's status.
    """

    client: JIRA
    column_map: JiraColumnMap
    project: str
    custom_ids: dict[str, str]
    custom_names: dict[str, str]
    types: _TypeInfo
    status_map: Optional[dict[str, Status]]


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


def _issue_type(level: int, issue_type_map: JiraIssueTypeMap,
                levels: Levels) -> Optional[str]:
    """Return the Jira issue type to write for one internal level.

    The preset's level-to-issue-type map wins when it names the level;
    otherwise the level's own name is used, as before.
    """
    mapped = issue_type_map.get(level)
    if mapped is not None:
        return mapped
    return level_name(level, levels)


def _internal_value(name: str, item: BacklogItem, levels: Levels,
                    issue_type_map: JiraIssueTypeMap) -> object:
    """Return the value to write for one internal field, or None."""
    if name == 'level':
        return _issue_type(item.level, issue_type_map, levels)
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
        value = _internal_value(name, item, ctx.types.levels,
                                ctx.types.issue_type_map)
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


def _types_from_dicts(items: object) -> dict[str, bool]:
    """Return each issue type ``name`` mapped to its ``subtask`` flag."""
    result: dict[str, bool] = {}
    if isinstance(items, list):
        for item in items:
            name = item.get('name') if isinstance(item, dict) else None
            if isinstance(name, str):
                result[name] = bool(item.get('subtask'))
    return result


def _types_from_issuetypes(client: JIRA, project: str) -> dict[str, bool]:
    """Return issue type name to subtask flag via the issuetypes API."""
    meta = client.createmeta_issuetypes(project)
    values = meta.get('values', []) if isinstance(meta, dict) else []
    return _types_from_dicts(values)


def _types_from_createmeta(client: JIRA, project: str) -> dict[str, bool]:
    """Return issue type name to subtask flag via the older createmeta API."""
    meta = client.createmeta(projectKeys=project, expand='projects.issuetypes')
    projects = meta.get('projects', []) if isinstance(meta, dict) else []
    result: dict[str, bool] = {}
    for proj in projects:
        if isinstance(proj, dict):
            result.update(_types_from_dicts(proj.get('issuetypes', [])))
    return result


def _issue_type_meta(client: JIRA, project: str) -> dict[str, bool]:
    """Return the project's creatable issue types with subtask flags.

    Each creatable issue type name is mapped to whether Jira marks it a
    sub-task. Different Jira versions expose the create metadata through
    different endpoints and reject the other, so both are tried; when
    neither works the result is empty, issue-type validation is skipped
    and sub-task detection falls back to the lowest configured level.
    """
    for reader in (_types_from_issuetypes, _types_from_createmeta):
        try:
            types = reader(client, project)
        except JIRAError:
            continue
        if types:
            return types
    return {}


def _subtask_types(type_meta: dict[str, bool]) -> Optional[frozenset[str]]:
    """Return the sub-task issue type names, or None when unknown.

    None means the create metadata was unavailable, so the caller detects
    a sub-task by the lowest configured level instead.
    """
    if not type_meta:
        return None
    return frozenset(name for name, subtask in type_meta.items() if subtask)


def _validate_issue_types(valid: set[str], backlog: Backlog, levels: Levels,
                          issue_type_map: JiraIssueTypeMap) -> None:
    """Raise when an item's issue type is not valid in the project.

    The issue type written for each item is resolved through the preset's
    level-to-issue-type map, falling back to the level name. The valid
    type names come from the project's create metadata. When that is
    empty (an unexpected response), the check is skipped and each issue
    type is left to fail at create time instead.
    """
    if not valid:
        return
    bad: dict[str, list[str]] = {}
    for item in backlog:
        name = _issue_type(item.level, issue_type_map, levels) \
            or f'level {item.level}'
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


def _is_subtask(item: BacklogItem, ctx: _WriteContext) -> bool:
    """Return whether the item is created as a Jira sub-task.

    The create metadata decides it when the sub-task type names are known;
    otherwise the lowest configured level is treated as the sub-task
    level, matching the default levels where level 0 is the sub-task.
    """
    types = ctx.types
    if types.subtask_types is None:
        return bool(types.levels) and item.level == min(types.levels)
    name = _issue_type(item.level, types.issue_type_map, types.levels)
    return name is not None and name in types.subtask_types


def _subtask_parent(item: BacklogItem, ctx: _WriteContext,
                    key_map: dict[str, str]) -> Optional[str]:
    """Return the Jira parent key to set for a sub-task, or None.

    A sub-task's parent must exist in Jira before it is created, so the
    parent's Jira key is taken from the keys assigned in this run, falling
    back to the item's parent key when the parent already exists in Jira.
    A non-sub-task, or a sub-task without a parent, gets None.
    """
    if not _is_subtask(item, ctx) or item.parent_key is None:
        return None
    return key_map.get(item.parent_key, item.parent_key)


def _subtasks_last(ctx: _WriteContext, backlog: Backlog) -> Backlog:
    """Return the backlog reordered with sub-tasks after non-sub-tasks.

    A sub-task's parent must already exist in Jira, so every non-sub-task
    is created first; the original order within each group is kept.
    """
    non_sub: Backlog = []
    sub: Backlog = []
    for item in backlog:
        (sub if _is_subtask(item, ctx) else non_sub).append(item)
    return non_sub + sub


def _create_issue(ctx: _WriteContext, item: BacklogItem,
                  parent_key: Optional[str]) -> tuple[str, list[str], object]:
    """Create the issue and set the fields its edit screen offers.

    The issue is created with the create-screen fields, then the remaining
    mapped fields are set through an update, limited to the fields the
    issue's edit screen offers. Mapped fields the edit screen does not
    offer (such as story points on an issue type without them) are
    returned as skipped so the caller can report them. A sub-task's
    ``parent_key`` is set at create time, which Jira requires. The created
    issue object is returned too, so its status can be reconciled.
    """
    fields = _create_fields(ctx, item)
    if parent_key is not None:
        fields['parent'] = {'key': parent_key}
    create = {name: value for name, value in fields.items()
              if name in _CREATE_FIELD_NAMES}
    update = {name: value for name, value in fields.items()
              if name not in _CREATE_FIELD_NAMES}
    issue = ctx.client.create_issue(fields=create)
    new_key = _issue_key(issue)
    if not update:
        return new_key, [], issue
    editable = _editable_field_ids(ctx.client, new_key)
    allowed = {name: value for name, value in update.items()
               if name in editable}
    if allowed:
        issue.update(fields=allowed)
    return new_key, sorted(set(update) - editable), issue


def _skipped_names(skipped: list[str], custom_names: dict[str, str]) -> str:
    """Return the skipped field ids, each with its display name if custom."""
    return ', '.join(f'{field_id} ({custom_names[field_id]})'
                     if field_id in custom_names else field_id
                     for field_id in skipped)


def _report_skipped(orig_key: str, new_key: str, skipped: list[str],
                    custom_names: dict[str, str], stderr_file: TextIO) -> None:
    """Report mapped fields the issue's edit screen did not offer.

    A custom field also shows its display name, so a bare field id such as
    ``customfield_10016`` is reported as ``customfield_10016 (Story point
    estimate)``. A plain field, which has no separate display name, is
    reported by its field name alone.
    """
    names = _skipped_names(skipped, custom_names)
    print(f'WARNING: {new_key} (added from {orig_key}) has no edit-screen '
          f'field for {names}; those values were not set.', file=stderr_file)


def _jira_reason(error: JIRAError) -> str:
    """Return a concise reason from a Jira error, not the full dump."""
    status = getattr(error, 'status_code', None)
    text = getattr(error, 'text', None) or 'Jira rejected the request'
    return f'HTTP {status}: {text}' if status else str(text)


def _remap_refs(item: BacklogItem, key_map: dict[str, str]) -> None:
    """Remap the item's parent and dependency keys via the key map.

    A key present in ``key_map`` is replaced by its assigned Jira key; a
    key not in the map is left unchanged, because it already refers to an
    issue in Jira or to an item outside this write.
    """
    if item.parent_key is not None:
        item.parent_key = key_map.get(item.parent_key, item.parent_key)
    for dep_field in DEPENDENCY_FIELDS:
        deps = getattr(item, dep_field)
        setattr(item, dep_field, [key_map.get(dep, dep) for dep in deps])


def _status_from_name(name: str, status_map: Optional[dict[str, Status]]
                      ) -> Optional[Status]:
    """Return the internal status a Jira status name maps to, or None.

    A configured ``status_map`` is matched case-insensitively first, as
    when reading; otherwise the built-in status-name matching is used. A
    name that matches neither returns None.
    """
    if status_map:
        lookup = {key.lower(): value for key, value in status_map.items()}
        mapped = lookup.get(name.lower())
        if mapped is not None:
            return mapped
    try:
        result = string_to_enum_best_match(name, Status)
    except KeyError:
        return None
    assert isinstance(result, Status)
    return result


def _maps_to(name: Optional[str], target: Status,
             status_map: Optional[dict[str, Status]]) -> bool:
    """Return whether a Jira status name maps to the target status."""
    return name is not None and _status_from_name(name, status_map) is target


def _jira_status_name(ctx: _WriteContext, issue: object) -> Optional[str]:
    """Return the created issue's Jira status name via the column map."""
    field_root = getattr(issue, 'fields', None)
    for attr in ctx.column_map.get('status', ()):
        value = _coerce(_resolve(issue, field_root, attr, ctx.custom_ids))
        if isinstance(value, str) and value:
            return value
    return None


def _transition_target(trans: dict[str, object]) -> Optional[str]:
    """Return the target status name of a workflow transition, or None."""
    to_field = trans.get('to')
    if isinstance(to_field, dict):
        name = to_field.get('name')
        if isinstance(name, str):
            return name
    return None


def _available_transitions(client: JIRA,
                           issue: object) -> list[dict[str, object]]:
    """Return the issue's available workflow transitions, or empty."""
    try:
        transitions = client.transitions(issue)
    except JIRAError:
        return []
    return transitions if isinstance(transitions, list) else []


def _matching_transitions(ctx: _WriteContext, target: Status,
                          issue: object) -> list[str]:
    """Return ids of transitions whose target maps to the target status."""
    result: list[str] = []
    for trans in _available_transitions(ctx.client, issue):
        trans_id = trans.get('id')
        if isinstance(trans_id, str) and _maps_to(_transition_target(trans),
                                                  target, ctx.status_map):
            result.append(trans_id)
    return result


def _try_transitions(ctx: _WriteContext, target: Status,
                     issue: object) -> bool:
    """Transition the issue to a matching status; True on the first success.

    A direct transition to the target status is assumed to reach it, so
    the first transition that Jira accepts is treated as a success.
    """
    for trans_id in _matching_transitions(ctx, target, issue):
        try:
            ctx.client.transition_issue(issue, trans_id)
            return True
        except JIRAError:
            continue
    return False


def _report_status_mismatch(bad: StatusMismatch, stderr_file: TextIO) -> None:
    """Warn that a created issue's status could not be matched."""
    print(f'WARNING: {bad.item.key} ({bad.item.title}) is {bad.actual!r} in '
          f'Jira, not a status matching {bad.expected.name}; transition it '
          'manually.', file=stderr_file)


def _reconcile_status(ctx: _WriteContext, item: BacklogItem, issue: object,
                      stderr_file: TextIO) -> Optional[StatusMismatch]:
    """Match the created issue's status to the item, or report a mismatch.

    When the created issue's status already maps to the item's status
    nothing is done. Otherwise a workflow transition to a matching status
    is attempted; if none succeeds the mismatch is reported and returned.
    """
    name = _jira_status_name(ctx, issue)
    if _maps_to(name, item.status, ctx.status_map):
        return None
    if _try_transitions(ctx, item.status, issue):
        return None
    bad = StatusMismatch(item, item.status, name)
    _report_status_mismatch(bad, stderr_file)
    return bad


@dataclass
class _Added:
    """Mutable accumulator of the add-to-Jira results being built."""

    stored: Backlog
    already: Backlog
    failed: list[FailedItem]
    mismatch: list[StatusMismatch]
    key_map: dict[str, str]


def _add_item(ctx: _WriteContext, item: BacklogItem, existing: set[str],
              acc: _Added, stderr_file: TextIO) -> None:
    """Create one not-yet-present item and record it in the accumulator.

    An already-present item is copied into ``already``. A refused create is
    recorded in ``failed``. A created item is copied with its Jira key,
    recorded in ``stored`` and ``key_map``, and its status is reconciled.
    """
    if item.key in existing:
        acc.already.append(copy.deepcopy(item))
        return
    try:
        parent = _subtask_parent(item, ctx, acc.key_map)
        new_key, skipped, issue = _create_issue(ctx, item, parent)
    except JIRAError as error:
        acc.failed.append(FailedItem(copy.deepcopy(item), _jira_reason(error)))
        return
    if skipped:
        _report_skipped(item.key, new_key, skipped, ctx.custom_names,
                        stderr_file)
    stored_item = _stored_copy(item, new_key)
    acc.stored.append(stored_item)
    acc.key_map[item.key] = new_key
    bad = _reconcile_status(ctx, stored_item, issue, stderr_file)
    if bad is not None:
        acc.mismatch.append(bad)


def _write_new_items(ctx: _WriteContext, backlog: Backlog, existing: set[str],
                     stderr_file: TextIO) -> AddedToJira:
    """Create the not-yet-present items, reporting the ones that fail.

    Sub-tasks are created last, after their parents exist, and each is
    created with its parent key. Once every issue exists, each stored
    copy's parent and dependency keys are remapped to the assigned Jira
    keys, so the returned backlog of stored items is internally consistent.
    """
    acc = _Added([], [], [], [], {})
    for item in _subtasks_last(ctx, backlog):
        _add_item(ctx, item, existing, acc, stderr_file)
    for stored_item in acc.stored:
        _remap_refs(stored_item, acc.key_map)
    return AddedToJira(acc.stored, acc.already, acc.failed, acc.key_map,
                       acc.mismatch)


# pylint: disable-next=too-many-arguments
def add_backlog_to_jira(connections: JiraConnections, preset_name: str,
                        backlog: Backlog, *, on_existing_key: OnExistingKey,
                        levels: Optional[Levels] = None,
                        status_map: Optional[dict[str, Status]] = None,
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
    Sub-tasks are created last, after their parents exist, and each is
    created with its parent issue key. An item whose creation Jira refuses
    is collected in ``failed`` with a concise reason, and the other items
    are still added. Once every issue exists, each stored copy's parent
    and dependency keys are remapped to the assigned Jira keys, and each
    created issue is transitioned to a Jira status matching the item's
    status; an issue that cannot be matched is collected in
    ``status_mismatch``. The argument backlog is never modified.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset, connection and backlog column map.
        preset_name: The name of the Jira preset to use.
        backlog: The backlog items to add. Not modified.
        on_existing_key: Whether to raise or skip when a key already
            exists in Jira.
        levels: The levels used to resolve the issue type from the item
            level, or None for the default levels.
        status_map: Extra Jira status names mapped to internal statuses,
            used to reconcile a created issue's status, or None for the
            built-in status-name matching only.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The stored items with their Jira keys and remapped references, the
        already-present items, the items whose creation failed with a
        reason, the map from each stored item's original key to its Jira
        key, and the created issues whose status could not be matched.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        UnknownIssueTypeError: If an item's issue type is not valid in the
            project.
        ExistsInJiraError: In ``RAISE`` mode, if any key already exists in
            Jira.
    """
    ctx, valid_types = _build_ctx(connections, preset_name, levels, status_map)
    _validate_issue_types(valid_types, backlog, ctx.types.levels,
                          ctx.types.issue_type_map)
    existing = _existing_keys(ctx.client, backlog)
    if on_existing_key is OnExistingKey.RAISE and existing:
        _raise_existing(existing, stderr_file)
    return _write_new_items(ctx, backlog, existing, stderr_file)


def _build_ctx(connections: JiraConnections, preset_name: str,
               levels: Optional[Levels],
               status_map: Optional[dict[str, Status]]
               ) -> tuple[_WriteContext, set[str]]:
    """Return the write context and the project's valid issue-type names.

    The preset names the connection, the backlog write map, the default
    project and an optional level-to-issue-type map, all looked up in the
    pool's configuration. The valid issue-type names come from the
    project's create metadata and are used to validate the items before
    anything is created.
    """
    jira_config = connections.jira_config
    preset = jira_config.get_preset(preset_name)
    client = connections.client(preset.connection_name)
    column_map = jira_config.backlog_column_maps[
        preset.write_backlog_map_name()]
    issue_type_map: JiraIssueTypeMap = jira_config.issue_type_maps.get(
        preset.issue_type_map_name, {})
    type_meta = _issue_type_meta(client, preset.def_project)
    custom_ids = _custom_ids(client.fields())
    custom_names = {field_id: name for name, field_id in custom_ids.items()}
    types = _TypeInfo(DEFAULT_LEVELS if levels is None else levels,
                      issue_type_map, _subtask_types(type_meta))
    ctx = _WriteContext(client=client, column_map=column_map,
                        project=preset.def_project, custom_ids=custom_ids,
                        custom_names=custom_names, types=types,
                        status_map=status_map)
    return ctx, set(type_meta)


def _labeled_lines(heading: str, count: int, body: list[str]) -> list[str]:
    """Return a heading with its count then the body, or a (none) line.

    An empty body becomes a single ``  (none)`` line, so every section
    shows either its items or that it has none. This is shared by the
    add-backlog and add-releases result listings.
    """
    return [f'{heading} ({count}):', *(body or ['  (none)'])]


def _result_section(heading: str, backlog: Backlog) -> list[str]:
    """Return the heading and the key-and-title lines for one backlog."""
    return _labeled_lines(heading, len(backlog),
                          [f'  {item.key}  {item.title}' for item in backlog])


def format_add_result(result: AddedToJira) -> str:
    """Return a listing of the added, present, failed and unmatched items.

    Each section has a heading with its count, then one ``key  title`` line
    per item, or a ``(none)`` line when the section is empty. The CLI
    prints this text and the GUI shows it in a copy-pasteable pop-up.
    """
    lines = _result_section('Added to Jira', result.stored)
    lines.append('')
    lines.extend(_result_section('Already in Jira', result.already_present))
    lines.append('')
    lines.extend(_failed_section('Failed to add', result.failed))
    lines.append('')
    lines.extend(_status_section('Status not set in Jira',
                                 result.status_mismatch))
    return '\n'.join(lines)


def _failed_section(heading: str, failed: list[FailedItem]) -> list[str]:
    """Return the heading and the key, title and reason of each failure."""
    body = [f'  {entry.item.key}  {entry.item.title}  - {entry.reason}'
            for entry in failed]
    return _labeled_lines(heading, len(failed), body)


def _status_section(heading: str, mismatch: list[StatusMismatch]) -> list[str]:
    """Return the heading and the key, title and status of each mismatch."""
    body = [f'  {bad.item.key}  {bad.item.title}  - expected '
            f'{bad.expected.name}, Jira status {bad.actual!r}'
            for bad in mismatch]
    return _labeled_lines(heading, len(mismatch), body)


def apply_jira_keys(backlog: Backlog, key_map: dict[str, str]) -> None:
    """Rekey each backlog item in place using the original-to-Jira map.

    Every item's own key, parent key and dependency keys are remapped: a
    key present in ``key_map`` gets its mapped Jira key, a key not in the
    map is left unchanged, and the order is preserved. This keeps a shown
    backlog consistent with the stored copies the add returns.
    """
    for item in backlog:
        item.key = key_map.get(item.key, item.key)
        _remap_refs(item, key_map)


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
