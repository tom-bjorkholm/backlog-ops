#! /usr/local/bin/python3
"""Tests for moving named issues to a chosen anchor of a Jira backlog.

The backlog read is replaced by a fixed one and a stand-in Jira client
holds the rank order, so a test drives the whole move without a Jira
server. The tests check that by default only the listed keys are ranked in
the listed order, that honouring relations pulls descendants and
dependencies with the named issues, how the four anchors place the moved
keys, how keys that are not part of the backlog are classified, and how the
filter is validated.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import importlib
from typing import Callable, Optional
import pytest
from backlogops import (
    Backlog, BacklogItem, BacklogReleases, BadJiraRankFilter, JiraRankAnchor,
    RankedInJira, Status, format_rank_result, jira_rank_move_keys)
from backlogops.jira_rank_move_keys import _descendants, _present_and_absent
from .jira_rank_helpers import FakeRankClient
from .jira_write_helpers import connections_for

# The package re-exports the function under the module's own name, so the
# module object is fetched here to monkeypatch its imported backlog reader.
_MODULE = importlib.import_module('backlogops.jira_rank_move_keys')


def _item(key: str, level: int = 1, parent: Optional[str] = None,
          f2s: Optional[list[str]] = None) -> BacklogItem:
    """Return a minimal backlog item for the move tests."""
    return BacklogItem(key=key, level=level, title=key, story_points=1,
                       status=Status.TODO, parent_key=parent,
                       depends_on_f2s=list(f2s or []))


def _reader(backlog: Backlog) -> Callable[..., BacklogReleases]:
    """Return a stand-in read that hands back the fixed backlog."""
    def read(connections: object, preset_name: str,
             **kwargs: object) -> BacklogReleases:
        """Ignore the arguments and return the fixed backlog."""
        _ = (connections, preset_name, kwargs)
        return BacklogReleases(backlog=list(backlog), releases=[])
    return read


# pylint: disable-next=too-many-arguments
def _move(monkeypatch: pytest.MonkeyPatch, backlog: Backlog, keys: list[str],
          anchor: JiraRankAnchor, *, honor: bool = False,
          exist: Optional[list[str]] = None
          ) -> tuple[RankedInJira, FakeRankClient]:
    """Run a move over a fixed backlog and return the result and client."""
    order = [item.key for item in backlog]
    client = FakeRankClient(order, exist=order if exist is None else exist)
    connections = connections_for(monkeypatch, client)
    monkeypatch.setattr(_MODULE, 'read_backlog_from_jira', _reader(backlog))
    result = jira_rank_move_keys(connections, 'w', keys, anchor=anchor,
                                 honor_relations=honor)
    return result, client


def _tree() -> Backlog:
    """Return E with children S1, S2, plus unrelated A and B."""
    return [_item('E', 2), _item('A'), _item('B'), _item('S1', 1, 'E'),
            _item('S2', 1, 'E')]


def test_only_listed_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the default move ranks only the listed key, not its children."""
    result, client = _move(monkeypatch, _tree(), ['E'],
                           JiraRankAnchor.BACKLOG_BOTTOM)
    assert client.order == ['A', 'B', 'S1', 'S2', 'E']
    assert result.keys_ranked_ok == ['E']


def test_listed_order_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the listed keys are ranked in the order they are given."""
    backlog = [_item('A'), _item('B'), _item('C'), _item('D')]
    _, client = _move(monkeypatch, backlog, ['C', 'A'],
                      JiraRankAnchor.BACKLOG_TOP)
    assert client.order[:2] == ['C', 'A']


def test_first_children(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a parent moved to the top brings its children when honoured."""
    result, client = _move(monkeypatch, _tree(), ['E'],
                           JiraRankAnchor.BACKLOG_TOP, honor=True)
    assert client.order == ['E', 'S1', 'S2', 'A', 'B']
    assert result.keys_ranked_ok == ['E']


