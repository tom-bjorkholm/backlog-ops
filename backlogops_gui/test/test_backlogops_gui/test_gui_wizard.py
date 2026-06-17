#! /usr/local/bin/python3
"""Tests for the Tkinter wizard bridge delegation."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable, Optional, Sequence, cast
import pytest
from backlogops import NoTextIO
from backlogops_gui.gui_wizard import TkWizardBridge, _WizardWindow


def _root_or_skip() -> tk.Tk:
    """Return a withdrawn Tk root, or skip when no display is available."""
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip('no display available')
    root.withdraw()
    return root


def _bridge(ask_fn: Optional[Callable[
                [str, Optional[str], Optional[Sequence[str]]],
                str | int]] = None,
            show_fn: Optional[Callable[[str], None]] = None,
            yes_no_fn: Optional[Callable[[str, bool], bool]] = None
            ) -> TkWizardBridge:
    """Return a bridge over a dummy parent with injected callables."""
    return TkWizardBridge(cast(tk.Misc, object()), ask_fn=ask_fn,
                          show_fn=show_fn, yes_no_fn=yes_no_fn)


def _cancel(_question: str, _reason: Optional[str],
            _choices: Optional[Sequence[str]]) -> str | int:
    """Raise as if the user cancelled the question dialog."""
    raise EOFError('cancelled')


def test_ask_returns_text() -> None:
    """Test the bridge returns the injected free-text answer."""
    bridge = _bridge(ask_fn=lambda question, reason, choices: 'hello')
    assert bridge.ask('Name?') == 'hello'


def test_ask_returns_index() -> None:
    """Test the bridge returns the injected choice index."""
    bridge = _bridge(ask_fn=lambda question, reason, choices: 2)
    assert bridge.ask('Pick', None, ['a', 'b', 'c']) == 2


def test_ask_cancel_raises() -> None:
    """Test a cancelled question propagates as an end-of-input error."""
    bridge = _bridge(ask_fn=_cancel)
    with pytest.raises(EOFError):
        bridge.ask('Name?')


def test_ask_yes_no_delegates() -> None:
    """Test the yes/no question forwards to the injected callable."""
    bridge = _bridge(yes_no_fn=lambda question, default: not default)
    assert bridge.ask_yes_no('Add?', False) is True
    assert bridge.ask_yes_no('Add?', True) is False


def test_show_forwards() -> None:
    """Test showing a message forwards it to the injected callable."""
    shown: list[str] = []
    bridge = _bridge(show_fn=shown.append)
    bridge.show('done')
    assert shown == ['done']


def test_error_file_is_sink() -> None:
    """Test the diagnostics stream discards its output without a log."""
    assert isinstance(_bridge().error_file(), NoTextIO)


def test_error_file_uses_log() -> None:
    """Test diagnostics go to the provided log when one is given."""
    log = NoTextIO()
    bridge = TkWizardBridge(cast(tk.Misc, object()), log)
    assert bridge.error_file() is log


def test_close_without_window() -> None:
    """Test closing is safe when no wizard window was opened."""
    _bridge().close()


def test_real_text() -> None:
    """Test a real window returns the entered free text."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._finish('typed'))
        assert bridge.ask('Name?') == 'typed'
        bridge.close()
    finally:
        root.destroy()


def test_real_reask() -> None:
    """Test a re-ask reason is shown above the question."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._finish('again'))
        assert bridge.ask('Name?', 'try again') == 'again'
        bridge.close()
    finally:
        root.destroy()


def test_real_reuse_window() -> None:
    """Test a second question reuses the window and clears the first."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._finish('one'))
        assert bridge.ask('Q1?') == 'one'
        root.after(0, lambda: bridge._window_obj()._finish('two'))
        assert bridge.ask('Q2?') == 'two'
        bridge.close()
    finally:
        root.destroy()


def test_real_choice() -> None:
    """Test a real window returns the selected choice index."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._finish(1))
        assert bridge.ask('Pick', None, ['a', 'b', 'c']) == 1
        bridge.close()
    finally:
        root.destroy()


def test_real_yes_no() -> None:
    """Test a real window returns the yes/no choice."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._finish(True))
        assert bridge.ask_yes_no('Add?', False) is True
        bridge.close()
    finally:
        root.destroy()


def test_real_show_and_close() -> None:
    """Test showing a message opens the window, then close removes it."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        bridge.show('a message')
        bridge.close()
    finally:
        root.destroy()


def test_real_cancel() -> None:
    """Test cancelling a real prompt raises an end-of-input error."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._cancel())
        with pytest.raises(EOFError):
            bridge.ask('Name?')
        bridge.close()
    finally:
        root.destroy()


def test_pick_selected() -> None:
    """Test picking a selected choice finishes with its index."""
    root = _root_or_skip()
    try:
        window = _WizardWindow(tk.Frame(root))
        listbox = tk.Listbox(window._content)
        listbox.insert('end', 'a')
        listbox.insert('end', 'b')
        listbox.selection_set(1)
        window._pick(listbox)
        assert window._result == 1
        window.close()
    finally:
        root.destroy()


def test_pick_empty() -> None:
    """Test picking with no selection leaves the answer unset."""
    root = _root_or_skip()
    try:
        window = _WizardWindow(root)
        listbox = tk.Listbox(window._content)
        listbox.insert('end', 'a')
        window._pick(listbox)
        assert window._result == ''
        window.close()
    finally:
        root.destroy()
