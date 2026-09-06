#! /usr/local/bin/python3
"""Tests for the read-only change-list and text-report windows."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable
import pytest
from backlogops_gui import report_windows
from backlogops_gui.report_windows import show_change_list, show_text_report
from .gui_test_helpers import CloseSpy, gui_root


def _scrollbars(window: tk.Toplevel) -> list[tk.Scrollbar]:
    """Return the scrollbars of the text box packed in a pop-up."""
    return [child for frame in window.winfo_children()
            for child in frame.winfo_children()
            if isinstance(child, tk.Scrollbar)]


@pytest.mark.parametrize('show', [
    lambda parent, text: show_text_report(parent, 'Report', text),
    lambda parent, text: show_change_list(parent, 'Changes', text,
                                          lambda: None)])
def test_scrollbars(show: Callable[[tk.Misc, str], tk.Toplevel]) -> None:
    """Test a pop-up scrolls a text taller and wider than its box."""
    with gui_root() as root:
        window = show(root, 'a long line of report text\n' * 40)
        orients = {str(scroll.cget('orient'))
                   for scroll in _scrollbars(window)}
        assert orients == {'vertical', 'horizontal'}
        window.destroy()


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
