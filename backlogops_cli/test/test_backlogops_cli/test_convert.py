#! /usr/local/bin/python3
"""Tests for the backlogops_cli convert command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from backlogops import (
    AvailableTeams, AvailableTeamsConfig, BacklogItem, BacklogReleases,
    Release, Status, make_output_config, read_backlog_releases,
    resolve_input_config, resolve_output_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import convert

NO_OUTPUT = NoTextIO()


def _write_source(path: Path) -> None:
    """Write a small backlog and releases file used as convert input."""
    data = BacklogReleases(
        backlog=[BacklogItem(key='A1', level=1, title='First', story_points=5,
                             status=Status.TODO, release='R1')],
        releases=[Release(name='R1')])
    config = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, config, stderr_file=NO_OUTPUT)


def test_in_command_list() -> None:
    """Test the convert command is discovered by the list command."""
    assert 'convert' in [name for name, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'in.csv'], ['-o', 'out.csv']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the input and the output file."""
    with pytest.raises(SystemExit):
        convert.build_parser().parse_args(args)


def test_convert_round_trip(tmp_path: Path) -> None:
    """Test convert reads one format and writes another with same data."""
    source = tmp_path / 'in.ods'
    target = tmp_path / 'out.csv'
    _write_source(source)
    assert convert.main(['-i', str(source), '-o', str(target)]) == 0
    config = resolve_input_config(None, data_file=target,
                                  stderr_file=NO_OUTPUT)
    back = read_backlog_releases(target, config, stderr_file=NO_OUTPUT)
    assert [item.key for item in back.backlog] == ['A1']
    assert [release.name for release in back.releases] == ['R1']


def test_output_preset(tmp_path: Path) -> None:
    """Test an output preset from the teams file renames written columns."""
    teams_file = tmp_path / 'teams.cfg'
    teams = AvailableTeamsConfig(neutral=AvailableTeams(persons={}, teams=[]),
                                 stderr_file=NO_OUTPUT)
    preset = make_output_config(
        resolve_output_config(None, data_file='x.csv',
                              stderr_file=NO_OUTPUT).tableio,
        {'level': 'Type'}, stderr_file=NO_OUTPUT)
    teams.output_configs = {'rep': preset}
    teams.write(to_json_filename=teams_file, stderr_file=NO_OUTPUT)
    source = tmp_path / 'in.ods'
    target = tmp_path / 'out.csv'
    _write_source(source)
    assert convert.main(['-i', str(source), '-o', str(target),
                         '-O', 'rep', '--io-config', str(teams_file)]) == 0
    assert 'Type' in target.read_text(encoding='UTF-8')


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing input file makes the command return 1."""
    assert convert.main(['-i', str(tmp_path / 'no.csv'),
                         '-o', str(tmp_path / 'out.csv')]) == 1
