#! /usr/local/bin/python3
"""Tests for the configuration and preset edit menu actions.

These cover choosing what to edit, what the session is given, what becomes
of the configuration the application uses, and how a file that cannot be
opened is reported. The editor window itself runs until the user closes it,
so the logic tests put a scripted session in its place; that stand-in
builds the model the window would have shown, so a file that cannot be
opened is refused there exactly as it is in a window. One test with a
display mounts the real editor in a window and checks what it wired up.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import gc
import tkinter as tk
from pathlib import Path
from typing import Callable, Optional, cast
import pytest
from config_as_json import Config
from edit_cfg_json import EditModel, editor_model
from backlogops import (
    AvailableTeams, BacklogOpsConfig, EDIT_SETTINGS, InputFormatConfig,
    NoTextIO, Team, descriptions_for, write_backlog_ops_config)
from backlogops_gui import config_edit
from backlogops_gui.application import BacklogApp
from backlogops_gui.choice_dialogs import EditTargetChoice
from .gui_test_helpers import CloseSpy, gui_root
from .app_test_helpers import record

VELOCITY = ('available_teams', 'teams', '0', 'velocity')
"""Path of the velocity of the one team of the test configuration."""


def _config() -> BacklogOpsConfig:
    """Return a configuration with one team whose velocity can be edited."""
    team = Team(name='Blue', velocity=10.0, sum_fte_at_velocity=1.0,
                sprint_length=10)
    teams = AvailableTeams(persons={}, teams=[team])
    return BacklogOpsConfig(available_teams=teams, stderr_file=NoTextIO())


def _write_config(path: Path) -> None:
    """Write that configuration to a file the editor can be given."""
    write_backlog_ops_config(_config(), path, NoTextIO())


def _write_preset(path: Path) -> None:
    """Write a stand-alone input preset whose one mapping can be edited."""
    preset = InputFormatConfig(stderr_file=NoTextIO())
    preset.backlog_to_internal = {'Nivå': 'level'}
    preset.write(to_json_filename=path, stderr_file=NoTextIO())


def _app(config: Optional[BacklogOpsConfig] = None,
         source: Optional[str] = None) -> BacklogApp:
    """Return an application over a dummy root with the given config."""
    app = BacklogApp(cast(tk.Tk, object()), config)
    app.config_source = source
    return app


def _shown(config: Config, in_file: Optional[str],
           out_file: Optional[str]) -> EditModel:
    """Return the model that the real editor window would have shown."""
    return editor_model(config, descriptions=descriptions_for(config),
                        in_file=in_file, out_file=out_file,
                        settings=EDIT_SETTINGS, stderr_file=NoTextIO())


def _session(act: Callable[[EditModel], None]) -> Callable[..., EditModel]:
    """Return a stand-in editor window running one scripted session."""
    def opened(_app: object, config: Config, _title: str, *,
               in_file: Optional[str] = None,
               out_file: Optional[str] = None) -> EditModel:
        """Do to the model of the session what the script does."""
        model = _shown(config, in_file, out_file)
        act(model)
        return model
    return opened


def _recording() -> tuple[list[str], Callable[..., EditModel]]:
    """Return the recorded titles and the stand-in window recording them."""
    titles: list[str] = []

    def opened(_app: object, config: Config, title: str, *,
               in_file: Optional[str] = None,
               out_file: Optional[str] = None) -> EditModel:
        """Record the title the editor window was opened with."""
        titles.append(title)
        return _shown(config, in_file, out_file)
    return titles, opened


def _saving(text: str) -> Callable[[EditModel], None]:
    """Return a session that sets the team velocity and saves."""
    def act(model: EditModel) -> None:
        """Edit one value and write the output file."""
        model.set_text(VELOCITY, text)
        model.save()
    return act


def _closing(model: EditModel) -> None:
    """Close the editor without saving anything."""
    _ = model


def _seen_models(store: list[EditModel]) -> Callable[..., EditModel]:
    """Return a stand-in editor window that only records its model."""
    return _session(store.append)


def _patch(monkeypatch: pytest.MonkeyPatch, app: BacklogApp, *,
           opened: Callable[..., EditModel],
           target: EditTargetChoice = EditTargetChoice.IN_USE,
           chosen: Optional[str] = None) -> list[tuple[str, str]]:
    """Patch the dialogs and the editor window, recording the messages."""
    messages: list[tuple[str, str]] = []
    monkeypatch.setattr(config_edit, 'edit_in_window', opened)
    monkeypatch.setattr(config_edit, 'ask_edit_target', lambda _parent: target)
    monkeypatch.setattr(config_edit, 'choose_config_to_edit',
                        lambda _parent: chosen)
    monkeypatch.setattr(config_edit, 'choose_preset_to_edit',
                        lambda _parent: chosen)
    monkeypatch.setattr(app, 'show_error', record(messages))
    monkeypatch.setattr(app, 'show_info', record(messages))
    return messages


def _titles(messages: list[tuple[str, str]]) -> list[str]:
    """Return the titles of the messages that were shown."""
    return [title for title, _ in messages]


def test_cancelled_target(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the target dialog opens no editor at all."""
    app = _app(_config())
    seen: list[EditModel] = []
    messages = _patch(monkeypatch, app, opened=_seen_models(seen),
                      target=EditTargetChoice.CANCEL)
    config_edit.edit_config(app)
    assert not seen
    assert not messages


