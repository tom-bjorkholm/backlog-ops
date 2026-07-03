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
from types import SimpleNamespace
from typing import Callable, Optional, cast
import pytest
from jira import JIRA, JIRAError
import backlogops
from backlogops.backlog import BacklogItem, Status
import backlogops.jira_connect as jc
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import (
    DEF_BACKLOG_COLUMN_MAP, DEF_RELEASE_COLUMN_MAP, JiraConnectConfig,
    JiraIOConfig, JiraPreset, TokenStorage)
from backlogops.jira_write import (
    add_backlog_to_jira, AddedToJira, ExistsInJiraError, FailedItem,
    OnExistingKey, UnknownIssueTypeError, apply_jira_keys, format_add_result,
    jira_custom_fields, jira_editable_fields, _valid_issue_types)
from backlogops.levels import DEFAULT_LEVELS, level_name
from backlogops.no_text_io import NoTextIO

NO = NoTextIO()

FIELDS: list[dict[str, str]] = [
    {'id': 'customfield_10016', 'name': 'Story point estimate'},
    {'id': 'customfield_10001', 'name': 'Team'}]
"""Field descriptors resolving the two custom fields used on create."""

_EDITABLE_DEFAULT: dict[str, str] = {
    'description': 'Description',
    'customfield_10016': 'Story point estimate',
    'customfield_10001': 'Team', 'fixVersions': 'Fix versions'}
"""Fields the fake issue's edit screen offers by default."""


def _recorder(record: dict[str, object]
              ) -> Callable[[dict[str, object]], None]:
    """Return an update callback that merges its fields into ``record``."""
    def update(fields: dict[str, object]) -> None:
        """Merge the update fields into the created issue's record."""
        record.update(fields)
    return update


class _WriteClient:
    """A stand-in Jira client for the add-to-Jira tests."""

    def __init__(self, existing: Optional[set[str]] = None, alive: bool = True,
                 editable: Optional[dict[str, str]] = None,
                 valid_types: Optional[set[str]] = None,
                 fail_types: Optional[set[str]] = None) -> None:
        """Start with the present keys, screens, types and failing types."""
        self.existing = set() if existing is None else set(existing)
        self.alive = alive
        self.editable = _EDITABLE_DEFAULT if editable is None else editable
        self.valid_types = ({'Story', 'Epic', 'Subtask'}
                            if valid_types is None else valid_types)
        self.fail_types = set() if fail_types is None else fail_types
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

    def createmeta_issuetypes(self, project: str) -> dict[str, object]:
        """Return the project's creatable issue types as create metadata."""
        _ = project
        return {'values': [{'name': name}
                           for name in sorted(self.valid_types)]}

    def create_issue(self, fields: dict[str, object]) -> SimpleNamespace:
        """Record the create payload; the issue merges a later update.

        Raises for an issue type in ``fail_types``, as Jira does when it
        refuses a create. The returned issue's ``update`` merges its fields
        into the same record, so the recorded payload holds the fields set
        at create and the fields set by the following update together.
        """
        issuetype = fields.get('issuetype')
        name = issuetype.get('name') if isinstance(issuetype, dict) else None
        if name in self.fail_types:
            raise JIRAError(status_code=400, text='Specify a valid issue type')
        record = dict(fields)
        self.created.append(record)
        return SimpleNamespace(key=f'JIRA-{len(self.created)}',
                               update=_recorder(record))

    def editmeta(self, issue: str) -> dict[str, object]:
        """Return the edit-screen field metadata for the issue."""
        _ = issue
        return {'fields': {fid: {'name': name}
                           for fid, name in self.editable.items()}}

    def close(self) -> None:
        """Count a close of the stand-in client."""
        self.closed += 1


def _config(project: str = 'PROJ') -> JiraIOConfig:
    """Return a Jira configuration with one connection and one preset."""
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = TokenStorage.CLEAR_INTERNAL
    conn.stored_token = 'TOK'
    preset = JiraPreset(stderr_file=NO)
    preset.connection_name = 'c'
    preset.backlog_column_map_name = 'bk'
    preset.release_column_map_name = 'rel'
    preset.def_project = project
    config = JiraIOConfig(stderr_file=NO)
    config.connections = {'c': conn}
    config.backlog_column_maps = {'bk': DEF_BACKLOG_COLUMN_MAP}
    config.release_column_maps = {'rel': DEF_RELEASE_COLUMN_MAP}
    config.presets = {'w': preset}
    return config


