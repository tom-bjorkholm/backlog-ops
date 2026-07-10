#! /usr/local/bin/python3
"""Tests for renaming releases in Jira from the GUI.

The dialog and the Jira rename are replaced by stand-ins and the worker
thread runs at once, so a test drives the handler synchronously: the tests
check the action is absent without Jira presets, that a confirmed dialog
renames and hands back the result, that cancelling renames nothing, and that
a failure is reported.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable
import pytest
from backlogops import (
    BacklogOpsConfig, BacklogReleases, Release, ReleaseRename,
    RenamedReleasesInJira)
from backlogops_gui.jira_dialogs import JiraRenameOptions
from .jira_test_helpers import config, make_app, make_immediate, record_calls

ASK = 'backlogops_gui.jira_rename.ask_jira_rename'
RENAME = 'backlogops_gui.jira_rename.rename_releases_in_jira'
THREAD = 'backlogops_gui.jira_base.threading.Thread'

DATA = BacklogReleases(backlog=[], releases=[Release('R1'), Release('R2')])


def _opts(_parent: object, _presets: object,
          _names: object) -> JiraRenameOptions:
    """Return rename options as if the rename dialog was confirmed."""
    return JiraRenameOptions('scrum', [ReleaseRename('R1', 'R9')])


def _no_opts(_parent: object, _presets: object, _names: object) -> None:
    """Return None as if the rename dialog was cancelled."""
    return None


def _fake_rename(result: RenamedReleasesInJira
                 ) -> Callable[..., RenamedReleasesInJira]:
    """Return a stand-in rename returning ``result``."""
    def rename(*_args: object, **_kwargs: object) -> RenamedReleasesInJira:
        """Ignore the arguments and return the canned result."""
        return result
    return rename


def test_rename_action_absent() -> None:
    """Test the rename action is absent without Jira presets."""
    empty = make_app(BacklogOpsConfig())
    assert empty.jira.renamer.rename_action() is None
    assert make_app(config()).jira.renamer.rename_action() is not None


def test_rename_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the handler renames the releases and hands back the result."""
    result = RenamedReleasesInJira([ReleaseRename('R1', 'R9')], [], [], [], [])
    monkeypatch.setattr(ASK, _opts)
    monkeypatch.setattr(RENAME, _fake_rename(result))
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    got: list[RenamedReleasesInJira] = []
    # pylint: disable-next=protected-access
    app.jira.renamer._rename(DATA, got.append)
    assert got == [result]
    assert 'Renamed' in app.log.text()


def test_rename_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the rename dialog renames nothing."""
    monkeypatch.setattr(ASK, _no_opts)
    app = make_app(config())
    got: list[RenamedReleasesInJira] = []
    # pylint: disable-next=protected-access
    app.jira.renamer._rename(DATA, got.append)
    assert not got


def test_rename_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a rename failure is reported and nothing is handed back."""
    def _raise(*_args: object, **_kwargs: object) -> RenamedReleasesInJira:
        """Raise as the rename does when Jira cannot be reached."""
        raise ValueError('boom')
    monkeypatch.setattr(ASK, _opts)
    monkeypatch.setattr(RENAME, _raise)
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', record_calls(errors))
    got: list[RenamedReleasesInJira] = []
    # pylint: disable-next=protected-access
    app.jira.renamer._rename(DATA, got.append)
    assert not got
    assert errors
