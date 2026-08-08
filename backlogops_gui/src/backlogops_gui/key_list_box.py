#! /usr/local/bin/python3
"""Shared key-list text box with a load-from-file button for dialogs.

The order-by-keys dialog and the Jira rank dialog both let the user type
or paste a list of keys and load it from a file. This module holds that
shared widget and the file reading so the two dialogs do not repeat it.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import filedialog, messagebox
from collections.abc import Callable
from typing import TextIO
from wizard_tk_bridge.gui_style import style_input
from backlogops import read_key_list

KEY_READ_ERRORS = (ValueError, TypeError, KeyError, OSError)


def build_key_box(win: tk.Misc, label: str, command: Callable[[], None], *,
                  label_pady: tuple[int, int] = (10, 2)) -> tk.Text:
    """Add a key-entry label, text box and load-from-file button."""
    tk.Label(win, text=label).pack(anchor='w', padx=12, pady=label_pady)
    text = tk.Text(win, width=40, height=8)
    style_input(text)
    text.pack(padx=12, pady=2)
    tk.Button(win, text='Load from file…',
              command=command).pack(anchor='w', padx=12, pady=4)
    return text


def load_keys_into(win: tk.Misc, text: tk.Text, sink: TextIO) -> None:
    """Read a key list file into the text box, reporting failures."""
    name = filedialog.askopenfilename(parent=win, title='Read key list')
    if not name:
        return
    try:
        keys = read_key_list(name, stderr_file=sink)
    except KEY_READ_ERRORS as error:
        messagebox.showerror('Could not read key list', str(error), parent=win)
        return
    text.delete('1.0', 'end')
    text.insert('end', '\n'.join(keys))
