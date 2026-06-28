#! /usr/local/bin/python3
"""Tests for the backlogops_cli adjust_release_content command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from pathlib import Path
import pytest
from backlogops import (
    BacklogItem, BacklogReleases, Release, Status, read_backlog_releases,
    resolve_input_config, resolve_output_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import adjust_release_content

NO_OUTPUT = NoTextIO()


def _write_input(path: Path) -> None:
    """Write an estimated backlog where item b no longer fits R1."""
    backlog = [
        BacklogItem(key='a', level=1, title='a', story_points=1,
                    status=Status.TODO, release='R1',
                    estimated_ready_date=date(2026, 1, 5)),
        BacklogItem(key='b', level=1, title='b', story_points=1,
                    status=Status.TODO, release='R1',
                    estimated_ready_date=date(2026, 1, 20))]
    releases = [Release(name='R1', planned_date=date(2026, 1, 15)),
                Release(name='R2', planned_date=date(2026, 2, 1))]
    data = BacklogReleases(backlog=backlog, releases=releases)
    config = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, config, stderr_file=NO_OUTPUT)


def _read_release(path: Path, key: str) -> object:
    """Return the release of one backlog item read back from a file."""
    config = resolve_input_config(None, data_file=path, stderr_file=NO_OUTPUT)
    data = read_backlog_releases(path, config, stderr_file=NO_OUTPUT)
    return next(item.release for item in data.backlog if item.key == key)


def test_in_command_list() -> None:
    """Test the command is discovered by the list command."""
    assert 'adjust_release_content' in [n for n, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'in.csv'], ['-o', 'out.csv']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the input and output files."""
    with pytest.raises(SystemExit):
        adjust_release_content.build_parser().parse_args(args)


def test_adjusts_content(tmp_path: Path) -> None:
    """Test the late item is moved to the later release in the output."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.csv'
    _write_input(source)
    assert adjust_release_content.main(
        ['-i', str(source), '-o', str(target), '--buffer-days', '0']) == 0
    assert _read_release(target, 'a') == 'R1'
    assert _read_release(target, 'b') == 'R2'


def test_changes_file_written(tmp_path: Path) -> None:
    """Test the content change is saved to the changes file."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.csv'
    changes = tmp_path / 'changes.csv'
    _write_input(source)
    assert adjust_release_content.main(
        ['-i', str(source), '-o', str(target), '--buffer-days', '0',
         '--changes-file', str(changes)]) == 0
    text = changes.read_text(encoding='utf-8')
    assert 'b' in text and 'R2' in text


def test_negative_buffer(tmp_path: Path) -> None:
    """Test a negative buffer makes the command return 1."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.csv'
    _write_input(source)
    assert adjust_release_content.main(
        ['-i', str(source), '-o', str(target), '--buffer-days', '-1']) == 1


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing input file makes the command return 1."""
    assert adjust_release_content.main(
        ['-i', str(tmp_path / 'no.csv'), '-o', str(tmp_path / 'o.csv')]) == 1


def test_missing_config(tmp_path: Path) -> None:
    """Test a -c config file that does not exist returns 1."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.csv'
    _write_input(source)
    assert adjust_release_content.main(
        ['-i', str(source), '-o', str(target),
         '-c', str(tmp_path / 'no.cfg')]) == 1
