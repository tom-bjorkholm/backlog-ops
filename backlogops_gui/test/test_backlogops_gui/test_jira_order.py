#! /usr/local/bin/python3
"""Tests for ordering releases in Jira from the GUI.

The dialog and the Jira ordering are replaced by stand-ins and the worker
thread runs at once, so a test drives the handler synchronously: the tests
check the action is absent without Jira presets, that the by-date, window and
by-names order sources call the right operation with the right names, that
cancelling orders nothing, and that a failure is reported.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable
import pytest
from backlogops import (
    BacklogOpsConfig, BacklogReleases, OrderedReleasesInJira, Release)
from backlogops_gui.jira_dialogs import JiraOrderOptions
from .jira_test_helpers import config, make_app, make_immediate, record_calls

ASK = 'backlogops_gui.jira_order.ask_jira_order'
BY_NAMES = 'backlogops_gui.jira_order.order_releases_in_jira'
BY_DATE = 'backlogops_gui.jira_order.order_jira_rel_by_date'
THREAD = 'backlogops_gui.jira_base.threading.Thread'

DATA = BacklogReleases(backlog=[], releases=[Release('R1'), Release('R2')])
RESULT = OrderedReleasesInJira(['R1', 'R2'], [])


def _opts(mode: str, names: list[str]) -> Callable[..., JiraOrderOptions]:
    """Return a dialog stand-in giving the mode and names as confirmed."""
    def ask(_parent: object, _presets: object) -> JiraOrderOptions:
        """Return the order options as if the dialog was confirmed."""
        return JiraOrderOptions('scrum', mode, names)
    return ask


def _no_opts(_parent: object, _presets: object) -> None:
    """Return None as if the order dialog was cancelled."""
    return None


def _fake_names(captured: dict[str, object]
                ) -> Callable[..., OrderedReleasesInJira]:
    """Return a stand-in name-list order that records its names.

    The wanted names are the third positional argument the order code passes.
    """
    def order(*args: object, **_kwargs: object) -> OrderedReleasesInJira:
        """Record the by-name order and return the canned result."""
        captured['func'] = 'names'
        captured['names'] = list(args[2])  # type: ignore[call-overload]
        return RESULT
    return order


def _fake_date(captured: dict[str, object]
               ) -> Callable[..., OrderedReleasesInJira]:
    """Return a stand-in by-date order that records it was called."""
    def order(*_args: object, **_kwargs: object) -> OrderedReleasesInJira:
        """Record the by-date order and return the canned result."""
        captured['func'] = 'date'
        return RESULT
    return order


def _patch(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Replace the dialog stand-in threads and both order operations."""
    captured: dict[str, object] = {}
    monkeypatch.setattr(BY_NAMES, _fake_names(captured))
    monkeypatch.setattr(BY_DATE, _fake_date(captured))
    monkeypatch.setattr(THREAD, make_immediate)
    return captured


def test_order_action_absent() -> None:
    """Test the order action is absent without Jira presets."""
    empty = make_app(BacklogOpsConfig())
    assert empty.jira.orderer.order_action() is None
    assert make_app(config()).jira.orderer.order_action() is not None


def test_order_by_date(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the by-date source calls the by-date order operation."""
    captured = _patch(monkeypatch)
    monkeypatch.setattr(ASK, _opts('date', []))
    app = make_app(config())
    got: list[OrderedReleasesInJira] = []
    # pylint: disable-next=protected-access
    app.jira.orderer._order(DATA, got.append)
    assert got == [RESULT] and captured['func'] == 'date'


def test_order_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the window source orders by the shown release names."""
    captured = _patch(monkeypatch)
    monkeypatch.setattr(ASK, _opts('window', []))
    app = make_app(config())
    # pylint: disable-next=protected-access
    app.jira.orderer._order(DATA, lambda _result: None)
    assert captured['func'] == 'names'
    assert captured['names'] == ['R1', 'R2']


def test_order_names(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the by-names source orders by the entered names."""
    captured = _patch(monkeypatch)
    monkeypatch.setattr(ASK, _opts('names', ['R2', 'R1']))
    app = make_app(config())
    # pylint: disable-next=protected-access
    app.jira.orderer._order(DATA, lambda _result: None)
    assert captured['names'] == ['R2', 'R1']


def test_order_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the order dialog orders nothing."""
    monkeypatch.setattr(ASK, _no_opts)
    app = make_app(config())
    got: list[OrderedReleasesInJira] = []
    # pylint: disable-next=protected-access
    app.jira.orderer._order(DATA, got.append)
    assert not got


def test_order_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an ordering failure is reported and nothing is handed back."""
    def _raise(*_args: object, **_kwargs: object) -> OrderedReleasesInJira:
        """Raise as the ordering does when Jira cannot be reached."""
        raise ValueError('boom')
    monkeypatch.setattr(ASK, _opts('date', []))
    monkeypatch.setattr(BY_DATE, _raise)
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', record_calls(errors))
    got: list[OrderedReleasesInJira] = []
    # pylint: disable-next=protected-access
    app.jira.orderer._order(DATA, got.append)
    assert not got
    assert errors
