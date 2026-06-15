#! /usr/local/bin/python3
"""Tests for the backlogops_cli order_by_keys command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from backlogops import (
    BacklogItem, BacklogReleases, Status, read_backlog_releases,
    resolve_input_config, resolve_output_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import order_by_keys

NO_OUTPUT = NoTextIO()
SPECS = [('E1', 2, None), ('E2', 2, None), ('S1', 1, 'E1'),
         ('S2', 1, 'E1'), ('S3', 1, 'E2')]


def _write_source(path: Path) -> None:
    """Write a small hierarchical backlog used as the order input."""
    backlog = [BacklogItem(key=key, level=level, title=key, story_points=1,
                           status=Status.TODO, parent_key=parent)
               for key, level, parent in SPECS]
    data = BacklogReleases(backlog=backlog, releases=[])
    config = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, config, stderr_file=NO_OUTPUT)


def test_in_command_list() -> None:
    """Test the order_by_keys command is discovered by the list command."""
    assert 'order_by_keys' in [name for name, _ in command_modules()]


@pytest.mark.parametrize('args', [
    [], ['-i', 'in.csv', '-o', 'out.csv'], ['-i', 'in.csv', '-k', 'k.txt']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires the input, key list and output files."""
    with pytest.raises(SystemExit):
        order_by_keys.build_parser().parse_args(args)


def test_reorders_backlog(tmp_path: Path) -> None:
    """Test the named keys and their children come first in the output."""
    source = tmp_path / 'in.ods'
    target = tmp_path / 'out.csv'
    key_file = tmp_path / 'keys.txt'
    _write_source(source)
    key_file.write_text('E1\nS3\n', encoding='utf-8')
    assert order_by_keys.main(['-i', str(source), '-k', str(key_file),
                               '-o', str(target)]) == 0
    config = resolve_input_config(None, data_file=target,
                                  stderr_file=NO_OUTPUT)
    back = read_backlog_releases(target, config, stderr_file=NO_OUTPUT)
    assert [item.key for item in back.backlog] == \
        ['S1', 'S2', 'E1', 'S3', 'E2']


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing input file makes the command return 1."""
    key_file = tmp_path / 'keys.txt'
    key_file.write_text('E1\n', encoding='utf-8')
    assert order_by_keys.main(['-i', str(tmp_path / 'no.csv'),
                               '-k', str(key_file),
                               '-o', str(tmp_path / 'out.csv')]) == 1
