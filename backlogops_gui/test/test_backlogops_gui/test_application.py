#! /usr/local/bin/python3
"""Tests for the backlog operations application logic."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable, Optional, TextIO, cast
import pytest
from backlogops import AvailableTeamsConfig, BacklogReleases
from backlogops_gui import application
from backlogops_gui.application import APP_TITLE, BacklogApp
from backlogops_gui.io_dialogs import ConfigChoice, ReadOptions

DATA = BacklogReleases(backlog=[], releases=[])


def _root_or_skip() -> tk.Tk:
    """Return a withdrawn Tk root, or skip when no display is available."""
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip('no display available')
    root.withdraw()
    return root


class _Recorder:
    """Record the message-box calls made through it."""

    def __init__(self) -> None:
        """Start with an empty record of calls."""
        self.calls: list[tuple[str, str]] = []

    def showerror(self, title: str, message: str, parent: object) -> None:
        """Record a shown error message."""
        assert parent is not None
        self.calls.append((title, message))

    def showinfo(self, title: str, message: str, parent: object) -> None:
        """Record a shown informational message."""
        assert parent is not None
        self.calls.append((title, message))


class _FakeBridge:
    """Stand-in wizard bridge that records being closed."""

    def __init__(self, root: object, log: object) -> None:
        """Accept the wizard arguments and start unclosed."""
        assert root is not None and log is not None
        self.closed = False

    def close(self) -> None:
        """Record that the bridge was closed."""
        self.closed = True


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


def _raise_exit(_arg: object, captured: TextIO) -> AvailableTeamsConfig:
    """Report a missing file and exit, as the config loader does."""
    captured.write('File aha does not exist. Cannot proceed.\n')
    raise SystemExit(1)


def _choices(*values: ConfigChoice) -> Callable[[object], ConfigChoice]:
    """Return a stub yielding the given no-config choices in turn."""
    pending = list(values)

    def chooser(_parent: object) -> ConfigChoice:
        return pending.pop(0)
    return chooser


def _load_for_path(config: object) -> Callable[[object, object], object]:
    """Return a loader that fails without a path and works with one."""
    def loader(arg: object, _sink: object) -> object:
        if arg is None:
            raise RuntimeError('none')
        return config
    return loader


def _read_opts(_parent: object, _presets: object) -> ReadOptions:
    """Return read options as if the format dialog was confirmed."""
    return ReadOptions(None)


def _read_data(_path: object, _value: object, _presets: object,
               _sink: object) -> BacklogReleases:
    """Return fixed data as if a backlog file was read."""
    return DATA


def _read_fail(_path: object, _value: object, _presets: object,
               _sink: object) -> BacklogReleases:
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


def test_initial_config_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a loader that exits is reported instead of ending the program."""
    monkeypatch.setattr(application, 'get_available_teams', _raise_exit)
    result, error = application.initial_config('aha')
    assert result is None
    assert error == 'File aha does not exist. Cannot proceed.'


def test_start_with_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test start adopts a loaded configuration and is ready."""
    config = FakeConfig()
    monkeypatch.setattr(application, 'get_available_teams', _returns(config))
    app = _app()
    assert app.start(None) is True
    assert app.config is cast(AvailableTeamsConfig, config)
    assert app.config_source == 'the default location'


def test_start_runs_wizard(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the no-config dialog can run the wizard to become ready."""
    config = cast(AvailableTeamsConfig, FakeConfig())
    monkeypatch.setattr(application, 'get_available_teams', _raise_none)
    monkeypatch.setattr(application, 'ask_no_config_choice',
                        _choices(ConfigChoice.WIZARD))
    app = _app()
    monkeypatch.setattr(app, 'run_wizard', lambda: config)
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    assert app.start(None) is True
    assert app.config is config
    assert app.config_source == 'the wizard'
    assert not errors


