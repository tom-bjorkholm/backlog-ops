#! /usr/local/bin/python3
"""An editable grid of cells for one wizard table question.

A table question shown by the wizard is rendered as a grid of cells. A
fixed table fills its seed rows only; a variable table, asked with both a
minimum and a maximum row count, offers add-row and remove-row buttons and
shows its grid in a scrolling area. :class:`TableEditor` builds the grid,
reads the final cell strings back, and runs the optional per-cell partial
check for early feedback.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Optional, Sequence, TypeVar
from tableio_cfg_json import PartialCheck, TableCell, TableColumn
from backlogops_gui.gui_style import style_input

WRAP_LENGTH = 520
TABLE_VIEW_HEIGHT = 210
HEADER_FONT = ('TkDefaultFont', 10, 'bold')

_V = TypeVar('_V')


def _uniform(values: list[_V], default: _V) -> _V:
    """Return the value shared by every entry, or the default."""
    if values and all(value == values[0] for value in values):
        return values[0]
    return default


def _new_row_template(columns: Sequence[TableColumn],
                      rows: Sequence[Sequence[TableCell]]) -> list[TableCell]:
    """Return the cell descriptors used for rows added at run time.

    For each column the new cell keeps the value, choices and nullable
    flag shared by every seed cell of that column, and falls back to an
    empty string, no choices and not-nullable when they differ. A cell in
    an added row is always editable, even in a read-only column.
    """
    template: list[TableCell] = []
    for col in range(len(columns)):
        column = [row[col] for row in rows]
        template.append(TableCell(
            value=_uniform([cell.value for cell in column], ''),
            choices=_uniform([cell.choices for cell in column], None),
            nullable=_uniform([cell.nullable for cell in column], False)))
    return template


@dataclass(frozen=True)
class Cell:
    """One built table cell: its widget and how its value is read.

    A read-only cell keeps the fixed text it shows in its label. An
    editable cell keeps the widget the user types in or selects from, and
    whether an empty cell is reported as ``None``.
    """

    widget: tk.Widget
    read_only: bool
    fixed: Optional[str]
    nullable: bool


def _cell_text(cell: Cell) -> Optional[str]:
    """Return the final string a cell holds, or None for an empty cell."""
    if cell.read_only:
        return cell.fixed
    assert isinstance(cell.widget, (tk.Entry, ttk.Combobox))
    text = cell.widget.get()
    if text == '' and cell.nullable:
        return None
    return text


# pylint: disable-next=too-many-instance-attributes
class TableEditor:
    """An editable grid of cells for one table question.

    A fixed table fills the seed rows only. A variable table, asked with
    both a minimum and a maximum row count, adds editable rows up to the
    maximum and removes the last row down to the minimum. A variable
    table shows its grid in a scrolling area, so a long table stays
    usable while the wizard window is resized.
    """

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __init__(self, parent: tk.Misc, columns: Sequence[TableColumn],
                 rows: Sequence[Sequence[TableCell]],
                 partial_check: Optional[PartialCheck],
                 min_rows: Optional[int] = None,
                 max_rows: Optional[int] = None) -> None:
        """Build the header and one widget per cell of the seed rows."""
        self._columns = columns
        self._check = partial_check
        self._variable = min_rows is not None and max_rows is not None
        self._min_rows = len(rows) if min_rows is None else min_rows
        self._max_rows = len(rows) if max_rows is None else max_rows
        self._template = _new_row_template(columns, rows)
        self._cells: list[list[Cell]] = []
        self._canvas: Optional[tk.Canvas] = None
        self._grid = self._build_grid_area(parent)
        self._status = tk.Label(parent, fg='red', wraplength=WRAP_LENGTH,
                                justify='left')
        self._status.pack(anchor='w')
        self._build_header()
        for row in rows:
            self._append_cells(list(row), False)

    def is_variable(self) -> bool:
        """Return whether the table can add and remove rows."""
        return self._variable

    def values(self) -> list[list[Optional[str]]]:
        """Return the whole table as rows of final cell strings."""
        return [[_cell_text(cell) for cell in row] for row in self._cells]

    def add_row(self) -> None:
        """Append one editable row, up to the maximum row count."""
        if len(self._cells) >= self._max_rows:
            self._show(f'At most {self._max_rows} rows allowed.')
            return
        self._append_cells(self._template, True)
        self._show('')
        self._scroll_to_end()

    def remove_row(self) -> None:
        """Remove the last row, down to the minimum row count."""
        if len(self._cells) <= self._min_rows:
            self._show(f'At least {self._min_rows} rows required.')
            return
        for cell in self._cells.pop():
            cell.widget.destroy()
        self._show('')

    def _build_grid_area(self, parent: tk.Misc) -> tk.Frame:
        """Return the frame holding the grid, scrolling when variable."""
        if not self._variable:
            frame = tk.Frame(parent)
            frame.pack(anchor='w', pady=6)
            return frame
        return self._build_scroll(parent)

    def _build_scroll(self, parent: tk.Misc) -> tk.Frame:
        """Build an expanding scrolling area and return its inner frame."""
        box = tk.Frame(parent)
        box.pack(anchor='w', fill='both', expand=True, pady=6)
        canvas = tk.Canvas(box, height=TABLE_VIEW_HEIGHT, highlightthickness=0)
        scrollbar = tk.Scrollbar(box, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        inner = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor='nw')
        inner.bind('<Configure>', lambda _event: canvas.configure(
            scrollregion=canvas.bbox('all')))
        self._canvas = canvas
        return inner

    def _scroll_to_end(self) -> None:
        """Bring the newly added last row into the scrolling area."""
        assert self._canvas is not None
        self._canvas.update_idletasks()
        self._canvas.yview_moveto(1.0)

    def _build_header(self) -> None:
        """Show one bold heading label per column."""
        for col, column in enumerate(self._columns):
            tk.Label(self._grid, text=column.header, font=HEADER_FONT).grid(
                row=0, column=col, padx=4, pady=2, sticky='w')

    def _append_cells(self, row: Sequence[TableCell], added: bool) -> None:
        """Build and store one widget per column of one new table row."""
        index = len(self._cells)
        built = [self._build_cell(index, col, pair, added)
                 for col, pair in enumerate(zip(self._columns, row))]
        self._cells.append(built)

    def _build_cell(self, index: int, col: int,
                    pair: tuple[TableColumn, TableCell], added: bool) -> Cell:
        """Build one read-only label or one editable cell widget."""
        column, cell = pair
        grid_row = index + 1
        if column.read_only and not added:
            label = tk.Label(self._grid, text=cell.value or '')
            label.grid(row=grid_row, column=col, padx=4, pady=2, sticky='w')
            return Cell(label, True, cell.value, False)
        widget = self._editable_widget(cell)
        widget.grid(row=grid_row, column=col, padx=4, pady=2)
        self._bind_change(widget, index, col)
        return Cell(widget, False, None, cell.nullable)

    def _editable_widget(self, cell: TableCell) -> tk.Widget:
        """Return a drop-down for a cell with choices, else a text entry."""
        if cell.choices is not None:
            box = ttk.Combobox(self._grid, values=list(cell.choices),
                               state='readonly', width=18)
            if cell.value is not None:
                box.set(cell.value)
            style_input(box)
            return box
        entry = tk.Entry(self._grid, width=20)
        if cell.value is not None:
            entry.insert(0, cell.value)
        style_input(entry)
        return entry

    def _bind_change(self, widget: tk.Widget, row: int, col: int) -> None:
        """Show early per-cell feedback when an edited cell changes."""
        if self._check is None:
            return
        event = ('<<ComboboxSelected>>' if isinstance(widget, ttk.Combobox)
                 else '<KeyRelease>')
        widget.bind(event, lambda _event: self._feedback(row, col))

    def _feedback(self, row: int, col: int) -> None:
        """Run the partial check and show its message for one cell."""
        assert self._check is not None
        accepted, message = self._check(self.values(), (row, col))
        self._show('' if accepted else message)

    def _show(self, message: str) -> None:
        """Show a status message below the grid."""
        self._status.config(text=message)
