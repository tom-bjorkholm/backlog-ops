#! /usr/local/bin/python3
"""Tests for the backlogops_cli update_backlog_in_jira command.

The Jira update itself is replaced by a stand-in so the command can be
tested without a Jira server: the tests check the command reads the input,
resolves the columns from the ``-s``/``--store`` and ``-e``/``--exclude``
flags (including the ``all`` word), maps the missing-key and link flags,
prints the result lists unless quiet, reports a missing-key raise as a
failure, and is discovered by the list command.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Callable
import pytest
from backlogops import (
    AddedToJira, AvailableTeams, BacklogItem, BacklogOpsConfig,
    BacklogReleases, DEF_BACKLOG_COLUMN_MAP, DEF_RELEASE_COLUMN_MAP,
    FormatRules, ItemNotInJiraError, JiraConnectConfig, JiraIOConfig,
    JiraPreset, JiraRankAnchor, LinkUpdate, OnMissingKey, Release, Status,
    TokenStorage, UpdatedBacklogInJira, allow_overwrite,
    resolve_output_config, write_backlog_ops_config, write_backlog_releases)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import update_backlog_in_jira
from backlogops_cli.update_backlog_in_jira import _passphrase

NO = NoTextIO()


def _jira_config() -> JiraIOConfig:
    """Return a Jira config with one preset ``'w'`` and the default maps."""
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = TokenStorage.CLEAR_INTERNAL
    conn.stored_token = 'TOK'
    preset = JiraPreset(stderr_file=NO)
    preset.connection_name = 'c'
    preset.backlog_column_map_name = 'bk'
    preset.release_column_map_name = 'rel'
    preset.def_project = 'PROJ'
    config = JiraIOConfig(stderr_file=NO)
    config.connections = {'c': conn}
    config.backlog_column_maps = {'bk': DEF_BACKLOG_COLUMN_MAP}
    config.release_column_maps = {'rel': DEF_RELEASE_COLUMN_MAP}
    config.presets = {'w': preset}
    return config


def _config_file(path: Path) -> None:
    """Write a backlog-ops configuration with a Jira preset to a file."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]), stderr_file=NO)
    config.jira = _jira_config()
    write_backlog_ops_config(config, path, NO)


def _write_input(path: Path) -> None:
    """Write an input file holding one backlog item and one release."""
    data = BacklogReleases(
        backlog=[BacklogItem(key='A', level=1, title='First', story_points=5,
                             status=Status.TODO, release='R1')],
        releases=[Release(name='R1')])
    out_config = resolve_output_config(None, data_file=path, stderr_file=NO)
    write_backlog_releases(data, path, out_config, FormatRules(),
                           file_exists_callback=allow_overwrite)


def _result() -> UpdatedBacklogInJira:
    """Return a canned update result with one updated item."""
    return UpdatedBacklogInJira(updated=['A'], already_correct=[], ignored=[],
                                failed=[], status_mismatch=[], failed_links=[],
                                added=AddedToJira([], [], [], {}, [], []))


def _fake_update(captured: dict[str, object], result: UpdatedBacklogInJira
                 ) -> Callable[..., UpdatedBacklogInJira]:
    """Return a stand-in update recording the fields, mode and link policy."""
    def update(connections: object, preset: str, backlog: object, *,
               on_missing_key: OnMissingKey, fields_to_update: list[str],
               link_update: LinkUpdate,
               **kwargs: object) -> UpdatedBacklogInJira:
        """Record the resolved fields, missing mode, links and rank anchor."""
        _ = (connections, preset, backlog)
        captured['fields'] = fields_to_update
        captured['mode'] = on_missing_key
        captured['link'] = link_update
        captured['rank'] = kwargs.get('rank_anchor')
        return result
    return update


def _patch(monkeypatch: pytest.MonkeyPatch,
           result: UpdatedBacklogInJira) -> dict[str, object]:
    """Replace the Jira update with a stand-in and return the capture."""
    captured: dict[str, object] = {}
    monkeypatch.setattr(update_backlog_in_jira, 'update_backlog_in_jira',
                        _fake_update(captured, result))
    return captured


def _args(tmp_path: Path, *extra: str) -> list[str]:
    """Return the base command arguments plus any extra flags."""
    return ['-i', str(tmp_path / 'in.csv'), '-p', 'w', '-c',
            str(tmp_path / 'ops.cfg'), *extra]


def _prepare(tmp_path: Path) -> None:
    """Write the configuration and the input file used by the tests."""
    _config_file(tmp_path / 'ops.cfg')
    _write_input(tmp_path / 'in.csv')


