#! /usr/local/bin/python3
"""Tests for validating a partial validator's prefill requests."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import cast
import pytest
from wizard_ui_bridge import AskField, PrefillValueType, PathAskOptions, \
    AskTextField, AskIntField, AskPathField, AskYesNoField, AskChoiceField, \
    AskMultiChoiceField, AskFloatField, AskDateField, AskTimeField, \
    AskDateTimeField, AskDurationField
from backlogops_gui.wizard_prefill import valid_prefills

_FIELDS: list[AskField] = [
    AskTextField('t', None),
    AskTextField('s', None, sensitive=True),
    AskIntField('i', None),
    AskFloatField('f', None),
    AskPathField('p', None, path_options=PathAskOptions()),
    AskYesNoField('y', None, default=False),
    AskChoiceField('c', None, choices=['a', 'b']),
    AskMultiChoiceField('m', None, choices=['a', 'b', 'c']),
    AskDateField('d', None),
    AskTimeField('tm', None),
    AskDateTimeField('dt', None),
    AskDurationField('du', None)]


def _one(index: int, value: PrefillValueType
         ) -> list[tuple[int, PrefillValueType]]:
    """Return the surviving prefills for one request, changed row -1."""
    return list(valid_prefills(_FIELDS, -1, ((index, value),)))


def test_skip_changed_row() -> None:
    """Test a prefill aimed at the changed row is skipped."""
    assert not list(valid_prefills(_FIELDS, 0, ((0, 'x'),)))


def test_bad_index_raises() -> None:
    """Test a prefill for a row outside the form raises IndexError."""
    with pytest.raises(IndexError):
        list(valid_prefills(_FIELDS, -1, ((99, 'x'),)))


def test_text_and_sensitive() -> None:
    """Test a text value is kept but a sensitive field is never filled."""
    assert _one(0, 'hi') == [(0, 'hi')]
    assert not _one(1, 'secret')


def test_int_rejects_bool() -> None:
    """Test an integer field keeps an int but a boolean is a type error."""
    assert _one(2, 3) == [(2, 3)]
    with pytest.raises(TypeError):
        _one(2, True)


def test_float_keeps_number() -> None:
    """Test a float field keeps a number unchanged but a bool is an error."""
    assert _one(3, 2) == [(3, 2)]
    assert _one(3, 2.5) == [(3, 2.5)]
    with pytest.raises(TypeError):
        _one(3, True)


def test_path_needs_path() -> None:
    """Test a path field keeps a Path but a plain string is an error."""
    target = Path('/tmp/x')
    assert _one(4, target) == [(4, target)]
    with pytest.raises(TypeError):
        _one(4, '/tmp/x')


def test_yes_no_needs_bool() -> None:
    """Test a yes/no field keeps a bool but an int is a type error."""
    assert _one(5, True) == [(5, True)]
    with pytest.raises(TypeError):
        _one(5, 1)


def test_choice_membership() -> None:
    """Test a choice value is kept only when it is a valid choice."""
    assert _one(6, 'a') == [(6, 'a')]
    assert not _one(6, 'z')


def test_multi_filter() -> None:
    """Test a multi-choice value keeps only valid members, else drops."""
    assert _one(7, ['a', 'z', 'c']) == [(7, ['a', 'c'])]
    assert not _one(7, ['z'])


def test_date_not_datetime() -> None:
    """Test a date field keeps a date but a datetime is a type error."""
    day = date(2026, 7, 24)
    assert _one(8, day) == [(8, day)]
    with pytest.raises(TypeError):
        _one(8, datetime(2026, 7, 24, 9))


def test_temporal_kinds() -> None:
    """Test the time, date-time and duration fields keep their own type."""
    clock = time(9, 0)
    moment = datetime(2026, 7, 24, 9)
    length = timedelta(hours=1)
    assert _one(9, clock) == [(9, clock)]
    assert _one(10, moment) == [(10, moment)]
    assert _one(11, length) == [(11, length)]


@pytest.mark.parametrize('index, value', [
    (9, date(2026, 7, 24)), (10, date(2026, 7, 24)), (11, 90)])
def test_temporal_bad_type(index: int, value: PrefillValueType) -> None:
    """Test each temporal field rejects a value of the wrong type.

    A plain date is not a time, a plain date is not a date-time (which is
    a stricter subtype), and a number is not a duration.
    """
    with pytest.raises(TypeError):
        _one(index, value)


@pytest.mark.parametrize('value', ['abc', 5])
def test_multi_scalar_bad(value: PrefillValueType) -> None:
    """Test a multi-choice prefill rejects a string and a non-sequence."""
    with pytest.raises(TypeError):
        _one(7, value)


def test_multi_member_bad() -> None:
    """Test a multi-choice prefill with a non-string member is rejected.

    The mixed list is cast because it deliberately violates the value type
    to exercise the validator's own type check.
    """
    with pytest.raises(TypeError):
        _one(7, cast(PrefillValueType, ['a', 5]))
