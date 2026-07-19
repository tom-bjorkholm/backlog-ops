#! /usr/local/bin/python3
"""A scroll command that shows a scrollbar only while it can scroll.

A table that fits its area needs no scrollbar, and a scrollbar that is
always shown wastes space and hints at hidden content that is not there.
:func:`auto_hide` returns the scroll command for a scrolling widget: the
command hides the scrollbar while the whole range is visible and shows it
again once the widget grows past its area. It works for any widget that
reports its position through an ``xscrollcommand`` or ``yscrollcommand``,
so the wizard table canvas and the read-only backlog tree can share it.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from tkinter import ttk
from typing import Callable


def auto_hide(scrollbar: ttk.Scrollbar
              ) -> Callable[[float | str, float | str], None]:
    """Return a scroll command that hides the scrollbar when it is full.

    The result is used as a widget's ``xscrollcommand`` or
    ``yscrollcommand``. Tk reports the position as two fractions, which it
    passes as strings, so the command accepts either a number or its
    string form. The scrollbar must be laid out with the grid manager,
    whose ``grid_remove`` remembers its cell across the hide.
    """
    def command(first: float | str, last: float | str) -> None:
        """Hide or show the scrollbar, then move its thumb to the view."""
        if float(first) <= 0.0 and float(last) >= 1.0:
            scrollbar.grid_remove()
        else:
            scrollbar.grid()
        scrollbar.set(first, last)
    return command
