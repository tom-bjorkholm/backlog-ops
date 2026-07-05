#! /usr/local/bin/python3
"""Update backlog items in Jira from an internal backlog.

:func:`update_backlog_in_jira` changes each Jira issue whose key matches an
internal backlog item so that a chosen subset of its mapped fields matches
the item. Only the fields named in ``fields_to_update`` are touched; the
identity field ``key`` and the issue type (``level``) are never changed on
an existing issue. For each selected field the current Jira value is read
through the write column map and compared to the item's value, so only the
fields that actually differ are written; an item whose selected fields
already match is reported as already correct and its issue is not touched.
An empty internal value is left unset, so an empty value never clears a
Jira field.

The selected fields are written in the same way they are read: a settable
field (summary, description, story points, team, fix version) through an
issue update, the status through a workflow transition, the parent through
the mapped parent field, and each dependency through Jira issue links. How
links are reconciled is chosen by :class:`LinkUpdate`: ``ADD_MISSING``
only creates the links that are missing, while ``RECONCILE`` also removes
the Jira links (and clears the parent) that the backlog no longer has.

A backlog item whose key is not present in Jira is handled by the chosen
:class:`OnMissingKey` policy: ``RAISE`` raises :class:`ItemNotInJiraError`
before anything is changed, ``IGNORE`` leaves the missing item alone, and
``ADD`` creates it exactly as :func:`add_backlog_to_jira` would, writing
all of its mapped fields. When items are added their assigned Jira keys are
used to remap the parent and dependency keys of the updated items, so an
updated item that referred to a newly added item links to its Jira key. An
item whose update Jira refuses is collected in the result's ``failed`` list
with a concise reason, and the remaining items are still processed. The
argument backlog is never modified.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import copy
import sys
from dataclasses import dataclass
from enum import Enum, auto
from functools import partial
from typing import NamedTuple, Optional, TextIO
from jira import JIRA, Issue, JIRAError
from backlogops.backlog import Backlog, BacklogItem, Status
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType
from backlogops.jira_read import (
    _backlog_row, _coerce_all, _field_id, _filtered_values, _walk)
from backlogops.jira_write import (
    AddedToJira, FailedItem, ItemNotInJiraError, OnExistingKey, OnMissingKey,
    StatusMismatch, _WriteContext, _build_ctx, _editable_field_ids,
    _failed_section, _internal_value, _jira_reason, _jira_status_name,
    _link_section, _maps_to, _outcome_prefix, _report_status_mismatch,
    _result_section, _skipped_names, _status_section, _try_link,
    _try_transitions, add_backlog_to_jira)
from backlogops.jira_write_fields import (
    FailedLink, _LinkSpec, _dep_link_attrs, _parent_fields, _place_value)
from backlogops.levels import Levels

_IDENTITY_FIELDS = frozenset({'key', 'level'})
"""Mapped fields never changed on an issue already in Jira.

