#! /usr/local/bin/python3
"""Tests for the backlogops_cli rank_in_jira command.

The Jira ranking itself is replaced by a stand-in so the command can be
tested without a Jira server: the tests check the command reads the key
list, passes the chosen anchor, relations flag and filter, prints the
result unless quiet, reports a bad filter as a failure, and is discovered by
the list command.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Callable
import pytest
from backlogops import (
    AvailableTeams, BacklogOpsConfig, BadJiraRankFilter, JiraRankAnchor,
    RankedInJira, write_backlog_ops_config)
from backlogops.no_text_io import NoTextIO
from backlogops_cli.list import command_modules
from backlogops_cli import rank_in_jira

NO = NoTextIO()


def _config_file(path: Path) -> None:
    """Write a minimal backlog-ops configuration to a file."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]), stderr_file=NO)
    write_backlog_ops_config(config, path, NO)


def _key_file(path: Path) -> None:
    """Write a key list file naming two issues to move."""
    path.write_text('B A\n', encoding='utf-8')


# pylint: disable-next=too-many-arguments
def _fake_rank(captured: dict[str, object]) -> Callable[..., RankedInJira]:
    """Return a stand-in rank that records its arguments."""
    def rank(connections: object, preset_name: str, keys: object, *,
             filter_override: object = None, anchor: object = None,
             honor_relations: bool = False, levels: object = None,
             status_map: object = None) -> RankedInJira:
        """Record the preset, keys, filter, anchor and relations flag."""
        _ = (connections, levels, status_map)
        captured['preset'] = preset_name
        captured['keys'] = list(keys)  # type: ignore[call-overload]
        captured['filter'] = filter_override
        captured['anchor'] = anchor
        captured['honor'] = honor_relations
        return RankedInJira(['B', 'A'], [], [])
    return rank


def _patch(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Replace the Jira ranking with a stand-in and return the capture."""
    captured: dict[str, object] = {}
    monkeypatch.setattr(rank_in_jira, 'jira_rank_move_keys',
                        _fake_rank(captured))
    return captured


def _args(tmp_path: Path, *extra: str) -> list[str]:
    """Return the base command line naming the config and key list."""
    return ['-p', 'w', '-k', str(tmp_path / 'keys.txt'),
            '-c', str(tmp_path / 'ops.cfg'), *extra]


def _prepare(tmp_path: Path) -> None:
    """Write the config file and the key list file."""
    _config_file(tmp_path / 'ops.cfg')
    _key_file(tmp_path / 'keys.txt')


def test_in_command_list() -> None:
    """Test the rank_in_jira command is discovered by the list command."""
    assert 'rank_in_jira' in [name for name, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-p', 'w']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the preset and the key list."""
    with pytest.raises(SystemExit):
        rank_in_jira.build_parser().parse_args(args)


def test_ranks_and_prints(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                          capsys: pytest.CaptureFixture[str]) -> None:
    """Test the command ranks at the top by default and prints the result."""
    captured = _patch(monkeypatch)
    _prepare(tmp_path)
    code = rank_in_jira.main(_args(tmp_path))
    assert code == 0
    assert captured['keys'] == ['B', 'A']
    assert captured['anchor'] is JiraRankAnchor.BACKLOG_TOP
    assert captured['honor'] is False
    assert captured['filter'] is None
    assert 'Ranked in Jira (2):' in capsys.readouterr().out


@pytest.mark.parametrize('value,anchor', [
    ('backlog-top', JiraRankAnchor.BACKLOG_TOP),
    ('backlog-bottom', JiraRankAnchor.BACKLOG_BOTTOM),
    ('first-key', JiraRankAnchor.FIRST_KEY),
    ('last-key', JiraRankAnchor.LAST_KEY)])
def test_anchor_choice(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                       value: str, anchor: JiraRankAnchor) -> None:
    """Test each --anchor value selects the matching anchor."""
    captured = _patch(monkeypatch)
    _prepare(tmp_path)
    rank_in_jira.main(_args(tmp_path, '--anchor', value))
    assert captured['anchor'] is anchor


def test_honor_relations(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test --honor-relations enables honouring dependencies and children."""
    captured = _patch(monkeypatch)
    _prepare(tmp_path)
    rank_in_jira.main(_args(tmp_path, '--honor-relations'))
    assert captured['honor'] is True


def test_filter_passed(tmp_path: Path,
                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the filter override is passed through to the ranking."""
    captured = _patch(monkeypatch)
    _prepare(tmp_path)
    rank_in_jira.main(_args(tmp_path, '--filter', 'project = X'))
    assert captured['filter'] == 'project = X'


def test_quiet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
               capsys: pytest.CaptureFixture[str]) -> None:
    """Test -q suppresses the result listing on stdout."""
    _patch(monkeypatch)
    _prepare(tmp_path)
    rank_in_jira.main(_args(tmp_path, '-q'))
    assert 'Ranked in Jira' not in capsys.readouterr().out


def test_error_returns_1(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a bad filter is reported and the command returns 1."""
    def _raise(*_args: object, **_kwargs: object) -> RankedInJira:
        """Raise as the ranking does for a filter that is not usable."""
        raise BadJiraRankFilter(jql_text='x', message='bad')
    monkeypatch.setattr(rank_in_jira, 'jira_rank_move_keys', _raise)
    _prepare(tmp_path)
    assert rank_in_jira.main(_args(tmp_path)) == 1
