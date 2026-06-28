#! /usr/local/bin/python3
"""Tests for the backlogops_cli convert command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from backlogops import (
    AvailableTeams, BacklogItem, BacklogOpsConfig, BacklogReleases,
    Release, Status, make_input_config, make_output_config,
    read_backlog_releases, resolve_input_config, resolve_output_config,
    write_backlog_releases)
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
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]),
        stderr_file=NO_OUTPUT)
    preset = make_output_config(
        resolve_output_config(None, data_file='x.csv',
                              stderr_file=NO_OUTPUT).tableio,
        {'level': 'Type'}, {}, stderr_file=NO_OUTPUT)
    config.output_configs = {'rep': preset}
    config.write(to_json_filename=teams_file, stderr_file=NO_OUTPUT)
    source = tmp_path / 'in.ods'
    target = tmp_path / 'out.csv'
    _write_source(source)
    assert convert.main(['-i', str(source), '-o', str(target),
                         '-O', 'rep', '-c', str(teams_file)]) == 0
    assert 'Type' in target.read_text(encoding='UTF-8')


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing input file makes the command return 1."""
    assert convert.main(['-i', str(tmp_path / 'no.csv'),
                         '-o', str(tmp_path / 'out.csv')]) == 1


def _empty_config() -> BacklogOpsConfig:
    """Return a configuration for an empty workforce and no presets."""
    return BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]),
        stderr_file=NO_OUTPUT)


def _write_status_source(path: Path, status: str) -> None:
    """Write a one-row backlog CSV using the given status text."""
    path.write_text('key,level,title,story_points,status\n'
                    f'A1,1,First,5,{status}\n', encoding='utf-8')


def _converted_status(target: Path) -> Status:
    """Return the status of the one item read back from a written file."""
    config = resolve_input_config(None, data_file=target,
                                  stderr_file=NO_OUTPUT)
    back = read_backlog_releases(target, config, stderr_file=NO_OUTPUT)
    return back.backlog[0].status


def test_global_status_map(tmp_path: Path) -> None:
    """Test the -c global status map resolves an extra name."""
    teams_file = tmp_path / 'teams.cfg'
    config = _empty_config()
    config.status_input_map = {'Implementing': Status.IN_PROGRESS}
    config.write(to_json_filename=teams_file, stderr_file=NO_OUTPUT)
    source = tmp_path / 'in.csv'
    target = tmp_path / 'out.csv'
    _write_status_source(source, 'Implementing')
    assert convert.main(['-i', str(source), '-o', str(target),
                         '-c', str(teams_file)]) == 0
    assert _converted_status(target) is Status.IN_PROGRESS


def test_preset_status_wins(tmp_path: Path) -> None:
    """Test an input preset's status map overrides the global one."""
    teams_file = tmp_path / 'teams.cfg'
    config = _empty_config()
    config.status_input_map = {'Reviewing': Status.IN_PROGRESS}
    preset = make_input_config(
        resolve_input_config(None, data_file='x.csv',
                             stderr_file=NO_OUTPUT).tableio,
        {}, {}, {'Reviewing': Status.DONE}, stderr_file=NO_OUTPUT)
    config.input_configs = {'jira': preset}
    config.write(to_json_filename=teams_file, stderr_file=NO_OUTPUT)
    source = tmp_path / 'in.csv'
    target = tmp_path / 'out.csv'
    _write_status_source(source, 'Reviewing')
    assert convert.main(['-i', str(source), '-o', str(target), '-I', 'jira',
                         '-c', str(teams_file)]) == 0
    assert _converted_status(target) is Status.DONE


def test_config_discovered(tmp_path: Path,
                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an output preset is found via $BACKLOGOPS_CFG without -c."""
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
    monkeypatch.setenv('BACKLOGOPS_CFG', str(teams_file))
    source, target = tmp_path / 'in.ods', tmp_path / 'out.csv'
    _write_source(source)
    assert convert.main(['-i', str(source), '-o', str(target),
                         '-O', 'rep']) == 0
    assert 'Type' in target.read_text(encoding='UTF-8')


def test_missing_config(tmp_path: Path) -> None:
    """Test a -c file that does not exist makes the command return 1."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.csv'
    _write_source(source)
    assert convert.main(['-i', str(source), '-o', str(target),
                         '-c', str(tmp_path / 'no.cfg')]) == 1


def test_no_config_note(tmp_path: Path,
                        capsys: pytest.CaptureFixture[str]) -> None:
    """Test a note is printed when no configuration is found."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.csv'
    _write_source(source)
    assert convert.main(['-i', str(source), '-o', str(target)]) == 0
    assert 'using built-in defaults' in capsys.readouterr().err
