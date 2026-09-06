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
from typing import Callable, Optional, cast
import pytest
from jira import Issue, JIRAError
import backlogops
from backlogops import JiraRankAnchor
from backlogops.backlog import BacklogItem, Status
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType, JiraColumnMap
from backlogops.jira_write import (
    AddedToJira, FailedItem, ItemNotInJiraError, OnExistingKey, OnMissingKey)
from backlogops.jira_write_status import StatusMismatch
from backlogops.jira_write_fields import (
    FailedField, FailedLink, _LinkSpec, _clear_parent_fields)
from backlogops import jira_update_backlog
from backlogops.jira_update_backlog import (
    LinkUpdate, UpdatedBacklogInJira, format_backlog_updates,
    updatable_backlog_fields, update_backlog_in_jira, _find_link_id)
from .jira_write_helpers import (
    attr_parent_config, connections_for as _connections, NO, RankCall,
    capture_rank)

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
           points: Optional[float] = 5.0, team: Optional[str] = None,
           status: str = 'To Do', parent: Optional[str] = None,
           release: Optional[str] = None,
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
    """A fake Jira issue that records or refuses its field updates.

    ``fail`` refuses every update, while ``fail_fields`` refuses only an
    update carrying one of the named fields, as Jira does for a value it
    cannot accept. A refused update is recorded in ``refused`` and none of
    its fields is merged, so a retry one field at a time is observable.
    """

    def __init__(self, key: str, fields: SimpleNamespace, fail: bool) -> None:
        """Start with the key, the current fields and the failing flag."""
        self.key = key
        self.fields = fields
        self.fail = fail
        self.fail_fields: set[str] = set()
        self.updates: list[dict[str, object]] = []
        self.refused: list[dict[str, object]] = []

    def update(self, fields: dict[str, object]) -> None:
        """Record the update and merge it, or raise when set to fail."""
        if self.fail or self.fail_fields & set(fields):
            self.refused.append(dict(fields))
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
        self.fail_editmeta = False
        self.versions = {'R1', 'R2'}
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
        """Return the edit-screen field metadata, or raise when set to."""
        _ = key
        if self.fail_editmeta:
            raise JIRAError(status_code=500, text='no edit screen')
        return {'fields': {fid: {'name': fid} for fid in self.editable}}

    def project_versions(self, project: str) -> list[SimpleNamespace]:
        """Return the project's versions, each carrying its name."""
        _ = project
        return [SimpleNamespace(name=name) for name in sorted(self.versions)]

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


