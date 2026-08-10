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
model belongs to the session and everything else is the application's.

The editor is mounted in a :class:`tkinter.Toplevel` this module creates,
rather than started through ``edit_cfg_json_tk.edit``. That entry point
creates a ``tkinter.Tk`` and an event loop of its own, which is for an
application that runs neither yet: a second Tcl interpreter shares nothing
with the first, and a nested loop would not end when the editor window
closed, because Tcl runs its loop while any window of the process lives.
``EditorWidgets`` is what the library offers for a window an application
owns, and it takes the close action as an argument so that the editor never
destroys a window it did not create.

The window is not made modal. The editor opens dialogs of its own — a file
chooser for Save as…, a question before it overwrites a file, and one asking
for the key of a new entry — and a grab held by the editor window would keep
their clicks and keys from reaching them.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from pathlib import Path
from typing import Callable, NamedTuple, Optional, TYPE_CHECKING
from edit_cfg_json import EditModel
from edit_cfg_json_tk.tk_editor import EditorWidgets
from wizard_tk_bridge.close_binding import bind_close
from backlogops import (
    BacklogOpsConfig, default_edit_config, edit_model_for, io_preset_class)
from backlogops_gui.choice_dialogs import EditTargetChoice, ask_edit_target
from backlogops_gui.file_choosers import (
    choose_config_to_edit, choose_preset_to_edit)

if TYPE_CHECKING:
    from backlogops_gui.application import BacklogApp

EDIT_ERRORS = (ValueError, TypeError, KeyError, OSError)
"""Errors raised when a configuration cannot be opened for editing."""

OPEN_FAIL_TITLE = 'Could not open the configuration'
NO_CONFIG_TEXT = 'There is no configuration to edit.'
NOT_SAVED_TEXT = 'The editor was closed without saving anything.'
EDITOR_TITLE = 'Configuration editor'
ADOPTED = 'The saved configuration is now the one in use.'


class EditorWindow(NamedTuple):
    """One editor window and the widgets that have to be kept with it.

    The widgets are carried beside the window because a ``StringVar`` unsets
    its Tcl variable when it is collected, and the field it belongs to would
    then lose both its text and the callback that writes into the model.
    """

    window: tk.Toplevel
    widgets: EditorWidgets


def editor_window(parent: tk.Misc, model: EditModel,
                  title: str) -> EditorWindow:
    """Create a window of the application with the editor mounted in it.

    Every way out of the editor — its Close button, its key, the close
    button of the window and the platform close key — goes through the
    editor's own close action, so none of them can drop an unsaved change
    without asking. Closing destroys this window and nothing else.

    Args:
        parent: Widget the window belongs to, which is the main window.
        model: Model of the editing session to show.
        title: Title of the window, saying what is being edited.

    Returns:
        The window and the widgets mounted in it.
    """
    window = tk.Toplevel(parent)
    window.title(title)
    if isinstance(parent, tk.Wm):
        window.transient(parent)
    widgets = EditorWidgets(parent=window, model=model,
                            on_close=window.destroy)
    window.protocol('WM_DELETE_WINDOW', widgets.close_editor)
    bind_close(window, widgets.close_editor)
    return EditorWindow(window=window, widgets=widgets)


def open_editor_window(parent: tk.Misc, model: EditModel, title: str) -> None:
    """Show one edit model in a window of its own until it is closed.

    The window and its widgets are held by the local name for as long as
    this call waits for the window, which is as long as they are needed.

    Args:
        parent: Widget the window belongs to, which is the main window.
        model: Model of the editing session to show.
        title: Title of the window, saying what is being edited.
    """
    mounted = editor_window(parent, model, title)
    mounted.window.wait_window()


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
    model = (_in_use_model(app) if choice is EditTargetChoice.IN_USE
             else _config_file_model(app))
    if model is None:
        return
    open_editor_window(app.root, model, _config_title(model))
    _adopt_saved(app, model)


def _config_title(model: EditModel) -> str:
    """Return the window title, naming the file when a save has one."""
    if model.out_file is None:
        return 'Edit configuration'
    return f'Edit configuration {Path(model.out_file).name}'


def edit_preset_file(app: 'BacklogApp') -> None:
    """Edit a stand-alone input or output preset file.

    The direction of the file is detected from its own contents, so the user
    picks a preset file and nothing else. What the editor writes is a file
    and not a configuration of the application, so nothing is adopted.
    """
    path = choose_preset_to_edit(app.root)
    if path is None:
        return
    model = _built(app, lambda: edit_model_for(
        default_edit_config(io_preset_class(path)), in_file=path,
        stderr_file=app.log))
    if model is None:
        return
    open_editor_window(app.root, model, f'Edit preset {Path(path).name}')
    _report_saved(app, model, 'Preset saved')


def _in_use_model(app: 'BacklogApp') -> Optional[EditModel]:
    """Return the model editing the configuration the application uses.

    A save writes the file the configuration was loaded from, when it came
    from one; a configuration that came from the wizard has no file yet and
    the editor asks for one before it can save.
    """
    config = app.config
    if config is None:
        app.show_error('No configuration', NO_CONFIG_TEXT)
        return None
    return _built(app, lambda: edit_model_for(config,
                                              out_file=_loaded_file(app),
                                              stderr_file=app.log))


def _config_file_model(app: 'BacklogApp') -> Optional[EditModel]:
    """Return the model editing a configuration file the user picks."""
    path = choose_config_to_edit(app.root)
    if path is None:
        return None
    return _built(app, lambda: edit_model_for(
        default_edit_config(BacklogOpsConfig), in_file=path,
        stderr_file=app.log))


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


def _built(app: 'BacklogApp',
           build: Callable[[], EditModel]) -> Optional[EditModel]:
    """Return the model that ``build`` makes, reporting a refusal."""
    try:
        return build()
    except EDIT_ERRORS as error:
        app.log.write(f'{OPEN_FAIL_TITLE}: {error}\n')
        app.show_error(OPEN_FAIL_TITLE, str(error))
        return None


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
