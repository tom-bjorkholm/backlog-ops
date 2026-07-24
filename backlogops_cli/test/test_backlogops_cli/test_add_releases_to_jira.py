#! /usr/local/bin/python3
"""Tests for the backlogops_cli add_releases_to_jira command.

The Jira write itself is replaced by a stand-in so the command can be
tested without a Jira server: the tests check the command reads the input,
passes the chosen on-existing mode, prints the two labelled lists unless
quiet, writes the returned releases to the requested files, reports an
already-present name as a failure, and is discovered by the list command.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from pathlib import Path
from typing import Callable
import pytest
from backlogops import (
    AddedReleasesToJira, OnExistingKey, Release, ReleaseExistsError)
from backlogops_cli.list import command_modules
from backlogops_cli import add_releases_to_jira
from .cli_test_helpers import (
    base_args, prepare_input, raising_call, read_data_file)


def _result() -> AddedReleasesToJira:
    """Return a canned add result with one added and one present release."""
    added = Release(name='R1', planned_date=date(2026, 1, 1))
    present = Release(name='R9')
    return AddedReleasesToJira(stored=[added], already_present=[present],
                               failed=[])


def _fake_add(captured: dict[str, object], result: AddedReleasesToJira
              ) -> Callable[..., AddedReleasesToJira]:
    """Return a stand-in add that records the mode and returns ``result``."""
    def add(connections: object, preset_name: str, releases: object, *,
            on_existing_key: OnExistingKey,
            **kwargs: object) -> AddedReleasesToJira:
        """Record the on-existing mode and return the canned result."""
        _ = (connections, preset_name, releases, kwargs)
        captured['mode'] = on_existing_key
        return result
    return add


def _patch(monkeypatch: pytest.MonkeyPatch,
           result: AddedReleasesToJira) -> dict[str, object]:
    """Replace the Jira write with a stand-in and return the capture."""
    captured: dict[str, object] = {}
    monkeypatch.setattr(add_releases_to_jira, 'add_releases_to_jira',
                        _fake_add(captured, result))
    return captured


def test_in_command_list() -> None:
    """Test the add_releases_to_jira command is found by the list command."""
    assert 'add_releases_to_jira' in [name for name, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'in.csv']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the input file and the preset."""
    with pytest.raises(SystemExit):
        add_releases_to_jira.build_parser().parse_args(args)


def test_adds_and_prints(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                         capsys: pytest.CaptureFixture[str]) -> None:
    """Test the command adds by default in raise mode and prints the lists."""
    captured = _patch(monkeypatch, _result())
    prepare_input(tmp_path)
    code = add_releases_to_jira.main(base_args(tmp_path))
    assert code == 0
    assert captured['mode'] is OnExistingKey.RAISE
    out = capsys.readouterr().out
    assert 'Added to Jira (1):' in out
    assert '  R1  2026-01-01' in out
    assert 'Already in Jira (1):' in out


def test_skip_existing(tmp_path: Path,
                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Test --skip-existing selects the skip mode."""
    captured = _patch(monkeypatch, _result())
    prepare_input(tmp_path)
    code = add_releases_to_jira.main(base_args(tmp_path, '--skip-existing'))
    assert code == 0
    assert captured['mode'] is OnExistingKey.SKIP


def test_quiet_suppresses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                          capsys: pytest.CaptureFixture[str]) -> None:
    """Test -q suppresses the two lists on stdout."""
    _patch(monkeypatch, _result())
    prepare_input(tmp_path)
    add_releases_to_jira.main(base_args(tmp_path, '-q'))
    assert 'Added to Jira' not in capsys.readouterr().out


def test_writes_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the returned releases are written to the named files."""
    _patch(monkeypatch, _result())
    prepare_input(tmp_path)
    added, existing = tmp_path / 'added.csv', tmp_path / 'existing.csv'
    args = base_args(tmp_path, '--added-file', str(added), '--existing-file',
                     str(existing))
    code = add_releases_to_jira.main(args)
    assert code == 0
    stored = read_data_file(added)
    assert [release.name for release in stored.releases] == ['R1']
    assert [item.key for item in stored.backlog] == ['A']
    assert existing.is_file()


def test_exists_returns_one(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an already-present name without --skip-existing fails."""
    monkeypatch.setattr(add_releases_to_jira, 'add_releases_to_jira',
                        raising_call(ReleaseExistsError(['R1'])))
    prepare_input(tmp_path)
    code = add_releases_to_jira.main(base_args(tmp_path))
    assert code == 1


def test_requires_config(tmp_path: Path) -> None:
    """Test the command fails when no configuration can be found."""
    code = add_releases_to_jira.main(['-i', str(tmp_path / 'in.csv'), '-p',
                                      'w'])
    assert code == 1
