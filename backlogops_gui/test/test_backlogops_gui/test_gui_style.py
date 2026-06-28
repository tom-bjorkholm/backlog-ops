#! /usr/local/bin/python3
"""Tests for the shared input look and focus helpers."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import ttk
import pytest
from backlogops_gui.gui_style import (
    focus_first_input, style_input, _first_input, _is_input)


def _root_or_skip() -> tk.Tk:
    """Return a withdrawn Tk root, or skip when no display is available."""
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip('no display available')
    root.withdraw()
    return root


def test_style_entry() -> None:
    """Test a classic entry gets a white field and a solid border."""
    root = _root_or_skip()
    try:
        entry = tk.Entry(root)
        style_input(entry)
        assert str(entry.cget('background')) == 'white'
        assert str(entry.cget('relief')) == 'solid'
        assert int(entry.cget('borderwidth')) == 1
    finally:
        root.destroy()


def test_style_text() -> None:
    """Test a text box gets a white field and a solid border."""
    root = _root_or_skip()
    try:
        text = tk.Text(root)
        style_input(text)
        assert str(text.cget('background')) == 'white'
        assert str(text.cget('relief')) == 'solid'
    finally:
        root.destroy()


def test_style_listbox() -> None:
    """Test a list box gets a white field and a solid border."""
    root = _root_or_skip()
    try:
        box = tk.Listbox(root)
        style_input(box)
        assert str(box.cget('background')) == 'white'
        assert str(box.cget('relief')) == 'solid'
    finally:
        root.destroy()


def test_style_combobox() -> None:
    """Test a drop-down is put on the shared input style."""
    root = _root_or_skip()
    try:
        box = ttk.Combobox(root, state='readonly')
        style_input(box)
        assert str(box.cget('style')) == 'Input.TCombobox'
    finally:
        root.destroy()


def test_style_other_noop() -> None:
    """Test a non-input widget is left unchanged by the styling."""
    root = _root_or_skip()
    try:
        label = tk.Label(root, relief='flat')
        style_input(label)
        assert str(label.cget('relief')) == 'flat'
    finally:
        root.destroy()


def test_is_input() -> None:
    """Test editable widgets are inputs and a label is not."""
    root = _root_or_skip()
    try:
        assert _is_input(tk.Entry(root)) is True
        assert _is_input(ttk.Combobox(root)) is True
        assert _is_input(tk.Listbox(root)) is True
        assert _is_input(tk.Label(root)) is False
    finally:
        root.destroy()


def test_is_input_disabled() -> None:
    """Test a disabled text box is not treated as an input."""
    root = _root_or_skip()
    try:
        assert _is_input(tk.Text(root, state='disabled')) is False
    finally:
        root.destroy()


def test_first_input_order() -> None:
    """Test the first editable widget in child order is returned."""
    root = _root_or_skip()
    try:
        frame = tk.Frame(root)
        tk.Label(frame, text='x').pack()
        first = tk.Entry(frame)
        first.pack()
        tk.Entry(frame).pack()
        assert _first_input(frame) is first
    finally:
        root.destroy()


def test_first_input_nested() -> None:
    """Test the search descends into child frames."""
    root = _root_or_skip()
    try:
        outer = tk.Frame(root)
        inner = tk.Frame(outer)
        inner.pack()
        entry = tk.Entry(inner)
        entry.pack()
        assert _first_input(outer) is entry
    finally:
        root.destroy()


def test_first_input_none() -> None:
    """Test a window without inputs yields no widget to focus."""
    root = _root_or_skip()
    try:
        frame = tk.Frame(root)
        tk.Button(frame, text='ok').pack()
        assert _first_input(frame) is None
    finally:
        root.destroy()


def test_focus_first_input() -> None:
    """Test focusing the first input runs and targets that input."""
    root = _root_or_skip()
    try:
        entry = tk.Entry(root)
        entry.pack()
        focus_first_input(root)
        assert _first_input(root) is entry
    finally:
        root.destroy()


def test_focus_no_input() -> None:
    """Test focusing is a no-op when there is no input field."""
    root = _root_or_skip()
    try:
        tk.Button(root, text='ok').pack()
        focus_first_input(root)
    finally:
        root.destroy()
