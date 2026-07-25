#! /usr/local/bin/python3
"""Tests for the month calendar picker and its date helpers."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from datetime import date
from typing import Optional
import pytest
from backlogops_gui.wizard_calendar import CalendarPicker, _restore_grab, \
    day_out_of_range, month_weeks, shift_month
from .gui_test_helpers import gui_root


def test_month_weeks() -> None:
    """Test month_weeks lays a month out as weeks of day numbers."""
    weeks = month_weeks(2026, 2)
    days = [day for week in weeks for day in week if day != 0]
    assert days == list(range(1, 29))
    assert all(len(week) == 7 for week in weeks)


@pytest.mark.parametrize('year, month, action, expected', [
    (2026, 1, 'prev_month', (2025, 12)), (2026, 12, 'next_month', (2027, 1)),
    (2026, 6, 'prev_year', (2025, 6)), (2026, 6, 'next_year', (2027, 6)),
    (2026, 6, 'prev_month', (2026, 5))])
def test_shift_month(year: int, month: int, action: str,
                     expected: tuple[int, int]) -> None:
    """Test shift_month moves the shown month across year boundaries."""
    assert shift_month(year, month, action) == expected


@pytest.mark.parametrize('day, lo, hi, expected', [
    (date(2026, 7, 1), None, None, False),
    (date(2025, 1, 1), date(2026, 1, 1), None, True),
    (date(2027, 1, 1), None, date(2026, 12, 31), True)])
def test_day_out_of_range(day: date, lo: Optional[date], hi: Optional[date],
                          expected: bool) -> None:
    """Test day_out_of_range respects the inclusive date bounds."""
    assert day_out_of_range(day, lo, hi) is expected


def _picker(root: tk.Tk, seed: date, lo: Optional[date] = None,
            hi: Optional[date] = None
            ) -> tuple[CalendarPicker, list[Optional[date]]]:
    """Build a calendar picker recording every picked outcome."""
    picked: list[Optional[date]] = []
    return CalendarPicker(root, seed, lo, hi, picked.append), picked


def test_picker_pick_day() -> None:
    """Test clicking a day returns its date and closes the window."""
    with gui_root() as root:
        picker, picked = _picker(root, date(2026, 7, 24))
        # pylint: disable-next=protected-access
        picker._pick(15)
        assert picked == [date(2026, 7, 15)]
        # pylint: disable-next=protected-access
        assert not picker._win.winfo_exists()


def test_picker_cancel() -> None:
    """Test cancelling returns no date and closes the window."""
    with gui_root() as root:
        picker, picked = _picker(root, date(2026, 7, 24))
        # pylint: disable-next=protected-access
        picker._cancel()
        assert picked == [None]


def test_restore_grab_none() -> None:
    """Test restoring the grab tolerates having no widget to restore to."""
    _restore_grab(None)


def test_restore_grab_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test restoring the grab swallows a Tcl error from a gone window."""
    with gui_root() as root:
        def _boom() -> None:
            """Fail the grab as Tk does when the window cannot hold it."""
            raise tk.TclError('cannot grab')
        monkeypatch.setattr(root, 'grab_set', _boom)
        _restore_grab(tk.Frame(root))


def test_grab_window_gone() -> None:
    """Test grabbing does nothing once the calendar window is destroyed."""
    with gui_root() as root:
        picker, _ = _picker(root, date(2026, 7, 24))
        # pylint: disable-next=protected-access
        picker._win.destroy()
        # pylint: disable-next=protected-access
        picker._grab()


def test_grab_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a not-yet-viewable window reschedules the grab on the loop.

    The window rejects the grab while it is not viewable, so the picker
    retries it after a short delay instead of raising.
    """
    with gui_root() as root:
        picker, _ = _picker(root, date(2026, 7, 24))
        scheduled: list[tuple[int, object]] = []

        def _boom() -> None:
            """Reject the grab as Tk does for a not-yet-viewable window."""
            raise tk.TclError('window not viewable')

        def _after(delay: int, callback: object) -> str:
            """Record a rescheduled retry instead of running it."""
            scheduled.append((delay, callback))
            return ''
        # pylint: disable-next=protected-access
        monkeypatch.setattr(picker._win, 'grab_set', _boom)
        # pylint: disable-next=protected-access
        monkeypatch.setattr(picker._win, 'after', _after)
        # pylint: disable-next=protected-access
        picker._grab()
        # pylint: disable-next=protected-access
        assert scheduled == [(50, picker._grab)]


@pytest.mark.focus_sensitive
def test_grab_real() -> None:
    """Test a shown calendar takes the modal grab and restores it on close.

    This is the real-display counterpart to the deterministic grab tests:
    the open calendar holds the grab and closing it hands the grab back to
    the wizard window.
    """
    with gui_root() as root:
        root.deiconify()
        root.grab_set()
        picker, _ = _picker(root, date(2026, 7, 24))
        root.update()
        current = root.grab_current()  # type: ignore[no-untyped-call]
        # pylint: disable-next=protected-access
        assert current is picker._win
        # pylint: disable-next=protected-access
        picker._cancel()
        root.update()
        assert root.grab_current() is root  # type: ignore[no-untyped-call]


def test_picker_navigate() -> None:
    """Test navigating changes the month a picked day belongs to."""
    with gui_root() as root:
        picker, picked = _picker(root, date(2026, 7, 24))
        # pylint: disable-next=protected-access
        picker._navigate('next_month')
        # pylint: disable-next=protected-access
        picker._pick(3)
        assert picked == [date(2026, 8, 3)]


def _day_buttons(picker: CalendarPicker) -> list[tk.Button]:
    """Return the day buttons currently placed in the calendar grid."""
    # pylint: disable-next=protected-access
    children = picker._grid.winfo_children()
    return [child for child in children if isinstance(child, tk.Button)]


def test_picker_bounds() -> None:
    """Test days outside the bounds are shown as disabled buttons."""
    with gui_root() as root:
        picker, _ = _picker(root, date(2026, 7, 15), date(2026, 7, 10),
                            date(2026, 7, 20))
        states = {int(button.cget('text')): str(button.cget('state'))
                  for button in _day_buttons(picker)}
        assert states[5] == 'disabled'
        assert states[15] == 'normal'
