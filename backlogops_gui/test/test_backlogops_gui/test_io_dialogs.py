#! /usr/local/bin/python3
"""Tests for the format-value mapping and option dataclasses."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from datetime import date
from typing import Callable, Optional
import pytest
from backlogops import DependencyMode
from backlogops_gui.io_dialogs import (
    MODE_FILE, MODE_INFER, MODE_PRESET, ConfigChoice, DepOptions, ReadOptions,
    StartChoice, WriteOptions, format_value)
from backlogops_gui.io_dialogs import (
    _BufferDialog, _DepOptionsDialog, _FormatDialog, _KeysDialog,
    _LevelsDialog, _ModalDialog, _NoConfigDialog, _StartDateDialog)
from backlogops_gui.io_dialogs import (
    ask_buffer_days, ask_dep_options, ask_keys, ask_levels,
    ask_no_config_choice, ask_read_options, ask_start_date, ask_write_options,
    choose_changes_output, choose_config_file, choose_existing_config,
    choose_input_file, choose_key_list_output, choose_output_file,
    show_change_list)
from backlogops.no_text_io import NoTextIO


def _root_or_skip() -> tk.Tk:
    """Return a withdrawn Tk root, or skip when no display is available."""
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip('no display available')
    root.withdraw()
    return root


def _no_wait(self: _ModalDialog) -> None:
    """Stand in for the modal show without grabbing or waiting."""
    assert self is not None


class _MsgRec:
    """Record message-box error calls raised by a dialog."""

    def __init__(self) -> None:
        """Start with an empty record of error calls."""
        self.calls: list[tuple[str, str]] = []

    def showerror(self, title: str, message: str, parent: object) -> None:
        """Record a shown error message."""
        assert parent is not None
        self.calls.append((title, message))


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


def test_option_dataclasses() -> None:
    """Test the option dataclasses hold the entered selection."""
    assert ReadOptions(None).config_value is None
    write = WriteOptions('preset', True)
    assert write.config_value == 'preset'
    assert write.releases_first is True


def test_action_dataclasses() -> None:
    """Test the action dataclasses hold the entered selection."""
    options = DepOptions(True, DependencyMode.EARLY, ['A'])
    assert options.later is True
    assert options.mode is DependencyMode.EARLY
    assert options.space_around == ['A']
    assert StartChoice(None).start_date is None
    assert StartChoice(date(2026, 6, 15)).start_date == date(2026, 6, 15)


def _cancel_show(self: _ModalDialog) -> None:
    """Stand in for the modal show that cancels at once."""
    self._cancel()


CHOOSERS: list[tuple[Callable[[tk.Misc], Optional[str]], str]] = [
    (choose_input_file, 'askopenfilename'),
    (choose_output_file, 'asksaveasfilename'),
    (choose_config_file, 'asksaveasfilename'),
    (choose_existing_config, 'askopenfilename'),
    (choose_key_list_output, 'asksaveasfilename'),
    (choose_changes_output, 'asksaveasfilename')]
"""Each file chooser paired with the file dialog it calls."""


@pytest.mark.parametrize('func, dialog_name', CHOOSERS)
def test_choosers(monkeypatch: pytest.MonkeyPatch,
                  func: Callable[[tk.Misc], Optional[str]],
                  dialog_name: str) -> None:
    """Test a chooser returns the picked name, or None when cancelled."""
    root = _root_or_skip()
    target = f'backlogops_gui.io_dialogs.filedialog.{dialog_name}'
    try:
        monkeypatch.setattr(target, lambda **kw: 'picked.csv')
        assert func(root) == 'picked.csv'
        monkeypatch.setattr(target, lambda **kw: '')
        assert func(root) is None
    finally:
        root.destroy()


def test_fmt_preset(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the format dialog returns a chosen preset and ordering."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        dialog = _FormatDialog(root, ['p1', 'p2'], True)
        dialog._mode.set(MODE_PRESET)
        dialog._preset.set('p2')
        dialog._rel_first.set(True)
        dialog._confirm()
        assert dialog.value == 'p2'
        assert dialog.releases_first is True
    finally:
        root.destroy()


def test_fmt_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the format dialog returns a chosen configuration file."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        dialog = _FormatDialog(root, ['p1'], False)
        dialog._mode.set(MODE_FILE)
        dialog._path.set('cfg.json')
        dialog._confirm()
        assert dialog.value == 'cfg.json'
    finally:
        root.destroy()


def test_fmt_infer(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the format dialog over a non-window parent infers the format."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        frame = tk.Frame(root)
        dialog = _FormatDialog(frame, [], False)
        dialog._confirm()
        assert dialog.value is None
    finally:
        root.destroy()


def test_fmt_browse(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test browsing selects a file and switches to the file mode."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    target = 'backlogops_gui.io_dialogs.filedialog.askopenfilename'
    monkeypatch.setattr(target, lambda **kw: 'chosen.cfg')
    root = _root_or_skip()
    try:
        dialog = _FormatDialog(root, ['p1'], False)
        dialog._browse()
        assert dialog._path.get() == 'chosen.cfg'
        assert dialog._mode.get() == MODE_FILE
    finally:
        root.destroy()


def test_fmt_browse_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the browse leaves the path unchanged."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    target = 'backlogops_gui.io_dialogs.filedialog.askopenfilename'
    monkeypatch.setattr(target, lambda **kw: '')
    root = _root_or_skip()
    try:
        dialog = _FormatDialog(root, ['p1'], False)
        dialog._browse()
        assert dialog._path.get() == ''
    finally:
        root.destroy()


def test_ask_read_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a confirmed read dialog returns read options."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        assert isinstance(ask_read_options(root, ['p']), ReadOptions)
    finally:
        root.destroy()


def test_ask_read_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled read dialog returns nothing."""
    monkeypatch.setattr(_ModalDialog, '_show', _cancel_show)
    root = _root_or_skip()
    try:
        assert ask_read_options(root, None) is None
    finally:
        root.destroy()


