#! /usr/local/bin/python3
"""Tests for updating a backlog in Jira.

A stand-in Jira client answers ``issue`` with fake issues that carry their
current field values, status, parent and issue links and record or refuse
updates, transitions and link changes, so the field diff, the selected-only
update, the already-correct detection, the status transition, the parent and
dependency link reconciliation, the missing-key policies (raise, ignore,
add) and the never-mutated argument are checked without a real server. The
add path for missing items is replaced by a stand-in, since it is tested in
full elsewhere.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from types import SimpleNamespace
from typing import Callable, Optional
import pytest
from jira import JIRAError
import backlogops
from backlogops.backlog import BacklogItem, Status
from backlogops.jira_connect import JiraConnections
from backlogops.jira_write import (
    AddedToJira, FailedItem, ItemNotInJiraError, OnExistingKey, OnMissingKey,
    StatusMismatch)
from backlogops.jira_write_fields import FailedLink
from backlogops import jira_update_backlog
from backlogops.jira_update_backlog import (
    LinkUpdate, UpdatedBacklogInJira, format_backlog_updates,
    updatable_backlog_fields, update_backlog_in_jira)
from .jira_write_helpers import connections_for as _connections, NO

FIELDS: list[dict[str, str]] = [
    {'id': 'customfield_10016', 'name': 'Story point estimate'},
    {'id': 'customfield_10001', 'name': 'Team'}]
"""Field descriptors resolving the two custom fields used on update."""

_EDITABLE = {'summary', 'description', 'customfield_10016',
             'customfield_10001', 'fixVersions'}
"""Field ids the fake issue's edit screen offers by default."""

SMAP: dict[str, Status] = {'To Do': Status.TODO, 'Done': Status.DONE,
                           'In Progress': Status.IN_PROGRESS}
"""A status map from Jira status names to internal statuses."""


def _blocks(dep: str, link_id: str = 'L1') -> SimpleNamespace:
    """Return an issuelink where a dependency blocks the current issue."""
    return SimpleNamespace(id=link_id, type=SimpleNamespace(name='Blocks'),
                           inwardIssue=SimpleNamespace(key=dep))


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _issue(key: str, *, summary: str = 'T', description: str = 'D',
           points: int = 5, team: Optional[str] = None, status: str = 'To Do',
           parent: Optional[str] = None, release: Optional[str] = None,
           links: Optional[list[SimpleNamespace]] = None,
           fail: bool = False) -> '_Issue':
    """Return a fake issue whose fields hold the given current values."""
    fields = SimpleNamespace(
        summary=summary, description=description, customfield_10016=points,
        customfield_10001=team, status=SimpleNamespace(name=status),
        parent=(SimpleNamespace(key=parent) if parent is not None else None),
        fixVersions=([SimpleNamespace(name=release)]
                     if release is not None else []),
        issuelinks=(links or []))
    return _Issue(key, fields, fail)


# pylint: disable-next=too-few-public-methods
class _Issue:
    """A fake Jira issue that records or refuses its field updates."""

    def __init__(self, key: str, fields: SimpleNamespace, fail: bool) -> None:
        """Start with the key, the current fields and the failing flag."""
        self.key = key
        self.fields = fields
        self.fail = fail
        self.updates: list[dict[str, object]] = []

    def update(self, fields: dict[str, object]) -> None:
        """Record the update and merge it, or raise when set to fail."""
        if self.fail:
            raise JIRAError(status_code=400, text='update rejected')
        self.updates.append(dict(fields))
        for name, value in fields.items():
            setattr(self.fields, name, value)