def test_clear_points(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an item nobody has estimated clears the Jira story points."""
    client = _Client({'A': _issue('A', points=5.0)})
    connections = _connections(monkeypatch, client)
    item = _item('A', story_points=None)
    result = _upd(connections, [item], ['story_points'])
    assert result.updated == ['A']
    assert client.issues['A'].updates == [{'customfield_10016': None}]


def test_points_stay_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an unestimated item and an empty Jira field need no change."""
    client = _Client({'A': _issue('A', points=None)})
    connections = _connections(monkeypatch, client)
    item = _item('A', story_points=None)
    result = _upd(connections, [item], ['story_points'])
    assert result.already_correct == ['A']
    assert client.issues['A'].updates == []


@pytest.mark.parametrize('points', [0.0, 0.5, 13.0])
def test_points_written(monkeypatch: pytest.MonkeyPatch,
                        points: float) -> None:
    """Test an estimate of zero, of a fraction and of a whole is written.

    Zero story points are an estimate somebody made rather than a missing
    one, so they are written although an empty value would not be.
    """
    client = _Client({'A': _issue('A', points=None)})
    connections = _connections(monkeypatch, client)
    item = _item('A', story_points=points)
    _upd(connections, [item], ['story_points'])
    assert client.issues['A'].updates == [{'customfield_10016': points}]


def test_clear_points_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a clear the edit screen has no field for is reported."""
    client = _Client({'A': _issue('A', points=5.0)})
    client.editable = {'summary'}
    connections = _connections(monkeypatch, client)
    errors = io.StringIO()
    item = _item('A', story_points=None)
    result = _upd(connections, [item], ['story_points'], stderr=errors)
    assert result.already_correct == ['A']
    assert client.issues['A'].updates == []
    assert 'customfield_10016' in errors.getvalue()


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


def test_parent_same(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a parent already matching the item needs no change."""
    client = _Client({'A': _issue('A', parent='SAME')})
    connections = _connections(monkeypatch, client)
    item = _item('A', parent_key='SAME')
    result = _upd(connections, [item], ['parent_key'])
    assert result.already_correct == ['A']
    assert client.issues['A'].updates == []


@pytest.mark.parametrize('attr, expected', [
    (None, {}),
    (JiraAttrPath(JiraAttrType.CUSTOM_FIELD, ('customfield_10001',)),
     {'customfield_10001': None}),
    (JiraAttrPath(JiraAttrType.CUSTOM_FIELD, ('Unknown',)), {}),
    (JiraAttrPath(JiraAttrType.FIELD, ('parent',)), {'parent': None}),
    (JiraAttrPath(JiraAttrType.ATTRIBUTE, ('parent',)), {})])
def test_clear_parent_fields(attr: Optional[JiraAttrPath],
                             expected: dict[str, object]) -> None:
    """Test the parent-clear fields depend on the mapped path kind."""
    column_map: JiraColumnMap = (
        {} if attr is None else {'parent_key': (attr,)})
    assert _clear_parent_fields(column_map, {}) == expected


def test_set_attr_parent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test setting a parent mapped to no writable field writes nothing."""
    client = _Client({'A': _issue('A')})
    connections = _connections(monkeypatch, client, attr_parent_config())
    _upd(connections, [_item('A', parent_key='NEW')], ['parent_key'])
    assert client.issues['A'].updates == []


def test_clear_attr_parent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test clearing a parent mapped to no writable field writes nothing."""
    client = _Client({'A': _issue('A')})
    setattr(client.issues['A'], 'parent', 'OLD')
    connections = _connections(monkeypatch, client, attr_parent_config())
    _upd(connections, [_item('A', parent_key=None)], ['parent_key'])
    assert client.issues['A'].updates == []


def test_dep_add(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing dependency link makes the dependency block the item.

    ``A`` depends on ``B``, so the link is created from ``B`` to ``A`` and
    Jira shows ``A`` as blocked by ``B``, the inverse of reading it from
    ``inwardIssue.key``.
    """
    client = _Client({'A': _issue('A')})
    connections = _connections(monkeypatch, client)
    item = _item('A', depends_on_f2s=['B'])
    result = _upd(connections, [item], ['depends_on_f2s'])
    assert result.updated == ['A']
    assert client.created_links == [('Blocks', 'B', 'A')]


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
    assert client.created_links == [('Blocks', 'C', 'A')]
    assert not client.deleted_links


def test_dep_not_selected(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a dependency field not selected is left untouched."""
    client = _Client({'A': _issue('A', links=[_blocks('B', 'L9')])})
    connections = _connections(monkeypatch, client)
    item = _item('A', title='New', depends_on_f2s=[])
    result = _upd(connections, [item], ['title'])
    assert result.updated == ['A']
    assert not client.deleted_links


def _bad_id_link(dep: str) -> SimpleNamespace:
    """Return a Blocks issuelink whose id is not a string."""
    return SimpleNamespace(id=None, type=SimpleNamespace(name='Blocks'),
                           inwardIssue=SimpleNamespace(key=dep))


def test_find_link_id() -> None:
    """Test the link id lookup matches type and side, else returns None."""
    spec = _LinkSpec('depends_on_f2s', 'Blocks', True)
    good = cast(Issue, SimpleNamespace(
        fields=SimpleNamespace(issuelinks=[_blocks('B')])))
    assert _find_link_id(good, spec, 'B') == 'L1'
    assert _find_link_id(good, spec, 'OTHER') is None
    no_list = cast(Issue, SimpleNamespace(
        fields=SimpleNamespace(issuelinks=None)))
    assert _find_link_id(no_list, spec, 'B') is None
    bad = cast(Issue, SimpleNamespace(
        fields=SimpleNamespace(issuelinks=[_bad_id_link('B')])))
    assert _find_link_id(bad, spec, 'B') is None


def test_remove_link_no_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test removing a link with no usable id deletes nothing."""
    client = _Client({'A': _issue('A', links=[_bad_id_link('B')])})
    connections = _connections(monkeypatch, client)
    _upd(connections, [_item('A', depends_on_f2s=[])], ['depends_on_f2s'])
    assert not client.deleted_links


def test_update_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused field value is reported and the others still run.

    The item is still counted as updated, the way an item whose link Jira
    refused is, because the change was needed.
    """
    client = _Client({'A': _issue('A', summary='Old', fail=True),
                      'B': _issue('B', summary='Old')})
    connections = _connections(monkeypatch, client)
    backlog = [_item('A', title='New'), _item('B', title='New')]
    result = _upd(connections, backlog, ['title'])
    assert result.updated == ['A', 'B']
    assert [bad.item.key for bad in result.failed_fields] == ['A']
    assert result.failed_fields[0].field == 'summary'
    assert 'HTTP 400' in result.failed_fields[0].reason


def test_update_field_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the fields Jira accepts are still written after a refusal.

    Jira applies an update as a whole, so the refused update is retried
    one field at a time and only the refused value is lost.
    """
    issue = _issue('A', summary='Old', release=None)
    issue.fail_fields = {'fixVersions'}
    connections = _connections(monkeypatch, _Client({'A': issue}))
    item = _item('A', title='New')
    item.release = 'R1'
    result = _upd(connections, [item], ['title', 'release'])
    assert issue.fields.summary == 'New'
    assert len(issue.refused) == 2
    assert result.updated == ['A']
    assert [bad.field for bad in result.failed_fields] == ['fixVersions']


def test_rest_still_run(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused field leaves the status and links still updated."""
    issue = _issue('A', summary='Old', status='To Do', fail=True)
    trans: list[dict[str, object]] = [{'id': '11', 'to': {'name': 'Done'}}]
    client = _Client({'A': issue}, transitions=trans)
    connections = _connections(monkeypatch, client)
    item = _item('A', title='New', status=Status.DONE, depends_on_f2s=['B'])
    result = _upd(connections, [item], ['title', 'status', 'depends_on_f2s'],
                  status_map=SMAP)
    assert client.transitioned == [('A', '11')]
    assert client.created_links == [('Blocks', 'B', 'A')]
    assert result.updated == ['A']
    assert [bad.field for bad in result.failed_fields] == ['summary']


def test_no_edit_screen(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an unreadable edit screen refuses fields and continues.

    The run no longer stops part-way: the item's fields are all reported
    refused and the remaining items are still updated.
    """
    client = _Client({'A': _issue('A', summary='Old'),
                      'B': _issue('B', summary='Old')})
    client.fail_editmeta = True
    connections = _connections(monkeypatch, client)
    backlog = [_item('A', title='New'), _item('B', title='New')]
    result = _upd(connections, backlog, ['title'])
    assert result.updated == ['A', 'B']
    assert [bad.item.key for bad in result.failed_fields] == ['A', 'B']
    assert 'HTTP 500' in result.failed_fields[0].reason


def test_refused_warned(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused field value is warned about, naming the field."""
    client = _Client({'A': _issue('A', summary='Old', fail=True)})
    connections = _connections(monkeypatch, client)
    errors = io.StringIO()
    _upd(connections, [_item('A', title='New')], ['title'], stderr=errors)
    text = errors.getvalue()
    assert 'A field summary was not set' in text
    assert 'HTTP 400' in text


def test_unknown_release(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a release the project has no version of is reported."""
    client = _Client({'A': _issue('A')})
    connections = _connections(monkeypatch, client)
    item = _item('A')
    item.release = 'Next'
    errors = io.StringIO()
    _upd(connections, [item], ['release'], stderr=errors)
    assert 'not a version of Jira project PROJ: Next' in errors.getvalue()


def test_release_unpicked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an unknown release is quiet when the release is not selected."""
    client = _Client({'A': _issue('A')})
    connections = _connections(monkeypatch, client)
    item = _item('A')
    item.release = 'Next'
    errors = io.StringIO()
    _upd(connections, [item], ['title'], stderr=errors)
    assert 'not a version' not in errors.getvalue()


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
    added = AddedToJira([added_item], [], [], {'NEW': 'JIRA-9'}, [], [], [])
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
    assert client.created_links == [('Blocks', 'JIRA-9', 'A')]


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
    """Test the listing shows the sections with their entries.

    The refused field values of the updated items and of the added items
    are shown together, as the status mismatches and links are.
    """
    failed = FailedItem(_item('E-1'), 'HTTP 400: nope')
    added_item = _item('P-1')
    added = AddedToJira([added_item], [], [failed], {}, [],
                        [FailedField(added_item, 'team', 'HTTP 400: team')],
                        [])
    result = UpdatedBacklogInJira(
        updated=['A'], already_correct=['B'], ignored=['C'],
        failed_fields=[FailedField(_item('F-1'), 'fixVersions', 'no such')],
        status_mismatch=[StatusMismatch(_item('M'), Status.DONE, 'To Do')],
        failed_links=[FailedLink(_item('L'), 'X', 'Blocks', 'nope')],
        added=added)
    text = format_backlog_updates(result)
    assert 'Updated in Jira (1):' in text and '  A' in text
    assert 'Already correct in Jira (1):' in text and '  B' in text
    assert 'Not in Jira (ignored) (1):' in text and '  C' in text
    assert 'Added to Jira (1):' in text and 'P-1' in text
    assert 'Failed to add (1):' in text and 'E-1' in text
    assert 'Status not set in Jira (1):' in text
    assert 'Fields not set (2):' in text
    assert 'F-1  fixVersions  - no such' in text
    assert 'P-1  team  - HTTP 400: team' in text
    assert 'Links not written (1):' in text
    assert text.startswith('NOT EVERYTHING SUCCEEDED IN JIRA:\n'
                           '  Failed to add: 1\n'
                           '  Status not set in Jira: 1\n'
                           '  Fields not set: 2\n'
                           '  Links not written: 1\n'
                           'Skipped:\n'
                           '  Not in Jira (ignored): 1\n')
    assert text.index('Fields not set (2):') < text.index('Updated in Jira')


def test_format_empty() -> None:
    """Test an empty section is shown as a count of zero and (none)."""
    empty = AddedToJira([], [], [], {}, [], [], [])
    text = format_backlog_updates(
        UpdatedBacklogInJira([], [], [], [], [], [], empty))
    assert 'Updated in Jira (0):' in text
    assert 'Added to Jira (0):' in text
    assert 'Fields not set (0):' in text
    assert '(none)' in text
    assert text.startswith('Everything requested succeeded in Jira.\n')


def test_reexport() -> None:
    """Test the package re-exports the update-backlog names."""
    assert backlogops.update_backlog_in_jira is update_backlog_in_jira
    assert backlogops.UpdatedBacklogInJira is UpdatedBacklogInJira
    assert backlogops.LinkUpdate is LinkUpdate
    assert backlogops.format_backlog_updates is format_backlog_updates
    assert backlogops.updatable_backlog_fields is updatable_backlog_fields
    assert 'update_backlog_in_jira' in backlogops.__all__
    assert 'LinkUpdate' in backlogops.__all__


def test_update_rank_wiring(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test present items are ranked in supplied order at the anchor."""
    record = RankCall()
    monkeypatch.setattr(jira_update_backlog, 'rank_backlog_or_warn',
                        capture_rank(record))
    client = _Client({'A': _issue('A'), 'B': _issue('B')})
    connections = _connections(monkeypatch, client)
    update_backlog_in_jira(connections, 'w', [_item('A'), _item('B')],
                           on_missing_key=OnMissingKey.IGNORE,
                           fields_to_update=['title'],
                           rank_anchor=JiraRankAnchor.BACKLOG_TOP)
    assert [item.key for item in record.present] == ['A', 'B']
    assert not record.key_map
    assert record.anchor is JiraRankAnchor.BACKLOG_TOP


def test_rank_skips_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an item not present in Jira is left out of the ranking."""
    record = RankCall()
    monkeypatch.setattr(jira_update_backlog, 'rank_backlog_or_warn',
                        capture_rank(record))
    connections = _connections(monkeypatch, _Client({'A': _issue('A')}))
    update_backlog_in_jira(connections, 'w', [_item('A'), _item('B')],
                           on_missing_key=OnMissingKey.IGNORE,
                           fields_to_update=['title'],
                           rank_anchor=JiraRankAnchor.BACKLOG_TOP)
    assert [item.key for item in record.present] == ['A']


def test_no_rank_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the ranking is not run when no anchor is given."""
    record = RankCall()
    monkeypatch.setattr(jira_update_backlog, 'rank_backlog_or_warn',
                        capture_rank(record))
    connections = _connections(monkeypatch, _Client({'A': _issue('A')}))
    update_backlog_in_jira(connections, 'w', [_item('A')],
                           on_missing_key=OnMissingKey.IGNORE,
                           fields_to_update=['title'])
    assert not record.called
