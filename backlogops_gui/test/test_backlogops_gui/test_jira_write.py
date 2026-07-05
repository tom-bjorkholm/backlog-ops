#! /usr/local/bin/python3
"""Tests for adding a backlog and releases to Jira."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable
import pytest
from backlogops import (
    AddedReleasesToJira, AddedToJira, BacklogItem, BacklogOpsConfig,
    BacklogReleases, ExistsInJiraError, Release, ReleaseExistsError, Status)
from backlogops_gui.jira_dialogs import JiraWriteOptions
from .jira_test_helpers import config, make_app, make_immediate, record_calls

DATA = BacklogReleases(backlog=[], releases=[])
ASK_WRITE = 'backlogops_gui.jira_write.ask_jira_write_options'
ADD_BACKLOG = 'backlogops_gui.jira_write.add_backlog_to_jira'
ADD_RELEASES = 'backlogops_gui.jira_write.add_releases_to_jira'
THREAD = 'backlogops_gui.jira_base.threading.Thread'


def _write_opts(_parent: object, _presets: object) -> JiraWriteOptions:
    """Return write options as if the write dialog was confirmed."""
    return JiraWriteOptions('scrum', False)


def _no_write_opts(_parent: object, _presets: object) -> None:
    """Return None as if the write dialog was cancelled."""
    return None


def _add_result() -> AddedToJira:
    """Return a canned add result with one stored item."""
    added = BacklogItem(key='PROJ-1', level=1, title='First', story_points=5,
                        status=Status.TODO)
    return AddedToJira(stored=[added], already_present=[], failed=[],
                       key_map={'A': 'PROJ-1'}, status_mismatch=[],
                       failed_links=[])


def _fake_write(result: AddedToJira) -> Callable[..., AddedToJira]:
    """Return a stand-in add_backlog_to_jira returning ``result``."""
    def add(*_args: object, **_kwargs: object) -> AddedToJira:
        """Ignore the arguments and return the canned result."""
        return result
    return add


def test_write_action_absent() -> None:
    """Test the add-to-Jira action is absent without write presets."""
    assert make_app(BacklogOpsConfig()).jira.writer.backlog_action() is None
    assert make_app(config()).jira.writer.backlog_action() is not None


def test_write_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the handler adds the backlog and hands back the result."""
    result = _add_result()
    monkeypatch.setattr(ASK_WRITE, _write_opts)
    monkeypatch.setattr(ADD_BACKLOG, _fake_write(result))
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    got: list[AddedToJira] = []
    # pylint: disable-next=protected-access
    app.jira.writer._add_backlog(DATA, got.append)
    assert got == [result]


def test_write_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the write dialog adds nothing."""
    monkeypatch.setattr(ASK_WRITE, _no_write_opts)
    app = make_app(config())
    got: list[AddedToJira] = []
    # pylint: disable-next=protected-access
    app.jira.writer._add_backlog(DATA, got.append)
    assert not got


def test_write_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a write failure is reported and nothing is handed back."""
    def _raise(*_args: object, **_kwargs: object) -> AddedToJira:
        """Raise as the real add does when a key already exists."""
        raise ExistsInJiraError(['A'])
    monkeypatch.setattr(ASK_WRITE, _write_opts)
    monkeypatch.setattr(ADD_BACKLOG, _raise)
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', record_calls(errors))
    got: list[AddedToJira] = []
    # pylint: disable-next=protected-access
    app.jira.writer._add_backlog(DATA, got.append)
    assert not got
    assert errors


def _add_releases_result() -> AddedReleasesToJira:
    """Return a canned add result with one stored release."""
    return AddedReleasesToJira(stored=[Release(name='R1')], already_present=[],
                               failed=[])


def _fake_releases(result: AddedReleasesToJira
                   ) -> Callable[..., AddedReleasesToJira]:
    """Return a stand-in add_releases_to_jira returning ``result``."""
    def add(*_args: object, **_kwargs: object) -> AddedReleasesToJira:
        """Ignore the arguments and return the canned result."""
        return result
    return add


def test_rel_action_absent() -> None:
    """Test the add-releases action is absent without write presets."""
    assert make_app(BacklogOpsConfig()).jira.writer.releases_action() is None
    assert make_app(config()).jira.writer.releases_action() is not None


def test_rel_write_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the handler adds the releases and hands back the result."""
    result = _add_releases_result()
    monkeypatch.setattr(ASK_WRITE, _write_opts)
    monkeypatch.setattr(ADD_RELEASES, _fake_releases(result))
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    got: list[AddedReleasesToJira] = []
    # pylint: disable-next=protected-access
    app.jira.writer._add_releases(DATA, got.append)
    assert got == [result]


def test_rel_write_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the releases write dialog adds nothing."""
    monkeypatch.setattr(ASK_WRITE, _no_write_opts)
    app = make_app(config())
    got: list[AddedReleasesToJira] = []
    # pylint: disable-next=protected-access
    app.jira.writer._add_releases(DATA, got.append)
    assert not got


def test_rel_write_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a releases write failure is reported and nothing handed back."""
    def _raise(*_args: object, **_kwargs: object) -> AddedReleasesToJira:
        """Raise as the real add does when a name already exists."""
        raise ReleaseExistsError(['R1'])
    monkeypatch.setattr(ASK_WRITE, _write_opts)
    monkeypatch.setattr(ADD_RELEASES, _raise)
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', record_calls(errors))
    got: list[AddedReleasesToJira] = []
    # pylint: disable-next=protected-access
    app.jira.writer._add_releases(DATA, got.append)
    assert not got
    assert errors
