#! /usr/local/bin/python3
"""Tests for reading backlog data from Jira in the GUI application."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable, Optional, TextIO, cast
import pytest
from backlogops import (
    AddedReleasesToJira, AddedToJira, BacklogItem, BacklogOpsConfig,
    BacklogReleases, ExistsInJiraError, JiraConnectConfig, JiraIOConfig,
    JiraPreset, Release, ReleaseExistsError, Status, TokenStorage)
from backlogops.jira_token import encrypt_token
from backlogops_gui import application
from backlogops_gui.application import BacklogApp
from backlogops_gui.io_dialogs import JiraReadOptions, JiraWriteOptions

DATA = BacklogReleases(backlog=[], releases=[])


def _record(store: list[tuple[str, str]]) -> Callable[[str, str], None]:
    """Return a callback recording its title and message."""
    def recorder(title: str, message: str) -> None:
        store.append((title, message))
    return recorder


def _opener(store: list[object]
            ) -> Callable[[BacklogReleases, str, Optional[str]], None]:
    """Return a callback recording an opened backlog including warning."""
    def recorder(backlog: BacklogReleases, title: str,
                 warning: Optional[str] = None) -> None:
        store.append((backlog, title, warning))
    return recorder


# pylint: disable-next=too-few-public-methods
class _AfterRoot:
    """Minimal root that runs scheduled callbacks immediately."""

    def after(self, delay: int, callback: Callable[[], None]) -> None:
        """Record a zero-delay GUI handoff by running it now."""
        assert delay == 0
        callback()


# pylint: disable-next=too-few-public-methods
class _ImmediateThread:
    """Small thread stand-in that runs its work when started."""

    def __init__(self, target: Callable[[], None], daemon: bool) -> None:
        """Store the worker callable and daemon flag."""
        self._target = target
        self.daemon = daemon
        self.started = False

    def start(self) -> None:
        """Mark the worker started and call its target immediately."""
        self.started = True
        self._target()


# pylint: disable-next=too-few-public-methods
class _BadJiraData:
    """Backlog-like data whose consistency check fails."""

    def __init__(self) -> None:
        """Create empty backlog and releases."""
        self.backlog: list[object] = []
        self.releases: list[object] = []

    def check_consistency(self, stderr_file: TextIO) -> None:
        """Report an inconsistent reference and raise."""
        stderr_file.write('bad jira reference\n')
        raise KeyError('bad jira reference')


def _jira_config(encrypted: bool = False) -> JiraIOConfig:
    """Return a minimal Jira configuration with one preset."""
    conn = JiraConnectConfig()
    conn.token_storage = (TokenStorage.ENCRYPTED_INTERNAL if encrypted
                          else TokenStorage.CLEAR_INTERNAL)
    conn.stored_token = encrypt_token('TOK', 'secret') if encrypted else 'TOK'
    preset = JiraPreset()
    preset.connection_name = 'main'
    preset.def_filter = 'project = SCRUM'
    config = JiraIOConfig()
    config.connections = {'main': conn}
    config.presets = {'scrum': preset}
    return config


def _config(encrypted: bool = False) -> BacklogOpsConfig:
    """Return a top-level config with one Jira preset."""
    config = BacklogOpsConfig()
    config.jira = _jira_config(encrypted)
    return config


def _app(config: Optional[BacklogOpsConfig]) -> BacklogApp:
    """Return an application with immediate ``after`` callbacks."""
    return BacklogApp(cast(tk.Tk, _AfterRoot()), config)


def _jira_opts(_parent: object, _filters: object) -> JiraReadOptions:
    """Return Jira read options as if the dialog was confirmed."""
    return JiraReadOptions('scrum', 'project = SCRUM ORDER BY rank ASC')


def _no_jira_opts(_parent: object, _filters: object) -> None:
    """Return None as if the Jira read dialog was cancelled."""
    return None


def _secret(_parent: object) -> str:
    """Return a fixed pass phrase as if the dialog was confirmed."""
    return 'secret'


def _cancel(_parent: object) -> None:
    """Return None as if a dialog was cancelled."""
    return None


def _none(*_args: object, **_kwargs: object) -> None:
    """Do nothing."""


def _make_immediate(target: Callable[[], None],
                    daemon: bool) -> _ImmediateThread:
    """Return an immediate thread stand-in."""
    return _ImmediateThread(target, daemon)


def _thread_recorder(store: list[object]) -> Callable[..., object]:
    """Return a thread factory that records if it was called."""
    def make(**_kwargs: object) -> object:
        thread = object()
        store.append(thread)
        return thread
    return make


def _read_data(*_args: object, **_kwargs: object) -> BacklogReleases:
    """Return fixed data as if Jira reading succeeded."""
    return DATA


def _bad_reader(data: BacklogReleases) -> Callable[..., BacklogReleases]:
    """Return a Jira reader yielding the supplied data."""
    def read(*_args: object, **_kwargs: object) -> BacklogReleases:
        return data
    return read


def test_jira_presets() -> None:
    """Test Jira preset defaults come from the loaded configuration."""
    # pylint: disable-next=protected-access
    assert _app(_config())._jira_preset_filters() == {
        'scrum': 'project = SCRUM'}
    # pylint: disable-next=protected-access
    assert _app(None)._jira_preset_filters() is None


def test_read_jira_no_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test reading from Jira without configuration reports an error."""
    app = _app(None)
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    # pylint: disable-next=protected-access
    app._read_jira_backlog()
    assert errors == [('No configuration',
                       'There is no configuration to read Jira from.')]


