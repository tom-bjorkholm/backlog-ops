#! /usr/local/bin/python3
"""Tests for the read-only change-list and text-report windows."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
import pytest
from backlogops_gui import report_windows
from backlogops_gui.report_windows import show_change_list, show_text_report
from .gui_test_helpers import CloseSpy, gui_root


def test_change_list_no_wm() -> None:
    """Test the change list builds over a non-window parent."""
    with gui_root() as root:
        frame = tk.Frame(root)
        window = show_change_list(frame, 'Changes', 'body', lambda: None)
        assert isinstance(window, tk.Toplevel)
        window.destroy()


def test_text_report_no_wm() -> None:
    """Test the text report builds over a non-window parent."""
    with gui_root() as root:
        frame = tk.Frame(root)
        window = show_text_report(frame, 'Report', 'body')
        assert isinstance(window, tk.Toplevel)
        window.destroy()


def test_change_list_build() -> None:
    """Test the change list pop-up builds and can be dismissed."""
    with gui_root() as root:
        window = show_change_list(root, 'Changes', 'a: R1 -> R2', lambda: None)
        assert isinstance(window, tk.Toplevel)
        assert window.title() == 'Changes'
        window.destroy()


def test_change_list_binds(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the change-list pop-up binds Cmd-W to close itself."""
    spy = CloseSpy()
    monkeypatch.setattr(report_windows, 'bind_close', spy)
    with gui_root() as root:
        window = show_change_list(root, 'Changes', 'body', lambda: None)
        assert spy.calls == [(window, None)]


def test_text_report_binds(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the text-report pop-up binds Cmd-W to close itself."""
    spy = CloseSpy()
    monkeypatch.setattr(report_windows, 'bind_close', spy)
    with gui_root() as root:
        window = show_text_report(root, 'Report', 'body')
        assert spy.calls == [(window, None)]
