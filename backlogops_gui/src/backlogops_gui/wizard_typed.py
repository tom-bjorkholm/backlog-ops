#! /usr/local/bin/python3
"""Text parsing and formatting for the typed wizard form fields.

The float, date, time, date-time and duration form fields each turn user
text into a typed value and a typed value back into text. This module
holds that conversion for the Tkinter bridge, together with the format
hints and the parse and range error messages, so the graphical form
accepts the same text a user would type on the console.

A duration is written as an optional day count and a clock part,
``<days> d HH:MM:SS``, where the seconds may carry a decimal fraction, or
as a single non-negative number of seconds. Dates, times and date-times
use the ISO 8601 forms accepted by the standard library fromisoformat()
parsers.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import math
import re
from datetime import date, datetime, time, timedelta
from typing import Optional, TypeVar
from tableio_cfg_json import AskField, AnswerField, AskFloatField, \
    AskDateField, AskTimeField, AskDateTimeField, AskDurationField, \
    AnswerFloatField, AnswerDateField, AnswerTimeField, AnswerDateTimeField, \
    AnswerDurationField

FLOAT_HINT = 'a number'
DATE_HINT = 'a date as YYYY-MM-DD'
TIME_HINT = 'a time as HH:MM or HH:MM:SS'
DATETIME_HINT = 'a date and time as YYYY-MM-DD HH:MM:SS'
DURATION_HINT = "a duration as '<days> d HH:MM:SS' or a number of seconds"
_TYPED_FIELDS = (AskFloatField, AskDateField, AskTimeField, AskDateTimeField,
                 AskDurationField)
_DURATION_RE = re.compile(r'^(?:(\d+)\s*d\s+)?(\d+):(\d+):(\d+(?:\.\d+)?)$')
_Ordered = TypeVar('_Ordered', float, date, time, datetime, timedelta)


def parse_float(text: str) -> Optional[float]:
    """Return a finite float from text, or None when not a number."""
    try:
        value = float(text.strip())
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def parse_date(text: str) -> Optional[date]:
    """Return an ISO date from text, or None when not a valid date."""
    try:
        return date.fromisoformat(text.strip())
    except ValueError:
        return None


def parse_time(text: str) -> Optional[time]:
    """Return an ISO time from text, or None when not a valid time."""
    try:
        return time.fromisoformat(text.strip())
    except ValueError:
        return None


def parse_datetime(text: str) -> Optional[datetime]:
    """Return an ISO date-time from text, or None when not valid."""
    try:
        return datetime.fromisoformat(text.strip())
    except ValueError:
        return None


def parse_duration(text: str) -> Optional[timedelta]:
    """Return a duration from text, or None when it is not valid.

    A lone non-negative number is read as a count of seconds; otherwise
    the text must be ``<hours>:<minutes>:<seconds>`` with an optional
    ``<days> d`` prefix, and the seconds may carry a decimal fraction.
    """
    stripped = text.strip()
    seconds = parse_float(stripped)
    if seconds is not None:
        return _seconds_delta(seconds)
    match = _DURATION_RE.match(stripped)
    return None if match is None else _parts_delta(match.groups())


def _seconds_delta(seconds: float) -> Optional[timedelta]:
    """Return a duration of seconds seconds, or None when unusable."""
    if seconds < 0:
        return None
    try:
        return timedelta(seconds=seconds)
    except OverflowError:
        return None


def _parts_delta(groups: tuple[Optional[str], ...]) -> Optional[timedelta]:
    """Return a duration built from matched day and clock groups."""
    days, hours, minutes, seconds = groups
    assert hours is not None and minutes is not None and seconds is not None
    try:
        return timedelta(days=int(days or 0), hours=int(hours),
                         minutes=int(minutes), seconds=float(seconds))
    except OverflowError:
        return None


def format_duration(value: timedelta) -> str:
    """Return a duration as ``<days> d HH:MM:SS`` with any fraction."""
    hours, rest = divmod(value.seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    text = f'{value.days} d {hours:02d}:{minutes:02d}:{seconds:02d}'
    if value.microseconds:
        return f'{text}.{value.microseconds:06d}'.rstrip('0')
    return text


def format_value(value: object) -> str:
    """Return the text a typed value would round-trip from."""
    if isinstance(value, timedelta):
        return format_duration(value)
    return str(value)


def value_out_of_range(value: _Ordered, minimum: Optional[_Ordered],
                       maximum: Optional[_Ordered]) -> bool:
    """Return whether value lies outside the inclusive bounds."""
    below = minimum is not None and value < minimum
    above = maximum is not None and value > maximum
    return below or above


def ordered_range_error(minimum: Optional[object],
                        maximum: Optional[object]) -> str:
    """Return the message shown when a typed value is out of range."""
    low = None if minimum is None else format_value(minimum)
    high = None if maximum is None else format_value(maximum)
    if low is None:
        return f'Please enter a value at most {high}.'
    if high is None:
        return f'Please enter a value at least {low}.'
    return f'Please enter a value between {low} and {high}.'


def is_typed(field: AskField) -> bool:
    """Return whether field is one of the five typed form fields."""
    return isinstance(field, _TYPED_FIELDS)


def field_hint(field: AskField) -> str:
    """Return the accepted-format hint shown for a typed field."""
    if isinstance(field, AskFloatField):
        return FLOAT_HINT
    if isinstance(field, AskDateField):
        return DATE_HINT
    if isinstance(field, AskTimeField):
        return TIME_HINT
    if isinstance(field, AskDateTimeField):
        return DATETIME_HINT
    assert isinstance(field, AskDurationField)
    return DURATION_HINT


def _default_of(field: AskField) -> Optional[object]:
    """Return the default of a typed field."""
    assert isinstance(field, _TYPED_FIELDS)
    return field.default


def _resolve(field: AskField,
             text: str) -> tuple[Optional[object], Optional[str]]:
    """Return a typed field's parsed value and any parse or range error."""
    if isinstance(field, AskFloatField):
        return _checked(parse_float(text), field, field.min_value,
                        field.max_value)
    if isinstance(field, AskDateField):
        return _checked(parse_date(text), field, field.min_value,
                        field.max_value)
    if isinstance(field, AskTimeField):
        return _checked(parse_time(text), field, field.min_value,
                        field.max_value)
    if isinstance(field, AskDateTimeField):
        return _checked(parse_datetime(text), field, field.min_value,
                        field.max_value)
    assert isinstance(field, AskDurationField)
    return _checked(parse_duration(text), field, field.min_value,
                    field.max_value)


