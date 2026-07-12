#! /usr/local/bin/python3
"""Reusable building blocks for the one-screen backlog-ops wizard forms.

A wizard form asks several related scalar questions on a single screen
through the ``ask_form`` method of a ``WizardUiBridge``. Each question is a
:class:`FormField` that pairs an ``AskField`` (what the bridge shows) with a
validator and a parser. The builder functions (:func:`text_field`,
:func:`date_field`, :func:`number_field` and friends) create the common
field kinds, so a wizard only lists the fields and, when needed, a ``rule``.

A ``rule`` is called with the current :class:`FormResult` after every change.
It returns a message for a cross-field problem, such as two pass phrases that
differ or an end date before its start date, and the keys of the fields that
the answers so far make irrelevant. :func:`run_form` shows the fields,
disables the irrelevant ones, blocks an invalid form and returns the typed
answers as a :class:`FormResult`.

Dates and decimals have no native field type, so they are asked as text
fields validated here. :func:`_parse_date` and :func:`_num_text` are shared
with the table-based wizard helpers.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass
from datetime import date
from typing import Callable, Optional, Sequence
from tableio_cfg_json import AnswerField, AskChoiceField, AskField, \
    AskIntField, AskTextField, AskYesNoField, PartFormValidationResult, \
    WizardUiBridge
from backlogops.io_config import PRESET_NAME_RE

_REQUIRED = 'Please enter a value.'
_NUMBER_ERROR = 'Please enter a number.'
_DATE_ERROR = 'Please enter a date as YYYY-MM-DD.'
_NAME_ERROR = 'Use only letters and digits for a name.'
_CHOICE_ERROR = 'Please choose a value.'
_PHRASE_ERROR = 'Please enter a pass phrase.'
_INVALID_FORM = 'Please correct the highlighted fields.'
_DATE_HINT = ' (YYYY-MM-DD)'
_DATE_HINT_OPT = ' (YYYY-MM-DD, blank for none)'


@dataclass(frozen=True)
class FormField:
    """One form field: what to ask, how to validate and how to parse it.

    Attributes:
        key: The name the wizard uses to read this field's answer.
        ask: The question the bridge shows for the field.
        error: Returns a message for an invalid answer, or None when valid.
        value: Returns the typed answer, such as a date or a float.
    """

    key: str
    ask: AskField
    error: Callable[[AnswerField], Optional[str]]
    value: Callable[[AnswerField], object]


class FormResult:
    """Typed answers of a form, read by field key with strict getters."""

    def __init__(self, values: dict[str, object]) -> None:
        """Store the parsed value of each field, keyed by field key."""
        self._values = values

    def text(self, key: str) -> str:
        """Return a required text or choice answer as a string."""
        value = self._values[key]
        assert isinstance(value, str)
        return value

    def opt_text(self, key: str) -> Optional[str]:
        """Return an optional text answer, or None when left blank."""
        value = self._values[key]
        assert value is None or isinstance(value, str)
        return value

    def flag(self, key: str) -> bool:
        """Return a yes/no answer as a boolean."""
        value = self._values[key]
        assert isinstance(value, bool)
        return value

    def whole(self, key: str) -> int:
        """Return an integer answer."""
        value = self._values[key]
        assert isinstance(value, int) and not isinstance(value, bool)
        return value

    def number(self, key: str) -> float:
        """Return a decimal answer as a float."""
        value = self._values[key]
        assert isinstance(value, float)
        return value

    def day(self, key: str) -> date:
        """Return a required date answer."""
        value = self._values[key]
        assert isinstance(value, date)
        return value

    def opt_day(self, key: str) -> Optional[date]:
        """Return an optional date answer, or None when left blank."""
        value = self._values[key]
        assert value is None or isinstance(value, date)
        return value


def _no_rule(_values: FormResult) -> tuple[Optional[str], set[str]]:
    """Enable every field and report no cross-field problem."""
    return None, set()


def run_form(bridge: WizardUiBridge, question: str,
             fields: Sequence[FormField],
             rule: Callable[[FormResult], tuple[Optional[str], set[str]]]
             = _no_rule) -> FormResult:
    """Ask a whole form and return its validated, typed answers.

    The rule disables the fields that the current answers make irrelevant
    and reports any cross-field problem. A bridge that validates on submit
    returns only valid answers; a plain console bridge may return an
    invalid form, which is re-asked with the blocking message shown.
    """
    asks = [field.ask for field in fields]

    def validate(answers: Sequence[AnswerField],
                 changed: int) -> PartFormValidationResult:
        """Validate the current answers for the bridge's live feedback."""
        return _validate(fields, rule, list(answers), changed)
    reason: Optional[str] = None
    while True:
        answers = list(bridge.ask_form(question, asks, re_ask_reason=reason,
                                       partial_validator=validate))
        outcome = _validate(fields, rule, answers, len(fields) - 1)
        if outcome.is_valid:
            return FormResult(_values_of(fields, answers))
        reason = outcome.message or _INVALID_FORM