The key is the identity used to find the issue and the level maps to the
issue type, which is not changed on an existing issue. These are excluded
from the selectable fields and from any update.
"""

_LINK_FIELDS = frozenset({'parent_key', 'depends_on_f2s', 'depends_on_f2f',
                          'depends_on_s2s'})
"""Selected fields written as links rather than as issue fields."""

_SKIP_DATA = frozenset({'key', 'level', 'status'}) | _LINK_FIELDS
"""Fields not written by the settable-field diff (handled elsewhere)."""


class LinkUpdate(Enum):
    """How to reconcile an item's links when updating it in Jira.

    ``ADD_MISSING`` only creates the dependency links that are missing and
    sets a parent that is not set; existing Jira links are left alone.
    ``RECONCILE`` also removes the Jira links the backlog no longer has and
    clears a parent the backlog no longer has, so the links match exactly.
    """

    ADD_MISSING = auto()
    RECONCILE = auto()


class UpdatedBacklogInJira(NamedTuple):
    """The result of updating backlog items in Jira.

    Fields:
        updated: Keys of the items already in Jira that had at least one
            selected field changed.
        already_correct: Keys of the items already in Jira whose selected
            fields already matched, so no change was made.
        ignored: Keys of the items not present in Jira and left untouched
            under the ``IGNORE`` policy.
        failed: Items whose update Jira refused, each with a concise
            reason; the argument backlog is not changed by a failure.
        status_mismatch: Updated items whose status could not be
            transitioned to a Jira status matching the item's status.
        failed_links: The parent and dependency links Jira refused to write
            or remove while updating existing items, each with a reason.
        added: The result of adding the items not present in Jira under the
            ``ADD`` policy, empty under the other policies. It carries the
            key map used to rekey the shown backlog for the added items.
    """

    updated: list[str]
    already_correct: list[str]
    ignored: list[str]
    failed: list[FailedItem]
    status_mismatch: list[StatusMismatch]
    failed_links: list[FailedLink]
    added: AddedToJira


@dataclass(frozen=True)
class _UpdateCtx:
    """The resolved target, the selected fields and the link policy.

    ``key_map`` maps an original key to the Jira key assigned to an item
    added in the same run, so an updated item's references to a newly added
    item are remapped. ``dep_specs`` pairs each writable dependency field's
    link spec with its ``issuelinks`` path.
    """

    base: _WriteContext
    selected: frozenset[str]
    key_map: dict[str, str]
    link_update: LinkUpdate
    dep_specs: tuple[tuple[_LinkSpec, JiraAttrPath], ...]
    stderr_file: TextIO


@dataclass
class _Updated:
    """Mutable accumulator of the update-backlog results being built."""

    updated: list[str]
    already_correct: list[str]
    ignored: list[str]
    failed: list[FailedItem]
    status_mismatch: list[StatusMismatch]
    links: list[FailedLink]


@dataclass
class _Work:
    """The state shared by the helpers that update one existing issue.

    ``current`` holds the item's current internal field values, read once
    from the issue before any change, so a diff never sees its own writes.
    """

    ctx: _UpdateCtx
    item: BacklogItem
    issue: Issue
    current: dict[str, object]
    acc: _Updated


def _existing_issues(client: JIRA, backlog: Backlog) -> dict[str, Issue]:
    """Return the Jira issues that exist, indexed by their backlog key."""
    result: dict[str, Issue] = {}
    for item in backlog:
        try:
            result[item.key] = client.issue(item.key)
        except JIRAError:
            pass
    return result


def _raise_missing(names: list[str], stderr_file: TextIO) -> None:
    """Report and raise for backlog keys not present in Jira."""
    error = ItemNotInJiraError(sorted(names), 'Backlog keys')
    print(str(error), file=stderr_file)
    raise error


def _report_skipped(key: str, skipped: list[str], custom_names: dict[str, str],
                    stderr_file: TextIO) -> None:
    """Report selected fields the issue's edit screen did not offer."""
    names = _skipped_names(skipped, custom_names)
    print(f'WARNING: {key} has no edit-screen field for {names}; those '
          'values were not updated.', file=stderr_file)


def _field_diff(work: _Work) -> dict[str, object]:
    """Return the settable-field payload whose value differs in Jira.

    Only the selected settable fields are considered; the status, parent
    and dependency fields are handled separately. An empty internal value
    is left unset, and a value equal to the current Jira value is skipped.
    """
    base = work.ctx.base
    fields: dict[str, object] = {}
    for name, attrs in base.column_map.items():
        if name not in work.ctx.selected or name in _SKIP_DATA or not attrs:
            continue
        desired = _internal_value(name, work.item, base.types.levels,
                                  base.types.issue_type_map)
        if desired in (None, '') or work.current.get(name) == desired:
            continue
        _place_value(fields, attrs[0], desired, base.custom_ids)
    return fields


