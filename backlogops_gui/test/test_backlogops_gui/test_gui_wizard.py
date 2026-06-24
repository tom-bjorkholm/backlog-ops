#! /usr/local/bin/python3
"""Tests for the Tkinter wizard bridge controls."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import cast
import pytest
from tableio_cfg_json import TableCell, TableColumn, WizardAbort, \
    WizardBack, WizardCancelLevel
from backlogops import NoTextIO
from backlogops_gui.gui_wizard import TkWizardBridge, _TableEditor, \
    _WizardWindow, _new_row_template, _uniform


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
        assert bridge.ask_text('Name?') == 'typed'
        bridge.close()
    finally:
        root.destroy()


def test_real_text_null() -> None:
    """Test an empty answer is reported as None when the cell is nullable."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._finish(''))
        assert bridge.ask_text('Name?', nullable=True) is None
        bridge.close()
    finally:
        root.destroy()


def test_real_text_empty() -> None:
    """Test an empty answer is the empty string when not nullable."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._finish(''))
        assert bridge.ask_text('Name?') == ''
        bridge.close()
    finally:
        root.destroy()


def test_real_reask() -> None:
    """Test a re-ask reason is shown above the question."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._finish('again'))
        assert bridge.ask_text('Name?', 'try again') == 'again'
        bridge.close()
    finally:
        root.destroy()


def test_real_reuse_window() -> None:
    """Test a second question reuses the window and clears the first."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._finish('one'))
        assert bridge.ask_text('Q1?') == 'one'
        root.after(0, lambda: bridge._window_obj()._finish('two'))
        assert bridge.ask_text('Q2?') == 'two'
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


def test_table_variable_add() -> None:
    """Test a variable table returns the seed row plus an added row."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        columns = [TableColumn(header='Src'), TableColumn(header='Dst')]
        cells = [[TableCell(value='a'), TableCell(value='b')]]

        def drive() -> None:
            window = bridge._window_obj()
            assert window._editor is not None
            window._editor.add_row()
            window._finish(window._editor.values())

        root.after(0, drive)
        result = bridge.ask_table(columns, cells, 'Q', min_rows=0, max_rows=3)
        assert result == [['a', 'b'], ['a', 'b']]
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


def test_real_abort() -> None:
    """Test the abort button raises a wizard-abort request."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._cancel())
        with pytest.raises(WizardAbort):
            bridge.ask_text('Name?')
        bridge.close()
    finally:
        root.destroy()


def test_real_back() -> None:
    """Test the back button raises a wizard-back request."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._back())
        with pytest.raises(WizardBack):
            bridge.ask_text('Name?')
        bridge.close()
    finally:
        root.destroy()


def test_real_cancel_level() -> None:
    """Test the out-one-level button raises a cancel-level request."""
    root = _root_or_skip()
    try:
        bridge = TkWizardBridge(root)
        root.after(0, lambda: bridge._window_obj()._cancel_level())
        with pytest.raises(WizardCancelLevel):
            bridge.ask_text('Name?')
        bridge.close()
    finally:
        root.destroy()


def test_uniform() -> None:
    """Test a shared value is kept and a mix falls back to the default."""
    assert _uniform([1, 1, 1], 0) == 1
    assert _uniform([1, 2], 0) == 0
    assert _uniform([], 0) == 0


def test_new_row_template() -> None:
    """Test the added-row template keeps shared cells and clears the rest."""
    columns = [TableColumn(header='A'), TableColumn(header='B')]
    rows = [[TableCell(value='x', choices=('x', 'y')), TableCell(value='m')],
            [TableCell(value='x', choices=('x', 'y')), TableCell(value='n')]]
    template = _new_row_template(columns, rows)
    assert template[0] == TableCell(value='x', choices=('x', 'y'))
    assert template[1] == TableCell(value='')


def test_template_empty() -> None:
    """Test the template of an empty seed is all default cells."""
    columns = [TableColumn(header='A')]
    assert _new_row_template(columns, []) == [TableCell(value='')]


def test_table_editor_text() -> None:
    """Test a read-only cell keeps its text and an entry returns its text."""
    root = _root_or_skip()
    try:
        columns = [TableColumn(header='Day', read_only=True),
                   TableColumn(header='Hours')]
        cells = [[TableCell(value='Mon'), TableCell(value='8')]]
        editor = _TableEditor(tk.Frame(root), columns, cells, None)
        assert editor.values() == [['Mon', '8']]
        assert editor.is_variable() is False
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


def test_table_add_row() -> None:
    """Test adding a row appends an editable row from the template."""
    root = _root_or_skip()
    try:
        columns = [TableColumn(header='Src'), TableColumn(header='Dst')]
        cells = [[TableCell(value='a'), TableCell(value='b')]]
        editor = _TableEditor(tk.Frame(root), columns, cells, None, min_rows=0,
                              max_rows=3)
        assert editor.is_variable() is True
        editor.add_row()
        assert editor.values() == [['a', 'b'], ['a', 'b']]
    finally:
        root.destroy()


def test_table_add_row_at_max() -> None:
    """Test adding past the maximum keeps the rows and warns the user."""
    root = _root_or_skip()
    try:
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value='v')]]
        editor = _TableEditor(tk.Frame(root), columns, cells, None, min_rows=0,
                              max_rows=2)
        editor.add_row()
        editor.add_row()
        assert len(editor.values()) == 2
        assert 'At most 2' in editor._status.cget('text')
    finally:
        root.destroy()


def test_table_remove_row() -> None:
    """Test removing a row drops the last row of the table."""
    root = _root_or_skip()
    try:
        columns = [TableColumn(header='A'), TableColumn(header='B')]
        cells = [[TableCell(value='a'), TableCell(value='b')],
                 [TableCell(value='c'), TableCell(value='d')]]
        editor = _TableEditor(tk.Frame(root), columns, cells, None, min_rows=0,
                              max_rows=3)
        editor.remove_row()
        assert editor.values() == [['a', 'b']]
    finally:
        root.destroy()


def test_remove_row_at_min() -> None:
    """Test removing past the minimum keeps the rows and warns the user."""
    root = _root_or_skip()
    try:
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value='v')]]
        editor = _TableEditor(tk.Frame(root), columns, cells, None, min_rows=1,
                              max_rows=3)
        editor.remove_row()
        assert len(editor.values()) == 1
        assert 'At least 1' in editor._status.cget('text')
    finally:
        root.destroy()


def test_added_row_editable() -> None:
    """Test an added row is editable even in a read-only column."""
    root = _root_or_skip()
    try:
        columns = [TableColumn(header='Day', read_only=True),
                   TableColumn(header='Hours')]
        cells = [[TableCell(value='Mon'), TableCell(value='8')]]
        editor = _TableEditor(tk.Frame(root), columns, cells, None, min_rows=0,
                              max_rows=2)
        assert editor._cells[0][0].read_only is True
        editor.add_row()
        added = editor._cells[1][0]
        assert added.read_only is False
        assert isinstance(added.widget, tk.Entry)
        assert editor.values()[1][0] == 'Mon'
    finally:
        root.destroy()


def test_choice_list_shown() -> None:
    """Test the choice list is packed and holds every choice.

    This guards against a regression where the single-selection list was
    built but never added to the window, so it stayed invisible.
    """
    root = _root_or_skip()
    try:
        window = _WizardWindow(tk.Frame(root))
        listbox = window._choice_list(['a', 'b', 'c'], None, 'browse')
        assert listbox.size() == 3
        assert listbox.winfo_manager() == 'pack'
        window.close()
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