def _values_of(fields: Sequence[FormField],
               answers: Sequence[AnswerField]) -> dict[str, object]:
    """Return the typed value of every field, keyed by field key."""
    return {field.key: field.value(answer)
            for field, answer in zip(fields, answers)}


def _validate(fields: Sequence[FormField],
              rule: Callable[[FormResult], tuple[Optional[str], set[str]]],
              answers: list[AnswerField],
              changed: int) -> PartFormValidationResult:
    """Run the rule and the field checks into one validation result."""
    message, disabled_keys = rule(FormResult(_values_of(fields, answers)))
    errors = _field_errors(fields, answers, disabled_keys)
    disabled = tuple(index for index, field in enumerate(fields)
                     if field.key in disabled_keys)
    valid = message is None and not errors
    return PartFormValidationResult(valid, _message(errors, message, changed),
                                    disabled)


def _field_errors(fields: Sequence[FormField], answers: list[AnswerField],
                  disabled_keys: set[str]) -> dict[int, str]:
    """Return the own error of every enabled field, keyed by row index."""
    errors: dict[int, str] = {}
    for index, field in enumerate(fields):
        if field.key in disabled_keys:
            continue
        error = field.error(answers[index])
        if error is not None:
            errors[index] = error
    return errors


def _message(errors: dict[int, str], rule_message: Optional[str],
             changed: int) -> str:
    """Return the most relevant message to show below the form."""
    if changed in errors:
        return errors[changed]
    if rule_message is not None:
        return rule_message
    if errors:
        return errors[min(errors)]
    return ''


def _answer_text(answer: AnswerField) -> Optional[str]:
    """Return the string an answer holds, or None when it holds none."""
    value = answer.value
    assert value is None or isinstance(value, str)
    return value


def _parse_date(answer: str) -> Optional[date]:
    """Return the ISO date in ``answer``, or None when it is invalid."""
    try:
        return date.fromisoformat(answer)
    except ValueError:
        return None


def _num_text(value: float) -> str:
    """Return a compact decimal text for a default numeric value."""
    return f'{value:g}'


def _parse_float(text: Optional[str]) -> Optional[float]:
    """Return the float in ``text``, or None when it is not a number."""
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def name_error(name: Optional[str], used: set[str]) -> Optional[str]:
    """Return why a preset-style name is invalid, or None when it is fine."""
    if name is None or PRESET_NAME_RE.match(name) is None:
        return _NAME_ERROR
    if name in used:
        return f'The name {name!r} is already used.'
    return None


def text_field(key: str, question: str, *,
               help_text: Optional[str] = None) -> FormField:
    """Return a required free-text field."""
    ask = AskTextField(question, help_text, nullable=True)

    def error(answer: AnswerField) -> Optional[str]:
        """Reject an empty required text answer."""
        return None if _answer_text(answer) else _REQUIRED
    return FormField(key, ask, error, _answer_text)


def opt_text_field(key: str, question: str, *,
                   help_text: Optional[str] = None) -> FormField:
    """Return an optional free-text field that may be left blank."""
    ask = AskTextField(question, help_text, nullable=True)
    return FormField(key, ask, _no_error, _answer_text)


def secret_field(key: str, question: str, *,
                 help_text: Optional[str] = None) -> FormField:
    """Return a required masked field, such as a pass phrase."""
    ask = AskTextField(question, help_text, nullable=True, sensitive=True)

    def error(answer: AnswerField) -> Optional[str]:
        """Reject an empty pass phrase."""
        return None if _answer_text(answer) else _PHRASE_ERROR
    return FormField(key, ask, error, _answer_text)