def test_no_config_in_use(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test editing the configuration in use needs one to be loaded."""
    app = _app()
    seen: list[EditModel] = []
    messages = _patch(monkeypatch, app, opened=_seen_models(seen))
    config_edit.edit_config(app)
    assert not seen
    assert _titles(messages) == ['No configuration']


def test_in_use_writes_source(tmp_path: Path,
                              monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a save of the configuration in use writes the file it came from."""
    source = tmp_path / 'team.cfg'
    _write_config(source)
    app = _app(_config(), str(source))
    _patch(monkeypatch, app, opened=_session(_saving('30.0')))
    config_edit.edit_config(app)
    assert isinstance(app.config, BacklogOpsConfig)
    assert app.config.available_teams.teams[0].velocity == 30.0
    assert app.config_source == str(source)


def test_in_use_without_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a configuration that came from the wizard has nowhere to save.

    The source is then a phrase and not a file, so the editor has no
    destination and asks the user for one before it can save.
    """
    app = _app(_config(), 'the wizard')
    seen: list[EditModel] = []
    _patch(monkeypatch, app, opened=_seen_models(seen))
    config_edit.edit_config(app)
    assert seen[0].out_file is None


def test_edits_chosen_file(tmp_path: Path,
                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a configuration file is read and its save becomes the config."""
    source = tmp_path / 'team.cfg'
    _write_config(source)
    app = _app()
    messages = _patch(monkeypatch, app, opened=_session(_saving('12.0')),
                      target=EditTargetChoice.FROM_FILE, chosen=str(source))
    config_edit.edit_config(app)
    assert isinstance(app.config, BacklogOpsConfig)
    assert app.config.available_teams.teams[0].velocity == 12.0
    assert app.config_source == str(source)
    assert _titles(messages) == ['Configuration saved']


def test_title_names_file(tmp_path: Path,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the window title names the file that a save would write."""
    source = tmp_path / 'team.cfg'
    _write_config(source)
    app = _app()
    titles, opened = _recording()
    _patch(monkeypatch, app, opened=opened, chosen=str(source),
           target=EditTargetChoice.FROM_FILE)
    config_edit.edit_config(app)
    assert titles == ['Edit configuration team.cfg']


def test_title_without_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the title names no file for a configuration that has none."""
    app = _app(_config(), 'the wizard')
    titles, opened = _recording()
    _patch(monkeypatch, app, opened=opened)
    config_edit.edit_config(app)
    assert titles == ['Edit configuration']


def test_cancelled_chooser(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the file chooser opens no editor and says nothing."""
    app = _app()
    seen: list[EditModel] = []
    messages = _patch(monkeypatch, app, opened=_seen_models(seen),
                      target=EditTargetChoice.FROM_FILE, chosen=None)
    config_edit.edit_config(app)
    assert not seen
    assert not messages


def test_unreadable_file(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a file that is no configuration is reported and logged."""
    bad = tmp_path / 'bad.cfg'
    bad.write_text('not json at all', encoding='utf-8')
    app = _app()
    seen: list[EditModel] = []
    messages = _patch(monkeypatch, app, opened=_seen_models(seen),
                      target=EditTargetChoice.FROM_FILE, chosen=str(bad))
    config_edit.edit_config(app)
    assert not seen
    assert _titles(messages) == [config_edit.OPEN_FAIL_TITLE]
    assert config_edit.OPEN_FAIL_TITLE in app.log.text()


def test_closed_unsaved(tmp_path: Path,
                        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test closing without saving keeps the configuration that was in use."""
    source = tmp_path / 'team.cfg'
    _write_config(source)
    before = source.read_text(encoding='utf-8')
    app = _app(_config(), str(source))
    kept = app.config
    messages = _patch(monkeypatch, app, opened=_session(_closing))
    config_edit.edit_config(app)
    assert app.config is kept
    assert source.read_text(encoding='utf-8') == before
    assert messages == [(config_edit.EDITOR_TITLE,
                         config_edit.NOT_SAVED_TEXT)]


def test_edits_preset_file(tmp_path: Path,
                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a preset file is edited as the kind the file itself says."""
    source = tmp_path / 'in.cfg'
    _write_preset(source)
    app = _app(_config())

    def act(model: EditModel) -> None:
        """Rename the mapped column and save the preset."""
        model.set_text(('backlog_to_internal', 'Nivå'), 'title')
        model.save()
    messages = _patch(monkeypatch, app, opened=_session(act),
                      chosen=str(source))
    config_edit.edit_preset_file(app)
    written = InputFormatConfig(from_json_filename=source,
                                stderr_file=NoTextIO())
    assert written.backlog_to_internal == {'Nivå': 'title'}
    assert _titles(messages) == ['Preset saved']


def test_preset_not_adopted(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test editing a preset file leaves the configuration in use alone."""
    source = tmp_path / 'in.cfg'
    _write_preset(source)
    app = _app(_config())
    kept = app.config
    _patch(monkeypatch, app, opened=_session(_closing), chosen=str(source))
    config_edit.edit_preset_file(app)
    assert app.config is kept


def test_config_as_preset(tmp_path: Path,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a complete configuration picked as a preset is refused."""
    source = tmp_path / 'team.cfg'
    _write_config(source)
    app = _app()
    seen: list[EditModel] = []
    messages = _patch(monkeypatch, app, opened=_seen_models(seen),
                      chosen=str(source))
    config_edit.edit_preset_file(app)
    assert not seen
    assert _titles(messages) == [config_edit.OPEN_FAIL_TITLE]


def test_editor_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the editor is mounted in a window that closes through it.

    No events are delivered to the window. The root of a test is withdrawn,
    and under Tk 8.6 a transient window of a withdrawn master never runs out
    of events to process, so an ``update`` here would never return. Nothing
    below needs one: a widget exists as soon as it is created.
    """
    spy = CloseSpy()
    monkeypatch.setattr(config_edit, 'bind_close', spy)
    with gui_root() as root:
        app = BacklogApp(root)
        mounted = config_edit.editor_window(
            app, BacklogOpsConfig(stderr_file=NoTextIO()),
            'Edit configuration')
        assert mounted.window.title() == 'Edit configuration'
        assert mounted.window.winfo_children()
        assert spy.calls == [(mounted.window, mounted.panel.close)]
        assert mounted.window.protocol('WM_DELETE_WINDOW')
        mounted.panel.close()
        assert not mounted.window.winfo_exists()
        # Every field of the editor owns a Tcl variable that unsets itself
        # when the Python object holding it is collected. One collected
        # after this root is destroyed, or on a worker thread another test
        # left running, raises inside its own __del__, which pytest reports
        # as an unraisable exception. So both references to those widgets
        # go here, and the collection is made to happen here.
        spy.calls.clear()
        del mounted
        gc.collect()
