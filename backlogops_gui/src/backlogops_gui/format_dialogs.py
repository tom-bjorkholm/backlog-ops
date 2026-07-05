#! /usr/local/bin/python3
"""File-format option dialogs for reading and writing backlog files.

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
from backlogops_gui.gui_style import style_input
from backlogops_gui.modal_dialog import ModalDialog

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


# pylint: disable-next=too-few-public-methods,too-many-instance-attributes
class FormatDialog(ModalDialog):
    """Modal dialog collecting the format selection for one file."""

    def __init__(self, parent: tk.Misc, presets: Sequence[str],
                 with_releases_first: bool) -> None:
        """Build, show and wait for the modal format dialog."""
        super().__init__(parent, 'File format')
        self.value: Optional[str] = None
        self.releases_first = False
        self._presets = presets
        self._mode = tk.IntVar(self._win, MODE_INFER)
        self._preset = tk.StringVar(self._win)
        self._path = tk.StringVar(self._win)
        self._rel_first = tk.BooleanVar(self._win, False)
        self._build(with_releases_first)
        self._show()

    def _build(self, with_releases_first: bool) -> None:
        """Create the radio buttons, inputs and action buttons."""
        self._add_radio('Infer format from file name', MODE_INFER)
        self._add_preset_row()
        self._add_file_row()
        if with_releases_first:
            check = tk.Checkbutton(self._win, variable=self._rel_first,
                                   text='Write releases before backlog')
            check.pack(anchor='w', padx=12, pady=4)

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
        style_input(box)
        box.pack(anchor='w', padx=36, pady=2)

    def _add_file_row(self) -> None:
        """Add the configuration-file radio button, entry and browse."""
        self._add_radio('Read format from a configuration file:', MODE_FILE)
        row = tk.Frame(self._win)
        row.pack(anchor='w', padx=36, pady=2, fill='x')
        entry = tk.Entry(row, textvariable=self._path, width=30)
        style_input(entry)
        entry.pack(side='left')
        tk.Button(row, text='Browse', command=self._browse).pack(side='left',
                                                                 padx=6)

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
        super()._confirm()

    def _selected_value(self) -> Optional[str]:
        """Return the format value for the selected mode."""
        return format_value(self._mode.get(), self._preset.get(),
                            self._path.get())


def ask_read_options(parent: tk.Misc, presets: Optional[Sequence[str]]
                     ) -> Optional[ReadOptions]:
    """Ask how to read a file, or None when the dialog is cancelled."""
    dialog = FormatDialog(parent, presets or [], False)
    if dialog.cancelled:
        return None
    return ReadOptions(config_value=dialog.value)


def ask_write_options(parent: tk.Misc, presets: Optional[Sequence[str]]
                      ) -> Optional[WriteOptions]:
    """Ask how to write a file, or None when the dialog is cancelled."""
    dialog = FormatDialog(parent, presets or [], True)
    if dialog.cancelled:
        return None
    return WriteOptions(config_value=dialog.value,
                        releases_first=dialog.releases_first)
