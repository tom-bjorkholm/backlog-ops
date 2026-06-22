#! /usr/local/bin/python3
"""Tests for the backlogops_cli order_releases command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
from pathlib import Path
import pytest
from backlogops import (
    BacklogItem, BacklogReleases, Release, Status, read_backlog_releases,
    resolve_input_config, resolve_output_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import order_releases

NO_OUTPUT = NoTextIO()


def _write_source(path: Path) -> None:
    """Write a backlog with three dated releases out of planned order."""
    backlog = [BacklogItem(key='BI-1', level=1, title='T', story_points=1,
                           status=Status.TODO, release='RB')]
    releases = [Release(name='RB', planned_date=date(2026, 3, 1),
                        estimated_date=date(2026, 1, 1)),
                Release(name='RA', planned_date=date(2026, 1, 1),
                        estimated_date=date(2026, 3, 1)),
                Release(name='RN', estimated_date=date(2026, 2, 1))]
    data = BacklogReleases(backlog=backlog, releases=releases)
    config = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, config, stderr_file=NO_OUTPUT)


def _release_names(path: Path) -> list[str]:
    """Return the ordered release names read back from an output file."""
    config = resolve_input_config(None, data_file=path, stderr_file=NO_OUTPUT)
    data = read_backlog_releases(path, config, stderr_file=NO_OUTPUT)
    return [release.name for release in data.releases]


def test_in_command_list() -> None:
    """Test the order_releases command is discovered by the list command."""
    assert 'order_releases' in [name for name, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'in.csv'], ['-o', 'out.csv']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the input and output files."""
    with pytest.raises(SystemExit):
        order_releases.build_parser().parse_args(args)


def test_default_planned(tmp_path: Path) -> None:
    """Test the default run orders the releases by their planned date."""
    source = tmp_path / 'in.ods'
    target = tmp_path / 'out.ods'
    _write_source(source)
    assert order_releases.main(['-i', str(source), '-o', str(target)]) == 0
    assert _release_names(target) == ['RA', 'RB', 'RN']


def test_by_estimated(tmp_path: Path) -> None:
    """Test the by-estimated flag orders by the estimated date."""
    source = tmp_path / 'in.ods'
    target = tmp_path / 'out.ods'
    _write_source(source)
    assert order_releases.main(['-i', str(source), '-o', str(target),
                                '-e']) == 0
    assert _release_names(target) == ['RB', 'RN', 'RA']


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing input file makes the command return 1."""
    assert order_releases.main(['-i', str(tmp_path / 'no.ods'),
                                '-o', str(tmp_path / 'out.ods')]) == 1


def _run_once(source: Path, target: Path) -> None:
    """Write the source and create the output file once."""
    _write_source(source)
    assert order_releases.main(['-i', str(source), '-o', str(target)]) == 0


def test_overwrite_declined(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test answering no leaves the existing output file unchanged."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.ods'
    _run_once(source, target)
    before = target.read_bytes()
    monkeypatch.setattr('sys.stdin', io.StringIO('n\n'))
    assert order_releases.main(['-i', str(source), '-o', str(target)]) == 1
    assert target.read_bytes() == before


def test_overwrite_yes(tmp_path: Path,
                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Test answering yes overwrites the existing output file."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.ods'
    _run_once(source, target)
    monkeypatch.setattr('sys.stdin', io.StringIO('y\n'))
    assert order_releases.main(['-i', str(source), '-o', str(target)]) == 0


def test_overwrite_force(tmp_path: Path) -> None:
    """Test the force flag overwrites without asking."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.ods'
    _run_once(source, target)
    assert order_releases.main(['-i', str(source), '-o', str(target),
                                '-f']) == 0
