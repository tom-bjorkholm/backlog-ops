#! /usr/local/bin/python3
"""A whole wizard form shown on one screen, and its answer parsing.

A form question asks several related fields at once. :class:`FormEditor`
builds a two-column grid, a label on the left and an input widget on the
right, one row per :class:`AskField`. It reads one :class:`AnswerField`
per row, runs the optional partial validator after every change to show
advisory feedback and disable irrelevant rows, and validates every
enabled field on submit so a submitted form is always complete.

The small scalar-answer helpers (:func:`text_answer`, :func:`int_answer`
and friends) turn the raw text of a text or integer field into its typed
answer. They are shared with the reused wizard window, which asks a
standalone integer question with the same rules.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from tkinter import ttk
from typing import Callable, NamedTuple, Optional, Sequence
from tableio_cfg_json import AskField, AnswerField, PartialFormValidator, \
    AskTextField, AskIntField, AskPathField, AskYesNoField, AskChoiceField, \
    AskMultiChoiceField, AnswerTextField, AnswerIntField, AnswerPathField, \
    AnswerYesNoField, AnswerChoiceField, AnswerMultiChoiceField
from backlogops_gui.gui_style import style_input
from backlogops_gui.wizard_path import PathRow, validate_path

WRAP_LENGTH = 520
LABEL_WRAP = 220
MULTI_HEIGHT = 6
ENTRY_WIDTH = 34
INT_WIDTH = 14
CHOICE_WIDTH = 30
_INT_ERROR = 'Please enter an integer.'
_CHOICE_REQUIRED = 'Please choose a value.'
TOOLTIP_BG = '#ffffe0'
TOOLTIP_WRAP = 320


def text_answer(text: str, nullable: bool,
                default: Optional[str]) -> Optional[str]:
    """Return the public text answer for the raw text of a text field."""
    if text == '' and default is not None:
        return default
    if text == '' and nullable:
        return None
    return text


def int_text(text: str) -> Optional[int]:
    """Return the integer in text, or None when it is not an integer."""
    try:
        return int(text)
    except ValueError:
        return None


def out_of_range(value: int, min_value: Optional[int],
                 max_value: Optional[int]) -> bool:
    """Return whether value lies outside the inclusive bounds."""
    below = min_value is not None and value < min_value
    above = max_value is not None and value > max_value
    return below or above


def range_error(min_value: Optional[int], max_value: Optional[int]) -> str:
    """Return the message shown when an integer is out of range."""
    if min_value is None:
        return f'Please enter an integer at most {max_value}.'
    if max_value is None:
        return f'Please enter an integer at least {min_value}.'
    return f'Please enter an integer between {min_value} and {max_value}.'


# pylint: disable-next=too-many-arguments
def int_answer(text: str, nullable: bool, min_value: Optional[int],
               max_value: Optional[int], default: Optional[int]
               ) -> tuple[bool, Optional[int], Optional[str]]:
    """Return whether an integer answer is final, its value, and a reason.

    An empty answer takes the default, is None when nullable, or is
    re-asked otherwise. A non-empty answer must parse as an integer that
    lies within the inclusive bounds.
    """
    if text == '':
        if default is not None:
            return (True, default, None)
        return (True, None, None) if nullable else (False, None, _INT_ERROR)
    value = int_text(text)
    if value is None:
        return (False, None, _INT_ERROR)
    if out_of_range(value, min_value, max_value):
        return (False, None, range_error(min_value, max_value))
    return (True, value, None)


def multi_count_error(min_select: int, max_select: Optional[int]) -> str:
    """Return the message shown when the selected count is not allowed."""
    if max_select is None:
        return f'Please select at least {min_select}.'
    if min_select == max_select:
        return f'Please select exactly {min_select}.'
    return f'Please select between {min_select} and {max_select}.'


class _Input(NamedTuple):
    """A built input: the widget to place, plus type-specific handles."""

    widget: tk.Widget
    var: Optional[tk.BooleanVar]
    path: Optional[PathRow]


class HelpTooltip:
    """A hover bubble showing a field's help text over its widgets.

    The bubble is a borderless top-level window shown when the pointer
    enters a bound widget and destroyed when it leaves, so help appears
    on hover as it does in the textual bridge. It uses neither a
    transient window, forced focus nor a grab, which can crash Tk in
    automated runs.
    """

    def __init__(self, text: str, anchor: tk.Widget,
                 widgets: Sequence[tk.Widget]) -> None:
        """Bind hover show and hide on each widget for the help text."""
        self.text = text
        self._anchor = anchor
        self._tip: Optional[tk.Toplevel] = None
        for widget in widgets:
            widget.bind('<Enter>', lambda _event: self.show(), add='+')
            widget.bind('<Leave>', lambda _event: self.hide(), add='+')

    def show(self) -> None:
        """Show the help bubble just below the anchor widget."""
        if self._tip is not None:
            return
        tip = tk.Toplevel(self._anchor)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(self._geometry())
        tk.Label(tip, text=self.text, background=TOOLTIP_BG, relief='solid',
                 borderwidth=1, justify='left', wraplength=TOOLTIP_WRAP).pack()
        self._tip = tip

    def hide(self) -> None:
        """Destroy the help bubble when one is shown."""
        if self._tip is not None:
            self._tip.destroy()
            self._tip = None

    def _geometry(self) -> str:
        """Return the position string placing the bubble under the anchor."""
        x = self._anchor.winfo_rootx()
        y = self._anchor.winfo_rooty() + self._anchor.winfo_height() + 2
        return f'+{x}+{y}'


@dataclass(frozen=True)
class FormRow:
    """One built form row: its field, label, input and help tooltip."""

    field: AskField
    label: tk.Label
    widget: tk.Widget
    var: Optional[tk.BooleanVar]
    path: Optional[PathRow]
    tooltip: Optional[HelpTooltip] = None


def _text_input(grid: tk.Misc, field: AskTextField,
                change: Callable[[], None]) -> _Input:
    """Build a text entry, masked and without a default when sensitive."""
    entry = tk.Entry(grid, width=ENTRY_WIDTH)
    if field.sensitive:
        entry.configure(show='*')
    elif field.default is not None:
        entry.insert(0, field.default)
    style_input(entry)
    entry.bind('<KeyRelease>', lambda _event: change())
    return _Input(entry, None, None)


def _int_input(grid: tk.Misc, field: AskIntField,
               change: Callable[[], None]) -> _Input:
    """Build a numeric text entry pre-filled with its default."""
    entry = tk.Entry(grid, width=INT_WIDTH)
    if field.default is not None:
        entry.insert(0, str(field.default))
    style_input(entry)
    entry.bind('<KeyRelease>', lambda _event: change())
    return _Input(entry, None, None)


def _path_input(grid: tk.Misc, field: AskPathField,
                change: Callable[[], None]) -> _Input:
    """Build a path entry with a Browse button from the path options."""
    default = field.path_options.default
    initial = '' if default is None else str(default)
    row = PathRow(grid, field.path_options, initial, change)
    return _Input(row.frame, None, row)


def _yes_no_input(grid: tk.Misc, field: AskYesNoField,
                  change: Callable[[], None]) -> _Input:
    """Build a check box holding the yes/no default."""
    var = tk.BooleanVar(grid, field.default)
    check = tk.Checkbutton(grid, variable=var, command=change)
    return _Input(check, var, None)


def _choice_input(grid: tk.Misc, field: AskChoiceField,
                  change: Callable[[], None]) -> _Input:
    """Build a read-only drop-down, preselecting any default choice."""
    box = ttk.Combobox(grid, values=list(field.choices), state='readonly',
                       width=CHOICE_WIDTH)
    if field.default is not None:
        box.set(field.default)
    style_input(box)
    box.bind('<<ComboboxSelected>>', lambda _event: change())
    return _Input(box, None, None)


def _multi_input(grid: tk.Misc, field: AskMultiChoiceField,
                 change: Callable[[], None]) -> _Input:
    """Build a multi-selection list, preselecting the default values."""
    box = tk.Listbox(grid, selectmode='multiple', exportselection=False,
                     height=min(len(field.choices), MULTI_HEIGHT))
    for choice in field.choices:
        box.insert('end', choice)
    _preselect(box, field.choices, field.default)
    style_input(box)
    box.bind('<<ListboxSelect>>', lambda _event: change())
    return _Input(box, None, None)


def _preselect(box: tk.Listbox, choices: Sequence[str],
               default: Optional[Sequence[str]]) -> None:
    """Select the default values in a multi-selection list."""
    if default is None:
        return
    wanted = set(default)
    for index, choice in enumerate(choices):
        if choice in wanted:
            box.selection_set(index)


def _make_input(grid: tk.Misc, field: AskField,
                change: Callable[[], None]) -> _Input:
    """Build the input widget matching the field type."""
    if isinstance(field, AskTextField):
        return _text_input(grid, field, change)
    if isinstance(field, AskIntField):
        return _int_input(grid, field, change)
    if isinstance(field, AskPathField):
        return _path_input(grid, field, change)
    if isinstance(field, AskYesNoField):
        return _yes_no_input(grid, field, change)
    if isinstance(field, AskChoiceField):
        return _choice_input(grid, field, change)
    assert isinstance(field, AskMultiChoiceField)
    return _multi_input(grid, field, change)


def _entry_widget(row: FormRow) -> tk.Entry:
    """Return the text entry of a text or integer row."""
    assert isinstance(row.widget, tk.Entry)
    return row.widget


def _int_value(row: FormRow, field: AskIntField) -> Optional[int]:
    """Return the integer value of a row, or its default when empty."""
    text = _entry_widget(row).get()
    return field.default if text == '' else int_text(text)


def _path_value(row: FormRow, field: AskPathField) -> Optional[Path]:
    """Return the accepted path of a row, or None when not accepted."""
    assert row.path is not None
    _, path, _ = validate_path(row.path.get(), field.path_options)
    return path


def _choice_value(row: FormRow) -> Optional[str]:
    """Return the chosen value of a row, or None when none is chosen."""
    assert isinstance(row.widget, ttk.Combobox)
    value = row.widget.get()
    return value if value != '' else None


def _multi_selected(row: FormRow) -> list[int]:
    """Return the selected 0-based indexes of a multi-selection row."""
    assert isinstance(row.widget, tk.Listbox)
    picks = row.widget.curselection()  # type: ignore[no-untyped-call]
    return [int(index) for index in picks]


def _multi_values(row: FormRow, field: AskMultiChoiceField) -> list[str]:
    """Return the chosen values of a multi-selection row, in order."""
    return [field.choices[index] for index in _multi_selected(row)]


def _int_error(row: FormRow, field: AskIntField) -> Optional[str]:
    """Return the integer row's own validation error, or None."""
    text = _entry_widget(row).get()
    done, _, reason = int_answer(text, field.nullable, field.min_value,
                                 field.max_value, field.default)
    return None if done else reason


