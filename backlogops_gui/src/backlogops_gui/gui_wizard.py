#! /usr/local/bin/python3
"""Graphical bridge that drives the synchronous teams wizard.

The teams configuration wizard asks its questions through a
:class:`WizardUiBridge`, extended here as a :class:`YesNoUiBridge` so
yes/no questions can offer dedicated buttons. This module answers every
call by updating one reused, fixed-size window, so the whole wizard session
happens in a single pop-up that does not jump around the display. A
cancelled prompt raises :class:`EOFError`, which the wizard documents as
the way an interrupted input is reported.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable, Optional, Sequence, TextIO
from backlogops import NoTextIO, YesNoUiBridge

WIZARD_TITLE = 'Configuration wizard'
WINDOW_SIZE = '560x460'
WRAP_LENGTH = 500
MESSAGE_HEIGHT = 8
CHOICE_HEIGHT = 10
CANCEL_TEXT = 'Configuration wizard cancelled by the user.'


class _WizardWindow:
    """One reused window that asks every wizard prompt in turn."""

    def __init__(self, parent: tk.Misc) -> None:
        """Create the fixed-size window and its lasting message area."""
        self._result: object = ''
        self._cancelled = False
        self._win = tk.Toplevel(parent)
        self._win.title(WIZARD_TITLE)
        self._win.geometry(WINDOW_SIZE)
        self._win.resizable(False, False)
        if isinstance(parent, tk.Wm):
            self._win.transient(parent)
        self._win.protocol('WM_DELETE_WINDOW', self._cancel)
        self._done = tk.IntVar(self._win, 0)
        self._messages = self._build_messages()
        self._content = tk.Frame(self._win)
        self._content.pack(fill='both', expand=True, padx=12, pady=6)
        self._win.grab_set()

    def _build_messages(self) -> tk.Text:
        """Build the read-only area that keeps the wizard messages."""
        text = tk.Text(self._win, height=MESSAGE_HEIGHT, wrap='word',
                       state='disabled')
        text.pack(fill='x', padx=12, pady=(12, 6))
        return text

    def show(self, message: str) -> None:
        """Append one lasting message to the message area."""
        self._messages.configure(state='normal')
        self._messages.insert('end', message + '\n')
        self._messages.see('end')
        self._messages.configure(state='disabled')

    def close(self) -> None:
        """Destroy the wizard window."""
        self._win.destroy()

    def ask(self, question: str, re_ask: Optional[str],
            choices: Optional[Sequence[str]]) -> str | int:
        """Ask one free-text or choice question and return the answer."""
        if choices is None:
            return self._ask_text(question, re_ask)
        return self._ask_choice(question, re_ask, choices)

    def ask_yes_no(self, question: str, default: bool) -> bool:
        """Ask one yes/no question with dedicated buttons."""
        self._begin(question, None)
        box = tk.Frame(self._content)
        box.pack(pady=10)
        yes = tk.Button(box, text='Yes', command=lambda: self._finish(True))
        no = tk.Button(box, text='No', command=lambda: self._finish(False))
        yes.pack(side='left', padx=6)
        no.pack(side='left', padx=6)
        chosen = yes if default else no
        chosen.focus_set()
        self._win.bind('<Return>', lambda event: chosen.invoke())
        result = self._wait()
        assert isinstance(result, bool)
        return result

    def _ask_text(self, question: str, re_ask: Optional[str]) -> str:
        """Ask one free-text question and return the entered text."""
        self._begin(question, re_ask)
        entry = tk.Entry(self._content, width=44)
        entry.pack(anchor='w', pady=6)
        entry.focus_set()
        self._add_buttons(lambda: self._finish(entry.get()), None)
        self._win.bind('<Return>', lambda event: self._finish(entry.get()))
        result = self._wait()
        assert isinstance(result, str)
        return result

    def _ask_choice(self, question: str, re_ask: Optional[str],
                    choices: Sequence[str]) -> str | int:
        """Ask one question with a single-selection list of choices."""
        self._begin(question, re_ask)
        listbox = tk.Listbox(self._content, exportselection=False,
                             height=min(len(choices), CHOICE_HEIGHT))
        for choice in choices:
            listbox.insert('end', choice)
        listbox.pack(fill='x', pady=6)
        self._add_buttons(lambda: self._pick(listbox),
                          lambda: self._finish(''))
        result = self._wait()
        assert isinstance(result, (str, int))
        return result

    def _pick(self, listbox: tk.Listbox) -> None:
        """Finish a choice question with the selected zero-based index."""
        picks = listbox.curselection()  # type: ignore[no-untyped-call]
        if picks:
            self._finish(int(picks[0]))

    def _begin(self, question: str, re_ask: Optional[str]) -> None:
        """Clear the content area and show the question and any reason."""
        self._win.unbind('<Return>')
        for child in self._content.winfo_children():
            child.destroy()
        if re_ask is not None:
            self._add_label(re_ask, 'red')
        self._add_label(question, 'black')

    def _add_label(self, text: str, color: str) -> None:
        """Add one wrapped label to the content area."""
        label = tk.Label(self._content, text=text, fg=color,
                         wraplength=WRAP_LENGTH, justify='left')
        label.pack(anchor='w', pady=4)

    def _add_buttons(self, on_ok: Callable[[], None],
                     on_default: Optional[Callable[[], None]]) -> None:
        """Add the confirm, optional default, and cancel buttons."""
        box = tk.Frame(self._content)
        box.pack(anchor='w', pady=10)
        ok_button = tk.Button(box, text='OK', command=on_ok)
        ok_button.pack(side='left')
        if on_default is not None:
            default_button = tk.Button(box, text='Use default',
                                       command=on_default)
            default_button.pack(side='left', padx=6)
        cancel_button = tk.Button(box, text='Cancel', command=self._cancel)
        cancel_button.pack(side='left', padx=6)

    def _wait(self) -> object:
        """Block until the current prompt is answered or cancelled."""
        self._win.wait_variable(self._done)
        if self._cancelled:
            raise EOFError(CANCEL_TEXT)
        return self._result

    def _finish(self, value: object) -> None:
        """Store the answer and release the waiting prompt."""
        self._result = value
        self._done.set(self._done.get() + 1)

    def _cancel(self) -> None:
        """Mark the session cancelled and release the waiting prompt."""
        self._cancelled = True
        self._done.set(self._done.get() + 1)


class TkWizardBridge(YesNoUiBridge):
    """Bridge that answers wizard prompts in one reused Tkinter window."""

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __init__(self, parent: tk.Misc, log: Optional[TextIO] = None,
                 ask_fn: Optional[Callable[
                     [str, Optional[str], Optional[Sequence[str]]],
                     str | int]] = None,
                 show_fn: Optional[Callable[[str], None]] = None,
                 yes_no_fn: Optional[Callable[[str, bool], bool]] = None
                 ) -> None:
        """Store the parent window, log sink, and optional test callables.

        Args:
            parent: The window the wizard window is shown over.
            log: Stream that receives low-level wizard diagnostics.
            ask_fn: Replacement for the question prompt, used by tests.
            show_fn: Replacement for the message display, used by tests.
            yes_no_fn: Replacement for the yes/no prompt, used by tests.
        """
        self._parent = parent
        self._log = log
        self._window: Optional[_WizardWindow] = None
        self._ask = ask_fn
        self._show = show_fn
        self._yes_no = yes_no_fn

    def ask(self, question: str, re_ask_reason: Optional[str] = None,
            choices: Optional[Sequence[str]] = None) -> str | int:
        """Ask one question and return the user's answer.

        Returns the entered text, the zero-based index of a selected
        choice, or an empty string when the user requests the default.

        Raises:
            EOFError: The user cancelled the wizard.
        """
        if self._ask is not None:
            return self._ask(question, re_ask_reason, choices)
        return self._window_obj().ask(question, re_ask_reason, choices)

    def ask_yes_no(self, question: str, default: bool) -> bool:
        """Ask one yes/no question with dedicated buttons."""
        if self._yes_no is not None:
            return self._yes_no(question, default)
        return self._window_obj().ask_yes_no(question, default)

    def show(self, message: str) -> None:
        """Show an informational message to the user."""
        if self._show is not None:
            self._show(message)
            return
        self._window_obj().show(message)

    def error_file(self) -> TextIO:
        """Return the stream used for low-level wizard diagnostics."""
        return self._log if self._log is not None else NoTextIO()

    def close(self) -> None:
        """Close the wizard window when one was opened."""
        if self._window is not None:
            self._window.close()
            self._window = None

    def _window_obj(self) -> _WizardWindow:
        """Return the wizard window, creating it on first use."""
        if self._window is None:
            self._window = _WizardWindow(self._parent)
        return self._window
