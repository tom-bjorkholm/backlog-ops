#! /usr/local/bin/python3
"""Tests for moving issues in the Jira rank order from the GUI.

The dialog and the Jira ranking are replaced by stand-ins and the worker
thread runs at once, so a test drives the handler synchronously: the tests
check the action is absent without Jira presets, that a confirmed dialog
ranks and hands back the result, that cancelling ranks nothing, and that a
failure is reported.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable
import pytest
from backlogops import (
    BacklogOpsConfig, BadJiraRankFilter, JiraRankAnchor, RankedInJira)
from backlogops_gui.jira_dialogs import JiraRankOptions
from .jira_test_helpers import config, make_app, make_immediate, record_calls

ASK = 'backlogops_gui.jira_rank.ask_jira_rank'
RANK = 'backlogops_gui.jira_rank.jira_rank_move_keys'
THREAD = 'backlogops_gui.jira_base.threading.Thread'


def _opts(_parent: object, _filters: object, _sink: object) -> JiraRankOptions:
    """Return rank options as if the rank dialog was confirmed."""
    return JiraRankOptions('scrum', 'project = SCRUM', ['A', 'B'],
                           JiraRankAnchor.BACKLOG_TOP, False)


def _no_opts(_parent: object, _filters: object, _sink: object) -> None:
    """Return None as if the rank dialog was cancelled."""
    return None


def _fake_rank(result: RankedInJira) -> Callable[..., RankedInJira]:
    """Return a stand-in jira_rank_move_keys returning ``result``."""
    def rank(*_args: object, **_kwargs: object) -> RankedInJira:
        """Ignore the arguments and return the canned result."""
        return result
    return rank


def test_rank_action_absent() -> None:
    """Test the rank action is absent without Jira presets."""
    empty = make_app(BacklogOpsConfig())
    assert empty.jira.ranker.rank_action() is None
    assert make_app(config()).jira.ranker.rank_action() is not None


def test_rank_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the handler ranks the items and hands back the result."""
    result = RankedInJira(['A', 'B'], [], [])
    monkeypatch.setattr(ASK, _opts)
    monkeypatch.setattr(RANK, _fake_rank(result))
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    got: list[RankedInJira] = []
    # pylint: disable-next=protected-access
    app.jira.ranker._rank(got.append)
    assert got == [result]
    assert 'Ranked' in app.log.text()


def test_rank_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the rank dialog ranks nothing."""
    monkeypatch.setattr(ASK, _no_opts)
    app = make_app(config())
    got: list[RankedInJira] = []
    # pylint: disable-next=protected-access
    app.jira.ranker._rank(got.append)
    assert not got


def test_rank_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a ranking failure is reported and nothing is handed back."""
    def _raise(*_args: object, **_kwargs: object) -> RankedInJira:
        """Raise as the ranking does for a filter that is not usable."""
        raise BadJiraRankFilter(jql_text='x', message='bad')
    monkeypatch.setattr(ASK, _opts)
    monkeypatch.setattr(RANK, _raise)
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', record_calls(errors))
    got: list[RankedInJira] = []
    # pylint: disable-next=protected-access
    app.jira.ranker._rank(got.append)
    assert not got
    assert errors
