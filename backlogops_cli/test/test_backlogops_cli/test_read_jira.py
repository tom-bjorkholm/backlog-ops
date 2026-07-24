#! /usr/local/bin/python3
"""Tests for the backlogops_cli read_jira command.

The Jira reading itself is replaced by a stand-in so the command can be
tested without a Jira server: the test checks the command writes the
read data to the output file, warns but still writes inconsistent data,
requires a configuration, and is discovered by the list command.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from backlogops import (
    AvailableTeams, BacklogItem, BacklogOpsConfig, BacklogReleases, Release,
    Status, read_backlog_releases, resolve_input_config,
    write_backlog_ops_config)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import read_jira

NO_OUTPUT = NoTextIO()


def _config_file(path: Path) -> None:
    """Write a minimal backlog-ops configuration to a file."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]),
        stderr_file=NO_OUTPUT)
    write_backlog_ops_config(config, path, NO_OUTPUT)


def _data(release: str = 'R1') -> BacklogReleases:
    """Return one backlog item and the named release."""
    return BacklogReleases(
        backlog=[BacklogItem(key='A1', level=1, title='First', story_points=5,
                             status=Status.TODO, release=release)],
        releases=[Release(name='R1')])


def _patch(monkeypatch: pytest.MonkeyPatch, data: BacklogReleases) -> None:
    """Replace the Jira read with a stand-in returning fixed data."""
    def _fake(config: object, preset: str,
              **kwargs: object) -> BacklogReleases:
        """Return the fixed data, ignoring the connection details."""
        _ = (config, preset, kwargs)
        return data
    monkeypatch.setattr(read_jira, 'read_jira_from_config', _fake)


def test_in_command_list() -> None:
    """Test the read_jira command is discovered by the list command."""
    assert 'read_jira' in [name for name, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-p', 'p'], ['-o', 'out.csv']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the preset and the output file."""
    with pytest.raises(SystemExit):
        read_jira.build_parser().parse_args(args)


def test_reads_and_writes(tmp_path: Path,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the command writes the data read from Jira to the output file."""
    _patch(monkeypatch, _data())
    config_file = tmp_path / 'ops.cfg'
    target = tmp_path / 'out.csv'
    _config_file(config_file)
    assert read_jira.main(['-p', 'scrum', '-o', str(target),
                           '-c', str(config_file)]) == 0
    in_config = resolve_input_config(None, data_file=target,
                                     stderr_file=NO_OUTPUT)
    back = read_backlog_releases(target, in_config, stderr_file=NO_OUTPUT)
    assert [item.key for item in back.backlog] == ['A1']
    assert [release.name for release in back.releases] == ['R1']


def test_inconsistent_warns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                            capsys: pytest.CaptureFixture[str]) -> None:
    """Test inconsistent data is reported but the file is still written."""
    _patch(monkeypatch, _data(release='MISSING'))
    config_file = tmp_path / 'ops.cfg'
    target = tmp_path / 'out.csv'
    _config_file(config_file)
    assert read_jira.main(['-p', 'scrum', '-o', str(target),
                           '-c', str(config_file)]) == 0
    assert target.is_file()
    assert 'not fully consistent' in capsys.readouterr().err


def test_requires_config(tmp_path: Path) -> None:
    """Test the command fails when no configuration can be found."""
    assert read_jira.main(['-p', 'scrum',
                           '-o', str(tmp_path / 'out.csv')]) == 1
