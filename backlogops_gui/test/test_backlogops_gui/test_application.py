#! /usr/local/bin/python3
"""Tests for the backlog operations application logic."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable, Optional, cast
import pytest
from backlogops import AvailableTeamsConfig, BacklogReleases
from backlogops_gui import application
from backlogops_gui.application import BacklogApp
from backlogops_gui.io_dialogs import ReadOptions

DATA = BacklogReleases(backlog=[], releases=[])


# pylint: disable-next=too-few-public-methods
class FakeConfig:
    """Stand-in configuration recording where it was written."""

    def __init__(self) -> None:
        """Create non-empty presets and an unset written destination."""
        self.input_configs: dict[str, object] = {'in': object()}
        self.output_configs: dict[str, object] = {'out': object()}
        self.written: Optional[str] = None

    def write(self, to_json_filename: str, stderr_file: object) -> None:
        """Record the destination the configuration was written to."""
        assert stderr_file is not None
        self.written = to_json_filename


def _app(config: Optional[FakeConfig] = None) -> BacklogApp:
    """Return an application over a dummy root for logic-only tests."""
    typed = cast(Optional[AvailableTeamsConfig], config)
    return BacklogApp(cast(tk.Tk, object()), typed)


def _record(store: list[tuple[str, str]]) -> Callable[[str, str], None]:
    """Return a callback that records its title and message."""
    def recorder(title: str, message: str) -> None:
        store.append((title, message))
    return recorder


def _opener(store: list[object]) -> Callable[[BacklogReleases, str], None]:
    """Return a callback that records an opened backlog and title."""
    def recorder(backlog: BacklogReleases, title: str) -> None:
        store.append((backlog, title))
    return recorder


def _raise_none(_arg: object, _sink: object) -> AvailableTeamsConfig:
    """Raise as if no configuration file was found."""
    raise RuntimeError('none')


def _raise_missing(_arg: object, _sink: object) -> AvailableTeamsConfig:
    """Raise as if a named configuration file was missing."""
    raise FileNotFoundError('missing')


def _read_opts(_parent: object, _presets: object) -> ReadOptions:
    """Return read options as if the format dialog was confirmed."""
    return ReadOptions(None)


def _read_data(_path: object, _value: object,
               _presets: object) -> BacklogReleases:
    """Return fixed data as if a backlog file was read."""
    return DATA


def _read_fail(_path: object, _value: object,
               _presets: object) -> BacklogReleases:
    """Raise as if reading a backlog file failed."""
    raise ValueError('bad file')


def _returns(value: object) -> Callable[[object, object], object]:
    """Return a two-argument stub yielding a fixed value."""
    def get(_arg: object, _sink: object) -> object:
        return value
    return get


def _pick_csv(_parent: object) -> str:
    """Return a backlog file name as if the chooser was confirmed."""
    return 'file.csv'


def _pick_none(_parent: object) -> Optional[str]:
    """Return nothing as if the file chooser was cancelled."""
    return None


def _pick_teams(_parent: object) -> str:
    """Return a configuration file name without an extension."""
    return 'teams'


def test_initial_config_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a loaded configuration is returned without an error."""
    config = FakeConfig()
    monkeypatch.setattr(application, 'get_available_teams', _returns(config))
    result, error = application.initial_config(None)
    assert result is cast(AvailableTeamsConfig, config)
    assert error is None


