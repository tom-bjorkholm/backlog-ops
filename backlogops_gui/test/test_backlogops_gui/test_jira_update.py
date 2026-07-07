#! /usr/local/bin/python3
"""Tests for updating releases and the backlog in Jira."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable
import pytest
from backlogops import (
    AddedToJira, BacklogOpsConfig, BacklogReleases, ItemNotInJiraError,
    LinkUpdate, OnMissingKey, UpdatedBacklogInJira, UpdatedReleasesInJira)
from backlogops_gui.jira_dialogs import (
    JiraBacklogUpdateOptions, JiraReleaseUpdateOptions)
from .jira_test_helpers import config, make_app, make_immediate, record_calls

DATA = BacklogReleases(backlog=[], releases=[])
ASK_REL = 'backlogops_gui.jira_update.ask_release_update'
UPD_REL = 'backlogops_gui.jira_update.update_releases_in_jira'
FIELDS = 'backlogops_gui.jira_update.updatable_backlog_fields'
ASK_BL = 'backlogops_gui.jira_update.ask_backlog_update'
UPD_BL = 'backlogops_gui.jira_update.update_backlog_in_jira'
THREAD = 'backlogops_gui.jira_base.threading.Thread'


def _update_opts(_parent: object, _presets: object,
                 _names: object) -> JiraReleaseUpdateOptions:
    """Return update options as if the update dialog was confirmed."""
    return JiraReleaseUpdateOptions('scrum', OnMissingKey.RAISE, [])


def _no_update_opts(_parent: object, _presets: object, _names: object) -> None:
    """Return None as if the release-update dialog was cancelled."""
    return None


def _update_result() -> UpdatedReleasesInJira:
    """Return a result with an updated and an already-correct release."""
    return UpdatedReleasesInJira(updated=['R1'], already_correct=['R2'],
                                 ignored=[], added=[], failed=[])


def _fake_update(result: UpdatedReleasesInJira
                 ) -> Callable[..., UpdatedReleasesInJira]:
    """Return a stand-in update_releases_in_jira returning ``result``."""
    def update(*_args: object, **_kwargs: object) -> UpdatedReleasesInJira:
        """Ignore the arguments and return the canned result."""
        return result
    return update


def test_upd_action_absent() -> None:
    """Test the update-releases action is absent without write presets."""
    empty = make_app(BacklogOpsConfig())
    assert empty.jira.updater.releases_action() is None
    assert make_app(config()).jira.updater.releases_action() is not None


def test_upd_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the handler updates the releases and hands back the result."""
    result = _update_result()
    monkeypatch.setattr(ASK_REL, _update_opts)
    monkeypatch.setattr(UPD_REL, _fake_update(result))
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    got: list[UpdatedReleasesInJira] = []
    # pylint: disable-next=protected-access
    app.jira.updater._update_releases(DATA, got.append)
    assert got == [result]
    assert 'already correct' in app.log.text()


def test_upd_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the update dialog updates nothing."""
    monkeypatch.setattr(ASK_REL, _no_update_opts)
    app = make_app(config())
    got: list[UpdatedReleasesInJira] = []
    # pylint: disable-next=protected-access
    app.jira.updater._update_releases(DATA, got.append)
    assert not got


def test_upd_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an update failure is reported and nothing is handed back."""
    def _raise(*_args: object, **_kwargs: object) -> UpdatedReleasesInJira:
        """Raise as the real update does when a name is missing."""
        raise ItemNotInJiraError(['R1'], 'Release names')
    monkeypatch.setattr(ASK_REL, _update_opts)
    monkeypatch.setattr(UPD_REL, _raise)
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', record_calls(errors))
    got: list[UpdatedReleasesInJira] = []
    # pylint: disable-next=protected-access
    app.jira.updater._update_releases(DATA, got.append)
    assert not got
    assert errors


