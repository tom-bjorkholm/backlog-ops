#! /usr/local/bin/python3
"""Modal button-choice dialogs shown outside a backlog window.

These dialogs present a short explanation and a column of buttons, each
selecting one enumerated value, with no OK or Cancel. The no-configuration
dialog offers to run the wizard, load a file, or exit at startup. The
preset-kind dialog asks whether a stand-alone preset file is an input or
an output preset before it is migrated.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from enum import Enum
from typing import Optional
from backlogops_gui.close_binding import bind_close

NO_CONFIG_WRAP = 360
NO_CONFIG_TEXT = (
    'The application cannot run without a configuration. Choose to run '
    'the configuration wizard, load an existing configuration file, or '
    'exit the application.')
PRESET_KIND_TEXT = (
    'Is the preset file an input format preset or an output format '
    'preset? The kind decides how the file is migrated.')


class ConfigChoice(Enum):
    """The action chosen in the no-configuration startup dialog."""

    WIZARD = 'wizard'
    LOAD = 'load'
    EXIT = 'exit'


class PresetKind(Enum):
    """Whether a stand-alone preset file is an input or output preset."""

    INPUT = 'input'
    OUTPUT = 'output'


# pylint: disable-next=too-few-public-methods
class NoConfigDialog:
    """Modal dialog offering to create, load, or exit without a config."""

    def __init__(self, parent: tk.Misc) -> None:
        """Build, show and wait for the no-configuration dialog."""
        self.choice = ConfigChoice.EXIT
        self._win = tk.Toplevel(parent)
        self._win.title('No configuration')
        if isinstance(parent, tk.Wm):
            self._win.transient(parent)
        self._win.protocol('WM_DELETE_WINDOW', self._win.destroy)
        bind_close(self._win)
        self._build()
        self._show()

    def _build(self) -> None:
        """Add the explanation and the three action buttons."""
        tk.Label(self._win, text=NO_CONFIG_TEXT, justify='left',
                 wraplength=NO_CONFIG_WRAP).pack(anchor='w', padx=12,
                                                 pady=(12, 6))
        self._add_button('Run the configuration wizard', ConfigChoice.WIZARD)
        load_choice = ConfigChoice.LOAD
        self._add_button('Load configuration from a file…', load_choice)
        self._add_button('Exit the application', ConfigChoice.EXIT)

    def _add_button(self, text: str, choice: ConfigChoice) -> None:
        """Add one action button that selects the given choice."""
        button = tk.Button(self._win, text=text,
                           command=lambda: self._choose(choice))
        button.pack(fill='x', padx=12, pady=4)

    def _show(self) -> None:
        """Grab the focus and wait for the dialog to close."""
        self._win.grab_set()
        self._win.wait_window()

    def _choose(self, choice: ConfigChoice) -> None:
        """Record the chosen action and close the dialog."""
        self.choice = choice
        self._win.destroy()


def ask_no_config_choice(parent: tk.Misc) -> ConfigChoice:
    """Ask whether to run the wizard, load a file, or exit."""
    return NoConfigDialog(parent).choice


# pylint: disable-next=too-few-public-methods
class PresetKindDialog:
    """Modal dialog asking whether a preset is for input or output."""

    def __init__(self, parent: tk.Misc) -> None:
        """Build, show and wait for the preset kind dialog."""
        self.kind: Optional[PresetKind] = None
        self._win = tk.Toplevel(parent)
        self._win.title('Preset kind')
        if isinstance(parent, tk.Wm):
            self._win.transient(parent)
        self._win.protocol('WM_DELETE_WINDOW', self._win.destroy)
        bind_close(self._win)
        self._build()
        self._show()

    def _build(self) -> None:
        """Add the explanation and the two kind buttons."""
        tk.Label(self._win, text=PRESET_KIND_TEXT, justify='left',
                 wraplength=NO_CONFIG_WRAP).pack(anchor='w', padx=12,
                                                 pady=(12, 6))
        self._add_button('Input format preset', PresetKind.INPUT)
        self._add_button('Output format preset', PresetKind.OUTPUT)

    def _add_button(self, text: str, kind: PresetKind) -> None:
        """Add one button that selects the given preset kind."""
        button = tk.Button(self._win, text=text,
                           command=lambda: self._choose(kind))
        button.pack(fill='x', padx=12, pady=4)

    def _show(self) -> None:
        """Grab the focus and wait for the dialog to close."""
        self._win.grab_set()
        self._win.wait_window()

    def _choose(self, kind: PresetKind) -> None:
        """Record the chosen kind and close the dialog."""
        self.kind = kind
        self._win.destroy()


def ask_preset_kind(parent: tk.Misc) -> Optional[PresetKind]:
    """Ask whether a preset file is an input or output preset.

    Returns the chosen kind, or None when the dialog is closed without a
    choice.
    """
    return PresetKindDialog(parent).kind
