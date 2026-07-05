#! /usr/local/bin/python3
"""Base for the small modal option dialogs of the application.

A modal option dialog is a top-level window with an OK and a Cancel
button. :class:`ModalDialog` builds the window and its close handler, adds
the two buttons, focuses the first input and waits for the window to
close. A subclass builds its own inputs and overrides :meth:`_confirm` to
store the entered values before the window closes.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from backlogops_gui.close_binding import bind_close
from backlogops_gui.gui_style import focus_first_input


# pylint: disable-next=too-few-public-methods
class ModalDialog:
    """Base for small modal dialogs with OK and Cancel buttons."""

    def __init__(self, parent: tk.Misc, title: str) -> None:
        """Create the modal top-level window and its close handler."""
        self.cancelled = False
        self._win = tk.Toplevel(parent)
        self._win.title(title)
        if isinstance(parent, tk.Wm):
            self._win.transient(parent)
        self._win.protocol('WM_DELETE_WINDOW', self._cancel)
        bind_close(self._win, self._cancel)

    def _show(self) -> None:
        """Add buttons, focus the first input and wait for the close."""
        self._add_buttons()
        focus_first_input(self._win)
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
