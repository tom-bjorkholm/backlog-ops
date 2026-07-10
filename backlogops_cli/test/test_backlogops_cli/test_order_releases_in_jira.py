#! /usr/local/bin/python3
"""Tests for the backlogops_cli order_releases_in_jira command.

The Jira ordering itself is replaced by stand-ins so the command can be tested
without a Jira server: the tests check the by-date, name-list and input order
sources, that a name may contain spaces, that argparse requires exactly one
source, that the result is printed unless quiet, and that the command is
discovered by the list command.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Callable
import pytest
from backlogops import (
    AvailableTeams, BacklogOpsConfig, BacklogReleases, OrderedReleasesInJira,
    Release, write_backlog_ops_config)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import order_releases_in_jira as order_cmd

NO = NoTextIO()


def _config_file(path: Path) -> None:
    """Write a minimal backlog-ops configuration to a file."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]), stderr_file=NO)
    write_backlog_ops_config(config, path, NO)


def _fake_names(captured: dict[str, object]
                ) -> Callable[..., OrderedReleasesInJira]:
    """Return a stand-in name-list order that records its names."""
    def order(connections: object, preset_name: str,
              names: list[str]) -> OrderedReleasesInJira:
        """Record the by-name order instead of talking to Jira."""
        _ = connections
        ordered = list(names)
        captured['func'] = 'names'
        captured['preset'] = preset_name
        captured['names'] = ordered
        return OrderedReleasesInJira(ordered, [])
    return order


def _fake_date(captured: dict[str, object]
               ) -> Callable[..., OrderedReleasesInJira]:
    """Return a stand-in by-date order that records it was called."""
    def order(connections: object, preset_name: str) -> OrderedReleasesInJira:
        """Record the by-date order instead of talking to Jira."""
        _ = connections
        captured['func'] = 'date'
        captured['preset'] = preset_name
        return OrderedReleasesInJira(['R1'], [])
    return order


def _patch(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Replace both Jira order functions and return the capture."""
    captured: dict[str, object] = {}
    monkeypatch.setattr(order_cmd, 'order_releases_in_jira',
                        _fake_names(captured))
    monkeypatch.setattr(order_cmd, 'order_jira_rel_by_date',
                        _fake_date(captured))
    return captured


def _args(tmp_path: Path, *extra: str) -> list[str]:
    """Return the base command line naming the preset and config."""
    return ['-p', 'w', '-c', str(tmp_path / 'ops.cfg'), *extra]


def test_in_command_list() -> None:
    """Test the order command is discovered by the list command."""
    names = [name for name, _ in command_modules()]
    assert 'order_releases_in_jira' in names


def test_requires_preset() -> None:
    """Test the command requires the preset argument."""
    with pytest.raises(SystemExit):
        order_cmd.build_parser().parse_args(['--by-date'])


def test_by_date(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                 capsys: pytest.CaptureFixture[str]) -> None:
    """Test --by-date orders by date and prints the result."""
    captured = _patch(monkeypatch)
    _config_file(tmp_path / 'ops.cfg')
    code = order_cmd.main(_args(tmp_path, '--by-date'))
    assert code == 0 and captured['func'] == 'date'
    assert 'Ordered in Jira (1):' in capsys.readouterr().out


def test_name_list(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test --name-list reads the wanted order from the named file."""
    captured = _patch(monkeypatch)
    _config_file(tmp_path / 'ops.cfg')
    name_file = tmp_path / 'names.txt'
    name_file.write_text('R1\nR2\n', encoding='utf-8')
    order_cmd.main(_args(tmp_path, '--name-list', str(name_file)))
    assert captured['func'] == 'names'
    assert captured['names'] == ['R1', 'R2']


def test_name_list_spaces(tmp_path: Path,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a --name-list release name may contain spaces."""
    captured = _patch(monkeypatch)
    _config_file(tmp_path / 'ops.cfg')
    name_file = tmp_path / 'names.txt'
    name_file.write_text('Release 1.0\nBig Bang 2.0\n', encoding='utf-8')
    order_cmd.main(_args(tmp_path, '--name-list', str(name_file)))
    assert captured['names'] == ['Release 1.0', 'Big Bang 2.0']


def test_from_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test -i/--input uses the input file's release order."""
    captured = _patch(monkeypatch)
    _config_file(tmp_path / 'ops.cfg')

    def _fake_input(*_args: object, **_kwargs: object) -> BacklogReleases:
        """Return releases as if read from the input file."""
        return BacklogReleases(backlog=[],
                               releases=[Release('R1'), Release('R2')])
    monkeypatch.setattr(order_cmd, 'read_input', _fake_input)
    order_cmd.main(_args(tmp_path, '-i', str(tmp_path / 'in.dat')))
    assert captured['names'] == ['R1', 'R2']


def test_no_source() -> None:
    """Test giving no order source is rejected by argparse."""
    with pytest.raises(SystemExit):
        order_cmd.build_parser().parse_args(['-p', 'w'])


def test_two_sources() -> None:
    """Test giving two order sources is rejected by argparse."""
    with pytest.raises(SystemExit):
        order_cmd.build_parser().parse_args(
            ['-p', 'w', '--by-date', '-i', 'in.dat'])


def test_name_list_and_input() -> None:
    """Test --name-list and -i/--input are mutually exclusive."""
    with pytest.raises(SystemExit):
        order_cmd.build_parser().parse_args(
            ['-p', 'w', '--name-list', 'n.txt', '-i', 'in.dat'])


def test_quiet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
               capsys: pytest.CaptureFixture[str]) -> None:
    """Test -q suppresses the result listing on stdout."""
    _patch(monkeypatch)
    _config_file(tmp_path / 'ops.cfg')
    order_cmd.main(_args(tmp_path, '--by-date', '-q'))
    assert 'Ordered in Jira' not in capsys.readouterr().out
