#! /usr/local/bin/python3
"""Tests for the backlogops_cli teams_wizard command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from pathlib import Path
import pytest
from backlogops import (
    AvailableTeams, BacklogOpsConfig, Membership, NoTextIO, Person, Team,
    read_backlog_ops_config)
from backlogops_cli.list import command_modules
from backlogops_cli import teams_wizard


def test_in_command_list() -> None:
    """Test the teams_wizard command is discovered by the list command."""
    names = [name for name, _ in command_modules()]
    assert 'teams_wizard' in names


def test_requires_output() -> None:
    """Test the command requires the output file argument."""
    with pytest.raises(SystemExit):
        teams_wizard.build_parser().parse_args([])


def test_no_textual_flag() -> None:
    """Test the --no-textual switch is parsed as a boolean flag."""
    parser = teams_wizard.build_parser()
    assert parser.parse_args(['-o', 'x']).no_textual is False
    assert parser.parse_args(['-o', 'x', '--no-textual']).no_textual is True


def test_no_textual_writes(tmp_path: Path,
                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the forced console interface writes a configuration file."""
    answers = [''] * 13
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'.join(answers) + '\n'))
    assert teams_wizard.main(
        ['-o', str(tmp_path / 'teams'), '--no-textual']) == 0
    assert (tmp_path / 'teams.cfg').exists()


def test_main_writes_file(tmp_path: Path,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the command adds the .cfg extension and writes a readable file."""
    answers = [''] * 13
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'.join(answers) + '\n'))
    assert teams_wizard.main(['-o', str(tmp_path / 'teams')]) == 0
    written = tmp_path / 'teams.cfg'
    assert written.exists()
    loaded = read_backlog_ops_config(written, NoTextIO())
    assert not loaded.available_teams.teams


def test_overwrite_declined(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test declining the overwrite keeps the config and skips the wizard."""
    target = tmp_path / 'teams.cfg'
    target.write_text('OLD', encoding='utf-8')
    monkeypatch.setattr('sys.stdin', io.StringIO('n\n'))
    assert teams_wizard.main(['-o', str(tmp_path / 'teams'),
                              '--no-textual']) == 1
    assert target.read_text(encoding='utf-8') == 'OLD'


def test_overwrite_force(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the force flag overwrites the existing config without asking."""
    target = tmp_path / 'teams.cfg'
    target.write_text('OLD', encoding='utf-8')
    answers = [''] * 13
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'.join(answers) + '\n'))
    assert teams_wizard.main(['-o', str(tmp_path / 'teams'),
                              '--no-textual', '-f']) == 0
    loaded = read_backlog_ops_config(target, NoTextIO())
    assert not loaded.available_teams.teams


def test_main_reports_failure(tmp_path: Path,
                              monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an inconsistent workforce makes the command return 1."""
    def _bad_wizard(_bridge: object) -> BacklogOpsConfig:
        """Return an over-allocated workforce that fails validation."""
        persons = {'ada': Person(name='Ada')}
        first = Team(name='A', velocity=1.0, sum_fte_at_velocity=1.0,
                     sprint_length=10, members=[Membership(person_name='Ada')])
        second = Team(name='B', velocity=1.0, sum_fte_at_velocity=1.0,
                      sprint_length=10,
                      members=[Membership(person_name='Ada', fte=0.5)])
        bad = AvailableTeams(persons=persons, teams=[first, second])
        return BacklogOpsConfig(available_teams=bad)
    monkeypatch.setattr(teams_wizard, 'teams_config_wizard', _bad_wizard)
    assert teams_wizard.main(['-o', str(tmp_path / 'teams')]) == 1
    assert not (tmp_path / 'teams.cfg').exists()
