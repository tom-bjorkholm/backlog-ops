#! /usr/local/bin/python3
"""Read-only text pop-ups for change listings and text reports.

A change listing is shown with a Save-to-file and a Dismiss button, so the
user can keep a record of what an action changed. A text report is shown
read-only but copy-pasteable, with only a Dismiss button. Both show their
text in a non-wrapping box with a vertical and a horizontal scrollbar, so
the user sees that the text continues past the visible part of the window.
Both return the created window so a caller or a test can drive or close it.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable
from wizard_tk_bridge.close_binding import bind_close


def _add_scrollbars(frame: tk.Frame, box: tk.Text) -> None:
    """Add the vertical and horizontal scrollbars driving the text box."""
    vertical = tk.Scrollbar(frame, orient='vertical', command=box.yview)
    horizontal = tk.Scrollbar(frame, orient='horizontal', command=box.xview)
    box.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    vertical.grid(row=0, column=1, sticky='ns')
    horizontal.grid(row=1, column=0, sticky='ew')


def _scrolled_text(parent: tk.Misc, text: str, width: int,
                   height: int) -> None:
    """Pack a read-only scrollable box showing the text in the parent.

    The text is shown in a disabled box, which still lets the user select
    and copy it. The box does not wrap, so a line longer than the window
    is reached with the horizontal scrollbar.
    """
    frame = tk.Frame(parent)
    frame.pack(padx=12, pady=(10, 4), fill='both', expand=True)
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    box = tk.Text(frame, width=width, height=height, wrap='none')
    box.insert('1.0', text)
    box.configure(state='disabled')
    box.grid(row=0, column=0, sticky='nsew')
    _add_scrollbars(frame, box)


def show_change_list(parent: tk.Misc, title: str, text: str,
                     on_save: Callable[[], None]) -> tk.Toplevel:
    """Show a change listing with Save-to-file and Dismiss buttons.

    The listing is shown read-only in a scrollable box. The Save button
    calls ``on_save`` and the Dismiss button closes the window. The created
    window is returned so a caller (or a test) can drive or close it.
    """
    win = tk.Toplevel(parent)
    win.title(title)
    if isinstance(parent, tk.Wm):
        win.transient(parent)
    _scrolled_text(win, text, 50, 12)
    button_bar = tk.Frame(win)
    button_bar.pack(padx=12, pady=10, fill='x')
    tk.Button(button_bar, text='Save to file…',
              command=on_save).pack(side='left')
    tk.Button(button_bar, text='Dismiss',
              command=win.destroy).pack(side='right')
    bind_close(win)
    return win


def show_text_report(parent: tk.Misc, title: str, text: str) -> tk.Toplevel:
    """Show read-only, copy-pasteable text with a Dismiss button.

    The report is shown in a scrollable box tall enough to show a listing
    with a few entries per section without scrolling. The created window
    is returned so a caller or a test can drive or close it.
    """
    win = tk.Toplevel(parent)
    win.title(title)
    if isinstance(parent, tk.Wm):
        win.transient(parent)
    _scrolled_text(win, text, 72, 24)
    tk.Button(win, text='Dismiss', command=win.destroy).pack(padx=12, pady=10)
    bind_close(win)
    return win
