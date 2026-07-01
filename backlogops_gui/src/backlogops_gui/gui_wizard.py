#! /usr/local/bin/python3
"""Graphical bridge that drives the synchronous config wizard.

The backlog-ops configuration wizard asks its questions through a
:class:`WizardUiBridge`. This module provides :class:`TkWizardBridge`, a
concrete bridge that overrides every typed ask method of that base class
with a real Tkinter control: a text entry, a yes/no button pair, a
single- and a multi-selection list, and an editable table. All questions
are answered in one reused window, so the whole wizard session happens in
a single pop-up that does not jump around the display.
Every prompt also offers back, out-one-level and abort buttons, which
raise the matching :class:`WizardNavigation` request so the wizard can
step within the configuration or abandon it.

A table question may have a fixed set of rows or, when it is asked with
both a minimum and a maximum row count, a variable set of rows. A
variable table offers add-row and remove-row buttons and shows its grid
in a scrolling area, so a long table stays usable in the fixed window.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable, Optional, Sequence, TextIO, TypeVar
from tableio_cfg_json import PartialCheck, TableCell, TableColumn, \
    WizardAbort, WizardBack, WizardCancelLevel, WizardNavigation, \
    WizardUiBridge
from backlogops import NoTextIO
from backlogops_gui.gui_style import focus_first_input, style_input

WIZARD_TITLE = 'Configuration wizard'
WINDOW_SIZE = '720x620'
WRAP_LENGTH = 520
MESSAGE_HEIGHT = 8
CHOICE_HEIGHT = 10
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
class _Cell:
    """One built table cell: its widget and how its value is read.

    A read-only cell keeps the fixed text it shows in its label. An
    editable cell keeps the widget the user types in or selects from, and
    whether an empty cell is reported as ``None``.
    """

    widget: tk.Widget
    read_only: bool
    fixed: Optional[str]
    nullable: bool


def _cell_text(cell: _Cell) -> Optional[str]:
    """Return the final string a cell holds, or None for an empty cell."""
    if cell.read_only:
        return cell.fixed
    assert isinstance(cell.widget, (tk.Entry, ttk.Combobox))
    text = cell.widget.get()
    if text == '' and cell.nullable:
        return None
    return text


# pylint: disable-next=too-many-instance-attributes
class _TableEditor:
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
        self._cells: list[list[_Cell]] = []
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
                    pair: tuple[TableColumn, TableCell], added: bool) -> _Cell:
        """Build one read-only label or one editable cell widget."""
        column, cell = pair
        grid_row = index + 1
        if column.read_only and not added:
            label = tk.Label(self._grid, text=cell.value or '')
            label.grid(row=grid_row, column=col, padx=4, pady=2, sticky='w')
            return _Cell(label, True, cell.value, False)
        widget = self._editable_widget(cell)
        widget.grid(row=grid_row, column=col, padx=4, pady=2)
        self._bind_change(widget, index, col)
        return _Cell(widget, False, None, cell.nullable)

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


class _WizardWindow:
    """One reused window that asks every wizard prompt in turn."""

    def __init__(self, parent: tk.Misc) -> None:
        """Create the fixed-size window and its lasting message area."""
        self._result: object = ''
        self._nav: Optional[type[WizardNavigation]] = None
        self._editor: Optional[_TableEditor] = None
        self._win = tk.Toplevel(parent)
        self._win.title(WIZARD_TITLE)
        self._win.geometry(WINDOW_SIZE)
        self._win.resizable(True, True)
        if isinstance(parent, tk.Wm):
            self._win.transient(parent)
        self._win.protocol('WM_DELETE_WINDOW', self._cancel)
        self._done = tk.IntVar(self._win, 0)
        self._messages = self._build_messages()
        self._content = tk.Frame(self._win)
        self._content.pack(fill='both', expand=True, padx=12, pady=6)
        self._win.grab_set()

    def _build_messages(self) -> tk.Text:
        """Build the read-only area that keeps the wizard messages."""
        text = tk.Text(self._win, height=MESSAGE_HEIGHT, wrap='word',
                       state='disabled')
        text.pack(fill='x', padx=12, pady=(12, 6))
        return text

    def show(self, message: str) -> None:
        """Append one lasting message to the message area."""
        self._messages.configure(state='normal')
        self._messages.insert('end', message + '\n')
        self._messages.see('end')
        self._messages.configure(state='disabled')

    def close(self) -> None:
        """Destroy the wizard window."""
        self._win.destroy()

    def ask_text(self, question: str, re_ask: Optional[str],
                 nullable: bool) -> Optional[str]:
        """Ask one free-text question and return the entered text."""
        self._begin(question, re_ask)
        entry = tk.Entry(self._content, width=44)
        style_input(entry)
        entry.pack(anchor='w', pady=6)
        self._add_buttons(lambda: self._finish(entry.get()))
        self._win.bind('<Return>', lambda event: self._finish(entry.get()))
        result = self._wait()
        assert isinstance(result, str)
        return None if (nullable and result == '') else result

    def ask_yes_no(self, question: str, default: bool,
                   re_ask: Optional[str]) -> bool:
        """Ask one yes/no question with dedicated buttons."""
        self._begin(question, re_ask)
        box = tk.Frame(self._content)
        box.pack(pady=10)
        yes = tk.Button(box, text='Yes', command=lambda: self._finish(True))
        no = tk.Button(box, text='No', command=lambda: self._finish(False))
        yes.pack(side='left', padx=6)
        no.pack(side='left', padx=6)
        self._add_nav_buttons(box)
        chosen = yes if default else no
        chosen.focus_set()
        self._win.bind('<Return>', lambda event: chosen.invoke())
        result = self._wait()
        assert isinstance(result, bool)
        return result

    def ask_choice(self, question: str, choices: Sequence[str],
                   default: Optional[str], re_ask: Optional[str]) -> str:
        """Ask the user to pick exactly one choice and return it."""
        self._begin(question, re_ask)
        listbox = self._choice_list(choices, default, 'browse')
        self._add_buttons(lambda: self._pick_one(listbox, choices))
        result = self._wait()
        assert isinstance(result, str)
        return result

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def ask_multi(self, question: str, choices: Sequence[str],
                  default: Optional[Sequence[str]], min_select: int,
                  max_select: Optional[int], re_ask: Optional[str]
                  ) -> list[str]:
        """Ask the user to pick several choices within the count bounds."""
        reason = re_ask
        while True:
            chosen = self._run_multi(question, reason, choices, default)
            if len(chosen) < min_select:
                reason = f'Please select at least {min_select}.'
            elif max_select is not None and len(chosen) > max_select:
                reason = f'Please select at most {max_select}.'
            else:
                return chosen

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def ask_table(self, columns: Sequence[TableColumn],
                  cells: Sequence[Sequence[TableCell]], question: str,
                  re_ask: Optional[str], partial_check: Optional[PartialCheck],
                  min_rows: Optional[int], max_rows: Optional[int]
                  ) -> list[list[Optional[str]]]:
        """Ask the user to fill the given table rows and return them."""
        self._begin(question, re_ask)
        editor = _TableEditor(self._content, columns, cells, partial_check,
                              min_rows, max_rows)
        self._editor = editor
        self._add_table_buttons(editor)
        result = self._wait()
        assert isinstance(result, list)
        return result

    def _run_multi(self, question: str, re_ask: Optional[str],
                   choices: Sequence[str],
                   default: Optional[Sequence[str]]) -> list[str]:
        """Show a multi-selection list once and return the picked values."""
        self._begin(question, re_ask)
        listbox = self._choice_list(choices, default, 'multiple')
        self._add_buttons(lambda: self._pick_many(listbox, choices))
        result = self._wait()
        assert isinstance(result, list)
        return result

    def _choice_list(self, choices: Sequence[str],
                     marked: Optional[str | Sequence[str]],
                     mode: str) -> tk.Listbox:
        """Build a selection list, preselecting the marked choices."""
        listbox = tk.Listbox(self._content, exportselection=False,
                             selectmode=mode,
                             height=min(len(choices), CHOICE_HEIGHT))
        for choice in choices:
            listbox.insert('end', choice)
        style_input(listbox)
        listbox.pack(anchor='w', pady=6)
        preset = self._preset_indexes(choices, marked)
        for index in preset:
            listbox.selection_set(index)
        return listbox

    @staticmethod
    def _preset_indexes(choices: Sequence[str],
                        marked: Optional[str | Sequence[str]]) -> list[int]:
        """Return the indexes to preselect from a default value or list."""
        if marked is None:
            return []
        wanted = {marked} if isinstance(marked, str) else set(marked)
        return [index for index, choice in enumerate(choices)
                if choice in wanted]

    def _pick_one(self, listbox: tk.Listbox, choices: Sequence[str]) -> None:
        """Finish a single-choice question with the selected value."""
        picks = listbox.curselection()  # type: ignore[no-untyped-call]
        if picks:
            self._finish(choices[int(picks[0])])

    def _pick_many(self, listbox: tk.Listbox, choices: Sequence[str]) -> None:
        """Finish a multi-choice question with the selected values."""
        picks = listbox.curselection()  # type: ignore[no-untyped-call]
        self._finish([choices[int(index)] for index in picks])

    def _begin(self, question: str, re_ask: Optional[str]) -> None:
        """Clear the content area and show the question and any reason."""
        self._nav = None
        self._editor = None
        self._win.unbind('<Return>')
        for child in self._content.winfo_children():
            child.destroy()
        if re_ask is not None:
            self._add_label(re_ask, 'red')
        self._add_label(question, 'black')

    def _add_label(self, text: str, color: str) -> None:
        """Add one wrapped label to the content area."""
        label = tk.Label(self._content, text=text, fg=color,
                         wraplength=WRAP_LENGTH, justify='left')
        label.pack(anchor='w', pady=4)

    def _add_buttons(self, on_ok: Callable[[], None]) -> None:
        """Add the confirm and navigation buttons."""
        box = tk.Frame(self._content)
        box.pack(side='bottom', anchor='w', pady=10)
        tk.Button(box, text='OK', command=on_ok).pack(side='left')
        self._add_nav_buttons(box)

    def _add_table_buttons(self, editor: _TableEditor) -> None:
        """Add confirm, optional add/remove-row and navigation buttons."""
        box = tk.Frame(self._content)
        box.pack(side='bottom', anchor='w', pady=10)
        tk.Button(box, text='OK',
                  command=lambda: self._finish(editor.values())).pack(
                      side='left')
        if editor.is_variable():
            tk.Button(box, text='Add row',
                      command=editor.add_row).pack(side='left', padx=6)
            tk.Button(box, text='Remove row',
                      command=editor.remove_row).pack(side='left', padx=6)
        self._add_nav_buttons(box)

    def _add_nav_buttons(self, box: tk.Frame) -> None:
        """Add the back, out-one-level and abort navigation buttons."""
        tk.Button(box, text='Back',
                  command=self._back).pack(side='left', padx=6)
        tk.Button(box, text='Out one level',
                  command=self._cancel_level).pack(side='left', padx=6)
        tk.Button(box, text='Abort',
                  command=self._cancel).pack(side='left', padx=6)

    def _wait(self) -> object:
        """Focus the first input, then wait for an answer or navigation."""
        focus_first_input(self._content)
        self._win.wait_variable(self._done)
        if self._nav is not None:
            raise self._nav()
        return self._result

    def _finish(self, value: object) -> None:
        """Store the answer and release the waiting prompt."""
        self._result = value
        self._done.set(self._done.get() + 1)

    def _back(self) -> None:
        """Request a step back to the previous question."""
        self._navigate(WizardBack)

    def _cancel_level(self) -> None:
        """Request leaving the current level by one step."""
        self._navigate(WizardCancelLevel)

    def _cancel(self) -> None:
        """Request abandoning the whole configuration."""
        self._navigate(WizardAbort)

    def _navigate(self, request: type[WizardNavigation]) -> None:
        """Record a navigation request and release the waiting prompt."""
        self._nav = request
        self._done.set(self._done.get() + 1)


class TkWizardBridge(WizardUiBridge):
    """Bridge that answers wizard prompts in one reused Tkinter window."""

    def __init__(self, parent: tk.Misc, log: Optional[TextIO] = None) -> None:
        """Store the parent window and the optional diagnostics log.

        Args:
            parent: The window the wizard window is shown over.
            log: Stream that receives low-level wizard diagnostics.
        """
        self._parent = parent
        self._log = log
        self._window: Optional[_WizardWindow] = None

    def ask_text(self, question: str, re_ask_reason: Optional[str] = None,
                 nullable: bool = False) -> Optional[str]:
        """Ask for free text; see WizardUiBridge.ask_text."""
        return self._window_obj().ask_text(question, re_ask_reason, nullable)

    def ask_yes_no(self, question: str, default: bool,
                   re_ask_reason: Optional[str] = None) -> bool:
        """Ask a yes/no question with dedicated yes and no buttons."""
        return self._window_obj().ask_yes_no(question, default, re_ask_reason)

    def ask_choice(self, question: str, *, choices: Sequence[str],
                   default: Optional[str] = None,
                   re_ask_reason: Optional[str] = None) -> str:
        """Ask the user to pick one choice from a single-selection list."""
        return self._window_obj().ask_choice(question, choices, default,
                                             re_ask_reason)

    # pylint: disable-next=too-many-arguments
    def ask_multi(self, question: str, *, choices: Sequence[str],
                  default: Optional[Sequence[str]] = None, min_select: int = 0,
                  max_select: Optional[int] = None,
                  re_ask_reason: Optional[str] = None) -> list[str]:
        """Ask the user to pick several choices from a multi-selection list."""
        return self._window_obj().ask_multi(question, choices, default,
                                            min_select, max_select,
                                            re_ask_reason)

    # pylint: disable-next=too-many-arguments
    def ask_table(self, columns: Sequence[TableColumn],
                  cells: list[list[TableCell]], question: str, *,
                  re_ask_reason: Optional[str] = None,
                  partial_check: Optional[PartialCheck] = None,
                  min_rows: Optional[int] = None,
                  max_rows: Optional[int] = None) -> list[list[Optional[str]]]:
        """Ask the user to fill an editable table of the given rows.

        With both ``min_rows`` and ``max_rows`` given the table has a
        variable number of rows: add-row and remove-row buttons grow the
        table up to ``max_rows`` and shrink it down to ``min_rows``.
        Otherwise the rows given in ``cells`` are fixed and only filled.
        """
        return self._window_obj().ask_table(columns, cells, question,
                                            re_ask_reason, partial_check,
                                            min_rows, max_rows)

    def show(self, message: str) -> None:
        """Show an informational message to the user."""
        self._window_obj().show(message)

    def error_file(self) -> TextIO:
        """Return the stream used for low-level wizard diagnostics."""
        return self._log if self._log is not None else NoTextIO()

    def close(self) -> None:
        """Close the wizard window when one was opened."""
        if self._window is not None:
            self._window.close()
            self._window = None

    def _window_obj(self) -> _WizardWindow:
        """Return the wizard window, creating it on first use."""
        if self._window is None:
            self._window = _WizardWindow(self._parent)
        return self._window
