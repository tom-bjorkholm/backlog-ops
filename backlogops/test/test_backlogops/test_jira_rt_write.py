#! /usr/local/bin/python3
"""Tests for adding and updating remaining time estimates in Jira.

The stand-in Jira clients of the add and update tests accept a time
tracking edit operation, store its remaining estimate and answer the
read-back, so the whole write is checked: the estimate is written as an
edit of whole minutes only while remaining time estimates are used, an
estimate already in Jira is left alone, an empty one never clears Jira,
and an estimate Jira silently ignores is reported as a field not set.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import timedelta
from typing import Optional
import pytest
from backlogops.backlog import BacklogItem, Status
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import (
    DEF_BACKLOG_COLUMN_MAP, JiraAttrPath, JiraAttrType, JiraIOConfig)
from backlogops.jira_update_backlog import (
    UpdatedBacklogInJira, update_backlog_in_jira)
from backlogops import jira_update_backlog
from backlogops.jira_write import (
    AddedToJira, OnExistingKey, OnMissingKey, add_backlog_to_jira)
from .jira_write_helpers import (
    EDITABLE_DEFAULT, NO, WriteClient, connections_for, jira_write_config)
from .test_jira_update_backlog import _Client, _issue, _item

TT_EDITABLE = {**EDITABLE_DEFAULT, 'timetracking': 'Time tracking',
               'customfield_10030': 'Hours left'}
"""An add edit screen offering the time tracking and a numeric field."""


def _edit(minutes: int) -> dict[str, object]:
    """Return the recorded time tracking edit of an estimate in minutes."""
    return {'timetracking': [{'edit': {'remainingEstimate': f'{minutes}m'}}]}


def _rt_config(*attrs: JiraAttrPath) -> JiraIOConfig:
    """Return a write config whose remaining time maps to these paths."""
    config = jira_write_config()
    backlog_map = dict(DEF_BACKLOG_COLUMN_MAP)
    backlog_map['remaining_time'] = attrs
    config.backlog_column_maps = {'bk': backlog_map}
    return config


def _new_item(remaining: Optional[timedelta]) -> BacklogItem:
    """Return a new backlog item carrying a remaining time."""
    return BacklogItem(key='A', level=1, title='T', story_points=5,
                       status=Status.TODO, remaining_time=remaining)


def _add(connections: JiraConnections, item: BacklogItem, use_rt: bool = True,
         stderr: Optional[io.StringIO] = None) -> AddedToJira:
    """Add the item to Jira, using remaining time estimates or not."""
    return add_backlog_to_jira(connections, 'w', [item],
                               on_existing_key=OnExistingKey.SKIP,
                               use_remaining_time=use_rt,
                               stderr_file=NO if stderr is None else stderr)


def _written(client: WriteClient) -> list[dict[str, object]]:
    """Return the updates the add made to the created issue."""
    return [fields for _, fields in client.link_log.updates]


@pytest.mark.parametrize('remaining, minutes', [
    (timedelta(hours=1, seconds=61), 62), (timedelta(hours=2), 120),
    (timedelta(0), 0), (timedelta(microseconds=1), 1)])
def test_add_rt(monkeypatch: pytest.MonkeyPatch, remaining: timedelta,
                minutes: int) -> None:
    """Test an added item's estimate is edited in, rounded up to minutes."""
    client = WriteClient(editable=TT_EDITABLE)
    result = _add(connections_for(monkeypatch, client), _new_item(remaining))
    assert _edit(minutes).items() <= _written(client)[0].items()
    assert client.link_log.time_seconds == {'JIRA-1': minutes * 60}
    assert not result.failed_fields


@pytest.mark.parametrize('remaining, use_rt', [
    (timedelta(hours=2), False), (None, True)])
def test_add_no_rt(monkeypatch: pytest.MonkeyPatch,
                   remaining: Optional[timedelta], use_rt: bool) -> None:
    """Test no estimate is written when unused or when the item has none."""
    client = WriteClient(editable=TT_EDITABLE)
    _add(connections_for(monkeypatch, client), _new_item(remaining), use_rt)
    assert not any('timetracking' in fields for fields in _written(client))
    assert not client.link_log.time_seconds


def test_add_rt_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an estimate Jira accepts but does not store is reported."""
    client = WriteClient(editable=TT_EDITABLE)
    client.link_log.ignore_time = True
    item = _new_item(timedelta(hours=1, seconds=61))
    result = _add(connections_for(monkeypatch, client), item)
    assert [fail.field for fail in result.failed_fields] == ['timetracking']
    assert '3720 s written' in result.failed_fields[0].reason
    assert [stored.key for stored in result.stored] == ['JIRA-1']


def test_add_rt_not_editable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an estimate the edit screen does not offer is warned about."""
    client = WriteClient()
    stderr = io.StringIO()
    result = _add(connections_for(monkeypatch, client),
                  _new_item(timedelta(hours=1)), stderr=stderr)
    assert not client.link_log.time_seconds and not result.failed_fields
    assert 'timetracking' in stderr.getvalue()


