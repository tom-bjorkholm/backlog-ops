#! /usr/local/bin/python3
"""Modal dialog collecting what is needed to encrypt a Jira token file.

The dialog gathers the clear text Jira API token, either typed directly or
read from a clear text file, the encrypted file to write, and a pass phrase
entered twice so the two entries can be confirmed to match. The typed token
wins when both a token and a clear text file are given. The token field is
shown in the clear so a pasted token can be checked, while the two pass
phrase fields are masked. The gathered values are returned as an
:class:`EncryptTokenRequest`, or None when the user cancels; performing the
encryption is left to the caller.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import filedialog, messagebox
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
from backlogops_gui.gui_style import style_input
from backlogops_gui.modal_dialog import ModalDialog


@dataclass
class EncryptTokenRequest:
    """The token source, output file and pass phrase to encrypt with.

    Exactly one of ``token`` and ``clear_file`` is set: ``token`` holds a
    token typed into the dialog, ``clear_file`` a clear text token file to
    read the token from instead.
    """

    token: Optional[str]
    clear_file: Optional[Path]
    out_file: Path
    passphrase: str


# pylint: disable-next=too-few-public-methods
class EncryptTokenDialog(ModalDialog):
    """Modal dialog collecting the token, output file and pass phrase."""

    def __init__(self, parent: tk.Misc) -> None:
        """Build, show and wait for the encrypt-token dialog."""
        super().__init__(parent, 'Encrypt Jira API token file')
        self.request: Optional[EncryptTokenRequest] = None
        self._token = tk.StringVar(self._win)
        self._clear = tk.StringVar(self._win)
        self._out = tk.StringVar(self._win)
        self._phrase = tk.StringVar(self._win)
        self._confirm_phrase = tk.StringVar(self._win)
        self._build()
        self._show()

    def _build(self) -> None:
        """Add the token, file, output and pass phrase inputs."""
        self._add_line('Jira API token (leave blank to use a file):',
                       self._token)
        self._add_file_row('Clear text token file (used only if no token):',
                           self._clear, self._browse_clear)
        self._add_file_row('Encrypted token file to write:', self._out,
                           self._browse_out)
        self._add_line('Pass phrase:', self._phrase, secret=True)
        self._add_line('Confirm pass phrase:', self._confirm_phrase,
                       secret=True)

    def _add_line(self, label: str, var: tk.StringVar, *,
                  secret: bool = False) -> None:
        """Add a label and a single-line entry, masked when ``secret``."""
        tk.Label(self._win, text=label).pack(anchor='w', padx=12, pady=(8, 2))
        entry = tk.Entry(self._win, textvariable=var, width=44,
                         show='*' if secret else '')
        style_input(entry)
        entry.pack(anchor='w', padx=12, fill='x')

    def _add_file_row(self, label: str, var: tk.StringVar,
                      browse: Callable[[], None]) -> None:
        """Add a label, a path entry and a Browse button for a file path."""
        tk.Label(self._win, text=label).pack(anchor='w', padx=12, pady=(8, 2))
        row = tk.Frame(self._win)
        row.pack(anchor='w', padx=12, fill='x')
        entry = tk.Entry(row, textvariable=var, width=34)
        style_input(entry)
        entry.pack(side='left', fill='x', expand=True)
        tk.Button(row, text='Browse…', command=browse).pack(side='left',
                                                            padx=4)

    def _browse_clear(self) -> None:
        """Fill the clear text file field from an open-file dialog."""
        name = filedialog.askopenfilename(parent=self._win,
                                          title='Clear text token file')
        if name:
            self._clear.set(name)

    def _browse_out(self) -> None:
        """Fill the encrypted file field from a save-file dialog."""
        name = filedialog.asksaveasfilename(parent=self._win,
                                            title='Encrypted token file')
        if name:
            self._out.set(name)

    def _confirm(self) -> None:
        """Validate the inputs and store the request, or report a problem."""
        problem = self._problem()
        if problem is not None:
            messagebox.showerror(problem[0], problem[1], parent=self._win)
            return
        self.request = self._make_request()
        super()._confirm()

    def _problem(self) -> Optional[tuple[str, str]]:
        """Return a (title, message) for the first invalid input, or None."""
        if not self._token.get().strip() and not self._clear.get().strip():
            return ('No token', 'Enter the API token or choose a clear text '
                    'token file.')
        if not self._out.get().strip():
            return ('No output file',
                    'Choose the encrypted token file to write.')
        if not self._phrase.get():
            return ('No pass phrase', 'Enter a pass phrase.')
        if self._phrase.get() != self._confirm_phrase.get():
            return ('Pass phrases differ', 'The two pass phrases do not '
                    'match.')
        return None

    def _make_request(self) -> EncryptTokenRequest:
        """Build the request from the validated inputs; typed token wins."""
        token = self._token.get().strip()
        clear = self._clear.get().strip()
        return EncryptTokenRequest(token if token else None,
                                   None if token else Path(clear),
                                   Path(self._out.get().strip()),
                                   self._phrase.get())


def ask_encrypt_token(parent: tk.Misc) -> Optional[EncryptTokenRequest]:
    """Ask for the token, output file and pass phrase; None if cancelled."""
    dialog = EncryptTokenDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.request