def _write_fields(work: _Work, payload: dict[str, object]) -> Optional[bool]:
    """Write the differing settable fields, or record a refusal.

    Returns whether anything was written, or None when Jira refused the
    update, in which case the item is recorded as failed and the rest of
    its update is skipped. Fields the edit screen does not offer are
    reported, exactly as when adding an issue.
    """
    if not payload:
        return False
    base = work.ctx.base
    editable = _editable_field_ids(base.client, work.item.key)
    allowed = {name: value for name, value in payload.items()
               if name in editable}
    skipped = sorted(set(payload) - editable)
    try:
        if allowed:
            work.issue.update(fields=allowed)
    except JIRAError as error:
        work.acc.failed.append(FailedItem(copy.deepcopy(work.item),
                                          _jira_reason(error)))
        return None
    if skipped:
        _report_skipped(work.item.key, skipped, base.custom_names,
                        work.ctx.stderr_file)
    return bool(allowed)


def _apply_status(work: _Work) -> bool:
    """Transition the issue to the item's status when selected.

    Returns whether a status change was needed. When the current status
    already matches nothing is done; otherwise a matching transition is
    tried, and a failure is reported and collected as a mismatch.
    """
    if 'status' not in work.ctx.selected:
        return False
    base = work.ctx.base
    name = _jira_status_name(base, work.issue)
    if _maps_to(name, work.item.status, base.status_map):
        return False
    if _try_transitions(base, work.item.status, work.issue):
        return True
    bad = StatusMismatch(copy.deepcopy(work.item), work.item.status, name)
    _report_status_mismatch(bad, work.ctx.stderr_file)
    work.acc.status_mismatch.append(bad)
    return True


def _desired_parent(work: _Work) -> Optional[str]:
    """Return the item's parent key remapped for an added parent, or None."""
    parent = work.item.parent_key
    if parent is None:
        return None
    return work.ctx.key_map.get(parent, parent)


def _apply_parent(work: _Work) -> bool:
    """Set, clear or leave the item's parent when selected.

    Returns whether a parent change was needed. Under ``ADD_MISSING`` the
    parent is set only when the issue has none, so an existing parent is
    never replaced or cleared. Under ``RECONCILE`` the parent is set to
    match, replacing a different one, and cleared when the item has none.
    """
    if 'parent_key' not in work.ctx.selected:
        return False
    desired = _desired_parent(work)
    current = work.current.get('parent_key')
    if current == desired:
        return False
    if work.ctx.link_update is LinkUpdate.ADD_MISSING:
        if current is None and desired is not None:
            _write_parent(work, desired)
            return True
        return False
    if desired is not None:
        _write_parent(work, desired)
        return True
    _clear_parent(work, current)
    return True


def _write_parent(work: _Work, parent_key: str) -> None:
    """Set the item's parent link to a parent key through the mapped field."""
    base = work.ctx.base
    fields = _parent_fields(base.column_map, base.custom_ids, parent_key)
    if not fields:
        return
    template = FailedLink(copy.deepcopy(work.item), parent_key, 'parent', '')
    _try_link(work.acc.links, template, work.ctx.stderr_file,
              lambda: work.issue.update(fields=fields))


def _clear_parent(work: _Work, current: object) -> None:
    """Clear the item's parent by setting the mapped parent field to None."""
    base = work.ctx.base
    fields = _clear_parent_fields(base.column_map, base.custom_ids)
    if not fields:
        return
    target = current if isinstance(current, str) else ''
    template = FailedLink(copy.deepcopy(work.item), target, 'parent', '')
    _try_link(work.acc.links, template, work.ctx.stderr_file,
              lambda: work.issue.update(fields=fields))


def _clear_parent_fields(column_map: dict[str, tuple[JiraAttrPath, ...]],
                         custom_ids: dict[str, str]) -> dict[str, object]:
    """Return the update fields that clear the first mapped parent path."""
    attrs = column_map.get('parent_key', ())
    if not attrs:
        return {}
    attr = attrs[0]
    if attr.kind is JiraAttrType.CUSTOM_FIELD:
        field_id = _field_id(attr.path[0], custom_ids)
        return {field_id: None} if field_id is not None else {}
    if attr.kind is JiraAttrType.FIELD:
        return {attr.path[0]: None}
    return {}