def test_last_children(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a parent moved to the bottom brings its children when honoured."""
    result, client = _move(monkeypatch, _tree(), ['E'],
                           JiraRankAnchor.BACKLOG_BOTTOM, honor=True)
    assert client.order == ['A', 'B', 'E', 'S1', 'S2']
    assert result.keys_ranked_ok == ['E']


def test_first_pulls_dep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a prerequisite is pulled to the top with the named item."""
    backlog = [_item('A'), _item('C'), _item('B', 1, None, ['A'])]
    result, client = _move(monkeypatch, backlog, ['B'],
                           JiraRankAnchor.BACKLOG_TOP, honor=True)
    assert client.order == ['A', 'B', 'C']
    assert result.keys_ranked_ok == ['B']


def test_last_keeps_prereq(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a prerequisite is not pulled to the bottom with the item."""
    backlog = [_item('A'), _item('B', 1, None, ['A']), _item('C')]
    _, client = _move(monkeypatch, backlog, ['B'],
                      JiraRankAnchor.BACKLOG_BOTTOM, honor=True)
    assert client.order == ['A', 'C', 'B']


def test_first_key_anchor(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test FIRST_KEY keeps the first listed key and orders the rest after."""
    backlog = [_item('A'), _item('B'), _item('C'), _item('D')]
    _, client = _move(monkeypatch, backlog, ['C', 'A'],
                      JiraRankAnchor.FIRST_KEY)
    assert client.order == ['B', 'C', 'A', 'D']


def test_last_key_anchor(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test LAST_KEY keeps the last listed key and orders the rest before."""
    backlog = [_item('A'), _item('B'), _item('C'), _item('D')]
    _, client = _move(monkeypatch, backlog, ['C', 'A'],
                      JiraRankAnchor.LAST_KEY)
    assert client.order == ['C', 'A', 'B', 'D']


def test_classify_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test keys missing from the backlog are classified and reported."""
    backlog = [_item('A'), _item('B')]
    result, _ = _move(monkeypatch, backlog, ['A', 'GONE', 'OTHER'],
                      JiraRankAnchor.BACKLOG_TOP, exist=['A', 'B', 'OTHER'])
    assert result == RankedInJira(['A'], ['GONE'], ['OTHER'])


def test_no_found_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test naming only absent keys ranks nothing."""
    result, client = _move(monkeypatch, [_item('A')], ['GONE'],
                           JiraRankAnchor.BACKLOG_TOP, exist=['A'])
    assert result.keys_ranked_ok == []
    assert not client.rank_calls


def test_status_map_sent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the levels and status map are forwarded to the backlog read."""
    captured: dict[str, object] = {}

    def read(connections: object, preset_name: str,
             **kwargs: object) -> BacklogReleases:
        """Record the read keyword arguments and return a one-item backlog."""
        _ = (connections, preset_name)
        captured.update(kwargs)
        return BacklogReleases(backlog=[_item('A')], releases=[])
    monkeypatch.setattr(_MODULE, 'read_backlog_from_jira', read)
    connections = connections_for(monkeypatch, FakeRankClient(['A']))
    status = {'To Do': Status.TODO}
    jira_rank_move_keys(connections, 'w', ['A'], status_map=status)
    assert captured['status_map'] == status


def test_bad_filter_run(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a bad filter override is rejected before any backlog is read."""
    connections = connections_for(monkeypatch, FakeRankClient([]))
    with pytest.raises(BadJiraRankFilter):
        jira_rank_move_keys(connections, 'w', ['A'],
                            filter_override='project = X ORDER BY priority')


def test_descendants_cycle() -> None:
    """Test descendant search terminates on a parent-key cycle."""
    backlog = [_item('A', parent='B'), _item('B', parent='A')]
    assert _descendants(backlog, ['A']) == {'A', 'B'}


def test_present_dedup() -> None:
    """Test a duplicate requested key is collapsed to one occurrence."""
    backlog = [_item('A'), _item('B')]
    found, absent = _present_and_absent(['A', 'A', 'X', 'X'], backlog)
    assert found == ['A'] and absent == ['X']


def test_format_result() -> None:
    """Test the result listing shows each section with its count."""
    text = format_rank_result(RankedInJira(['A'], ['B'], ['C']))
    assert 'Ranked in Jira (1):' in text
    assert 'Not in Jira (1):' in text
    assert 'Excluded by the filter (1):' in text
