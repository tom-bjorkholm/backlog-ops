#! /usr/local/bin/python3
"""Tests for the backlogops_cli demo_backlog command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from backlogops import (
    AvailableTeams, BacklogOpsConfig, make_output_config,
    read_backlog_releases, resolve_input_config, resolve_output_config)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import demo_backlog

NO_OUTPUT = NoTextIO()


def test_in_command_list() -> None:
    """Test the demo_backlog command is discovered by the list command."""
    assert 'demo_backlog' in [name for name, _ in command_modules()]


def test_requires_output() -> None:
    """Test the command requires the output file argument."""
    with pytest.raises(SystemExit):
        demo_backlog.build_parser().parse_args([])


def test_writes_demo(tmp_path: Path) -> None:
    """Test the command writes a readable demo backlog and releases."""
    target = tmp_path / 'demo.ods'
    assert demo_backlog.main(['-o', str(target)]) == 0
    config = resolve_input_config(None, data_file=target,
                                  stderr_file=NO_OUTPUT)
    back = read_backlog_releases(target, config, stderr_file=NO_OUTPUT)
    assert len(back.backlog) == 25
    assert len(back.releases) == 2


def test_output_preset(tmp_path: Path) -> None:
    """Test an output preset from the -c config renames written columns."""
    teams_file = tmp_path / 'teams.cfg'
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]),
        stderr_file=NO_OUTPUT)
    preset = make_output_config(
        resolve_output_config(None, data_file='x.csv',
                              stderr_file=NO_OUTPUT).tableio,
        {'level': 'Type'}, {}, stderr_file=NO_OUTPUT)
    config.output_configs = {'rep': preset}
    config.write(to_json_filename=teams_file, stderr_file=NO_OUTPUT)
    target = tmp_path / 'demo.csv'
    assert demo_backlog.main(['-o', str(target), '-O', 'rep',
                              '-c', str(teams_file)]) == 0
    assert 'Type' in target.read_text(encoding='UTF-8')


def test_missing_config(tmp_path: Path) -> None:
    """Test a -c config file that does not exist returns 1."""
    assert demo_backlog.main(['-o', str(tmp_path / 'demo.csv'),
                              '-c', str(tmp_path / 'no.cfg')]) == 1
