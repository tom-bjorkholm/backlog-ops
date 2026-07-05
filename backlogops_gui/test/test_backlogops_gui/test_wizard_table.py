#! /usr/local/bin/python3
"""Tests for the editable wizard table editor and its row helpers."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Optional
from tableio_cfg_json import TableCell, TableColumn
from backlogops_gui.wizard_table import TableEditor, _new_row_template, \
    _uniform
from .gui_test_helpers import gui_root


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
    with gui_root() as root:
        columns = [TableColumn(header='Day', read_only=True),
                   TableColumn(header='Hours')]
        cells = [[TableCell(value='Mon'), TableCell(value='8')]]
        editor = TableEditor(tk.Frame(root), columns, cells, None)
        assert editor.values() == [['Mon', '8']]
        assert editor.is_variable() is False


def test_table_editor_null() -> None:
    """Test an empty nullable entry cell is reported as None."""
    with gui_root() as root:
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value=None, nullable=True)]]
        editor = TableEditor(tk.Frame(root), columns, cells, None)
        assert editor.values() == [[None]]


def test_table_editor_choice() -> None:
    """Test a cell with choices returns its preselected value."""
    with gui_root() as root:
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value='a', choices=('a', 'b'))]]
        editor = TableEditor(tk.Frame(root), columns, cells, None)
        assert editor.values() == [['a']]


def test_table_add_row() -> None:
    """Test adding a row appends an editable row from the template."""
    with gui_root() as root:
        columns = [TableColumn(header='Src'), TableColumn(header='Dst')]
        cells = [[TableCell(value='a'), TableCell(value='b')]]
        editor = TableEditor(tk.Frame(root), columns, cells, None, min_rows=0,
                             max_rows=3)
        assert editor.is_variable() is True
        editor.add_row()
        assert editor.values() == [['a', 'b'], ['a', 'b']]


def test_table_add_row_at_max() -> None:
    """Test adding past the maximum keeps the rows and warns the user."""
    with gui_root() as root:
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value='v')]]
        editor = TableEditor(tk.Frame(root), columns, cells, None, min_rows=0,
                             max_rows=2)
        editor.add_row()
        editor.add_row()
        assert len(editor.values()) == 2
        # pylint: disable-next=protected-access
        assert 'At most 2' in editor._status.cget('text')


def test_table_remove_row() -> None:
    """Test removing a row drops the last row of the table."""
    with gui_root() as root:
        columns = [TableColumn(header='A'), TableColumn(header='B')]
        cells = [[TableCell(value='a'), TableCell(value='b')],
                 [TableCell(value='c'), TableCell(value='d')]]
        editor = TableEditor(tk.Frame(root), columns, cells, None, min_rows=0,
                             max_rows=3)
        editor.remove_row()
        assert editor.values() == [['a', 'b']]


def test_remove_row_at_min() -> None:
    """Test removing past the minimum keeps the rows and warns the user."""
    with gui_root() as root:
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value='v')]]
        editor = TableEditor(tk.Frame(root), columns, cells, None, min_rows=1,
                             max_rows=3)
        editor.remove_row()
        assert len(editor.values()) == 1
        # pylint: disable-next=protected-access
        assert 'At least 1' in editor._status.cget('text')


def test_added_row_editable() -> None:
    """Test an added row is editable even in a read-only column."""
    with gui_root() as root:
        columns = [TableColumn(header='Day', read_only=True),
                   TableColumn(header='Hours')]
        cells = [[TableCell(value='Mon'), TableCell(value='8')]]
        editor = TableEditor(tk.Frame(root), columns, cells, None, min_rows=0,
                             max_rows=2)
        # pylint: disable-next=protected-access
        assert editor._cells[0][0].read_only is True
        editor.add_row()
        # pylint: disable-next=protected-access
        added = editor._cells[1][0]
        assert added.read_only is False
        assert isinstance(added.widget, tk.Entry)
        assert editor.values()[1][0] == 'Mon'


def test_choice_no_value() -> None:
    """Test a drop-down cell with no value builds an empty combobox."""
    with gui_root() as root:
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value=None, choices=('a', 'b'))]]
        editor = TableEditor(tk.Frame(root), columns, cells, None)
        assert editor.values() == [['']]


def test_table_scroll_expands() -> None:
    """Test a variable table can grow with the wizard window."""
    with gui_root() as root:
        parent = tk.Frame(root)
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value='v')]]
        editor = TableEditor(parent, columns, cells, None, min_rows=0,
                             max_rows=10)
        # pylint: disable-next=protected-access
        assert editor._canvas is not None
        # pylint: disable-next=protected-access
        box = editor._canvas.master
        assert isinstance(box, tk.Frame)
        info = box.pack_info()
        assert info['fill'] == 'both'
        assert str(info['expand']) == '1'


def test_table_feedback() -> None:
    """Test a table with a check binds cells and shows per-cell feedback.

    Both a drop-down and a text cell are bound to the partial check; the
    check accepts the drop-down column and rejects the text column, so
    the status line clears and then shows the rejection message.
    """
    with gui_root() as root:
        columns = [TableColumn(header='Sel'), TableColumn(header='Txt')]
        cells = [[TableCell(value='a', choices=('a', 'b')),
                  TableCell(value='x')]]
        seen: list[tuple[int, int]] = []

        def check(table: list[list[Optional[str]]],
                  pos: tuple[int, int]) -> tuple[bool, str]:
            """Accept the drop-down column and reject the text column."""
            _ = table
            seen.append(pos)
            return (pos[1] == 0, '' if pos[1] == 0 else 'bad')
        editor = TableEditor(tk.Frame(root), columns, cells, check)
        # pylint: disable-next=protected-access
        editor._feedback(0, 1)
        # pylint: disable-next=protected-access
        assert editor._status.cget('text') == 'bad'
        # pylint: disable-next=protected-access
        editor._feedback(0, 0)
        # pylint: disable-next=protected-access
        assert editor._status.cget('text') == ''
        assert (0, 1) in seen and (0, 0) in seen
