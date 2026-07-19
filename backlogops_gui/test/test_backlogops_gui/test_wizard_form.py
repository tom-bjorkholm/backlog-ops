#! /usr/local/bin/python3
"""Tests for the whole-form editor and its answer-parsing helpers."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from pathlib import Path
from typing import Optional, Sequence
import pytest
from tableio_cfg_json import AnswerFields, AnswerField, AskField, \
    PartFormValidationResult, PartialFormValidator, PathAskOptions, \
    WizardPathKind, AskTextField, AskIntField, AskPathField, AskYesNoField, \
    AskChoiceField, AskMultiChoiceField, AnswerTextField, AnswerIntField, \
    AnswerPathField, AnswerYesNoField, AnswerChoiceField, \
    AnswerMultiChoiceField
from backlogops_gui.wizard_form import FormEditor, HelpTooltip, int_answer, \
    int_text, multi_count_error, out_of_range, range_error, text_answer, \
    _INT_ERROR
from .gui_test_helpers import gui_root


@pytest.mark.parametrize('text, expected', [
    ('5', 5), ('-3', -3), ('x', None), ('', None), ('1.5', None)])
def test_int_text(text: str, expected: Optional[int]) -> None:
    """Test int_text parses a whole number or reports None."""
    assert int_text(text) == expected


@pytest.mark.parametrize('value, lo, hi, expected', [
    (5, 1, 10, False), (0, 1, 10, True), (11, 1, 10, True),
    (5, None, None, False), (5, None, 4, True), (5, 6, None, True)])
def test_out_of_range(value: int, lo: Optional[int], hi: Optional[int],
                      expected: bool) -> None:
    """Test out_of_range respects each inclusive bound."""
    assert out_of_range(value, lo, hi) is expected


@pytest.mark.parametrize('lo, hi, needle', [
    (None, 5, 'at most 5'), (1, None, 'at least 1'),
    (1, 5, 'between 1 and 5')])
def test_range_error(lo: Optional[int], hi: Optional[int],
                     needle: str) -> None:
    """Test the range error names the bounds that apply."""
    assert needle in range_error(lo, hi)


@pytest.mark.parametrize('lo, hi, needle', [
    (2, None, 'at least 2'), (3, 3, 'exactly 3'), (1, 4, 'between 1 and 4')])
def test_multi_count_error(lo: int, hi: Optional[int], needle: str) -> None:
    """Test the multi-select count error names the allowed range."""
    assert needle in multi_count_error(lo, hi)


@pytest.mark.parametrize('text, nullable, default, expected', [
    ('hi', False, None, 'hi'), ('', True, None, None), ('', False, None, ''),
    ('', False, 'd', 'd'), ('', True, 'd', 'd')])
def test_text_answer(text: str, nullable: bool, default: Optional[str],
                     expected: Optional[str]) -> None:
    """Test the default and nullable rules for a text answer."""
    assert text_answer(text, nullable, default) == expected


@pytest.mark.parametrize('text, nullable, lo, hi, default, expected', [
    ('5', False, 1, 10, None, (True, 5, None)),
    ('', False, None, None, 3, (True, 3, None)),
    ('', True, None, None, None, (True, None, None)),
    ('', False, None, None, None, (False, None, _INT_ERROR)),
    ('x', False, None, None, None, (False, None, _INT_ERROR)),
    ('20', False, 1, 10, None,
     (False, None, 'Please enter an integer between 1 and 10.'))])
# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def test_int_answer(text: str, nullable: bool, lo: Optional[int],
                    hi: Optional[int], default: Optional[int],
                    expected: tuple[bool, Optional[int], Optional[str]]
                    ) -> None:
    """Test int_answer reports its value or a re-ask reason."""
    assert int_answer(text, nullable, lo, hi, default) == expected


def _build(root: tk.Tk, fields: Sequence[AskField],
           validator: Optional[PartialFormValidator] = None
           ) -> tuple[FormEditor, list[list[AnswerField]]]:
    """Build a form editor recording every submitted answer set."""
    recorded: list[list[AnswerField]] = []
    editor = FormEditor(tk.Frame(root), fields, validator, recorded.append)
    return editor, recorded


def test_form_text_default() -> None:
    """Test a text field starts from its default answer."""
    with gui_root() as root:
        field = AskTextField('Name', None, default='Bob')
        editor, _ = _build(root, [field])
        assert editor.answers() == [AnswerTextField(field, 'Bob')]


def test_form_sensitive_masks() -> None:
    """Test a sensitive text field masks its entry text."""
    with gui_root() as root:
        field = AskTextField('PW', None, sensitive=True)
        editor, _ = _build(root, [field])
        # pylint: disable-next=protected-access
        widget = editor._rows[0].widget
        assert isinstance(widget, tk.Entry) and widget.cget('show') == '*'


def test_form_int_default() -> None:
    """Test an integer field starts from its default answer."""
    with gui_root() as root:
        field = AskIntField('Age', None, default=7)
        editor, _ = _build(root, [field])
        assert editor.answers() == [AnswerIntField(field, 7)]


def test_form_yes_no_default() -> None:
    """Test a yes/no field starts from its default answer."""
    with gui_root() as root:
        field = AskYesNoField('OK?', None, default=True)
        editor, _ = _build(root, [field])
        assert editor.answers() == [AnswerYesNoField(field, True)]


def test_form_multi_default() -> None:
    """Test a multi-select field starts with its defaults selected."""
    with gui_root() as root:
        field = AskMultiChoiceField('Cols', None, choices=('a', 'b', 'c'),
                                    default=('a', 'c'))
        editor, _ = _build(root, [field])
        answer = editor.answers()[0]
        assert isinstance(answer, AnswerMultiChoiceField)
        assert answer.value == ['a', 'c']


def test_form_submit_ok() -> None:
    """Test submitting a valid form passes the answers on."""
    with gui_root() as root:
        field = AskChoiceField('Pick', None, choices=('a', 'b'), default='a')
        editor, recorded = _build(root, [field])
        editor.submit()
        assert recorded == [[AnswerChoiceField(field, 'a')]]


def test_form_choice_required() -> None:
    """Test a choice with no default blocks submit until answered."""
    with gui_root() as root:
        field = AskChoiceField('Pick', None, choices=('a', 'b'))
        editor, recorded = _build(root, [field])
        assert editor.answers() == [AnswerChoiceField(field, None)]
        editor.submit()
        assert not recorded
        # pylint: disable-next=protected-access
        assert editor._status.cget('text') != ''


def test_form_int_oor_blocks() -> None:
    """Test an out-of-range integer blocks submit and is reported."""
    with gui_root() as root:
        field = AskIntField('Age', None, min_value=1, max_value=5)
        editor, recorded = _build(root, [field])
        # pylint: disable-next=protected-access
        entry = editor._rows[0].widget
        assert isinstance(entry, tk.Entry)
        entry.insert(0, '9')
        editor.submit()
        assert not recorded
        # pylint: disable-next=protected-access
        assert 'between 1 and 5' in editor._status.cget('text')


def test_form_multi_min() -> None:
    """Test selecting fewer than the minimum blocks submit."""
    with gui_root() as root:
        field = AskMultiChoiceField('Cols', None, choices=('a', 'b'),
                                    min_select=1)
        editor, recorded = _build(root, [field])
        editor.submit()
        assert not recorded


def test_form_path_value(tmp_path: Path) -> None:
    """Test a path field reports and submits its accepted default path."""
    with gui_root() as root:
        target = tmp_path / 'f.txt'
        target.write_text('x')
        options = PathAskOptions(kind=WizardPathKind.EXISTING_FILE,
                                 default=target)
        field = AskPathField('File', None, options)
        editor, recorded = _build(root, [field])
        assert editor.answers() == [AnswerPathField(field, target)]
        editor.submit()
        assert recorded == [[AnswerPathField(field, target)]]


def test_form_path_required() -> None:
    """Test an empty required path blocks submit."""
    with gui_root() as root:
        field = AskPathField('File', None,
                             PathAskOptions(kind=WizardPathKind.FILE))
        editor, recorded = _build(root, [field])
        editor.submit()
        assert not recorded
        # pylint: disable-next=protected-access
        assert editor._status.cget('text') != ''


def _invalid(_answers: AnswerFields, _index: int) -> PartFormValidationResult:
    """Return a validator result that always rejects the form."""
    return PartFormValidationResult(False, 'nope')


def test_form_valid_blocks() -> None:
    """Test a rejecting validator blocks submit and shows its message."""
    with gui_root() as root:
        field = AskTextField('Name', None, default='x')
        editor, recorded = _build(root, [field], _invalid)
        editor.submit()
        assert not recorded
        # pylint: disable-next=protected-access
        assert editor._status.cget('text') == 'nope'


def _disable_second(_answers: AnswerFields,
                    _index: int) -> PartFormValidationResult:
    """Return a validator result that disables the second row."""
    return PartFormValidationResult(True, '', (1,))


def test_form_valid_disable() -> None:
    """Test a disabled row is skipped so its own error never blocks."""
    with gui_root() as root:
        first = AskChoiceField('Fmt', None, choices=('a', 'b'), default='a')
        second = AskChoiceField('Delim', None, choices=(',', ';'))
        editor, recorded = _build(root, [first, second], _disable_second)
        # pylint: disable-next=protected-access
        assert 1 in editor._disabled
        editor.submit()
        assert len(recorded) == 1
        answers = recorded[0]
        assert answers[1] == AnswerChoiceField(second, None)


def test_form_live_error() -> None:
    """Test a field change shows the changed field's own error live."""
    with gui_root() as root:
        field = AskIntField('Age', None, min_value=1, max_value=5)
        editor, _ = _build(root, [field])
        # pylint: disable-next=protected-access
        entry = editor._rows[0].widget
        assert isinstance(entry, tk.Entry)
        entry.insert(0, '9')
        # pylint: disable-next=protected-access
        editor._changed(0)
        # pylint: disable-next=protected-access
        assert 'between 1 and 5' in editor._status.cget('text')