def test_start_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test choosing exit in the no-config dialog is not ready."""
    monkeypatch.setattr(application, 'get_available_teams', _raise_none)
    monkeypatch.setattr(application, 'ask_no_config_choice',
                        _choices(ConfigChoice.EXIT))
    assert _app().start(None) is False


def test_start_wizard_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled startup wizard returns to the no-config dialog."""
    monkeypatch.setattr(application, 'get_available_teams', _raise_none)
    monkeypatch.setattr(application, 'ask_no_config_choice',
                        _choices(ConfigChoice.WIZARD, ConfigChoice.EXIT))
    app = _app()
    monkeypatch.setattr(app, 'run_wizard', lambda: None)
    assert app.start(None) is False


def test_start_loads_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the no-config dialog can load a chosen configuration file."""
    config = FakeConfig()
    monkeypatch.setattr(application, 'get_available_teams',
                        _load_for_path(config))
    monkeypatch.setattr(application, 'ask_no_config_choice',
                        _choices(ConfigChoice.LOAD))
    monkeypatch.setattr(application, 'choose_existing_config',
                        lambda parent: 'teams.cfg')
    app = _app()
    assert app.start(None) is True
    assert app.config is cast(AvailableTeamsConfig, config)
    assert app.config_source == 'teams.cfg'


def test_start_load_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the load chooser returns to the no-config dialog."""
    monkeypatch.setattr(application, 'get_available_teams', _raise_none)
    monkeypatch.setattr(application, 'ask_no_config_choice',
                        _choices(ConfigChoice.LOAD, ConfigChoice.EXIT))
    monkeypatch.setattr(application, 'choose_existing_config',
                        lambda parent: None)
    assert _app().start(None) is False


def test_start_load_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a bad chosen file is reported and returns to the dialog."""
    monkeypatch.setattr(application, 'get_available_teams', _raise_none)
    monkeypatch.setattr(application, 'ask_no_config_choice',
                        _choices(ConfigChoice.LOAD, ConfigChoice.EXIT))
    monkeypatch.setattr(application, 'choose_existing_config',
                        lambda parent: 'bad.cfg')
    app = _app()
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    assert app.start(None) is False
    assert errors == [('Configuration error', 'none')]


def test_exit_config_dialog(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a -c file that makes the loader exit reaches the no-config dialog.

    This is the missing-file case that previously ended the application
    silently instead of reporting the error and offering the choices.
    """
    config = cast(AvailableTeamsConfig, FakeConfig())
    monkeypatch.setattr(application, 'get_available_teams', _raise_exit)
    monkeypatch.setattr(application, 'ask_no_config_choice',
                        _choices(ConfigChoice.WIZARD))
    app = _app()
    monkeypatch.setattr(app, 'run_wizard', lambda: config)
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    assert app.start('aha') is True
    assert errors == [('Configuration error',
                       'File aha does not exist. Cannot proceed.')]


def test_bad_config_shows_err(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a bad named configuration is reported before the dialog."""
    config = cast(AvailableTeamsConfig, FakeConfig())
    monkeypatch.setattr(application, 'get_available_teams', _raise_missing)
    monkeypatch.setattr(application, 'ask_no_config_choice',
                        _choices(ConfigChoice.WIZARD))
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


def test_available_teams() -> None:
    """Test the available teams come from the loaded configuration."""
    config = FakeConfig()
    assert _app(config).available_teams() is \
        cast(AvailableTeamsConfig, config)
    assert _app().available_teams() is None


def test_show_messages(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the show helpers forward to the message box."""
    recorder = _Recorder()
    monkeypatch.setattr(application, 'messagebox', recorder)
    app = _app()
    app.show_error('E', 'err')
    app.show_info('I', 'info')
    assert recorder.calls == [('E', 'err'), ('I', 'info')]


def test_run_wizard_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a successful wizard run returns the configuration."""
    config = cast(AvailableTeamsConfig, FakeConfig())
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'teams_config_wizard',
                        lambda bridge: config)
    assert _app().run_wizard() is config


def test_run_wizard_eof(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a wizard cancelled with EOF returns no configuration."""
    def cancel(bridge: object) -> AvailableTeamsConfig:
        raise EOFError()
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'teams_config_wizard', cancel)
    assert _app().run_wizard() is None


