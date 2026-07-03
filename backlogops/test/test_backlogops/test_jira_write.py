#! /usr/local/bin/python3
"""Tests for adding a backlog to Jira.

A stand-in Jira client records the created field payloads and answers key
look-ups from a set of already-present keys, so the orchestration, the
raise-before-write rule, the inverted field mapping and the never-mutated
argument are checked without a real server. The connection pool is
exercised for client reuse and for reconnecting a session the server
closed.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Callable, Optional, cast
import pytest
from jira import JIRA, JIRAError
import backlogops
from backlogops.backlog import BacklogItem, Status
import backlogops.jira_connect as jc
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import JiraIOConfig
from backlogops.jira_write import (
    add_backlog_to_jira, AddedToJira, ExistsInJiraError, FailedItem,
    OnExistingKey, StatusMismatch, UnknownIssueTypeError, apply_jira_keys,
    format_add_result, jira_custom_fields, jira_editable_fields,
    _issue_type_meta, _status_from_name, _transition_target)
from backlogops.levels import DEFAULT_LEVELS, level_name
from .jira_write_helpers import (
    connections_for as _connections, jira_write_config as _config, NO)

FIELDS: list[dict[str, str]] = [
    {'id': 'customfield_10016', 'name': 'Story point estimate'},
    {'id': 'customfield_10001', 'name': 'Team'}]
"""Field descriptors resolving the two custom fields used on create."""

_EDITABLE_DEFAULT: dict[str, str] = {
    'description': 'Description',
    'customfield_10016': 'Story point estimate',
    'customfield_10001': 'Team', 'fixVersions': 'Fix versions'}
"""Fields the fake issue's edit screen offers by default."""

_ISSUE_TYPES_DEFAULT: dict[str, bool] = {
    'Story': False, 'Epic': False, 'Subtask': True}
"""Creatable issue types of the fake Jira, mapped to their subtask flag.

An empty issue-type map instead models a Jira whose create metadata is
unavailable, so that sub-task detection falls back to the lowest level.
"""


def _recorder(record: dict[str, object]
              ) -> Callable[[dict[str, object]], None]:
    """Return an update callback that merges its fields into ``record``."""
    def update(fields: dict[str, object]) -> None:
        """Merge the update fields into the created issue's record."""
        record.update(fields)
    return update


@dataclass
class _Behavior:
    """How the fake Jira answers create, edit and transition calls.

    The create and edit knobs are set from the constructor; the status
    and transition knobs default to a status matching a fresh TODO item
    and no transitions, and a status test sets the ones it needs.
    """

    editable: dict[str, str]
    issue_types: dict[str, bool]
    fail_types: set[str]
    init_status: str = 'TODO'
    transitions: list[dict[str, object]] = field(default_factory=list)
    fail_transition: bool = False
    transitioned: list[tuple[str, str]] = field(default_factory=list)


