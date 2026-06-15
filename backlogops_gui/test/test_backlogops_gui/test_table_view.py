#! /usr/local/bin/python3
"""Tests for building the backlog and releases tables."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from backlogops import BacklogReleases, Release, get_demo_backlog
from backlogops_gui.table_view import backlog_table, release_table


def test_backlog_columns() -> None:
    """Test the backlog table has a key column and one row per item."""
    data = get_demo_backlog()
    columns, rows = backlog_table(data)
    assert 'key' in columns
    assert len(rows) == len(data.backlog)
    assert all(len(row) == len(columns) for row in rows)


def test_release_columns() -> None:
    """Test the releases table starts with the name column."""
    data = get_demo_backlog()
    columns, rows = release_table(data)
    assert columns[0] == 'name'
    assert len(rows) == len(data.releases)


def test_empty_tables() -> None:
    """Test empty data yields empty columns and rows."""
    data = BacklogReleases(backlog=[], releases=[])
    assert backlog_table(data) == ([], [])
    assert release_table(data) == ([], [])


def test_none_cell_is_blank() -> None:
    """Test a missing date is shown as an empty cell."""
    data = BacklogReleases(backlog=[], releases=[Release(name='R1')])
    columns, rows = release_table(data)
    assert columns[0] == 'name'
    assert rows[0][0] == 'R1'
    assert rows[0][columns.index('planned_date')] == ''
