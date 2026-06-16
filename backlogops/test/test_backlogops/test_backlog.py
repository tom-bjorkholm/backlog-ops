#! /usr/local/bin/python3
"""Tests for backlog item conversion and consistency checks."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date, datetime
from io import StringIO

import pytest

from backlogops.backlog import BacklogItem, Status, get_backlog
from backlogops.backlog import get_backlog_item, check_backlog_consistency
from backlogops.no_text_io import NoTextIO


def _valid_data(status: object = Status.TODO) -> dict[str, object]:
    """Return dictionary data for one valid backlog item."""
    return {'key': 'BI-1', 'level': 1, 'title': 'Create backlog',
            'story_points': 3, 'status': status}


def _valid_item() -> BacklogItem:
    """Return one minimal valid backlog item."""
    return BacklogItem(key='BI-1', level=1, title='Title', story_points=3,
                       status=Status.TODO)


def _backlog_pair() -> list[BacklogItem]:
    """Return a small consistent backlog of two related items.

    ``BI-1`` is the parent of ``BI-2`` and is therefore at a higher
    level than its child. The child has no explicit dependency on its
    parent, because a child cannot finish-to-start depend on a parent
    that only finishes after the child.
    """
    return [BacklogItem(key='BI-1', level=2, title='A', story_points=1,
                        status=Status.TODO),
            BacklogItem(key='BI-2', level=1, title='B', story_points=2,
                        status=Status.TODO, parent_key='BI-1')]


def test_item_from_dict() -> None:
    """Test creating one backlog item from dictionary data."""
    data = _valid_data()
    data['description'] = 'First useful backlog item'
    item = get_backlog_item(data)
    assert item == BacklogItem(key='BI-1', level=1, title='Create backlog',
                               story_points=3, status=Status.TODO,
                               extra_fields={
                                   'description':
                                   'First useful backlog item'})


@pytest.mark.parametrize('status_value', [1, 'TODO'])
def test_item_converts_status(status_value: object) -> None:
    """Test raw enum values are converted to status values."""
    item = get_backlog_item(_valid_data(status_value))
    assert item.status == Status.TODO


@pytest.mark.parametrize('value, expected', [
    ('TODO', Status.TODO),
    ('todo', Status.TODO),
    ('Done', Status.DONE),
    ('IN_PROGRESS', Status.IN_PROGRESS),
    (1, Status.TODO),
    (2, Status.IN_PROGRESS),
    (Status.REJECTED, Status.REJECTED)])
def test_status_best_match(value: object, expected: Status) -> None:
    """Test status names, raw values and members are all accepted."""
    assert get_backlog_item(_valid_data(value)).status == expected


def test_get_backlog() -> None:
    """Test creating a backlog from a list of dictionaries."""
    data = [_valid_data('TODO'), _valid_data('DONE')]
    backlog = get_backlog(data)
    assert [item.status for item in backlog] == [Status.TODO, Status.DONE]


def test_item_optional_fields() -> None:
    """Test optional scalar and dependency fields are converted."""
    data = _valid_data()
    data['parent_key'] = 'BI-0'
    data['release'] = 'R1'
    data['depends_on_f2s'] = ['BI-2', 'BI-3']
    item = get_backlog_item(data)
    assert item.parent_key == 'BI-0'
    assert item.release == 'R1'
    assert item.depends_on_f2s == ['BI-2', 'BI-3']


def test_item_converts_dates() -> None:
    """Test ISO 8601 date strings are converted to date objects."""
    data = _valid_data()
    data['planned_ready_date'] = '2026-06-12'
    data['estimated_ready_date'] = '2026-07-01'
    item = get_backlog_item(data)
    assert item.planned_ready_date == date(2026, 6, 12)
    assert item.estimated_ready_date == date(2026, 7, 1)


def test_item_date_obj() -> None:
    """Test an existing date object is accepted unchanged."""
    data = _valid_data()
    data['planned_ready_date'] = date(2026, 6, 12)
    item = get_backlog_item(data)
    assert item.planned_ready_date == date(2026, 6, 12)


def test_item_date_from_dt() -> None:
    """Test a spreadsheet datetime is stored as a comparable date.

    Reading from Excel yields a datetime for a date column. It must be
    narrowed to a date so that later comparisons with a date succeed.
    """
    data = _valid_data()
    data['planned_ready_date'] = datetime(2026, 6, 12, 9, 30)
    item = get_backlog_item(data)
    assert item.planned_ready_date == date(2026, 6, 12)
    assert not isinstance(item.planned_ready_date, datetime)
    assert item.planned_ready_date > date(2026, 6, 11)


def test_optional_date_none() -> None:
    """Test an explicit None is accepted for an optional date field."""
    data = _valid_data()
    data['planned_ready_date'] = None
    item = get_backlog_item(data)
    assert item.planned_ready_date is None


@pytest.mark.parametrize('value', ['not-a-date', '2026-13-01', 42])
def test_bad_date_errors(value: object) -> None:
    """Test invalid date values are reported and rejected."""
    data = _valid_data()
    data['planned_ready_date'] = value
    with pytest.raises(TypeError):
        get_backlog_item(data, stderr_file=NoTextIO())


@pytest.mark.parametrize('field_name', [
    'key',
    'level',
    'title',
    'story_points',
    'status'
])
def test_missing_field_errors(field_name: str) -> None:
    """Test missing mandatory fields are reported and rejected."""
    data = _valid_data()
    del data[field_name]
    stderr_file = StringIO()
    with pytest.raises(KeyError):
        get_backlog_item(data, stderr_file=stderr_file)
    assert field_name in stderr_file.getvalue()


@pytest.mark.parametrize('field_name, value', [
    ('key', True),
    ('level', 1.5),
    ('level', True),
    ('title', True),
    ('story_points', '3'),
    ('story_points', True),
    ('status', 'UNKNOWN')
])
def test_bad_field_errors(field_name: str, value: object) -> None:
    """Test invalid mandatory fields are reported and rejected."""
    data = _valid_data()
    data[field_name] = value
    stderr_file = StringIO()
    with pytest.raises(TypeError):
        get_backlog_item(data, stderr_file=stderr_file)
    error_text = stderr_file.getvalue()
    assert field_name in error_text
    assert repr(value) in error_text


def test_internal_ok() -> None:
    """Test a fully populated valid item passes the internal check."""
    item = BacklogItem(key='BI-1', level=1, title='Title', story_points=3,
                       status=Status.TODO, release='R1',
                       depends_on_f2s=['BI-2'],
                       planned_ready_date=date(2026, 6, 12))
    item.check_consistency(NoTextIO())


@pytest.mark.parametrize('field_name, value', [
    ('story_points', 'three'),
    ('key', 7),
    ('level', 'one'),
    ('level', True),
    ('status', 'TODO')])
def test_internal_type_errors(field_name: str, value: object) -> None:
    """Test wrong field types are reported by the internal check."""
    item = _valid_item()
    setattr(item, field_name, value)
    with pytest.raises(TypeError):
        item.check_consistency(NoTextIO())


@pytest.mark.parametrize('field_name, value', [
    ('key', ''),
    ('key', 'BI 1'),
    ('key', 'BI,1'),
    ('key', 'a(b)'),
    ('release', ''),
    ('release', 'R 1')])
def test_internal_value_err(field_name: str, value: object) -> None:
    """Test invalid key or release syntax is reported as a ValueError."""
    item = _valid_item()
    setattr(item, field_name, value)
    with pytest.raises(ValueError):
        item.check_consistency(NoTextIO())


def test_internal_bad_dep() -> None:
    """Test an invalid dependency key is reported as a ValueError."""
    item = _valid_item()
    item.depends_on_f2s = ['bad key']
    with pytest.raises(ValueError):
        item.check_consistency(NoTextIO())


def test_setitem_named_field() -> None:
    """Test setting a named field does not write into extra_fields."""
    item = _valid_item()
    item['title'] = 'New title'
    assert item.title == 'New title'
    assert 'title' not in item.extra_fields
    assert item.to_dict()['title'] == 'New title'


def test_setitem_extra_field() -> None:
    """Test setting an unknown field writes into extra_fields."""
    item = _valid_item()
    item['note'] = 'a note'
    assert item.extra_fields == {'note': 'a note'}
    assert item['note'] == 'a note'


def test_internal_shadow() -> None:
    """Test an extra field shadowing a named field is a ValueError."""
    item = _valid_item()
    item.extra_fields['title'] = 'Shadow'
    with pytest.raises(ValueError):
        item.check_consistency(NoTextIO())


def test_backlog_valid_passes() -> None:
    """Test a consistent backlog passes the backlog check."""
    check_backlog_consistency(_backlog_pair(), NoTextIO())


def test_dup_keys() -> None:
    """Test duplicate item keys are reported as a ValueError."""
    backlog = _backlog_pair()
    backlog[1].key = 'BI-1'
    with pytest.raises(ValueError):
        check_backlog_consistency(backlog, NoTextIO())


def test_unknown_parent() -> None:
    """Test an unknown parent_key is reported as a KeyError."""
    backlog = _backlog_pair()
    backlog[1].parent_key = 'BI-9'
    with pytest.raises(KeyError):
        check_backlog_consistency(backlog, NoTextIO())


def test_unknown_dep() -> None:
    """Test an unknown dependency key is reported as a KeyError."""
    backlog = _backlog_pair()
    backlog[1].depends_on_f2s = ['BI-9']
    with pytest.raises(KeyError):
        check_backlog_consistency(backlog, NoTextIO())


def test_self_dep() -> None:
    """Test a self dependency is reported as a ValueError."""
    backlog = _backlog_pair()
    backlog[0].depends_on_s2s = ['BI-1']
    with pytest.raises(ValueError):
        check_backlog_consistency(backlog, NoTextIO())


def test_backlog_cycle() -> None:
    """Test a dependency cycle is reported as a ValueError."""
    backlog = _backlog_pair()
    backlog[0].depends_on_f2s = ['BI-2']
    with pytest.raises(ValueError):
        check_backlog_consistency(backlog, NoTextIO())


@pytest.mark.parametrize('value, expected', [
    (2, 2), ('Story', 1), ('story', 1), ('TASK', 1), ('Bug', 1),
    ('Initiative', 3)])
def test_level_from_string(value: object, expected: int) -> None:
    """Test level names and aliases resolve to level numbers."""
    data = _valid_data()
    data['level'] = value
    assert get_backlog_item(data).level == expected


def test_level_unknown_name() -> None:
    """Test an unknown level name is reported as a ValueError."""
    data = _valid_data()
    data['level'] = 'Nonexistent'
    stderr_file = StringIO()
    with pytest.raises(ValueError):
        get_backlog_item(data, stderr_file=stderr_file)
    assert 'Nonexistent' in stderr_file.getvalue()


def test_get_backlog_levels() -> None:
    """Test get_backlog resolves string levels for every item."""
    first = _valid_data()
    first['level'] = 'Epic'
    second = _valid_data()
    second['key'] = 'BI-2'
    second['level'] = 'Story'
    backlog = get_backlog([first, second])
    assert [item.level for item in backlog] == [2, 1]


def test_parent_higher_ok() -> None:
    """Test a parent at a higher level passes the backlog check."""
    check_backlog_consistency(_backlog_pair(), NoTextIO())


@pytest.mark.parametrize('parent_level', [1, 0])
def test_parent_not_higher(parent_level: int) -> None:
    """Test a parent not at a higher level is a ValueError."""
    backlog = _backlog_pair()
    backlog[0].level = parent_level
    stderr_file = StringIO()
    with pytest.raises(ValueError):
        check_backlog_consistency(backlog, stderr_file)
    assert 'parent_key' in stderr_file.getvalue()


def test_nesting_no_cycle() -> None:
    """Test the implicit parent dependencies are not a false cycle."""
    backlog = [BacklogItem(key='E', level=2, title='Epic', story_points=5,
                           status=Status.TODO),
               BacklogItem(key='S1', level=1, title='S1', story_points=2,
                           status=Status.TODO, parent_key='E'),
               BacklogItem(key='S2', level=1, title='S2', story_points=2,
                           status=Status.TODO, parent_key='E',
                           depends_on_f2s=['S1'])]
    check_backlog_consistency(backlog, StringIO())


def test_implicit_cycle() -> None:
    """Test a contradiction with an implicit parent edge is a cycle.

    The implicit parent relation requires the child to start no earlier
    than its parent. An explicit start-to-start dependency in the
    opposite direction (the parent must not start before the child)
    contradicts it, so a cycle is found. Without the implicit parent
    edge there would be no cycle.
    """
    backlog = [BacklogItem(key='E', level=2, title='Epic', story_points=5,
                           status=Status.TODO, depends_on_s2s=['S1']),
               BacklogItem(key='S1', level=1, title='S1', story_points=2,
                           status=Status.TODO, parent_key='E')]
    with pytest.raises(ValueError):
        check_backlog_consistency(backlog, NoTextIO())
