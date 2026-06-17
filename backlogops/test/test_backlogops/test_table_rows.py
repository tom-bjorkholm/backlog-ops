#! /usr/local/bin/python3
"""Tests for converting backlog items and releases to and from rows."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
import pytest
from backlogops.backlog import BacklogItem, Status
from backlogops.no_text_io import NoTextIO
from backlogops.releases import Release
from backlogops.table_rows import item_to_row, release_to_row
from backlogops.table_rows import row_to_item, row_to_release
from backlogops.table_rows import _extra_cell, _maybe_int, _split_deps


def _item() -> BacklogItem:
    """Return one minimal valid backlog item for row conversions."""
    return BacklogItem(key='BI-1', level=1, title='T', story_points=3,
                       status=Status.TODO)


def test_item_to_row_basic() -> None:
    """Test named fields convert to cells keyed by field name."""
    item = _item()
    item.depends_on_f2s = ['BI-2', 'BI-3']
    row = item_to_row(item)
    assert row['status'] == 'TODO'
    assert row['depends_on_f2s'] == 'BI-2 BI-3'
    assert row['key'] == 'BI-1'


def test_extra_cell_date() -> None:
    """Test an extra field holding a date becomes an ISO string."""
    item = _item()
    item.extra_fields['due'] = date(2026, 6, 17)
    assert item_to_row(item)['due'] == '2026-06-17'


@pytest.mark.parametrize('value, expected', [
    (date(2026, 6, 17), '2026-06-17'),
    ('text', 'text'),
    (5, 5),
    (None, None),
    ([1, 2], '[1, 2]')])
def test_extra_cell(value: object, expected: object) -> None:
    """Test extra cells keep scalars and stringify other objects."""
    assert _extra_cell(value) == expected


@pytest.mark.parametrize('value, expected', [
    (None, []),
    ('', []),
    ('BI-2', ['BI-2']),
    ('BI-2 BI-3', ['BI-2', 'BI-3'])])
def test_split_deps(value: object, expected: list[str]) -> None:
    """Test dependency cells split on whitespace, empty cells give []."""
    assert _split_deps(value) == expected


@pytest.mark.parametrize('value, expected', [
    (True, True),
    (False, False),
    (3.0, 3),
    (2.5, 2.5),
    ('5', 5),
    ('  7 ', 7),
    ('x', 'x'),
    (4, 4)])
def test_maybe_int(value: object, expected: object) -> None:
    """Test numeric cells become integers, others stay unchanged."""
    result = _maybe_int(value)
    assert result == expected
    assert isinstance(result, type(expected))


def test_round_trip() -> None:
    """Test an item converted to a row and back is unchanged."""
    item = _item()
    item.story_points = 3
    restored = row_to_item(item_to_row(item), stderr_file=NoTextIO())
    assert restored == item


def test_row_to_item_missing() -> None:
    """Test a row missing a mandatory column is reported on rebuild."""
    row = {'key': 'BI-1', 'level': 1, 'title': 'T', 'status': 'TODO'}
    with pytest.raises(KeyError):
        row_to_item(row, stderr_file=NoTextIO())


def test_release_round_trip() -> None:
    """Test a release converts to a row and back unchanged."""
    release = Release(name='R1', planned_date=date(2026, 6, 17))
    row = release_to_row(release)
    assert row['planned_date'] == '2026-06-17'
    assert row['estimated_date'] is None
    assert row_to_release(row, stderr_file=NoTextIO()) == release