def test_passphrase(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the pass phrase prompt reads from getpass."""
    monkeypatch.setattr(update_backlog_in_jira, 'getpass',
                        lambda _prompt: 'secret')
    assert _passphrase() == 'secret'


def test_in_command_list() -> None:
    """Test the update_backlog_in_jira command is found by the list."""
    assert 'update_backlog_in_jira' in [n for n, _ in command_modules()]


@pytest.mark.parametrize('args', [['-i', 'in.csv', '-p', 'w'],
                                  ['-i', 'in.csv', '-s', 'title'],
                                  ['-i', 'in.csv', '-p', 'w', '-s', 'title',
                                   '-e', 'team']])
def test_bad_args(args: list[str]) -> None:
    """Test the parser requires the preset and exactly one column flag."""
    with pytest.raises(SystemExit):
        update_backlog_in_jira.build_parser().parse_args(args)


def test_store_list(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test -s stores exactly the listed columns."""
    captured = _patch(monkeypatch, _result())
    _prepare(tmp_path)
    code = update_backlog_in_jira.main(
        _args(tmp_path, '-s', 'title', 'status'))
    assert code == 0
    assert captured['fields'] == ['title', 'status']


def test_store_all(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test -s all stores every mapped writable column."""
    captured = _patch(monkeypatch, _result())
    _prepare(tmp_path)
    code = update_backlog_in_jira.main(_args(tmp_path, '-s', 'all'))
    assert code == 0
    fields = captured['fields']
    assert isinstance(fields, list)
    assert set(fields) == {'title', 'status', 'parent_key', 'release', 'team',
                           'story_points', 'depends_on_f2s', 'description'}


def test_exclude(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test -e stores every column except the excluded ones."""
    captured = _patch(monkeypatch, _result())
    _prepare(tmp_path)
    code = update_backlog_in_jira.main(
        _args(tmp_path, '-e', 'description', 'team'))
    assert code == 0
    fields = captured['fields']
    assert isinstance(fields, list)
    assert 'description' not in fields and 'team' not in fields
    assert 'title' in fields and 'status' in fields


def test_store_unknown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                       capsys: pytest.CaptureFixture[str]) -> None:
    """Test a -s column that is not updatable is dropped and reported."""
    captured = _patch(monkeypatch, _result())
    _prepare(tmp_path)
    code = update_backlog_in_jira.main(_args(tmp_path, '-s', 'title', 'bogus'))
    assert code == 0
    assert captured['fields'] == ['title']
    assert 'bogus' in capsys.readouterr().err


@pytest.mark.parametrize('flag, mode', [
    ('ignore', OnMissingKey.IGNORE), ('add', OnMissingKey.ADD),
    ('raise', OnMissingKey.RAISE)])
def test_on_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, flag: str,
                    mode: OnMissingKey) -> None:
    """Test --on-missing maps to the matching missing-key mode."""
    captured = _patch(monkeypatch, _result())
    _prepare(tmp_path)
    code = update_backlog_in_jira.main(
        _args(tmp_path, '-s', 'all', '--on-missing', flag))
    assert code == 0
    assert captured['mode'] is mode


@pytest.mark.parametrize('extra, link', [
    ([], LinkUpdate.RECONCILE),
    (['--links', 'reconcile'], LinkUpdate.RECONCILE),
    (['--links', 'add'], LinkUpdate.ADD_MISSING)])
def test_link_policy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                     extra: list[str], link: LinkUpdate) -> None:
    """Test --links chooses the link policy, reconciling by default."""
    captured = _patch(monkeypatch, _result())
    _prepare(tmp_path)
    code = update_backlog_in_jira.main(_args(tmp_path, '-s', 'all', *extra))
    assert code == 0
    assert captured['link'] is link


def test_prints_lists(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                      capsys: pytest.CaptureFixture[str]) -> None:
    """Test the result lists are printed by default."""
    _patch(monkeypatch, _result())
    _prepare(tmp_path)
    code = update_backlog_in_jira.main(_args(tmp_path, '-s', 'all'))
    assert code == 0
    out = capsys.readouterr().out
    assert 'Updated in Jira (1):' in out and '  A' in out


def test_quiet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
               capsys: pytest.CaptureFixture[str]) -> None:
    """Test -q suppresses the result lists on stdout."""
    _patch(monkeypatch, _result())
    _prepare(tmp_path)
    update_backlog_in_jira.main(_args(tmp_path, '-s', 'all', '-q'))
    assert 'Updated in Jira' not in capsys.readouterr().out


def test_missing_raises(tmp_path: Path,
                        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a raised missing key returns one."""
    def _raising(connections: object, preset: str, backlog: object, *,
                 on_missing_key: OnMissingKey, fields_to_update: list[str],
                 link_update: LinkUpdate,
                 **kwargs: object) -> UpdatedBacklogInJira:
        """Raise as the real function does when a key is missing."""
        _ = (connections, preset, backlog, on_missing_key, fields_to_update,
             link_update, kwargs)
        raise ItemNotInJiraError(['A'], 'Backlog keys')
    monkeypatch.setattr(update_backlog_in_jira, 'update_backlog_in_jira',
                        _raising)
    _prepare(tmp_path)
    assert update_backlog_in_jira.main(_args(tmp_path, '-s', 'all')) == 1


def test_requires_config(tmp_path: Path) -> None:
    """Test the command fails when no configuration can be found."""
    code = update_backlog_in_jira.main(['-i', str(tmp_path / 'in.csv'), '-p',
                                        'w', '-s', 'all'])
    assert code == 1


def test_rank_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test --rank passes the chosen anchor to the update."""
    captured = _patch(monkeypatch, _result())
    _prepare(tmp_path)
    code = update_backlog_in_jira.main(
        _args(tmp_path, '-s', 'all', '--rank', 'first-key'))
    assert code == 0
    assert captured['rank'] is JiraRankAnchor.FIRST_KEY


def test_no_rank_default(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test no --rank leaves the rank anchor unset."""
    captured = _patch(monkeypatch, _result())
    _prepare(tmp_path)
    update_backlog_in_jira.main(_args(tmp_path, '-s', 'all'))
    assert captured['rank'] is None