def test_read_jira_no_presets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test reading from Jira without Jira presets reports an error."""
    app = _app(BacklogOpsConfig())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    # pylint: disable-next=protected-access
    app._read_jira_backlog()
    assert errors == [('No Jira presets',
                       'There are no Jira presets in the configuration.')]


def test_read_jira_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the Jira read dialog starts no worker."""
    app = _app(_config())
    monkeypatch.setattr(application, 'ask_jira_read_options', _no_jira_opts)
    made: list[object] = []
    monkeypatch.setattr('backlogops_gui.application.threading.Thread',
                        _thread_recorder(made))
    # pylint: disable-next=protected-access
    app._read_jira_backlog()
    assert not made


def test_jira_thread_opens(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a Jira read runs on a worker and opens the result."""
    app = _app(_config())
    monkeypatch.setattr(application, 'ask_jira_read_options', _jira_opts)
    monkeypatch.setattr(application, 'read_jira_from_config', _read_data)
    made: list[_ImmediateThread] = []

    def make_thread(target: Callable[[], None],
                    daemon: bool) -> _ImmediateThread:
        thread = _ImmediateThread(target, daemon)
        made.append(thread)
        return thread
    monkeypatch.setattr('backlogops_gui.application.threading.Thread',
                        make_thread)
    opened: list[object] = []
    infos: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'open_backlog', _opener(opened))
    monkeypatch.setattr(app, 'show_info', _record(infos))
    # pylint: disable-next=protected-access
    app._read_jira_backlog()
    assert len(made) == 1 and made[0].daemon is True
    assert opened == [(DATA, 'Jira: scrum', None)]
    assert infos == [('Read from Jira',
                      "Finished reading from Jira preset 'scrum'.")]


def test_read_jira_passphrase(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test encrypted Jira connections cache the token after one prompt."""
    app = _app(_config(encrypted=True))
    asked: list[object] = []

    def read(_config_obj: BacklogOpsConfig, _preset: str, *,
             filter_override: Optional[str], stderr_file: TextIO,
             passphrase: Optional[Callable[[], str]] = None
             ) -> BacklogReleases:
        """Check the worker reader gets no pass phrase provider."""
        assert filter_override is not None
        assert stderr_file is not None
        assert passphrase is None
        return DATA

    def secret(_parent: object) -> str:
        """Record that the pass phrase was requested."""
        asked.append(_parent)
        return 'secret'
    monkeypatch.setattr(application, 'ask_jira_read_options', _jira_opts)
    monkeypatch.setattr(application, 'ask_jira_passphrase', secret)
    monkeypatch.setattr(application, 'read_jira_from_config', read)
    monkeypatch.setattr('backlogops_gui.application.threading.Thread',
                        _make_immediate)
    monkeypatch.setattr(app, 'show_info', _none)
    monkeypatch.setattr(app, 'open_backlog', _none)
    # pylint: disable-next=protected-access
    app._read_jira_backlog()
    # pylint: disable-next=protected-access
    app._read_jira_backlog()
    assert len(asked) == 1


def test_jira_pass_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the pass phrase dialog starts no worker."""
    app = _app(_config(encrypted=True))
    monkeypatch.setattr(application, 'ask_jira_read_options', _jira_opts)
    monkeypatch.setattr(application, 'ask_jira_passphrase', _cancel)
    made: list[object] = []
    monkeypatch.setattr('backlogops_gui.application.threading.Thread',
                        _thread_recorder(made))
    # pylint: disable-next=protected-access
    app._read_jira_backlog()
    assert not made


def test_read_jira_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a Jira read failure is reported from the GUI thread."""
    app = _app(_config())

    def read(*_args: object, **_kw: object) -> BacklogReleases:
        """Raise as if Jira reading failed."""
        raise ValueError('bad jira')
    monkeypatch.setattr(application, 'ask_jira_read_options', _jira_opts)
    monkeypatch.setattr(application, 'read_jira_from_config', read)
    monkeypatch.setattr('backlogops_gui.application.threading.Thread',
                        _make_immediate)
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    # pylint: disable-next=protected-access
    app._read_jira_backlog()
    assert errors == [('Could not read from Jira', 'bad jira')]
    assert 'Could not read from Jira preset' in app.log.text()


def test_read_jira_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test inconsistent Jira data opens with a warning and logs details."""
    app = _app(_config())
    bad_data = cast(BacklogReleases, _BadJiraData())
    monkeypatch.setattr(application, 'ask_jira_read_options', _jira_opts)
    monkeypatch.setattr(application, 'read_jira_from_config',
                        _bad_reader(bad_data))
    monkeypatch.setattr('backlogops_gui.application.threading.Thread',
                        _make_immediate)
    monkeypatch.setattr(app, 'show_info', _none)
    opened: list[object] = []
    monkeypatch.setattr(app, 'open_backlog', _opener(opened))
    # pylint: disable-next=protected-access
    app._read_jira_backlog()
    assert opened == [(bad_data, 'Jira: scrum', application.JIRA_WARNING)]
    assert 'bad jira reference' in app.log.text()


def _write_opts(_parent: object, _presets: object) -> JiraWriteOptions:
    """Return write options as if the write dialog was confirmed."""
    return JiraWriteOptions('scrum', False)


def _add_result() -> AddedToJira:
    """Return a canned add result with one stored item."""
    added = BacklogItem(key='PROJ-1', level=1, title='First', story_points=5,
                        status=Status.TODO)
    return AddedToJira(stored=[added], already_present=[], failed=[],
                       key_map={'A': 'PROJ-1'}, status_mismatch=[])


def _fake_write(result: AddedToJira) -> Callable[..., AddedToJira]:
    """Return a stand-in add_backlog_to_jira returning ``result``."""
    def add(*_args: object, **_kwargs: object) -> AddedToJira:
        """Ignore the arguments and return the canned result."""
        return result
    return add


def test_write_action_absent() -> None:
    """Test the add-to-Jira action is absent without write presets."""
    # pylint: disable-next=protected-access
    assert _app(BacklogOpsConfig())._jira_write_action() is None
    # pylint: disable-next=protected-access
    assert _app(_config())._jira_write_action() is not None


def test_write_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the handler adds the backlog and hands back the result."""
    result = _add_result()
    monkeypatch.setattr(application, 'ask_jira_write_options', _write_opts)
    monkeypatch.setattr(application, 'add_backlog_to_jira',
                        _fake_write(result))
    monkeypatch.setattr('backlogops_gui.application.threading.Thread',
                        _make_immediate)
    app = _app(_config())
    got: list[AddedToJira] = []
    # pylint: disable-next=protected-access
    app._add_backlog_to_jira(DATA, got.append)
    assert got == [result]


def test_write_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the write dialog adds nothing."""
    monkeypatch.setattr(application, 'ask_jira_write_options', _no_jira_opts)
    app = _app(_config())
    got: list[AddedToJira] = []
    # pylint: disable-next=protected-access
    app._add_backlog_to_jira(DATA, got.append)
    assert not got


def test_write_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a write failure is reported and nothing is handed back."""
    def _raise(*_args: object, **_kwargs: object) -> AddedToJira:
        """Raise as the real add does when a key already exists."""
        raise ExistsInJiraError(['A'])
    monkeypatch.setattr(application, 'ask_jira_write_options', _write_opts)
    monkeypatch.setattr(application, 'add_backlog_to_jira', _raise)
    monkeypatch.setattr('backlogops_gui.application.threading.Thread',
                        _make_immediate)
    app = _app(_config())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    got: list[AddedToJira] = []
    # pylint: disable-next=protected-access
    app._add_backlog_to_jira(DATA, got.append)
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
    # pylint: disable-next=protected-access
    assert _app(BacklogOpsConfig())._jira_releases_action() is None
    # pylint: disable-next=protected-access
    assert _app(_config())._jira_releases_action() is not None


def test_rel_write_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the handler adds the releases and hands back the result."""
    result = _add_releases_result()
    monkeypatch.setattr(application, 'ask_jira_write_options', _write_opts)
    monkeypatch.setattr(application, 'add_releases_to_jira',
                        _fake_releases(result))
    monkeypatch.setattr('backlogops_gui.application.threading.Thread',
                        _make_immediate)
    app = _app(_config())
    got: list[AddedReleasesToJira] = []
    # pylint: disable-next=protected-access
    app._add_releases_to_jira(DATA, got.append)
    assert got == [result]


def test_rel_write_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the releases write dialog adds nothing."""
    monkeypatch.setattr(application, 'ask_jira_write_options', _no_jira_opts)
    app = _app(_config())
    got: list[AddedReleasesToJira] = []
    # pylint: disable-next=protected-access
    app._add_releases_to_jira(DATA, got.append)
    assert not got


def test_rel_write_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a releases write failure is reported and nothing handed back."""
    def _raise(*_args: object, **_kwargs: object) -> AddedReleasesToJira:
        """Raise as the real add does when a name already exists."""
        raise ReleaseExistsError(['R1'])
    monkeypatch.setattr(application, 'ask_jira_write_options', _write_opts)
    monkeypatch.setattr(application, 'add_releases_to_jira', _raise)
    monkeypatch.setattr('backlogops_gui.application.threading.Thread',
                        _make_immediate)
    app = _app(_config())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    got: list[AddedReleasesToJira] = []
    # pylint: disable-next=protected-access
    app._add_releases_to_jira(DATA, got.append)
    assert not got
    assert errors
