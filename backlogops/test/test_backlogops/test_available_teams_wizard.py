#! /usr/local/bin/python3
"""Tests for the interactive AvailableTeams wizard."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
from tableio_cfg_json import WizardUiBridgeConsole
from backlogops.available_teams import AvailableTeams
from backlogops.available_teams_wizard import available_teams_wizard
from backlogops.work_hours import DEFAULT_WORK_WEEK, WeekDay


def _run(answers: list[str]) -> AvailableTeams:
    """Run the wizard with scripted console answers and return the result."""
    stdin = io.StringIO('\n'.join(answers) + '\n')
    bridge = WizardUiBridgeConsole(io.StringIO(), stdin, io.StringIO())
    return available_teams_wizard(bridge)


def test_minimal_workforce() -> None:
    """Test an all-default run yields an empty workforce with defaults."""
    answers = ['', '', '', '', '', '', '', '', '', '']
    teams = _run(answers)
    assert not teams.persons
    assert not teams.teams
    assert teams.company_work_hours.work_hours == DEFAULT_WORK_WEEK


def test_full_workforce() -> None:
    """Test a full run builds the persons, team, and memberships."""
    answers = [
        '', '', '', '', '', '', '',
        '',
        'y', 'Ada', '',
        'y', 'Bo', '',
        '',
        'y', 'Phoenix', '30', '2', '',
        '',
        'y', '1', '', '', '', '',
        'y', '1', '0.5', '', '', '',
        '']
    teams = _run(answers)
    assert sorted(teams.persons) == ['ada', 'bo']
    team = teams.teams[0]
    assert team.name == 'Phoenix'
    assert team.velocity == 30.0
    assert [(m.person_name, m.fte) for m in team.members] == \
        [('Ada', 1.0), ('Bo', 0.5)]


def test_choose_by_name() -> None:
    """Test a membership can select a person by typing the name."""
    answers = [
        '', '', '', '', '', '', '',
        '',
        'y', 'Ada', '',
        '',
        'y', 'T', '', '', '', '',
        'y', 'ada', '', '', '', '',
        '',
        '']
    teams = _run(answers)
    assert teams.teams[0].members[0].person_name == 'Ada'


def test_duplicate_name() -> None:
    """Test entering a duplicate person name is rejected and re-asked."""
    answers = [
        '', '', '', '', '', '', '',
        '',
        'y', 'Ada', '',
        'y', 'ada', 'Bo', '',
        '',
        '']
    teams = _run(answers)
    assert sorted(teams.persons) == ['ada', 'bo']


def test_reask_number() -> None:
    """Test a non-numeric velocity is rejected and then accepted."""
    answers = [
        '', '', '', '', '', '', '',
        '',
        '',
        'y', 'Phoenix', 'abc', '5', '', '',
        '',
        '']
    teams = _run(answers)
    assert teams.teams[0].velocity == 5.0


def test_company_exc() -> None:
    """Test a company exception with re-asked invalid date and end order."""
    answers = [
        '', '', '', '', '', '', '',
        'y', 'bad', '2026-01-01', '2025-12-31', '2026-01-05', '', 'maybe',
        'n',
        '',
        '',
        '']
    teams = _run(answers)
    exception = teams.company_work_hours.exceptions[0]
    assert exception.start_date == date(2026, 1, 1)
    assert exception.end_date == date(2026, 1, 5)
    assert exception.new_work_days is False


def test_vacation() -> None:
    """Test a personal vacation exception is captured for the person."""
    answers = [
        '', '', '', '', '', '', '',
        '',
        'y', 'Ada', 'y', '2026-07-01', '2026-07-20', '0', 'n', '',
        '',
        '']
    teams = _run(answers)
    vacation = teams.persons['ada'].exceptions[0]
    assert vacation.start_date == date(2026, 7, 1)
    assert vacation.end_date == date(2026, 7, 20)
    assert teams.company_work_hours.work_hours[WeekDay.MONDAY] == 8.0
