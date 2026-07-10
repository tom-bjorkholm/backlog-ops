#! /usr/local/bin/python3
"""Tests for reading a backlog from Jira into a new window."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable, Optional, TextIO, cast
import pytest
from backlogops import BacklogOpsConfig, BacklogReleases
from backlogops_gui import jira_read
from backlogops_gui.application import BacklogApp
from backlogops_gui.jira_dialogs import JiraReadOptions
from .jira_test_helpers import (
    ImmediateThread, config, make_app, make_immediate, record_calls)


# pylint: disable-next=too-few-public-methods
class _DeadRoot:
    """A root whose after raises as a destroyed window's would."""

    def after(self, delay: int, callback: Callable[[], None]) -> None:
        """Raise a TclError as a destroyed window does on after."""
        _ = (delay, callback)
        raise tk.TclError('window gone')


DATA = BacklogReleases(backlog=[], releases=[])
ASK_READ = 'backlogops_gui.jira_read.ask_jira_read_options'
READ_JIRA = 'backlogops_gui.jira_read.read_jira_from_config'
ASK_PASS = 'backlogops_gui.jira_base.ask_jira_passphrase'
THREAD = 'backlogops_gui.jira_base.threading.Thread'


def _opener(store: list[object]
            ) -> Callable[[BacklogReleases, str, Optional[str]], None]:
    """Return a callback recording an opened backlog including warning."""
    def recorder(backlog: BacklogReleases, title: str,
                 warning: Optional[str] = None) -> None:
        store.append((backlog, title, warning))
    return recorder


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


def _jira_opts(_parent: object, _filters: object) -> JiraReadOptions:
    """Return Jira read options as if the dialog was confirmed."""
    return JiraReadOptions('scrum', 'project = SCRUM ORDER BY rank ASC')


def _no_jira_opts(_parent: object, _filters: object) -> None:
    """Return None as if the Jira read dialog was cancelled."""
    return None


def _cancel(_parent: object) -> None:
    """Return None as if a dialog was cancelled."""
    return None


def _none(*_args: object, **_kwargs: object) -> None:
    """Do nothing."""


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
    reader = make_app(config()).jira.reader
    # pylint: disable-next=protected-access
    assert reader._preset_filters() == {'scrum': 'project = SCRUM'}


def test_read_jira_no_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test reading from Jira without configuration reports an error."""
    app = make_app(None)
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', record_calls(errors))
    app.jira.reader.read_backlog()
    assert errors == [('No configuration',
                       'There is no configuration to read Jira from.')]


def test_read_jira_no_presets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test reading from Jira without Jira presets reports an error."""
    app = make_app(BacklogOpsConfig())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', record_calls(errors))
    app.jira.reader.read_backlog()
    assert errors == [('No Jira presets',
                       'There are no Jira presets in the configuration.')]


def test_read_jira_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the Jira read dialog starts no worker."""
    app = make_app(config())
    monkeypatch.setattr(ASK_READ, _no_jira_opts)
    made: list[object] = []
    monkeypatch.setattr(THREAD, _thread_recorder(made))
    app.jira.reader.read_backlog()
    assert not made


def test_jira_thread_opens(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a Jira read runs on a worker and opens the result."""
    app = make_app(config())
    monkeypatch.setattr(ASK_READ, _jira_opts)
    monkeypatch.setattr(READ_JIRA, _read_data)
    made: list[ImmediateThread] = []

    def make_thread(target: Callable[[], None],
                    daemon: bool) -> ImmediateThread:
        thread = ImmediateThread(target, daemon)
        made.append(thread)
        return thread
    monkeypatch.setattr(THREAD, make_thread)
    opened: list[object] = []
    infos: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'open_backlog', _opener(opened))
    monkeypatch.setattr(app, 'show_info', record_calls(infos))
    app.jira.reader.read_backlog()
    assert len(made) == 1 and made[0].daemon is True
    assert opened == [(DATA, 'Jira: scrum', None)]
    assert infos == [('Read from Jira',
                      "Finished reading from Jira preset 'scrum'.")]


def test_read_jira_passphrase(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test encrypted Jira connections cache the token after one prompt."""
    app = make_app(config(encrypted=True))
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
    monkeypatch.setattr(ASK_READ, _jira_opts)
    monkeypatch.setattr(ASK_PASS, secret)
    monkeypatch.setattr(READ_JIRA, read)
    monkeypatch.setattr(THREAD, make_immediate)
    monkeypatch.setattr(app, 'show_info', _none)
    monkeypatch.setattr(app, 'open_backlog', _none)
    app.jira.reader.read_backlog()
    app.jira.reader.read_backlog()
    assert len(asked) == 1


def test_jira_pass_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the pass phrase dialog starts no worker."""
    app = make_app(config(encrypted=True))
    monkeypatch.setattr(ASK_READ, _jira_opts)
    monkeypatch.setattr(ASK_PASS, _cancel)
    made: list[object] = []
    monkeypatch.setattr(THREAD, _thread_recorder(made))
    app.jira.reader.read_backlog()
    assert not made


def test_jira_token_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a failing token materialization is reported, no worker runs."""
    app = make_app(config(encrypted=True))
    monkeypatch.setattr(ASK_READ, _jira_opts)
    monkeypatch.setattr(ASK_PASS, lambda parent: 'wrong')
    made: list[object] = []
    monkeypatch.setattr(THREAD, _thread_recorder(made))
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', record_calls(errors))
    app.jira.reader.read_backlog()
    assert not made
    assert errors and errors[0][0] == 'Could not read Jira token'


def test_jira_after_gone(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a result handoff to a destroyed window is swallowed."""
    app = BacklogApp(cast(tk.Tk, _DeadRoot()), config())
    monkeypatch.setattr(ASK_READ, _jira_opts)
    monkeypatch.setattr(READ_JIRA, _read_data)
    monkeypatch.setattr(THREAD, make_immediate)
    opened: list[object] = []
    monkeypatch.setattr(app, 'open_backlog', _opener(opened))
    app.jira.reader.read_backlog()
    assert not opened


def test_read_jira_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a Jira read failure is reported from the GUI thread."""
    app = make_app(config())

    def read(*_args: object, **_kw: object) -> BacklogReleases:
        """Raise as if Jira reading failed."""
        raise ValueError('bad jira')
    monkeypatch.setattr(ASK_READ, _jira_opts)
    monkeypatch.setattr(READ_JIRA, read)
    monkeypatch.setattr(THREAD, make_immediate)
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', record_calls(errors))
    app.jira.reader.read_backlog()
    assert errors == [('Could not read from Jira', 'bad jira')]
    assert 'Could not read from Jira preset' in app.log.text()


def test_read_jira_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test inconsistent Jira data opens with a warning and logs details."""
    app = make_app(config())
    bad_data = cast(BacklogReleases, _BadJiraData())
    monkeypatch.setattr(ASK_READ, _jira_opts)
    monkeypatch.setattr(READ_JIRA, _bad_reader(bad_data))
    monkeypatch.setattr(THREAD, make_immediate)
    monkeypatch.setattr(app, 'show_info', _none)
    opened: list[object] = []
    monkeypatch.setattr(app, 'open_backlog', _opener(opened))
    app.jira.reader.read_backlog()
    assert opened == [(bad_data, 'Jira: scrum', jira_read.JIRA_WARNING)]
    assert 'bad jira reference' in app.log.text()
