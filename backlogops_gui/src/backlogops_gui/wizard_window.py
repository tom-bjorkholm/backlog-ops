#! /usr/local/bin/python3
"""One reused window that asks every wizard prompt in turn.

The wizard bridge answers all of its questions in a single
:class:`WizardWindow`, so the whole wizard session happens in one pop-up
that does not jump around the display. The window offers a text entry, an
integer entry, a path entry with a native Browse button, a yes/no button
pair, a single- and a multi-selection list, an editable table and a whole
form on one screen, and keeps a lasting message area above the changing
content. Every prompt also offers back, out-one-level and abort buttons,
which raise the matching :class:`WizardNavigation` request so the wizard
can step within the configuration or abandon it.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from pathlib import Path
from typing import Callable, Optional, Sequence
from tableio_cfg_json import AnswerFields, AskFields, PartialCheck, \
    PartialFormValidator, PathAskOptions, TableCell, TableColumn, \
    WizardAbort, WizardBack, WizardCancelLevel, WizardNavigation
from backlogops_gui.close_binding import bind_close
from backlogops_gui.gui_style import focus_first_input, style_input
from backlogops_gui.wizard_form import FormEditor, int_answer
from backlogops_gui.wizard_path import PathRow, validate_path
from backlogops_gui.wizard_table import TableEditor

WIZARD_TITLE = 'Configuration wizard'
WINDOW_SIZE = '720x620'
WRAP_LENGTH = 520
MESSAGE_HEIGHT = 8
CHOICE_HEIGHT = 10


def _default_path_text(options: PathAskOptions) -> str:
    """Return the initial path text from the option's default."""
    return '' if options.default is None else str(options.default)


# pylint: disable-next=too-many-instance-attributes
class WizardWindow:
    """One reused window that asks every wizard prompt in turn."""

    def __init__(self, parent: tk.Misc) -> None:
        """Create the fixed-size window and its lasting message area."""
        self._result: object = ''
        self._nav: Optional[type[WizardNavigation]] = None
        self._editor: Optional[TableEditor] = None
        self._form: Optional[FormEditor] = None
        self._win = tk.Toplevel(parent)
        self._win.title(WIZARD_TITLE)
        self._win.geometry(WINDOW_SIZE)
        self._win.resizable(True, True)
        if isinstance(parent, tk.Wm):
            self._win.transient(parent)
        self._win.protocol('WM_DELETE_WINDOW', self._cancel)
        bind_close(self._win, self._cancel)
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

    def ask_text(self, question: str, re_ask: Optional[str], nullable: bool,
                 default: Optional[str] = None,
                 sensitive: bool = False) -> Optional[str]:
        """Ask one free-text question and return the entered text.

        A sensitive question masks the typed text; a default value is
        pre-filled and returned when the answer is left empty.
        """
        self._begin(question, re_ask)
        entry = tk.Entry(self._content, width=44)
        if sensitive:
            entry.configure(show='*')
        elif default is not None:
            entry.insert(0, default)
        style_input(entry)
        entry.pack(anchor='w', pady=6)
        self._add_buttons(lambda: self._finish(entry.get()))
        self._win.bind('<Return>', lambda event: self._finish(entry.get()))
        result = self._wait()
        assert isinstance(result, str)
        return self._text_result(result, nullable, default)

    @staticmethod
    def _text_result(result: str, nullable: bool,
                     default: Optional[str]) -> Optional[str]:
        """Return the answer after the default and nullable rules."""
        if result != '':
            return result
        if default is not None:
            return default
        return None if nullable else ''

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def ask_int(self, question: str, re_ask: Optional[str], nullable: bool,
                min_value: Optional[int], max_value: Optional[int],
                default: Optional[int]) -> Optional[int]:
        """Ask one integer question, re-asking until it is in range."""
        reason = re_ask
        while True:
            text = self._run_int(question, reason, default)
            done, value, reason = int_answer(text, nullable, min_value,
                                             max_value, default)
            if done:
                return value

    def _run_int(self, question: str, re_ask: Optional[str],
                 default: Optional[int]) -> str:
        """Show one integer entry and return the entered text."""
        self._begin(question, re_ask)
        entry = tk.Entry(self._content, width=14)
        if default is not None:
            entry.insert(0, str(default))
        style_input(entry)
        entry.pack(anchor='w', pady=6)
        self._add_buttons(lambda: self._finish(entry.get()))
        self._win.bind('<Return>', lambda _event: self._finish(entry.get()))
        result = self._wait()
        assert isinstance(result, str)
        return result

    def ask_path(self, question: str, options: PathAskOptions,
                 re_ask: Optional[str]) -> Optional[Path]:
        """Ask one path question with a Browse button, re-asking on error."""
        reason = re_ask
        value: Optional[str] = None
        while True:
            text = self._run_path(question, reason, options, value)
            done, path, reason = validate_path(text, options)
            if done:
                return path
            value = text

    def _run_path(self, question: str, re_ask: Optional[str],
                  options: PathAskOptions, value: Optional[str]) -> str:
        """Show one path entry with a Browse button and return the text."""
        self._begin(question, re_ask)
        initial = value if value is not None else _default_path_text(options)
        row = PathRow(self._content, options, initial)
        row.frame.pack(anchor='w', pady=6)
        self._add_buttons(lambda: self._finish(row.get()))
        self._win.bind('<Return>', lambda _event: self._finish(row.get()))
        result = self._wait()
        assert isinstance(result, str)
        return result

    def ask_form(self, long_question: str, fields: AskFields,
                 re_ask: Optional[str],
                 validator: Optional[PartialFormValidator]) -> AnswerFields:
        """Ask a whole form on one screen and return its answers."""
        self._begin(long_question, re_ask)
        self._form = FormEditor(self._content, fields, validator, self._finish)
        self._add_buttons(self._form.submit)
        result = self._wait()
        assert isinstance(result, list)
        return result

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
        editor = TableEditor(self._content, columns, cells, partial_check,
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
        self._form = None
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

    def _add_table_buttons(self, editor: TableEditor) -> None:
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
