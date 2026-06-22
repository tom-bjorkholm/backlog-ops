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


def test_overwrite(tmp_path: Path) -> None:
    """Test writing again over the same file overwrites it without error.

    The native save dialog confirms the overwrite, so the GUI write helper
    allows it instead of refusing an existing file.
    """
    path = str(tmp_path / 'out.csv')
    write_backlog(_data(), path, None, None, False)
    write_backlog(_data(), path, None, None, False)
    assert read_backlog(path, None, None).backlog[0].key == 'A1'