def _apply_deps(work: _Work) -> bool:
    """Reconcile every selected dependency field's Jira issue links."""
    changed = False
    for spec, attr in work.ctx.dep_specs:
        if spec.field in work.ctx.selected:
            if _apply_one_dep(work, spec, attr):
                changed = True
    return changed


def _apply_one_dep(work: _Work, spec: _LinkSpec, attr: JiraAttrPath) -> bool:
    """Add the missing links of one dependency field, removing stale ones.

    The links present on the issue for this field are read and compared to
    the item's dependency keys (remapped for added items). The missing keys
    are linked; under ``RECONCILE`` the keys no longer wanted are unlinked.
    """
    field_root = getattr(work.issue, 'fields', None)
    current = [str(key)
               for key in _coerce_all(_filtered_values(field_root, attr))]
    desired = [work.ctx.key_map.get(dep, dep)
               for dep in getattr(work.item, spec.field)]
    to_add = [dep for dep in desired if dep not in current]
    to_remove = ([dep for dep in current if dep not in desired]
                 if work.ctx.link_update is LinkUpdate.RECONCILE else [])
    for dep in to_add:
        _create_dep_link(work, spec, dep)
    for dep in to_remove:
        _remove_dep_link(work, spec, dep)
    return bool(to_add or to_remove)


def _create_dep_link(work: _Work, spec: _LinkSpec, dep: str) -> None:
    """Create one Jira issue link for a dependency in the spec's direction.

    A Jira link is created from its inward issue to its outward issue. When
    the dependency is the inward issue (the dependency blocks the item) the
    link is created from the dependency to the item, so the item ends up
    blocked by the dependency, the exact inverse of the read.
    """
    inward, outward = ((dep, work.item.key) if spec.dep_is_inward
                       else (work.item.key, dep))
    template = FailedLink(copy.deepcopy(work.item), dep, spec.link_type, '')
    _try_link(work.acc.links, template, work.ctx.stderr_file,
              partial(work.ctx.base.client.create_issue_link, spec.link_type,
                      inward, outward))


def _remove_dep_link(work: _Work, spec: _LinkSpec, dep: str) -> None:
    """Delete the Jira issue link of the spec's type to a dependency key."""
    link_id = _find_link_id(work.issue, spec, dep)
    if link_id is None:
        return
    template = FailedLink(copy.deepcopy(work.item), dep, spec.link_type, '')
    _try_link(work.acc.links, template, work.ctx.stderr_file,
              partial(work.ctx.base.client.delete_issue_link, link_id))


def _find_link_id(issue: Issue, spec: _LinkSpec, dep: str) -> Optional[str]:
    """Return the id of the issue link of the spec's type to a dep key."""
    links = getattr(getattr(issue, 'fields', None), 'issuelinks', None)
    if not isinstance(links, (list, tuple)):
        return None
    side = 'inwardIssue' if spec.dep_is_inward else 'outwardIssue'
    for link in links:
        if _walk(link, ('type', 'name')) == spec.link_type and \
                _walk(link, (side, 'key')) == dep:
            link_id = getattr(link, 'id', None)
            if isinstance(link_id, str):
                return link_id
    return None


