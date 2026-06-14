#! /usr/local/bin/python3
"""Tests for storing and loading AvailableTeams as config-as-json."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import json
from datetime import date
from pathlib import Path
import pytest
from backlogops.available_teams import AvailableTeams
from backlogops.available_teams_config import (
    AvailableTeamsConfig, read_available_teams, write_available_teams)
from backlogops.person import Person
from backlogops.team import FteException, Membership, Team
from backlogops.work_hours import (
    CompanyWorkHours, DEFAULT_WORK_WEEK, ExceptionWorkHours, WeekDay)
from backlogops.no_text_io import NoTextIO


def _company() -> CompanyWorkHours:
    """Return a company schedule with a shorter Friday and one holiday."""
    schedule = dict(DEFAULT_WORK_WEEK)
    schedule[WeekDay.FRIDAY] = 6.0
    holiday = ExceptionWorkHours(date(2026, 12, 24), date(2026, 12, 26), 0.0)
    return CompanyWorkHours(work_hours=schedule, exceptions=[holiday])


def _persons() -> dict[str, Person]:
    """Return two persons, one of which has a vacation period."""
    vacation = ExceptionWorkHours(date(2026, 7, 1), date(2026, 7, 20), 0.0)
    return {'ada': Person(name='Ada', exceptions=[vacation]),
            'bo': Person(name='Bo')}


def _team() -> Team:
    """Return a team with two members and one full-time-equivalent change."""
    learning = FteException(date(2026, 2, 1), date(2026, 2, 28), 0.5)
    ada = Membership(person_name='Ada', fte=1.0, start_date=date(2026, 1, 1),
                     fte_exceptions=[learning])
    bo = Membership(person_name='Bo', fte=0.5)
    return Team(name='Phoenix', velocity=30.0, sum_fte_at_velocity=2.0,
                sprint_length=10, aliases=['PHX'], members=[ada, bo])


def _sample_teams() -> AvailableTeams:
    """Return a rich but consistent workforce used by several tests."""
    return AvailableTeams(persons=_persons(), teams=[_team()],
                          company_work_hours=_company())


def test_round_trip(tmp_path: Path) -> None:
    """Test a workforce survives a write followed by a read unchanged."""
    filename = tmp_path / 'teams.json'
    write_available_teams(_sample_teams(), filename, NoTextIO())
    loaded = read_available_teams(filename, NoTextIO())
    loaded.check_consistency(NoTextIO())
    team = loaded.teams[0]
    assert team.name == 'Phoenix'
    assert team.aliases == ['PHX']
    assert team.members[0].start_date == date(2026, 1, 1)
    assert team.members[0].fte_exceptions[0].fte == 0.5
    assert team.members[1].fte == 0.5
    assert loaded.persons['ada'].exceptions[0].end_date == date(2026, 7, 20)
    assert loaded.company_work_hours.work_hours[WeekDay.FRIDAY] == 6.0
    assert loaded.company_work_hours.exceptions[0].start_date == \
        date(2026, 12, 24)


def test_stable(tmp_path: Path) -> None:
    """Test writing the same workforce twice yields identical files."""
    first = tmp_path / 'first.json'
    second = tmp_path / 'second.json'
    write_available_teams(_sample_teams(), first, NoTextIO())
    loaded = read_available_teams(first, NoTextIO())
    write_available_teams(loaded, second, NoTextIO())
    assert first.read_text() == second.read_text()


def test_day_name_keys(tmp_path: Path) -> None:
    """Test the week-day schedule uses day-name keys in the JSON file."""
    filename = tmp_path / 'teams.json'
    write_available_teams(_sample_teams(), filename, NoTextIO())
    data = json.loads(filename.read_text())
    assert data['company_work_hours']['work_hours']['FRIDAY'] == 6.0


def test_dates_omitted(tmp_path: Path) -> None:
    """Test a membership without dates omits them from the JSON file."""
    filename = tmp_path / 'teams.json'
    write_available_teams(_sample_teams(), filename, NoTextIO())
    data = json.loads(filename.read_text())
    bo_member = data['teams'][0]['members'][1]
    assert 'start_date' not in bo_member
    assert 'end_date' not in bo_member


def test_empty(tmp_path: Path) -> None:
    """Test an empty workforce can be written and read back."""
    filename = tmp_path / 'empty.json'
    write_available_teams(AvailableTeams(persons={}, teams=[]), filename,
                          NoTextIO())
    loaded = read_available_teams(filename, NoTextIO())
    assert not loaded.persons
    assert not loaded.teams


def test_unknown_member(tmp_path: Path) -> None:
    """Test writing a team that references an unknown person fails."""
    persons = {'ada': Person(name='Ada')}
    team = Team(name='Phoenix', velocity=1.0, sum_fte_at_velocity=1.0,
                sprint_length=10, members=[Membership(person_name='Cory')])
    teams = AvailableTeams(persons=persons, teams=[team])
    with pytest.raises(KeyError):
        write_available_teams(teams, tmp_path / 'bad.json', NoTextIO())


def test_overallocation(tmp_path: Path) -> None:
    """Test writing an over-allocated person fails the capacity check."""
    persons = {'ada': Person(name='Ada')}
    first = Team(name='A', velocity=1.0, sum_fte_at_velocity=1.0,
                 sprint_length=10, members=[Membership(person_name='Ada')])
    second = Team(name='B', velocity=1.0, sum_fte_at_velocity=1.0,
                  sprint_length=10,
                  members=[Membership(person_name='Ada', fte=0.5)])
    teams = AvailableTeams(persons=persons, teams=[first, second])
    with pytest.raises(ValueError):
        write_available_teams(teams, tmp_path / 'bad.json', NoTextIO())


def _config_text(members: list[dict[str, object]]) -> str:
    """Return configuration JSON text with the given team members."""
    return json.dumps({
        'company_work_hours': {
            'work_hours': {day.name: 8.0 for day in WeekDay},
            'exceptions': []},
        'persons': {'ada': {'name': 'Ada', 'exceptions': []}},
        'teams': [{
            'name': 'Phoenix', 'velocity': 1.0, 'sum_fte_at_velocity': 1.0,
            'sprint_length': 10, 'aliases': [], 'members': members}]})


def test_bad_date() -> None:
    """Test reading a membership with a malformed date is rejected."""
    members = [{'person_name': 'Ada', 'fte': 1.0, 'fte_exceptions': [],
                'start_date': 'not-a-date'}]
    with pytest.raises(TypeError):
        AvailableTeamsConfig(from_json_data_text=_config_text(members),
                             stderr_file=NoTextIO())


def test_missing_field() -> None:
    """Test reading a person without the required name is rejected."""
    text = json.dumps({
        'company_work_hours': {
            'work_hours': {day.name: 8.0 for day in WeekDay},
            'exceptions': []},
        'persons': {'ada': {'exceptions': []}},
        'teams': []})
    with pytest.raises(KeyError):
        AvailableTeamsConfig(from_json_data_text=text, stderr_file=NoTextIO())
