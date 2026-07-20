#! /usr/local/bin/python3
"""Tests for the encrypt-token dialog and its request dataclass.

The dialog gathers a typed token or a clear text token file, the encrypted
output file and a pass phrase entered twice. The tests cover a typed token
winning over a file, a file used when no token is typed, whitespace being
stripped, each validation problem being reported, the Browse buttons
filling their fields, and the ask_encrypt_token wrapper on a cancelled and
a confirmed dialog.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Callable, Optional, cast
import tkinter as tk
import pytest
from backlogops_gui import token_dialog
from backlogops_gui.token_dialog import (
    EncryptTokenDialog, EncryptTokenRequest, ask_encrypt_token)
from backlogops_gui.modal_dialog import ModalDialog
from .gui_test_helpers import MsgRecorder, gui_root
from .dialog_test_helpers import cancel_show, no_wait

MESSAGEBOX = 'backlogops_gui.token_dialog.messagebox'
OPEN_DIALOG = 'backlogops_gui.token_dialog.filedialog.askopenfilename'
SAVE_DIALOG = 'backlogops_gui.token_dialog.filedialog.asksaveasfilename'


def _fill(dialog: EncryptTokenDialog, values: dict[str, str]) -> None:
    """Set the dialog's input variables from a field-name to value map."""
    # pylint: disable-next=protected-access
    dialog._token.set(values.get('token', ''))
    # pylint: disable-next=protected-access
    dialog._clear.set(values.get('clear', ''))
    # pylint: disable-next=protected-access
    dialog._out.set(values.get('out', ''))
    # pylint: disable-next=protected-access
    dialog._phrase.set(values.get('phrase', ''))
    # pylint: disable-next=protected-access
    dialog._confirm_phrase.set(values.get('confirm', ''))


def _confirm(dialog: EncryptTokenDialog) -> None:
    """Invoke the dialog's OK handler."""
    # pylint: disable-next=protected-access
    dialog._confirm()


def _problem(dialog: EncryptTokenDialog) -> Optional[tuple[str, str]]:
    """Return the dialog's first validation problem, if any."""
    # pylint: disable-next=protected-access
    return dialog._problem()


def _clear_text(dialog: EncryptTokenDialog) -> str:
    """Return the clear text file field of the dialog."""
    # pylint: disable-next=protected-access
    return dialog._clear.get()


def _out_text(dialog: EncryptTokenDialog) -> str:
    """Return the encrypted output file field of the dialog."""
    # pylint: disable-next=protected-access
    return dialog._out.get()


def _fake_dialog(cancelled: bool, request: Optional[EncryptTokenRequest]
                 ) -> Callable[[object], object]:
    """Return an EncryptTokenDialog stand-in with a fixed result."""
    # pylint: disable-next=too-few-public-methods
    class _Dialog:
        """Stand-in dialog exposing the fixed cancelled flag and request."""

        def __init__(self, parent: object) -> None:
            """Accept the parent the wrapper passes in."""
            assert parent is not None
            self.cancelled = cancelled
            self.request = request
    return _Dialog


def test_request_fields() -> None:
    """Test the request dataclass holds token, file, output and phrase."""
    request = EncryptTokenRequest('tok', None, Path('out.enc'), 'pw')
    assert request.token == 'tok'
    assert request.clear_file is None
    assert request.out_file == Path('out.enc')
    assert request.passphrase == 'pw'


def test_typed_token_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a typed token is used and its clear text file is ignored."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = EncryptTokenDialog(root)
        _fill(dialog, {'token': '  tok  ', 'clear': 'clear.txt',
                       'out': 'o.enc', 'phrase': 'pw', 'confirm': 'pw'})
        _confirm(dialog)
        assert dialog.request == EncryptTokenRequest('tok', None,
                                                     Path('o.enc'), 'pw')


def test_file_when_no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the clear text file is used when no token is typed."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = EncryptTokenDialog(root)
        _fill(dialog, {'clear': 'clear.txt', 'out': 'o.enc', 'phrase': 'pw',
                       'confirm': 'pw'})
        _confirm(dialog)
        assert dialog.request == EncryptTokenRequest(None, Path('clear.txt'),
                                                     Path('o.enc'), 'pw')


_PROBLEMS = [
    ({'out': 'o', 'phrase': 'pw', 'confirm': 'pw'}, 'No token'),
    ({'token': 'tok', 'phrase': 'pw', 'confirm': 'pw'}, 'No output file'),
    ({'token': 'tok', 'out': 'o', 'confirm': 'pw'}, 'No pass phrase'),
    ({'token': 'tok', 'out': 'o', 'phrase': 'pw', 'confirm': 'no'},
     'Pass phrases differ')]


@pytest.mark.parametrize('values,title', _PROBLEMS)
def test_problem_cases(values: dict[str, str], title: str,
                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Test each invalid combination reports the matching problem title."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = EncryptTokenDialog(root)
        _fill(dialog, values)
        problem = _problem(dialog)
        assert problem is not None and problem[0] == title


def test_confirm_reports(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a validation problem is shown and stores no request."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    recorder = MsgRecorder()
    monkeypatch.setattr(MESSAGEBOX, recorder)
    with gui_root() as root:
        dialog = EncryptTokenDialog(root)
        _fill(dialog, {'out': 'o.enc', 'phrase': 'pw', 'confirm': 'pw'})
        _confirm(dialog)
        assert dialog.request is None
        assert recorder.calls == [('No token', 'Enter the API token or '
                                   'choose a clear text token file.')]


def test_browse_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the clear-file Browse button fills the clear text file field."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(OPEN_DIALOG, lambda **_kw: 'chosen.txt')
    with gui_root() as root:
        dialog = EncryptTokenDialog(root)
        # pylint: disable-next=protected-access
        dialog._browse_clear()
        assert _clear_text(dialog) == 'chosen.txt'


def test_browse_out(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the output Browse button fills the encrypted file field."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(SAVE_DIALOG, lambda **_kw: 'chosen.enc')
    with gui_root() as root:
        dialog = EncryptTokenDialog(root)
        # pylint: disable-next=protected-access
        dialog._browse_out()
        assert _out_text(dialog) == 'chosen.enc'


def test_browse_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the Browse dialog leaves the field unchanged."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(OPEN_DIALOG, lambda **_kw: '')
    with gui_root() as root:
        dialog = EncryptTokenDialog(root)
        _fill(dialog, {'clear': 'keep.txt'})
        # pylint: disable-next=protected-access
        dialog._browse_clear()
        assert _clear_text(dialog) == 'keep.txt'


def test_browse_out_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the output Browse dialog leaves the field unchanged."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(SAVE_DIALOG, lambda **_kw: '')
    with gui_root() as root:
        dialog = EncryptTokenDialog(root)
        _fill(dialog, {'out': 'keep.enc'})
        # pylint: disable-next=protected-access
        dialog._browse_out()
        assert _out_text(dialog) == 'keep.enc'


def test_ask_cancelled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the wrapper returns None when the dialog is cancelled."""
    monkeypatch.setattr(token_dialog, 'EncryptTokenDialog',
                        _fake_dialog(True, None))
    assert ask_encrypt_token(cast(tk.Misc, object())) is None


def test_ask_returns_request(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the wrapper returns the request of a confirmed dialog."""
    request = EncryptTokenRequest('tok', None, Path('o.enc'), 'pw')
    monkeypatch.setattr(token_dialog, 'EncryptTokenDialog',
                        _fake_dialog(False, request))
    assert ask_encrypt_token(cast(tk.Misc, object())) is request


def test_ask_cancel_real(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a real dialog cancelled through its close path yields None."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_encrypt_token(root) is None
