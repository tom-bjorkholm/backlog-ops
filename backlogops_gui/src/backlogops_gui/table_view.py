#! /usr/local/bin/python3
"""Build tables of a backlog and its releases with cell formatting.

A backlog and its releases are shown as two tables. The table data and the
cell formatting are derived from the same formatting the file writer uses,
so the on-screen colors match a written spreadsheet: the status cell and the
estimated-ready-date cell are highlighted by the format rules, and the other
cells are left plain. The columns are the union of the field names met in the
rows, kept in first-seen order, and every cell is rendered as text so the
table can show any value type. A per-table column-name map can rename a
column or drop it from the display, as the GUI display configuration decides.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from collections.abc import Mapping
from tkinter import font as tkfont
from tkinter import ttk
from typing import Optional, Sequence, TextIO
from tableio import Color, Fmt, Value, ValueFmt
from backlogops import (
    BacklogReleases, DEFAULT_LEVELS, FormatRules, LevelDisplay, Levels,
    NoTextIO, apply_column_map, display_level_rows, format_backlog,
    format_releases)

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


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def backlog_table(data: BacklogReleases, levels: Optional[Levels] = None,
                  display: LevelDisplay = LevelDisplay.BOTH,
                  names: Optional[Mapping[str, Optional[str]]] = None,
                  sink: Optional[TextIO] = None
                  ) -> tuple[list[str], list[list[ValueFmt]]]:
    """Return the columns and formatted rows for the backlog table.

    The level of each item is shown as its number, its name, or both, as
    ``display`` decides, using ``levels`` to translate a number to a name.
    The ``names`` map then renames or drops columns, as documented for
    :func:`backlogops.apply_column_map`.
    """
    out = sink if sink is not None else NoTextIO()
    chosen = DEFAULT_LEVELS if levels is None else levels
    rows = display_level_rows(format_backlog(data.backlog, FormatRules()),
                              chosen, display, out)
    return _table([apply_column_map(row, names or {}) for row in rows])


def release_table(data: BacklogReleases,
                  names: Optional[Mapping[str, Optional[str]]] = None
                  ) -> tuple[list[str], list[list[ValueFmt]]]:
    """Return the columns and formatted rows for the releases table.

    The ``names`` map renames or drops columns, as documented for
    :func:`backlogops.apply_column_map`.
    """
    rows = format_releases(data.releases, FormatRules())
    return _table([apply_column_map(row, names or {}) for row in rows])


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


def supports_cell_tags(tree: ttk.Treeview) -> bool:
    """Return whether this Tk build supports per-cell Treeview tags.

    Per-cell tags are a Tk 8.7+ feature. On an older Tk the ``tag cell``
    subcommand does not exist, so the probe raises and coloring falls back
    to whole-row tags, which Tk has supported for far longer.
    """
    try:
        tree.tk.call(str(tree), 'tag', 'cell', 'has', 'fmt-probe')
    except tk.TclError:
        return False
    return True


def _row_format(row: Sequence[ValueFmt]) -> Fmt:
    """Return the first non-plain cell format in a row, else plain."""
    for cell in row:
        if cell.fmt != Fmt():
            return cell.fmt
    return Fmt()


def _color_cells(tree: ttk.Treeview, item: str, columns: Sequence[str],
                 row: Sequence[ValueFmt]) -> None:
    """Color each formatted cell of an inserted row separately."""
    for column, cell in zip(columns, row):
        _format_cell(tree, item, column, cell.fmt)


def _insert_row(tree: ttk.Treeview, columns: Sequence[str],
                row: Sequence[ValueFmt], cell_tags: bool) -> None:
    """Insert one row as text and color it per cell or per row.

    With per-cell tags every formatted cell keeps its own color. Without
    them the whole row takes the format of its first formatted cell, so an
    older Tk still highlights the row instead of failing to build the table.
    """
    values = [_cell_text(cell.value) for cell in row]
    if cell_tags:
        item = tree.insert('', 'end', values=values)
        _color_cells(tree, item, columns, row)
        return
    fmt = _row_format(row)
    tags = () if fmt == Fmt() else (_ensure_tag(tree, fmt),)
    tree.insert('', 'end', values=values, tags=tags)


def make_table(parent: tk.Misc, columns: Sequence[str],
               rows: Sequence[Sequence[ValueFmt]], width: int = COLUMN_WIDTH,
               stretch: bool = True) -> ttk.Treeview:
    """Create a read-only Treeview showing the given columns and rows.

    Each cell is colored by the format rules, so a late estimate or a done
    or rejected status appears with the same highlight and font as in a
    written spreadsheet. On a Tk too old for per-cell tags the whole row is
    colored instead, so the table still builds and shows the highlight. When
    ``stretch`` is True the columns share the table width; when False each
    column keeps ``width`` pixels, so a table with few columns stays narrow
    instead of spreading across the whole width.
    """
    tree = ttk.Treeview(parent, columns=list(columns), show='headings')
    cell_tags = supports_cell_tags(tree)
    for name in columns:
        tree.heading(name, text=name)
        tree.column(name, width=width, stretch=stretch)
    for row in rows:
        _insert_row(tree, columns, row, cell_tags)
    return tree
