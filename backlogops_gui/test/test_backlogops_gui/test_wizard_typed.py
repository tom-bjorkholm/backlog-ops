#! /usr/local/bin/python3
"""Tests for the typed form field parsing and formatting helpers."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date, datetime, time, timedelta
from typing import Optional
import pytest
from tableio_cfg_json import AskField, AskTextField, AskFloatField, \
    AskDateField, AskTimeField, AskDateTimeField, AskDurationField, \
    AnswerFloatField, AnswerDateField, AnswerTimeField, \
    AnswerDateTimeField, AnswerDurationField
from backlogops_gui.wizard_typed import calendar_seed, combined_text, \
    date_of, default_text, field_hint, format_duration, format_value, \
    is_typed, ordered_range_error, parse_date, parse_datetime, \
    parse_duration, parse_float, parse_time, typed_answer, typed_error, \
    typed_value, value_out_of_range


@pytest.mark.parametrize('text, expected', [
    ('3.5', 3.5), ('  2 ', 2.0), ('-1', -1.0), ('x', None), ('', None),
    ('inf', None), ('nan', None)])
def test_parse_float(text: str, expected: Optional[float]) -> None:
    """Test parse_float reads a finite number or reports None."""
    assert parse_float(text) == expected


@pytest.mark.parametrize('text, expected', [
    ('2026-07-24', date(2026, 7, 24)), (' 2026-01-01 ', date(2026, 1, 1)),
    ('2026-13-01', None), ('nope', None), ('', None)])
def test_parse_date(text: str, expected: Optional[date]) -> None:
    """Test parse_date reads an ISO date or reports None."""
    assert parse_date(text) == expected


@pytest.mark.parametrize('text, expected', [
    ('09:00', time(9, 0)), ('09:00:30', time(9, 0, 30)), ('bad', None),
    ('', None)])
def test_parse_time(text: str, expected: Optional[time]) -> None:
    """Test parse_time reads HH:MM or HH:MM:SS or reports None."""
    assert parse_time(text) == expected


@pytest.mark.parametrize('text, expected', [
    ('2026-07-24 09:00:00', datetime(2026, 7, 24, 9)),
    ('2026-07-24T09:15', datetime(2026, 7, 24, 9, 15)), ('bad', None)])
def test_parse_datetime(text: str, expected: Optional[datetime]) -> None:
    """Test parse_datetime reads an ISO date-time or reports None."""
    assert parse_datetime(text) == expected


@pytest.mark.parametrize('text, expected', [
    ('90', timedelta(seconds=90)),
    ('1 d 02:30:00', timedelta(days=1, hours=2, minutes=30)),
    ('02:30:00', timedelta(hours=2, minutes=30)),
    ('00:00:01.5', timedelta(seconds=1.5)), ('-5', None), ('bad', None)])
def test_parse_duration(text: str, expected: Optional[timedelta]) -> None:
    """Test parse_duration reads the two accepted duration forms."""
    assert parse_duration(text) == expected


@pytest.mark.parametrize('text', ['1e308', '999999999999 d 00:00:00'])
def test_duration_overflow(text: str) -> None:
    """Test a duration too large for a timedelta reports None.

    A lone seconds count and a day-and-clock form both overflow the
    timedelta constructor, and each reports None rather than raising.
    """
    assert parse_duration(text) is None


@pytest.mark.parametrize('value, expected', [
    (timedelta(hours=1), '0 d 01:00:00'),
    (timedelta(days=1, hours=2, minutes=30), '1 d 02:30:00'),
    (timedelta(seconds=1, microseconds=500000), '0 d 00:00:01.5')])
def test_format_duration(value: timedelta, expected: str) -> None:
    """Test format_duration writes the days and clock parts."""
    assert format_duration(value) == expected


def test_format_value_kinds() -> None:
    """Test format_value renders durations specially and others plainly."""
    assert format_value(timedelta(hours=1)) == '0 d 01:00:00'
    assert format_value(2.5) == '2.5'
    assert format_value(date(2026, 7, 24)) == '2026-07-24'


def test_duration_round_trip() -> None:
    """Test a formatted duration parses back to the same value."""
    value = timedelta(days=2, hours=3, minutes=4, seconds=5)
    assert parse_duration(format_duration(value)) == value


@pytest.mark.parametrize('field, hint', [
    (AskFloatField('n', None), 'a number'),
    (AskDateField('d', None), 'a date as YYYY-MM-DD'),
    (AskTimeField('t', None), 'a time as HH:MM or HH:MM:SS'),
    (AskDateTimeField('e', None),
     'a date and time as YYYY-MM-DD HH:MM:SS'),
    (AskDurationField('l', None), "a duration as '<days> d HH:MM:SS' "
     'or a number of seconds')])
def test_field_hint(field: AskField, hint: str) -> None:
    """Test each typed field reports its accepted-format hint."""
    assert field_hint(field) == hint


def test_is_typed() -> None:
    """Test is_typed accepts the typed fields and rejects text."""
    assert is_typed(AskFloatField('n', None)) is True
    assert is_typed(AskTextField('t', None)) is False


def test_value_out_of_range() -> None:
    """Test value_out_of_range respects each inclusive bound."""
    low, high = date(2026, 1, 1), date(2026, 12, 31)
    assert value_out_of_range(date(2026, 7, 1), low, high) is False
    assert value_out_of_range(date(2025, 1, 1), low, None) is True
    assert value_out_of_range(5.0, None, 4.0) is True
    assert value_out_of_range(5.0, None, None) is False


@pytest.mark.parametrize('lo, hi, needle', [
    (None, 5.0, 'at most 5.0'), (1.0, None, 'at least 1.0'),
    (1.0, 5.0, 'between 1.0 and 5.0')])
def test_ordered_range_error(lo: Optional[float], hi: Optional[float],
                             needle: str) -> None:
    """Test the ordered range error names the bounds that apply."""
    assert needle in ordered_range_error(lo, hi)


def test_typed_value_default() -> None:
    """Test empty text yields the field default."""
    field = AskFloatField('n', None, default=1.5)
    assert typed_value(field, '') == 1.5


def test_typed_value_parsed() -> None:
    """Test non-empty valid text yields the parsed value."""
    field = AskDateField('d', None)
    assert typed_value(field, '2026-07-24') == date(2026, 7, 24)


def test_typed_value_bad() -> None:
    """Test unparsable or out-of-range text yields None."""
    field = AskFloatField('n', None, min_value=0.0, max_value=1.0)
    assert typed_value(field, 'x') is None
    assert typed_value(field, '5') is None


@pytest.mark.parametrize('field, text, ok', [
    (AskFloatField('n', None), '', False),
    (AskFloatField('n', None, nullable=True), '', True),
    (AskFloatField('n', None, default=0.0), '', True),
    (AskFloatField('n', None), '2', True),
    (AskFloatField('n', None), 'x', False),
    (AskFloatField('n', None, max_value=1.0), '5', False)])
def test_typed_error(field: AskField, text: str, ok: bool) -> None:
    """Test typed_error accepts valid text and rejects the rest."""
    assert (typed_error(field, text) is None) is ok


@pytest.mark.parametrize('field, text, value', [
    (AskTimeField('t', None), '09:30', time(9, 30)),
    (AskDateTimeField('e', None), '2026-07-24 09:00:00',
     datetime(2026, 7, 24, 9)),
    (AskDurationField('l', None), '90', timedelta(seconds=90))])
def test_typed_value_kinds(field: AskField, text: str, value: object) -> None:
    """Test typed_value resolves the time, date-time and duration kinds."""
    assert typed_value(field, text) == value


@pytest.mark.parametrize('field, text, needle', [
    (AskDateField('d', None, min_value=date(2026, 1, 1)), '2025-12-31',
     'at least 2026-01-01'),
    (AskTimeField('t', None, max_value=time(12)), '13:00', 'at most 12:00:00'),
    (AskDateTimeField('e', None, min_value=datetime(2026, 1, 1)),
     '2025-12-31 09:00:00', 'at least 2026-01-01'),
    (AskDurationField('l', None, max_value=timedelta(hours=1)), '02:00:00',
     'at most 0 d 01:00:00')])
def test_typed_range_kinds(field: AskField, text: str, needle: str) -> None:
    """Test each typed kind reports an out-of-range value by its bound."""
    message = typed_error(field, text)
    assert message is not None and needle in message


def test_typed_answer_kinds() -> None:
    """Test typed_answer wraps a value in the matching answer type."""
    float_field = AskFloatField('n', None)
    assert typed_answer(float_field, 2.0) == AnswerFloatField(float_field, 2.0)
    date_field = AskDateField('d', None)
    day = date(2026, 7, 24)
    assert typed_answer(date_field, day) == AnswerDateField(date_field, day)
    dur_field = AskDurationField('l', None)
    length = timedelta(hours=1)
    assert typed_answer(dur_field, length) == \
        AnswerDurationField(dur_field, length)


@pytest.mark.parametrize('field, value, answer_type', [
    (AskTimeField('t', None), time(9, 30), AnswerTimeField),
    (AskDateTimeField('e', None), datetime(2026, 7, 24, 9),
     AnswerDateTimeField)])
def test_answer_temporal(field: AskField, value: object,
                         answer_type: type) -> None:
    """Test typed_answer wraps time and date-time values in their answers."""
    answer = typed_answer(field, value)
    assert isinstance(answer, answer_type) and answer.value == value


def test_default_text() -> None:
    """Test default_text formats the default or is empty when none."""
    timed = AskTimeField('t', None, default=time(9, 0))
    assert default_text(timed) == '09:00:00'
    assert default_text(AskFloatField('n', None)) == ''


@pytest.mark.parametrize('value, expected', [
    (datetime(2026, 7, 24, 9), date(2026, 7, 24)),
    (date(2026, 7, 24), date(2026, 7, 24)), (None, None), (5, None)])
def test_date_of(value: object, expected: Optional[date]) -> None:
    """Test date_of returns the date part of a date or datetime."""
    assert date_of(value) == expected


def test_calendar_seed_date() -> None:
    """Test the date field seeds the calendar from its text and bounds."""
    field = AskDateField('d', None, min_value=date(2026, 1, 1),
                         max_value=date(2026, 12, 31))
    seed, lo, hi = calendar_seed(field, '2026-07-24')
    assert seed == date(2026, 7, 24)
    assert (lo, hi) == (date(2026, 1, 1), date(2026, 12, 31))


def test_calendar_seed_dt() -> None:
    """Test the date-time field seeds the calendar from its date parts."""
    field = AskDateTimeField('e', None, min_value=datetime(2026, 1, 1),
                             max_value=datetime(2026, 12, 31, 23, 59))
    seed, lo, hi = calendar_seed(field, '2026-08-01 09:00:00')
    assert seed == date(2026, 8, 1)
    assert (lo, hi) == (date(2026, 1, 1), date(2026, 12, 31))


def test_combined_text_date() -> None:
    """Test a date field's combined text is the plain ISO date."""
    field = AskDateField('d', None)
    assert combined_text(field, date(2026, 8, 1), '') == '2026-08-01'


def test_combined_text_dt() -> None:
    """Test a date-time field keeps its typed time when a date is picked."""
    field = AskDateTimeField('e', None)
    text = combined_text(field, date(2026, 8, 1), '2026-07-24 09:15:00')
    assert text == '2026-08-01 09:15:00'
