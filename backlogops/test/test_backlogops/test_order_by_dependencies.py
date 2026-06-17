#! /usr/local/bin/python3
"""Tests for ordering a backlog by dependencies."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional, Sequence
import pytest
from backlogops import (
    Backlog, BacklogItem, Status, order_by_dependencies, DependencyMode)
from backlogops.order_by_dependencies import _merge_even, _space_around_limit
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()


def _item(key: str, *, f2s: Sequence[str] = (), f2f: Sequence[str] = (),
          s2s: Sequence[str] = (), parent: Optional[str] = None
          ) -> BacklogItem:
    """Return a minimal backlog item for the ordering tests."""
    return BacklogItem(key=key, level=1, title=key, story_points=1,
                       status=Status.TODO, parent_key=parent,
                       depends_on_f2s=list(f2s), depends_on_f2f=list(f2f),
                       depends_on_s2s=list(s2s))


def _keys(backlog: Backlog) -> list[str]:
    """Return the keys of a backlog in their current order."""
    return [item.key for item in backlog]


def _run(backlog: Backlog, **kwargs: object) -> list[str]:
    """Order the backlog with the given options and return the keys."""
    return _keys(order_by_dependencies(backlog, stderr_file=NO_OUTPUT,
                                       **kwargs))  # type: ignore[arg-type]


def test_no_deps_same_object() -> None:
    """Test a backlog without dependencies is returned unchanged."""
    backlog = [_item('A'), _item('B'), _item('C')]
    result = order_by_dependencies(backlog, stderr_file=NO_OUTPUT)
    assert result is backlog


@pytest.mark.parametrize('backlog', [[], [_item('only')]])
def test_trivial_backlogs(backlog: Backlog) -> None:
    """Test empty and single-item backlogs are returned unchanged."""
    assert order_by_dependencies(backlog, stderr_file=NO_OUTPUT) is backlog


def test_forward_pulls_prereq() -> None:
    """Test the default forward mode pulls a prerequisite just ahead."""
    backlog = [_item('C', f2s=['P']), _item('X'), _item('P')]
    assert _run(backlog) == ['P', 'C', 'X']


def test_later_pushes() -> None:
    """Test later mode keeps prerequisites and pushes the dependent."""
    backlog = [_item('C', f2s=['P']), _item('X'), _item('P')]
    assert _run(backlog, later=True) == ['X', 'P', 'C']


def test_independent_kept() -> None:
    """Test items in no dependency keep their relative order in KEEP."""
    backlog = [_item('D', f2s=['A']), _item('B'), _item('C'), _item('A')]
    assert _run(backlog) == ['A', 'D', 'B', 'C']
    assert _run(backlog, later=True) == ['B', 'C', 'A', 'D']


def test_f2f_no_reorder() -> None:
    """Test a finish-to-finish dependency does not move an item."""
    backlog = [_item('B', f2f=['A']), _item('A')]
    assert _run(backlog) == ['B', 'A']


def test_s2s_orders() -> None:
    """Test a start-to-start dependency orders the start of the items."""
    backlog = [_item('B', s2s=['A']), _item('A')]
    assert _run(backlog) == ['A', 'B']


def test_parent_first() -> None:
    """Test the implicit parent relation starts the parent first."""
    backlog = [_item('child', parent='parent'), _item('parent')]
    assert _run(backlog) == ['parent', 'child']


def test_early_mode() -> None:
    """Test EARLY places all linked items before the independent ones."""
    backlog = [_item('A'), _item('F1'), _item('B', f2s=['A']), _item('F2')]
    assert _run(backlog, mode=DependencyMode.EARLY) == ['A', 'B', 'F1', 'F2']


def test_even_mode() -> None:
    """Test EVEN spreads the linked items evenly among the others."""
    backlog = [_item('A'), _item('F1'), _item('B', f2s=['A']), _item('F2')]
    assert _run(backlog, mode=DependencyMode.EVEN) == ['F1', 'A', 'F2', 'B']


def test_space_moves_item() -> None:
    """Test a key with only prerequisites is pushed to the back."""
    backlog = [_item('A'), _item('B', f2s=['A']), _item('C', f2s=['B']),
               _item('F1'), _item('F2'), _item('F3')]
    assert _run(backlog, space_around='C') == \
        ['A', 'B', 'F1', 'F2', 'F3', 'C']


def test_space_sequence() -> None:
    """Test space_around accepts a sequence of keys."""
    backlog = [_item('A'), _item('B', f2s=['A']), _item('F1'), _item('F2')]
    assert _run(backlog, space_around=['B']) == ['A', 'F1', 'F2', 'B']


def test_space_chain() -> None:
    """Test space_around spreads a named item far from its chain."""
    backlog = [_item('S1'), _item('D2'), _item('D3', f2s=['D2']),
               _item('D4', f2s=['D3']), _item('S5'), _item('S6'),
               _item('S7')]
    assert _run(backlog, space_around='D3') == \
        ['D2', 'S1', 'S5', 'D3', 'S6', 'S7', 'D4']
    assert _run(backlog, space_around='D2') == \
        ['D2', 'S1', 'S5', 'S6', 'S7', 'D3', 'D4']


@pytest.mark.parametrize('bad', [123, ['ok', 7], object()])
def test_space_wrong_type(bad: object) -> None:
    """Test a non-string, non-sequence-of-strings raises TypeError."""
    backlog = [_item('A'), _item('B', f2s=['A'])]
    with pytest.raises(TypeError):
        order_by_dependencies(backlog, space_around=bad,  # type: ignore
                              stderr_file=NO_OUTPUT)


def test_space_unknown() -> None:
    """Test a space_around key not in the backlog raises KeyError."""
    backlog = [_item('A'), _item('B', f2s=['A'])]
    with pytest.raises(KeyError):
        order_by_dependencies(backlog, space_around='missing',
                              stderr_file=NO_OUTPUT)


def test_space_too_many() -> None:
    """Test more space_around keys than allowed raises RuntimeError."""
    backlog = [_item(f'K{index}') for index in range(8)]
    with pytest.raises(RuntimeError):
        order_by_dependencies(backlog, space_around=['K0', 'K1'],
                              stderr_file=NO_OUTPUT)


def test_input_unchanged() -> None:
    """Test the argument backlog keeps its order after ordering."""
    backlog = [_item('C', f2s=['P']), _item('X'), _item('P')]
    order_by_dependencies(backlog, stderr_file=NO_OUTPUT)
    assert _keys(backlog) == ['C', 'X', 'P']


def test_diamond_two_prereqs() -> None:
    """Test an item depending on two prerequisites is ordered after both.

    The diamond A -> B, A -> C, (B, C) -> D exercises a dependent that is
    still pending after one prerequisite finishes, and a prerequisite that
    is reached along two paths during the start-reachability search.
    """
    backlog = [_item('D', f2s=['B', 'C']), _item('B', f2s=['A']),
               _item('C', f2s=['A']), _item('A')]
    for order in (_run(backlog), _run(backlog, later=True)):
        position = {key: index for index, key in enumerate(order)}
        assert position['A'] < position['B'] < position['D']
        assert position['A'] < position['C'] < position['D']


def test_dangling_dep() -> None:
    """Test a dependency on a key not in the backlog is tolerated.

    The ordering assumes a consistent backlog but degrades gracefully: a
    reference to a missing key is ignored rather than dropping the item.
    """
    backlog = [_item('B', f2s=['A', 'GONE']), _item('A')]
    assert _run(backlog) == ['A', 'B']


@pytest.mark.parametrize('count, expected', [
    (0, 1), (8, 1), (30, 3), (49, 4), (50, 5), (100, 5)])
def test_space_around_limit(count: int, expected: int) -> None:
    """Test the space_around limit caps at five for large backlogs."""
    assert _space_around_limit(count) == expected


def test_merge_even_no_linked() -> None:
    """Test merging with no linked keys returns the unlinked keys as is."""
    assert _merge_even([], ['A', 'B', 'C']) == ['A', 'B', 'C']


def test_all_deps_respected() -> None:
    """Test every start constraint is honored in a longer backlog."""
    backlog = [_item('E', f2s=['C']), _item('A'), _item('C', s2s=['B']),
               _item('B', f2s=['A']), _item('D', parent='E')]
    order = _run(backlog)
    position = {key: index for index, key in enumerate(order)}
    assert position['A'] < position['B'] < position['C'] < position['E']
    assert position['E'] < position['D']