def test_ask_write_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a confirmed write dialog returns write options."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        assert isinstance(ask_write_options(root, None), WriteOptions)
    finally:
        root.destroy()


def test_ask_write_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled write dialog returns nothing."""
    monkeypatch.setattr(_ModalDialog, '_show', _cancel_show)
    root = _root_or_skip()
    try:
        assert ask_write_options(root, None) is None
    finally:
        root.destroy()


def test_buffer_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the buffer dialog returns a valid number of days."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        dialog = _BufferDialog(root)
        dialog._text.set('3')
        dialog._confirm()
        assert dialog.days == 3
    finally:
        root.destroy()


@pytest.mark.parametrize('text', ['x', '-1'])
def test_buffer_bad(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    """Test a non-numeric or negative buffer is rejected with an error."""
    rec = _MsgRec()
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    monkeypatch.setattr('backlogops_gui.io_dialogs.messagebox', rec)
    root = _root_or_skip()
    try:
        dialog = _BufferDialog(root)
        dialog._text.set(text)
        dialog._confirm()
        assert dialog.days is None
        assert len(rec.calls) == 1
    finally:
        root.destroy()


def test_ask_buffer_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled buffer dialog returns nothing."""
    monkeypatch.setattr(_ModalDialog, '_show', _cancel_show)
    root = _root_or_skip()
    try:
        assert ask_buffer_days(root) is None
    finally:
        root.destroy()


def test_ask_wrappers_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test each ask wrapper returns the dialog result when confirmed."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        assert ask_buffer_days(root) is None
        assert ask_keys(root, NoTextIO()) is None
        assert ask_dep_options(root) is None
        assert ask_start_date(root) is None
        assert ask_levels(root) is None
    finally:
        root.destroy()


def test_keys_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the keys dialog splits the entered text into keys."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        dialog = _KeysDialog(root, NoTextIO())
        dialog._text.insert('1.0', 'A B\nC')
        dialog._confirm()
        assert dialog.keys == ['A', 'B', 'C']
    finally:
        root.destroy()


