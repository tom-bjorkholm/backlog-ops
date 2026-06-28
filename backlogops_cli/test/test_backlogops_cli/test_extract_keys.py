#! /usr/local/bin/python3
"""Tests for the backlogops_cli extract_keys command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from pathlib import Path
import pytest
from backlogops import (
    BacklogItem, BacklogReleases, Status, read_key_list,
    resolve_output_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import extract_keys

NO_OUTPUT = NoTextIO()


def _backlog() -> list[BacklogItem]:
    """Return two epics and three stories, in mixed level order."""
    levels = {'E1': 2, 'S1': 1, 'S2': 1, 'E2': 2, 'S3': 1}
    return [BacklogItem(key=key, level=level, title=key, story_points=2,
                        status=Status.TODO)
            for key, level in levels.items()]


def _write_source(path: Path) -> None:
    """Write the sample backlog to a file used as extract input."""
    data = BacklogReleases(backlog=_backlog(), releases=[])
    config = resolve_output_config(None, data_file=path, stderr_file=NO_OUTPUT)
    write_backlog_releases(data, path, config, stderr_file=NO_OUTPUT)


def test_in_command_list() -> None:
    """Test the extract_keys command is discovered by the list command."""
    assert 'extract_keys' in [name for name, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'in.csv'], ['--levels', 'Epic']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires the input file and the levels."""
    with pytest.raises(SystemExit):
        extract_keys.build_parser().parse_args(args)


def test_extract_to_file(tmp_path: Path) -> None:
    """Test extracting epics by name writes the epic keys in order."""
    source = tmp_path / 'in.ods'
    target = tmp_path / 'keys.txt'
    _write_source(source)
    assert extract_keys.main(['-i', str(source), '--levels', 'Epic',
                              '-o', str(target)]) == 0
    assert read_key_list(target, stderr_file=NO_OUTPUT) == ['E1', 'E2']


def test_extract_to_stdout(tmp_path: Path,
                           capsys: pytest.CaptureFixture[str]) -> None:
    """Test extracting level 1 without -o prints the keys to stdout."""
    source = tmp_path / 'in.ods'
    _write_source(source)
    assert extract_keys.main(['-i', str(source), '--levels', '1']) == 0
    printed = capsys.readouterr().out.split()
    assert printed == ['S1', 'S2', 'S3']


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing input file makes the command return 1."""
    assert extract_keys.main(['-i', str(tmp_path / 'no.csv'),
                              '--levels', 'Story']) == 1


def test_missing_config(tmp_path: Path) -> None:
    """Test a -c config file that does not exist returns 1."""
    source = tmp_path / 'in.ods'
    _write_source(source)
    assert extract_keys.main(['-i', str(source), '--levels', 'Epic',
                              '-c', str(tmp_path / 'no.cfg')]) == 1


def _extract(source: Path, target: Path, extra: list[str]) -> int:
    """Run extract_keys writing epics to target with extra arguments."""
    return extract_keys.main(['-i', str(source), '--levels', 'Epic',
                              '-o', str(target), *extra])


def test_overwrite_declined(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test answering no leaves the existing key list file unchanged."""
    source, target = tmp_path / 'in.ods', tmp_path / 'keys.txt'
    _write_source(source)
    target.write_text('OLD\n', encoding='utf-8')
    monkeypatch.setattr('sys.stdin', io.StringIO('n\n'))
    assert _extract(source, target, []) == 1
    assert target.read_text(encoding='utf-8') == 'OLD\n'


def test_overwrite_force(tmp_path: Path) -> None:
    """Test the force flag overwrites the existing key list file."""
    source, target = tmp_path / 'in.ods', tmp_path / 'keys.txt'
    _write_source(source)
    target.write_text('OLD\n', encoding='utf-8')
    assert _extract(source, target, ['-f']) == 0
    assert read_key_list(target, stderr_file=NO_OUTPUT) == ['E1', 'E2']
