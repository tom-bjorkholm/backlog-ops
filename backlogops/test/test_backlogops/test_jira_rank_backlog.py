#! /usr/local/bin/python3
"""Tests for ranking a backlog in Jira at a chosen anchor.

A stand-in Jira client holds the rank order and, for the end anchors, the
backlog read is replaced by a fixed one, so a test drives the whole ranking
without a Jira server. The tests check the placement for each anchor, that
the convenience wrapper ranks the backlog keys in order, that
``rank_backlog_or_warn`` remaps added keys and reports a refusal as a
warning, and the anchor-plan and filter helpers directly.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import importlib
import io
from typing import Callable
import pytest
from backlogops import (
    Backlog, BacklogItem, BacklogReleases, BadJiraRankFilter, JiraRankAnchor,
    Status, jira_rank_backlog)
from backlogops.jira_rank_backlog import (
    RankEnv, _anchor_plan, _ensure_rank_order, rank_backlog_or_warn)
from .jira_rank_helpers import FakeRankClient
from .jira_write_helpers import connections_for

_MODULE = importlib.import_module('backlogops.jira_rank_backlog')


def _item(key: str) -> BacklogItem:
    """Return a minimal backlog item carrying only the key."""
    return BacklogItem(key=key, level=1, title=key, story_points=1,
                       status=Status.TODO)


def _reader(order: list[str]) -> Callable[..., BacklogReleases]:
    """Return a stand-in read handing back a backlog of the given keys."""
    def read(connections: object, preset_name: str,
             **kwargs: object) -> BacklogReleases:
        """Ignore the arguments and return the fixed backlog."""
        _ = (connections, preset_name, kwargs)
        return BacklogReleases(backlog=[_item(key) for key in order],
                               releases=[])
    return read


def _run(monkeypatch: pytest.MonkeyPatch, order: list[str], keys: list[str],
         anchor: JiraRankAnchor) -> FakeRankClient:
    """Rank a backlog of ``keys`` over a client holding ``order``."""
    client = FakeRankClient(order)
    connections = connections_for(monkeypatch, client)
    monkeypatch.setattr(_MODULE, 'read_backlog_from_jira', _reader(order))
    backlog: Backlog = [_item(key) for key in keys]
    jira_rank_backlog(connections, 'w', backlog, anchor=anchor)
    return client


def test_first_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test FIRST_KEY keeps the first key fixed and orders the rest after."""
    client = _run(monkeypatch, ['A', 'B', 'C', 'D'], ['C', 'A'],
                  JiraRankAnchor.FIRST_KEY)
    assert client.order == ['B', 'C', 'A', 'D']


def test_last_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test LAST_KEY keeps the last key fixed and orders the rest before."""
    client = _run(monkeypatch, ['A', 'B', 'C', 'D'], ['C', 'A'],
                  JiraRankAnchor.LAST_KEY)
    assert client.order == ['C', 'A', 'B', 'D']


def test_backlog_top(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test BACKLOG_TOP moves the item to the top of the read backlog."""
    client = _run(monkeypatch, ['A', 'B', 'C', 'D'], ['C'],
                  JiraRankAnchor.BACKLOG_TOP)
    assert client.order == ['C', 'A', 'B', 'D']


def test_backlog_bottom(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test BACKLOG_BOTTOM moves the item to the bottom of the backlog."""
    client = _run(monkeypatch, ['A', 'B', 'C', 'D'], ['C'],
                  JiraRankAnchor.BACKLOG_BOTTOM)
    assert client.order == ['A', 'B', 'D', 'C']


def test_single_item_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a one-item backlog with a key anchor ranks nothing."""
    client = _run(monkeypatch, ['A'], ['A'], JiraRankAnchor.FIRST_KEY)
    assert not client.rank_calls


def test_warn_remaps_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test rank_backlog_or_warn ranks by the mapped Jira keys."""
    client = FakeRankClient(['A', 'B', 'C'])
    connections = connections_for(monkeypatch, client)
    present: Backlog = [_item('old1'), _item('old2')]
    key_map = {'old1': 'B', 'old2': 'A'}
    env = RankEnv(connections, 'w', JiraRankAnchor.FIRST_KEY)
    rank_backlog_or_warn(env, present, key_map)
    assert client.order == ['B', 'A', 'C']


def test_warn_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a ranking Jira refuses is reported as a warning, not raised."""
    client = FakeRankClient(['A'], exist=['A'])
    connections = connections_for(monkeypatch, client)
    sink = io.StringIO()
    present: Backlog = [_item('A'), _item('MISSING')]
    env = RankEnv(connections, 'w', JiraRankAnchor.FIRST_KEY, stderr_file=sink)
    rank_backlog_or_warn(env, present, {})
    assert 'WARNING' in sink.getvalue()


@pytest.mark.parametrize('anchor,rest,expected', [
    (JiraRankAnchor.FIRST_KEY, ['X'], (['A', 'B'], False)),
    (JiraRankAnchor.LAST_KEY, ['X'], (['A', 'B'], True)),
    (JiraRankAnchor.BACKLOG_TOP, ['X', 'Y'], (['A', 'B', 'X'], True)),
    (JiraRankAnchor.BACKLOG_BOTTOM, ['X', 'Y'], (['Y', 'A', 'B'], False)),
    (JiraRankAnchor.BACKLOG_TOP, [], (['A', 'B'], False))])
def test_anchor_plan(anchor: JiraRankAnchor, rest: list[str],
                     expected: tuple[list[str], bool]) -> None:
    """Test the anchor plan places the keys and picks the move-before flag."""
    assert _anchor_plan(['A', 'B'], anchor, rest) == expected


@pytest.mark.parametrize('given,expected', [
    ('project = X', 'project = X ORDER BY Rank ASC'),
    ('project = X ORDER BY Rank ASC', 'project = X ORDER BY Rank ASC'),
    ('project = X order by rank', 'project = X order by rank'),
    ('project = X ORDER BY rank asc', 'project = X ORDER BY rank asc')])
def test_ensure_rank_order(given: str, expected: str) -> None:
    """Test the filter gets or keeps an order-by-rank-ascending clause."""
    assert _ensure_rank_order(given) == expected


@pytest.mark.parametrize('given', [
    'project = X ORDER BY priority',
    'project = X order by rank desc',
    'project = X ORDER BY key, rank'])
def test_bad_filter(given: str) -> None:
    """Test a filter ordering by anything but rank is rejected."""
    with pytest.raises(BadJiraRankFilter):
        _ensure_rank_order(given)
