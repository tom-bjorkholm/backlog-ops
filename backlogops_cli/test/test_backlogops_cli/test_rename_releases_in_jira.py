#! /usr/local/bin/python3
"""Tests for the backlogops_cli rename_releases_in_jira command.

The Jira rename itself is replaced by a stand-in so the command can be tested
without a Jira server: the tests check the command builds the renames from
--rename and from a rename file, that a name may contain spaces, that argparse
requires exactly one way, prints the result unless quiet, reports a failure
and is discovered by the list command.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Callable
import pytest
from backlogops import (
    AvailableTeams, BacklogOpsConfig, ReleaseRename, RenamedReleasesInJira,
    write_backlog_ops_config)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import rename_releases_in_jira as rename_cmd
from backlogops_cli.rename_releases_in_jira import _passphrase

NO = NoTextIO()


def _config_file(path: Path) -> None:
    """Write a minimal backlog-ops configuration to a file."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]), stderr_file=NO)
    write_backlog_ops_config(config, path, NO)


def _fake_rename(captured: dict[str, object]
                 ) -> Callable[..., RenamedReleasesInJira]:
    """Return a stand-in rename that records the preset and renames."""
    def rename(connections: object, preset_name: str,
               renames: object) -> RenamedReleasesInJira:
        """Record the preset and renames instead of talking to Jira."""
        _ = connections
        captured['preset'] = preset_name
        captured['renames'] = list(renames)  # type: ignore[call-overload]
        return RenamedReleasesInJira([ReleaseRename('R1', 'R9')], [], [], [],
                                     [])
    return rename


def _patch(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Replace the Jira rename with a stand-in and return the capture."""
    captured: dict[str, object] = {}
    monkeypatch.setattr(rename_cmd, 'rename_releases_in_jira',
                        _fake_rename(captured))
    return captured


def _args(tmp_path: Path, *extra: str) -> list[str]:
    """Return the base command line naming the preset and config."""
    return ['-p', 'w', '-c', str(tmp_path / 'ops.cfg'), *extra]


def test_passphrase(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the pass phrase prompt reads from getpass."""
    monkeypatch.setattr(rename_cmd, 'getpass', lambda _prompt: 'secret')
    assert _passphrase() == 'secret'


def test_in_command_list() -> None:
    """Test the rename command is discovered by the list command."""
    names = [name for name, _ in command_modules()]
    assert 'rename_releases_in_jira' in names


def test_requires_preset() -> None:
    """Test the command requires the preset argument."""
    with pytest.raises(SystemExit):
        rename_cmd.build_parser().parse_args(['--rename', 'R1', 'R9'])


def test_single_rename(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                       capsys: pytest.CaptureFixture[str]) -> None:
    """Test --rename builds a single rename and prints the result."""
    captured = _patch(monkeypatch)
    _config_file(tmp_path / 'ops.cfg')
    code = rename_cmd.main(_args(tmp_path, '--rename', 'R1', 'R9'))
    assert code == 0
    assert captured['renames'] == [ReleaseRename('R1', 'R9')]
    assert 'Renamed in Jira (1):' in capsys.readouterr().out


def test_single_rename_spaces(tmp_path: Path,
                              monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a --rename old and new name may contain spaces."""
    captured = _patch(monkeypatch)
    _config_file(tmp_path / 'ops.cfg')
    rename_cmd.main(_args(tmp_path, '--rename', 'Release 1', 'Big Bang 2'))
    assert captured['renames'] == [
        ReleaseRename('Release 1', 'Big Bang 2')]


def test_rename_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test --rename-file reads the old and new names from the file."""
    captured = _patch(monkeypatch)
    _config_file(tmp_path / 'ops.cfg')
    rename_file = tmp_path / 'renames.txt'
    rename_file.write_text('R1\tR9\nR2\tR8\n', encoding='utf-8')
    rename_cmd.main(_args(tmp_path, '--rename-file', str(rename_file)))
    assert captured['renames'] == [ReleaseRename('R1', 'R9'),
                                   ReleaseRename('R2', 'R8')]


def test_both_error() -> None:
    """Test giving both --rename and --rename-file is rejected by argparse."""
    with pytest.raises(SystemExit):
        rename_cmd.build_parser().parse_args(
            ['-p', 'w', '--rename', 'R1', 'R9', '--rename-file', 'r.txt'])


def test_one_value_error() -> None:
    """Test --rename with only one value is rejected by argparse."""
    with pytest.raises(SystemExit):
        rename_cmd.build_parser().parse_args(['-p', 'w', '--rename', 'R1'])


def test_neither_error() -> None:
    """Test giving neither a rename nor a file is rejected by argparse."""
    with pytest.raises(SystemExit):
        rename_cmd.build_parser().parse_args(['-p', 'w'])


def test_quiet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
               capsys: pytest.CaptureFixture[str]) -> None:
    """Test -q suppresses the result listing on stdout."""
    _patch(monkeypatch)
    _config_file(tmp_path / 'ops.cfg')
    rename_cmd.main(_args(tmp_path, '--rename', 'R1', 'R9', '-q'))
    assert 'Renamed in Jira' not in capsys.readouterr().out


def test_error_returns_1(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a rename failure is reported and the command returns 1."""
    def _raise(*_args: object, **_kwargs: object) -> RenamedReleasesInJira:
        """Raise as the rename does when Jira cannot be reached."""
        raise ValueError('boom')
    monkeypatch.setattr(rename_cmd, 'rename_releases_in_jira', _raise)
    _config_file(tmp_path / 'ops.cfg')
    assert rename_cmd.main(_args(tmp_path, '--rename', 'R1', 'R9')) == 1
