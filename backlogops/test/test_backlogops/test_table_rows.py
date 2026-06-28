#! /usr/local/bin/python3
"""Tests for converting backlog items and releases to and from rows."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
import pytest
from tableio import DictData, Fmt, Value, ValueFmt
from backlogops.backlog import BacklogItem, Status
from backlogops.levels import DEFAULT_LEVELS, LevelDisplay
from backlogops.no_text_io import NoTextIO
from backlogops.releases import Release
from backlogops.table_rows import item_to_row, release_to_row
from backlogops.table_rows import row_to_item, row_to_release
from backlogops.table_rows import _extra_cell, _maybe_int, _split_deps
from backlogops.table_rows import (
    LEVEL_NAME_COLUMN, _name_cell_text, display_level_rows, fold_level_name)


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


@pytest.mark.parametrize('value, expected', [
    (None, ('', False)),
    ('Story', ('Story', False)),
    (True, ('True', False))])
def test_name_cell_non_int(value: Value, expected: tuple[str, bool]) -> None:
    """Test a non-numeric level cell becomes its text, reported unnamed.

    Only a real level number can map to a configured name. None becomes
    an empty cell and any other value becomes its text, both flagged as
    not found so the value itself is shown and never lost.
    """
    assert _name_cell_text(value, DEFAULT_LEVELS) == expected


def test_expand_no_level() -> None:
    """Test a row without a level column is returned unchanged."""
    rows: DictData[ValueFmt] = [{'key': ValueFmt(value='BI-1', fmt=Fmt())}]
    result = display_level_rows(rows, DEFAULT_LEVELS, LevelDisplay.BOTH)
    assert result == rows


def test_fold_empty_name() -> None:
    """Test an empty level-name cell is dropped without setting a level."""
    rows: DictData[Value] = [{LEVEL_NAME_COLUMN: ''}]
    fold_level_name(rows)
    assert rows == [{}]
