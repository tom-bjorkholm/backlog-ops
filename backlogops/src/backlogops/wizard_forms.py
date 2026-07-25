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

A form may also pass a ``prefill`` callback. It is called with the current
:class:`FormResult` and the key of the field that just changed, and returns
``(key, value)`` requests that offer a value to another field as its live
default, exactly as if the user had typed it. This lets one field be derived
from others, such as a Jira filter derived from the project key, while the
user stays free to override the offered value.

Dates use :class:`AskDateField` (a calendar picker in a graphical bridge) and
decimals use :class:`AskFloatField`, so both come back as typed answers, with
their format and range checked by the field rather than by validated text.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from typing import Callable, Optional, Sequence
from tableio_cfg_json import AnswerField, AskChoiceField, AskDateField, \
    AskField, AskFloatField, AskIntField, AskPathField, AskTextField, \
    AskYesNoField, PartFormValidationResult, PathAskOptions, PrefillValues, \
    PrefillValueType, WizardPathKind, WizardUiBridge
from backlogops.io_config import PRESET_NAME_RE

_REQUIRED = 'Please enter a value.'
_DATE_ERROR = 'Please enter a date.'
_NAME_ERROR = 'Use only letters and digits for a name.'
_CHOICE_ERROR = 'Please choose a value.'
_PHRASE_ERROR = 'Please enter a pass phrase.'
_INVALID_FORM = 'Please correct the highlighted fields.'


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

    def path(self, key: str) -> Path:
        """Return a required path answer."""
        value = self._values[key]
        assert isinstance(value, Path)
        return value

    def raw(self, key: str) -> object:
        """Return the parsed value of a field, or None when it is absent."""
        return self._values.get(key)


def _no_rule(_values: FormResult) -> tuple[Optional[str], set[str]]:
    """Enable every field and report no cross-field problem."""
    return None, set()


def _no_prefill(_values: FormResult,
                _changed: str) -> list[tuple[str, PrefillValueType]]:
    """Offer no field a derived default."""
    return []


def _seeded_fields(fields: Sequence[FormField],
                   seed: Optional[FormResult]) -> list[FormField]:
    """Return the fields with each ask pre-filled from a seed result."""
    if seed is None:
        return list(fields)
    return [_seed_field(field, seed.raw(field.key)) for field in fields]


def _seed_field(field: FormField, value: object) -> FormField:
    """Return a copy of a field whose ask starts on a seed value."""
    if value is None:
        return field
    return replace(field, ask=_reseed_ask(field.ask, value))


def _reseed_ask(ask: AskField, value: object) -> AskField:
    """Return a copy of an ask field with its default set from a value."""
    if isinstance(ask, AskYesNoField):
        return replace(ask, default=bool(value))
    if isinstance(ask, AskIntField) and isinstance(value, int) \
            and not isinstance(value, bool):
        return replace(ask, default=_clamped_int(value, ask))
    if isinstance(ask, AskPathField) and isinstance(value, str) and value:
        options = replace(ask.path_options, default=Path(value))
        return replace(ask, path_options=options)
    return _reseed_typed(ask, value)


def _reseed_typed(ask: AskField, value: object) -> AskField:
    """Return ask reseeded for the value-typed fields, else unchanged."""
    if isinstance(ask, AskFloatField) and isinstance(value, float):
        return replace(ask, default=value)
    if isinstance(ask, AskDateField) and isinstance(value, date):
        return replace(ask, default=value)
    if isinstance(ask, AskChoiceField) and isinstance(value, str) \
            and value in ask.choices:
        return replace(ask, default=value)
    if isinstance(ask, AskTextField) and not ask.sensitive \
            and isinstance(value, str):
        return replace(ask, default=value)
    return ask


def _clamped_int(value: int, ask: AskIntField) -> int:
    """Return an integer default clamped into the field's inclusive bounds.

    A remembered count seeded above a now-smaller maximum, such as a
    member count above the current number of persons, is offered at the
    maximum instead of failing the field's range check.
    """
    if ask.min_value is not None:
        value = max(value, ask.min_value)
    if ask.max_value is not None:
        value = min(value, ask.max_value)
    return value


# pylint: disable-next=too-many-arguments
def run_form(bridge: WizardUiBridge, question: str,
             fields: Sequence[FormField],
             rule: Callable[[FormResult], tuple[Optional[str], set[str]]]
             = _no_rule, *,
             prefill: Callable[[FormResult, str],
                               list[tuple[str, PrefillValueType]]]
             = _no_prefill,
             seed: Optional[FormResult] = None) -> FormResult:
    """Ask a whole form and return its validated, typed answers.

    The rule disables the fields that the current answers make irrelevant
    and reports any cross-field problem. The prefill callback offers a
    derived value to another field after each change, ignored on submit so
    the caller must still apply the same default itself. A bridge that
    validates on submit returns only valid answers; a plain console bridge
    may return an invalid form, which is re-asked with the blocking message
    shown. When a ``seed`` result is given each field starts pre-filled with
    its seed value, so a re-asked or default-driven form opens on the earlier
    answers; sensitive fields keep no default and are always asked afresh.
    """
    fields = _seeded_fields(fields, seed)
    asks = [field.ask for field in fields]

    def validate(answers: Sequence[AnswerField],
                 changed: int) -> PartFormValidationResult:
        """Validate the current answers for the bridge's live feedback."""
        return _validate(fields, rule, list(answers), changed, prefill)
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
              answers: list[AnswerField], changed: int,
              prefill: Callable[[FormResult, str],
                                list[tuple[str, PrefillValueType]]]
              = _no_prefill) -> PartFormValidationResult:
    """Run the rule, the field checks and the prefill into one result."""
    values = FormResult(_values_of(fields, answers))
    message, disabled_keys = rule(values)
    errors = _field_errors(fields, answers, disabled_keys)
    disabled = tuple(index for index, field in enumerate(fields)
                     if field.key in disabled_keys)
    valid = message is None and not errors
    prefills = _prefills(fields, values, changed, prefill)
    return PartFormValidationResult(valid, _message(errors, message, changed),
                                    disabled, prefills)