class _WriteClient:
    """A stand-in Jira client for the add-to-Jira tests."""

    def __init__(self, existing: Optional[set[str]] = None, alive: bool = True,
                 editable: Optional[dict[str, str]] = None,
                 issue_types: Optional[dict[str, bool]] = None,
                 fail_types: Optional[set[str]] = None) -> None:
        """Start with the present keys, screens, types and failing types.

        ``issue_types`` maps each creatable issue type name to whether it
        is a sub-task; an empty map models unavailable create metadata.
        The status and transition behaviour lives in ``behavior`` and a
        status test sets the fields it needs.
        """
        self.existing = set() if existing is None else set(existing)
        self.alive = alive
        self.behavior = _Behavior(
            editable=_EDITABLE_DEFAULT if editable is None else editable,
            issue_types=(_ISSUE_TYPES_DEFAULT if issue_types is None
                         else issue_types),
            fail_types=set() if fail_types is None else fail_types)
        self.created: list[dict[str, object]] = []
        self.closed = 0

    def myself(self) -> dict[str, str]:
        """Report a live session, or raise when the client is dead."""
        if not self.alive:
            raise JIRAError(status_code=401, text='session closed')
        return {'name': 'tester'}

    def fields(self) -> list[dict[str, str]]:
        """Return the canned field descriptors."""
        return FIELDS

    def issue(self, key: str) -> SimpleNamespace:
        """Return the issue for a present key, or raise for an absent one."""
        if key in self.existing:
            return SimpleNamespace(key=key)
        raise JIRAError(status_code=404, text='not found')

    def _issue_type_values(self) -> list[dict[str, object]]:
        """Return the issue types with their sub-task flags for metadata."""
        return [{'name': name, 'subtask': subtask}
                for name, subtask in sorted(self.behavior.issue_types.items())]

    def createmeta_issuetypes(self, project: str) -> dict[str, object]:
        """Return the project's creatable issue types as create metadata."""
        _ = project
        return {'values': self._issue_type_values()}

    def createmeta(self, **kwargs: object) -> dict[str, object]:
        """Return the creatable issue types via the older createmeta API."""
        _ = kwargs
        return {'projects': [{'issuetypes': self._issue_type_values()}]}

    def create_issue(self, fields: dict[str, object]) -> SimpleNamespace:
        """Record the create payload; the issue merges a later update.

        Raises for an issue type in ``fail_types``, and for a sub-task
        without a ``parent``, as Jira does when it refuses a create. The
        returned issue's ``update`` merges its fields into the same record,
        and it carries a ``fields.status`` set to the initial status, so
        the status reconciliation can read and transition it.
        """
        issuetype = fields.get('issuetype')
        name = issuetype.get('name') if isinstance(issuetype, dict) else None
        if name in self.behavior.fail_types:
            raise JIRAError(status_code=400, text='Specify a valid issue type')
        if name is not None and self.behavior.issue_types.get(name) \
                and 'parent' not in fields:
            raise JIRAError(status_code=400, text='Issue type is a sub-task '
                            'but parent issue key or id not specified.')
        record = dict(fields)
        self.created.append(record)
        status = SimpleNamespace(name=self.behavior.init_status)
        return SimpleNamespace(key=f'JIRA-{len(self.created)}',
                               update=_recorder(record),
                               fields=SimpleNamespace(status=status))

    def editmeta(self, issue: str) -> dict[str, object]:
        """Return the edit-screen field metadata for the issue."""
        _ = issue
        return {'fields': {fid: {'name': name}
                           for fid, name in self.behavior.editable.items()}}

    def transitions(self, issue: SimpleNamespace) -> list[dict[str, object]]:
        """Return the configured available workflow transitions."""
        _ = issue
        return list(self.behavior.transitions)

    def transition_issue(self, issue: SimpleNamespace,
                         transition: str) -> None:
        """Apply a transition, updating the status, or raise when set to."""
        if self.behavior.fail_transition:
            raise JIRAError(status_code=400, text='transition rejected')
        target = self._target_of(transition)
        if target is not None:
            issue.fields.status.name = target
        self.behavior.transitioned.append((issue.key, transition))

    def _target_of(self, transition: str) -> Optional[str]:
        """Return the target status name of a transition id, or None."""
        for trans in self.behavior.transitions:
            if trans.get('id') == transition:
                return _transition_target(trans)
        return None

    def close(self) -> None:
        """Count a close of the stand-in client."""
        self.closed += 1


def _issue_config(mapping: dict[int, str], project: str = 'PROJ',
                  ref: str = 'im') -> JiraIOConfig:
    """Return a config whose preset names a level-to-issue-type map."""
    config = _config(project)
    config.issue_type_maps = {ref: mapping}
    config.presets['w'].issue_type_map_name = ref
    return config


def _connect_each(clients: list[_WriteClient]
                  ) -> Callable[[object, object], _WriteClient]:
    """Return a stand-in ``_connect`` yielding each client in turn."""
    supply = iter(clients)
    return lambda connection, passphrase: next(supply)