# pylint: disable-next=too-many-instance-attributes
class _Client:
    """A stand-in Jira client for the update-backlog tests."""

    def __init__(self, issues: dict[str, _Issue],
                 transitions: Optional[list[dict[str, object]]] = None,
                 fail_link: Optional[set[str]] = None,
                 fail_transition: bool = False) -> None:
        """Start with the present issues, transitions and failure knobs."""
        self.issues = issues
        self._transitions = transitions or []
        self.fail_link = set() if fail_link is None else set(fail_link)
        self.fail_transition = fail_transition
        self.editable = set(_EDITABLE)
        self.created_links: list[tuple[str, str, str]] = []
        self.deleted_links: list[str] = []
        self.transitioned: list[tuple[str, str]] = []

    def myself(self) -> dict[str, str]:
        """Report a live session for the connection pool."""
        return {'name': 'tester'}

    def fields(self) -> list[dict[str, str]]:
        """Return the canned field descriptors."""
        return FIELDS

    def issue(self, key: str) -> _Issue:
        """Return the issue for a present key, or raise for an absent one."""
        if key in self.issues:
            return self.issues[key]
        raise JIRAError(status_code=404, text='not found')

    def createmeta_issuetypes(self, project: str) -> dict[str, object]:
        """Return one creatable issue type as create metadata."""
        _ = project
        return {'values': [{'name': 'Story', 'subtask': False}]}

    def createmeta(self, **kwargs: object) -> dict[str, object]:
        """Return one creatable issue type via the older createmeta API."""
        _ = kwargs
        return {'projects': [{'issuetypes': [{'name': 'Story'}]}]}

    def editmeta(self, key: str) -> dict[str, object]:
        """Return the edit-screen field metadata for the issue."""
        _ = key
        return {'fields': {fid: {'name': fid} for fid in self.editable}}

    def transitions(self, issue: _Issue) -> list[dict[str, object]]:
        """Return the configured available workflow transitions."""
        _ = issue
        return list(self._transitions)

    def transition_issue(self, issue: _Issue, transition: str) -> None:
        """Apply a transition, updating the status, or raise when set to."""
        if self.fail_transition:
            raise JIRAError(status_code=400, text='transition rejected')
        for trans in self._transitions:
            if trans.get('id') == transition:
                to_field = trans.get('to')
                assert isinstance(to_field, dict)
                issue.fields.status.name = to_field['name']
        self.transitioned.append((issue.key, transition))

    def create_issue_link(self, link_type: str, inward: str, outward: str,
                          comment: Optional[dict[str, object]] = None) -> None:
        """Record a created issue link, or refuse a failing endpoint."""
        _ = comment
        if inward in self.fail_link or outward in self.fail_link:
            raise JIRAError(status_code=400, text='link rejected')
        self.created_links.append((link_type, inward, outward))

    def delete_issue_link(self, link_id: str) -> None:
        """Record a deleted issue link, or refuse a failing id."""
        if link_id in self.fail_link:
            raise JIRAError(status_code=400, text='unlink rejected')
        self.deleted_links.append(link_id)

    def close(self) -> None:
        """Ignore a close of the stand-in client."""


def _item(key: str, **kwargs: object) -> BacklogItem:
    """Return a default backlog item matching the default fake issue."""
    base: dict[str, object] = {'level': 1, 'title': 'T', 'story_points': 5,
                               'status': Status.TODO,
                               'extra_fields': {'description': 'D'}}
    base.update(kwargs)
    return BacklogItem(key=key, **base)  # type: ignore[arg-type]


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _upd(connections: JiraConnections, backlog: list[BacklogItem],
         fields: list[str], mode: OnMissingKey = OnMissingKey.IGNORE,
         link: LinkUpdate = LinkUpdate.RECONCILE,
         status_map: Optional[dict[str, Status]] = None,
         stderr: Optional[io.StringIO] = None) -> UpdatedBacklogInJira:
    """Update the backlog with the given fields, mode and link policy."""
    sink = NO if stderr is None else stderr
    return update_backlog_in_jira(connections, 'w', backlog,
                                  on_missing_key=mode, fields_to_update=fields,
                                  link_update=link, status_map=status_map,
                                  stderr_file=sink)


