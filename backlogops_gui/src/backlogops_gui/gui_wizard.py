#! /usr/local/bin/python3
"""Graphical bridge that drives the synchronous teams wizard.

The teams configuration wizard asks its questions through a
:class:`WizardUiBridge` by calling :meth:`ask` in a loop. This module
provides a bridge that answers each call with a modal Tkinter dialog, so
the existing synchronous wizard can run unchanged inside a menu callback.
A cancelled dialog raises :class:`EOFError`, which the wizard documents as
the way an interrupted input is reported.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional, Sequence, TextIO
from tableio_cfg_json import WizardUiBridge
from backlogops import NoTextIO

WIZARD_TITLE = 'Configuration wizard'
WRAP_LENGTH = 480


# pylint: disable-next=too-few-public-methods
class _AskDialog:
    """Modal dialog that asks one wizard question and stores the answer."""

    def __init__(self, parent: tk.Misc, question: str,
                 re_ask_reason: Optional[str],
                 choices: Optional[Sequence[str]]) -> None:
        """Build, show and wait for the modal question dialog."""
        self.result: Optional[str | int] = None
        self.cancelled = False
        self._choices = choices
        self._win = tk.Toplevel(parent)
        self._win.title(WIZARD_TITLE)
        if isinstance(parent, tk.Wm):
            self._win.transient(parent)
        self._win.protocol('WM_DELETE_WINDOW', self._cancel)
        self._listbox: Optional[tk.Listbox] = None
        self._entry: Optional[tk.Entry] = None
        self._build(question, re_ask_reason, choices)
        self._win.grab_set()
        self._win.wait_window()

    def _build(self, question: str, re_ask_reason: Optional[str],
               choices: Optional[Sequence[str]]) -> None:
        """Create the widgets for the question and the answer area."""
        if re_ask_reason is not None:
            self._add_label(re_ask_reason, 'red')
        self._add_label(question, 'black')
        if choices is not None:
            self._add_choices(choices)
        else:
            self._add_entry()
        self._add_buttons(choices is not None)

    def _add_label(self, text: str, color: str) -> None:
        """Add one wrapped text label to the dialog."""
        label = tk.Label(self._win, text=text, fg=color,
                         wraplength=WRAP_LENGTH, justify='left')
        label.pack(padx=12, pady=6, anchor='w')

    def _add_choices(self, choices: Sequence[str]) -> None:
        """Add a single-selection list of the offered choices."""
        listbox = tk.Listbox(self._win, height=min(len(choices), 12),
                             exportselection=False)
        for choice in choices:
            listbox.insert('end', choice)
        listbox.pack(padx=12, pady=6, fill='both', expand=True)
        self._listbox = listbox

    def _add_entry(self) -> None:
        """Add a free-text entry for the answer."""
        entry = tk.Entry(self._win, width=40)
        entry.pack(padx=12, pady=6, fill='x')
        entry.focus_set()
        self._entry = entry

    def _add_buttons(self, has_choices: bool) -> None:
        """Add the confirm, default and cancel buttons."""
        button_bar = tk.Frame(self._win)
        button_bar.pack(padx=12, pady=10, fill='x')
        ok_button = tk.Button(button_bar, text='OK', command=self._confirm)
        ok_button.pack(side='left')
        if has_choices:
            default_button = tk.Button(button_bar, text='Use default',
                                       command=self._default)
            default_button.pack(side='left', padx=6)
        cancel_button = tk.Button(button_bar, text='Cancel',
                                  command=self._cancel)
        cancel_button.pack(side='right')

    def _confirm(self) -> None:
        """Store the selected or entered answer and close the dialog."""
        if self._listbox is not None:
            box = self._listbox
            picks = box.curselection()  # type: ignore[no-untyped-call]
            if not picks:
                return
            self.result = int(picks[0])
        else:
            assert self._entry is not None
            self.result = self._entry.get()
        self._win.destroy()

    def _default(self) -> None:
        """Answer with an empty string to request the default value."""
        self.result = ''
        self._win.destroy()

    def _cancel(self) -> None:
        """Mark the dialog cancelled and close it."""
        self.cancelled = True
        self._win.destroy()


class TkWizardBridge(WizardUiBridge):
    """Bridge that answers wizard questions with Tkinter dialogs."""

    def __init__(self, parent: tk.Misc,
                 ask_fn: Optional[Callable[
                     [str, Optional[str], Optional[Sequence[str]]],
                     str | int]] = None,
                 show_fn: Optional[Callable[[str], None]] = None) -> None:
        """Store the parent window and optional injected dialog callables.

        Args:
            parent: The window the modal dialogs are shown over.
            ask_fn: Replacement for the modal question dialog, used by
                tests to script answers without a display.
            show_fn: Replacement for the modal message dialog.
        """
        self._parent = parent
        self._ask = ask_fn if ask_fn is not None else self._ask_modal
        self._show = show_fn if show_fn is not None else self._show_modal

    def ask(self, question: str, re_ask_reason: Optional[str] = None,
            choices: Optional[Sequence[str]] = None) -> str | int:
        """Ask one question and return the user's answer.

        Returns the entered text, or the zero-based index of a selected
        choice, or an empty string when the user requests the default.

        Raises:
            EOFError: The user cancelled the dialog.
        """
        return self._ask(question, re_ask_reason, choices)

    def error_file(self) -> TextIO:
        """Return a sink that discards low-level wizard diagnostics."""
        return NoTextIO()

    def show(self, message: str) -> None:
        """Show an informational message to the user."""
        self._show(message)

    def _ask_modal(self, question: str, re_ask_reason: Optional[str],
                   choices: Optional[Sequence[str]]) -> str | int:
        """Ask one question with a modal dialog over the parent window."""
        dialog = _AskDialog(self._parent, question, re_ask_reason, choices)
        if dialog.cancelled:
            raise EOFError('Configuration wizard cancelled by the user.')
        assert dialog.result is not None
        return dialog.result

    def _show_modal(self, message: str) -> None:
        """Show one informational message with a modal dialog."""
        messagebox.showinfo(WIZARD_TITLE, message, parent=self._parent)
