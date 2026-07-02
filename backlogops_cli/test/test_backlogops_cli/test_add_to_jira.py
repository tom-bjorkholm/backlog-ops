#! /usr/local/bin/python3
"""Tests for the backlogops_cli add_to_jira command.

The Jira write itself is replaced by a stand-in so the command can be
tested without a Jira server: the tests check the command reads the input,
passes the chosen on-existing mode, prints the two labelled lists unless
quiet, writes the returned backlogs to the requested files, reports an
already-present key as a failure, and is discovered by the list command.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Callable
import pytest
from backlogops import (
    AddedToJira, AvailableTeams, BacklogItem, BacklogOpsConfig,
    BacklogReleases, ExistsInJiraError, FormatRules, OnExistingKey, Release,
    Status, allow_overwrite, read_backlog_releases, resolve_input_config,
    resolve_output_config, write_backlog_ops_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import add_to_jira

NO = NoTextIO()


def _config_file(path: Path) -> None:
    """Write a minimal backlog-ops configuration to a file."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]), stderr_file=NO)
    write_backlog_ops_config(config, path, NO)


def _write_input(path: Path) -> None:
    """Write an input file holding one backlog item and its release."""
    data = BacklogReleases(
        backlog=[BacklogItem(key='A', level=1, title='First', story_points=5,
                             status=Status.TODO, release='R1')],
        releases=[Release(name='R1')])
    out_config = resolve_output_config(None, data_file=path, stderr_file=NO)
    write_backlog_releases(data, path, out_config, FormatRules(),
                           file_exists_callback=allow_overwrite)


def _result() -> AddedToJira:
    """Return a canned add result with one added and one present item."""
    added = BacklogItem(key='PROJ-1', level=1, title='First', story_points=5,
                        status=Status.TODO, release='R1')
    present = BacklogItem(key='X-9', level=1, title='Old', story_points=5,
                          status=Status.TODO)
    return AddedToJira(stored=[added], already_present=[present],
                       key_map={'A': 'PROJ-1'})


def _fake_add(captured: dict[str, object],
              result: AddedToJira) -> Callable[..., AddedToJira]:
    """Return a stand-in add that records the mode and returns ``result``."""
    def add(connections: object, preset_name: str, backlog: object, *,
            on_existing_key: OnExistingKey, **kwargs: object) -> AddedToJira:
        """Record the on-existing mode and return the canned result."""
        _ = (connections, preset_name, backlog, kwargs)
        captured['mode'] = on_existing_key
        return result
    return add


def _patch(monkeypatch: pytest.MonkeyPatch,
           result: AddedToJira) -> dict[str, object]:
    """Replace the Jira write with a stand-in and return the capture."""
    captured: dict[str, object] = {}
    monkeypatch.setattr(add_to_jira, 'add_backlog_to_jira',
                        _fake_add(captured, result))
    return captured


def test_in_command_list() -> None:
    """Test the add_to_jira command is discovered by the list command."""
    assert 'add_to_jira' in [name for name, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'in.csv']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the input file and the preset."""
    with pytest.raises(SystemExit):
        add_to_jira.build_parser().parse_args(args)


def test_adds_and_prints(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                         capsys: pytest.CaptureFixture[str]) -> None:
    """Test the command adds by default in raise mode and prints the lists."""
    captured = _patch(monkeypatch, _result())
    _config_file(tmp_path / 'ops.cfg')
    _write_input(tmp_path / 'in.csv')
    code = add_to_jira.main(['-i', str(tmp_path / 'in.csv'), '-p', 'w',
                             '-c', str(tmp_path / 'ops.cfg')])
    assert code == 0
    assert captured['mode'] is OnExistingKey.RAISE
    out = capsys.readouterr().out
    assert 'Added to Jira (1):' in out
    assert 'PROJ-1  First' in out
    assert 'Already in Jira (1):' in out


def test_skip_existing(tmp_path: Path,
                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Test --skip-existing selects the skip mode."""
    captured = _patch(monkeypatch, _result())
    _config_file(tmp_path / 'ops.cfg')
    _write_input(tmp_path / 'in.csv')
    code = add_to_jira.main(['-i', str(tmp_path / 'in.csv'), '-p', 'w',
                             '-c', str(tmp_path / 'ops.cfg'),
                             '--skip-existing'])
    assert code == 0
    assert captured['mode'] is OnExistingKey.SKIP


def test_quiet_suppresses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                          capsys: pytest.CaptureFixture[str]) -> None:
    """Test -q suppresses the two lists on stdout."""
    _patch(monkeypatch, _result())
    _config_file(tmp_path / 'ops.cfg')
    _write_input(tmp_path / 'in.csv')
    add_to_jira.main(['-i', str(tmp_path / 'in.csv'), '-p', 'w',
                      '-c', str(tmp_path / 'ops.cfg'), '-q'])
    assert 'Added to Jira' not in capsys.readouterr().out


def test_writes_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the returned backlogs are written to the named files."""
    _patch(monkeypatch, _result())
    _config_file(tmp_path / 'ops.cfg')
    _write_input(tmp_path / 'in.csv')
    added = tmp_path / 'added.csv'
    existing = tmp_path / 'existing.csv'
    code = add_to_jira.main([
        '-i', str(tmp_path / 'in.csv'), '-p', 'w',
        '-c', str(tmp_path / 'ops.cfg'), '--added-file', str(added),
        '--existing-file', str(existing)])
    assert code == 0
    stored = read_backlog_releases(
        added, resolve_input_config(None, data_file=added, stderr_file=NO),
        stderr_file=NO)
    assert [item.key for item in stored.backlog] == ['PROJ-1']
    assert [release.name for release in stored.releases] == ['R1']
    assert existing.is_file()


def test_exists_returns_one(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an already-present key without --skip-existing fails."""
    def _raising(connections: object, preset_name: str, backlog: object, *,
                 on_existing_key: OnExistingKey,
                 **kwargs: object) -> AddedToJira:
        """Raise as the real function does when a key already exists."""
        _ = (connections, preset_name, backlog, on_existing_key, kwargs)
        raise ExistsInJiraError(['A'])
    monkeypatch.setattr(add_to_jira, 'add_backlog_to_jira', _raising)
    _config_file(tmp_path / 'ops.cfg')
    _write_input(tmp_path / 'in.csv')
    code = add_to_jira.main(['-i', str(tmp_path / 'in.csv'), '-p', 'w',
                             '-c', str(tmp_path / 'ops.cfg')])
    assert code == 1


def test_requires_config(tmp_path: Path) -> None:
    """Test the command fails when no configuration can be found."""
    code = add_to_jira.main(['-i', str(tmp_path / 'in.csv'), '-p', 'w'])
    assert code == 1
