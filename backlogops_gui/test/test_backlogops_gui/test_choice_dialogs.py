#! /usr/local/bin/python3
"""Tests for the no-configuration and preset-kind choice dialogs."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
import pytest
from backlogops_gui.choice_dialogs import (
    ConfigChoice, NoConfigDialog, PresetKind, PresetKindDialog,
    ask_no_config_choice, ask_preset_kind)
from .gui_test_helpers import gui_root


def _no_config_wait(self: NoConfigDialog) -> None:
    """Stand in for the no-config show without grabbing or waiting."""
    assert self is not None


@pytest.mark.parametrize('choice', [
    ConfigChoice.WIZARD, ConfigChoice.LOAD, ConfigChoice.EXIT])
def test_no_config_choice(monkeypatch: pytest.MonkeyPatch,
                          choice: ConfigChoice) -> None:
    """Test each button records its choice in the no-config dialog."""
    monkeypatch.setattr(NoConfigDialog, '_show', _no_config_wait)
    with gui_root() as root:
        dialog = NoConfigDialog(root)
        # pylint: disable-next=protected-access
        dialog._choose(choice)
        assert dialog.choice is choice


def test_no_config_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the no-config dialog over a non-window parent defaults to exit."""
    monkeypatch.setattr(NoConfigDialog, '_show', _no_config_wait)
    with gui_root() as root:
        frame = tk.Frame(root)
        assert NoConfigDialog(frame).choice is ConfigChoice.EXIT


# pylint: disable-next=too-few-public-methods
class _AutoNoConfig(NoConfigDialog):
    """No-config dialog that picks the wizard once shown, for coverage."""

    def _show(self) -> None:
        """Schedule a wizard choice and run the real modal show."""
        self._win.after(0, lambda: self._choose(ConfigChoice.WIZARD))
        super()._show()


def test_no_config_show_real() -> None:
    """Test the real no-config show waits and returns the picked choice."""
    with gui_root() as root:
        assert _AutoNoConfig(root).choice is ConfigChoice.WIZARD


def test_ask_no_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the ask wrapper returns the dialog's recorded choice."""
    monkeypatch.setattr(NoConfigDialog, '_show', _no_config_wait)
    with gui_root() as root:
        assert ask_no_config_choice(root) is ConfigChoice.EXIT


def _kind_wait(self: PresetKindDialog) -> None:
    """Stand in for the preset-kind show without grabbing or waiting."""
    assert self is not None


@pytest.mark.parametrize('kind', [PresetKind.INPUT, PresetKind.OUTPUT])
def test_preset_kind_choice(monkeypatch: pytest.MonkeyPatch,
                            kind: PresetKind) -> None:
    """Test each button records its kind in the preset-kind dialog."""
    monkeypatch.setattr(PresetKindDialog, '_show', _kind_wait)
    with gui_root() as root:
        dialog = PresetKindDialog(root)
        # pylint: disable-next=protected-access
        dialog._choose(kind)
        assert dialog.kind is kind


def test_preset_kind_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a closed preset-kind dialog over a frame chooses nothing."""
    monkeypatch.setattr(PresetKindDialog, '_show', _kind_wait)
    with gui_root() as root:
        frame = tk.Frame(root)
        assert PresetKindDialog(frame).kind is None


# pylint: disable-next=too-few-public-methods
class _AutoPresetKind(PresetKindDialog):
    """Preset-kind dialog that picks input once shown, for coverage."""

    def _show(self) -> None:
        """Schedule an input choice and run the real modal show."""
        self._win.after(0, lambda: self._choose(PresetKind.INPUT))
        super()._show()


def test_kind_show_real() -> None:
    """Test the real preset-kind show waits and returns the picked kind."""
    with gui_root() as root:
        assert _AutoPresetKind(root).kind is PresetKind.INPUT


def test_ask_preset_kind(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the ask wrapper returns the dialog's recorded kind."""
    monkeypatch.setattr(PresetKindDialog, '_show', _kind_wait)
    with gui_root() as root:
        assert ask_preset_kind(root) is None
