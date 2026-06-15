#! /usr/local/bin/python3
"""File choosers and format-option dialogs for backlog files.

The format options mirror the command line: the format is either inferred
from the file name, taken from a named preset stored in the teams
configuration, or read from a stand-alone configuration file. Writing also
offers to put the releases before the backlog. The chosen format is
returned as a single value understood by the resolver in
:mod:`backlogops_gui.backlog_io`.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import filedialog, ttk
from dataclasses import dataclass
from typing import Optional, Sequence

MODE_INFER = 0
MODE_PRESET = 1
MODE_FILE = 2


def format_value(mode: int, preset: str, path: str) -> Optional[str]:
    """Return the resolver value for a selected mode and inputs.

    A preset or file mode with an empty input falls back to inference, so
    an unfinished selection behaves like inferring from the file name.
    """
    if mode == MODE_PRESET:
        return preset or None
    if mode == MODE_FILE:
        return path or None
    return None


@dataclass
class ReadOptions:
    """The format selection entered for reading a file."""

    config_value: Optional[str]


@dataclass
class WriteOptions:
    """The format selection and ordering entered for writing a file."""

    config_value: Optional[str]
    releases_first: bool


def choose_input_file(parent: tk.Misc) -> Optional[str]:
    """Ask for an existing backlog file, or None when cancelled."""
    name = filedialog.askopenfilename(parent=parent, title='Read backlog')
    return name or None


def choose_output_file(parent: tk.Misc) -> Optional[str]:
    """Ask for a backlog file to create, or None when cancelled."""
    name = filedialog.asksaveasfilename(parent=parent, title='Save backlog')
    return name or None


def choose_config_file(parent: tk.Misc) -> Optional[str]:
    """Ask for a configuration file to create, or None when cancelled."""
    name = filedialog.asksaveasfilename(parent=parent,
                                        title='Write configuration')
    return name or None


# pylint: disable-next=too-few-public-methods
class _FormatDialog:  # pylint: disable=too-many-instance-attributes
    """Modal dialog collecting the format selection for one file."""

    def __init__(self, parent: tk.Misc, presets: Sequence[str],
                 with_releases_first: bool) -> None:
        """Build, show and wait for the modal format dialog."""
        self.cancelled = False
        self.value: Optional[str] = None
        self.releases_first = False
        self._presets = presets
        self._win = tk.Toplevel(parent)
        self._win.title('File format')
        if isinstance(parent, tk.Wm):
            self._win.transient(parent)
        self._win.protocol('WM_DELETE_WINDOW', self._cancel)
        self._mode = tk.IntVar(self._win, MODE_INFER)
        self._preset = tk.StringVar(self._win)
        self._path = tk.StringVar(self._win)
        self._rel_first = tk.BooleanVar(self._win, False)
        self._build(with_releases_first)
        self._win.grab_set()
        self._win.wait_window()

    def _build(self, with_releases_first: bool) -> None:
        """Create the radio buttons, inputs and action buttons."""
        self._add_radio('Infer format from file name', MODE_INFER)
        self._add_preset_row()
        self._add_file_row()
        if with_releases_first:
            check = tk.Checkbutton(self._win, variable=self._rel_first,
                                   text='Write releases before backlog')
            check.pack(anchor='w', padx=12, pady=4)
        self._add_buttons()

    def _add_radio(self, text: str, mode: int) -> None:
        """Add one mode radio button."""
        tk.Radiobutton(self._win, text=text, variable=self._mode,
                       value=mode).pack(anchor='w', padx=12, pady=2)

    def _add_preset_row(self) -> None:
        """Add the preset radio button and its choices, when available."""
        if not self._presets:
            return
        self._add_radio('Use a named preset:', MODE_PRESET)
        box = ttk.Combobox(self._win, textvariable=self._preset,
                           values=list(self._presets), state='readonly')
        box.pack(anchor='w', padx=36, pady=2)

    def _add_file_row(self) -> None:
        """Add the configuration-file radio button, entry and browse."""
        self._add_radio('Read format from a configuration file:', MODE_FILE)
        row = tk.Frame(self._win)
        row.pack(anchor='w', padx=36, pady=2, fill='x')
        tk.Entry(row, textvariable=self._path, width=30).pack(side='left')
        tk.Button(row, text='Browse', command=self._browse).pack(side='left',
                                                                 padx=6)

    def _add_buttons(self) -> None:
        """Add the confirm and cancel buttons."""
        button_bar = tk.Frame(self._win)
        button_bar.pack(padx=12, pady=10, fill='x')
        ok_button = tk.Button(button_bar, text='OK', command=self._confirm)
        ok_button.pack(side='left')
        cancel_button = tk.Button(button_bar, text='Cancel',
                                  command=self._cancel)
        cancel_button.pack(side='right')

    def _browse(self) -> None:
        """Pick a configuration file and select the file mode."""
        name = filedialog.askopenfilename(parent=self._win,
                                          title='Format configuration')
        if name:
            self._path.set(name)
            self._mode.set(MODE_FILE)

    def _confirm(self) -> None:
        """Store the selected format value and close the dialog."""
        self.value = self._selected_value()
        self.releases_first = self._rel_first.get()
        self._win.destroy()

    def _selected_value(self) -> Optional[str]:
        """Return the format value for the selected mode."""
        return format_value(self._mode.get(), self._preset.get(),
                            self._path.get())

    def _cancel(self) -> None:
        """Mark the dialog cancelled and close it."""
        self.cancelled = True
        self._win.destroy()


def ask_read_options(parent: tk.Misc, presets: Optional[Sequence[str]]
                     ) -> Optional[ReadOptions]:
    """Ask how to read a file, or None when the dialog is cancelled."""
    dialog = _FormatDialog(parent, presets or [], False)
    if dialog.cancelled:
        return None
    return ReadOptions(config_value=dialog.value)


def ask_write_options(parent: tk.Misc, presets: Optional[Sequence[str]]
                      ) -> Optional[WriteOptions]:
    """Ask how to write a file, or None when the dialog is cancelled."""
    dialog = _FormatDialog(parent, presets or [], True)
    if dialog.cancelled:
        return None
    return WriteOptions(config_value=dialog.value,
                        releases_first=dialog.releases_first)