def _multi_error(row: FormRow, field: AskMultiChoiceField) -> Optional[str]:
    """Return the multi-selection row's count error, or None."""
    count = len(_multi_selected(row))
    too_few = count < field.min_select
    too_many = field.max_select is not None and count > field.max_select
    if too_few or too_many:
        return multi_count_error(field.min_select, field.max_select)
    return None


def _set_widget_state(row: FormRow, enabled: bool) -> None:
    """Enable or disable a row's input widget, keeping combo read-only."""
    if row.path is not None:
        row.path.set_enabled(enabled)
        return
    active = 'readonly' if isinstance(row.widget, ttk.Combobox) else 'normal'
    row.widget['state'] = active if enabled else 'disabled'


def _enable_row(row: FormRow, enabled: bool) -> None:
    """Enable or disable one form row, greying its label when disabled."""
    _set_widget_state(row, enabled)
    row.label.configure(fg='black' if enabled else 'grey')


def _row_tooltip(field: AskField, label: tk.Label,
                 widget: tk.Widget) -> Optional[HelpTooltip]:
    """Return a hover tooltip for the field's help text, or None."""
    if field.help_text is None:
        return None
    return HelpTooltip(field.help_text, label, (label, widget))


class FormEditor:
    """A two-column grid that asks a whole wizard form on one screen."""

    def __init__(self, parent: tk.Misc, fields: Sequence[AskField],
                 validator: Optional[PartialFormValidator],
                 on_submit: Callable[[list[AnswerField]], None]) -> None:
        """Build one labelled input row per field, plus a status line."""
        self._validator = validator
        self._on_submit = on_submit
        self._disabled: set[int] = set()
        self._last_changed = 0
        grid = tk.Frame(parent)
        grid.pack(anchor='w', pady=6)
        self._rows = [self._build_row(grid, index, field)
                      for index, field in enumerate(fields)]
        self._status = tk.Label(parent, fg='red', wraplength=WRAP_LENGTH,
                                justify='left')
        self._status.pack(anchor='w')
        self._apply_initial()

    def _apply_initial(self) -> None:
        """Disable the initially irrelevant rows, showing no message yet."""
        if self._validator is not None:
            result = self._validator(self.answers(), 0)
            self._apply_disabled(result.disable_row_idxs)

    def _build_row(self, grid: tk.Misc, index: int,
                   field: AskField) -> FormRow:
        """Build and place one labelled input row of the grid."""
        label = tk.Label(grid, text=field.short_question, justify='left',
                         wraplength=LABEL_WRAP, anchor='w')
        label.grid(row=index, column=0, sticky='nw', padx=4, pady=3)
        built = _make_input(grid, field, partial(self._changed, index))
        built.widget.grid(row=index, column=1, sticky='w', padx=4, pady=3)
        tooltip = _row_tooltip(field, label, built.widget)
        return FormRow(field, label, built.widget, built.var, built.path,
                       tooltip)

    def answers(self) -> list[AnswerField]:
        """Return the current answer of every row, in field order."""
        return [self._read(index) for index in range(len(self._rows))]

    def submit(self) -> None:
        """Validate every enabled field and submit when all pass."""
        answers = self.answers()
        error = self._first_error()
        if error is not None:
            self._show(error)
            return
        if self._validator_blocks(answers):
            return
        self._on_submit(answers)

    def _validator_blocks(self, answers: list[AnswerField]) -> bool:
        """Run the whole-form validator and return whether it blocks."""
        if self._validator is None:
            return False
        result = self._validator(answers, self._last_changed)
        self._apply_disabled(result.disable_row_idxs)
        if not result.is_valid:
            self._show(result.message)
        return not result.is_valid

    def _changed(self, index: int) -> None:
        """React to a field change with live feedback and row enabling."""
        self._last_changed = index
        self._show(self._feedback(self.answers(), index))

    def _feedback(self, answers: list[AnswerField], index: int) -> str:
        """Return the live message for the field that just changed."""
        validator_msg = self._run_validator(answers, index)
        if index in self._disabled:
            return validator_msg
        own = self._field_error(index)
        return validator_msg if own is None else own

    def _run_validator(self, answers: list[AnswerField], index: int) -> str:
        """Apply the validator's disabled rows and return its message."""
        if self._validator is None:
            return ''
        result = self._validator(answers, index)
        self._apply_disabled(result.disable_row_idxs)
        return '' if result.is_valid else result.message

    def _first_error(self) -> Optional[str]:
        """Return the first enabled field's own error, or None."""
        for index in range(len(self._rows)):
            if index in self._disabled:
                continue
            error = self._field_error(index)
            if error is not None:
                return error
        return None

    def _apply_disabled(self, disable_row_idxs: tuple[int, ...]) -> None:
        """Enable or disable each row to match the validator result."""
        self._disabled = set(disable_row_idxs)
        for index, row in enumerate(self._rows):
            _enable_row(row, index not in self._disabled)

    def _show(self, message: str) -> None:
        """Show a status message below the form."""
        self._status.config(text=message)

    def _read(self, index: int) -> AnswerField:
        """Return the current answer of one row read from its widget."""
        row = self._rows[index]
        field = row.field
        if isinstance(field, AskTextField):
            text = _entry_widget(row).get()
            return AnswerTextField(field, text_answer(text, field.nullable,
                                                      field.default))
        if isinstance(field, AskIntField):
            return AnswerIntField(field, _int_value(row, field))
        if isinstance(field, AskPathField):
            return AnswerPathField(field, _path_value(row, field))
        if isinstance(field, AskYesNoField):
            assert row.var is not None
            return AnswerYesNoField(field, bool(row.var.get()))
        if isinstance(field, AskChoiceField):
            return AnswerChoiceField(field, _choice_value(row))
        assert isinstance(field, AskMultiChoiceField)
        return AnswerMultiChoiceField(field, _multi_values(row, field))

    def _field_error(self, index: int) -> Optional[str]:
        """Return one field's own validation error, or None when valid."""
        row = self._rows[index]
        field = row.field
        if isinstance(field, AskIntField):
            return _int_error(row, field)
        if isinstance(field, AskPathField):
            assert row.path is not None
            done, _, reason = validate_path(row.path.get(), field.path_options)
            return None if done else reason
        if isinstance(field, AskChoiceField):
            return None if _choice_value(row) is not None else _CHOICE_REQUIRED
        if isinstance(field, AskMultiChoiceField):
            return _multi_error(row, field)
        return None