def _item(key: str) -> BacklogItem:
    """Return a default backlog item with a description extra field."""
    return BacklogItem(key=key, level=1, title='T', story_points=5,
                       status=Status.TODO, extra_fields={'description': 'D'})


def _leveled(key: str, level: int,
             parent: Optional[str] = None) -> BacklogItem:
    """Return a backlog item at a level, optionally with a parent key."""
    return BacklogItem(key=key, level=level, title=f'T {key}', story_points=0,
                       status=Status.TODO, parent_key=parent)


SMAP: dict[str, Status] = {
    'To Do': Status.TODO, 'In Progress': Status.IN_PROGRESS,
    'Done': Status.DONE, 'Rejected': Status.REJECTED}
"""A status map from Jira status names to internal statuses."""


def _trans(trans_id: str, target: str) -> dict[str, object]:
    """Return a fake workflow transition leading to a target status."""
    return {'id': trans_id, 'to': {'name': target}}


def test_add_all_new(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test every item is created and copied with its new Jira key."""
    client = _WriteClient()
    connections = _connections(monkeypatch, client)
    backlog = [_item('A'), _item('B')]
    result = add_backlog_to_jira(connections, 'w', backlog,
                                 on_existing_key=OnExistingKey.SKIP)
    assert [item.key for item in result.stored] == ['JIRA-1', 'JIRA-2']
    assert not result.already_present
    assert result.key_map == {'A': 'JIRA-1', 'B': 'JIRA-2'}
    assert len(client.created) == 2
    assert [item.key for item in backlog] == ['A', 'B']


def test_skip_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test present keys are skipped and the rest are created."""
    client = _WriteClient(existing={'B'})
    connections = _connections(monkeypatch, client)
    backlog = [_item('A'), _item('B'), _item('C')]
    result = add_backlog_to_jira(connections, 'w', backlog,
                                 on_existing_key=OnExistingKey.SKIP)
    assert [item.key for item in result.stored] == ['JIRA-1', 'JIRA-2']
    assert [item.key for item in result.already_present] == ['B']
    assert result.key_map == {'A': 'JIRA-1', 'C': 'JIRA-2'}
    assert len(client.created) == 2


def test_raise_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a present key raises before anything is created."""
    client = _WriteClient(existing={'B'})
    connections = _connections(monkeypatch, client)
    backlog = [_item('A'), _item('B')]
    with pytest.raises(ExistsInJiraError) as caught:
        add_backlog_to_jira(connections, 'w', backlog,
                            on_existing_key=OnExistingKey.RAISE,
                            stderr_file=NO)
    assert caught.value.keys == ['B']
    assert not client.created


def test_create_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the inverted column map builds the create payload."""
    client = _WriteClient()
    connections = _connections(monkeypatch, client)
    item = _item('A')
    item.title = 'Build'
    item.story_points = 8
    item.release = 'R1'
    item.team = 'Alpha'
    add_backlog_to_jira(connections, 'w', [item],
                        on_existing_key=OnExistingKey.SKIP)
    fields = client.created[0]
    assert fields['project'] == {'key': 'PROJ'}
    assert fields['summary'] == 'Build'
    assert fields['issuetype'] == {'name': level_name(1, DEFAULT_LEVELS)}
    assert fields['description'] == 'D'
    assert fields['customfield_10016'] == 8
    assert fields['customfield_10001'] == 'Alpha'
    assert fields['fixVersions'] == [{'name': 'R1'}]
    assert 'key' not in fields


def test_skip_unsettable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a field the edit screen omits is skipped and reported."""
    client = _WriteClient(editable={'description': 'Description'})
    connections = _connections(monkeypatch, client)
    item = _item('A')
    item.story_points = 8
    errors = io.StringIO()
    add_backlog_to_jira(connections, 'w', [item],
                        on_existing_key=OnExistingKey.SKIP, stderr_file=errors)
    assert 'customfield_10016' not in client.created[0]
    assert client.created[0]['description'] == 'D'
    assert 'customfield_10016' in errors.getvalue()


def test_skipped_custom_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a skipped custom field also shows its display name.

    A custom field is reported as ``id (Display Name)`` while a plain
    field, which has no separate display name, keeps just its field name.
    """
    client = _WriteClient(editable={'description': 'Description'})
    connections = _connections(monkeypatch, client)
    item = _item('A')
    item.story_points = 8
    item.release = 'R1'
    errors = io.StringIO()
    add_backlog_to_jira(connections, 'w', [item],
                        on_existing_key=OnExistingKey.SKIP, stderr_file=errors)
    text = errors.getvalue()
    assert 'customfield_10016 (Story point estimate)' in text
    assert 'fixVersions' in text
    assert 'fixVersions (' not in text


def test_input_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test mutating a stored copy leaves the argument item untouched."""
    client = _WriteClient()
    connections = _connections(monkeypatch, client)
    item = _item('A')
    item.depends_on_f2s = ['X']
    result = add_backlog_to_jira(connections, 'w', [item],
                                 on_existing_key=OnExistingKey.SKIP)
    stored = result.stored[0]
    stored.depends_on_f2s.append('Y')
    stored.parent_key = 'P'
    assert item.key == 'A'
    assert item.depends_on_f2s == ['X']
    assert item.parent_key is None


def test_client_reused(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a live cached client is reused for the same connection."""
    client = _WriteClient()
    connections = _connections(monkeypatch, client)
    first = connections.client('c')
    second = connections.client('c')
    assert first is second


def test_client_reconnect(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a dead cached client is closed and replaced on next use."""
    dead = _WriteClient(alive=False)
    live = _WriteClient()
    monkeypatch.setattr(jc, '_connect', _connect_each([dead, live]))
    connections = JiraConnections(_config(), None)
    first: object = connections.client('c')
    second: object = connections.client('c')
    assert first is dead
    assert second is live
    assert dead.closed == 1


def test_close_clients(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test closing the pool closes every opened client."""
    client = _WriteClient()
    connections = _connections(monkeypatch, client)
    connections.client('c')
    connections.close()
    assert client.closed == 1


def test_format_result() -> None:
    """Test the listing shows added, present, failed and status sections."""
    added = _item('P-1')
    added.title = 'First'
    present = _item('X-9')
    present.title = 'Old'
    bad = _item('E-1')
    bad.title = 'Epic'
    late = _item('P-2')
    late.title = 'Late'
    result = AddedToJira(
        stored=[added], already_present=[present],
        failed=[FailedItem(bad, 'HTTP 400: nope')], key_map={'A': 'P-1'},
        status_mismatch=[StatusMismatch(late, Status.DONE, 'To Do')])
    text = format_add_result(result)
    assert 'Added to Jira (1):' in text
    assert '  P-1  First' in text
    assert 'Already in Jira (1):' in text
    assert '  X-9  Old' in text
    assert 'Failed to add (1):' in text
    assert 'E-1  Epic  - HTTP 400: nope' in text
    assert 'Status not set in Jira (1):' in text
    assert "P-2  Late  - expected DONE, Jira status 'To Do'" in text


def test_format_empty() -> None:
    """Test an empty section is shown as a count of zero and (none)."""
    text = format_add_result(AddedToJira([], [], [], {}, []))
    assert 'Added to Jira (0):' in text
    assert 'Failed to add (0):' in text
    assert 'Status not set in Jira (0):' in text
    assert '(none)' in text


def test_failed_continue(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused create is reported and the others still added."""
    client = _WriteClient(fail_types={'Epic'})
    connections = _connections(monkeypatch, client)
    story = _item('S')
    epic = BacklogItem(key='E', level=2, title='Epic 1', story_points=0,
                       status=Status.TODO)
    result = add_backlog_to_jira(connections, 'w', [story, epic],
                                 on_existing_key=OnExistingKey.SKIP,
                                 stderr_file=NO)
    assert [item.key for item in result.stored] == ['JIRA-1']
    assert [entry.item.key for entry in result.failed] == ['E']
    assert 'HTTP 400' in result.failed[0].reason


def test_invalid_type(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an unknown issue type raises before anything is created."""
    client = _WriteClient()
    connections = _connections(monkeypatch, client)
    item = BacklogItem(key='I', level=3, title='Init', story_points=0,
                       status=Status.TODO)
    with pytest.raises(UnknownIssueTypeError) as caught:
        add_backlog_to_jira(connections, 'w', [item],
                            on_existing_key=OnExistingKey.SKIP, stderr_file=NO)
    assert 'Initiative' in caught.value.bad
    assert not client.created


def test_itmap_on_write(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a mapped level writes the Jira issue type from the map."""
    client = _WriteClient(issue_types={'Deluppgift': False, 'Story': False})
    connections = _connections(monkeypatch, client,
                               _issue_config({0: 'Deluppgift'}))
    item = BacklogItem(key='T', level=0, title='Sub', story_points=0,
                       status=Status.TODO)
    add_backlog_to_jira(connections, 'w', [item],
                        on_existing_key=OnExistingKey.SKIP, stderr_file=NO)
    assert client.created[0]['issuetype'] == {'name': 'Deluppgift'}


def test_itmap_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a level absent from the map writes the level name."""
    client = _WriteClient(issue_types={'Deluppgift': False, 'Story': False})
    connections = _connections(monkeypatch, client,
                               _issue_config({0: 'Deluppgift'}))
    add_backlog_to_jira(connections, 'w', [_item('S')],
                        on_existing_key=OnExistingKey.SKIP, stderr_file=NO)
    assert client.created[0]['issuetype'] == {'name': 'Story'}


def test_itmap_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the bare level name is rejected when no map renames it.

    This is the reported failure: a Jira that renamed the sub-task type
    rejects the level name 'Sub-Task', and without a map the write is
    refused before anything is created.
    """
    client = _WriteClient(issue_types={'Deluppgift': False, 'Story': False,
                                       'Epic': False})
    connections = _connections(monkeypatch, client)
    item = BacklogItem(key='T', level=0, title='Sub', story_points=0,
                       status=Status.TODO)
    with pytest.raises(UnknownIssueTypeError) as caught:
        add_backlog_to_jira(connections, 'w', [item],
                            on_existing_key=OnExistingKey.SKIP, stderr_file=NO)
    assert 'Sub-Task' in caught.value.bad
    assert not client.created


def test_subtask_last_parent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a sub-task is created last with its parent's new Jira key.

    The sub-task is listed before its parent in the input, yet the parent
    is created first so the sub-task can carry the parent's assigned key.
    """
    client = _WriteClient(issue_types={'Story': False, 'Sub-Task': True})
    connections = _connections(monkeypatch, client)
    backlog = [_leveled('T', 0, 'P'), _leveled('P', 1)]
    result = add_backlog_to_jira(connections, 'w', backlog,
                                 on_existing_key=OnExistingKey.SKIP,
                                 stderr_file=NO)
    assert [item.key for item in result.stored] == ['JIRA-1', 'JIRA-2']
    assert result.key_map == {'P': 'JIRA-1', 'T': 'JIRA-2'}
    assert 'parent' not in client.created[0]
    assert client.created[0]['issuetype'] == {'name': 'Story'}
    assert client.created[1]['issuetype'] == {'name': 'Sub-Task'}
    assert client.created[1]['parent'] == {'key': 'JIRA-1'}
    assert not result.failed


def test_subtask_present(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a sub-task attaches to a parent already present in Jira."""
    client = _WriteClient(existing={'EX'},
                          issue_types={'Story': False, 'Sub-Task': True})
    connections = _connections(monkeypatch, client)
    backlog = [_leveled('EX', 1), _leveled('T', 0, 'EX')]
    result = add_backlog_to_jira(connections, 'w', backlog,
                                 on_existing_key=OnExistingKey.SKIP,
                                 stderr_file=NO)
    assert [item.key for item in result.already_present] == ['EX']
    assert [item.key for item in result.stored] == ['JIRA-1']
    assert client.created[0]['parent'] == {'key': 'EX'}
    assert not result.failed


def test_subtask_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the lowest level marks a sub-task when metadata is missing."""
    client = _WriteClient(issue_types={})
    connections = _connections(monkeypatch, client)
    backlog = [_leveled('T', 0, 'P'), _leveled('P', 1)]
    result = add_backlog_to_jira(connections, 'w', backlog,
                                 on_existing_key=OnExistingKey.SKIP,
                                 stderr_file=NO)
    assert [item.key for item in result.stored] == ['JIRA-1', 'JIRA-2']
    assert client.created[1]['parent'] == {'key': 'JIRA-1'}
    assert not result.failed


def test_subtask_no_parent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a sub-task without a parent is refused as Jira refuses it."""
    client = _WriteClient(issue_types={'Sub-Task': True})
    connections = _connections(monkeypatch, client)
    result = add_backlog_to_jira(connections, 'w', [_leveled('T', 0)],
                                 on_existing_key=OnExistingKey.SKIP,
                                 stderr_file=NO)
    assert not result.stored
    assert [entry.item.key for entry in result.failed] == ['T']
    assert 'sub-task' in result.failed[0].reason


def test_apply_keys() -> None:
    """Test rekeying updates mapped items in place and keeps order."""
    backlog = [_item('A'), _item('B'), _item('C')]
    apply_jira_keys(backlog, {'A': 'P-1', 'C': 'P-3'})
    assert [item.key for item in backlog] == ['P-1', 'B', 'P-3']


def test_custom_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the diagnostic returns the custom field id and name pairs."""
    connections = _connections(monkeypatch, _WriteClient())
    pairs = jira_custom_fields(connections, 'w')
    assert ('customfield_10001', 'Team') in pairs
    assert ('customfield_10016', 'Story point estimate') in pairs


def test_editable_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the diagnostic returns an issue's edit-screen fields."""
    connections = _connections(monkeypatch, _WriteClient())
    ids = [fid for fid, _ in jira_editable_fields(connections, 'w', 'SCRUM-1')]
    assert 'customfield_10016' in ids
    assert 'description' in ids


class _MetaClient:
    """A client whose issue types are only available via createmeta."""

    def createmeta_issuetypes(self, project: str) -> dict[str, object]:
        """Refuse the issuetypes API as some Jira versions do."""
        _ = project
        raise JIRAError(text='Use createmeta instead')

    def createmeta(self, **kwargs: object) -> dict[str, object]:
        """Return the creatable issue types via the older createmeta API."""
        _ = kwargs
        return {'projects': [{'issuetypes': [
            {'name': 'Story'}, {'name': 'Subtask', 'subtask': True}]}]}


def test_types_via_createmeta() -> None:
    """Test issue-type metadata falls back to createmeta when refused."""
    client = cast(JIRA, _MetaClient())
    assert _issue_type_meta(client, 'P') == {'Story': False, 'Subtask': True}


def test_reexport() -> None:
    """Test the package re-exports the add-to-Jira names."""
    assert backlogops.add_backlog_to_jira is add_backlog_to_jira
    assert backlogops.AddedToJira is AddedToJira
    assert backlogops.ExistsInJiraError is ExistsInJiraError
    assert backlogops.StatusMismatch is StatusMismatch
    assert 'add_backlog_to_jira' in backlogops.__all__
    assert 'StatusMismatch' in backlogops.__all__
    assert 'JiraConnections' in backlogops.__all__


def test_stored_refs_remap(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test stored copies get parent and dependency keys remapped.

    A dependency on an item created in the same run is remapped to its
    Jira key, while a dependency on an item outside the run is kept.
    """
    client = _WriteClient(issue_types={'Story': False, 'Epic': False})
    connections = _connections(monkeypatch, client)
    child = _leveled('C', 1, 'P')
    child.depends_on_f2s = ['P']
    child.depends_on_s2s = ['EXT']
    result = add_backlog_to_jira(connections, 'w', [_leveled('P', 2), child],
                                 on_existing_key=OnExistingKey.SKIP,
                                 status_map=SMAP, stderr_file=NO)
    stored_child = result.stored[1]
    assert stored_child.key == 'JIRA-2'
    assert stored_child.parent_key == 'JIRA-1'
    assert stored_child.depends_on_f2s == ['JIRA-1']
    assert stored_child.depends_on_s2s == ['EXT']
    assert child.parent_key == 'P'
    assert child.depends_on_f2s == ['P']


def test_apply_keys_refs() -> None:
    """Test rekeying also remaps parent and dependency keys in place."""
    child = _leveled('C', 1, 'P')
    child.depends_on_f2s = ['P', 'EXT']
    backlog = [_leveled('P', 2), child]
    apply_jira_keys(backlog, {'P': 'J-1', 'C': 'J-2'})
    assert [item.key for item in backlog] == ['J-1', 'J-2']
    assert backlog[1].parent_key == 'J-1'
    assert backlog[1].depends_on_f2s == ['J-1', 'EXT']


def test_status_match(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a created status matching the item needs no transition."""
    client = _WriteClient()
    client.behavior.init_status = 'To Do'
    client.behavior.transitions = [_trans('11', 'Done')]
    connections = _connections(monkeypatch, client)
    result = add_backlog_to_jira(connections, 'w', [_item('A')],
                                 on_existing_key=OnExistingKey.SKIP,
                                 status_map=SMAP, stderr_file=NO)
    assert result.status_mismatch == []
    assert not client.behavior.transitioned


def test_status_transition(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a mismatching status is fixed by a matching transition."""
    client = _WriteClient()
    client.behavior.init_status = 'To Do'
    client.behavior.transitions = [_trans('21', 'Done')]
    connections = _connections(monkeypatch, client)
    item = _item('A')
    item.status = Status.DONE
    result = add_backlog_to_jira(connections, 'w', [item],
                                 on_existing_key=OnExistingKey.SKIP,
                                 status_map=SMAP, stderr_file=NO)
    assert result.status_mismatch == []
    assert client.behavior.transitioned == [('JIRA-1', '21')]


def test_status_no_match(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an unreachable status is reported as a mismatch."""
    client = _WriteClient()
    client.behavior.init_status = 'To Do'
    client.behavior.transitions = [_trans('11', 'In Progress')]
    connections = _connections(monkeypatch, client)
    item = _item('A')
    item.status = Status.DONE
    errors = io.StringIO()
    result = add_backlog_to_jira(connections, 'w', [item],
                                 on_existing_key=OnExistingKey.SKIP,
                                 status_map=SMAP, stderr_file=errors)
    assert [bad.item.key for bad in result.status_mismatch] == ['JIRA-1']
    bad = result.status_mismatch[0]
    assert bad.expected is Status.DONE
    assert bad.actual == 'To Do'
    assert not client.behavior.transitioned
    assert 'JIRA-1' in errors.getvalue()


def test_status_trans_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a rejected transition leaves a reported status mismatch."""
    client = _WriteClient()
    client.behavior.init_status = 'To Do'
    client.behavior.transitions = [_trans('31', 'Done')]
    client.behavior.fail_transition = True
    connections = _connections(monkeypatch, client)
    item = _item('A')
    item.status = Status.DONE
    result = add_backlog_to_jira(connections, 'w', [item],
                                 on_existing_key=OnExistingKey.SKIP,
                                 status_map=SMAP, stderr_file=NO)
    assert [bad.item.key for bad in result.status_mismatch] == ['JIRA-1']
    assert result.status_mismatch[0].actual == 'To Do'


@pytest.mark.parametrize('name,expected', [
    ('To Do', Status.TODO), ('IN_PROGRESS', Status.IN_PROGRESS),
    ('Done', Status.DONE), ('nope', None)])
def test_status_from_name(name: str, expected: Optional[Status]) -> None:
    """Test a status map match wins over the built-in name matching."""
    assert _status_from_name(name, {'To Do': Status.TODO}) is expected