def _checked(value: Optional[_Ordered], field: AskField,
             minimum: Optional[_Ordered], maximum: Optional[_Ordered]
             ) -> tuple[Optional[object], Optional[str]]:
    """Return value and no error, or None and the reason it is unusable."""
    if value is None:
        return (None, f'Please enter {field_hint(field)}.')
    if value_out_of_range(value, minimum, maximum):
        return (None, ordered_range_error(minimum, maximum))
    return (value, None)


def default_text(field: AskField) -> str:
    """Return the starting entry text for a typed field's default."""
    default = _default_of(field)
    return '' if default is None else format_value(default)


def typed_value(field: AskField, text: str) -> Optional[object]:
    """Return the typed value of a typed field for its widget text.

    An empty text yields the field default. A non-empty text is parsed;
    unparsable or out-of-range text yields None, and the caller reports
    the error separately through typed_error().
    """
    if text == '':
        return _default_of(field)
    return _resolve(field, text)[0]


def typed_error(field: AskField, text: str) -> Optional[str]:
    """Return the parse or range error of a typed field's widget text.

    Empty text is accepted when the field is nullable or has a default,
    and otherwise reports that a value is required.
    """
    if text != '':
        return _resolve(field, text)[1]
    assert isinstance(field, _TYPED_FIELDS)
    if field.nullable or field.default is not None:
        return None
    return f'Please enter {field_hint(field)}.'


def typed_answer(field: AskField, value: Optional[object]) -> AnswerField:
    """Wrap a typed value in the answer matching a typed field."""
    if isinstance(field, AskFloatField):
        assert value is None or isinstance(value, float)
        return AnswerFloatField(field, value)
    if isinstance(field, AskDateField):
        assert value is None or isinstance(value, date)
        return AnswerDateField(field, value)
    if isinstance(field, AskTimeField):
        assert value is None or isinstance(value, time)
        return AnswerTimeField(field, value)
    if isinstance(field, AskDateTimeField):
        assert value is None or isinstance(value, datetime)
        return AnswerDateTimeField(field, value)
    assert isinstance(field, AskDurationField)
    assert value is None or isinstance(value, timedelta)
    return AnswerDurationField(field, value)


def date_of(value: Optional[object]) -> Optional[date]:
    """Return the date part of a date or datetime, or None."""
    if isinstance(value, datetime):
        return value.date()
    return value if isinstance(value, date) else None


def calendar_seed(field: AskField, text: str
                  ) -> tuple[date, Optional[date], Optional[date]]:
    """Return the calendar seed date and its inclusive day bounds.

    A date-time field's bounds are its date parts, so the calendar offers
    the acceptable days and the field itself validates the exact value.
    """
    if isinstance(field, AskDateField):
        parsed = parse_date(text)
        minimum, maximum = field.min_value, field.max_value
    else:
        assert isinstance(field, AskDateTimeField)
        parsed = date_of(parse_datetime(text))
        minimum = date_of(field.min_value)
        maximum = date_of(field.max_value)
    seed = parsed or date_of(field.default) or date.today()
    return (seed, minimum, maximum)


def combined_text(field: AskField, picked: date, current: str) -> str:
    """Return the input text for a picked date, keeping any typed time."""
    if isinstance(field, AskDateField):
        return picked.isoformat()
    assert isinstance(field, AskDateTimeField)
    existing = parse_datetime(current)
    clock = existing.time() if existing is not None else time()
    return datetime.combine(picked, clock).isoformat(sep=' ')