def _update_one(ctx: _UpdateCtx, item: BacklogItem, issue: Issue,
                acc: _Updated) -> None:
    """Update one existing issue's selected fields, links and status.

    The current values are read once, the differing settable fields are
    written, and the status, parent and dependency links are reconciled.
    The item is recorded as updated when anything changed, as already
    correct when nothing needed changing, or as failed when the field
    update was refused.
    """
    current = _backlog_row(issue, getattr(issue, 'fields', None),
                           ctx.base.column_map, ctx.base.custom_ids,
                           ctx.stderr_file)
    work = _Work(ctx, item, issue, current, acc)
    data_changed = _write_fields(work, _field_diff(work))
    if data_changed is None:
        return
    status_changed = _apply_status(work)
    parent_changed = _apply_parent(work)
    deps_changed = _apply_deps(work)
    changed = (data_changed or status_changed or parent_changed
               or deps_changed)
    (acc.updated if changed else acc.already_correct).append(item.key)


def _make_ctx(base: _WriteContext, fields_to_update: list[str],
              key_map: dict[str, str], link_update: LinkUpdate,
              stderr_file: TextIO) -> _UpdateCtx:
    """Build the update context from the write context and the selection."""
    selected = frozenset(name for name in fields_to_update
                         if name in base.column_map
                         and name not in _IDENTITY_FIELDS)
    return _UpdateCtx(base=base, selected=selected, key_map=key_map,
                      link_update=link_update,
                      dep_specs=tuple(_dep_link_attrs(base.column_map)),
                      stderr_file=stderr_file)


def _empty_added() -> AddedToJira:
    """Return an empty add result for the non-add policies."""
    return AddedToJira([], [], [], {}, [], [])


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _add_or_raise(connections: JiraConnections, preset_name: str,
                  backlog: Backlog, existing: dict[str, Issue],
                  mode: OnMissingKey, levels: Optional[Levels],
                  status_map: Optional[dict[str, Status]],
                  stderr_file: TextIO) -> AddedToJira:
    """Handle the items not present in Jira per the missing-key policy.

    ``RAISE`` raises before anything is changed, ``ADD`` creates the
    missing items with all of their fields as :func:`add_backlog_to_jira`
    does, and any other policy leaves them alone with an empty add result.
    """
    missing = [item for item in backlog if item.key not in existing]
    if mode is OnMissingKey.RAISE and missing:
        _raise_missing([item.key for item in missing], stderr_file)
    if mode is OnMissingKey.ADD and missing:
        return add_backlog_to_jira(connections, preset_name, missing,
                                   on_existing_key=OnExistingKey.SKIP,
                                   levels=levels, status_map=status_map,
                                   stderr_file=stderr_file)
    return _empty_added()


def _run_updates(ctx: _UpdateCtx, backlog: Backlog, existing: dict[str, Issue],
                 mode: OnMissingKey,
                 added: AddedToJira) -> UpdatedBacklogInJira:
    """Update every present item and record the ignored missing keys."""
    ignored = ([item.key for item in backlog if item.key not in existing]
               if mode is OnMissingKey.IGNORE else [])
    acc = _Updated([], [], sorted(ignored), [], [], [])
    for item in backlog:
        issue = existing.get(item.key)
        if issue is not None:
            _update_one(ctx, item, issue, acc)
    return UpdatedBacklogInJira(acc.updated, acc.already_correct, acc.ignored,
                                acc.failed, acc.status_mismatch, acc.links,
                                added)


