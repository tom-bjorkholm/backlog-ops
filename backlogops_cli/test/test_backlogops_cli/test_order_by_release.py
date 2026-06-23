#! /usr/local/bin/python3
"""Tests for the backlogops_cli order_by_release command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from pathlib import Path
from typing import Optional
import pytest
from backlogops import (
    BacklogItem, BacklogReleases, Release, Status, read_backlog_releases,
    resolve_input_config, resolve_output_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import order_by_release

NO_OUTPUT = NoTextIO()
RELEASE_ORDER = ['R1', 'R2', 'R3']
DEFAULT_ORDER = ['B', 'C', 'A', 'D', 'E']
HONORED_ORDER = ['B', 'A', 'D', 'C', 'E']


def _item(key: str, release: Optional[str] = None,
          deps: Optional[list[str]] = None) -> BacklogItem:
    """Build a minimal backlog item with an optional release and deps."""
    return BacklogItem(key=key, level=1, title=key, story_points=1,
                       status=Status.TODO, release=release,
                       depends_on_f2s=deps or [])


def _write_source(path: Path) -> None:
    """Write a backlog and releases that show both ordering modes.

    The releases are listed R1, R2, R3. Item C is in the first release R1
    but depends on item D in the last release R3, so honoring dependencies
    must move D ahead of C while the plain release order keeps C before D.
    Item E has no release and belongs after every listed release.
    """
    backlog = [_item('A', 'R2'), _item('B', 'R1'),
               _item('C', 'R1', ['D']), _item('D', 'R3'), _item('E')]
    releases = [Release(name=name) for name in RELEASE_ORDER]
    data = BacklogReleases(backlog=backlog, releases=releases)
    config = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, config, stderr_file=NO_OUTPUT)


def _result_keys(path: Path) -> list[str]:
    """Return the ordered backlog keys read back from an output file."""
    config = resolve_input_config(None, data_file=path, stderr_file=NO_OUTPUT)
    data = read_backlog_releases(path, config, stderr_file=NO_OUTPUT)
    return [item.key for item in data.backlog]


def _release_names(path: Path) -> list[str]:
    """Return the release names read back from an output file."""
    config = resolve_input_config(None, data_file=path, stderr_file=NO_OUTPUT)
    data = read_backlog_releases(path, config, stderr_file=NO_OUTPUT)
    return [release.name for release in data.releases]


def test_in_command_list() -> None:
    """Test the order_by_release command is found by the list command."""
    assert 'order_by_release' in [name for name, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'in.csv'], ['-o', 'out.csv']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the input and output files."""
    with pytest.raises(SystemExit):
        order_by_release.build_parser().parse_args(args)


def test_default_order(tmp_path: Path) -> None:
    """Test the default run groups the backlog by the release order.

    The dependency of C on D is ignored, so C stays in its own release R1
    ahead of D, and the item without a release ends up last.
    """
    source, target = tmp_path / 'in.ods', tmp_path / 'out.ods'
    _write_source(source)
    assert order_by_release.main(['-i', str(source), '-o', str(target)]) == 0
    assert _result_keys(target) == DEFAULT_ORDER


@pytest.mark.parametrize('flag', ['-d', '--honor-deps'])
def test_honor_deps(tmp_path: Path, flag: str) -> None:
    """Test the honor-deps flag moves a prerequisite ahead of its user.

    D is delivered in the last release but C depends on it, so honoring
    dependencies places D before C even though the release order alone
    would keep C first.
    """
    source, target = tmp_path / 'in.ods', tmp_path / 'out.ods'
    _write_source(source)
    assert order_by_release.main(['-i', str(source), '-o', str(target),
                                  flag]) == 0
    assert _result_keys(target) == HONORED_ORDER


def test_releases_unchanged(tmp_path: Path) -> None:
    """Test the command writes the releases back in their original order."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.ods'
    _write_source(source)
    assert order_by_release.main(['-i', str(source), '-o', str(target)]) == 0
    assert _release_names(target) == RELEASE_ORDER


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing input file makes the command return 1."""
    assert order_by_release.main(['-i', str(tmp_path / 'no.ods'),
                                  '-o', str(tmp_path / 'out.ods')]) == 1


def test_bad_release_fails(tmp_path: Path) -> None:
    """Test an input that names a missing release returns 1.

    Reading validates the data before ordering, so a backlog item that
    references a release absent from the releases list is an error.
    """
    source, target = tmp_path / 'in.ods', tmp_path / 'out.ods'
    backlog = [_item('A', 'GONE')]
    data = BacklogReleases(backlog=backlog, releases=[Release(name='R1')])
    config = resolve_output_config(None, data_file=source,
                                   stderr_file=NO_OUTPUT)
    write_backlog_releases(data, source, config, stderr_file=NO_OUTPUT)
    assert order_by_release.main(['-i', str(source), '-o', str(target)]) == 1


def _run_once(source: Path, target: Path) -> None:
    """Write the source and create the output file once."""
    _write_source(source)
    assert order_by_release.main(['-i', str(source), '-o', str(target)]) == 0


def test_overwrite_declined(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test answering no leaves the existing output file unchanged."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.ods'
    _run_once(source, target)
    before = target.read_bytes()
    monkeypatch.setattr('sys.stdin', io.StringIO('n\n'))
    assert order_by_release.main(['-i', str(source), '-o', str(target)]) == 1
    assert target.read_bytes() == before


def test_overwrite_yes(tmp_path: Path,
                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Test answering yes overwrites the existing output file."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.ods'
    _run_once(source, target)
    monkeypatch.setattr('sys.stdin', io.StringIO('y\n'))
    assert order_by_release.main(['-i', str(source), '-o', str(target)]) == 0


def test_overwrite_force(tmp_path: Path) -> None:
    """Test the force flag overwrites without asking."""
    source, target = tmp_path / 'in.ods', tmp_path / 'out.ods'
    _run_once(source, target)
    assert order_by_release.main(['-i', str(source), '-o', str(target),
                                  '-f']) == 0
