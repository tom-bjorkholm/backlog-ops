#! /usr/local/bin/python3
"""Shared helpers for the modal option-dialog tests.

The dialogs block in a modal loop, so the tests replace the modal show
with a stand-in that either does nothing, cancels at once, or confirms at
once. Patching the show on the shared :class:`ModalDialog` base affects
every dialog that inherits it.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from backlogops_gui.modal_dialog import ModalDialog


def no_wait(self: ModalDialog) -> None:
    """Stand in for the modal show without grabbing or waiting."""
    assert self is not None


def cancel_show(self: ModalDialog) -> None:
    """Stand in for the modal show that cancels at once."""
    # pylint: disable-next=protected-access
    self._cancel()


def confirm_show(self: ModalDialog) -> None:
    """Stand in for the modal show that confirms at once."""
    # pylint: disable-next=protected-access
    self._confirm()