def test_keys_load_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading keys from a file fills the text box."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    target = 'backlogops_gui.io_dialogs.filedialog.askopenfilename'
    monkeypatch.setattr(target, lambda **kw: 'keys.txt')
    reader = 'backlogops_gui.io_dialogs.read_key_list'
    monkeypatch.setattr(reader, lambda name, stderr_file: ['X', 'Y'])
    root = _root_or_skip()
    try:
        dialog = _KeysDialog(root, NoTextIO())
        dialog._load()
        assert dialog._text.get('1.0', 'end').split() == ['X', 'Y']
    finally:
        root.destroy()


def test_keys_load_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the load leaves the text box empty."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    target = 'backlogops_gui.io_dialogs.filedialog.askopenfilename'
    monkeypatch.setattr(target, lambda **kw: '')
    root = _root_or_skip()
    try:
        dialog = _KeysDialog(root, NoTextIO())
        dialog._load()
        assert dialog._text.get('1.0', 'end').strip() == ''
    finally:
        root.destroy()


def test_keys_load_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a key-list read failure is reported and loads nothing."""
    def boom(name: str, stderr_file: object) -> list[str]:
        raise ValueError('bad list')
    rec = _MsgRec()
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    target = 'backlogops_gui.io_dialogs.filedialog.askopenfilename'
    monkeypatch.setattr(target, lambda **kw: 'keys.txt')
    monkeypatch.setattr('backlogops_gui.io_dialogs.read_key_list', boom)
    monkeypatch.setattr('backlogops_gui.io_dialogs.messagebox', rec)
    root = _root_or_skip()
    try:
        dialog = _KeysDialog(root, NoTextIO())
        dialog._load()
        assert dialog._text.get('1.0', 'end').strip() == ''
        assert rec.calls == [('Could not read key list', 'bad list')]
    finally:
        root.destroy()


def test_ask_keys_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled keys dialog returns nothing."""
    monkeypatch.setattr(_ModalDialog, '_show', _cancel_show)
    root = _root_or_skip()
    try:
        assert ask_keys(root, NoTextIO()) is None
    finally:
        root.destroy()


def test_dep_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the dependency dialog keeps an empty space list as None."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        dialog = _DepOptionsDialog(root)
        dialog._confirm()
        assert dialog.options is not None
        assert dialog.options.space_around is None
        assert dialog.options.mode is DependencyMode.KEEP
    finally:
        root.destroy()


