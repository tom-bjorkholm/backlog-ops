#! /usr/local/bin/python3
"""Tests for the shared Cmd-W close-window binding."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
import tkinter as tk
import pytest
from backlogops_gui.close_binding import bind_close, _close_events, \
    _perform_close
from .gui_test_helpers import gui_root, press_close


def test_events_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test Windows adds the Ctrl-W close shortcut, other platforms not."""
    monkeypatch.setattr(sys, 'platform', 'win32')
    assert _close_events() == ['<Command-w>', '<Control-w>']
    monkeypatch.setattr(sys, 'platform', 'darwin')
    assert _close_events() == ['<Command-w>']


def test_close_default() -> None:
    """Test the default close action destroys the window and breaks."""
    with gui_root() as root:
        win = tk.Toplevel(root)
        assert _perform_close(win, None) == 'break'
        assert not win.winfo_exists()


def test_close_custom() -> None:
    """Test a custom close action runs and leaves the window open."""
    with gui_root() as root:
        win = tk.Toplevel(root)
        calls: list[int] = []
        assert _perform_close(win, lambda: calls.append(1)) == 'break'
        assert calls == [1]
        assert win.winfo_exists()
        win.destroy()


@pytest.mark.focus_sensitive
@pytest.mark.parametrize('platform,ctrl', [
    ('darwin', False), ('linux', False), ('win32', True)])
def test_events(monkeypatch: pytest.MonkeyPatch, platform: str,
                ctrl: bool) -> None:
    """Test Cmd-W is always bound and Ctrl-W only on Windows."""
    monkeypatch.setattr(sys, 'platform', platform)
    with gui_root() as root:
        win = tk.Toplevel(root)
        bind_close(win)
        assert win.bind('<Command-w>')
        assert bool(win.bind('<Control-w>')) is ctrl
        win.destroy()


@pytest.mark.focus_sensitive
def test_default_destroys() -> None:
    """Test Cmd-W destroys a window with the default close action."""
    with gui_root() as root:
        win = tk.Toplevel(root)
        bind_close(win)
        press_close(win)
        assert not win.winfo_exists()


@pytest.mark.focus_sensitive
def test_custom_action() -> None:
    """Test Cmd-W runs a custom action and leaves the window open."""
    with gui_root() as root:
        win = tk.Toplevel(root)
        calls: list[int] = []
        bind_close(win, lambda: calls.append(1))
        press_close(win)
        assert calls == [1]
        assert win.winfo_exists()
        win.destroy()


@pytest.mark.focus_sensitive
def test_stops_propagation() -> None:
    """Test the close binding returns break, stopping later handlers.

    A second handler is added on the same window, so it would run right
    after the close handler unless that handler stops the event.
    """
    with gui_root() as root:
        win = tk.Toplevel(root)
        also: list[int] = []
        bind_close(win, lambda: None)
        win.bind('<Command-w>', lambda _e: also.append(1), add=True)
        press_close(win)
        assert not also
        win.destroy()
