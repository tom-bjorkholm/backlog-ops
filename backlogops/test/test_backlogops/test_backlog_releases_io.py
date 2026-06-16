#! /usr/local/bin/python3
"""Tests for reading and writing a backlog and releases with TableIO."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from pathlib import Path
import pytest
from backlogops import (
    BacklogItem, BacklogReleases, FormatRules, Release, Status, item_to_row,
    make_input_config, make_output_config, read_backlog_releases,
    release_to_row, resolve_input_config, resolve_output_config, row_to_item,
    row_to_release, write_backlog_releases)
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()
FORMATS = ['.csv', '.ods', '.xlsx']


def _sample() -> BacklogReleases:
    """Return a small backlog and releases used by several tests."""
    backlog = [
        BacklogItem(key='A1', level=1, title='First', story_points=5,
                    status=Status.TODO, release='R1', team='Blue',
                    depends_on_f2s=['A2'],
                    estimated_ready_date=date(2026, 6, 1)),
        BacklogItem(key='A2', level=1, title='Second', story_points=3,
                    status=Status.DONE, extra_fields={'note': 'hi'})]
    releases = [Release(name='R1', planned_date=date(2026, 7, 1))]
    return BacklogReleases(backlog=backlog, releases=releases)


def test_item_row_special() -> None:
    """Test status, dependencies and dates become simple cell values."""
    item = _sample().backlog[0]
    row = item_to_row(item)
    assert row['status'] == 'TODO'
    assert row['depends_on_f2s'] == 'A2'
    assert row['estimated_ready_date'] == '2026-06-01'


def test_item_row_extra() -> None:
    """Test extra fields are written as their own columns."""
    item = _sample().backlog[1]
    assert item_to_row(item)['note'] == 'hi'


def test_release_row() -> None:
    """Test a release date becomes an ISO string and absent dates are None."""
    row = release_to_row(Release(name='R1', planned_date=date(2026, 7, 1)))
    assert row['name'] == 'R1'
    assert row['planned_date'] == '2026-07-01'
    assert row['estimated_date'] is None


@pytest.mark.parametrize('story_points', [5, '5', 5.0])
@pytest.mark.parametrize('level', [1, '1'])
def test_row_coerce_num(story_points: object, level: object) -> None:
    """Test numeric cells from text formats are coerced to integers."""
    row = {'key': 'A1', 'level': level, 'title': 'T',
           'story_points': story_points, 'status': 'TODO',
           'depends_on_f2s': 'A2 A3'}
    item = row_to_item(row, stderr_file=NO_OUTPUT)
    assert item.story_points == 5
    assert item.level == 1
    assert item.depends_on_f2s == ['A2', 'A3']


def test_row_drop_empty() -> None:
    """Test empty cells of optional fields fall back to their defaults."""
    row = {'key': 'A1', 'level': 1, 'title': 'T', 'story_points': 1,
           'status': 'TODO', 'release': '', 'parent_key': ''}
    item = row_to_item(row, stderr_file=NO_OUTPUT)
    assert item.release is None
    assert item.parent_key is None


def test_row_rel_extra() -> None:
    """Test a releases row keeps known fields and ignores extra columns."""
    row = {'name': 'R1', 'planned_date': '2026-07-01', 'comment': 'x'}
    release = row_to_release(row, stderr_file=NO_OUTPUT)
    assert release.name == 'R1'
    assert release.planned_date == date(2026, 7, 1)


def _round_trip(data: BacklogReleases, path: Path) -> BacklogReleases:
    """Write ``data`` to ``path`` and read it back with default configs."""
    output = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, output, stderr_file=NO_OUTPUT)
    input_config = resolve_input_config(None, data_file=path,
                                        stderr_file=NO_OUTPUT)
    return read_backlog_releases(path, input_config, stderr_file=NO_OUTPUT)


@pytest.mark.parametrize('suffix', FORMATS)
def test_both_roundtrip(suffix: str, tmp_path: Path) -> None:
    """Test a file with both tables round-trips through every format."""
    back = _round_trip(_sample(), tmp_path / ('data' + suffix))
    assert {item.key for item in back.backlog} == {'A1', 'A2'}
    assert [release.name for release in back.releases] == ['R1']
    first = next(item for item in back.backlog if item.key == 'A1')
    assert first.depends_on_f2s == ['A2']
    assert first.estimated_ready_date == date(2026, 6, 1)
    second = next(item for item in back.backlog if item.key == 'A2')
    assert second.extra_fields.get('note') == 'hi'


@pytest.mark.parametrize('suffix', FORMATS)
def test_backlog_only(suffix: str, tmp_path: Path) -> None:
    """Test a file holding only a backlog reads back without releases."""
    data = BacklogReleases(backlog=_sample().backlog, releases=[])
    back = _round_trip(data, tmp_path / ('data' + suffix))
    assert len(back.backlog) == 2
    assert not back.releases


@pytest.mark.parametrize('suffix', FORMATS)
def test_releases_only(suffix: str, tmp_path: Path) -> None:
    """Test a file holding only releases reads back without a backlog."""
    data = BacklogReleases(backlog=[], releases=_sample().releases)
    back = _round_trip(data, tmp_path / ('data' + suffix))
    assert not back.backlog
    assert [release.name for release in back.releases] == ['R1']


def test_releases_first(tmp_path: Path) -> None:
    """Test the releases table can be written before the backlog table."""
    path = tmp_path / 'data.csv'
    output = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    rules = FormatRules(backlog_first=False)
    write_backlog_releases(_sample(), path, output, rules,
                           stderr_file=NO_OUTPUT)
    text = path.read_text(encoding='UTF-8')
    assert text.index('Releases') < text.index('Backlog')


def test_plain_format_rt(tmp_path: Path) -> None:
    """Test writing with cell formatting off still round-trips values."""
    path = tmp_path / 'data.xlsx'
    output = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    rules = FormatRules()
    rules.turn_off_cell_format()
    write_backlog_releases(_sample(), path, output, rules,
                           stderr_file=NO_OUTPUT)
    input_config = resolve_input_config(None, data_file=path,
                                        stderr_file=NO_OUTPUT)
    back = read_backlog_releases(path, input_config, stderr_file=NO_OUTPUT)
    assert {item.key for item in back.backlog} == {'A1', 'A2'}


def test_col_map_rt(tmp_path: Path) -> None:
    """Test external column names are written and read back as fields."""
    path = tmp_path / 'data.csv'
    default_out = resolve_output_config(None, data_file=path,
                                        stderr_file=NO_OUTPUT)
    output = make_output_config(default_out.tableio,
                                {'estimated_ready_date': 'Estimated ready',
                                 'level': 'Type'}, stderr_file=NO_OUTPUT)
    write_backlog_releases(_sample(), path, output, stderr_file=NO_OUTPUT)
    text = path.read_text(encoding='UTF-8')
    assert 'Estimated ready' in text and 'Type' in text
    default_in = resolve_input_config(None, data_file=path,
                                      stderr_file=NO_OUTPUT)
    input_map = {'Estimated ready': 'estimated_ready_date', 'Type': 'level'}
    input_config = make_input_config(default_in.tableio, input_map,
                                     stderr_file=NO_OUTPUT)
    back = read_backlog_releases(path, input_config, stderr_file=NO_OUTPUT)
    first = next(item for item in back.backlog if item.key == 'A1')
    assert first.estimated_ready_date == date(2026, 6, 1)
    assert first.level == 1


def test_bad_table(tmp_path: Path) -> None:
    """Test a table without a key or name column is reported as an error."""
    path = tmp_path / 'data.csv'
    path.write_text('foo,bar\n1,2\n', encoding='UTF-8')
    input_config = resolve_input_config(None, data_file=path,
                                        stderr_file=NO_OUTPUT)
    with pytest.raises(ValueError):
        read_backlog_releases(path, input_config, stderr_file=NO_OUTPUT)
