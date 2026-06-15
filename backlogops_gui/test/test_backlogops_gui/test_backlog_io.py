#! /usr/local/bin/python3
"""Tests for reading and writing a backlog with format options."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from backlogops import BacklogItem, BacklogReleases, Release, Status
from backlogops_gui.backlog_io import read_backlog, write_backlog


def _data() -> BacklogReleases:
    """Return a small backlog and releases used as test data."""
    return BacklogReleases(
        backlog=[BacklogItem(key='A1', level=1, title='First', story_points=5,
                             status=Status.TODO, release='R1')],
        releases=[Release(name='R1')])


def test_round_trip(tmp_path: Path) -> None:
    """Test data written by inference reads back with the same keys."""
    path = str(tmp_path / 'out.csv')
    write_backlog(_data(), path, None, None, False)
    data = read_backlog(path, None, None)
    assert [item.key for item in data.backlog] == ['A1']
    assert [release.name for release in data.releases] == ['R1']
