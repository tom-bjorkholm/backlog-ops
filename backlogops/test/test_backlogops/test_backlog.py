#! /usr/local/bin/python3
"""Tests for backlog item conversion."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from io import StringIO

import pytest

from backlogops.backlog import BacklogItem, Status, get_backlog
from backlogops.backlog import get_backlog_item


def _valid_data(status: object = Status.TODO) -> dict[str, object]:
    """Return dictionary data for one valid backlog item."""
    return {'key': 'BI-1', 'title': 'Create backlog', 'story_points': 3,
            'status': status}


def test_item_from_dict() -> None:
    """Test creating one backlog item from dictionary data."""
    data = _valid_data()
    data['description'] = 'First useful backlog item'
    item = get_backlog_item(data)
    assert item == BacklogItem(key='BI-1', title='Create backlog',
                               story_points=3, status=Status.TODO,
                               extra_fields={
                                   'description':
                                   'First useful backlog item'})


@pytest.mark.parametrize('status_value', [1, 'TODO'])
def test_item_converts_status(status_value: object) -> None:
    """Test raw enum values are converted to status values."""
    item = get_backlog_item(_valid_data(status_value))
    assert item.status == Status.TODO


def test_get_backlog() -> None:
    """Test creating a backlog from a list of dictionaries."""
    data = [_valid_data('TODO'), _valid_data('DONE')]
    backlog = get_backlog(data)
    assert [item.status for item in backlog] == [Status.TODO, Status.DONE]


@pytest.mark.parametrize('field_name', [
    'key',
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
        get_backlog_item(data, stderr_file)
    assert field_name in stderr_file.getvalue()


@pytest.mark.parametrize('field_name, value', [
    ('key', 7),
    ('title', 7),
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
        get_backlog_item(data, stderr_file)
    error_text = stderr_file.getvalue()
    assert field_name in error_text
    assert repr(value) in error_text
