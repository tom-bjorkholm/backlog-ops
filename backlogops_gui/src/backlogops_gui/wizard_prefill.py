#! /usr/local/bin/python3
"""Validate a partial validator's prefill requests for the form editor.

A partial form validator may return prefill values: requests to place a
value into another row's input during live editing, as if the user had
typed it. :func:`valid_prefills` turns those requests into the ones the
Tkinter form editor should apply.

A prefill aimed at the row that just changed is skipped. A row index
outside the form raises ``IndexError`` and a value whose Python type does
not match its field raises ``TypeError``, because both are validator
bugs and should surface as early as possible. A choice value not among
the field's choices, any prefill of a sensitive text field, and a
multi-choice value with no valid member are dropped instead, so a
portable validator stays safe. These rules match the console and Textual
bridges, so a validator behaves the same on every bridge.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from collections.abc import Sequence
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterator, NoReturn, Optional
from tableio_cfg_json import AskField, PrefillValues, PrefillValueType, \
    AskTextField, AskIntField, AskPathField, AskYesNoField, AskChoiceField, \
    AskMultiChoiceField, AskFloatField, AskDateField, AskTimeField, \
    AskDateTimeField, AskDurationField

_ORDERED_FIELDS = (AskIntField, AskFloatField, AskDateField, AskTimeField,
                   AskDateTimeField, AskDurationField)


def valid_prefills(fields: Sequence[AskField], changed: int,
                   prefills: PrefillValues
                   ) -> Iterator[tuple[int, PrefillValueType]]:
    """Yield the prefill requests the form editor should apply.

    A request aimed at the changed row is skipped so writing back never
    fights the user's current edit. A row index outside the form raises
    IndexError and a value whose type does not match its field raises
    TypeError. Requests that are valid but not applicable are dropped.
    """
    for index, value in prefills:
        _check_row(fields, index)
        if index == changed:
            continue
        usable = _prefill_value(fields[index], value, index)
        if usable is not None:
            yield (index, usable)


def _check_row(fields: Sequence[AskField], index: int) -> None:
    """Raise when a prefill row index lies outside the form."""
    if not 0 <= index < len(fields):
        raise IndexError(f'prefill row index {index} is out of range')


def _prefill_value(field: AskField, value: PrefillValueType,
                   index: int) -> Optional[PrefillValueType]:
    """Return the value to apply for a prefill, or None to drop it.

    Raises TypeError when value's Python type does not match field.
    """
    if isinstance(field, _ORDERED_FIELDS):
        return _ordered_prefill(field, value, index)
    if isinstance(field, AskTextField):
        _need(value, index, str)
        return None if field.sensitive else value
    if isinstance(field, AskPathField):
        _need(value, index, Path)
        return value
    if isinstance(field, AskYesNoField):
        if not isinstance(value, bool):
            _bad_type(index)
        return value
    if isinstance(field, AskChoiceField):
        _need(value, index, str)
        return value if value in field.choices else None
    assert isinstance(field, AskMultiChoiceField)
    return _multi_prefill(field, value, index)


def _ordered_prefill(field: AskField, value: PrefillValueType,
                     index: int) -> PrefillValueType:
    """Return an ordered field's prefill, or raise TypeError for it.

    An integer or float field takes a number, and a date field takes a
    date that is not a datetime, so a datetime is never mistaken for a
    plain date. Each temporal field takes exactly its own type.
    """
    if isinstance(field, AskIntField):
        if isinstance(value, bool) or not isinstance(value, int):
            _bad_type(index)
        return value
    if isinstance(field, AskFloatField):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            _bad_type(index)
        return value
    if isinstance(field, AskDateField):
        if not isinstance(value, date) or isinstance(value, datetime):
            _bad_type(index)
        return value
    if isinstance(field, AskTimeField):
        if not isinstance(value, time):
            _bad_type(index)
        return value
    if isinstance(field, AskDateTimeField):
        if not isinstance(value, datetime):
            _bad_type(index)
        return value
    assert isinstance(field, AskDurationField)
    if not isinstance(value, timedelta):
        _bad_type(index)
    return value


def _multi_prefill(field: AskMultiChoiceField, value: PrefillValueType,
                   index: int) -> Optional[list[str]]:
    """Return the valid members of a multi-choice prefill, or None."""
    if isinstance(value, str) or not isinstance(value, Sequence):
        _bad_type(index)
    if not all(isinstance(member, str) for member in value):
        _bad_type(index)
    members = [member for member in value if member in field.choices]
    return members if members else None


def _need(value: PrefillValueType, index: int, wanted: type) -> None:
    """Raise TypeError when value is not an instance of wanted."""
    if not isinstance(value, wanted):
        _bad_type(index)


def _bad_type(index: int) -> NoReturn:
    """Raise a TypeError for a prefill value of the wrong type."""
    raise TypeError(f'prefill value for row {index} has the wrong type')