def test_run_wizard_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a wizard IO error is reported and returns no configuration."""
    def boom(bridge: object) -> AvailableTeamsConfig:
        raise ValueError('bad')
    monkeypatch.setattr(application, 'TkWizardBridge', _FakeBridge)
    monkeypatch.setattr(application, 'teams_config_wizard', boom)
    app = _app()
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    assert app.run_wizard() is None
    assert errors == [('Wizard error', 'bad')]


def test_teams_wizard_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled wizard leaves the configuration unchanged."""
    app = _app()
    monkeypatch.setattr(app, 'run_wizard', lambda: None)
    infos: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_info', _record(infos))
    app.run_teams_wizard()
    assert app.config is None
    assert not infos


def test_write_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the file chooser writes nothing."""
    config = FakeConfig()
    monkeypatch.setattr(application, 'choose_config_file', _pick_none)
    app = _app(config)
    app.write_config()
    assert config.written is None


def test_write_io_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a write failure is reported to the user."""
    class _Failing(FakeConfig):
        def write(self, to_json_filename: str, stderr_file: object) -> None:
            raise OSError('disk full')
    monkeypatch.setattr(application, 'choose_config_file', _pick_teams)
    app = _app(_Failing())
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(app, 'show_error', _record(errors))
    app.write_config()
    assert errors == [('Could not write configuration', 'disk full')]


def test_read_options_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the read-options dialog opens no window."""
    monkeypatch.setattr(application, 'choose_input_file', _pick_csv)
    monkeypatch.setattr(application, 'ask_read_options', lambda *a: None)
    app = _app()
    opened: list[object] = []
    monkeypatch.setattr(app, 'open_backlog', _opener(opened))
    app.read_backlog_file()
    assert not opened


def test_open_backlog(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test opening a backlog constructs a backlog window."""
    made: list[tuple[object, ...]] = []
    monkeypatch.setattr(application, 'BacklogWindow',
                        lambda *args: made.append(args))
    _app().open_backlog(DATA, 'Title')
    assert len(made) == 1
    assert made[0][1] is DATA and made[0][2] == 'Title'


def test_build_parser() -> None:
    """Test the launcher parser reads the configuration option."""
    parsed = application._build_parser().parse_args(['-c', 'x.cfg'])
    assert parsed.config == 'x.cfg'


