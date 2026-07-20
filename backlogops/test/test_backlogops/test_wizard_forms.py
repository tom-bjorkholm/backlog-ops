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
from pathlib import Path
from typing import Optional
import pytest
from tableio_cfg_json import AnswerPathField, AnswerTextField, \
    AskChoiceField, AskIntField, AskPathField, AskTextField, \
    AskYesNoField, WizardPathKind, WizardUiBridgeConsole
import backlogops.wizard_forms as wf
from backlogops.wizard_forms import FormField, FormResult, _as_text, \
    _parse_float, _seed_field


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


def _path_form(answers: list[str],
               seed: Optional[FormResult] = None) -> FormResult:
    """Run a one-field required path form with scripted answers."""
    fields = [wf.path_field('p', 'File', kind=WizardPathKind.FILE)]
    return wf.run_form(_console(answers), 'Path form', fields, seed=seed)


def _text_answer(field: FormField, value: Optional[str]) -> AnswerTextField:
    """Wrap a raw string as a text answer for the field's own check."""
    ask = field.ask
    assert isinstance(ask, AskTextField)
    return AnswerTextField(ask, value)


def _path_answer(field: FormField, value: Optional[Path]) -> AnswerPathField:
    """Wrap a raw Path as a path answer for the field's own check."""
    ask = field.ask
    assert isinstance(ask, AskPathField)
    return AnswerPathField(ask, value)


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


@pytest.mark.parametrize('name, taken, ok', [
    ('Ada', set(), True), ('', set(), False), (None, set(), False),
    ('ada', {'ada'}, False), ('Bo', {'ada'}, True)])
def test_unique_name_field(name: Optional[str], taken: set[str],
                           ok: bool) -> None:
    """Test a unique-name field rejects an empty or already-used name."""
    field = wf.unique_name_field('n', 'Name', taken)
    assert (field.error(_text_answer(field, name)) is None) is ok


@pytest.mark.parametrize('minimum, maximum, seed, expected', [
    (0, 2, 5, 2), (0, 2, 1, 1), (3, 9, 1, 3), (3, 9, 5, 5)])
def test_int_seed_clamped(minimum: int, maximum: int, seed: int,
                          expected: int) -> None:
    """Test a seeded integer default is clamped into the field's bounds.

    A blank answer keeps the seeded default, so the kept value shows the
    clamped default even when the seed is out of range.
    """
    field = wf.int_field('i', 'Count', default=minimum, minimum=minimum,
                         maximum=maximum)
    result = wf.run_form(_console(['']), 'Form', [field],
                         seed=FormResult({'i': seed}))
    assert result.whole('i') == expected


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


def test_path_field_built() -> None:
    """Test a path field carries its kind and is nullable when asked."""
    ask = wf.path_field('p', 'File', kind=WizardPathKind.FILE).ask
    assert isinstance(ask, AskPathField)
    assert ask.path_options.kind is WizardPathKind.FILE
    assert ask.path_options.nullable is True


@pytest.mark.parametrize('value, ok', [(Path('/tmp/x'), True), (None, False)])
def test_path_field_required(value: Optional[Path], ok: bool) -> None:
    """Test a required path field rejects a missing path."""
    field = wf.path_field('p', 'File', kind=WizardPathKind.FILE)
    assert (field.error(_path_answer(field, value)) is None) is ok


def test_path_field_value() -> None:
    """Test a path field returns the Path its answer holds."""
    field = wf.path_field('p', 'File', kind=WizardPathKind.FILE)
    assert field.value(_path_answer(field, Path('/tmp/x'))) == Path('/tmp/x')


def test_form_result_path() -> None:
    """Test the strict path getter returns its stored Path."""
    assert FormResult({'p': Path('/tmp/x')}).path('p') == Path('/tmp/x')


def test_path_form_reask() -> None:
    """Test a blank path re-asks the whole form until a path is given."""
    assert _path_form(['', '/tmp/tok.txt']).path('p') == Path('/tmp/tok.txt')


def test_path_form_seed() -> None:
    """Test a seeded path pre-fills so a blank answer keeps it."""
    result = _path_form([''], seed=FormResult({'p': '/tmp/seed.txt'}))
    assert result.path('p') == Path('/tmp/seed.txt')


@pytest.mark.parametrize('value, expected', [
    (date(2026, 1, 2), '2026-01-02'), (True, None), (2.5, '2.5'),
    (3.0, '3'), ('hi', 'hi'), (7, None)])
def test_as_text(value: object, expected: Optional[str]) -> None:
    """Test a seed value becomes a text default only for text-like types.

    A date is shown as an ISO date and a decimal in compact form, a string
    is kept as is, and a boolean or a whole number has no text default.
    """
    assert _as_text(value) == expected


@pytest.mark.parametrize('text, expected', [
    (None, None), ('', None), ('abc', None), ('2.5', 2.5), ('-1', -1.0)])
def test_parse_float(text: Optional[str], expected: Optional[float]) -> None:
    """Test a decimal parses and a blank or non-number gives None."""
    assert _parse_float(text) == expected


def test_seed_none_keeps() -> None:
    """Test a field with no seed value is left unchanged."""
    field = wf.text_field('t', 'Text')
    assert _seed_field(field, None) is field


def test_seed_field_yes_no() -> None:
    """Test a yes/no field is reseeded with its stored boolean default."""
    ask = _seed_field(wf.yes_no_field('g', 'Gate?', False), True).ask
    assert isinstance(ask, AskYesNoField)
    assert ask.default is True


def test_int_seed_no_min() -> None:
    """Test a seeded integer over the max is clamped with no minimum set."""
    field = wf.int_field('i', 'Count', default=0, maximum=2)
    result = wf.run_form(_console(['']), 'Form', [field],
                         seed=FormResult({'i': 5}))
    assert result.whole('i') == 2
