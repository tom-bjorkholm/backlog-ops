#! /usr/local/bin/python3
"""Tests for the placeholder entry and the calendar pick row."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from datetime import date
from typing import Callable, Optional
import pytest
from tableio_cfg_json import AskDateField
import backlogops_gui.wizard_pick_row as pick_row
from backlogops_gui.wizard_pick_row import HintEntry, PickRow
from .gui_test_helpers import gui_root


def _noop() -> None:
    """Ignore a change notification."""


def test_hint_placeholder() -> None:
    """Test an empty entry reads as empty while showing its hint."""
    with gui_root() as root:
        entry = HintEntry(root, 'a number', '', _noop)
        assert entry.text() == ''
        assert entry.entry.get() == 'a number'


def test_hint_initial() -> None:
    """Test an entry built with initial text shows and reads that text."""
    with gui_root() as root:
        entry = HintEntry(root, 'a number', '3.5', _noop)
        assert entry.text() == '3.5'


def test_hint_set_text() -> None:
    """Test set_text replaces the value and restores the hint on empty."""
    with gui_root() as root:
        entry = HintEntry(root, 'a number', '', _noop)
        entry.set_text('7')
        assert entry.text() == '7'
        entry.set_text('')
        assert entry.text() == ''
        assert entry.entry.get() == 'a number'


def test_hint_focus() -> None:
    """Test focusing clears the hint and leaving empty restores it."""
    with gui_root() as root:
        entry = HintEntry(root, 'a number', '', _noop)
        # pylint: disable-next=protected-access
        entry._focus_in()
        assert entry.entry.get() == ''
        # pylint: disable-next=protected-access
        entry._focus_out()
        assert entry.text() == ''
        assert entry.entry.get() == 'a number'


def test_hint_set_text_noop() -> None:
    """Test set_text with the current text is a no-op early return."""
    with gui_root() as root:
        entry = HintEntry(root, 'a number', '5', _noop)
        entry.set_text('5')
        assert entry.text() == '5'


def test_hint_focus_no_change() -> None:
    """Test focus events do nothing to an entry already showing typed text.

    With real text present the entry is not a placeholder, so focusing in
    keeps the text, and it is not empty, so leaving it restores nothing.
    """
    with gui_root() as root:
        entry = HintEntry(root, 'a number', '3.5', _noop)
        # pylint: disable-next=protected-access
        entry._focus_in()
        assert entry.entry.get() == '3.5'
        # pylint: disable-next=protected-access
        entry._focus_out()
        assert entry.text() == '3.5'


@pytest.mark.focus_sensitive
def test_hint_real_focus() -> None:
    """Test real focus in and out clears and restores the greyed hint.

    This drives the same behaviour as :func:`test_hint_focus` but through
    genuine keyboard-focus transitions, so it needs a focused display.
    """
    with gui_root() as root:
        root.deiconify()
        entry = HintEntry(root, 'a number', '', _noop)
        entry.entry.pack()
        other = tk.Entry(root)
        other.pack()
        root.update()
        entry.entry.focus_force()
        root.update()
        assert entry.entry.get() == ''
        other.focus_force()
        root.update()
        assert entry.entry.get() == 'a number'


def test_hint_set_disabled() -> None:
    """Test set_text writes into a disabled entry and keeps it disabled."""
    with gui_root() as root:
        entry = HintEntry(root, 'a number', '', _noop)
        entry.set_enabled(False)
        entry.set_text('9')
        assert entry.text() == '9'
        assert str(entry.entry.cget('state')) == 'disabled'


def _row(root: tk.Tk) -> tuple[PickRow, list[int]]:
    """Build a date pick row recording each change notification."""
    changes: list[int] = []
    field = AskDateField('Day', None)
    row = PickRow(tk.Frame(root), field, 'a date as YYYY-MM-DD', '',
                  lambda: changes.append(1))
    return row, changes


def _fake_calendars(monkeypatch: pytest.MonkeyPatch
                    ) -> list[Callable[[Optional[date]], None]]:
    """Replace the calendar with a recorder of its pick callbacks."""
    opened: list[Callable[[Optional[date]], None]] = []
    monkeypatch.setattr(pick_row, 'CalendarPicker',
                        lambda *args: opened.append(args[-1]))
    return opened


def test_pick_row_question(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test typing the pick token clears it and opens the calendar."""
    with gui_root() as root:
        opened = _fake_calendars(monkeypatch)
        row, _ = _row(root)
        row.set_text('?')
        # pylint: disable-next=protected-access
        row._changed()
        assert len(opened) == 1
        assert row.text() == ''


def test_pick_row_notifies(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test typing an ordinary value notifies a change without a calendar."""
    with gui_root() as root:
        opened = _fake_calendars(monkeypatch)
        row, changes = _row(root)
        row.set_text('2026-07-24')
        # pylint: disable-next=protected-access
        row._changed()
        assert changes == [1] and not opened


def test_pick_row_picked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a calendar choice fills the entry and notifies a change."""
    with gui_root() as root:
        opened = _fake_calendars(monkeypatch)
        row, changes = _row(root)
        # pylint: disable-next=protected-access
        row._open_calendar()
        opened[0](date(2026, 8, 1))
        assert row.text() == '2026-08-01'
        assert changes == [1]


def test_pick_row_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the calendar leaves the entry unchanged."""
    with gui_root() as root:
        opened = _fake_calendars(monkeypatch)
        row, changes = _row(root)
        # pylint: disable-next=protected-access
        row._open_calendar()
        opened[0](None)
        assert row.text() == ''
        assert not changes