def test_update_field(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a differing selected field is written and reported updated."""
    client = _Client({'A': _issue('A', summary='Old')})
    connections = _connections(monkeypatch, client)
    result = _upd(connections, [_item('A', title='New')], ['title'])
    assert result.updated == ['A'] and not result.already_correct
    assert client.issues['A'].updates == [{'summary': 'New'}]


def test_already_correct(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an item whose selected fields already match is not touched."""
    client = _Client({'A': _issue('A', summary='T')})
    connections = _connections(monkeypatch, client)
    result = _upd(connections, [_item('A', title='T')], ['title'])
    assert result.already_correct == ['A'] and not result.updated
    assert client.issues['A'].updates == []


def test_only_selected(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an unselected differing field is left untouched."""
    client = _Client({'A': _issue('A', summary='Old', points=1)})
    connections = _connections(monkeypatch, client)
    item = _item('A', title='New', story_points=9)
    result = _upd(connections, [item], ['title'])
    assert result.updated == ['A']
    assert client.issues['A'].updates == [{'summary': 'New'}]


def test_diff_only_written(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test only the differing selected field is written."""
    client = _Client({'A': _issue('A', summary='T', points=1)})
    connections = _connections(monkeypatch, client)
    item = _item('A', title='T', story_points=9)
    _upd(connections, [item], ['title', 'story_points'])
    assert client.issues['A'].updates == [{'customfield_10016': 9}]


def test_empty_left_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an empty internal value never clears a Jira field."""
    client = _Client({'A': _issue('A', team='Alpha')})
    connections = _connections(monkeypatch, client)
    result = _upd(connections, [_item('A', team=None)], ['team'])
    assert result.already_correct == ['A']
    assert client.issues['A'].updates == []


def test_status_transition(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a selected differing status is fixed by a transition."""
    client = _Client({'A': _issue('A', status='To Do')},
                     transitions=[{'id': '21', 'to': {'name': 'Done'}}])
    connections = _connections(monkeypatch, client)
    item = _item('A', status=Status.DONE)
    result = _upd(connections, [item], ['status'], status_map=SMAP)
    assert result.updated == ['A']
    assert client.transitioned == [('A', '21')]
    assert not result.status_mismatch


def test_status_already(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a status already matching needs no transition."""
    client = _Client({'A': _issue('A', status='Done')},
                     transitions=[{'id': '21', 'to': {'name': 'Done'}}])
    connections = _connections(monkeypatch, client)
    item = _item('A', status=Status.DONE)
    result = _upd(connections, [item], ['status'], status_map=SMAP)
    assert result.already_correct == ['A']
    assert not client.transitioned


def test_status_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an unreachable status is reported as a mismatch, still updated."""
    client = _Client({'A': _issue('A', status='To Do')},
                     transitions=[{'id': '11', 'to': {'name': 'In Progress'}}])
    connections = _connections(monkeypatch, client)
    item = _item('A', status=Status.DONE)
    result = _upd(connections, [item], ['status'], status_map=SMAP)
    assert result.updated == ['A']
    assert [bad.item.key for bad in result.status_mismatch] == ['A']
    assert result.status_mismatch[0].expected is Status.DONE


def test_parent_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a differing parent is written through the mapped parent field."""
    client = _Client({'A': _issue('A', parent='OLD')})
    connections = _connections(monkeypatch, client)
    item = _item('A', parent_key='NEW')
    result = _upd(connections, [item], ['parent_key'])
    assert result.updated == ['A']
    assert client.issues['A'].updates == [{'parent': {'key': 'NEW'}}]


def test_parent_add_keep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test add-missing leaves an existing different parent untouched."""
    client = _Client({'A': _issue('A', parent='OLD')})
    connections = _connections(monkeypatch, client)
    item = _item('A', parent_key='NEW')
    result = _upd(connections, [item], ['parent_key'],
                  link=LinkUpdate.ADD_MISSING)
    assert result.already_correct == ['A']
    assert client.issues['A'].updates == []


def test_parent_add_sets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test add-missing sets the parent when the issue has none."""
    client = _Client({'A': _issue('A', parent=None)})
    connections = _connections(monkeypatch, client)
    item = _item('A', parent_key='NEW')
    result = _upd(connections, [item], ['parent_key'],
                  link=LinkUpdate.ADD_MISSING)
    assert result.updated == ['A']
    assert client.issues['A'].updates == [{'parent': {'key': 'NEW'}}]


def test_reconcile_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test reconcile clears a parent the item no longer has."""
    client = _Client({'A': _issue('A', parent='OLD')})
    connections = _connections(monkeypatch, client)
    item = _item('A', parent_key=None)
    result = _upd(connections, [item], ['parent_key'])
    assert result.updated == ['A']
    assert client.issues['A'].updates == [{'parent': None}]


def test_dep_add(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing dependency link is created in the read direction."""
    client = _Client({'A': _issue('A')})
    connections = _connections(monkeypatch, client)
    item = _item('A', depends_on_f2s=['B'])
    result = _upd(connections, [item], ['depends_on_f2s'])
    assert result.updated == ['A']
    assert client.created_links == [('Blocks', 'A', 'B')]


def test_dep_already(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a dependency already linked needs no change."""
    client = _Client({'A': _issue('A', links=[_blocks('B')])})
    connections = _connections(monkeypatch, client)
    item = _item('A', depends_on_f2s=['B'])
    result = _upd(connections, [item], ['depends_on_f2s'])
    assert result.already_correct == ['A']
    assert not client.created_links and not client.deleted_links


def test_dep_reconcile_remove(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test reconcile removes a Jira dependency the backlog no longer has."""
    client = _Client({'A': _issue('A', links=[_blocks('B', 'L9')])})
    connections = _connections(monkeypatch, client)
    result = _upd(connections, [_item('A', depends_on_f2s=[])],
                  ['depends_on_f2s'])
    assert result.updated == ['A']
    assert client.deleted_links == ['L9']


def test_dep_add_missing_keep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test add-missing keeps a stale dependency and adds a new one."""
    client = _Client({'A': _issue('A', links=[_blocks('B', 'L9')])})
    connections = _connections(monkeypatch, client)
    item = _item('A', depends_on_f2s=['C'])
    result = _upd(connections, [item], ['depends_on_f2s'],
                  link=LinkUpdate.ADD_MISSING)
    assert result.updated == ['A']
    assert client.created_links == [('Blocks', 'A', 'C')]
    assert not client.deleted_links


def test_dep_not_selected(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a dependency field not selected is left untouched."""
    client = _Client({'A': _issue('A', links=[_blocks('B', 'L9')])})
    connections = _connections(monkeypatch, client)
    item = _item('A', title='New', depends_on_f2s=[])
    result = _upd(connections, [item], ['title'])
    assert result.updated == ['A']
    assert not client.deleted_links


def test_update_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused field update is reported and the others still run."""
    client = _Client({'A': _issue('A', summary='Old', fail=True),
                      'B': _issue('B', summary='Old')})
    connections = _connections(monkeypatch, client)
    backlog = [_item('A', title='New'), _item('B', title='New')]
    result = _upd(connections, backlog, ['title'])
    assert result.updated == ['B']
    assert [entry.item.key for entry in result.failed] == ['A']
    assert 'HTTP 400' in result.failed[0].reason


def test_link_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused link is collected and the item still counts updated."""
    client = _Client({'A': _issue('A')}, fail_link={'B'})
    connections = _connections(monkeypatch, client)
    errors = io.StringIO()
    item = _item('A', depends_on_f2s=['B'])
    result = _upd(connections, [item], ['depends_on_f2s'], stderr=errors)
    assert result.updated == ['A']
    assert [link.target for link in result.failed_links] == ['B']
    assert 'A' in errors.getvalue()


def test_skipped_field(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a selected field the edit screen omits is skipped and reported."""
    client = _Client({'A': _issue('A', points=1)})
    client.editable = {'summary'}
    connections = _connections(monkeypatch, client)
    errors = io.StringIO()
    item = _item('A', story_points=9)
    result = _upd(connections, [item], ['story_points'], stderr=errors)
    assert result.already_correct == ['A']
    assert client.issues['A'].updates == []
    assert 'customfield_10016' in errors.getvalue()


def test_missing_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing key raises before anything is changed."""
    client = _Client({'A': _issue('A', summary='Old')})
    connections = _connections(monkeypatch, client)
    backlog = [_item('A', title='New'), _item('B')]
    with pytest.raises(ItemNotInJiraError) as caught:
        _upd(connections, backlog, ['title'], mode=OnMissingKey.RAISE)
    assert caught.value.names == ['B']
    assert client.issues['A'].updates == []


def test_missing_ignore(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing key is ignored and the present items still update."""
    client = _Client({'A': _issue('A', summary='Old')})
    connections = _connections(monkeypatch, client)
    backlog = [_item('A', title='New'), _item('B')]
    result = _upd(connections, backlog, ['title'], mode=OnMissingKey.IGNORE)
    assert result.updated == ['A'] and result.ignored == ['B']
    assert not result.added.stored


def _stub_add(captured: dict[str, object], result: AddedToJira
              ) -> Callable[..., AddedToJira]:
    """Return a stand-in add recording the missing items and the mode."""
    def add(connections: object, preset: str, backlog: list[BacklogItem], *,
            on_existing_key: OnExistingKey, **kwargs: object) -> AddedToJira:
        """Record the added keys and the existing-key mode."""
        _ = (connections, preset, kwargs)
        captured['added'] = [item.key for item in backlog]
        captured['mode'] = on_existing_key
        return result
    return add


def test_missing_add(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing key is added and its Jira key remaps a dependency.

    The real add is replaced by a stand-in; the update remaps an existing
    item's dependency on the newly added item to the assigned Jira key.
    """
    added_item = BacklogItem(key='JIRA-9', level=1, title='New',
                             story_points=0, status=Status.TODO)
    added = AddedToJira([added_item], [], [], {'NEW': 'JIRA-9'}, [], [])
    captured: dict[str, object] = {}
    monkeypatch.setattr(jira_update_backlog, 'add_backlog_to_jira',
                        _stub_add(captured, added))
    client = _Client({'A': _issue('A')})
    connections = _connections(monkeypatch, client)
    item = _item('A', depends_on_f2s=['NEW'])
    new = _item('NEW')
    result = _upd(connections, [item, new], ['depends_on_f2s'],
                  mode=OnMissingKey.ADD)
    assert captured['added'] == ['NEW']
    assert captured['mode'] is OnExistingKey.SKIP
    assert result.added is added
    assert client.created_links == [('Blocks', 'A', 'JIRA-9')]


def test_input_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the argument backlog is not modified by an update."""
    client = _Client({'A': _issue('A', summary='Old')})
    connections = _connections(monkeypatch, client)
    item = _item('A', title='New', depends_on_f2s=['B'])
    _upd(connections, [item], ['title', 'depends_on_f2s'])
    assert item.key == 'A' and item.title == 'New'
    assert item.depends_on_f2s == ['B']


def test_updatable_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the updatable fields are the mapped ones minus key and level."""
    connections = _connections(monkeypatch, _Client({}))
    fields = updatable_backlog_fields(connections, 'w')
    assert 'title' in fields and 'status' in fields
    assert 'depends_on_f2s' in fields
    assert 'key' not in fields and 'level' not in fields


def test_ignores_bad_field(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a field name that is not updatable is ignored."""
    client = _Client({'A': _issue('A', summary='T')})
    connections = _connections(monkeypatch, client)
    result = _upd(connections, [_item('A', title='T')], ['key', 'level',
                                                         'nope'])
    assert result.already_correct == ['A']
    assert client.issues['A'].updates == []


def test_format_updates() -> None:
    """Test the listing shows the sections with their entries."""
    failed = FailedItem(_item('E-1'), 'HTTP 400: nope')
    added_item = _item('P-1')
    added = AddedToJira([added_item], [], [], {}, [], [])
    result = UpdatedBacklogInJira(
        updated=['A'], already_correct=['B'], ignored=['C'], failed=[failed],
        status_mismatch=[StatusMismatch(_item('M'), Status.DONE, 'To Do')],
        failed_links=[FailedLink(_item('L'), 'X', 'Blocks', 'nope')],
        added=added)
    text = format_backlog_updates(result)
    assert 'Updated in Jira (1):' in text and '  A' in text
    assert 'Already correct in Jira (1):' in text and '  B' in text
    assert 'Not in Jira (ignored) (1):' in text and '  C' in text
    assert 'Added to Jira (1):' in text and 'P-1' in text
    assert 'Failed to update (1):' in text and 'E-1' in text
    assert 'Status not set in Jira (1):' in text
    assert 'Links not written (1):' in text


def test_format_empty() -> None:
    """Test an empty section is shown as a count of zero and (none)."""
    empty = AddedToJira([], [], [], {}, [], [])
    text = format_backlog_updates(
        UpdatedBacklogInJira([], [], [], [], [], [], empty))
    assert 'Updated in Jira (0):' in text
    assert 'Added to Jira (0):' in text
    assert '(none)' in text


def test_reexport() -> None:
    """Test the package re-exports the update-backlog names."""
    assert backlogops.update_backlog_in_jira is update_backlog_in_jira
    assert backlogops.UpdatedBacklogInJira is UpdatedBacklogInJira
    assert backlogops.LinkUpdate is LinkUpdate
    assert backlogops.format_backlog_updates is format_backlog_updates
    assert backlogops.updatable_backlog_fields is updatable_backlog_fields
    assert 'update_backlog_in_jira' in backlogops.__all__
    assert 'LinkUpdate' in backlogops.__all__
