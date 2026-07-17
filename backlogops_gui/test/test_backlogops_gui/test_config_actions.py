#! /usr/local/bin/python3
"""Tests for the configuration, preset and write menu actions.

These cover running the configuration wizard and the IO preset wizard,
each of which first asks whether to start empty or be pre-filled from an
existing file, and writing a configuration or preset to a chosen file with
the overwrite confirmation and the crash-safe write.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Callable, TextIO, cast
import pytest
from backlogops import BacklogOpsConfig, OutputFormatConfig
from backlogops_gui import application
from backlogops_gui.choice_dialogs import SourceChoice
from .app_test_helpers import (
    FakeConfig, make_app as _app, pick_none as _pick_none,
    raise_exit as _raise_exit, record as _record, returns as _returns)
from .gui_test_helpers import MsgRecorder


# pylint: disable-next=too-few-public-methods
class _FakeBridge:
    """Stand-in wizard bridge that records being closed."""

    def __init__(self, root: object, log: object) -> None:
        """Accept the wizard arguments and start unclosed."""
        assert root is not None and log is not None
        self.closed = False

    def close(self) -> None:
        """Record that the bridge was closed."""
        self.closed = True


def _source(choice: SourceChoice) -> Callable[..., SourceChoice]:
    """Return a stub source dialog yielding the given source choice."""
    def chooser(_parent: object, _title: str, _text: str) -> SourceChoice:
        return choice
    return chooser


def _wizard_of(config: object) -> Callable[..., object]:
    """Return a wizard stub yielding a fixed config, accepting default."""
    def wizard(_bridge: object, *, default: object = None) -> object:
        _ = default
        return config
    return wizard


def _rec_wizard(seen: list[object], result: object) -> Callable[..., object]:
    """Return a run_wizard stub recording its default and yielding result."""
    def run(default: object = None) -> object:
        seen.append(default)
        return result
    return run


def _safe_write_rec(store: list[str]) -> Callable[..., None]:
    """Return a crash-safe-write stub that records the output path."""
    def writer(_config: object, output: str, _stderr: object) -> None:
        store.append(output)
    return writer


def _preset_of(value: object) -> Callable[..., object]:
    """Return a read_io_preset stub yielding a fixed preset config."""
    def read(_path: object, _hook: object, _stderr: object) -> object:
        return value
    return read


def _preset_exit(_path: object, _hook: object, captured: TextIO) -> object:
    """Report a bad preset file and exit, as the preset reader does."""
    captured.write('File bad.cfg is not a preset. Cannot proceed.\n')
    raise SystemExit(1)


def _pick_teams(_parent: object) -> str:
    """Return a configuration file name without an extension."""
    return 'teams'


def _pick_path(target: Path) -> Callable[[object], str]:
    """Return a chooser stub yielding the given target path as a string."""
    def chooser(_parent: object) -> str:
        return str(target)
    return chooser


def test_run_wizard_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a successful wizard run returns the configuration."""
    config = cast(BacklogOpsConfig, FakeConfig())
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'backlog_ops_wizard', _wizard_of(config))
    assert _app().run_wizard() is config


def test_run_wizard_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the pre-fill default is passed on to the wizard."""
    seen: list[object] = []

    def wizard(_bridge: object, *, default: object = None) -> object:
        seen.append(default)
        return default
    prefill = FakeConfig()
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'backlog_ops_wizard', wizard)
    _app().run_wizard(cast(BacklogOpsConfig, prefill))
    assert seen == [prefill]


def test_run_wizard_eof(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a wizard cancelled with EOF returns no configuration."""
    def cancel(_bridge: object, *, default: object = None) -> BacklogOpsConfig:
        _ = default
        raise EOFError()
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'backlog_ops_wizard', cancel)
    assert _app().run_wizard() is None


def test_run_wizard_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a wizard IO error is reported and returns no configuration."""
    def boom(_bridge: object, *, default: object = None) -> BacklogOpsConfig:
        _ = default
        raise ValueError('bad')
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'backlog_ops_wizard', boom)
    app = _app()
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    assert app.run_wizard() is None
    assert errors == [('Wizard error', 'bad')]


def test_cfg_wiz_active(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a from-scratch wizard result becomes the active config."""
    config = cast(BacklogOpsConfig, FakeConfig())
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.SCRATCH))
    app = _app()
    seen: list[object] = []
    monkeypatch.setattr(app, 'run_wizard', _rec_wizard(seen, config))
    infos: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_info', _record(infos))
    app.run_config_wizard()
    assert app.config is config
    assert seen == [None]
    assert len(infos) == 1


