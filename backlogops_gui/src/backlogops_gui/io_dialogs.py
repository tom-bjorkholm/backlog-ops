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
from tkinter import filedialog, messagebox, ttk
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Callable, Optional, Sequence, TextIO
from backlogops import DependencyMode, DEFAULT_LEVELS, read_key_list

MODE_INFER = 0
MODE_PRESET = 1
MODE_FILE = 2
KEY_READ_ERRORS = (ValueError, TypeError, KeyError, OSError)
DEFAULT_BUFFER_DAYS = 5
NO_CONFIG_WRAP = 360
NO_CONFIG_TEXT = (
    'The application cannot run without a configuration. Choose to run '
    'the configuration wizard, load an existing configuration file, or '
    'exit the application.')


class ConfigChoice(Enum):
    """The action chosen in the no-configuration startup dialog."""

    WIZARD = 'wizard'
    LOAD = 'load'
    EXIT = 'exit'


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


def choose_existing_config(parent: tk.Misc) -> Optional[str]:
    """Ask for an existing configuration file, or None when cancelled."""
    name = filedialog.askopenfilename(parent=parent,
                                      title='Load configuration')
    return name or None


# pylint: disable-next=too-few-public-methods
class _NoConfigDialog:
    """Modal dialog offering to create, load, or exit without a config."""

    def __init__(self, parent: tk.Misc) -> None:
        """Build, show and wait for the no-configuration dialog."""
        self.choice = ConfigChoice.EXIT
        self._win = tk.Toplevel(parent)
        self._win.title('No configuration')
        if isinstance(parent, tk.Wm):
            self._win.transient(parent)
        self._win.protocol('WM_DELETE_WINDOW', self._win.destroy)
        self._build()
        self._show()

    def _build(self) -> None:
        """Add the explanation and the three action buttons."""
        tk.Label(self._win, text=NO_CONFIG_TEXT, justify='left',
                 wraplength=NO_CONFIG_WRAP).pack(anchor='w', padx=12,
                                                 pady=(12, 6))
        self._add_button('Run the configuration wizard', ConfigChoice.WIZARD)
        self._add_button('Load configuration from a file…', ConfigChoice.LOAD)
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
    return _NoConfigDialog(parent).choice


# pylint: disable-next=too-few-public-methods
class _ModalDialog:
    """Base for small modal dialogs with OK and Cancel buttons."""

    def __init__(self, parent: tk.Misc, title: str) -> None:
        """Create the modal top-level window and its close handler."""
        self.cancelled = False
        self._win = tk.Toplevel(parent)
        self._win.title(title)
        if isinstance(parent, tk.Wm):
            self._win.transient(parent)
        self._win.protocol('WM_DELETE_WINDOW', self._cancel)

    def _show(self) -> None:
        """Add the buttons, grab the focus and wait for the close."""
        self._add_buttons()
        self._win.grab_set()
        self._win.wait_window()

    def _add_buttons(self) -> None:
        """Add the confirm and cancel buttons."""
        button_bar = tk.Frame(self._win)
        button_bar.pack(padx=12, pady=10, fill='x')
        tk.Button(button_bar, text='OK',
                  command=self._confirm).pack(side='left')
        tk.Button(button_bar, text='Cancel',
                  command=self._cancel).pack(side='right')

    def _confirm(self) -> None:
        """Close the dialog; subclasses override to store their values."""
        self._win.destroy()

    def _cancel(self) -> None:
        """Mark the dialog cancelled and close it."""
        self.cancelled = True
        self._win.destroy()


# pylint: disable-next=too-few-public-methods,too-many-instance-attributes
class _FormatDialog(_ModalDialog):
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
        box.pack(anchor='w', padx=36, pady=2)

    def _add_file_row(self) -> None:
        """Add the configuration-file radio button, entry and browse."""
        self._add_radio('Read format from a configuration file:', MODE_FILE)
        row = tk.Frame(self._win)
        row.pack(anchor='w', padx=36, pady=2, fill='x')
        tk.Entry(row, textvariable=self._path, width=30).pack(side='left')
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


def choose_key_list_output(parent: tk.Misc) -> Optional[str]:
    """Ask for a key list file to create, or None when cancelled."""
    name = filedialog.asksaveasfilename(parent=parent, title='Write keys')
    return name or None


