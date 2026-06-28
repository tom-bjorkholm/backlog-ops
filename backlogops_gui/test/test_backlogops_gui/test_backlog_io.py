#! /usr/local/bin/python3
"""Tests for reading and writing a backlog with format options."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from pathlib import Path
from backlogops import (
    BacklogItem, BacklogReleases, Release, Status, make_input_config,
    resolve_input_config)
from backlogops.no_text_io import NoTextIO
from backlogops_gui.backlog_io import read_backlog, write_backlog
from backlogops_gui._migrate_warn import (
    GuiMigrateWarnHook, GuiPresetMigrateWarnHook)


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


def _status_csv(path: Path, status: str) -> None:
    """Write a one-row backlog CSV using the given status text."""
    path.write_text('key,level,title,story_points,status\n'
                    f'A1,1,First,5,{status}\n', encoding='utf-8')


def test_global_status_map(tmp_path: Path) -> None:
    """Test read_backlog applies the global status map to an extra name."""
    path = tmp_path / 'in.csv'
    _status_csv(path, 'Implementing')
    data = read_backlog(str(path), None, None,
                        status_map={'implementing': Status.IN_PROGRESS})
    assert data.backlog[0].status is Status.IN_PROGRESS


def test_preset_status_wins(tmp_path: Path) -> None:
    """Test a named input preset's status map overrides the global one."""
    path = tmp_path / 'in.csv'
    _status_csv(path, 'Reviewing')
    preset = make_input_config(
        resolve_input_config(None, data_file='x.csv',
                             stderr_file=NoTextIO()).tableio,
        {}, {}, {'Reviewing': Status.DONE}, stderr_file=NoTextIO())
    data = read_backlog(str(path), 'jira', {'jira': preset},
                        status_map={'Reviewing': Status.IN_PROGRESS})
    assert data.backlog[0].status is Status.DONE


def test_old_input_warns(tmp_path: Path) -> None:
    """Test reading via an old input config file warns into the sink."""
    config_file = tmp_path / 'in.cfg'
    config_file.write_text('{"tableio": {"format_name": "CSV"}}',
                           encoding='UTF-8')
    data_file = tmp_path / 'in.csv'
    _status_csv(data_file, 'TODO')
    sink = io.StringIO()
    read_backlog(str(data_file), str(config_file), None, sink)
    assert 'Migrate IO preset file' in sink.getvalue()


def test_old_output_warns(tmp_path: Path) -> None:
    """Test writing via an old output config file warns into the sink."""
    config_file = tmp_path / 'out.cfg'
    config_file.write_text('{"tableio": {"format_name": "CSV"}}',
                           encoding='UTF-8')
    sink = io.StringIO()
    write_backlog(_data(), str(tmp_path / 'res.csv'), str(config_file), None,
                  False, sink)
    assert 'Migrate IO preset file' in sink.getvalue()


def test_warn_hook_text() -> None:
    """Test the config warning hook points at the write-config action."""
    message = GuiMigrateWarnHook.migrate_warn_msg()
    assert 'Backward compatibility' in message
    assert 'Write configuration' in message


def test_preset_warn_text() -> None:
    """Test the preset warning hook points at the migrate-preset action."""
    message = GuiPresetMigrateWarnHook.migrate_warn_msg()
    assert 'Backward compatibility' in message
    assert 'Migrate IO preset file' in message
