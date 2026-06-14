#! /usr/local/bin/python3
"""Tests for the backlogops_cli teams_wizard command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from pathlib import Path
import pytest
from backlogops import (
    AvailableTeams, Membership, NoTextIO, Person, Team, read_available_teams)
from backlogops_cli.list import command_modules
import backlogops_cli.teams_wizard as teams_wizard


def test_in_command_list() -> None:
    """Test the teams_wizard command is discovered by the list command."""
    names = [name for name, _ in command_modules()]
    assert 'teams_wizard' in names


def test_requires_output() -> None:
    """Test the command requires the output file argument."""
    with pytest.raises(SystemExit):
        teams_wizard.build_parser().parse_args([])


def test_main_writes_file(tmp_path: Path,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the command adds the .cfg extension and writes a readable file."""
    answers = ['', '', '', '', '', '', '', '', '', '']
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'.join(answers) + '\n'))
    assert teams_wizard.main(['-o', str(tmp_path / 'teams')]) == 0
    written = tmp_path / 'teams.cfg'
    assert written.exists()
    loaded = read_available_teams(written, NoTextIO())
    assert not loaded.teams


def test_main_reports_failure(tmp_path: Path,
                              monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an inconsistent workforce makes the command return 1."""
    def _bad_wizard(_bridge: object) -> AvailableTeams:
        """Return an over-allocated workforce that fails validation."""
        persons = {'ada': Person(name='Ada')}
        first = Team(name='A', velocity=1.0, sum_fte_at_velocity=1.0,
                     sprint_length=10, members=[Membership(person_name='Ada')])
        second = Team(name='B', velocity=1.0, sum_fte_at_velocity=1.0,
                      sprint_length=10,
                      members=[Membership(person_name='Ada', fte=0.5)])
        return AvailableTeams(persons=persons, teams=[first, second])
    monkeypatch.setattr(teams_wizard, 'available_teams_wizard', _bad_wizard)
    assert teams_wizard.main(['-o', str(tmp_path / 'teams')]) == 1
    assert not (tmp_path / 'teams.cfg').exists()
