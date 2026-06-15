#! /usr/local/bin/python3
"""Tests for the backlogops_cli order_by_deps command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from backlogops import (
    BacklogItem, BacklogReleases, Status, read_backlog_releases,
    resolve_input_config, resolve_output_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import order_by_deps

NO_OUTPUT = NoTextIO()
SPECS = [('C', ['P']), ('X', []), ('P', [])]


def _write_source(path: Path) -> None:
    """Write a small backlog where C depends on P, with X independent."""
    backlog = [BacklogItem(key=key, level=1, title=key, story_points=1,
                           status=Status.TODO, depends_on_f2s=list(deps))
               for key, deps in SPECS]
    data = BacklogReleases(backlog=backlog, releases=[])
    config = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, config, stderr_file=NO_OUTPUT)


def _result_keys(path: Path) -> list[str]:
    """Return the ordered keys read back from an output file."""
    config = resolve_input_config(None, data_file=path, stderr_file=NO_OUTPUT)
    data = read_backlog_releases(path, config, stderr_file=NO_OUTPUT)
    return [item.key for item in data.backlog]


def test_in_command_list() -> None:
    """Test the order_by_deps command is discovered by the list command."""
    assert 'order_by_deps' in [name for name, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'in.csv'], ['-o', 'out.csv']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the input and output files."""
    with pytest.raises(SystemExit):
        order_by_deps.build_parser().parse_args(args)


def test_rejects_unknown_mode() -> None:
    """Test an unknown mode value is rejected by the parser."""
    with pytest.raises(SystemExit):
        order_by_deps.build_parser().parse_args(
            ['-i', 'in.csv', '-o', 'out.csv', '-m', 'NOPE'])


def test_default_pulls(tmp_path: Path) -> None:
    """Test the default run pulls the prerequisite ahead of its user."""
    source = tmp_path / 'in.ods'
    target = tmp_path / 'out.csv'
    _write_source(source)
    assert order_by_deps.main(['-i', str(source), '-o', str(target)]) == 0
    assert _result_keys(target) == ['P', 'C', 'X']


def test_later_pushes(tmp_path: Path) -> None:
    """Test the later flag pushes the dependent item back."""
    source = tmp_path / 'in.ods'
    target = tmp_path / 'out.csv'
    _write_source(source)
    assert order_by_deps.main(['-i', str(source), '-o', str(target),
                               '-L']) == 0
    assert _result_keys(target) == ['X', 'P', 'C']


def test_space_ok(tmp_path: Path) -> None:
    """Test the space-around flag is accepted and produces output."""
    source = tmp_path / 'in.ods'
    target = tmp_path / 'out.csv'
    _write_source(source)
    assert order_by_deps.main(['-i', str(source), '-o', str(target),
                               '-s', 'C']) == 0


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing input file makes the command return 1."""
    assert order_by_deps.main(['-i', str(tmp_path / 'no.csv'),
                               '-o', str(tmp_path / 'out.csv')]) == 1
