#! /usr/local/bin/python3
"""Placeholder-aware entries for the typed wizard form fields.

The float, time and duration form fields are shown as a text entry that
displays its accepted-format hint as greyed placeholder text while empty,
so the user learns the format without cluttering the field label. A date
or date-time field adds a Pick button that opens a month calendar, and
typing the ``?`` token into the entry opens the same calendar.

:class:`HintEntry` is the placeholder entry, and :class:`PickRow` bundles
one with the calendar button. Both satisfy :class:`TypedInput`, the small
interface the form editor uses to read, write, and enable a typed row.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from datetime import date
from typing import Callable, Optional, Protocol
from wizard_ui_bridge import AskField
from backlogops_gui.gui_style import style_input
from backlogops_gui.wizard_calendar import CalendarPicker
from backlogops_gui.wizard_typed import calendar_seed, combined_text

ENTRY_WIDTH = 34
NORMAL_FG = 'black'
HINT_FG = 'grey'
_PICK_TOKEN = '?'


class TypedInput(Protocol):
    """The read, write and enable interface of a typed form input."""

    def text(self) -> str:
        """Return the current text, empty when only a placeholder shows."""

    def set_text(self, text: str) -> None:
        """Replace the current text, showing the placeholder when empty."""

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the input for user editing."""


class HintEntry:
    """A text entry showing a greyed format hint while it is empty."""

    def __init__(self, parent: tk.Misc, hint: str, initial: str,
                 on_change: Callable[[], None]) -> None:
        """Build the entry, showing initial text or the greyed hint."""
        self._hint = hint
        self._placeholder = False
        self.entry = tk.Entry(parent, width=ENTRY_WIDTH)
        style_input(self.entry)
        if initial != '':
            self.entry.configure(fg=NORMAL_FG)
            self.entry.insert(0, initial)
        else:
            self._show_hint()
        self.entry.bind('<FocusIn>', lambda _event: self._focus_in())
        self.entry.bind('<FocusOut>', lambda _event: self._focus_out())
        self.entry.bind('<KeyRelease>', lambda _event: on_change())

    def text(self) -> str:
        """Return the entered text, empty when only the hint shows."""
        return '' if self._placeholder else self.entry.get()

    def set_text(self, text: str) -> None:
        """Replace the text, showing the greyed hint when text is empty."""
        if self.text() == text:
            return
        state = self.entry['state']
        self.entry['state'] = 'normal'
        self.entry.delete(0, 'end')
        if text == '':
            self._show_hint()
        else:
            self._placeholder = False
            self.entry.configure(fg=NORMAL_FG)
            self.entry.insert(0, text)
        self.entry['state'] = state

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the entry for user editing."""
        self.entry['state'] = 'normal' if enabled else 'disabled'

    def _show_hint(self) -> None:
        """Show the greyed placeholder hint in the empty entry."""
        self._placeholder = True
        self.entry.configure(fg=HINT_FG)
        self.entry.insert(0, self._hint)

    def _focus_in(self) -> None:
        """Clear the greyed hint when the entry gains focus."""
        if self._placeholder:
            self._placeholder = False
            self.entry.delete(0, 'end')
            self.entry.configure(fg=NORMAL_FG)

    def _focus_out(self) -> None:
        """Restore the greyed hint when the entry is left empty."""
        if self.entry.get() == '':
            self.entry.delete(0, 'end')
            self._show_hint()


class PickRow:
    """A hint entry paired with a Pick button that opens a calendar."""

    def __init__(self, parent: tk.Misc, field: AskField, hint: str,
                 initial: str, on_change: Callable[[], None]) -> None:
        """Build the entry and Pick button inside a new frame."""
        self._field = field
        self._on_change = on_change
        self.frame = tk.Frame(parent)
        self._input = HintEntry(self.frame, hint, initial, self._changed)
        self._input.entry.pack(side='left')
        self._button = tk.Button(self.frame, text='Pick…',
                                 command=self._open_calendar)
        self._button.pack(side='left', padx=6)

    def text(self) -> str:
        """Return the entered date or date-time text."""
        return self._input.text()

    def set_text(self, text: str) -> None:
        """Replace the entered text, showing the hint when empty."""
        self._input.set_text(text)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable both the entry and the Pick button."""
        self._input.set_enabled(enabled)
        self._button['state'] = 'normal' if enabled else 'disabled'

    def _changed(self) -> None:
        """React to typing, opening the calendar on the pick token."""
        if self._input.text() == _PICK_TOKEN:
            self._input.set_text('')
            self._open_calendar()
            return
        self._on_change()

    def _open_calendar(self) -> None:
        """Open the month calendar seeded from the current value."""
        seed, minimum, maximum = calendar_seed(self._field, self._input.text())
        CalendarPicker(self.frame, seed, minimum, maximum, self._picked)

    def _picked(self, picked: Optional[date]) -> None:
        """Write a picked date into the entry, keeping any typed time."""
        if picked is None:
            return
        self._input.set_text(combined_text(self._field, picked,
                                           self._input.text()))
        self._on_change()
