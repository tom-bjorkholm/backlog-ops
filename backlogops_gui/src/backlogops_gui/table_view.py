#! /usr/local/bin/python3
"""Build read-only tables of a backlog and its releases.

A backlog and its releases are shown as two tables. The table data is
derived from the same row conversion the file writer uses, so the columns
match what would be written to a file. The columns are the union of the
field names met in the rows, kept in first-seen order, and every cell is
rendered as text so the table can show any value type.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import ttk
from typing import Sequence
from tableio import Value
from backlogops import BacklogReleases, item_to_row, release_to_row

COLUMN_WIDTH = 120


def _columns(rows: Sequence[dict[str, Value]]) -> list[str]:
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


def _table(rows: Sequence[dict[str, Value]]
           ) -> tuple[list[str], list[list[str]]]:
    """Return the columns and text rows for a sequence of row dicts."""
    columns = _columns(rows)
    text_rows = [[_cell_text(row.get(name)) for name in columns]
                 for row in rows]
    return columns, text_rows


def backlog_table(data: BacklogReleases) -> tuple[list[str], list[list[str]]]:
    """Return the columns and text rows for the backlog table."""
    return _table([item_to_row(item) for item in data.backlog])


def release_table(data: BacklogReleases) -> tuple[list[str], list[list[str]]]:
    """Return the columns and text rows for the releases table."""
    return _table([release_to_row(rel) for rel in data.releases])


def make_table(parent: tk.Misc, columns: Sequence[str],
               rows: Sequence[Sequence[str]]) -> ttk.Treeview:
    """Create a read-only Treeview showing the given columns and rows."""
    tree = ttk.Treeview(parent, columns=list(columns), show='headings')
    for name in columns:
        tree.heading(name, text=name)
        tree.column(name, width=COLUMN_WIDTH, stretch=True)
    for row in rows:
        tree.insert('', 'end', values=list(row))
    return tree