def _issue_config(mapping: dict[int, str], project: str = 'PROJ',
                  ref: str = 'im') -> JiraIOConfig:
    """Return a config whose preset names a level-to-issue-type map."""
    config = _config(project)
    config.issue_type_maps = {ref: mapping}
    config.presets['w'].issue_type_map_name = ref
    return config


def _connections(monkeypatch: pytest.MonkeyPatch, client: _WriteClient,
                 config: Optional[JiraIOConfig] = None) -> JiraConnections:
    """Return a pool whose connections all yield the given fake client."""
    monkeypatch.setattr(jc, '_connect', lambda connection, passphrase: client)
    return JiraConnections(_config() if config is None else config, None)


def _connect_each(clients: list[_WriteClient]
                  ) -> Callable[[object, object], _WriteClient]:
    """Return a stand-in ``_connect`` yielding each client in turn."""
    supply = iter(clients)
    return lambda connection, passphrase: next(supply)


def _item(key: str) -> BacklogItem:
    """Return a default backlog item with a description extra field."""
    return BacklogItem(key=key, level=1, title='T', story_points=5,
                       status=Status.TODO, extra_fields={'description': 'D'})


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
    """Test the listing shows the added, present and failed sections."""
    added = _item('P-1')
    added.title = 'First'
    present = _item('X-9')
    present.title = 'Old'
    bad = _item('E-1')
    bad.title = 'Epic'
    result = AddedToJira(stored=[added], already_present=[present],
                         failed=[FailedItem(bad, 'HTTP 400: nope')],
                         key_map={'A': 'P-1'})
    text = format_add_result(result)
    assert 'Added to Jira (1):' in text
    assert '  P-1  First' in text
    assert 'Already in Jira (1):' in text
    assert '  X-9  Old' in text
    assert 'Failed to add (1):' in text
    assert 'E-1  Epic  - HTTP 400: nope' in text


def test_format_empty() -> None:
    """Test an empty section is shown as a count of zero and (none)."""
    text = format_add_result(AddedToJira([], [], [], {}))
    assert 'Added to Jira (0):' in text
    assert 'Failed to add (0):' in text
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
    client = _WriteClient(valid_types={'Deluppgift', 'Story'})
    connections = _connections(monkeypatch, client,
                               _issue_config({0: 'Deluppgift'}))
    item = BacklogItem(key='T', level=0, title='Sub', story_points=0,
                       status=Status.TODO)
    add_backlog_to_jira(connections, 'w', [item],
                        on_existing_key=OnExistingKey.SKIP, stderr_file=NO)
    assert client.created[0]['issuetype'] == {'name': 'Deluppgift'}


def test_itmap_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a level absent from the map writes the level name."""
    client = _WriteClient(valid_types={'Deluppgift', 'Story'})
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
    client = _WriteClient(valid_types={'Deluppgift', 'Story', 'Epic'})
    connections = _connections(monkeypatch, client)
    item = BacklogItem(key='T', level=0, title='Sub', story_points=0,
                       status=Status.TODO)
    with pytest.raises(UnknownIssueTypeError) as caught:
        add_backlog_to_jira(connections, 'w', [item],
                            on_existing_key=OnExistingKey.SKIP, stderr_file=NO)
    assert 'Sub-Task' in caught.value.bad
    assert not client.created


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
        return {'projects': [{'issuetypes': [{'name': 'Story'},
                                             {'name': 'Subtask'}]}]}


def test_types_via_createmeta() -> None:
    """Test valid types fall back to createmeta when issuetypes refuses."""
    client = cast(JIRA, _MetaClient())
    assert _valid_issue_types(client, 'P') == {'Story', 'Subtask'}


def test_reexport() -> None:
    """Test the package re-exports the add-to-Jira names."""
    assert backlogops.add_backlog_to_jira is add_backlog_to_jira
    assert backlogops.AddedToJira is AddedToJira
    assert backlogops.ExistsInJiraError is ExistsInJiraError
    assert 'add_backlog_to_jira' in backlogops.__all__
    assert 'JiraConnections' in backlogops.__all__