def _prefills(fields: Sequence[FormField], values: FormResult, changed: int,
              prefill: Callable[[FormResult, str],
                                list[tuple[str, PrefillValueType]]]
              ) -> PrefillValues:
    """Translate the prefill callback's key requests into row indexes."""
    index_of = {field.key: index for index, field in enumerate(fields)}
    return tuple((index_of[key], value)
                 for key, value in prefill(values, fields[changed].key))


def _field_errors(fields: Sequence[FormField], answers: list[AnswerField],
                  disabled_keys: set[str]) -> dict[int, str]:
    """Return the labelled own error of each enabled field, by row index.

    Each message is prefixed with the field's label so a form that shows
    every field at once makes clear which field the message refers to.
    """
    errors: dict[int, str] = {}
    for index, field in enumerate(fields):
        if field.key in disabled_keys:
            continue
        error = field.error(answers[index])
        if error is not None:
            errors[index] = f'{field.ask.short_question}: {error}'
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


def _answer_path(answer: AnswerField) -> Optional[Path]:
    """Return the Path an answer holds, or None when it holds none."""
    value = answer.value
    assert value is None or isinstance(value, Path)
    return value


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


def path_field(key: str, question: str, *, kind: WizardPathKind,
               help_text: Optional[str] = None) -> FormField:
    """Return a required path field shown with a native file picker.

    A graphical bridge asks the path with a file picker and every bridge
    validates the answer against ``kind``. The field is nullable at the ask
    level so a single-field prompt does not loop on an empty answer; an
    empty required path is rejected here, as for a required text field.
    """
    options = PathAskOptions(kind=kind, nullable=True)
    ask = AskPathField(question, help_text, path_options=options)

    def error(answer: AnswerField) -> Optional[str]:
        """Reject an empty required path answer."""
        return None if _answer_path(answer) else _REQUIRED
    return FormField(key, ask, error, _answer_path)


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


def unique_name_field(key: str, question: str, taken: set[str], *,
                      help_text: Optional[str] = None) -> FormField:
    """Return a required free-text field whose value must be unused.

    The answer must be non-empty and, compared case-insensitively, must
    not already be one of ``taken``, which holds the lower-cased names
    already in use. This suits a person name that must be unique but may
    otherwise contain any characters, unlike the stricter name_field.
    """
    ask = AskTextField(question, help_text, nullable=True)

    def error(answer: AnswerField) -> Optional[str]:
        """Reject an empty name or one already used, case-insensitively."""
        text = _answer_text(answer)
        if not text:
            return _REQUIRED
        if text.lower() in taken:
            return f'The name {text!r} is already used.'
        return None
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
    """Return a decimal field pre-filled with its default.

    The field itself checks that the answer is a number within the
    inclusive bounds and returns the default for a blank answer.
    """
    ask = AskFloatField(question, None, default=default, min_value=minimum,
                        max_value=maximum)
    return FormField(key, ask, _no_error, _float_value)


def date_field(key: str, question: str, *,
               help_text: Optional[str] = None) -> FormField:
    """Return a required date field, shown with a calendar picker."""
    ask = AskDateField(question, help_text, nullable=True)

    def error(answer: AnswerField) -> Optional[str]:
        """Reject a missing required date."""
        return None if _answer_date(answer) is not None else _DATE_ERROR
    return FormField(key, ask, error, _answer_date)


def opt_date_field(key: str, question: str, *,
                   help_text: Optional[str] = None) -> FormField:
    """Return an optional date field that may be left blank."""
    ask = AskDateField(question, help_text, nullable=True)
    return FormField(key, ask, _no_error, _answer_date)


def _no_error(_answer: AnswerField) -> Optional[str]:
    """Report no own error for a field that validates itself."""
    return None


def _flag_value(answer: AnswerField) -> object:
    """Return the boolean an answer holds."""
    value = answer.value
    assert isinstance(value, bool)
    return value


def _int_value(answer: AnswerField) -> object:
    """Return the integer an answer holds, or None when not yet valid.

    A graphical or textual bridge runs the validator after every change,
    so a field may still be empty or out of range; the strict FormResult
    getters check the type only when the accepted answer is read.
    """
    value = answer.value
    assert value is None or isinstance(value, int)
    return value


def _float_value(answer: AnswerField) -> object:
    """Return the decimal an answer holds, or None when not yet valid."""
    value = answer.value
    assert value is None or isinstance(value, float)
    return value


def _answer_date(answer: AnswerField) -> Optional[date]:
    """Return the date an answer holds, or None when it is blank."""
    value = answer.value
    assert value is None or isinstance(value, date)
    return value