def test_initial_config_err(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a lookup failure is mapped to a None config and a message."""
    monkeypatch.setattr(application, 'get_available_teams', _raise_none)
    result, error = application.initial_config(None)
    assert result is None
    assert error == 'none'


def test_start_with_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test start adopts a loaded configuration and is ready."""
    config = FakeConfig()
    monkeypatch.setattr(application, 'get_available_teams', _returns(config))
    app = _app()
    assert app.start(None) is True
    assert app.config is cast(AvailableTeamsConfig, config)


def test_start_runs_wizard(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test start runs the wizard when no configuration is found."""
    config = cast(AvailableTeamsConfig, FakeConfig())
    monkeypatch.setattr(application, 'get_available_teams', _raise_none)
    app = _app()
    monkeypatch.setattr(app, 'run_wizard', lambda: config)
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    assert app.start(None) is True
    assert app.config is config
    assert not errors


def test_start_wizard_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test start is not ready when the startup wizard is cancelled."""
    monkeypatch.setattr(application, 'get_available_teams', _raise_none)
    app = _app()
    monkeypatch.setattr(app, 'run_wizard', lambda: None)
    assert app.start(None) is False


def test_bad_config_shows_err(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a bad named configuration is reported before the wizard."""
    config = cast(AvailableTeamsConfig, FakeConfig())
    monkeypatch.setattr(application, 'get_available_teams', _raise_missing)
    app = _app()
    monkeypatch.setattr(app, 'run_wizard', lambda: config)
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    assert app.start('bad.cfg') is True
    assert errors == [('Configuration error', 'missing')]


def test_read_backlog_opens(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test reading a backlog opens it in a new window."""
    monkeypatch.setattr(application, 'choose_input_file', _pick_csv)
    monkeypatch.setattr(application, 'ask_read_options', _read_opts)
    monkeypatch.setattr(application, 'read_backlog', _read_data)
    app = _app()
    opened: list[object] = []
    monkeypatch.setattr(app, 'open_backlog', _opener(opened))
    app.read_backlog_file()
    assert opened == [(DATA, 'file.csv')]


def test_read_cancel_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test no window opens when the file selection is cancelled."""
    monkeypatch.setattr(application, 'choose_input_file', _pick_none)
    app = _app()
    opened: list[object] = []
    monkeypatch.setattr(app, 'open_backlog', _opener(opened))
    app.read_backlog_file()
    assert not opened


def test_read_error_dialog(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a read failure is reported and opens no window."""
    monkeypatch.setattr(application, 'choose_input_file', _pick_csv)
    monkeypatch.setattr(application, 'ask_read_options', _read_opts)
    monkeypatch.setattr(application, 'read_backlog', _read_fail)
    app = _app()
    errors: list[tuple[str, str]] = []
    opened: list[object] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    monkeypatch.setattr(app, 'open_backlog', _opener(opened))
    app.read_backlog_file()
    assert errors == [('Could not read file', 'bad file')]
    assert not opened


def test_demo_backlog_opens(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the demo action opens the demo backlog in a window."""
    monkeypatch.setattr(application, 'get_demo_backlog', lambda: DATA)
    app = _app()
    opened: list[object] = []
    monkeypatch.setattr(app, 'open_backlog', _opener(opened))
    app.new_demo_backlog()
    assert opened == [(DATA, 'Demo backlog')]


def test_write_config_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test writing the configuration adds the extension and reports."""
    config = FakeConfig()
    monkeypatch.setattr(application, 'choose_config_file', _pick_teams)
    app = _app(config)
    infos: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_info', _record(infos))
    app.write_config()
    assert config.written == 'teams.cfg'
    assert infos == [('Wrote configuration', 'Wrote teams.cfg')]


def test_write_config_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test writing without a configuration reports the problem."""
    app = _app()
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    app.write_config()
    assert errors == [('No configuration',
                       'There is no configuration to write.')]


def test_teams_wizard_active(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a wizard result becomes the active configuration."""
    config = cast(AvailableTeamsConfig, FakeConfig())
    app = _app()
    monkeypatch.setattr(app, 'run_wizard', lambda: config)
    infos: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_info', _record(infos))
    app.run_teams_wizard()
    assert app.config is config
    assert len(infos) == 1


def test_presets_from_config() -> None:
    """Test the presets come from the current configuration."""
    config = FakeConfig()
    app = _app(config)
    assert app.in_presets() == config.input_configs
    assert app.out_presets() == config.output_configs


def test_no_cfg_no_presets() -> None:
    """Test there are no presets when no configuration is loaded."""
    app = _app()
    assert app.in_presets() is None
    assert app.out_presets() is None
