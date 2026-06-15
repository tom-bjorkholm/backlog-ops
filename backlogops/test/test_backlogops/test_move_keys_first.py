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


# Reference cases for move_keys_first. Each case is a (specs, keys,
# expected) triple where specs are (key, level, parent) tuples in the
# original backlog order. The id of each case names the rule it pins
# down, so a case a user brings up can be pointed at directly.
REORDER_CASES = [
    ([('A', 1, None), ('B', 1, None), ('C', 1, None), ('D', 1, None)],
     ['C', 'A'], ['C', 'A', 'B', 'D']),
    ([('E1', 2, None), ('E2', 2, None), ('S1', 1, 'E1'), ('S2', 1, 'E1'),
      ('S3', 1, 'E2')],
     ['E1', 'S3'], ['S1', 'S2', 'E1', 'S3', 'E2']),
    ([('E45', 2, None), ('S451', 1, 'E45'), ('S452', 1, 'E45'),
      ('T4521', 0, 'S452')],
     ['E45'], ['S451', 'T4521', 'S452', 'E45']),
    ([('I1', 3, None), ('E1', 2, 'I1'), ('S1', 1, 'E1')],
     ['I1'], ['S1', 'E1', 'I1']),
    ([('I1', 3, None), ('E1', 2, 'I1'), ('S1', 1, 'E1')],
     ['I1', 'E1'], ['I1', 'S1', 'E1']),
    ([('E1', 2, None), ('S1', 1, 'E1'), ('S2', 1, 'E1')],
     ['E1', 'S1'], ['S2', 'E1', 'S1']),
    ([('E1', 2, None), ('S2', 1, 'E1'), ('S1', 1, 'E1')],
     ['E1'], ['S2', 'S1', 'E1']),
    ([('E1', 2, None), ('E2', 2, None), ('S1', 1, 'E1'), ('S2', 1, 'E2'),
      ('G1', 0, 'S1')],
     ['E2', 'E1'], ['S2', 'E2', 'G1', 'S1', 'E1']),
    ([('E1', 2, None), ('S1', 1, 'E1'), ('T1', 0, 'S1'), ('T2', 0, 'S1'),
      ('S2', 1, 'E1'), ('T3', 0, 'S2')],
     ['E1'], ['T1', 'T2', 'S1', 'T3', 'S2', 'E1']),
    ([('A', 1, None), ('E1', 2, None), ('S1', 1, 'E1'), ('B', 1, None)],
     ['E1'], ['S1', 'E1', 'A', 'B'])]
REORDER_IDS = [
    'flat_keeps_rest_order', 'children_before_named_parent',
    'grandchild_nested_postorder', 'chain_postorder',
    'chain_named_epic_after_initiative', 'named_child_after_named_parent',
    'siblings_keep_backlog_order', 'two_subtrees_in_key_order',
    'several_grandchildren', 'unrelated_items_kept_last']


@pytest.mark.parametrize('specs,keys,expected', REORDER_CASES, ids=REORDER_IDS)
def test_reorder_cases(specs: list[tuple[str, int, Optional[str]]],
                       keys: list[str], expected: list[str]) -> None:
    """Test move_keys_first against the documented reference cases."""
    backlog = [_item(*spec) for spec in specs]
    result = move_keys_first(backlog, keys, NO_OUTPUT)
    assert _order(result) == expected


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
