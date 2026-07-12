#! /usr/local/bin/python3
"""Tests for the reusable one-screen wizard form toolkit.

The end-to-end tests drive :func:`run_form` through a scripted console
bridge, which asks each enabled field in turn and re-asks the whole form
when a value fails validation. The focused tests check the individual
builders, the strict :class:`FormResult` getters and the name validator.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
from typing import Optional
import pytest
from tableio_cfg_json import AnswerTextField, AskChoiceField, AskIntField, \
    AskTextField, WizardUiBridgeConsole
import backlogops.wizard_forms as wf
from backlogops.wizard_forms import FormField, FormResult


def _console(answers: list[str]) -> WizardUiBridgeConsole:
    """Return a console bridge scripted with the given answers."""
    text = '\n'.join(answers) + '\n'
    return WizardUiBridgeConsole(io.StringIO(), io.StringIO(text),
                                 io.StringIO())


def _demo_fields() -> list[FormField]:
    """Return a mixed demo form with a gated optional text field."""
    return [wf.yes_no_field('gate', 'Add an extra value?', False),
            wf.text_field('extra', 'Extra value'),
            wf.number_field('amount', 'Amount', default=1.0, minimum=0.0,
                            maximum=10.0),
            wf.date_field('when', 'When'),
            wf.choice_field('kind', 'Kind', ['a', 'b'], default='a')]


def _demo_rule(values: FormResult) -> tuple[Optional[str], set[str]]:
    """Disable the extra value when the gate is off; block amount two."""
    disabled = set() if values.flag('gate') else {'extra'}
    if values.number('amount') == 2.0:
        return 'Amount two is not allowed.', disabled
    return None, disabled


def _run_demo(answers: list[str]) -> FormResult:
    """Run the demo form with scripted console answers."""
    return wf.run_form(_console(answers), 'Demo form', _demo_fields(),
                       _demo_rule)


def _text_answer(field: FormField, value: Optional[str]) -> AnswerTextField:
    """Wrap a raw string as a text answer for the field's own check."""
    ask = field.ask
    assert isinstance(ask, AskTextField)
    return AnswerTextField(ask, value)


def _text_default(field: FormField) -> Optional[str]:
    """Return the pre-filled default text shown for a text field."""
    ask = field.ask
    assert isinstance(ask, AskTextField)
    return ask.default


def test_demo_valid() -> None:
    """Test a fully valid form parses each field to its typed value."""
    result = _run_demo(['yes', 'hello', '5', '2026-01-02', 'b'])
    assert result.flag('gate') is True
    assert result.text('extra') == 'hello'
    assert result.number('amount') == 5.0
    assert result.day('when') == date(2026, 1, 2)
    assert result.text('kind') == 'b'


def test_demo_disabled_skip() -> None:
    """Test a disabled field is not asked and keeps its blank value."""
    result = _run_demo(['no', '5', '2026-01-02', 'a'])
    assert result.flag('gate') is False
    assert result.opt_text('extra') is None
    assert result.number('amount') == 5.0


def test_demo_number_reask() -> None:
    """Test an out-of-range amount re-asks the whole form."""
    result = _run_demo(['no', '20', '2026-01-02', 'a',
                        'no', '5', '2026-01-02', 'a'])
    assert result.number('amount') == 5.0


def test_demo_date_reask() -> None:
    """Test a malformed date re-asks the whole form until it parses."""
    result = _run_demo(['no', '5', 'not-a-date', 'a',
                        'no', '5', '2026-01-02', 'a'])
    assert result.day('when') == date(2026, 1, 2)


def test_demo_rule_blocks() -> None:
    """Test a cross-field rule blocks and re-asks with its message."""
    result = _run_demo(['no', '2', '2026-01-02', 'a',
                        'no', '5', '2026-01-02', 'a'])
    assert result.number('amount') == 5.0


def test_demo_default_amount() -> None:
    """Test a blank amount takes the pre-filled default."""
    result = _run_demo(['no', '', '2026-01-02', 'a'])
    assert result.number('amount') == 1.0


