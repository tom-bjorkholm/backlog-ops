#! /usr/local/bin/python3
"""Shared look and focus helpers for the Tkinter input windows.

Editable input widgets blend into the window background on some
platforms, so the user cannot tell an entry, drop-down or list from the
surrounding window. :func:`style_input` gives such a widget a white
field and a thin border so it stands out. :func:`focus_first_input`
puts the keyboard focus on the first editable widget of a window, so the
user can start typing as soon as the window opens.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import ttk
from typing import Optional

INPUT_BG = 'white'
INPUT_STYLE = 'Input.TCombobox'


def style_input(widget: tk.Widget) -> None:
    """Make one editable input widget stand out from the background.

    A classic entry, text box or list gets a white field and a thin
    solid border. A drop-down keeps its arrow but gets a white field
    through a shared ttk style. Any other widget is left unchanged. The
    ttk styling is best-effort: a native theme that ignores field colors
    leaves the drop-down as it is.
    """
    if isinstance(widget, ttk.Widget):
        if isinstance(widget, ttk.Combobox):
            _style_combobox(widget)
        return
    if isinstance(widget, (tk.Entry, tk.Text, tk.Listbox)):
        widget.configure(background=INPUT_BG, relief='solid', borderwidth=1)


def _style_combobox(widget: ttk.Combobox) -> None:
    """Give a drop-down a white field through a shared ttk style."""
    style = ttk.Style(widget)
    style.configure(INPUT_STYLE, fieldbackground=INPUT_BG)
    style.map(INPUT_STYLE, fieldbackground=[('readonly', INPUT_BG)])
    widget.configure(style=INPUT_STYLE)


def focus_first_input(window: tk.Misc) -> None:
    """Give the keyboard focus to the first editable input, if any."""
    target = _first_input(window)
    if target is not None:
        target.focus_set()


def _first_input(parent: tk.Misc) -> Optional[tk.Misc]:
    """Return the first editable input under parent, in child order."""
    for child in parent.winfo_children():
        if _is_input(child):
            return child
        found = _first_input(child)
        if found is not None:
            return found
    return None


def _is_input(widget: tk.Misc) -> bool:
    """Return whether the widget is an editable input to fill in."""
    if not isinstance(widget, (tk.Entry, tk.Listbox, tk.Text)):
        return False
    return str(widget.cget('state')) != 'disabled'
