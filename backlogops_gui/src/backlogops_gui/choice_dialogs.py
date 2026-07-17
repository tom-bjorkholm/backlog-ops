#! /usr/local/bin/python3
"""Modal button-choice dialogs shown outside a backlog window.

These dialogs present a short explanation and a column of buttons, each
selecting one enumerated value, with no OK or Cancel. The no-configuration
dialog offers to run the wizard, load a file, or exit at startup. The
preset-kind dialog asks whether a stand-alone preset file is an input or
an output preset before it is migrated. The source dialog asks whether to
start a wizard from scratch, base it on an existing file, or cancel. All
three are built from the same :class:`ButtonChoiceDialog`.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from enum import Enum
from typing import Generic, Optional, Sequence, TypeVar
from backlogops_gui.close_binding import bind_close

CHOICE_WRAP = 360
NO_CONFIG_TEXT = (
    'The application cannot run without a configuration. Choose to run '
    'the configuration wizard, load an existing configuration file, or '
    'exit the application.')
PRESET_KIND_TEXT = (
    'Is the preset file an input format preset or an output format '
    'preset? The kind decides how the file is migrated.')
_Choice = TypeVar('_Choice')


class ConfigChoice(Enum):
    """The action chosen in the no-configuration startup dialog."""

    WIZARD = 'wizard'
    LOAD = 'load'
    EXIT = 'exit'


class PresetKind(Enum):
    """Whether a stand-alone preset file is an input or output preset."""

    INPUT = 'input'
    OUTPUT = 'output'


class SourceChoice(Enum):
    """Whether a wizard starts empty, from a file, or is cancelled."""

    SCRATCH = 'scratch'
    FROM_FILE = 'from_file'
    CANCEL = 'cancel'


# pylint: disable-next=too-few-public-methods
class ButtonChoiceDialog(Generic[_Choice]):
    """Modal dialog presenting a column of single-choice buttons.

    Each option is one button that records its value and closes the
    dialog. Closing the window without pressing a button keeps the given
    default value, so a caller can tell a real choice from a dismissal.
    """

    def __init__(self, parent: tk.Misc, title: str, text: str,
                 options: Sequence[tuple[str, _Choice]],
                 default: _Choice) -> None:
        """Build, show and wait for the button-choice dialog."""
        self.choice: _Choice = default
        self._win = tk.Toplevel(parent)
        self._win.title(title)
        if isinstance(parent, tk.Wm):
            self._win.transient(parent)
        self._win.protocol('WM_DELETE_WINDOW', self._win.destroy)
        bind_close(self._win)
        self._build(text, options)
        self._show()

    def _build(self, text: str,
               options: Sequence[tuple[str, _Choice]]) -> None:
        """Add the explanation and one button per option."""
        tk.Label(self._win, text=text, justify='left',
                 wraplength=CHOICE_WRAP).pack(anchor='w', padx=12,
                                              pady=(12, 6))
        for label, value in options:
            self._add_button(label, value)

    def _add_button(self, text: str, value: _Choice) -> None:
        """Add one button that selects the given value."""
        button = tk.Button(self._win, text=text,
                           command=lambda: self._choose(value))
        button.pack(fill='x', padx=12, pady=4)

    def _show(self) -> None:
        """Grab the focus and wait for the dialog to close."""
        self._win.grab_set()
        self._win.wait_window()

    def _choose(self, value: _Choice) -> None:
        """Record the chosen value and close the dialog."""
        self.choice = value
        self._win.destroy()


def ask_no_config_choice(parent: tk.Misc) -> ConfigChoice:
    """Ask whether to run the wizard, load a file, or exit."""
    options = [('Run the configuration wizard', ConfigChoice.WIZARD),
               ('Load configuration from a file…', ConfigChoice.LOAD),
               ('Exit the application', ConfigChoice.EXIT)]
    return ButtonChoiceDialog(parent, 'No configuration', NO_CONFIG_TEXT,
                              options, ConfigChoice.EXIT).choice


def ask_preset_kind(parent: tk.Misc) -> Optional[PresetKind]:
    """Ask whether a preset file is an input or output preset.

    Returns the chosen kind, or None when the dialog is closed without a
    choice.
    """
    options: list[tuple[str, Optional[PresetKind]]] = [
        ('Input format preset', PresetKind.INPUT),
        ('Output format preset', PresetKind.OUTPUT)]
    return ButtonChoiceDialog(parent, 'Preset kind', PRESET_KIND_TEXT, options,
                              None).choice


def ask_source_choice(parent: tk.Misc, title: str, text: str) -> SourceChoice:
    """Ask whether to start from scratch, base on a file, or cancel."""
    options = [('Start from scratch', SourceChoice.SCRATCH),
               ('Base it on an existing file…', SourceChoice.FROM_FILE),
               ('Cancel', SourceChoice.CANCEL)]
    return ButtonChoiceDialog(parent, title, text, options,
                              SourceChoice.CANCEL).choice