def test_build_menu_and_body(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the menu and body build and the log view refreshes."""
    monkeypatch.setattr(application, 'check_tcltk_version', lambda root: None)
    monkeypatch.setattr(application, 'check_python_version', lambda: None)
    root = _root_or_skip()
    try:
        app = BacklogApp(root)
        app.build_menu()
        app.build_body()
        app.log.write('a log line\n')
        app._refresh_log()
        app._update_status()
        assert 'No configuration' in app._status_text()
    finally:
        root.destroy()


def test_body_config_warn(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the body shows the loaded status and a version warning."""
    monkeypatch.setattr(application, 'check_tcltk_version',
                        lambda root: 'old Tk warning')
    monkeypatch.setattr(application, 'check_python_version', lambda: None)
    root = _root_or_skip()
    try:
        app = BacklogApp(root, cast(AvailableTeamsConfig, FakeConfig()))
        app.config_source = 'a file'
        app.build_body()
        assert app._status_text() == 'Configuration loaded from a file.'
    finally:
        root.destroy()


def test_refresh_no_view() -> None:
    """Test the log refresh returns at once before the view exists."""
    root = _root_or_skip()
    try:
        BacklogApp(root)._refresh_log()
    finally:
        root.destroy()


def test_sched_destroyed() -> None:
    """Test the log refresh stops quietly once the window is gone."""
    root = _root_or_skip()
    app = BacklogApp(root)
    app.build_body()
    root.destroy()
    app._schedule_refresh()


class _FakeRoot:
    """Minimal main-window stand-in used to drive ``main``."""

    def __init__(self) -> None:
        """Start with no title set and nothing run yet."""
        self.titled: Optional[str] = None
        self.destroyed = False
        self.looped = False

    def title(self, text: str) -> None:
        """Record the window title."""
        self.titled = text

    def destroy(self) -> None:
        """Record that the window was destroyed."""
        self.destroyed = True

    def mainloop(self) -> None:
        """Record that the main loop was entered."""
        self.looped = True


def _main_patches(monkeypatch: pytest.MonkeyPatch, root: _FakeRoot,
                  ready: bool) -> None:
    """Patch main's dependencies to use a fake root and readiness."""
    monkeypatch.setattr('backlogops_gui.application.tk.Tk', lambda: root)
    auto = 'backlogops_gui.application.argcomplete.autocomplete'
    monkeypatch.setattr(auto, lambda parser: None)
    monkeypatch.setattr(BacklogApp, 'start', lambda self, arg: ready)
    monkeypatch.setattr(BacklogApp, 'build_menu', lambda self: None)
    monkeypatch.setattr(BacklogApp, 'build_body', lambda self: None)


def test_main_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main builds the window and enters the loop when ready."""
    root = _FakeRoot()
    _main_patches(monkeypatch, root, ready=True)
    application.main([])
    assert root.titled == APP_TITLE
    assert root.looped is True


def test_main_not_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main destroys the window and exits when not ready."""
    root = _FakeRoot()
    _main_patches(monkeypatch, root, ready=False)
    application.main([])
    assert root.destroyed is True
    assert root.looped is False


# pylint: disable-next=too-few-public-methods
class _FakeReporter:
    """Stand-in reporter writing a fixed line to its stream."""

    def print(self, out_file: TextIO) -> None:
        """Write a version report line to the stream."""
        out_file.write('backlogops-gui report\n')


# pylint: disable-next=too-few-public-methods
class _FailReporter:
    """Stand-in reporter raising a network-like error."""

    def print(self, out_file: TextIO) -> None:
        """Raise an error as if PyPI could not be reached."""
        assert out_file is not None
        raise OSError('no network')


# pylint: disable-next=too-few-public-methods
class _FakeThread:
    """Records the thread target and runs it when started."""

    def __init__(self, target: Callable[[], None], daemon: bool) -> None:
        """Store the worker target and the daemon flag."""
        self.target = target
        self.daemon = daemon
        self.started = False

    def start(self) -> None:
        """Run the stored target as the started worker would."""
        self.started = True
        self.target()


def test_write_report_log(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the worker writes the version report to the log."""
    monkeypatch.setattr(application, 'BloGuiVersionReporter', _FakeReporter)
    app = _app()
    app._write_version_report()
    assert 'backlogops-gui report' in app.log.text()


def test_write_report_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a failing report is logged rather than raised."""
    monkeypatch.setattr(application, 'BloGuiVersionReporter', _FailReporter)
    app = _app()
    app._write_version_report()
    assert 'Could not report versions: no network' in app.log.text()


def test_report_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the report runs on a started daemon thread via the log."""
    made: list[_FakeThread] = []

    def make_thread(target: Callable[[], None], daemon: bool) -> _FakeThread:
        thread = _FakeThread(target, daemon)
        made.append(thread)
        return thread
    monkeypatch.setattr('backlogops_gui.application.threading.Thread',
                        make_thread)
    monkeypatch.setattr(application, 'BloGuiVersionReporter', _FakeReporter)
    app = _app()
    app.report_versions()
    assert len(made) == 1 and made[0].daemon is True
    assert made[0].started is True
    assert 'Collecting version information' in app.log.text()
    assert 'backlogops-gui report' in app.log.text()


def test_body_python_warn(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the body shows the Python version warning when present."""
    monkeypatch.setattr(application, 'check_tcltk_version', lambda root: None)
    monkeypatch.setattr(application, 'check_python_version',
                        lambda: 'old Python warning')
    root = _root_or_skip()
    try:
        app = BacklogApp(root)
        app.build_body()
        texts = [w.cget('text') for w in app.root.winfo_children()
                 if isinstance(w, tk.Label)]
        assert 'old Python warning' in texts
    finally:
        root.destroy()