def _fields_stub(_connections: object, _name: str) -> list[str]:
    """Return a fixed updatable field list as the library would."""
    return ['title', 'status']


def _bl_upd_opts(_parent: object, _fields: object) -> JiraBacklogUpdateOptions:
    """Return backlog-update options as if the dialog was confirmed."""
    return JiraBacklogUpdateOptions('scrum', OnMissingKey.RAISE,
                                    ['title', 'status'], True, None)


def _no_bl_upd_opts(_parent: object, _fields: object) -> None:
    """Return None as if the backlog-update dialog was cancelled."""
    return None


def _bl_update_result() -> UpdatedBacklogInJira:
    """Return a result with an updated and an already-correct item."""
    return UpdatedBacklogInJira(updated=['A'], already_correct=['B'],
                                ignored=[], failed=[], status_mismatch=[],
                                failed_links=[],
                                added=AddedToJira([], [], [], {}, [], []))


def _fake_bl_update(captured: dict[str, object], result: UpdatedBacklogInJira
                    ) -> Callable[..., UpdatedBacklogInJira]:
    """Return a stand-in update recording the fields and link policy."""
    def update(connections: object, preset: str, backlog: object, *,
               fields_to_update: list[str], link_update: LinkUpdate,
               **kwargs: object) -> UpdatedBacklogInJira:
        """Record the resolved fields and the link policy."""
        _ = (connections, preset, backlog, kwargs)
        captured['fields'] = fields_to_update
        captured['link'] = link_update
        return result
    return update


def test_bl_upd_action_absent() -> None:
    """Test the update-backlog action is absent without write presets."""
    empty = make_app(BacklogOpsConfig())
    assert empty.jira.updater.backlog_action() is None
    assert make_app(config()).jira.updater.backlog_action() is not None


def test_bl_preset_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the preset-to-fields map is built from the library helper."""
    monkeypatch.setattr(FIELDS, _fields_stub)
    app = make_app(config())
    # pylint: disable-next=protected-access
    assert app.jira.updater._preset_fields() == {'scrum': ['title', 'status']}


def test_bl_upd_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the handler updates the backlog and hands back the result."""
    captured: dict[str, object] = {}
    result = _bl_update_result()
    monkeypatch.setattr(FIELDS, _fields_stub)
    monkeypatch.setattr(ASK_BL, _bl_upd_opts)
    monkeypatch.setattr(UPD_BL, _fake_bl_update(captured, result))
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    got: list[UpdatedBacklogInJira] = []
    # pylint: disable-next=protected-access
    app.jira.updater._update_backlog(DATA, got.append)
    assert got == [result]
    assert captured['fields'] == ['title', 'status']
    assert captured['link'] is LinkUpdate.RECONCILE
    assert 'already correct' in app.log.text()


def test_bl_upd_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the backlog-update dialog updates nothing."""
    monkeypatch.setattr(FIELDS, _fields_stub)
    monkeypatch.setattr(ASK_BL, _no_bl_upd_opts)
    app = make_app(config())
    got: list[UpdatedBacklogInJira] = []
    # pylint: disable-next=protected-access
    app.jira.updater._update_backlog(DATA, got.append)
    assert not got


def test_bl_upd_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a backlog-update failure is reported and nothing handed back."""
    def _raise(*_args: object, **_kwargs: object) -> UpdatedBacklogInJira:
        """Raise as the real update does when a key is missing."""
        raise ItemNotInJiraError(['A'], 'Backlog keys')
    monkeypatch.setattr(FIELDS, _fields_stub)
    monkeypatch.setattr(ASK_BL, _bl_upd_opts)
    monkeypatch.setattr(UPD_BL, _raise)
    monkeypatch.setattr(THREAD, make_immediate)
    app = make_app(config())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', record_calls(errors))
    got: list[UpdatedBacklogInJira] = []
    # pylint: disable-next=protected-access
    app.jira.updater._update_backlog(DATA, got.append)
    assert not got
    assert errors
