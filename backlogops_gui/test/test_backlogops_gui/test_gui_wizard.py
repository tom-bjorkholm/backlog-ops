#! /usr/local/bin/python3
"""Tests for the Tkinter wizard bridge delegation."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable, Optional, Sequence, cast
import pytest
from backlogops import NoTextIO
from backlogops_gui.gui_wizard import TkWizardBridge


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