def test_cfg_wiz_prefill(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test basing the wizard on a file pre-fills it with that file."""
    prefill = cast(BacklogOpsConfig, FakeConfig())
    result = cast(BacklogOpsConfig, FakeConfig())
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.FROM_FILE))
    monkeypatch.setattr(application, 'choose_existing_config', _pick_teams)
    monkeypatch.setattr(application, 'read_backlog_ops_config',
                        _returns(prefill))
    app = _app()
    seen: list[object] = []
    monkeypatch.setattr(app, 'run_wizard', _rec_wizard(seen, result))
    monkeypatch.setattr(app, 'show_info', _record([]))
    app.run_config_wizard()
    assert seen == [prefill]
    assert app.config is result


def test_cfg_wiz_src_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the source dialog runs no wizard."""
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.CANCEL))
    app = _app()
    seen: list[object] = []
    monkeypatch.setattr(app, 'run_wizard', _rec_wizard(seen, None))
    app.run_config_wizard()
    assert app.config is None
    assert not seen


def test_cfg_wiz_file_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the file chooser runs no wizard."""
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.FROM_FILE))
    monkeypatch.setattr(application, 'choose_existing_config', _pick_none)
    app = _app()
    seen: list[object] = []
    monkeypatch.setattr(app, 'run_wizard', _rec_wizard(seen, None))
    app.run_config_wizard()
    assert not seen


def test_cfg_wiz_read_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a pre-fill read failure is reported and runs no wizard."""
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.FROM_FILE))
    monkeypatch.setattr(application, 'choose_existing_config', _pick_teams)
    monkeypatch.setattr(application, 'read_backlog_ops_config', _raise_exit)
    app = _app()
    seen: list[object] = []
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'run_wizard', _rec_wizard(seen, None))
    monkeypatch.setattr(app, 'show_error', _record(errors))
    app.run_config_wizard()
    assert not seen
    assert len(errors) == 1


def test_cfg_wiz_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled wizard leaves the configuration unchanged."""
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.SCRATCH))
    app = _app()
    seen: list[object] = []
    monkeypatch.setattr(app, 'run_wizard', _rec_wizard(seen, None))
    infos: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_info', _record(infos))
    app.run_config_wizard()
    assert app.config is None
    assert not infos


def test_preset_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test creating a preset writes the wizard result to a chosen file."""
    config = FakeConfig()
    written: list[str] = []
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.SCRATCH))
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'preset_wizard', _wizard_of(config))
    monkeypatch.setattr(application, 'choose_config_file', _pick_teams)
    monkeypatch.setattr(application, 'safe_write_config',
                        _safe_write_rec(written))
    app = _app()
    infos: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_info', _record(infos))
    app.create_preset_file()
    assert written == ['teams.cfg']
    assert infos == [('Wrote preset', 'Wrote teams.cfg')]


def test_preset_from_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test basing a preset on a file pre-fills the wizard from it."""
    prefill = cast(OutputFormatConfig, FakeConfig())
    seen: list[object] = []

    def wizard(_bridge: object, *, default: object = None) -> object:
        seen.append(default)
        return default
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.FROM_FILE))
    monkeypatch.setattr(application, 'choose_existing_preset', _pick_teams)
    monkeypatch.setattr(application, 'read_io_preset', _preset_of(prefill))
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'preset_wizard', wizard)
    monkeypatch.setattr(application, 'choose_config_file', _pick_none)
    _app().create_preset_file()
    assert seen == [prefill]


def test_preset_src_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the source dialog runs no preset wizard."""
    ran: list[object] = []

    def wizard(_bridge: object, *, default: object = None) -> object:
        ran.append(default)
        return default
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.CANCEL))
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'preset_wizard', wizard)
    _app().create_preset_file()
    assert not ran


def test_preset_read_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a preset pre-fill read failure is reported, writes nothing."""
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.FROM_FILE))
    monkeypatch.setattr(application, 'choose_existing_preset', _pick_teams)
    monkeypatch.setattr(application, 'read_io_preset', _preset_exit)
    picked: list[object] = []
    monkeypatch.setattr(application, 'choose_config_file', picked.append)
    app = _app()
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    app.create_preset_file()
    assert not picked
    assert len(errors) == 1


def test_preset_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an abandoned preset wizard asks for no file and writes nothing."""
    def cancel(_bridge: object, *,
               default: object = None) -> OutputFormatConfig:
        _ = default
        raise EOFError()
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.SCRATCH))
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'preset_wizard', cancel)
    picked: list[object] = []
    monkeypatch.setattr(application, 'choose_config_file', picked.append)
    _app().create_preset_file()
    assert not picked


