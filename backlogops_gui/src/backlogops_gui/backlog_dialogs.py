#! /usr/local/bin/python3
"""Modal dialogs collecting options for the backlog operations.

These dialogs gather the options for the actions offered by a backlog
window: the leading keys for a reordering, the order-by-dependencies
options, the start date for a ready-date estimate, the levels to extract
keys at, the buffer in calendar days, and the two release-ordering
choices. Each dialog stores its result and the matching ``ask_`` wrapper
returns it, or None when the dialog is cancelled.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dataclasses import dataclass
from datetime import date
from typing import Optional, TextIO
from backlogops import DependencyMode, DEFAULT_LEVELS, read_key_list
from backlogops_gui.gui_style import style_input
from backlogops_gui.modal_dialog import ModalDialog

KEY_READ_ERRORS = (ValueError, TypeError, KeyError, OSError)
DEFAULT_BUFFER_DAYS = 5


@dataclass
class DepOptions:
    """The options selected for ordering a backlog by dependencies."""

    later: bool
    mode: DependencyMode
    space_around: Optional[list[str]]


@dataclass
class ReleaseOrderOptions:
    """The options selected for ordering a backlog by release order."""

    honor_dependencies: bool
    later: bool


@dataclass
class StartChoice:
    """The start date selected for estimating ready dates."""

    start_date: Optional[date]


# pylint: disable-next=too-few-public-methods
class KeysDialog(ModalDialog):
    """Modal dialog collecting the leading keys for a reordering."""

    def __init__(self, parent: tk.Misc, sink: TextIO) -> None:
        """Build, show and wait for the key entry dialog."""
        super().__init__(parent, 'Order by keys')
        self.keys: Optional[list[str]] = None
        self._sink = sink
        self._text = self._build_text()
        self._show()

    def _build_text(self) -> tk.Text:
        """Add the entry label, text box and the load-from-file button."""
        tk.Label(self._win, text='Enter keys separated by spaces or '
                 'newlines:').pack(anchor='w', padx=12, pady=(10, 2))
        text = tk.Text(self._win, width=40, height=8)
        style_input(text)
        text.pack(padx=12, pady=2)
        tk.Button(self._win, text='Load from file…',
                  command=self._load).pack(anchor='w', padx=12, pady=4)
        return text

    def _load(self) -> None:
        """Read a key list file into the text box, reporting failures."""
        name = filedialog.askopenfilename(parent=self._win,
                                          title='Read key list')
        if not name:
            return
        try:
            keys = read_key_list(name, stderr_file=self._sink)
        except KEY_READ_ERRORS as error:
            messagebox.showerror('Could not read key list', str(error),
                                 parent=self._win)
            return
        self._text.delete('1.0', 'end')
        self._text.insert('end', '\n'.join(keys))

    def _confirm(self) -> None:
        """Split the text on whitespace and close the dialog."""
        self.keys = self._text.get('1.0', 'end').split()
        super()._confirm()


# pylint: disable-next=too-few-public-methods
class DepOptionsDialog(ModalDialog):
    """Modal dialog collecting the order-by-dependencies options."""

    def __init__(self, parent: tk.Misc) -> None:
        """Build, show and wait for the dependency options dialog."""
        super().__init__(parent, 'Order by dependencies')
        self.options: Optional[DepOptions] = None
        self._later = tk.BooleanVar(self._win, False)
        self._mode = tk.StringVar(self._win, DependencyMode.KEEP.name)
        self._space = tk.StringVar(self._win)
        self._build()
        self._show()

    def _build(self) -> None:
        """Add the later check box, the mode chooser and the key entry."""
        tk.Checkbutton(self._win, variable=self._later,
                       text='Push dependent items later instead of pulling '
                       'prerequisites earlier').pack(anchor='w', padx=12,
                                                     pady=(10, 2))
        self._build_mode()
        self._build_space()

    def _build_mode(self) -> None:
        """Add the placement-mode label and chooser."""
        tk.Label(self._win, text='Placement of dependency items:'
                 ).pack(anchor='w', padx=12, pady=(6, 2))
        names = [mode.name for mode in DependencyMode]
        box = ttk.Combobox(self._win, textvariable=self._mode, values=names,
                           state='readonly')
        style_input(box)
        box.pack(anchor='w', padx=12)

    def _build_space(self) -> None:
        """Add the space-around label and key entry."""
        tk.Label(self._win, text='Keys to keep far from dependencies '
                 '(optional, space separated):').pack(anchor='w', padx=12,
                                                      pady=(6, 2))
        entry = tk.Entry(self._win, textvariable=self._space, width=40)
        style_input(entry)
        entry.pack(anchor='w', padx=12)

    def _confirm(self) -> None:
        """Store the selected options and close the dialog."""
        space = self._space.get().split()
        self.options = DepOptions(later=self._later.get(),
                                  mode=DependencyMode[self._mode.get()],
                                  space_around=space or None)
        super()._confirm()


# pylint: disable-next=too-few-public-methods
class StartDateDialog(ModalDialog):
    """Modal dialog collecting the start date for the estimate."""

    def __init__(self, parent: tk.Misc) -> None:
        """Build, show and wait for the start date dialog."""
        super().__init__(parent, 'Estimate ready date')
        self.choice: Optional[StartChoice] = None
        self._date = tk.StringVar(self._win, date.today().isoformat())
        self._build()
        self._show()

    def _build(self) -> None:
        """Add the start date label and entry."""
        tk.Label(self._win, text='Start date (ISO, empty for today):'
                 ).pack(anchor='w', padx=12, pady=(10, 2))
        entry = tk.Entry(self._win, textvariable=self._date, width=20)
        style_input(entry)
        entry.pack(anchor='w', padx=12)

    def _confirm(self) -> None:
        """Parse the date, keeping the dialog open on a bad value."""
        text = self._date.get().strip()
        if text == '':
            self.choice = StartChoice(start_date=None)
            super()._confirm()
            return
        try:
            self.choice = StartChoice(start_date=date.fromisoformat(text))
        except ValueError as error:
            messagebox.showerror('Invalid date', str(error), parent=self._win)
            return
        super()._confirm()


# pylint: disable-next=too-few-public-methods
class LevelsDialog(ModalDialog):
    """Modal dialog selecting the levels to extract keys at."""

    def __init__(self, parent: tk.Misc) -> None:
        """Build, show and wait for the level selection dialog."""
        super().__init__(parent, 'Extract keys')
        self.levels: Optional[list[int]] = None
        self._chosen = self._build()
        self._show()

    def _build(self) -> dict[int, tk.BooleanVar]:
        """Add a check box for each default level and return its variables."""
        tk.Label(self._win, text='Select levels to extract keys at:'
                 ).pack(anchor='w', padx=12, pady=(10, 2))
        chosen: dict[int, tk.BooleanVar] = {}
        for number in sorted(DEFAULT_LEVELS):
            var = tk.BooleanVar(self._win, False)
            chosen[number] = var
            tk.Checkbutton(self._win, variable=var,
                           text=DEFAULT_LEVELS[number].name).pack(anchor='w',
                                                                  padx=24)
        return chosen

    def _confirm(self) -> None:
        """Store the chosen levels, requiring at least one selection."""
        selected = [n for n, var in self._chosen.items() if var.get()]
        if not selected:
            messagebox.showerror('No levels', 'Select at least one level.',
                                 parent=self._win)
            return
        self.levels = selected
        super()._confirm()


# pylint: disable-next=too-few-public-methods
class DateOrderDialog(ModalDialog):
    """Modal dialog choosing planned or estimated date for ordering."""

    def __init__(self, parent: tk.Misc) -> None:
        """Build, show and wait for the date order dialog."""
        super().__init__(parent, 'Order releases by date')
        self.by_estimated = False
        self._estimated = tk.BooleanVar(self._win, False)
        self._build()
        self._show()

    def _build(self) -> None:
        """Add the estimated-date check box, off for the planned date."""
        tk.Checkbutton(self._win, variable=self._estimated,
                       text='Order by estimated date instead of planned '
                       'date').pack(anchor='w', padx=12, pady=(10, 2))

    def _confirm(self) -> None:
        """Store the chosen date kind and close the dialog."""
        self.by_estimated = self._estimated.get()
        super()._confirm()


# pylint: disable-next=too-few-public-methods
class ReleaseOrderDialog(ModalDialog):
    """Modal dialog choosing options for ordering by release order."""

    def __init__(self, parent: tk.Misc) -> None:
        """Build, show and wait for the release-order dialog."""
        super().__init__(parent, 'Order by release order')
        self.options: Optional[ReleaseOrderOptions] = None
        self._honor = tk.BooleanVar(self._win, False)
        self._later = tk.BooleanVar(self._win, False)
        self._build()
        self._show()

    def _build(self) -> None:
        """Add the honor-dependencies and direction check boxes."""
        tk.Checkbutton(self._win, variable=self._honor,
                       text='Honor dependencies').pack(anchor='w', padx=12,
                                                       pady=(10, 2))
        tk.Checkbutton(self._win, variable=self._later,
                       text='Push dependent items later instead of pulling '
                       'prerequisites earlier').pack(anchor='w', padx=12,
                                                     pady=(0, 2))

    def _confirm(self) -> None:
        """Store the chosen release-order options and close."""
        self.options = ReleaseOrderOptions(
            honor_dependencies=self._honor.get(), later=self._later.get())
        super()._confirm()


# pylint: disable-next=too-few-public-methods
class BufferDialog(ModalDialog):
    """Modal dialog collecting the buffer in calendar days."""

    def __init__(self, parent: tk.Misc) -> None:
        """Build, show and wait for the buffer days dialog."""
        super().__init__(parent, 'Buffer days')
        self.days: Optional[int] = None
        self._text = tk.StringVar(self._win, str(DEFAULT_BUFFER_DAYS))
        self._build()
        self._show()

    def _build(self) -> None:
        """Add the buffer label and entry prefilled with the default."""
        tk.Label(self._win, text='Buffer in calendar days (0 or more):'
                 ).pack(anchor='w', padx=12, pady=(10, 2))
        entry = tk.Entry(self._win, textvariable=self._text, width=10)
        style_input(entry)
        entry.pack(anchor='w', padx=12)

    def _confirm(self) -> None:
        """Parse the buffer, keeping the dialog open on a bad value."""
        try:
            days = int(self._text.get().strip())
        except ValueError:
            messagebox.showerror('Invalid number',
                                 'Enter a whole number of days.',
                                 parent=self._win)
            return
        if days < 0:
            messagebox.showerror('Invalid number',
                                 'The buffer must not be negative.',
                                 parent=self._win)
            return
        self.days = days
        super()._confirm()


def ask_keys(parent: tk.Misc, sink: TextIO) -> Optional[list[str]]:
    """Ask for the leading keys, or None when the dialog is cancelled."""
    dialog = KeysDialog(parent, sink)
    if dialog.cancelled:
        return None
    return dialog.keys


def ask_dep_options(parent: tk.Misc) -> Optional[DepOptions]:
    """Ask for the dependency options, or None when cancelled."""
    dialog = DepOptionsDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.options


def ask_start_date(parent: tk.Misc) -> Optional[StartChoice]:
    """Ask for the start date, or None when the dialog is cancelled."""
    dialog = StartDateDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.choice


def ask_levels(parent: tk.Misc) -> Optional[list[int]]:
    """Ask for the levels to extract, or None when cancelled."""
    dialog = LevelsDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.levels


def ask_date_order(parent: tk.Misc) -> Optional[bool]:
    """Ask whether to order by estimated date, or None when cancelled."""
    dialog = DateOrderDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.by_estimated


def ask_release_order(parent: tk.Misc) -> Optional[ReleaseOrderOptions]:
    """Ask for the release-order options, or None when cancelled."""
    dialog = ReleaseOrderDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.options


def ask_buffer_days(parent: tk.Misc) -> Optional[int]:
    """Ask for the buffer in days, or None when the dialog is cancelled."""
    dialog = BufferDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.days
