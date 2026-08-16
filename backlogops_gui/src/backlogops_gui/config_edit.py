#! /usr/local/bin/python3
"""Edit a configuration in a window of the application.

The two edit actions of the configuration menu live here.
:func:`edit_config` opens the configuration the application is using, or one
in a file the user picks; :func:`edit_preset_file` opens a stand-alone input
or output preset file, whose direction is detected from the file itself.
What can be edited, what a save writes, and what each member is for all
belong to :mod:`backlogops.config_editing`, so the editor of the terminal
interface shows exactly the same configuration.

These are functions taking the application rather than a collaborator
object, because an editing session keeps nothing between two of them: the
session belongs to the window and everything else is the application's.

The editor is mounted in a :class:`tkinter.Toplevel` this module creates,
rather than started through ``edit_cfg_json_tk.edit``. That entry point
creates a ``tkinter.Tk`` and an event loop of its own, which is for an
application that runs neither yet: a second Tcl interpreter shares nothing
with the first, and a nested loop would not end when the editor window
closed, because Tcl runs its loop while any window of the process lives.
``TkEditorPanel`` is what the library offers for an application that already
runs Tk. It is given the window as its ``area``, so that the window stays
this module's — its title names the file being edited, and the editor
destroys only what it built itself.

The window is not made modal. The editor opens dialogs of its own — a file
chooser for Save as…, a question before it overwrites a file, and one asking
for the key of a new entry — and a grab held by the editor window would keep
their clicks and keys from reaching them.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from pathlib import Path
from typing import NamedTuple, Optional, TYPE_CHECKING
from config_as_json import Config, PathOrStr
from edit_cfg_json import ConfigLoadError, EditModel, default_config
from edit_cfg_json_tk import TkEditorPanel
from wizard_tk_bridge.close_binding import bind_close
from backlogops import (
    BacklogOpsConfig, EDIT_SETTINGS, descriptions_for, io_preset_class)
from backlogops_gui.choice_dialogs import EditTargetChoice, ask_edit_target
from backlogops_gui.file_choosers import (
    choose_config_to_edit, choose_preset_to_edit)

if TYPE_CHECKING:
    from backlogops_gui.application import BacklogApp

EDIT_ERRORS = (ConfigLoadError, ValueError, TypeError, KeyError, OSError)
"""Errors raised when a configuration cannot be opened for editing."""

OPEN_FAIL_TITLE = 'Could not open the configuration'
NO_CONFIG_TEXT = 'There is no configuration to edit.'
NOT_SAVED_TEXT = 'The editor was closed without saving anything.'
EDITOR_TITLE = 'Configuration editor'
ADOPTED = 'The saved configuration is now the one in use.'


class EditorWindow(NamedTuple):
    """One editor window and the panel running the session inside it."""

    window: tk.Toplevel
    panel: TkEditorPanel


def editor_window(app: 'BacklogApp', config: Config, title: str, *,
                  in_file: Optional[PathOrStr] = None,
                  out_file: Optional[PathOrStr] = None) -> EditorWindow:
    """Create a window of the application with the editor mounted in it.

    Every way out of the editor — its Close button, its key, the close
    button of the window and the platform close key — goes through the
    editor's own close action, so none of them can drop an unsaved change
    without asking. Closing takes the editor off this window, and the
    window then goes with it.

    Args:
        app: The application, whose window this one belongs to.
        config: Configuration object of the class to edit, holding the
            values to start from when there is no input file.
        title: Title of the window, saying what is being edited.
        in_file: Configuration file to read, or None to edit the values
            that ``config`` holds.
        out_file: Configuration file a save writes, or None to write the
            input file. With neither, the editor asks the user for one.

    Returns:
        The window and the panel that the editor runs in.

    Raises:
        ConfigLoadError: The input file cannot be opened for editing. The
            window is taken away again before this is raised.
    """
    window = tk.Toplevel(app.root)
    window.title(title)
    window.transient(app.root)
    try:
        panel = TkEditorPanel(config, area=window, modal=False,
                              on_close=window.destroy,
                              descriptions=descriptions_for(config),
                              in_file=in_file, out_file=out_file,
                              settings=EDIT_SETTINGS, stderr_file=app.log)
    except EDIT_ERRORS:
        window.destroy()
        raise
    window.protocol('WM_DELETE_WINDOW', panel.close)
    bind_close(window, panel.close)
    return EditorWindow(window=window, panel=panel)


def edit_in_window(app: 'BacklogApp', config: Config, title: str, *,
                   in_file: Optional[PathOrStr] = None,
                   out_file: Optional[PathOrStr] = None) -> EditModel:
    """Show one configuration in a window of its own until it is closed.

    Args:
        app, config, title, in_file, out_file: As of :func:`editor_window`.

    Returns:
        The model of the session that has just ended, which says what it
        saved.

    Raises:
        ConfigLoadError: The input file cannot be opened for editing.
    """
    mounted = editor_window(app, config, title, in_file=in_file,
                            out_file=out_file)
    mounted.window.wait_window()
    return mounted.panel.model


def open_editor_window(app: 'BacklogApp', config: Config, title: str, *,
                       in_file: Optional[PathOrStr] = None,
                       out_file: Optional[PathOrStr] = None
                       ) -> Optional[EditModel]:
    """Run one editing session in a window, or report why it cannot run.

    Args:
        app, config, title, in_file, out_file: As of :func:`editor_window`.

    Returns:
        The model of the session that ran, or None when the configuration
        could not be opened for editing, which is then reported.
    """
    try:
        return edit_in_window(app, config, title, in_file=in_file,
                              out_file=out_file)
    except EDIT_ERRORS as error:
        _report_failure(app, error)
        return None


def edit_config(app: 'BacklogApp') -> None:
    """Edit the configuration in use, or one in a file the user picks.

    A configuration the editor saved becomes the active configuration,
    whichever of the two was edited, because the user has just said that
    those are the values they want. Cancelling any step, and closing the
    editor without saving, leaves everything as it was.
    """
    choice = ask_edit_target(app.root)
    if choice is EditTargetChoice.CANCEL:
        return
    model = (_edit_in_use(app) if choice is EditTargetChoice.IN_USE
             else _edit_config_file(app))
    if model is not None:
        _adopt_saved(app, model)


def edit_preset_file(app: 'BacklogApp') -> None:
    """Edit a stand-alone input or output preset file.

    The direction of the file is detected from its own contents, so the user
    picks a preset file and nothing else. What the editor writes is a file
    and not a configuration of the application, so nothing is adopted.
    """
    path = choose_preset_to_edit(app.root)
    if path is None:
        return
    try:
        config = default_config(io_preset_class(path))
    except EDIT_ERRORS as error:
        _report_failure(app, error)
        return
    model = open_editor_window(app, config, f'Edit preset {Path(path).name}',
                               in_file=path)
    if model is not None:
        _report_saved(app, model, 'Preset saved')


def _edit_in_use(app: 'BacklogApp') -> Optional[EditModel]:
    """Edit the configuration the application uses, in a window.

    A save writes the file the configuration was loaded from, when it came
    from one; a configuration that came from the wizard has no file yet and
    the editor asks for one before it can save.
    """
    config = app.config
    if config is None:
        app.show_error('No configuration', NO_CONFIG_TEXT)
        return None
    out_file = _loaded_file(app)
    return open_editor_window(app, config, _config_title(out_file),
                              out_file=out_file)


def _edit_config_file(app: 'BacklogApp') -> Optional[EditModel]:
    """Edit a configuration file the user picks, in a window."""
    path = choose_config_to_edit(app.root)
    if path is None:
        return None
    return open_editor_window(app, default_config(BacklogOpsConfig),
                              _config_title(path), in_file=path)


def _config_title(name: Optional[str]) -> str:
    """Return the window title, naming the file when the session has one."""
    if name is None:
        return 'Edit configuration'
    return f'Edit configuration {Path(name).name}'


def _loaded_file(app: 'BacklogApp') -> Optional[str]:
    """Return the file the active configuration was loaded from, if any.

    The source of a configuration is either a file name or a phrase saying
    where else it came from, so only a name that is a file now is a
    destination that a save may write.
    """
    source = app.config_source
    if source is None or not Path(source).is_file():
        return None
    return source


def _report_failure(app: 'BacklogApp', error: Exception) -> None:
    """Log and show why a configuration cannot be opened for editing."""
    app.log.write(f'{OPEN_FAIL_TITLE}: {error}\n')
    app.show_error(OPEN_FAIL_TITLE, str(error))


def _adopt_saved(app: 'BacklogApp', model: EditModel) -> None:
    """Make what the editor saved the configuration the application uses."""
    saved = model.saved_config
    if saved is None:
        app.show_info(EDITOR_TITLE, NOT_SAVED_TEXT)
        return
    assert isinstance(saved, BacklogOpsConfig)
    app.adopt_config(saved, str(model.out_file))
    app.show_info('Configuration saved', f'{model.save_message}\n{ADOPTED}')


def _report_saved(app: 'BacklogApp', model: EditModel, title: str) -> None:
    """Report what the editor wrote, or that it wrote nothing."""
    if model.saved_config is None:
        app.show_info(EDITOR_TITLE, NOT_SAVED_TEXT)
        return
    app.show_info(title, model.save_message)
