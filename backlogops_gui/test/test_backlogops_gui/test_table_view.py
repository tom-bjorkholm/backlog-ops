#! /usr/local/bin/python3
"""Tests for building the backlog and releases tables."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from datetime import date
import pytest
from tableio import Color, Fmt
from backlogops import BacklogReleases, Release, get_demo_backlog
from backlogops_gui.table_view import (
    HIGHLIGHT_FILL, backlog_table, make_table, release_table, _tag_name)


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


def test_none_cell_blank() -> None:
    """Test a missing date is an empty, unformatted cell value."""
    data = BacklogReleases(backlog=[], releases=[Release(name='R1')])
    columns, rows = release_table(data)
    assert columns[0] == 'name'
    assert rows[0][0].value == 'R1'
    assert rows[0][columns.index('planned_date')].value is None


def test_late_estimate_red() -> None:
    """Test a late estimate cell carries the late highlight format."""
    rel = Release(name='R1', planned_date=date(2026, 1, 1),
                  estimated_date=date(2026, 2, 1))
    data = BacklogReleases(backlog=[], releases=[rel])
    columns, rows = release_table(data)
    cell = rows[0][columns.index('estimated_date')]
    assert cell.fmt.highlight == Color.RED
    assert cell.fmt.bold


def test_early_estimate_plain() -> None:
    """Test an early estimate leaves the estimate cell unformatted."""
    rel = Release(name='R1', planned_date=date(2026, 2, 1),
                  estimated_date=date(2026, 1, 1))
    data = BacklogReleases(backlog=[], releases=[rel])
    columns, rows = release_table(data)
    assert rows[0][columns.index('estimated_date')].fmt == Fmt()


def test_tag_name_unique() -> None:
    """Test distinct formats map to distinct tag names."""
    late = _tag_name(Fmt(bold=True, highlight=Color.RED))
    done = _tag_name(Fmt(italic=True, highlight=Color.GREEN))
    assert late != done
    assert _tag_name(Fmt()) not in (late, done)


def test_fill_has_colors() -> None:
    """Test the highlight fill covers the colors but not Color.NONE."""
    assert set(HIGHLIGHT_FILL) == {Color.RED, Color.GREEN, Color.YELLOW}
    assert Color.NONE not in HIGHLIGHT_FILL


def _root_or_skip() -> tk.Tk:
    """Return a Tk root, or skip the test when no display is available."""
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip('no display available')
    return root


def test_cell_color_applied() -> None:
    """Test the late estimate cell is tagged in the built table."""
    root = _root_or_skip()
    try:
        rel = Release(name='R1', planned_date=date(2026, 1, 1),
                      estimated_date=date(2026, 2, 1))
        data = BacklogReleases(backlog=[], releases=[rel])
        columns, rows = release_table(data)
        tree = make_table(root, columns, rows)
        tag = _tag_name(Fmt(bold=True, highlight=Color.RED))
        tagged = tree.tk.call(str(tree), 'tag', 'cell', 'has', tag)
        assert tagged
    finally:
        root.destroy()