def test_dep_space(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the dependency dialog captures the later, mode and space keys."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        dialog = _DepOptionsDialog(root)
        dialog._later.set(True)
        dialog._mode.set(DependencyMode.EARLY.name)
        dialog._space.set('A B')
        dialog._confirm()
        assert dialog.options is not None
        assert dialog.options.later is True
        assert dialog.options.mode is DependencyMode.EARLY
        assert dialog.options.space_around == ['A', 'B']
    finally:
        root.destroy()


def test_ask_dep_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled dependency dialog returns nothing."""
    monkeypatch.setattr(_ModalDialog, '_show', _cancel_show)
    root = _root_or_skip()
    try:
        assert ask_dep_options(root) is None
    finally:
        root.destroy()


def test_start_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an empty start date stands for today."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        dialog = _StartDateDialog(root)
        dialog._date.set('')
        dialog._confirm()
        assert dialog.choice is not None
        assert dialog.choice.start_date is None
    finally:
        root.destroy()


def test_start_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a valid ISO date is captured as the start date."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        dialog = _StartDateDialog(root)
        dialog._date.set('2026-06-15')
        dialog._confirm()
        assert dialog.choice is not None
        assert dialog.choice.start_date == date(2026, 6, 15)
    finally:
        root.destroy()


def test_start_bad(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an invalid start date is rejected with an error."""
    rec = _MsgRec()
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    monkeypatch.setattr('backlogops_gui.io_dialogs.messagebox', rec)
    root = _root_or_skip()
    try:
        dialog = _StartDateDialog(root)
        dialog._date.set('nope')
        dialog._confirm()
        assert dialog.choice is None
        assert len(rec.calls) == 1
    finally:
        root.destroy()


def test_ask_start_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled start date dialog returns nothing."""
    monkeypatch.setattr(_ModalDialog, '_show', _cancel_show)
    root = _root_or_skip()
    try:
        assert ask_start_date(root) is None
    finally:
        root.destroy()


def test_levels_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the levels dialog returns the selected level numbers."""
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    root = _root_or_skip()
    try:
        dialog = _LevelsDialog(root)
        number = sorted(dialog._chosen)[0]
        dialog._chosen[number].set(True)
        dialog._confirm()
        assert dialog.levels == [number]
    finally:
        root.destroy()


def test_levels_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test selecting no levels is rejected with an error."""
    rec = _MsgRec()
    monkeypatch.setattr(_ModalDialog, '_show', _no_wait)
    monkeypatch.setattr('backlogops_gui.io_dialogs.messagebox', rec)
    root = _root_or_skip()
    try:
        dialog = _LevelsDialog(root)
        dialog._confirm()
        assert dialog.levels is None
        assert len(rec.calls) == 1
    finally:
        root.destroy()


def test_ask_levels_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled levels dialog returns nothing."""
    monkeypatch.setattr(_ModalDialog, '_show', _cancel_show)
    root = _root_or_skip()
    try:
        assert ask_levels(root) is None
    finally:
        root.destroy()


class _AutoBuffer(_BufferDialog):
    """Buffer dialog that confirms itself once shown, for show coverage."""

    def _show(self) -> None:
        """Schedule a confirm and run the real modal show."""
        self._win.after(0, self._confirm)
        super()._show()


def test_modal_show_real() -> None:
    """Test the real modal show builds the buttons and waits for a close."""
    root = _root_or_skip()
    try:
        dialog = _AutoBuffer(root)
        assert dialog.days == 5
    finally:
        root.destroy()


def _no_config_wait(self: _NoConfigDialog) -> None:
    """Stand in for the no-config show without grabbing or waiting."""
    assert self is not None


@pytest.mark.parametrize('choice', [
    ConfigChoice.WIZARD, ConfigChoice.LOAD, ConfigChoice.EXIT])
def test_no_config_choice(monkeypatch: pytest.MonkeyPatch,
                          choice: ConfigChoice) -> None:
    """Test each button records its choice in the no-config dialog."""
    monkeypatch.setattr(_NoConfigDialog, '_show', _no_config_wait)
    root = _root_or_skip()
    try:
        dialog = _NoConfigDialog(root)
        dialog._choose(choice)
        assert dialog.choice is choice
    finally:
        root.destroy()


def test_no_config_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the no-config dialog over a non-window parent defaults to exit."""
    monkeypatch.setattr(_NoConfigDialog, '_show', _no_config_wait)
    root = _root_or_skip()
    try:
        frame = tk.Frame(root)
        assert _NoConfigDialog(frame).choice is ConfigChoice.EXIT
    finally:
        root.destroy()


class _AutoNoConfig(_NoConfigDialog):
    """No-config dialog that picks the wizard once shown, for coverage."""

    def _show(self) -> None:
        """Schedule a wizard choice and run the real modal show."""
        self._win.after(0, lambda: self._choose(ConfigChoice.WIZARD))
        super()._show()


def test_no_config_show_real() -> None:
    """Test the real no-config show waits and returns the picked choice."""
    root = _root_or_skip()
    try:
        assert _AutoNoConfig(root).choice is ConfigChoice.WIZARD
    finally:
        root.destroy()


def test_ask_no_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the ask wrapper returns the dialog's recorded choice."""
    monkeypatch.setattr(_NoConfigDialog, '_show', _no_config_wait)
    root = _root_or_skip()
    try:
        assert ask_no_config_choice(root) is ConfigChoice.EXIT
    finally:
        root.destroy()


def test_change_list_no_wm() -> None:
    """Test the change list builds over a non-window parent."""
    root = _root_or_skip()
    try:
        frame = tk.Frame(root)
        window = show_change_list(frame, 'Changes', 'body', lambda: None)
        assert isinstance(window, tk.Toplevel)
        window.destroy()
    finally:
        root.destroy()
