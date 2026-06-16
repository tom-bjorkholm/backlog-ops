#! /usr/local/bin/python3
"""Build tables of a backlog and its releases with cell formatting.

A backlog and its releases are shown as two tables. The table data and the
cell formatting are derived from the same formatting the file writer uses,
so the on-screen colors match a written spreadsheet: the status cell and the
estimated-ready-date cell are highlighted by the format rules, and the other
cells are left plain. The columns are the union of the field names met in the
rows, kept in first-seen order, and every cell is rendered as text so the
table can show any value type.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from typing import Sequence
from tableio import Color, Fmt, Value, ValueFmt
from backlogops import (
    BacklogReleases, FormatRules, format_backlog, format_releases)

COLUMN_WIDTH = 120
BLANK_CELL = ValueFmt(value=None, fmt=Fmt())
HIGHLIGHT_FILL = {Color.RED: '#ffd6d6', Color.GREEN: '#d6f5d6',
                  Color.YELLOW: '#fff3bf'}


def _columns(rows: Sequence[dict[str, ValueFmt]]) -> list[str]:
    """Return the column names met in the rows, in first-seen order."""
    columns: list[str] = []
    for row in rows:
        for name in row:
            if name not in columns:
                columns.append(name)
    return columns


def _cell_text(value: Value) -> str:
    """Return one cell value rendered as display text."""
    return '' if value is None else str(value)


def _table(rows: Sequence[dict[str, ValueFmt]]
           ) -> tuple[list[str], list[list[ValueFmt]]]:
    """Return the columns and column-aligned formatted rows.

    Each row becomes one cell per column, in column order, so a cell that a
    row does not have becomes a blank, unformatted cell.
    """
    columns = _columns(rows)
    cells = [[row.get(name, BLANK_CELL) for name in columns] for row in rows]
    return columns, cells


def backlog_table(data: BacklogReleases
                  ) -> tuple[list[str], list[list[ValueFmt]]]:
    """Return the columns and formatted rows for the backlog table."""
    return _table(format_backlog(data.backlog, FormatRules()))


def release_table(data: BacklogReleases
                  ) -> tuple[list[str], list[list[ValueFmt]]]:
    """Return the columns and formatted rows for the releases table."""
    return _table(format_releases(data.releases, FormatRules()))


def _tag_name(fmt: Fmt) -> str:
    """Return a stable tag name identifying one cell format."""
    return f'fmt-{int(fmt.bold)}{int(fmt.italic)}-{fmt.highlight.value}'


def _tag_font(tree: ttk.Treeview, fmt: Fmt) -> tuple[str, int, str]:
    """Return a font descriptor for the bold and italic of a format."""
    base = tkfont.nametofont('TkDefaultFont', root=tree)
    styles = ' '.join(name for name, on in
                      (('bold', fmt.bold), ('italic', fmt.italic)) if on)
    return (base.actual('family'), base.actual('size'), styles)


def _ensure_tag(tree: ttk.Treeview, fmt: Fmt) -> str:
    """Configure and return the tag for one non-plain cell format."""
    name = _tag_name(fmt)
    tree.tag_configure(name, background=HIGHLIGHT_FILL.get(fmt.highlight, ''),
                       font=_tag_font(tree, fmt))
    return name


def _format_cell(tree: ttk.Treeview, item: str, column: str, fmt: Fmt) -> None:
    """Color one table cell, leaving plain cells untouched."""
    if fmt == Fmt():
        return
    tag = _ensure_tag(tree, fmt)
    tree.tk.call(str(tree), 'tag', 'cell', 'add', tag, (item, column))


def _insert_row(tree: ttk.Treeview, columns: Sequence[str],
                row: Sequence[ValueFmt]) -> None:
    """Insert one row as text and color its formatted cells."""
    values = [_cell_text(cell.value) for cell in row]
    item = tree.insert('', 'end', values=values)
    for column, cell in zip(columns, row):
        _format_cell(tree, item, column, cell.fmt)


def make_table(parent: tk.Misc, columns: Sequence[str],
               rows: Sequence[Sequence[ValueFmt]], width: int = COLUMN_WIDTH,
               stretch: bool = True) -> ttk.Treeview:
    """Create a read-only Treeview showing the given columns and rows.

    Each cell is colored by the format rules, so a late estimate or a done
    or rejected status appears with the same highlight and font as in a
    written spreadsheet. When ``stretch`` is True the columns share the table
    width; when False each column keeps ``width`` pixels, so a table with few
    columns stays narrow instead of spreading across the whole width.
    """
    tree = ttk.Treeview(parent, columns=list(columns), show='headings')
    for name in columns:
        tree.heading(name, text=name)
        tree.column(name, width=width, stretch=stretch)
    for row in rows:
        _insert_row(tree, columns, row)
    return tree