def test_form_disable_state() -> None:
    """Test applying and clearing disabled rows toggles widget state."""
    with gui_root() as root:
        field = AskTextField('Name', None)
        editor, _ = _build(root, [field])
        # pylint: disable-next=protected-access
        editor._apply_disabled((0,))
        # pylint: disable-next=protected-access
        row = editor._rows[0]
        assert str(row.widget.cget('state')) == 'disabled'
        # pylint: disable-next=protected-access
        editor._apply_disabled(())
        assert str(row.widget.cget('state')) == 'normal'


def test_form_tooltip_help() -> None:
    """Test a field with help text gets a tooltip carrying that text."""
    with gui_root() as root:
        field = AskTextField('Name', 'Type your name')
        editor, _ = _build(root, [field])
        # pylint: disable-next=protected-access
        row = editor._rows[0]
        assert row.tooltip is not None
        assert row.tooltip.text == 'Type your name'


def test_form_no_tooltip() -> None:
    """Test a field without help text gets no tooltip."""
    with gui_root() as root:
        field = AskTextField('Name', None)
        editor, _ = _build(root, [field])
        # pylint: disable-next=protected-access
        assert editor._rows[0].tooltip is None


def _bubbles(anchor: tk.Widget) -> list[tk.Toplevel]:
    """Return the tooltip top-level windows parented to a widget."""
    return [child for child in anchor.winfo_children()
            if isinstance(child, tk.Toplevel)]


def test_tooltip_show_hide() -> None:
    """Test showing then hiding a tooltip creates and removes its bubble."""
    with gui_root() as root:
        anchor = tk.Label(root, text='x')
        tip = HelpTooltip('help me', anchor, (anchor,))
        tip.show()
        assert len(_bubbles(anchor)) == 1
        tip.hide()
        assert not _bubbles(anchor)
