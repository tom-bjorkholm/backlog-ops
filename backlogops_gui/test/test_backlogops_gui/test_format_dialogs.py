#! /usr/local/bin/python3
"""Tests for the read/write file-format option dialogs."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Optional
import pytest
from backlogops_gui.format_dialogs import (
    MODE_FILE, MODE_INFER, MODE_PRESET, FormatDialog, ReadOptions,
    WriteOptions, ask_read_options, ask_write_options, format_value)
from backlogops_gui.modal_dialog import ModalDialog
from .gui_test_helpers import gui_root
from .dialog_test_helpers import cancel_show, no_wait


@pytest.mark.parametrize('mode,preset,path,expected', [
    (MODE_INFER, 'preset', 'file.csv', None),
    (MODE_PRESET, 'preset', '', 'preset'),
    (MODE_PRESET, '', '', None),
    (MODE_FILE, '', 'cfg.json', 'cfg.json'),
    (MODE_FILE, '', '', None)])
def test_format_value(mode: int, preset: str, path: str,
                      expected: Optional[str]) -> None:
    """Test the selected mode maps to the right resolver value."""
    assert format_value(mode, preset, path) == expected


def test_format_options() -> None:
    """Test the format option dataclasses hold the entered selection."""
    assert ReadOptions(None).config_value is None
    write = WriteOptions('preset', True)
    assert write.config_value == 'preset'
    assert write.releases_first is True


def test_fmt_preset(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the format dialog returns a chosen preset and ordering."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = FormatDialog(root, ['p1', 'p2'], True)
        # pylint: disable-next=protected-access
        dialog._mode.set(MODE_PRESET)
        # pylint: disable-next=protected-access
        dialog._preset.set('p2')
        # pylint: disable-next=protected-access
        dialog._rel_first.set(True)
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.value == 'p2'
        assert dialog.releases_first is True


def test_fmt_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the format dialog returns a chosen configuration file."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = FormatDialog(root, ['p1'], False)
        # pylint: disable-next=protected-access
        dialog._mode.set(MODE_FILE)
        # pylint: disable-next=protected-access
        dialog._path.set('cfg.json')
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.value == 'cfg.json'


def test_fmt_infer(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the format dialog over a non-window parent infers the format."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        frame = tk.Frame(root)
        dialog = FormatDialog(frame, [], False)
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.value is None


def test_fmt_browse(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test browsing selects a file and switches to the file mode."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    target = 'backlogops_gui.format_dialogs.filedialog.askopenfilename'
    monkeypatch.setattr(target, lambda **kw: 'chosen.cfg')
    with gui_root() as root:
        dialog = FormatDialog(root, ['p1'], False)
        # pylint: disable-next=protected-access
        dialog._browse()
        # pylint: disable-next=protected-access
        assert dialog._path.get() == 'chosen.cfg'
        # pylint: disable-next=protected-access
        assert dialog._mode.get() == MODE_FILE


def test_fmt_browse_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the browse leaves the path unchanged."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    target = 'backlogops_gui.format_dialogs.filedialog.askopenfilename'
    monkeypatch.setattr(target, lambda **kw: '')
    with gui_root() as root:
        dialog = FormatDialog(root, ['p1'], False)
        # pylint: disable-next=protected-access
        dialog._browse()
        # pylint: disable-next=protected-access
        assert dialog._path.get() == ''


def test_ask_read_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a confirmed read dialog returns read options."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        assert isinstance(ask_read_options(root, ['p']), ReadOptions)


def test_ask_read_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled read dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_read_options(root, None) is None


def test_ask_write_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a confirmed write dialog returns write options."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        assert isinstance(ask_write_options(root, None), WriteOptions)


def test_ask_write_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled write dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_write_options(root, None) is None