# pylint: disable-next=too-many-arguments
def update_backlog_in_jira(connections: JiraConnections, preset_name: str,
                           backlog: Backlog, *, on_missing_key: OnMissingKey,
                           fields_to_update: list[str],
                           link_update: LinkUpdate = LinkUpdate.RECONCILE,
                           levels: Optional[Levels] = None,
                           status_map: Optional[dict[str, Status]] = None,
                           stderr_file: TextIO = sys.stderr
                           ) -> UpdatedBacklogInJira:
    """Update the backlog items in Jira, matching a Jira issue by its key.

    Every item's key is looked up in Jira. In ``RAISE`` mode, if any key is
    not present the function raises before changing anything. Items not
    present are added in ``ADD`` mode (writing all of their mapped fields,
    as :func:`add_backlog_to_jira` does) and left alone in ``IGNORE`` mode.
    Each matched issue has the selected fields updated: only the fields
    named in ``fields_to_update`` that are mapped for writing and are not
    the key or the issue type, and among those only the ones whose current
    Jira value differs from the item. The status is set by a transition,
    the parent by the mapped parent field, and the dependencies by Jira
    issue links reconciled per ``link_update``. An item whose update Jira
    refuses is collected in ``failed`` with a concise reason, and the other
    items are still processed. The argument backlog is never modified.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset, connection and backlog write column map.
        preset_name: The name of the Jira preset to use.
        backlog: The backlog items to update. Not modified.
        on_missing_key: Whether to raise, ignore or add when a key is not
            present in Jira.
        fields_to_update: The internal field names to update. Names that
            are not mapped for writing, or that are the key or the issue
            type, are ignored. Use :func:`updatable_backlog_fields` for the
            full set of updatable fields of a preset.
        link_update: Whether to only add missing links or also remove the
            Jira links the backlog no longer has.
        levels: The levels used to resolve the issue type when adding a
            missing item, or None for the default levels.
        status_map: Extra Jira status names mapped to internal statuses,
            used to reconcile a status, or None for the built-in matching.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The keys of the updated, already-correct and ignored items, the
        items whose update failed, the status mismatches and failed links
        of the updated items, and the add result for any added items.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        UnknownIssueTypeError: In ``ADD`` mode, if an added item's issue
            type is not valid in the project.
        ItemNotInJiraError: In ``RAISE`` mode, if any key is not present in
            Jira.
    """
    ctx, _ = _build_ctx(connections, preset_name, levels, status_map)
    existing = _existing_issues(ctx.client, backlog)
    added = _add_or_raise(connections, preset_name, backlog, existing,
                          on_missing_key, levels, status_map, stderr_file)
    update_ctx = _make_ctx(ctx, fields_to_update, added.key_map, link_update,
                           stderr_file)
    return _run_updates(update_ctx, backlog, existing, on_missing_key, added)


def updatable_backlog_fields(connections: JiraConnections,
                             preset_name: str) -> list[str]:
    """Return the internal fields a preset can update on an existing issue.

    These are the fields mapped in the preset's backlog write map, minus
    the key and the issue type (level), which are never changed on an
    existing issue. The order follows the write map. This is the set the
    CLI ``all`` value and the GUI checkbox list offer, and the set
    :func:`update_backlog_in_jira` intersects ``fields_to_update`` with.

    Args:
        connections: The pool holding the configuration with the preset.
        preset_name: The name of the Jira preset to use.

    Returns:
        The updatable internal field names, in write-map order.

    Raises:
        KeyError: If the preset or its backlog write map is missing.
    """
    jira_config = connections.jira_config
    preset = jira_config.get_preset(preset_name)
    column_map = jira_config.backlog_column_maps[
        preset.write_backlog_map_name()]
    return [name for name in column_map if name not in _IDENTITY_FIELDS]


def format_backlog_updates(result: UpdatedBacklogInJira) -> str:
    """Return a listing of the update outcome per backlog item.

    The sections are the updated, already-correct and ignored keys, the
    added items, and the failed items, status mismatches and failed links,
    which combine the updated items with any added items. Each section has
    a heading with its count, then one line per entry, or a ``(none)`` line
    when empty. The CLI prints this text and the GUI shows it in a
    copy-pasteable pop-up.
    """
    added = result.added
    failed = result.failed + added.failed
    mismatch = result.status_mismatch + added.status_mismatch
    links = result.failed_links + added.failed_links
    lines = _outcome_prefix(result.updated, result.already_correct,
                            result.ignored)
    lines.append('')
    lines.extend(_result_section('Added to Jira', added.stored))
    lines.append('')
    lines.extend(_failed_section('Failed to update', failed))
    lines.append('')
    lines.extend(_status_section('Status not set in Jira', mismatch))
    lines.append('')
    lines.extend(_link_section('Links not written', links))
    return '\n'.join(lines)