def test_add_rt_estimate_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a map reading only timeestimate still writes time tracking."""
    client = WriteClient(editable=TT_EDITABLE)
    config = _rt_config(JiraAttrPath(JiraAttrType.FIELD, ('timeestimate',)))
    _add(connections_for(monkeypatch, client, config),
         _new_item(timedelta(minutes=5)))
    assert _edit(5).items() <= _written(client)[0].items()


def test_add_rt_custom(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a numeric custom field path gets the raw whole seconds."""
    client = WriteClient(editable=TT_EDITABLE)
    config = _rt_config(JiraAttrPath(JiraAttrType.CUSTOM_FIELD,
                                     ('customfield_10030',)))
    _add(connections_for(monkeypatch, client, config),
         _new_item(timedelta(seconds=3661, microseconds=1)))
    assert _written(client)[0]['customfield_10030'] == 3662
    assert not client.link_log.time_seconds


def _update(connections: JiraConnections, item: BacklogItem,
            use_rt: bool = True) -> UpdatedBacklogInJira:
    """Update the item's remaining time in Jira, ignoring missing keys."""
    return update_backlog_in_jira(connections, 'w', [item],
                                  on_missing_key=OnMissingKey.IGNORE,
                                  fields_to_update=['remaining_time'],
                                  use_remaining_time=use_rt, stderr_file=NO)


def _rt_client(remaining: Optional[int]) -> _Client:
    """Return an update client whose issue A has this estimate in seconds."""
    client = _Client({'A': _issue('A', remaining=remaining)})
    client.editable.add('timetracking')
    return client


@pytest.mark.parametrize('current', [None, 3600])
def test_update_rt(monkeypatch: pytest.MonkeyPatch,
                   current: Optional[int]) -> None:
    """Test a differing estimate is edited in and read back as stored."""
    client = _rt_client(current)
    item = _item('A', remaining_time=timedelta(hours=1, seconds=61))
    result = _update(connections_for(monkeypatch, client), item)
    assert result.updated == ['A'] and not result.failed_fields
    assert client.issues['A'].updates == [_edit(62)]


@pytest.mark.parametrize('current, remaining', [
    (3720, timedelta(hours=1, seconds=61)), (3600, timedelta(hours=1)),
    (0, timedelta(0)), (3600, None)])
def test_update_rt_same(monkeypatch: pytest.MonkeyPatch, current: int,
                        remaining: Optional[timedelta]) -> None:
    """Test an estimate Jira already holds, or none, leaves Jira alone.

    An estimate is compared as the whole minutes Jira keeps, and an item
    with no remaining time never clears the estimate in Jira.
    """
    client = _rt_client(current)
    item = _item('A', remaining_time=remaining)
    result = _update(connections_for(monkeypatch, client), item)
    assert result.already_correct == ['A']
    assert not client.issues['A'].updates


def test_update_rt_unused(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a selected estimate is not updated when estimates are unused."""
    client = _rt_client(3600)
    item = _item('A', remaining_time=timedelta(hours=3))
    result = _update(connections_for(monkeypatch, client), item, False)
    assert result.already_correct == ['A']
    assert not client.issues['A'].updates


def test_update_rt_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an update Jira accepts without storing it is reported."""
    client = _rt_client(3600)
    client.issues['A'].ignore_time = True
    item = _item('A', remaining_time=timedelta(hours=3))
    result = _update(connections_for(monkeypatch, client), item)
    assert result.updated == ['A']
    assert [fail.field for fail in result.failed_fields] == ['timetracking']
    assert '10800 s written, 3600 s stored' in result.failed_fields[0].reason


def test_update_adds_with_rt(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing item is added using the update's remaining time use."""
    captured: dict[str, object] = {}

    def add(*args: object, **kwargs: object) -> AddedToJira:
        """Record the remaining time use the add was given."""
        _ = args
        captured['use_rt'] = kwargs.get('use_remaining_time')
        return AddedToJira([], [], [], {}, [], [], [])
    monkeypatch.setattr(jira_update_backlog, 'add_backlog_to_jira', add)
    connections = connections_for(monkeypatch, _rt_client(None))
    update_backlog_in_jira(connections, 'w', [_item('NEW')],
                           on_missing_key=OnMissingKey.ADD,
                           fields_to_update=['remaining_time'],
                           use_remaining_time=True, stderr_file=NO)
    assert captured['use_rt'] is True
