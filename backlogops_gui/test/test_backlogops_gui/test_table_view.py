#! /usr/local/bin/python3
"""Tests for building the backlog and releases tables."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import ttk
from datetime import date
from typing import cast
import pytest
from tableio import Color, Fmt, ValueFmt
from backlogops import (
    BacklogItem, BacklogReleases, LevelDisplay, Release, Status,
    get_demo_backlog)
from backlogops_gui import table_view
from backlogops_gui.table_view import (
    HIGHLIGHT_FILL, backlog_table, make_table, release_table,
    supports_cell_tags, _tag_name)
from backlogops_gui.table_view import _insert_row, _row_format


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


def _one_item_data() -> BacklogReleases:
    """Return a one-item backlog used by the level display tests."""
    item = BacklogItem(key='A1', level=1, title='T', story_points=3,
                       status=Status.TODO)
    return BacklogReleases(backlog=[item], releases=[])


def test_level_display_both() -> None:
    """Test the default display shows a numeric and a named level column."""
    columns, _rows = backlog_table(_one_item_data())
    assert 'level' in columns and 'level name' in columns


def test_level_disp_numeric() -> None:
    """Test the numeric display shows only the numeric level column."""
    columns, _rows = backlog_table(_one_item_data(),
                                   display=LevelDisplay.NUMERIC)
    assert 'level' in columns and 'level name' not in columns


def test_level_display_name() -> None:
    """Test the name display shows the level name in its own column."""
    columns, rows = backlog_table(_one_item_data(), display=LevelDisplay.NAME)
    assert 'level name' in columns and 'level' not in columns
    assert rows[0][columns.index('level name')].value == 'Story'


def test_backlog_rename() -> None:
    """Test the backlog map renames one column and drops another."""
    columns, _rows = backlog_table(_one_item_data(),
                                   names={'key': 'Id', 'story_points': None})
    assert 'Id' in columns and 'key' not in columns
    assert 'story_points' not in columns


def test_release_rename() -> None:
    """Test the releases map renames the name column shown in the GUI."""
    data = BacklogReleases(backlog=[], releases=[Release(name='R1')])
    columns, _rows = release_table(data, names={'name': 'Release'})
    assert columns[0] == 'Release'


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


def _cell_tagged(tree: ttk.Treeview, tag: str) -> bool:
    """Return whether any cell carries the tag (Tk with cell tags)."""
    return bool(tree.tk.call(str(tree), 'tag', 'cell', 'has', tag))


def _row_tagged(tree: ttk.Treeview, tag: str) -> bool:
    """Return whether the single inserted row carries the tag."""
    item = tree.get_children()[0]
    return bool(tree.tag_has(tag, item))


# pylint: disable-next=too-few-public-methods
class _RaisingTk:
    """Tk stand-in whose call always raises, as an old Tk would."""

    def call(self, *args: object) -> object:
        """Raise as a Tk without per-cell tag support does."""
        raise tk.TclError('tag cell not supported')


# pylint: disable-next=too-few-public-methods
class _FakeTree:
    """Minimal Treeview stand-in for the cell-tag support probe."""

    def __init__(self) -> None:
        """Hold a Tk interpreter stand-in that rejects cell tags."""
        self.tk = _RaisingTk()

    def __str__(self) -> str:
        """Return a widget path the probe can pass to Tk."""
        return 'faketree'


def test_no_cell_tags() -> None:
    """Test the probe reports no support when Tk rejects cell tags."""
    tree = cast(ttk.Treeview, _FakeTree())
    assert supports_cell_tags(tree) is False


# pylint: disable-next=too-few-public-methods
class _RecordingTk:
    """Tk stand-in that records cell-tag calls without a real Tk 8.7."""

    def __init__(self) -> None:
        """Start with an empty record of interpreter calls."""
        self.calls: list[tuple[object, ...]] = []

    def call(self, *args: object) -> str:
        """Record one interpreter call and report success."""
        self.calls.append(args)
        return ''


class _CellTree:
    """Treeview stand-in capturing per-cell styling on any Tk version."""

    def __init__(self) -> None:
        """Start with a recording interpreter and empty row store."""
        self.tk = _RecordingTk()
        self.inserted: list[object] = []

    def __str__(self) -> str:
        """Return a widget path the cell-tag call can use."""
        return 'celltree'

    def tag_configure(self, name: str, **_kwargs: object) -> None:
        """Accept a tag configuration without a real widget."""
        assert name

    def insert(self, _parent: str, _index: str, values: object = None) -> str:
        """Record one inserted row and return its item id."""
        self.inserted.append(values)
        return f'I{len(self.inserted)}'


def test_supports_cell_tags() -> None:
    """Test the probe reports support when the cell-tag call succeeds."""
    assert supports_cell_tags(cast(ttk.Treeview, _CellTree())) is True


def test_cell_tag_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the per-cell tag path styles each formatted cell.

    A fake tree drives the cell-tag code on any Tk version, including an
    older Tk that lacks the per-cell tag subcommand.
    """
    monkeypatch.setattr(table_view, '_tag_font',
                        lambda *a: ('TkDefaultFont', 10, 'bold'))
    fake = _CellTree()
    tree = cast(ttk.Treeview, fake)
    red = Fmt(bold=True, highlight=Color.RED)
    _insert_row(tree, ['a', 'b'],
                [ValueFmt(value='x', fmt=Fmt()),
                 ValueFmt(value='y', fmt=red)], cell_tags=True)
    assert fake.inserted == [['x', 'y']]
    assert fake.tk.calls


@pytest.mark.parametrize('formats, expected', [
    ([Fmt(), Fmt(bold=True)], Fmt(bold=True)),
    ([Fmt(), Fmt()], Fmt())])
def test_row_format(formats: list[Fmt], expected: Fmt) -> None:
    """Test the row format is the first non-plain cell, else plain."""
    row = [ValueFmt(value=None, fmt=fmt) for fmt in formats]
    assert _row_format(row) == expected


def test_row_tag_color() -> None:
    """Test the fallback path colors a whole row by its first format."""
    root = _root_or_skip()
    try:
        tree = ttk.Treeview(root, columns=['a', 'b'], show='headings')
        red = Fmt(bold=True, highlight=Color.RED)
        _insert_row(tree, ['a', 'b'],
                    [ValueFmt(value='x', fmt=Fmt()),
                     ValueFmt(value='y', fmt=red)], cell_tags=False)
        assert _row_tagged(tree, _tag_name(red))
        _insert_row(tree, ['a', 'b'],
                    [ValueFmt(value='p', fmt=Fmt()),
                     ValueFmt(value='q', fmt=Fmt())], cell_tags=False)
        plain = tree.get_children()[1]
        assert tree.item(plain, 'tags') in ((), '')
    finally:
        root.destroy()


def test_cell_color_applied() -> None:
    """Test the late estimate is tagged per cell or per row by Tk."""
    root = _root_or_skip()
    try:
        rel = Release(name='R1', planned_date=date(2026, 1, 1),
                      estimated_date=date(2026, 2, 1))
        data = BacklogReleases(backlog=[], releases=[rel])
        columns, rows = release_table(data)
        tree = make_table(root, columns, rows)
        tag = _tag_name(Fmt(bold=True, highlight=Color.RED))
        if supports_cell_tags(tree):
            assert _cell_tagged(tree, tag)
        else:
            assert _row_tagged(tree, tag)
    finally:
        root.destroy()
