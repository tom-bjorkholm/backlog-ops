#! /usr/local/bin/python3
"""Tkinter placeholder application for backlog operations."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Literal

from backlogops_gui.tcltk_version import check_tcltk_version


APP_TEXT = 'Backlog operations GUI - no functionality yet'
APP_TITLE = 'Backlog operations GUI'
WARN_WRAP_LENGTH = 520


def _add_label(root: tk.Tk, text: str,
               justify: Literal['center', 'left']) -> None:
    """Add one text label to the main window."""
    label = tk.Label(root, text=text, wraplength=WARN_WRAP_LENGTH,
                     justify=justify)
    label.pack(padx=16, pady=8)


def _add_quit_button(root: tk.Tk) -> None:
    """Add the quit button to the main window."""
    button = tk.Button(root, text='Quit', command=root.quit)
    button.pack(padx=16, pady=12)


def build_main_window(root: tk.Tk) -> None:
    """Build the placeholder widgets in the main window."""
    root.title(APP_TITLE)
    _add_label(root, APP_TEXT, 'center')
    warning_text = check_tcltk_version(root)
    if warning_text is not None:
        _add_label(root, warning_text, 'left')
    _add_quit_button(root)


def main() -> None:
    """Start the backlog operations GUI."""
    root = tk.Tk()
    build_main_window(root)
    root.mainloop()
