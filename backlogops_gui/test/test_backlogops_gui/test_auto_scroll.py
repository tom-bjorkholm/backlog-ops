#! /usr/local/bin/python3
"""Tests for the auto-hiding scroll command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import ttk
import pytest
from backlogops_gui.auto_scroll import auto_hide
from .gui_test_helpers import gui_root


@pytest.mark.parametrize('first,last,shown', [
    ('0.0', '1.0', False),
    ('0.0', '0.5', True),
    ('0.3', '1.0', True),
    ('0.25', '0.75', True)])
def test_auto_hide(first: str, last: str, shown: bool) -> None:
    """Test the scrollbar hides only when the whole range is visible."""
    with gui_root() as root:
        scrollbar = ttk.Scrollbar(tk.Frame(root), orient='horizontal')
        scrollbar.grid(row=0, column=0, sticky='ew')
        auto_hide(scrollbar)(first, last)
        assert bool(scrollbar.grid_info()) is shown


def test_reappears() -> None:
    """Test a hidden scrollbar returns to its cell when it can scroll."""
    with gui_root() as root:
        scrollbar = ttk.Scrollbar(tk.Frame(root), orient='horizontal')
        scrollbar.grid(row=1, column=0, sticky='ew')
        command = auto_hide(scrollbar)
        command('0.0', '1.0')
        assert not scrollbar.grid_info()
        command('0.0', '0.5')
        assert scrollbar.grid_info()['row'] == 1
