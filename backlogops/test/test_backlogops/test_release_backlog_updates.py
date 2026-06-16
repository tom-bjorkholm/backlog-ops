#! /usr/local/bin/python3
"""Tests for the release update operations on a backlog."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date, timedelta
from typing import Optional
import pytest
from backlogops import (
    BacklogItem, Release, Status, adjust_release_content,
    estimate_release_dates, release_plan_on_estimate)


def _item(key: str, release: Optional[str], ready: Optional[date],
          status: Status = Status.TODO) -> BacklogItem:
    """Return a one-point backlog item with a release and an estimate."""
    return BacklogItem(key=key, level=1, title=key, story_points=1,
                       status=status, release=release,
                       estimated_ready_date=ready)


def _date_changes(changes: object) -> list[tuple[str, object, object]]:
    """Return date change records as comparable tuples."""
    assert isinstance(changes, list)
    return [(c.release, c.old_date, c.new_date) for c in changes]


def test_est_latest() -> None:
    """Test a release estimate is the latest of its item estimates."""
    backlog = [_item('a', 'R1', date(2026, 1, 10)),
               _item('b', 'R1', date(2026, 1, 20))]
    new_releases, changes = estimate_release_dates([Release(name='R1')],
                                                   backlog)
    assert new_releases[0].estimated_date == date(2026, 1, 20)
    assert _date_changes(changes) == [('R1', None, date(2026, 1, 20))]


def test_est_none() -> None:
    """Test a release with no estimable item gets no estimated date."""
    backlog = [_item('a', 'R2', None, status=Status.DONE)]
    old = Release(name='R1', estimated_date=date(2025, 1, 1))
    new_releases, changes = estimate_release_dates([old], backlog)
    assert new_releases[0].estimated_date is None
    assert _date_changes(changes) == [('R1', date(2025, 1, 1), None)]


def test_est_no_change() -> None:
    """Test an unchanged estimated date produces no change record."""
    backlog = [_item('a', 'R1', date(2026, 1, 10))]
    release = Release(name='R1', estimated_date=date(2026, 1, 10))
    new_releases, changes = estimate_release_dates([release], backlog)
    assert new_releases[0].estimated_date == date(2026, 1, 10)
    assert not changes


def test_plan_adds_buffer() -> None:
    """Test the planned date is the estimated date plus the buffer."""
    release = Release(name='R1', estimated_date=date(2026, 1, 10))
    new_releases, changes = release_plan_on_estimate([release],
                                                     timedelta(days=5))
    assert new_releases[0].planned_date == date(2026, 1, 15)
    assert _date_changes(changes) == [('R1', None, date(2026, 1, 15))]


def test_plan_none() -> None:
    """Test a release with no estimate gets no planned date."""
    release = Release(name='R1', planned_date=date(2025, 1, 1))
    new_releases, changes = release_plan_on_estimate([release],
                                                     timedelta(days=5))
    assert new_releases[0].planned_date is None
    assert _date_changes(changes) == [('R1', date(2025, 1, 1), None)]


@pytest.mark.parametrize('buffer', [timedelta(days=-1), timedelta(seconds=-1)])
def test_neg_buffer(buffer: timedelta) -> None:
    """Test a negative buffer is rejected by both buffer operations."""
    with pytest.raises(ValueError):
        release_plan_on_estimate([], buffer)
    with pytest.raises(ValueError):
        adjust_release_content([], [], buffer)


def _release(name: str, planned: Optional[date]) -> Release:
    """Return a release with only a planned date."""
    return Release(name=name, planned_date=planned)


def test_content_push() -> None:
    """Test an item that misses its release moves to the next one."""
    releases = [_release('R1', date(2026, 1, 15)),
                _release('R2', date(2026, 2, 1))]
    backlog = [_item('b', 'R1', date(2026, 1, 20))]
    new_backlog, changes = adjust_release_content(releases, backlog,
                                                  timedelta(days=5))
    assert new_backlog[0].release == 'R2'
    assert changes[0].old_release == 'R1'
    assert changes[0].new_release == 'R2'


def test_content_pull() -> None:
    """Test an item that now fits sooner moves to the earlier release."""
    releases = [_release('R1', date(2026, 1, 15)),
                _release('R2', date(2026, 2, 1))]
    backlog = [_item('a', 'R2', date(2026, 1, 5))]
    new_backlog, _ = adjust_release_content(releases, backlog,
                                            timedelta(days=5))
    assert new_backlog[0].release == 'R1'


def test_content_remove() -> None:
    """Test an item later than every release loses its release."""
    releases = [_release('R1', date(2026, 1, 15))]
    backlog = [_item('a', 'R1', date(2026, 6, 1))]
    new_backlog, changes = adjust_release_content(releases, backlog,
                                                  timedelta(days=5))
    assert new_backlog[0].release is None
    assert changes[0].new_release is None


def test_content_keep() -> None:
    """Test an item with no estimate keeps its release unchanged."""
    releases = [_release('R1', date(2026, 1, 15))]
    backlog = [_item('a', 'R1', None)]
    new_backlog, changes = adjust_release_content(releases, backlog,
                                                  timedelta(days=5))
    assert new_backlog[0].release == 'R1'
    assert not changes


def test_content_assign() -> None:
    """Test an item with no release is assigned to where it fits."""
    releases = [_release('R1', date(2026, 1, 15))]
    backlog = [_item('b', None, date(2026, 1, 1))]
    new_backlog, changes = adjust_release_content(releases, backlog,
                                                  timedelta(days=5))
    assert new_backlog[0].release == 'R1'
    assert changes[0].old_release is None
    assert changes[0].new_release == 'R1'


def test_content_undated() -> None:
    """Test a release with no planned date is no target for an item."""
    releases = [_release('R1', None), _release('R2', date(2026, 2, 1))]
    backlog = [_item('a', 'R1', date(2026, 1, 1))]
    new_backlog, _ = adjust_release_content(releases, backlog,
                                            timedelta(days=5))
    assert new_backlog[0].release == 'R2'
