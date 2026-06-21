#! /usr/local/bin/python3
"""Graphical bridge that drives the synchronous teams wizard.

The teams configuration wizard asks its questions through a
:class:`WizardUiBridge`. This module provides :class:`TkWizardBridge`, a
concrete bridge that overrides every ask method of that base class with a
real Tkinter control: a text entry, a yes/no button pair, a single- and a
multi-selection list, and an editable table. All questions are answered in
one reused, fixed-size window, so the whole wizard session happens in a
single pop-up that does not jump around the display. A cancelled prompt
raises :class:`EOFError`, which the wizard documents as the way an
interrupted input is reported.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable, Optional, Sequence, TextIO
from tableio_cfg_json import PartialCheck, TableCell, TableColumn, \
    WizardUiBridge
from backlogops import NoTextIO

WIZARD_TITLE = 'Configuration wizard'
WINDOW_SIZE = '620x520'
WRAP_LENGTH = 520
MESSAGE_HEIGHT = 8
CHOICE_HEIGHT = 10
HEADER_FONT = ('TkDefaultFont', 10, 'bold')
CANCEL_TEXT = 'Configuration wizard cancelled by the user.'


@dataclass(frozen=True)
class _Cell:
    """One built table cell: its widget and how its value is read.

    A read-only cell keeps the fixed text it shows. An editable cell keeps
    the widget the user types in or selects from, and whether an empty
    cell is reported as ``None``.
    """

    widget: Optional[tk.Widget]
    read_only: bool
    fixed: Optional[str]
    nullable: bool


def _cell_text(cell: _Cell) -> Optional[str]:
    """Return the final string a cell holds, or None for an empty cell."""
    if cell.read_only or cell.widget is None:
        return cell.fixed
    assert isinstance(cell.widget, (tk.Entry, ttk.Combobox))
    text = cell.widget.get()
    if text == '' and cell.nullable:
        return None
    return text


# pylint: disable-next=too-few-public-methods
class _TableEditor:
    """An editable grid of cells for one table question."""

    def __init__(self, parent: tk.Misc, columns: Sequence[TableColumn],
                 rows: Sequence[Sequence[TableCell]],
                 partial_check: Optional[PartialCheck]) -> None:
        """Build the header and one widget per cell of the given rows."""
        self._columns = columns
        self._check = partial_check
        self._cells: list[list[_Cell]] = []
        self._frame = tk.Frame(parent)
        self._frame.pack(anchor='w', pady=6)
        self._status = tk.Label(parent, fg='red', wraplength=WRAP_LENGTH,
                                justify='left')
        self._status.pack(anchor='w')
        self._build_header()
        for row_index, row in enumerate(rows):
            self._build_row(row_index, row)

    def values(self) -> list[list[Optional[str]]]:
        """Return the whole table as rows of final cell strings."""
        return [[_cell_text(cell) for cell in row] for row in self._cells]

    def _build_header(self) -> None:
        """Show one bold heading label per column."""
        for col, column in enumerate(self._columns):
            tk.Label(self._frame, text=column.header, font=HEADER_FONT).grid(
                row=0, column=col, padx=4, pady=2, sticky='w')

    def _build_row(self, row_index: int, row: Sequence[TableCell]) -> None:
        """Build and store one widget per column of one table row."""
        cells = [self._build_cell(row_index, col, column, cell)
                 for col, (column, cell) in enumerate(zip(self._columns, row))]
        self._cells.append(cells)

    def _build_cell(self, row_index: int, col: int, column: TableColumn,
                    cell: TableCell) -> _Cell:
        """Build one read-only label or one editable cell widget."""
        grid_row = row_index + 1
        if column.read_only:
            label = tk.Label(self._frame, text=cell.value or '')
            label.grid(row=grid_row, column=col, padx=4, pady=2, sticky='w')
            return _Cell(None, True, cell.value, False)
        widget = self._editable_widget(cell)
        widget.grid(row=grid_row, column=col, padx=4, pady=2)
        self._bind_change(widget, row_index, col)
        return _Cell(widget, False, None, cell.nullable)

    def _editable_widget(self, cell: TableCell) -> tk.Widget:
        """Return a drop-down for a cell with choices, else a text entry."""
        if cell.choices is not None:
            box = ttk.Combobox(self._frame, values=list(cell.choices),
                               state='readonly', width=18)
            if cell.value is not None:
                box.set(cell.value)
            return box
        entry = tk.Entry(self._frame, width=20)
        if cell.value is not None:
            entry.insert(0, cell.value)
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
        self._status.config(text='' if accepted else message)


class _WizardWindow:
    """One reused window that asks every wizard prompt in turn."""

    def __init__(self, parent: tk.Misc) -> None:
        """Create the fixed-size window and its lasting message area."""
        self._result: object = ''
        self._cancelled = False
        self._win = tk.Toplevel(parent)
        self._win.title(WIZARD_TITLE)
        self._win.geometry(WINDOW_SIZE)
        self._win.resizable(False, False)
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

    def ask(self, question: str, re_ask: Optional[str],
            choices: Optional[Sequence[str]]) -> str | int:
        """Ask one free-text or choice question and return the answer."""
        if choices is None:
            return self._ask_text(question, re_ask)
        return self._ask_index(question, re_ask, choices)

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
        self._add_buttons(lambda: self._pick_one(listbox, choices), None)
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

    def ask_table(self, columns: Sequence[TableColumn],
                  cells: Sequence[Sequence[TableCell]], question: str,
                  re_ask: Optional[str], partial_check: Optional[PartialCheck]
                  ) -> list[list[Optional[str]]]:
        """Ask the user to fill the given table rows and return them."""
        self._begin(question, re_ask)
        editor = _TableEditor(self._content, columns, cells, partial_check)
        self._add_buttons(lambda: self._finish(editor.values()), None)
        result = self._wait()
        assert isinstance(result, list)
        return result

    def _ask_text(self, question: str, re_ask: Optional[str]) -> str:
        """Ask one free-text question and return the entered text."""
        self._begin(question, re_ask)
        entry = tk.Entry(self._content, width=44)
        entry.pack(anchor='w', pady=6)
        entry.focus_set()
        self._add_buttons(lambda: self._finish(entry.get()), None)
        self._win.bind('<Return>', lambda event: self._finish(entry.get()))
        result = self._wait()
        assert isinstance(result, str)
        return result

    def _ask_index(self, question: str, re_ask: Optional[str],
                   choices: Sequence[str]) -> str | int:
        """Ask one question with a single-selection list of choices."""
        self._begin(question, re_ask)
        listbox = self._choice_list(choices, None, 'browse')
        self._add_buttons(lambda: self._pick(listbox),
                          lambda: self._finish(''))
        result = self._wait()
        assert isinstance(result, (str, int))
        return result

    def _run_multi(self, question: str, re_ask: Optional[str],
                   choices: Sequence[str],
                   default: Optional[Sequence[str]]) -> list[str]:
        """Show a multi-selection list once and return the picked values."""
        self._begin(question, re_ask)
        listbox = self._choice_list(choices, default, 'multiple')
        self._add_buttons(lambda: self._pick_many(listbox, choices), None)
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

    def _pick(self, listbox: tk.Listbox) -> None:
        """Finish a choice question with the selected zero-based index."""
        picks = listbox.curselection()  # type: ignore[no-untyped-call]
        if picks:
            self._finish(int(picks[0]))

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

    def _add_buttons(self, on_ok: Callable[[], None],
                     on_default: Optional[Callable[[], None]]) -> None:
        """Add the confirm, optional default, and cancel buttons."""
        box = tk.Frame(self._content)
        box.pack(anchor='w', pady=10)
        tk.Button(box, text='OK', command=on_ok).pack(side='left')
        if on_default is not None:
            tk.Button(box, text='Use default',
                      command=on_default).pack(side='left', padx=6)
        tk.Button(box, text='Cancel',
                  command=self._cancel).pack(side='left', padx=6)

    def _wait(self) -> object:
        """Block until the current prompt is answered or cancelled."""
        self._win.wait_variable(self._done)
        if self._cancelled:
            raise EOFError(CANCEL_TEXT)
        return self._result

    def _finish(self, value: object) -> None:
        """Store the answer and release the waiting prompt."""
        self._result = value
        self._done.set(self._done.get() + 1)

    def _cancel(self) -> None:
        """Mark the session cancelled and release the waiting prompt."""
        self._cancelled = True
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

    def ask(self, question: str, re_ask_reason: Optional[str] = None,
            choices: Optional[Sequence[str]] = None) -> str | int:
        """Ask one free-text or choice question; see WizardUiBridge.ask."""
        return self._window_obj().ask(question, re_ask_reason, choices)

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

    # pylint: disable-next=too-many-arguments,unused-argument
    def ask_table(self, columns: Sequence[TableColumn],
                  cells: list[list[TableCell]], question: str, *,
                  re_ask_reason: Optional[str] = None,
                  partial_check: Optional[PartialCheck] = None,
                  min_rows: Optional[int] = None,
                  max_rows: Optional[int] = None) -> list[list[Optional[str]]]:
        """Ask the user to fill an editable table of the given rows.

        Like the console bridge, this fills the rows given in ``cells`` and
        does not add or remove rows, so ``min_rows`` and ``max_rows`` are
        accepted but leave the row set fixed.
        """
        return self._window_obj().ask_table(columns, cells, question,
                                            re_ask_reason, partial_check)

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