def choose_changes_output(parent: tk.Misc) -> Optional[str]:
    """Ask for a changes file to create, or None when cancelled."""
    name = filedialog.asksaveasfilename(parent=parent, title='Save changes')
    return name or None


# pylint: disable-next=too-few-public-methods
class _BufferDialog(_ModalDialog):
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
        tk.Entry(self._win, textvariable=self._text,
                 width=10).pack(anchor='w', padx=12)

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


def ask_buffer_days(parent: tk.Misc) -> Optional[int]:
    """Ask for the buffer in days, or None when the dialog is cancelled."""
    dialog = _BufferDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.days


def show_change_list(parent: tk.Misc, title: str, text: str,
                     on_save: Callable[[], None]) -> tk.Toplevel:
    """Show a change listing with Save-to-file and Dismiss buttons.

    The listing is shown read-only. The Save button calls ``on_save`` and
    the Dismiss button closes the window. The created window is returned
    so a caller (or a test) can drive or close it.
    """
    win = tk.Toplevel(parent)
    win.title(title)
    if isinstance(parent, tk.Wm):
        win.transient(parent)
    box = tk.Text(win, width=50, height=12, wrap='none')
    box.insert('1.0', text)
    box.configure(state='disabled')
    box.pack(padx=12, pady=(10, 4), fill='both', expand=True)
    button_bar = tk.Frame(win)
    button_bar.pack(padx=12, pady=10, fill='x')
    tk.Button(button_bar, text='Save to file…',
              command=on_save).pack(side='left')
    tk.Button(button_bar, text='Dismiss',
              command=win.destroy).pack(side='right')
    return win


@dataclass
class DepOptions:
    """The options selected for ordering a backlog by dependencies."""

    later: bool
    mode: DependencyMode
    space_around: Optional[list[str]]


@dataclass
class StartChoice:
    """The start date selected for estimating ready dates."""

    start_date: Optional[date]


# pylint: disable-next=too-few-public-methods
class _KeysDialog(_ModalDialog):
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
class _DepOptionsDialog(_ModalDialog):
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
        ttk.Combobox(self._win, textvariable=self._mode, values=names,
                     state='readonly').pack(anchor='w', padx=12)

    def _build_space(self) -> None:
        """Add the space-around label and key entry."""
        tk.Label(self._win, text='Keys to keep far from dependencies '
                 '(optional, space separated):').pack(anchor='w', padx=12,
                                                      pady=(6, 2))
        tk.Entry(self._win, textvariable=self._space,
                 width=40).pack(anchor='w', padx=12)

    def _confirm(self) -> None:
        """Store the selected options and close the dialog."""
        space = self._space.get().split()
        self.options = DepOptions(later=self._later.get(),
                                  mode=DependencyMode[self._mode.get()],
                                  space_around=space or None)
        super()._confirm()


# pylint: disable-next=too-few-public-methods
class _StartDateDialog(_ModalDialog):
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
        tk.Entry(self._win, textvariable=self._date,
                 width=20).pack(anchor='w', padx=12)

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
class _LevelsDialog(_ModalDialog):
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
class _DateOrderDialog(_ModalDialog):
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


def ask_keys(parent: tk.Misc, sink: TextIO) -> Optional[list[str]]:
    """Ask for the leading keys, or None when the dialog is cancelled."""
    dialog = _KeysDialog(parent, sink)
    if dialog.cancelled:
        return None
    return dialog.keys


def ask_dep_options(parent: tk.Misc) -> Optional[DepOptions]:
    """Ask for the dependency options, or None when cancelled."""
    dialog = _DepOptionsDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.options


def ask_start_date(parent: tk.Misc) -> Optional[StartChoice]:
    """Ask for the start date, or None when the dialog is cancelled."""
    dialog = _StartDateDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.choice


def ask_levels(parent: tk.Misc) -> Optional[list[int]]:
    """Ask for the levels to extract, or None when cancelled."""
    dialog = _LevelsDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.levels


def ask_date_order(parent: tk.Misc) -> Optional[bool]:
    """Ask whether to order by estimated date, or None when cancelled."""
    dialog = _DateOrderDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.by_estimated
