#! /usr/local/bin/python3
"""Read-only text pop-ups for change listings and text reports.

A change listing is shown with a Save-to-file and a Dismiss button, so the
user can keep a record of what an action changed. A text report is shown
read-only but copy-pasteable, with only a Dismiss button. Both return the
created window so a caller or a test can drive or close it.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable


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


def show_text_report(parent: tk.Misc, title: str, text: str) -> tk.Toplevel:
    """Show read-only, copy-pasteable text with a Dismiss button.

    The text is shown in a disabled text box, which still lets the user
    select and copy it. The created window is returned so a caller or a
    test can drive or close it.
    """
    win = tk.Toplevel(parent)
    win.title(title)
    if isinstance(parent, tk.Wm):
        win.transient(parent)
    box = tk.Text(win, width=50, height=14, wrap='none')
    box.insert('1.0', text)
    box.configure(state='disabled')
    box.pack(padx=12, pady=(10, 4), fill='both', expand=True)
    tk.Button(win, text='Dismiss', command=win.destroy).pack(padx=12, pady=10)
    return win
