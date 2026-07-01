#! /usr/local/bin/python3
"""Tests for the backlog and its related releases."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from typing import Optional

import pytest

from backlogops.backlog import BacklogItem, Status
from backlogops.backlog_releases import BacklogReleases
from backlogops.releases import Release
from backlogops.no_text_io import NoTextIO


def _item(key: str, release: Optional[str] = None,
          level: int = 1) -> BacklogItem:
    """Return one valid backlog item with an optional release."""
    return BacklogItem(key=key, level=level, title='Title', story_points=3,
                       status=Status.TODO, release=release)


def _backlog() -> list[BacklogItem]:
    """Return a small backlog whose items name releases R1 and R2."""
    return [_item('BI-1', 'R1', level=2),
            _item('BI-2', 'R2'),
            _item('BI-3', 'R1')]


def test_add_creates_releases() -> None:
    """Test releases named by the backlog are added with no dates."""
    releases = BacklogReleases.add_to_releases(_backlog(), [])
    assert releases == [Release(name='R1'), Release(name='R2')]


def test_add_keeps_existing() -> None:
    """Test existing releases are kept and only missing ones added."""
    existing = [Release(name='R2', planned_date=None)]
    releases = BacklogReleases.add_to_releases(_backlog(), existing)
    assert [release.name for release in releases] == ['R2', 'R1']


def test_add_no_change_same() -> None:
    """Test the argument list is returned unchanged when nothing is new."""
    existing = [Release(name='R1'), Release(name='R2')]
    releases = BacklogReleases.add_to_releases(_backlog(), existing)
    assert releases is existing


def test_add_keeps_arg() -> None:
    """Test the passed releases list is never modified in place."""
    existing: list[Release] = []
    BacklogReleases.add_to_releases(_backlog(), existing)
    assert not existing


def test_add_skips_no_rel() -> None:
    """Test items without a release contribute no release."""
    backlog = [_item('BI-1'), _item('BI-2')]
    assert not BacklogReleases.add_to_releases(backlog, [])


def test_check_in_ok() -> None:
    """Test all backlog releases present in the list pass the check."""
    releases = [Release(name='R1'), Release(name='R2')]
    BacklogReleases.check_in_releases(_backlog(), releases, NoTextIO())


def test_check_in_missing() -> None:
    """Test a backlog release missing from the list is a KeyError."""
    releases = [Release(name='R1')]
    with pytest.raises(KeyError):
        BacklogReleases.check_in_releases(_backlog(), releases, NoTextIO())


def test_update_releases() -> None:
    """Test update_releases adds the backlog releases to the member list."""
    backlog_releases = BacklogReleases(_backlog(), [])
    backlog_releases.update_releases()
    assert backlog_releases.releases == [Release(name='R1'),
                                         Release(name='R2')]


def test_check_xref_ok() -> None:
    """Test the cross reference check passes after update_releases."""
    backlog_releases = BacklogReleases(_backlog(), [])
    backlog_releases.update_releases()
    backlog_releases.check_release_xref(NoTextIO())


def test_check_xref_missing() -> None:
    """Test the cross reference check fails for a missing release."""
    backlog_releases = BacklogReleases(_backlog(), [Release(name='R1')])
    with pytest.raises(KeyError):
        backlog_releases.check_release_xref(NoTextIO())


def test_cons_ok() -> None:
    """Test a consistent backlog with its releases passes the check."""
    releases = [Release(name='R1'), Release(name='R2')]
    BacklogReleases(_backlog(), releases).check_consistency(NoTextIO())


def test_cons_label_release() -> None:
    """Test release labels with spaces and punctuation match by name."""
    release_name = 'First release (R1.0)'
    backlog = [_item('BI-1', release_name)]
    releases = [Release(name=release_name)]
    BacklogReleases(backlog, releases).check_consistency(NoTextIO())


def test_cons_missing_rel() -> None:
    """Test a release named by the backlog but absent is a KeyError."""
    backlog_releases = BacklogReleases(_backlog(), [Release(name='R1')])
    with pytest.raises(KeyError):
        backlog_releases.check_consistency(NoTextIO())


def test_cons_dup_release() -> None:
    """Test duplicate release names are reported as a ValueError."""
    releases = [Release(name='R1'), Release(name='R2'), Release(name='R1')]
    backlog_releases = BacklogReleases(_backlog(), releases)
    with pytest.raises(ValueError):
        backlog_releases.check_consistency(NoTextIO())


def test_cons_bad_backlog() -> None:
    """Test an inconsistent backlog is reported by the check."""
    backlog = [_item('BI-1', 'R1'), _item('BI-1', 'R1')]
    backlog_releases = BacklogReleases(backlog, [Release(name='R1')])
    with pytest.raises(ValueError):
        backlog_releases.check_consistency(NoTextIO())


def test_cons_bad_release() -> None:
    """Test an internally invalid release is reported by the check."""
    backlog_releases = BacklogReleases([_item('BI-1', 'R1')],
                                       [Release(name=' R1')])
    with pytest.raises(ValueError):
        backlog_releases.check_consistency(NoTextIO())


def test_order_dates_planned() -> None:
    """Test the wrapper orders the member releases by planned date."""
    releases = [Release(name='B', planned_date=date(2026, 2, 1)),
                Release(name='A', planned_date=date(2026, 1, 1))]
    data = BacklogReleases([], releases)
    data.order_releases_by_date(stderr_file=NoTextIO())
    assert [release.name for release in data.releases] == ['A', 'B']


def test_order_dates_est() -> None:
    """Test the wrapper can order by the estimated date instead."""
    releases = [Release(name='A', estimated_date=date(2026, 2, 1)),
                Release(name='B', estimated_date=date(2026, 1, 1))]
    data = BacklogReleases([], releases)
    data.order_releases_by_date(by_estimated=True, stderr_file=NoTextIO())
    assert [release.name for release in data.releases] == ['B', 'A']
