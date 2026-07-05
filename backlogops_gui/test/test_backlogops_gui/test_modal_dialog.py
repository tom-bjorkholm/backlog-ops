#! /usr/local/bin/python3
"""Tests for the shared modal dialog base show behavior."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from backlogops_gui.backlog_dialogs import BufferDialog
from .gui_test_helpers import gui_root


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
