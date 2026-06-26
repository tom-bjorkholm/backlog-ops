#! /usr/local/bin/python3
"""Tests for reading and writing a backlog and releases with TableIO."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
from pathlib import Path
from typing import Optional
import pytest
from backlogops import (
    BacklogItem, BacklogReleases, DEFAULT_LEVELS, FileExistsCb, FormatRules,
    LevelDisplay, Release, Status, allow_overwrite, item_to_row,
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


def _write(data: BacklogReleases, path: Path,
           callback: Optional[FileExistsCb] = None) -> None:
    """Write ``data`` to ``path``, optionally with an overwrite callback."""
    output = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, output, stderr_file=NO_OUTPUT,
                           file_exists_callback=callback)


def test_overwrite_refused(tmp_path: Path) -> None:
    """Test writing over an existing file is refused without a callback."""
    path = tmp_path / 'data.csv'
    _write(_sample(), path)
    with pytest.raises(FileExistsError):
        _write(_sample(), path)


def test_overwrite_allowed(tmp_path: Path) -> None:
    """Test the allow-overwrite callback lets the file be rewritten."""
    path = tmp_path / 'data.csv'
    _write(_sample(), path)
    _write(_sample(), path, allow_overwrite)
    assert path.is_file()


def test_overwrite_declined(tmp_path: Path) -> None:
    """Test a raising callback keeps the existing file from being written."""
    path = tmp_path / 'data.csv'
    _write(_sample(), path)

    def refuse(name: str) -> None:
        """Refuse the overwrite as a declining callback would."""
        raise FileExistsError(name)
    with pytest.raises(FileExistsError):
        _write(_sample(), path, refuse)


def _one_item(level: int = 1) -> BacklogReleases:
    """Return a one-item backlog at the given level and no releases."""
    item = BacklogItem(key='A1', level=level, title='T', story_points=3,
                       status=Status.TODO)
    return BacklogReleases(backlog=[item], releases=[])


def _write_display(data: BacklogReleases, path: Path,
                   display: LevelDisplay) -> None:
    """Write ``data`` with the given level display configuration."""
    base = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    config = make_output_config(base.tableio, {}, display)
    write_backlog_releases(data, path, config, levels=DEFAULT_LEVELS,
                           stderr_file=NO_OUTPUT)


def _csv_text(data: BacklogReleases, path: Path, display: LevelDisplay) -> str:
    """Write a CSV with the given display and return its text."""
    _write_display(data, path, display)
    return path.read_text(encoding='UTF-8')


def _read_back(path: Path) -> BacklogReleases:
    """Read a backlog file with the default input configuration."""
    config = resolve_input_config(None, data_file=path, stderr_file=NO_OUTPUT)
    return read_backlog_releases(path, config, DEFAULT_LEVELS, NO_OUTPUT)


def test_display_both(tmp_path: Path) -> None:
    """Test BOTH writes a numeric and a named level column."""
    text = _csv_text(_one_item(), tmp_path / 'b.csv', LevelDisplay.BOTH)
    assert '"level"' in text and '"level name"' in text
    assert _read_back(tmp_path / 'b.csv').backlog[0].level == 1


def test_display_numeric(tmp_path: Path) -> None:
    """Test NUMERIC writes only the numeric level column."""
    text = _csv_text(_one_item(), tmp_path / 'n.csv', LevelDisplay.NUMERIC)
    assert '"level"' in text and '"level name"' not in text
    assert _read_back(tmp_path / 'n.csv').backlog[0].level == 1


def test_display_name(tmp_path: Path) -> None:
    """Test NAME writes only the named level column and round-trips."""
    text = _csv_text(_one_item(), tmp_path / 'm.csv', LevelDisplay.NAME)
    assert '"level name"' in text and '"level"' not in text
    assert 'Story' in text
    assert _read_back(tmp_path / 'm.csv').backlog[0].level == 1


def test_unnamed_level_number(tmp_path: Path) -> None:
    """Test a level number without a name is shown as the number."""
    errors = io.StringIO()
    base = resolve_output_config(None, data_file=tmp_path / 'u.csv',
                                 stderr_file=NO_OUTPUT)
    config = make_output_config(base.tableio, {}, LevelDisplay.NAME)
    write_backlog_releases(_one_item(level=9), tmp_path / 'u.csv', config,
                           levels=DEFAULT_LEVELS, stderr_file=errors)
    text = (tmp_path / 'u.csv').read_text(encoding='UTF-8')
    assert '"9"' in text
    assert 'without a configured name' in errors.getvalue()
    assert _read_back(tmp_path / 'u.csv').backlog[0].level == 9


def _backlog_csv(tmp_path: Path, header: str, row: str) -> Path:
    """Write a one-table backlog CSV with the given header and row."""
    path = tmp_path / 'in.csv'
    path.write_text(f'# Backlog\n\n{header}\n{row}\n', encoding='UTF-8')
    return path


def test_read_name_only(tmp_path: Path) -> None:
    """Test a sole level name column is resolved to its level number."""
    path = _backlog_csv(tmp_path, 'key,level name,title,story_points,status',
                        'A1,Epic,T,3,TODO')
    assert _read_back(path).backlog[0].level == 2


def test_read_both_columns(tmp_path: Path) -> None:
    """Test the numeric column wins when both level columns are present."""
    errors = io.StringIO()
    path = _backlog_csv(tmp_path,
                        'key,level,level name,title,story_points,status',
                        'A1,2,Story,T,3,TODO')
    config = resolve_input_config(None, data_file=path, stderr_file=NO_OUTPUT)
    back = read_backlog_releases(path, config, DEFAULT_LEVELS, errors)
    assert back.backlog[0].level == 2
    assert 'level name column' in errors.getvalue()


def test_display_round_trip(tmp_path: Path) -> None:
    """Test every level display round-trips the level for every format."""
    for suffix in FORMATS:
        for display in LevelDisplay:
            path = tmp_path / f'{display.name}{suffix}'
            _write_display(_one_item(level=2), path, display)
            assert _read_back(path).backlog[0].level == 2