def test_preset_save_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the save chooser writes no preset file."""
    config = FakeConfig()
    written: list[str] = []
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.SCRATCH))
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'preset_wizard', _wizard_of(config))
    monkeypatch.setattr(application, 'choose_config_file', _pick_none)
    monkeypatch.setattr(application, 'safe_write_config',
                        _safe_write_rec(written))
    _app().create_preset_file()
    assert not written


def test_preset_write_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a preset write failure is reported to the user."""
    def boom(_config: object, _output: str, _stderr: object) -> None:
        raise OSError('disk full')
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.SCRATCH))
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'preset_wizard', _wizard_of(FakeConfig()))
    monkeypatch.setattr(application, 'choose_config_file', _pick_teams)
    monkeypatch.setattr(application, 'safe_write_config', boom)
    app = _app()
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    app.create_preset_file()
    assert errors == [('Could not write preset', 'disk full')]


def test_preset_wizard_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a preset wizard failure is reported and writes nothing."""
    def boom(_bridge: object, *, default: object = None) -> OutputFormatConfig:
        _ = default
        raise ValueError('bad')
    monkeypatch.setattr(application, 'ask_source_choice',
                        _source(SourceChoice.SCRATCH))
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'preset_wizard', boom)
    app = _app()
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    app.create_preset_file()
    assert errors == [('Preset wizard error', 'bad')]


def test_write_config_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test writing the configuration adds the extension and reports."""
    config = FakeConfig()
    written: list[str] = []
    monkeypatch.setattr(application, 'choose_config_file', _pick_teams)
    monkeypatch.setattr(application, 'safe_write_config',
                        _safe_write_rec(written))
    app = _app(config)
    infos: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_info', _record(infos))
    app.write_config()
    assert written == ['teams.cfg']
    assert infos == [('Wrote configuration', 'Wrote teams.cfg')]


def test_write_config_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test writing without a configuration reports the problem."""
    app = _app()
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    app.write_config()
    assert errors == [('No configuration',
                       'There is no configuration to write.')]


def test_write_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the file chooser writes nothing."""
    config = FakeConfig()
    monkeypatch.setattr(application, 'choose_config_file', _pick_none)
    app = _app(config)
    app.write_config()
    assert config.written is None


def test_write_io_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a write failure is reported to the user."""
    def boom(_config: object, _output: str, _stderr: object) -> None:
        raise OSError('disk full')
    monkeypatch.setattr(application, 'choose_config_file', _pick_teams)
    monkeypatch.setattr(application, 'safe_write_config', boom)
    app = _app(FakeConfig())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    app.write_config()
    assert errors == [('Could not write configuration', 'disk full')]


def test_write_new_no_prompt(tmp_path: Path,
                             monkeypatch: pytest.MonkeyPatch) -> None:
    """Test writing a new file does not ask to overwrite."""
    target = tmp_path / 'new.cfg'
    written: list[str] = []
    recorder = MsgRecorder()
    monkeypatch.setattr(application, 'messagebox', recorder)
    monkeypatch.setattr(application, 'choose_config_file', _pick_path(target))
    monkeypatch.setattr(application, 'safe_write_config',
                        _safe_write_rec(written))
    app = _app(FakeConfig())
    monkeypatch.setattr(app, 'show_info', _record([]))
    app.write_config()
    assert written == [str(target)]
    assert not recorder.calls


def test_write_overwrite_yes(tmp_path: Path,
                             monkeypatch: pytest.MonkeyPatch) -> None:
    """Test confirming the overwrite of an existing file writes it."""
    target = tmp_path / 'old.cfg'
    target.write_text('OLD', encoding='utf-8')
    written: list[str] = []
    recorder = MsgRecorder(yes=True)
    monkeypatch.setattr(application, 'messagebox', recorder)
    monkeypatch.setattr(application, 'choose_config_file', _pick_path(target))
    monkeypatch.setattr(application, 'safe_write_config',
                        _safe_write_rec(written))
    app = _app(FakeConfig())
    monkeypatch.setattr(app, 'show_info', _record([]))
    app.write_config()
    assert written == [str(target)]
    assert len(recorder.calls) == 1


def test_write_overwrite_no(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test declining the overwrite of an existing file writes nothing."""
    target = tmp_path / 'old.cfg'
    target.write_text('OLD', encoding='utf-8')
    written: list[str] = []
    recorder = MsgRecorder(yes=False)
    monkeypatch.setattr(application, 'messagebox', recorder)
    monkeypatch.setattr(application, 'choose_config_file', _pick_path(target))
    monkeypatch.setattr(application, 'safe_write_config',
                        _safe_write_rec(written))
    infos: list[tuple[str, str]] = []
    app = _app(FakeConfig())
    monkeypatch.setattr(app, 'show_info', _record(infos))
    app.write_config()
    assert not written
    assert not infos