def test_form_result_getters() -> None:
    """Test every strict getter returns its stored typed value."""
    result = FormResult({'t': 'hi', 'n': 2.5, 'i': 3, 'b': True,
                         'd': date(2026, 1, 2), 'o': None})
    assert result.text('t') == 'hi'
    assert result.number('n') == 2.5
    assert result.whole('i') == 3
    assert result.flag('b') is True
    assert result.day('d') == date(2026, 1, 2)
    assert result.opt_text('o') is None
    assert result.opt_day('o') is None


@pytest.mark.parametrize('name, used, ok', [
    ('good1', set(), True), ('with space', set(), False),
    ('', set(), False), (None, set(), False), ('dup', {'dup'}, False)])
def test_name_error(name: Optional[str], used: set[str], ok: bool) -> None:
    """Test only a letters-and-digits name that is unused is accepted."""
    assert (wf.name_error(name, used) is None) is ok


def test_secret_field_masked() -> None:
    """Test a secret field is masked and refuses a default value."""
    ask = wf.secret_field('p', 'Pass phrase').ask
    assert isinstance(ask, AskTextField)
    assert ask.sensitive is True
    assert ask.default is None


def test_choice_field_built() -> None:
    """Test a choice field carries its choices and default."""
    ask = wf.choice_field('k', 'Kind', ['a', 'b'], default='b').ask
    assert isinstance(ask, AskChoiceField)
    assert list(ask.choices) == ['a', 'b']
    assert ask.default == 'b'


def test_int_field_bounds() -> None:
    """Test an integer field carries its default and inclusive bounds."""
    ask = wf.int_field('i', 'Count', default=10, minimum=1).ask
    assert isinstance(ask, AskIntField)
    assert (ask.default, ask.min_value, ask.max_value) == (10, 1, None)


@pytest.mark.parametrize('default, text', [(2.5, '2.5'), (3.0, '3'),
                                           (0.0, '0')])
def test_number_default_text(default: float, text: str) -> None:
    """Test a decimal field shows a compact default text."""
    assert _text_default(wf.number_field('x', 'Q', default=default)) == text


def test_date_field_hint() -> None:
    """Test a date field appends the ISO date hint to its question."""
    ask = wf.date_field('d', 'When').ask
    assert isinstance(ask, AskTextField)
    assert ask.short_question == 'When (YYYY-MM-DD)'


@pytest.mark.parametrize('value, ok', [('hi', True), ('', False),
                                       (None, False)])
def test_text_field_required(value: Optional[str], ok: bool) -> None:
    """Test a required text field rejects an empty answer."""
    field = wf.text_field('t', 'Text')
    assert (field.error(_text_answer(field, value)) is None) is ok


@pytest.mark.parametrize('text, ok', [('5', True), ('', True), ('abc', False),
                                      ('-1', False), ('20', False)])
def test_number_field_error(text: str, ok: bool) -> None:
    """Test a decimal field rejects a non-number or out-of-range value."""
    field = wf.number_field('x', 'Q', default=0.0, minimum=0.0, maximum=10.0)
    assert (field.error(_text_answer(field, text)) is None) is ok


@pytest.mark.parametrize('text, ok', [('2026-01-02', True), ('', False),
                                      ('bad', False), ('2026-13-02', False)])
def test_date_field_error(text: str, ok: bool) -> None:
    """Test a required date field rejects a missing or malformed date."""
    field = wf.date_field('d', 'When')
    assert (field.error(_text_answer(field, text)) is None) is ok


@pytest.mark.parametrize('text, ok', [('2026-01-02', True), ('', True),
                                      ('bad', False)])
def test_opt_date_field_error(text: str, ok: bool) -> None:
    """Test an optional date field accepts a blank but not a bad date."""
    field = wf.opt_date_field('d', 'When')
    assert (field.error(_text_answer(field, text)) is None) is ok
