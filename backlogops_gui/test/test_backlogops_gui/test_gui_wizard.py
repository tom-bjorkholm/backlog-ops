#! /usr/local/bin/python3
"""Tests for the Tkinter wizard bridge controls."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import cast
import pytest
from tableio_cfg_json import TableCell, TableColumn
from backlogops import NoTextIO
from backlogops_gui.gui_wizard import TkWizardBridge, _TableEditor, \
    _WizardWindow


def _root_or_skip() -> tk.Tk:
    """Return a withdrawn Tk root, or skip when no display is available."""
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip('no display available')
    root.withdraw()
    return root


def test_error_file_is_sink() -> None:
    """Test the diagnostics stream discards its output without a log."""
    bridge = TkWizardBridge(cast(tk.Misc, object()))
    assert isinstance(bridge.error_file(), NoTextIO)


def test_error_file_uses_log() -> None:
    """Test diagnostics go to the provided log when one is given."""
    log = NoTextIO()
    bridge = TkWizardBridge(cast(tk.Misc, object()), log)
    assert bridge.error_file() is log


def test_close_without_window() -> None:
    """Test closing is safe when no wizard window was opened."""
    TkWizardBridge(cast(tk.Misc, object())).close()


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


def test_real_index() -> None:
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


def test_real_choice() -> None:
    """Test a real window returns the selected choice value."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._finish('b'))
        assert bridge.ask_choice('Pick', choices=['a', 'b', 'c']) == 'b'
        bridge.close()
    finally:
        root.destroy()


def test_real_multi() -> None:
    """Test a real window returns the selected choice values."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._finish(['a', 'c']))
        assert bridge.ask_multi('Pick', choices=['a', 'b', 'c']) == ['a', 'c']
        bridge.close()
    finally:
        root.destroy()


def test_real_table() -> None:
    """Test a real window returns the table the user filled in."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value='v')]]
        root.after(0, lambda: bridge._window_obj()._finish([['v']]))
        assert bridge.ask_table(columns, cells, 'Q') == [['v']]
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


def test_table_editor_text() -> None:
    """Test a read-only cell keeps its text and an entry returns its text."""
    root = _root_or_skip()
    try:
        columns = [TableColumn(header='Day', read_only=True),
                   TableColumn(header='Hours')]
        cells = [[TableCell(value='Mon'), TableCell(value='8')]]
        editor = _TableEditor(tk.Frame(root), columns, cells, None)
        assert editor.values() == [['Mon', '8']]
    finally:
        root.destroy()


def test_table_editor_null() -> None:
    """Test an empty nullable entry cell is reported as None."""
    root = _root_or_skip()
    try:
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value=None, nullable=True)]]
        editor = _TableEditor(tk.Frame(root), columns, cells, None)
        assert editor.values() == [[None]]
    finally:
        root.destroy()


def test_table_editor_choice() -> None:
    """Test a cell with choices returns its preselected value."""
    root = _root_or_skip()
    try:
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value='a', choices=('a', 'b'))]]
        editor = _TableEditor(tk.Frame(root), columns, cells, None)
        assert editor.values() == [['a']]
    finally:
        root.destroy()


def test_pick_one() -> None:
    """Test picking a single choice finishes with its value."""
    root = _root_or_skip()
    try:
        window = _WizardWindow(tk.Frame(root))
        listbox = tk.Listbox(window._content)
        listbox.insert('end', 'a')
        listbox.insert('end', 'b')
        listbox.selection_set(1)
        window._pick_one(listbox, ['a', 'b'])
        assert window._result == 'b'
        window.close()
    finally:
        root.destroy()


def test_pick_many() -> None:
    """Test picking several choices finishes with the values in order."""
    root = _root_or_skip()
    try:
        window = _WizardWindow(tk.Frame(root))
        listbox = tk.Listbox(window._content, selectmode='multiple')
        for choice in ('a', 'b', 'c'):
            listbox.insert('end', choice)
        listbox.selection_set(0)
        listbox.selection_set(2)
        window._pick_many(listbox, ['a', 'b', 'c'])
        assert window._result == ['a', 'c']
        window.close()
    finally:
        root.destroy()


def test_pick_empty() -> None:
    """Test picking with no selection leaves the answer unset."""
    root = _root_or_skip()
    try:
        window = _WizardWindow(tk.Frame(root))
        listbox = tk.Listbox(window._content)
        listbox.insert('end', 'a')
        window._pick(listbox)
        assert window._result == ''
        window.close()
    finally:
        root.destroy()
