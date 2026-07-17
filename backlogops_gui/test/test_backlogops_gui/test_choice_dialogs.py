#! /usr/local/bin/python3
"""Tests for the shared button-choice dialog and its ask wrappers.

The generic :class:`ButtonChoiceDialog` records the value of the pressed
button and keeps the default when the window is dismissed. The three
wrappers build it with their own options and defaults.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
import pytest
from backlogops_gui import choice_dialogs
from backlogops_gui.choice_dialogs import (
    ButtonChoiceDialog, ConfigChoice, SourceChoice, ask_no_config_choice,
    ask_preset_kind, ask_source_choice)
from .gui_test_helpers import CloseSpy, gui_root

_OPTIONS = [('First', ConfigChoice.WIZARD), ('Second', ConfigChoice.LOAD)]


def _no_wait(self: ButtonChoiceDialog[ConfigChoice]) -> None:
    """Stand in for the modal show without grabbing or waiting."""
    assert self is not None


def _dialog(parent: tk.Misc) -> ButtonChoiceDialog[ConfigChoice]:
    """Return a button-choice dialog whose show does not block."""
    return ButtonChoiceDialog(parent, 'Title', 'Explain', _OPTIONS,
                              ConfigChoice.EXIT)


@pytest.mark.parametrize('value', [ConfigChoice.WIZARD, ConfigChoice.LOAD])
def test_button_records(monkeypatch: pytest.MonkeyPatch,
                        value: ConfigChoice) -> None:
    """Test choosing a button records its value on the dialog."""
    monkeypatch.setattr(ButtonChoiceDialog, '_show', _no_wait)
    with gui_root() as root:
        dialog = _dialog(root)
        # pylint: disable-next=protected-access
        dialog._choose(value)
        assert dialog.choice is value


def test_default_on_dismiss(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test closing without a button keeps the default choice."""
    monkeypatch.setattr(ButtonChoiceDialog, '_show', _no_wait)
    with gui_root() as root:
        assert _dialog(root).choice is ConfigChoice.EXIT


def test_frame_parent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the dialog builds over a non-window parent."""
    monkeypatch.setattr(ButtonChoiceDialog, '_show', _no_wait)
    with gui_root() as root:
        frame = tk.Frame(root)
        assert _dialog(frame).choice is ConfigChoice.EXIT


def test_binds_close(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the dialog binds Cmd-W to close itself."""
    spy = CloseSpy()
    monkeypatch.setattr(choice_dialogs, 'bind_close', spy)
    monkeypatch.setattr(ButtonChoiceDialog, '_show', _no_wait)
    with gui_root() as root:
        dialog = _dialog(root)
        # pylint: disable-next=protected-access
        assert spy.calls == [(dialog._win, None)]


# pylint: disable-next=too-few-public-methods
class _AutoChoice(ButtonChoiceDialog[ConfigChoice]):
    """Dialog that picks the first option once shown, for coverage."""

    def _show(self) -> None:
        """Schedule the wizard choice and run the real modal show."""
        self._win.after(0, lambda: self._choose(ConfigChoice.WIZARD))
        super()._show()


def test_show_real() -> None:
    """Test the real modal show waits and returns the picked choice."""
    with gui_root() as root:
        auto = _AutoChoice(root, 'Title', 'Explain', _OPTIONS,
                           ConfigChoice.EXIT)
        assert auto.choice is ConfigChoice.WIZARD


def test_ask_no_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the no-config wrapper returns its default when dismissed."""
    monkeypatch.setattr(ButtonChoiceDialog, '_show', _no_wait)
    with gui_root() as root:
        assert ask_no_config_choice(root) is ConfigChoice.EXIT


def test_ask_preset_kind(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the preset-kind wrapper returns None when dismissed."""
    monkeypatch.setattr(ButtonChoiceDialog, '_show', _no_wait)
    with gui_root() as root:
        assert ask_preset_kind(root) is None


def test_ask_source(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the source wrapper returns cancel when dismissed."""
    monkeypatch.setattr(ButtonChoiceDialog, '_show', _no_wait)
    with gui_root() as root:
        assert ask_source_choice(root, 'Wiz', 'Explain') \
            is SourceChoice.CANCEL
