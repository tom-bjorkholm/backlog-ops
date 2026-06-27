#! /usr/local/bin/python3
"""Tests for the backlogops_cli estimate_ready_date command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from pathlib import Path
import pytest
from backlogops import (
    AvailableTeams, BacklogItem, BacklogOpsConfig, BacklogReleases,
    Membership, Person, Release, Status, Team, read_backlog_releases,
    resolve_input_config, resolve_output_config, write_available_teams,
    write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import estimate_ready_date

NO_OUTPUT = NoTextIO()


def _write_teams(path: Path) -> None:
    """Write a teams config with one full-time member at one point a day."""
    ann = Person(name='Ann')
    one = Team(name='T', velocity=10.0, sum_fte_at_velocity=1.0,
               sprint_length=10, members=[Membership(person_name='Ann')])
    teams = AvailableTeams(persons={'ann': ann}, teams=[one])
    write_available_teams(teams, path, NO_OUTPUT)


def _write_backlog(path: Path) -> None:
    """Write a small backlog with one three-point item to estimate."""
    backlog = [BacklogItem(key='a', level=1, title='a', story_points=3,
                           status=Status.TODO)]
    data = BacklogReleases(backlog=backlog, releases=[])
    config = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, config, stderr_file=NO_OUTPUT)


def _read_item(path: Path) -> BacklogItem:
    """Return the single backlog item read back from an output file."""
    config = resolve_input_config(None, data_file=path, stderr_file=NO_OUTPUT)
    data = read_backlog_releases(path, config, stderr_file=NO_OUTPUT)
    return data.backlog[0]


def _sources(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Write the input backlog and teams config, return the three paths."""
    source = tmp_path / 'in.ods'
    target = tmp_path / 'out.csv'
    config = tmp_path / 'teams.cfg'
    _write_backlog(source)
    _write_teams(config)
    return source, target, config


def test_in_command_list() -> None:
    """Test the command is discovered by the list command."""
    assert 'estimate_ready_date' in [n for n, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'in.csv'], ['-o', 'out.csv']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the input and output files."""
    with pytest.raises(SystemExit):
        estimate_ready_date.build_parser().parse_args(args)


def test_estimates(tmp_path: Path) -> None:
    """Test the command writes the estimated ready date to the output."""
    source, target, config = _sources(tmp_path)
    assert estimate_ready_date.main(
        ['-i', str(source), '-o', str(target), '-c', str(config),
         '-d', '2026-06-15']) == 0
    assert _read_item(target).estimated_ready_date == date(2026, 6, 17)


def test_default_date(tmp_path: Path) -> None:
    """Test the command runs without a start date, using today."""
    source, target, config = _sources(tmp_path)
    assert estimate_ready_date.main(
        ['-i', str(source), '-o', str(target), '-c', str(config)]) == 0


def test_set_plan(tmp_path: Path) -> None:
    """Test the set-plan flag copies the estimate to the planned date."""
    source, target, config = _sources(tmp_path)
    assert estimate_ready_date.main(
        ['-i', str(source), '-o', str(target), '-c', str(config),
         '-d', '2026-06-15', '--set-plan']) == 0
    assert _read_item(target).planned_ready_date == date(2026, 6, 17)


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing input file makes the command return 1."""
    assert estimate_ready_date.main(
        ['-i', str(tmp_path / 'no.csv'), '-o', str(tmp_path / 'out.csv')]) == 1


def test_missing_config(tmp_path: Path) -> None:
    """Test a missing teams config file makes the command return 1."""
    source = tmp_path / 'in.ods'
    _write_backlog(source)
    assert estimate_ready_date.main(
        ['-i', str(source), '-o', str(tmp_path / 'out.csv'),
         '-c', str(tmp_path / 'missing.cfg')]) == 1


def test_load_teams_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a RuntimeError while loading teams becomes a ValueError."""
    def boom(config: object, *args: object) -> BacklogOpsConfig:
        raise RuntimeError('no teams configured')
    monkeypatch.setattr(estimate_ready_date, 'get_backlog_ops_config', boom)
    with pytest.raises(ValueError, match='no teams configured'):
        # pylint: disable-next=protected-access
        estimate_ready_date._load_teams(None)


def _write_backlog_release(path: Path) -> None:
    """Write a backlog whose single item belongs to a release R1."""
    backlog = [BacklogItem(key='a', level=1, title='a', story_points=3,
                           status=Status.TODO, release='R1')]
    data = BacklogReleases(backlog=backlog, releases=[Release(name='R1')])
    config = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, config, stderr_file=NO_OUTPUT)


def test_changes_file_written(tmp_path: Path) -> None:
    """Test the estimated release date change is saved to a file."""
    source, target, config = tmp_path / 'in.ods', tmp_path / 'out.csv', \
        tmp_path / 'teams.cfg'
    changes = tmp_path / 'changes.csv'
    _write_backlog_release(source)
    _write_teams(config)
    assert estimate_ready_date.main(
        ['-i', str(source), '-o', str(target), '-c', str(config),
         '-d', '2026-06-15', '--changes-file', str(changes)]) == 0
    text = changes.read_text(encoding='utf-8')
    assert 'R1' in text and '2026-06-17' in text


def test_changes_empty(tmp_path: Path) -> None:
    """Test no changes file is created when there are no changes."""
    source, target, config = _sources(tmp_path)
    changes = tmp_path / 'changes.csv'
    assert estimate_ready_date.main(
        ['-i', str(source), '-o', str(target), '-c', str(config),
         '-d', '2026-06-15', '--changes-file', str(changes)]) == 0
    assert not changes.exists()
