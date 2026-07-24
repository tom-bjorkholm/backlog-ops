#! /usr/local/bin/python3
"""Shared helpers for the backlogops_cli command tests.

These build the small configuration and data files the command tests read
and write, and read a written file back, so the individual test modules do
not repeat that scaffolding. They deliberately use ``NoTextIO()`` inline
rather than a shared sink alias.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from collections.abc import Callable, Sequence
from pathlib import Path
from backlogops import (
    AvailableTeams, BacklogItem, BacklogOpsConfig, BacklogReleases,
    FormatRules, Release, Status, allow_overwrite, make_output_config,
    read_backlog_releases, resolve_input_config, resolve_output_config,
    write_backlog_ops_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO


def write_min_config(path: Path) -> None:
    """Write a minimal backlog-ops configuration to a file."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]),
        stderr_file=NoTextIO())
    write_backlog_ops_config(config, path, NoTextIO())


def write_item_input(path: Path,
                     release_names: Sequence[str] = ('R1',)) -> None:
    """Write an input file with one item in R1 and the named releases."""
    data = BacklogReleases(
        backlog=[BacklogItem(key='A', level=1, title='First', story_points=5,
                             status=Status.TODO, release='R1')],
        releases=[Release(name=name) for name in release_names])
    out_config = resolve_output_config(None, data_file=path,
                                       stderr_file=NoTextIO())
    write_backlog_releases(data, path, out_config, FormatRules(),
                           file_exists_callback=allow_overwrite)


def prepare_input(tmp_path: Path) -> None:
    """Write a minimal ``ops.cfg`` and a one-item ``in.csv`` for a test."""
    write_min_config(tmp_path / 'ops.cfg')
    write_item_input(tmp_path / 'in.csv')


def base_args(tmp_path: Path, *extra: str) -> list[str]:
    """Return the base ``-i``/``-p``/``-c`` command line plus extra flags."""
    return ['-i', str(tmp_path / 'in.csv'), '-p', 'w', '-c',
            str(tmp_path / 'ops.cfg'), *extra]


def raising_call(error: Exception) -> Callable[..., object]:
    """Return a stand-in Jira call that always raises ``error``."""
    def call(*args: object, **kwargs: object) -> object:
        """Raise the given error instead of talking to Jira."""
        _ = (args, kwargs)
        raise error
    return call


def write_data_file(path: Path, backlog: list[BacklogItem],
                    releases: list[Release]) -> None:
    """Write a backlog and releases to a test output file."""
    data = BacklogReleases(backlog=backlog, releases=releases)
    config = resolve_output_config(None, data_file=path,
                                   stderr_file=NoTextIO())
    write_backlog_releases(data, path, config, stderr_file=NoTextIO())


def read_data_file(path: Path) -> BacklogReleases:
    """Read back the backlog and releases from a test output file."""
    config = resolve_input_config(None, data_file=path, stderr_file=NoTextIO())
    return read_backlog_releases(path, config, stderr_file=NoTextIO())


def write_preset_config(path: Path, name: str = 'rep') -> None:
    """Write a config with one output preset renaming level to Type."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]),
        stderr_file=NoTextIO())
    tableio = resolve_output_config(None, data_file='x.csv',
                                    stderr_file=NoTextIO()).tableio
    preset = make_output_config(tableio, {'level': 'Type'}, {},
                                stderr_file=NoTextIO())
    config.output_configs = {name: preset}
    config.write(to_json_filename=path, stderr_file=NoTextIO())
