#! /usr/local/bin/python3
"""Tests for reordering a backlog and extracting keys by level."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional
from collections.abc import Sequence
import pytest
from backlogops import (
    Backlog, BacklogItem, Level, Status, get_keys_in_order, move_keys_first)
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()


def _item(key: str, level: int, parent: Optional[str] = None) -> BacklogItem:
    """Return a minimal backlog item for the reordering tests."""
    return BacklogItem(key=key, level=level, title=key, story_points=1,
                       status=Status.TODO, parent_key=parent)


def _hierarchy() -> Backlog:
    """Return E1, E2 epics with stories S1, S2 (E1) and S3 (E2)."""
    return [_item('E1', 2), _item('E2', 2), _item('S1', 1, 'E1'),
            _item('S2', 1, 'E1'), _item('S3', 1, 'E2')]


def _order(backlog: Backlog) -> list[str]:
    """Return the keys of a backlog in their current order."""
    return [item.key for item in backlog]


def test_children_before() -> None:
    """Test descendants are pulled to just before their named parent."""
    result = move_keys_first(_hierarchy(), ['E1', 'S3'], NO_OUTPUT)
    assert _order(result) == ['S1', 'S2', 'E1', 'S3', 'E2']


def test_named_child_after() -> None:
    """Test a named child is placed by its own key, after its named parent."""
    result = move_keys_first(_hierarchy(), ['E1', 'S1'], NO_OUTPUT)
    assert _order(result) == ['S2', 'E1', 'S1', 'E2', 'S3']


def test_nearest_named() -> None:
    """Test a descendant belongs to its nearest named ancestor."""
    backlog = [_item('I1', 3), _item('E1', 2, 'I1'), _item('S1', 1, 'E1')]
    after_top = move_keys_first(backlog, ['I1'], NO_OUTPUT)
    assert _order(after_top) == ['S1', 'E1', 'I1']
    after_both = move_keys_first(backlog, ['I1', 'E1'], NO_OUTPUT)
    assert _order(after_both) == ['I1', 'S1', 'E1']


def test_grandchild_nesting() -> None:
    """Test a grandchild comes before its parent before the grandparent."""
    backlog = [_item('E45', 2), _item('S451', 1, 'E45'),
               _item('S452', 1, 'E45'), _item('T4521', 0, 'S452')]
    result = move_keys_first(backlog, ['E45'], NO_OUTPUT)
    assert _order(result) == ['S451', 'T4521', 'S452', 'E45']


def test_empty_keys() -> None:
    """Test an empty key list returns a new backlog in the same order."""
    backlog = _hierarchy()
    result = move_keys_first(backlog, [], NO_OUTPUT)
    assert _order(result) == _order(backlog)
    assert result is not backlog


def test_arg_not_modified() -> None:
    """Test the input backlog keeps its original order."""
    backlog = _hierarchy()
    before = _order(backlog)
    move_keys_first(backlog, ['S3', 'E1'], NO_OUTPUT)
    assert _order(backlog) == before


def test_duplicate_key() -> None:
    """Test a duplicate key in the key list raises ValueError."""
    with pytest.raises(ValueError):
        move_keys_first(_hierarchy(), ['E1', 'E1'], NO_OUTPUT)


def test_missing_key() -> None:
    """Test a key absent from the backlog raises KeyError."""
    with pytest.raises(KeyError):
        move_keys_first(_hierarchy(), ['nope'], NO_OUTPUT)


def _level_backlog() -> Backlog:
    """Return items A, D at level 2 and B, C at level 1, in order."""
    return [_item('A', 2), _item('B', 1), _item('C', 1), _item('D', 2)]


@pytest.mark.parametrize('only_levels,expected', [
    (1, ['B', 'C']),
    ('Story', ['B', 'C']),
    ('Epic', ['A', 'D']),
    (['Epic', 1], ['A', 'B', 'C', 'D']),
    (99, [])])
def test_get_keys_in_order(only_levels: int | str | Sequence[int | str],
                           expected: list[str]) -> None:
    """Test keys are kept by level, in backlog order, using default levels."""
    assert get_keys_in_order(_level_backlog(), only_levels) == expected


def test_keys_custom_levels() -> None:
    """Test a level name is resolved through a supplied levels mapping."""
    levels = {1: Level(level=1, name='Item', aliases=['Card'])}
    keys = get_keys_in_order(_level_backlog(), 'Card', levels)
    assert keys == ['B', 'C']


def test_keys_unknown_name() -> None:
    """Test an unknown level name raises ValueError."""
    with pytest.raises(ValueError):
        get_keys_in_order(_level_backlog(), 'Nope')


@pytest.mark.parametrize('only_levels', [1.5, True, [1, 2.0]])
def test_keys_wrong_type(only_levels: object) -> None:
    """Test a level that is not an int or str raises TypeError."""
    with pytest.raises(TypeError):
        get_keys_in_order(_level_backlog(),
                          only_levels)  # type: ignore[arg-type]
