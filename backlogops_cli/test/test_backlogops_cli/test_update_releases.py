#! /usr/local/bin/python3
"""Tests for the backlogops_cli update_releases_in_jira command.

The Jira update itself is replaced by a stand-in so the command can be
tested without a Jira server: the tests check the command reads the input,
maps the ``--on-missing`` flag to the mode, limits the releases with
``--only-listed``, prints the result lists unless quiet, reports a
missing-name raise as a failure, and is discovered by the list command.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Callable
import pytest
from backlogops import (
    AvailableTeams, BacklogItem, BacklogOpsConfig, BacklogReleases,
    FormatRules, ItemNotInJiraError, OnMissingKey, Release, Status,
    UpdatedReleasesInJira, allow_overwrite, resolve_output_config,
    write_backlog_ops_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import update_releases_in_jira

NO = NoTextIO()


def _config_file(path: Path) -> None:
    """Write a minimal backlog-ops configuration to a file."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]), stderr_file=NO)
    write_backlog_ops_config(config, path, NO)


def _write_input(path: Path) -> None:
    """Write an input file holding one backlog item and two releases."""
    data = BacklogReleases(
        backlog=[BacklogItem(key='A', level=1, title='First', story_points=5,
                             status=Status.TODO, release='R1')],
        releases=[Release(name='R1'), Release(name='R2')])
    out_config = resolve_output_config(None, data_file=path, stderr_file=NO)
    write_backlog_releases(data, path, out_config, FormatRules(),
                           file_exists_callback=allow_overwrite)


def _result() -> UpdatedReleasesInJira:
    """Return a canned update result with one updated release."""
    return UpdatedReleasesInJira(updated=['R1'], ignored=[], added=[],
                                 failed=[])


def _fake_update(captured: dict[str, object], result: UpdatedReleasesInJira
                 ) -> Callable[..., UpdatedReleasesInJira]:
    """Return a stand-in update recording the mode and release names."""
    def update(connections: object, preset_name: str, releases: object, *,
               on_missing_key: OnMissingKey,
               **kwargs: object) -> UpdatedReleasesInJira:
        """Record the mode and the release names and return the result."""
        _ = (connections, preset_name, kwargs)
        captured['mode'] = on_missing_key
        assert isinstance(releases, list)
        captured['names'] = [release.name for release in releases]
        return result
    return update


def _patch(monkeypatch: pytest.MonkeyPatch,
           result: UpdatedReleasesInJira) -> dict[str, object]:
    """Replace the Jira update with a stand-in and return the capture."""
    captured: dict[str, object] = {}
    monkeypatch.setattr(update_releases_in_jira, 'update_releases_in_jira',
                        _fake_update(captured, result))
    return captured


def _args(tmp_path: Path, *extra: str) -> list[str]:
    """Return the base command arguments plus any extra flags."""
    return ['-i', str(tmp_path / 'in.csv'), '-p', 'w', '-c',
            str(tmp_path / 'ops.cfg'), *extra]


def test_in_command_list() -> None:
    """Test the update_releases_in_jira command is found by the list."""
    assert 'update_releases_in_jira' in [n for n, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'in.csv']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the input file and the preset."""
    with pytest.raises(SystemExit):
        update_releases_in_jira.build_parser().parse_args(args)


def test_default_raise(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                       capsys: pytest.CaptureFixture[str]) -> None:
    """Test the command updates in raise mode and prints the lists."""
    captured = _patch(monkeypatch, _result())
    _config_file(tmp_path / 'ops.cfg')
    _write_input(tmp_path / 'in.csv')
    code = update_releases_in_jira.main(_args(tmp_path))
    assert code == 0
    assert captured['mode'] is OnMissingKey.RAISE
    assert captured['names'] == ['R1', 'R2']
    out = capsys.readouterr().out
    assert 'Updated in Jira (1):' in out and '  R1' in out


@pytest.mark.parametrize('flag, mode', [
    ('ignore', OnMissingKey.IGNORE), ('add', OnMissingKey.ADD)])
def test_on_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, flag: str,
                    mode: OnMissingKey) -> None:
    """Test --on-missing maps to the matching missing-name mode."""
    captured = _patch(monkeypatch, _result())
    _config_file(tmp_path / 'ops.cfg')
    _write_input(tmp_path / 'in.csv')
    code = update_releases_in_jira.main(_args(tmp_path, '--on-missing', flag))
    assert code == 0
    assert captured['mode'] is mode


def test_only_listed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test --only-listed limits the update to the named releases."""
    captured = _patch(monkeypatch, _result())
    _config_file(tmp_path / 'ops.cfg')
    _write_input(tmp_path / 'in.csv')
    code = update_releases_in_jira.main(
        _args(tmp_path, '--release', 'R1', '--only-listed'))
    assert code == 0
    assert captured['names'] == ['R1']


def test_quiet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
               capsys: pytest.CaptureFixture[str]) -> None:
    """Test -q suppresses the result lists on stdout."""
    _patch(monkeypatch, _result())
    _config_file(tmp_path / 'ops.cfg')
    _write_input(tmp_path / 'in.csv')
    update_releases_in_jira.main(_args(tmp_path, '-q'))
    assert 'Updated in Jira' not in capsys.readouterr().out


def test_missing_raises(tmp_path: Path,
                        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a raised missing name without add/ignore returns one."""
    def _raising(connections: object, preset_name: str, releases: object, *,
                 on_missing_key: OnMissingKey,
                 **kwargs: object) -> UpdatedReleasesInJira:
        """Raise as the real function does when a name is missing."""
        _ = (connections, preset_name, releases, on_missing_key, kwargs)
        raise ItemNotInJiraError(['R2'], 'Release names')
    monkeypatch.setattr(update_releases_in_jira, 'update_releases_in_jira',
                        _raising)
    _config_file(tmp_path / 'ops.cfg')
    _write_input(tmp_path / 'in.csv')
    assert update_releases_in_jira.main(_args(tmp_path)) == 1


def test_requires_config(tmp_path: Path) -> None:
    """Test the command fails when no configuration can be found."""
    code = update_releases_in_jira.main(['-i', str(tmp_path / 'in.csv'), '-p',
                                         'w'])
    assert code == 1
