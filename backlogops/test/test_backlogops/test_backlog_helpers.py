#! /usr/local/bin/python3
"""Tests for the backlog helper functions."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import fields
from datetime import date, datetime
from io import StringIO
from typing import Optional

import pytest

from backlogops.backlog import BacklogItem, Status
from backlogops.backlog_helpers import accepts_none, build_item_kwargs
from backlogops.backlog_helpers import check_key_syntax, construct
from backlogops.backlog_helpers import convert_field_value, convert_to_date
from backlogops.backlog_helpers import convert_to_enum, convert_to_str
from backlogops.backlog_helpers import enum_class_of
from backlogops.backlog_helpers import field_type_hints, find_cycle
from backlogops.backlog_helpers import is_mandatory_field, non_optional_type
from backlogops.backlog_helpers import report_bad_value
from backlogops.backlog_helpers import report_missing_field
from backlogops.backlog_helpers import report_unknown_reference
from backlogops.backlog_helpers import report_wrong_type, value_matches_type


@pytest.mark.parametrize('value, data_type, expected', [
    (5, int, True),
    (True, int, False),
    ('x', str, True),
    (None, Optional[str], True),
    (None, str, False),
    (['a', 'b'], list[str], True),
    (['a', 1], list[str], False),
    ({'k': 1}, dict[str, object], True),
    (Status.TODO, Status, True),
    (1, Status, False),
    (date(2026, 6, 12), date, True),
    (datetime(2026, 6, 12, 9, 0), date, False),
    ('anything', object, True)])
def test_value_matches_type(value: object, data_type: object,
                            expected: bool) -> None:
    """Test runtime type matching for the supported type hints."""
    assert value_matches_type(value, data_type) is expected


@pytest.mark.parametrize('data_type, expected', [
    (Optional[str], str),
    (str, str),
    (Optional[date], date)])
def test_non_optional_type(data_type: object, expected: object) -> None:
    """Test the inner type of an optional hint is returned."""
    assert non_optional_type(data_type) is expected


@pytest.mark.parametrize('data_type, expected', [
    (Optional[str], True),
    (str, False),
    (Optional[date], True)])
def test_accepts_none(data_type: object, expected: bool) -> None:
    """Test detection of type hints that accept None."""
    assert accepts_none(data_type) is expected


def test_enum_class_of() -> None:
    """Test the enum class is extracted only from enum hints."""
    assert enum_class_of(Status) is Status
    assert enum_class_of(str) is None
    assert enum_class_of(Optional[str]) is None


@pytest.mark.parametrize('value, expected', [
    (Status.DONE, Status.DONE),
    ('DONE', Status.DONE),
    ('done', Status.DONE),
    (3, Status.DONE)])
def test_convert_to_enum(value: object, expected: Status) -> None:
    """Test members, names and raw values convert to enum members."""
    assert convert_to_enum('status', value, Status, StringIO()) == expected


@pytest.mark.parametrize('value', ['nope', True, 99, 1.5])
def test_convert_to_enum_bad(value: object) -> None:
    """Test unmatched enum values raise a TypeError."""
    with pytest.raises(TypeError):
        convert_to_enum('status', value, Status, StringIO())


def test_to_date_str() -> None:
    """Test an ISO 8601 string is parsed to a date."""
    assert convert_to_date('d', '2026-06-12', StringIO()) == \
        date(2026, 6, 12)


def test_to_date_obj() -> None:
    """Test an existing date object is returned unchanged."""
    given = date(2026, 6, 12)
    assert convert_to_date('d', given, StringIO()) is given


def test_to_date_datetime() -> None:
    """Test a datetime is narrowed to its date, dropping the time."""
    given = datetime(2026, 6, 12, 9, 30)
    assert convert_to_date('d', given, StringIO()) == date(2026, 6, 12)


@pytest.mark.parametrize('value', ['nope', '2026-13-01', 5, None])
def test_convert_to_date_bad(value: object) -> None:
    """Test invalid date values raise a TypeError."""
    with pytest.raises(TypeError):
        convert_to_date('d', value, StringIO())


def test_field_none_opt() -> None:
    """Test None is accepted for an optional field."""
    assert convert_field_value('p', None, Optional[date], StringIO()) is None


def test_field_enum() -> None:
    """Test an enum field value is converted to a member."""
    assert convert_field_value('status', 'TODO', Status,
                               StringIO()) == Status.TODO


def test_field_date() -> None:
    """Test an optional date field value is parsed."""
    assert convert_field_value('p', '2026-06-12', Optional[date],
                               StringIO()) == date(2026, 6, 12)


def test_field_list() -> None:
    """Test a list field value is validated and returned."""
    assert convert_field_value('d', ['a'], list[str], StringIO()) == ['a']


def test_field_str_from_int() -> None:
    """Test an integer field value is converted to its string form."""
    assert convert_field_value('key', 100, str, StringIO()) == '100'


def test_field_date_dt() -> None:
    """Test a datetime field value is narrowed to a date."""
    assert convert_field_value('p', datetime(2026, 6, 12, 9, 0),
                               Optional[date], StringIO()) == date(2026, 6, 12)


@pytest.mark.parametrize('value, expected', [
    ('abc', 'abc'),
    (100, '100'),
    (100.0, '100'),
    (2.5, '2.5')])
def test_convert_to_str(value: object, expected: str) -> None:
    """Test unambiguous values convert to their string form."""
    assert convert_to_str('key', value, StringIO()) == expected


@pytest.mark.parametrize('value', [True, False, date(2026, 6, 12)])
def test_convert_to_str_bad(value: object) -> None:
    """Test ambiguous or unconvertible values raise a TypeError."""
    with pytest.raises(TypeError):
        convert_to_str('key', value, StringIO())


def test_field_bad() -> None:
    """Test a value that does not match its type raises a TypeError."""
    with pytest.raises(TypeError):
        convert_field_value('s', True, str, StringIO())


@pytest.mark.parametrize('value', ['BI-1', 'a_b', 'x#1', '$money', 'abc'])
def test_key_ok(value: str) -> None:
    """Test that well formed keys pass the syntax check."""
    check_key_syntax('key', value, StringIO())


@pytest.mark.parametrize('value', [
    '', 'a b', 'a,b', 'a.b', 'a;b', 'a:b', 'a(b', 'a)b', '[x]', '{y}'])
def test_key_value_err(value: str) -> None:
    """Test that empty or forbidden keys raise a ValueError."""
    with pytest.raises(ValueError):
        check_key_syntax('key', value, StringIO())


def test_key_type_err() -> None:
    """Test that a non-string key raises a TypeError."""
    with pytest.raises(TypeError):
        check_key_syntax('key', 7, StringIO())


def test_find_cycle_acyclic() -> None:
    """Test that an acyclic graph returns None."""
    assert find_cycle({'a': ['b'], 'b': ['c'], 'c': []}) is None


def test_find_cycle_simple() -> None:
    """Test that a two node cycle is detected."""
    cycle = find_cycle({'a': ['b'], 'b': ['a']})
    assert cycle is not None
    assert cycle[0] == cycle[-1]


def test_find_cycle_self() -> None:
    """Test that a self reference is detected as a cycle."""
    assert find_cycle({'a': ['a']}) == ['a', 'a']


def test_cycle_missing() -> None:
    """Test that edges to absent nodes do not create a false cycle."""
    assert find_cycle({'a': ['b']}) is None


def test_field_type_hints() -> None:
    """Test that field annotations are resolved to concrete types."""
    hints = field_type_hints(BacklogItem)
    assert hints['key'] is str
    assert hints['status'] is Status


def test_is_mandatory_field() -> None:
    """Test detection of fields that must be supplied."""
    item_fields = {f.name: f for f in fields(BacklogItem)}
    assert is_mandatory_field(item_fields['key'])
    assert not is_mandatory_field(item_fields['parent_key'])
    assert not is_mandatory_field(item_fields['extra_fields'])


def test_build_construct() -> None:
    """Test building kwargs from data and constructing an item."""
    data: dict[str, object] = {'key': 'BI-1', 'level': 1, 'title': 'T',
                               'story_points': 2, 'status': 'TODO',
                               'note': 'hi'}
    hints = field_type_hints(BacklogItem)
    kwargs = build_item_kwargs(fields(BacklogItem), hints, data, StringIO())
    item = construct(BacklogItem, kwargs)
    assert item.status == Status.TODO
    assert item.extra_fields == {'note': 'hi'}


def test_report_missing_field() -> None:
    """Test reporting a missing field raises a KeyError."""
    err = StringIO()
    with pytest.raises(KeyError):
        report_missing_field('key', err)
    assert 'key' in err.getvalue()


def test_report_wrong_type() -> None:
    """Test reporting a wrong type raises a TypeError with details."""
    err = StringIO()
    with pytest.raises(TypeError):
        report_wrong_type('story_points', 'x', int, err)
    assert 'story_points' in err.getvalue()


def test_report_bad_value() -> None:
    """Test reporting a bad value raises a ValueError with details."""
    err = StringIO()
    with pytest.raises(ValueError):
        report_bad_value('key', 'a b', 'must not contain whitespace', err)
    assert 'key' in err.getvalue()


def test_report_unknown_ref() -> None:
    """Test reporting an unknown reference raises a KeyError."""
    err = StringIO()
    with pytest.raises(KeyError):
        report_unknown_reference('parent_key', 'BI-2', 'BI-9', err)
    assert 'BI-9' in err.getvalue()


def test_subject_default() -> None:
    """Test the default subject names a backlog item field."""
    err = StringIO()
    with pytest.raises(ValueError):
        report_bad_value('k', 1, 'bad', err)
    assert err.getvalue().startswith("Backlog item field 'k'")


def test_subject_custom() -> None:
    """Test a custom subject replaces the backlog item wording."""
    err = StringIO()
    with pytest.raises(TypeError):
        report_wrong_type('name', 1, str, err, 'Person')
    message = err.getvalue()
    assert message.startswith("Person field 'name'")
    assert 'Backlog item' not in message
