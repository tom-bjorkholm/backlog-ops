#! /usr/local/bin/python3
"""Tests for ordering a backlog to follow the release order."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from io import StringIO
from typing import Optional, Sequence
import pytest
from backlogops import (
    Backlog, BacklogItem, Releases, Release, Status, BacklogReleases,
    backlog_in_release_order)
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()


def _item(key: str, release: Optional[str] = None, *, f2s: Sequence[str] = (),
          f2f: Sequence[str] = (), s2s: Sequence[str] = ()) -> BacklogItem:
    """Return a minimal backlog item for the release-order tests."""
    return BacklogItem(key=key, level=1, title=key, story_points=1,
                       status=Status.TODO, release=release,
                       depends_on_f2s=list(f2s), depends_on_f2f=list(f2f),
                       depends_on_s2s=list(s2s))


def _child(key: str, release: Optional[str], parent: str) -> BacklogItem:
    """Return a backlog item that names the given parent."""
    return BacklogItem(key=key, level=1, title=key, story_points=1,
                       status=Status.TODO, release=release, parent_key=parent)


def _releases(*names: str) -> Releases:
    """Return releases with the given names and no dates, in order."""
    return [Release(name=name) for name in names]


def _keys(backlog: Backlog) -> list[str]:
    """Return the keys of a backlog in their current order."""
    return [item.key for item in backlog]


def _run(backlog: Backlog, releases: Releases,
         honor: bool = False) -> list[str]:
    """Order the backlog and return the resulting keys."""
    return _keys(backlog_in_release_order(backlog, releases, honor, NO_OUTPUT))


@pytest.mark.parametrize('honor', [False, True])
def test_release_grouping(honor: bool) -> None:
    """Test items are grouped by the order of the releases list."""
    releases = _releases('R1', 'R2', 'R3')
    backlog = [_item('a', 'R2'), _item('b', 'R1'), _item('c', 'R3'),
               _item('d', 'R1'), _item('e')]
    assert _run(backlog, releases, honor) == ['b', 'd', 'a', 'c', 'e']


def test_no_release_last() -> None:
    """Test items with no release are placed after the last release."""
    releases = _releases('R1', 'R2')
    backlog = [_item('x'), _item('y', 'R1'), _item('z', 'R2'), _item('w')]
    assert _run(backlog, releases) == ['y', 'z', 'x', 'w']


def test_stable_in_release() -> None:
    """Test items of one release keep their original relative order."""
    releases = _releases('R1')
    backlog = [_item('a', 'R1'), _item('b', 'R1'), _item('c', 'R1')]
    assert _run(backlog, releases) == ['a', 'b', 'c']


def test_release_list_order() -> None:
    """Test the release list order, not the names, drives the result."""
    backlog = [_item('a', 'R1'), _item('b', 'R2')]
    assert _run(backlog, _releases('R1', 'R2')) == ['a', 'b']
    assert _run(backlog, _releases('R2', 'R1')) == ['b', 'a']


def test_empty_backlog() -> None:
    """Test an empty backlog yields an empty result."""
    assert not backlog_in_release_order([], _releases('R1'), False, NO_OUTPUT)


def test_unknown_release() -> None:
    """Test an unknown release is reported and placed after the last."""
    releases = _releases('R1')
    backlog = [_item('x', 'R1'), _item('y', 'RX'), _item('z')]
    stderr_file = StringIO()
    result = backlog_in_release_order(backlog, releases, False, stderr_file)
    assert _keys(result) == ['x', 'y', 'z']
    message = stderr_file.getvalue()
    assert 'RX' in message and 'y' in message
    assert message.count('unknown release') == 1


def test_empty_releases() -> None:
    """Test all items follow the backlog order when there is no release."""
    backlog = [_item('a', 'R1'), _item('b'), _item('c', 'R2')]
    stderr_file = StringIO()
    result = backlog_in_release_order(backlog, [], False, stderr_file)
    assert _keys(result) == ['a', 'b', 'c']
    assert stderr_file.getvalue().count('unknown release') == 2


def test_input_unchanged() -> None:
    """Test the argument backlog keeps its order after ordering."""
    releases = _releases('R1', 'R2')
    backlog = [_item('a', 'R2'), _item('b', 'R1')]
    backlog_in_release_order(backlog, releases, False, NO_OUTPUT)
    assert _keys(backlog) == ['a', 'b']


def test_returns_new_list() -> None:
    """Test a new list is returned even for an already ordered backlog."""
    releases = _releases('R1')
    backlog = [_item('a', 'R1'), _item('b', 'R1')]
    result = backlog_in_release_order(backlog, releases, False, NO_OUTPUT)
    assert result is not backlog
    assert _keys(result) == ['a', 'b']


def test_child_before_parent() -> None:
    """Test honoring dependencies places a child before its parent."""
    releases = _releases('R1')
    backlog = [_item('parent', 'R1'), _child('child', 'R1', 'parent')]
    assert _run(backlog, releases, True) == ['child', 'parent']


def _dependent(kind: str) -> BacklogItem:
    """Return item 'b' depending on 'a' through the named relation."""
    on_a = ['a']
    return _item('b', 'R1', f2s=on_a if kind == 'f2s' else [],
                 f2f=on_a if kind == 'f2f' else [],
                 s2s=on_a if kind == 's2s' else [])


@pytest.mark.parametrize('kind, expected', [
    ('f2s', ['a', 'b']), ('f2f', ['a', 'b']), ('s2s', ['b', 'a'])])
def test_relation_orders(kind: str, expected: list[str]) -> None:
    """Test f2s and f2f order delivery, while s2s does not reorder."""
    backlog = [_dependent(kind), _item('a', 'R1')]
    assert _run(backlog, _releases('R1'), True) == expected


def test_dep_pulls_across() -> None:
    """Test a prerequisite in a later release is pulled before its user."""
    releases = _releases('R1', 'R2')
    backlog = [_item('dep', 'R1', f2s=['pre']), _item('pre', 'R2'),
               _item('other', 'R1')]
    assert _run(backlog, releases) == ['dep', 'other', 'pre']
    assert _run(backlog, releases, True) == ['other', 'pre', 'dep']


def test_child_across_release() -> None:
    """Test a child in a later release moves before its earlier parent."""
    releases = _releases('R1', 'R2')
    backlog = [_item('parent', 'R1'), _child('child', 'R2', 'parent')]
    assert _run(backlog, releases) == ['parent', 'child']
    assert _run(backlog, releases, True) == ['child', 'parent']


def test_diamond_transitive() -> None:
    """Test a diamond of finish dependencies is ordered transitively."""
    releases = _releases('R1')
    backlog = [_item('d', 'R1', f2f=['b', 'c']),
               _item('b', 'R1', f2f=['a']),
               _item('c', 'R1', f2f=['a']), _item('a', 'R1')]
    assert _run(backlog, releases, True) == ['a', 'b', 'c', 'd']


def test_cycle_keeps_all() -> None:
    """Test a dependency cycle never drops a backlog item."""
    releases = _releases('R1')
    backlog = [_item('a', 'R1', f2f=['b']), _item('b', 'R1', f2f=['a'])]
    result = _run(backlog, releases, True)
    assert sorted(result) == ['a', 'b']


def test_dangling_dep() -> None:
    """Test a dependency on a key not in the backlog is tolerated."""
    releases = _releases('R1')
    backlog = [_item('b', 'R1', f2s=['GONE']), _item('a', 'R1')]
    assert _run(backlog, releases, True) == ['b', 'a']


def test_input_unchanged_deps() -> None:
    """Test the argument backlog is not modified when honoring deps."""
    releases = _releases('R1', 'R2')
    backlog = [_item('dep', 'R1', f2s=['pre']), _item('pre', 'R2')]
    backlog_in_release_order(backlog, releases, True, NO_OUTPUT)
    assert _keys(backlog) == ['dep', 'pre']


def test_wrapper_orders() -> None:
    """Test the BacklogReleases wrapper reorders the member backlog."""
    releases = _releases('R1', 'R2')
    backlog = [_item('a', 'R2'), _item('b', 'R1')]
    data = BacklogReleases(backlog, releases)
    data.backlog_in_release_order(stderr_file=NO_OUTPUT)
    assert _keys(data.backlog) == ['b', 'a']


def test_wrapper_honor_deps() -> None:
    """Test the wrapper honors dependencies when asked to."""
    releases = _releases('R1', 'R2')
    backlog = [_item('dep', 'R1', f2s=['pre']), _item('pre', 'R2'),
               _item('other', 'R1')]
    data = BacklogReleases(backlog, releases)
    data.backlog_in_release_order(honor_dependencies=True,
                                  stderr_file=NO_OUTPUT)
    assert _keys(data.backlog) == ['other', 'pre', 'dep']