def name_field(key: str, question: str, used: set[str], *,
               help_text: Optional[str] = None) -> FormField:
    """Return a field for a unique letters-and-digits name."""
    ask = AskTextField(question, help_text, nullable=True)

    def error(answer: AnswerField) -> Optional[str]:
        """Reject a badly formed or already used name."""
        return name_error(_answer_text(answer), used)
    return FormField(key, ask, error, _answer_text)


def choice_field(key: str, question: str, choices: Sequence[str], *,
                 default: Optional[str] = None,
                 help_text: Optional[str] = None) -> FormField:
    """Return a single-choice field, optionally with a default choice."""
    ask = AskChoiceField(question, help_text, choices=list(choices),
                         default=default)

    def error(answer: AnswerField) -> Optional[str]:
        """Reject a choice field with nothing chosen."""
        return None if _answer_text(answer) else _CHOICE_ERROR
    return FormField(key, ask, error, _answer_text)


def yes_no_field(key: str, question: str, default: bool, *,
                 help_text: Optional[str] = None) -> FormField:
    """Return a yes/no field with the given default."""
    ask = AskYesNoField(question, help_text, default)
    return FormField(key, ask, _no_error, _flag_value)


def int_field(key: str, question: str, *, default: int,
              minimum: Optional[int] = None,
              maximum: Optional[int] = None) -> FormField:
    """Return an integer field pre-filled with its default."""
    ask = AskIntField(question, None, default=default, min_value=minimum,
                      max_value=maximum)
    return FormField(key, ask, _no_error, _int_value)


def number_field(key: str, question: str, *, default: float,
                 minimum: Optional[float] = None,
                 maximum: Optional[float] = None) -> FormField:
    """Return a decimal field pre-filled with its default."""
    ask = AskTextField(question, None, nullable=True,
                       default=_num_text(default))

    def error(answer: AnswerField) -> Optional[str]:
        """Reject a non-numeric or out-of-range decimal answer."""
        return _number_error(_answer_text(answer), minimum, maximum)

    def value(answer: AnswerField) -> object:
        """Return the entered decimal, or the default for a blank answer."""
        parsed = _parse_float(_answer_text(answer))
        return default if parsed is None else parsed
    return FormField(key, ask, error, value)


def date_field(key: str, question: str, *,
               help_text: Optional[str] = None) -> FormField:
    """Return a required ISO date field, asked as validated text."""
    ask = AskTextField(question + _DATE_HINT, help_text, nullable=True)

    def error(answer: AnswerField) -> Optional[str]:
        """Reject a missing or malformed required date."""
        return _date_error(_answer_text(answer), required=True)
    return FormField(key, ask, error, _date_value)


def opt_date_field(key: str, question: str, *,
                   help_text: Optional[str] = None) -> FormField:
    """Return an optional ISO date field that may be left blank."""
    ask = AskTextField(question + _DATE_HINT_OPT, help_text, nullable=True)

    def error(answer: AnswerField) -> Optional[str]:
        """Reject a malformed date but accept a blank one."""
        return _date_error(_answer_text(answer), required=False)
    return FormField(key, ask, error, _date_value)


def _no_error(_answer: AnswerField) -> Optional[str]:
    """Report no own error for a field that validates itself."""
    return None


def _flag_value(answer: AnswerField) -> object:
    """Return the boolean an answer holds."""
    value = answer.value
    assert isinstance(value, bool)
    return value


def _int_value(answer: AnswerField) -> object:
    """Return the integer an answer holds."""
    value = answer.value
    assert isinstance(value, int)
    return value


def _date_value(answer: AnswerField) -> object:
    """Return the date an answer holds, or None when it is blank."""
    text = _answer_text(answer)
    return _parse_date(text) if text else None


def _number_error(text: Optional[str], minimum: Optional[float],
                  maximum: Optional[float]) -> Optional[str]:
    """Return why a decimal answer is invalid, or None when it is fine."""
    if not text:
        return None
    value = _parse_float(text)
    if value is None:
        return _NUMBER_ERROR
    if minimum is not None and value < minimum:
        return f'Please enter a value of at least {minimum:g}.'
    if maximum is not None and value > maximum:
        return f'Please enter a value of at most {maximum:g}.'
    return None


def _date_error(text: Optional[str], required: bool) -> Optional[str]:
    """Return why a date answer is invalid, or None when it is fine."""
    if not text:
        return _DATE_ERROR if required else None
    return None if _parse_date(text) else _DATE_ERROR
