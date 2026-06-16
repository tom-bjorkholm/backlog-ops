#! /usr/local/bin/python3
"""Tests for the backlogops_cli plan_release_dates command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from pathlib import Path
import pytest
from backlogops import (
    BacklogReleases, Release, read_backlog_releases, resolve_input_config,
    resolve_output_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import plan_release_dates

NO_OUTPUT = NoTextIO()


def _write_input(path: Path) -> None:
    """Write releases with estimated dates but no planned dates."""
    releases = [Release(name='R1', estimated_date=date(2026, 1, 10)),
                Release(name='R2')]
    data = BacklogReleases(backlog=[], releases=releases)
    config = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, config, stderr_file=NO_OUTPUT)


def _read_planned(path: Path, name: str) -> object:
    """Return the planned date of one release read back from a file."""
    config = resolve_input_config(None, data_file=path, stderr_file=NO_OUTPUT)
    data = read_backlog_releases(path, config, stderr_file=NO_OUTPUT)
    return next(rel.planned_date for rel in data.releases
                if rel.name == name)


def test_in_command_list() -> None:
    """Test the command is discovered by the list command."""
    assert 'plan_release_dates' in [n for n, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'in.csv'], ['-o', 'out.csv']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the input and output files."""
    with pytest.raises(SystemExit):
        plan_release_dates.build_parser().parse_args(args)


def test_sets_planned_dates(tmp_path: Path) -> None:
    """Test the planned date becomes the estimate plus the buffer."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.csv'
    _write_input(source)
    assert plan_release_dates.main(
        ['-i', str(source), '-o', str(target), '--buffer-days', '5']) == 0
    assert _read_planned(target, 'R1') == date(2026, 1, 15)
    assert _read_planned(target, 'R2') is None


def test_changes_file_written(tmp_path: Path) -> None:
    """Test the planned date change is saved to the changes file."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.csv'
    changes = tmp_path / 'changes.csv'
    _write_input(source)
    assert plan_release_dates.main(
        ['-i', str(source), '-o', str(target), '--buffer-days', '5',
         '--changes-file', str(changes)]) == 0
    text = changes.read_text(encoding='utf-8')
    assert 'R1' in text and '2026-01-15' in text


def test_negative_buffer(tmp_path: Path) -> None:
    """Test a negative buffer makes the command return 1."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.csv'
    _write_input(source)
    assert plan_release_dates.main(
        ['-i', str(source), '-o', str(target), '--buffer-days', '-1']) == 1


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing input file makes the command return 1."""
    assert plan_release_dates.main(
        ['-i', str(tmp_path / 'no.csv'), '-o', str(tmp_path / 'o.csv')]) == 1
