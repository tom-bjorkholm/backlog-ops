#! /usr/local/bin/python3
"""Tests for the remaining time of backlog items in rows and files.

Also tests leaving out columns that are empty on every row, which decides
whether a remaining time column is written at all.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional
import openpyxl
import pytest
from tableio import Fmt, TimeDeltaFallback, ValueFmt
from backlogops import (
    BacklogItem, BacklogReleases, Release, Status, drop_empty_columns,
    get_backlog_item, item_to_row, make_output_config, omittable_columns,
    read_backlog_releases, resolve_input_config, resolve_output_config,
    row_to_item, write_backlog_releases)
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()
FORMATS = ['.csv', '.ods', '.xlsx']


def _item(remaining: Optional[timedelta] = None,
          key: str = 'A1') -> BacklogItem:
    """Return a minimal valid backlog item with a remaining time."""
    return BacklogItem(key=key, level=1, title='T', story_points=3,
                       status=Status.TODO, remaining_time=remaining)


def _row(remaining: object) -> dict[str, object]:
    """Return a minimal backlog row with the given remaining time cell."""
    return {'key': 'A1', 'level': 1, 'title': 'T', 'story_points': 1,
            'status': 'TODO', 'remaining_time': remaining}


@pytest.mark.parametrize('remaining', [
    None, timedelta(0), timedelta(days=1, hours=1, minutes=30, seconds=45)])
def test_item_to_row(remaining: Optional[timedelta]) -> None:
    """Test a remaining time cell is the timedelta, for TableIO to write."""
    assert item_to_row(_item(remaining))['remaining_time'] == remaining


def test_extra_timedelta() -> None:
    """Test an extra field holding a timedelta is kept as a timedelta."""
    item = _item()
    item.extra_fields['spent'] = timedelta(hours=4)
    assert item_to_row(item)['spent'] == timedelta(hours=4)


@pytest.mark.parametrize('cell, expected', [
    ('25:30:00', timedelta(hours=25, minutes=30)),
    ('1d 1:30:00', timedelta(hours=25, minutes=30)),
    ('1w 00:00:00', timedelta(days=7)),
    ('1 day, 1:30:00', timedelta(hours=25, minutes=30)),
    ('12:00:00', timedelta(hours=12)),
    ('00:00:01.5', timedelta(seconds=1.5)),
    ('0:00:00', timedelta(0)),
    (timedelta(hours=2), timedelta(hours=2)),
    (90, timedelta(seconds=90)),
    (5400.5, timedelta(seconds=5400.5)),
    ('90', timedelta(seconds=90)),
    ('-1:00:00', timedelta(hours=-1)),
    ('', None),
    (None, None)])
def test_row_to_item(cell: object, expected: Optional[timedelta]) -> None:
    """Test TableIO durations, seconds and an empty cell are read.

    A number counts seconds, as TableIO's ``FLOATSECONDS`` writes it. A
    negative remaining time is read, and refused by the consistency check.
    """
    item = row_to_item(_row(cell), stderr_file=NO_OUTPUT)
    assert item.remaining_time == expected


def test_row_no_column() -> None:
    """Test a row without a remaining time column has no remaining time."""
    row = _row(None)
    del row['remaining_time']
    assert row_to_item(row, stderr_file=NO_OUTPUT).remaining_time is None


@pytest.mark.parametrize('cell', [
    '1:30', '1h', '1w', 'soon', True, datetime(1900, 1, 1, 1, 30)])
def test_row_refused(cell: object) -> None:
    """Test a boolean, a date and text not a duration are refused."""
    with pytest.raises(TypeError, match='remaining_time'):
        row_to_item(_row(cell), stderr_file=NO_OUTPUT)


def test_get_item_timedelta() -> None:
    """Test a timedelta given to get_backlog_item is kept as it is."""
    data = {**_row(None), 'status': Status.TODO,
            'remaining_time': timedelta(minutes=5)}
    item = get_backlog_item(data, stderr_file=NO_OUTPUT)
    assert item.remaining_time == timedelta(minutes=5)


@pytest.mark.parametrize('remaining', [None, timedelta(0), timedelta(days=9)])
def test_consistency_ok(remaining: Optional[timedelta]) -> None:
    """Test no, zero and a positive remaining time are consistent."""
    _item(remaining).check_consistency(NO_OUTPUT)


def test_consistency_negative() -> None:
    """Test a negative remaining time is refused."""
    with pytest.raises(ValueError, match='must not be negative'):
        _item(timedelta(seconds=-1)).check_consistency(NO_OUTPUT)


def test_consistency_type() -> None:
    """Test a remaining time that is not a timedelta is refused."""
    item = _item()
    item.remaining_time = 5  # type: ignore[assignment]
    with pytest.raises(TypeError, match='remaining_time'):
        item.check_consistency(NO_OUTPUT)


ORDER = ['key', 'remaining_time', 'release']
"""A column order holding the remaining time column."""


@pytest.mark.parametrize('order, omit, use_rt, expected', [
    (ORDER, True, True, ORDER),
    (ORDER, True, False, ORDER),
    (ORDER, False, False, ['remaining_time']),
    (ORDER, False, True, []),
    (['key', 'release'], False, False, []),
    ([], True, False, [])])
def test_omittable(order: list[str], omit: bool, use_rt: bool,
                   expected: list[str]) -> None:
    """Test which columns may be left out when empty on every row."""
    assert omittable_columns(order, omit, use_rt) == expected


def _cells(**values: object) -> dict[str, ValueFmt]:
    """Return one formatted row with plain cells of the given values."""
    return {name: ValueFmt(value=value, fmt=Fmt())  # type: ignore[arg-type]
            for name, value in values.items()}


def test_drop_empty() -> None:
    """Test only candidates empty on every row are dropped."""
    rows = [_cells(key='A1', deps='', release=None, note=None),
            _cells(key='A2', deps='', release='R1')]
    order = ['key', 'deps', 'release', 'note']
    kept, kept_order = drop_empty_columns(rows, order,
                                          ['deps', 'release', 'note'])
    assert kept_order == ['key', 'release']
    assert [list(row) for row in kept] == [['key', 'release']] * 2


def test_drop_not_candidate() -> None:
    """Test an empty column that is no candidate is kept."""
    rows = [_cells(key='A1', release=None)]
    kept, kept_order = drop_empty_columns(rows, ['key', 'release'], [])
    assert kept_order == ['key', 'release']
    assert kept == rows


def test_drop_no_rows() -> None:
    """Test every candidate is empty when there are no rows."""
    assert drop_empty_columns([], ['key', 'note'], ['note']) == ([], ['key'])


def _data(remaining: Optional[timedelta]) -> BacklogReleases:
    """Return a two-item backlog, one item with a remaining time."""
    return BacklogReleases(backlog=[_item(remaining), _item(key='A2')],
                           releases=[Release(name='R1'), Release(name='R2')])


def _write(data: BacklogReleases, path: Path, omit: bool,
           use_rt: bool) -> None:
    """Write ``data`` with the given column omission settings."""
    base = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    config = make_output_config(base.tableio, {}, {}, omit_none_column=omit)
    write_backlog_releases(data, path, config, stderr_file=NO_OUTPUT,
                           use_remaining_time=use_rt)


def _read(path: Path) -> BacklogReleases:
    """Read a backlog file with the default input configuration."""
    config = resolve_input_config(None, data_file=path, stderr_file=NO_OUTPUT)
    return read_backlog_releases(path, config, stderr_file=NO_OUTPUT)


def _header(path: Path, heading: str) -> list[str]:
    """Return the column names of the CSV table after ``heading``."""
    lines = [line for line in path.read_text(encoding='UTF-8').splitlines()
             if line]
    titles = [line.lstrip('#').strip() for line in lines]
    header = lines[titles.index(heading) + 1]
    return [name.strip('"') for name in header.split(',')]


@pytest.mark.parametrize('omit, use_rt, remaining, written', [
    (False, True, None, True),
    (False, False, None, False),
    (False, False, timedelta(hours=2), True),
    (True, True, None, False),
    (True, True, timedelta(hours=2), True)])
def test_write_rt_column(omit: bool, use_rt: bool,
                         remaining: Optional[timedelta], written: bool,
                         tmp_path: Path) -> None:
    """Test when the remaining time column is written."""
    path = tmp_path / 'data.csv'
    _write(_data(remaining), path, omit, use_rt)
    assert ('remaining_time' in _header(path, 'Backlog')) == written


@pytest.mark.parametrize('omit', [False, True])
def test_write_omit_columns(omit: bool, tmp_path: Path) -> None:
    """Test omit_none_column leaves out empty columns of both tables."""
    path = tmp_path / 'data.csv'
    _write(_data(None), path, omit, use_rt=True)
    backlog = _header(path, 'Backlog')
    releases = _header(path, 'Releases')
    assert ('planned_ready_date' in backlog) != omit
    assert ('depends_on_f2s' in backlog) != omit
    assert ('planned_date' in releases) != omit
    assert {'key', 'title', 'status', 'story_points'} <= set(backlog)
    assert releases[0] == 'name'


def test_write_one_release(tmp_path: Path) -> None:
    """Test one release without dates keeps its columns when omitting.

    Only a name column would be left, a table of one cell, which TableIO
    cannot write.
    """
    path = tmp_path / 'data.csv'
    data = _data(None)
    data.releases.pop()
    _write(data, path, omit=True, use_rt=True)
    assert _header(path, 'Releases') == ['name', 'planned_date',
                                         'estimated_date']
    assert 'planned_ready_date' not in _header(path, 'Backlog')
    assert [release.name for release in _read(path).releases] == ['R1']


def test_write_mapped_rt(tmp_path: Path) -> None:
    """Test the remaining time column is renamed after the omission."""
    path = tmp_path / 'data.csv'
    base = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    config = make_output_config(base.tableio, {'remaining_time': 'Left'}, {})
    write_backlog_releases(_data(timedelta(hours=3)), path, config,
                           stderr_file=NO_OUTPUT)
    assert 'Left' in _header(path, 'Backlog')
    assert '"03:00:00"' in path.read_text(encoding='UTF-8')


@pytest.mark.parametrize('suffix', FORMATS)
def test_round_trip(suffix: str, tmp_path: Path) -> None:
    """Test a remaining time round-trips through every file format."""
    path = tmp_path / ('data' + suffix)
    remaining = timedelta(days=1, hours=1, minutes=30, seconds=45)
    _write(_data(remaining), path, omit=False, use_rt=False)
    back = {item.key: item.remaining_time for item in _read(path).backlog}
    assert back == {'A1': remaining, 'A2': None}


@pytest.mark.parametrize('fallback', list(TimeDeltaFallback))
def test_csv_fallbacks(fallback: TimeDeltaFallback, tmp_path: Path) -> None:
    """Test every TableIO duration fallback of a CSV file reads back."""
    path = tmp_path / 'data.csv'
    base = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    base.tableio.timedelta_fallback = fallback
    config = make_output_config(base.tableio, {}, {})
    remaining = timedelta(weeks=1, days=1, hours=2, seconds=1.5)
    write_backlog_releases(_data(remaining), path, config,
                           stderr_file=NO_OUTPUT, use_remaining_time=True)
    assert _read(path).backlog[0].remaining_time == remaining


def test_excel_duration_cell(tmp_path: Path) -> None:
    """Test Excel duration and time cells are read as remaining times.

    A spreadsheet program turns a typed ``25:30:00`` into a duration cell,
    which TableIO reads as a ``timedelta``, and a cell formatted as a time
    of day reaches the reader as the text ``12:00:00``.
    """
    path = tmp_path / 'data.xlsx'
    book = openpyxl.Workbook()
    sheet = book.active
    assert sheet is not None
    sheet.append(['key', 'level', 'title', 'status', 'remaining_time'])
    sheet.append(['A1', 1, 'T', 'TODO', 25.5 / 24])
    sheet.append(['A2', 1, 'T', 'TODO', 0.5])
    sheet['E2'].number_format = '[h]:mm:ss'
    sheet['E3'].number_format = 'hh:mm:ss'
    book.save(path)
    back = {item.key: item.remaining_time for item in _read(path).backlog}
    assert back == {'A1': timedelta(hours=25, minutes=30),
                    'A2': timedelta(hours=12)}


def test_estimate_date_kept(tmp_path: Path) -> None:
    """Test leaving out empty columns keeps a column with any value."""
    path = tmp_path / 'data.csv'
    data = _data(None)
    data.backlog[1].estimated_ready_date = date(2026, 6, 1)
    _write(data, path, omit=True, use_rt=False)
    assert 'estimated_ready_date' in _header(path, 'Backlog')
    assert _read(path).backlog[1].estimated_ready_date == date(2026, 6, 1)
