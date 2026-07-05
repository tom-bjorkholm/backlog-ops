#! /usr/local/bin/python3
"""Tests for the shared modal dialog base show behavior."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import pytest
from backlogops_gui import modal_dialog
from backlogops_gui.backlog_dialogs import BufferDialog
from .dialog_test_helpers import no_wait
from .gui_test_helpers import CloseSpy, gui_root


# pylint: disable-next=too-few-public-methods
class _AutoBuffer(BufferDialog):
    """Buffer dialog that confirms itself once shown, for show coverage."""

    def _show(self) -> None:
        """Schedule a confirm and run the real modal show."""
        self._win.after(0, self._confirm)
        super()._show()


def test_modal_show_real() -> None:
    """Test the real modal show builds the buttons and waits for a close."""
    with gui_root() as root:
        dialog = _AutoBuffer(root)
        assert dialog.days == 5


def test_binds_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a modal dialog binds Cmd-W to its cancel action."""
    spy = CloseSpy()
    monkeypatch.setattr(modal_dialog, 'bind_close', spy)
    monkeypatch.setattr(BufferDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = BufferDialog(root)
        # pylint: disable-next=protected-access
        assert spy.calls == [(dialog._win, dialog._cancel)]
