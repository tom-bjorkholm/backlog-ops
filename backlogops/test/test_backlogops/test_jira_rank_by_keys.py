#! /usr/local/bin/python3
"""Tests for the low-level Jira ranking primitive.

A stand-in Jira client holds a global rank order, so a test drives the
whole read-verify loop without a Jira server: the tests check the chaining
direction, that the loop retries until a flaky ranking converges, that a
ranking that never converges raises, and that a missing key is reported.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import pytest
from backlogops import JiraKeyError, JiraTooManyLoops, jira_rank_by_keys_raw
from .jira_rank_helpers import FakeRankClient
from .jira_write_helpers import connections_for


def test_chain_after(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test move_before False anchors the first key and chains after it."""
    client = FakeRankClient(['X', 'A', 'B', 'C'])
    connections = connections_for(monkeypatch, client)
    jira_rank_by_keys_raw(connections, 'c', ['C', 'B', 'A'], move_before=False)
    assert client.order == ['X', 'C', 'B', 'A']


def test_chain_before(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test move_before True anchors the last key and chains before it."""
    client = FakeRankClient(['A', 'B', 'C', 'X'])
    connections = connections_for(monkeypatch, client)
    jira_rank_by_keys_raw(connections, 'c', ['C', 'B', 'A'], move_before=True)
    assert client.order == ['C', 'B', 'A', 'X']


def test_short_list_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a list of fewer than two keys ranks nothing."""
    client = FakeRankClient(['A', 'B'])
    connections = connections_for(monkeypatch, client)
    jira_rank_by_keys_raw(connections, 'c', ['A'])
    assert not client.rank_calls


def test_loop_converges(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the loop retries when the first pass of moves is lost."""
    client = FakeRankClient(['A', 'B', 'C'], drop_ranks=2)
    connections = connections_for(monkeypatch, client)
    jira_rank_by_keys_raw(connections, 'c', ['C', 'B', 'A'], move_before=False)
    assert client.order == ['C', 'B', 'A']
    assert len(client.rank_calls) == 4


def test_too_many_loops(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a ranking that never converges raises JiraTooManyLoops."""
    client = FakeRankClient(['A', 'B', 'C'], drop_ranks=1000)
    connections = connections_for(monkeypatch, client)
    with pytest.raises(JiraTooManyLoops) as info:
        jira_rank_by_keys_raw(connections, 'c', ['C', 'B', 'A'])
    assert info.value.max_loops == 6
    assert info.value.connection_name == 'c'


def test_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a key that does not exist in Jira raises JiraKeyError."""
    client = FakeRankClient(['A', 'B'], exist=['A', 'B'])
    connections = connections_for(monkeypatch, client)
    with pytest.raises(JiraKeyError) as info:
        jira_rank_by_keys_raw(connections, 'c', ['A', 'B', 'GONE'])
    assert info.value.key_name == 'GONE'


def test_absent_from_search(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a key that exists but is unranked raises JiraKeyError."""
    client = FakeRankClient(['A', 'B'], exist=['A', 'B', 'C'])
    connections = connections_for(monkeypatch, client)
    with pytest.raises(JiraKeyError) as info:
        jira_rank_by_keys_raw(connections, 'c', ['A', 'B', 'C'])
    assert info.value.key_name == 'C'


def test_key_error_message() -> None:
    """Test the key error message names the key and connection."""
    error = JiraKeyError('PROJ-1', connection_name='c',
                         message='while ranking')
    text = str(error)
    assert 'PROJ-1' in text and 'c' in text and 'while ranking' in text


def test_too_many_message() -> None:
    """Test the loop error message names the loop count and connection."""
    error = JiraTooManyLoops(6, connection_name='c')
    assert '6' in str(error) and 'c' in str(error)
