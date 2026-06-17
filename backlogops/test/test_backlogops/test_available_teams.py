#! /usr/local/bin/python3
"""Tests for the available workforce and its consistency checks."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from io import StringIO

import pytest

from backlogops.available_teams import AvailableTeams, candidate_days
from backlogops.available_teams import membership_fte_on
from backlogops.person import Person
from backlogops.team import FteException, Membership, Team
from backlogops.work_hours import ExceptionWorkHours
from backlogops.no_text_io import NoTextIO


def _persons() -> dict[str, Person]:
    """Return a registry with two persons keyed by lower-case name."""
    return {'ada': Person(name='Ada'), 'bo': Person(name='Bo')}


def _available(teams: list[Team]) -> AvailableTeams:
    """Return an available workforce with the two known persons."""
    return AvailableTeams(persons=_persons(), teams=teams)


def test_available_ok() -> None:
    """Test a consistent workforce passes its consistency check."""
    team = Team(name='Phoenix', velocity=30.0, sum_fte_at_velocity=2.0,
                sprint_length=10,
                members=[Membership(person_name='Ada'),
                         Membership(person_name='Bo', fte=0.5)])
    _available([team]).check_consistency(NoTextIO())


def test_unknown_person() -> None:
    """Test a membership referencing an unknown person is a KeyError."""
    team = Team(name='Phoenix', velocity=1.0, sum_fte_at_velocity=1.0,
                sprint_length=10, members=[Membership(person_name='Cory')])
    with pytest.raises(KeyError):
        _available([team]).check_consistency(NoTextIO())


def test_person_ref_any_case() -> None:
    """Test the person reference is matched case-insensitively."""
    team = Team(name='Phoenix', velocity=1.0, sum_fte_at_velocity=1.0,
                sprint_length=10, members=[Membership(person_name='ADA')])
    _available([team]).check_consistency(NoTextIO())


def test_person_key_mismatch() -> None:
    """Test a registry key not matching the person name is a ValueError."""
    workforce = AvailableTeams(persons={'wrong': Person(name='Ada')}, teams=[])
    with pytest.raises(ValueError):
        workforce.check_consistency(NoTextIO())


def test_empty_person_name() -> None:
    """Test a person with an empty name is reported as a ValueError."""
    workforce = AvailableTeams(persons={'': Person(name='')}, teams=[])
    with pytest.raises(ValueError):
        workforce.check_consistency(NoTextIO())


def test_empty_team_alias() -> None:
    """Test an empty team alias is reported as a ValueError."""
    team = Team(name='Phoenix', velocity=1.0, sum_fte_at_velocity=1.0,
                sprint_length=10, aliases=[''])
    with pytest.raises(ValueError):
        _available([team]).check_consistency(NoTextIO())


@pytest.mark.parametrize('second_name', ['Phoenix', 'phoenix', 'PHX'])
def test_duplicate_team_label(second_name: str) -> None:
    """Test a duplicate team name or alias (any case) is a ValueError."""
    first = Team(name='Phoenix', velocity=1.0, sum_fte_at_velocity=1.0,
                 sprint_length=10, aliases=['PHX'])
    second = Team(name=second_name, velocity=1.0, sum_fte_at_velocity=1.0,
                  sprint_length=10)
    with pytest.raises(ValueError):
        _available([first, second]).check_consistency(NoTextIO())


def test_person_exc_overlap() -> None:
    """Test overlapping personal work hour exceptions are reported."""
    person = Person(name='Ada', exceptions=[
        ExceptionWorkHours(date(2026, 1, 1), date(2026, 2, 1), 0.0),
        ExceptionWorkHours(date(2026, 2, 1), date(2026, 3, 1), 0.0)])
    workforce = AvailableTeams(persons={'ada': person}, teams=[])
    with pytest.raises(ValueError):
        workforce.check_consistency(NoTextIO())


def test_over_allocated() -> None:
    """Test a person allocated more than 1.0 FTE in total is reported."""
    team_a = Team(name='Alpha', velocity=1.0, sum_fte_at_velocity=1.0,
                  sprint_length=10,
                  members=[Membership(person_name='Ada', fte=0.6)])
    team_b = Team(name='Beta', velocity=1.0, sum_fte_at_velocity=1.0,
                  sprint_length=10,
                  members=[Membership(person_name='Ada', fte=0.6)])
    with pytest.raises(ValueError):
        _available([team_a, team_b]).check_consistency(NoTextIO())


def test_split_allocation_ok() -> None:
    """Test a person split half and half across two teams passes."""
    team_a = Team(name='Alpha', velocity=1.0, sum_fte_at_velocity=1.0,
                  sprint_length=10,
                  members=[Membership(person_name='Ada', fte=0.5)])
    team_b = Team(name='Beta', velocity=1.0, sum_fte_at_velocity=1.0,
                  sprint_length=10,
                  members=[Membership(person_name='Ada', fte=0.5)])
    _available([team_a, team_b]).check_consistency(NoTextIO())


def test_moving_team_ok() -> None:
    """Test a person moving full time between teams is not over-allocated."""
    team_a = Team(name='Alpha', velocity=1.0, sum_fte_at_velocity=1.0,
                  sprint_length=10,
                  members=[Membership(person_name='Ada',
                                      end_date=date(2026, 6, 30))])
    team_b = Team(name='Beta', velocity=1.0, sum_fte_at_velocity=1.0,
                  sprint_length=10,
                  members=[Membership(person_name='Ada',
                                      start_date=date(2026, 7, 1))])
    _available([team_a, team_b]).check_consistency(NoTextIO())


def test_fte_on_outside() -> None:
    """Test a day outside the membership range gives zero."""
    membership = Membership(person_name='Ada', fte=1.0,
                            start_date=date(2026, 2, 1),
                            end_date=date(2026, 2, 28))
    assert membership_fte_on(membership, date(2026, 1, 1)) == 0.0
    assert membership_fte_on(membership, date(2026, 2, 15)) == 1.0


def test_fte_on_exception() -> None:
    """Test an fte_exception overrides the base full-time equivalent."""
    membership = Membership(person_name='Ada', fte=1.0, fte_exceptions=[
        FteException(date(2026, 2, 1), date(2026, 2, 28), 0.25)])
    assert membership_fte_on(membership, date(2026, 2, 10)) == 0.25
    assert membership_fte_on(membership, date(2026, 3, 10)) == 1.0


def test_candidate_days_open() -> None:
    """Test fully open memberships fall back to a single day."""
    assert candidate_days([Membership(person_name='Ada')]) == {date.min}


def test_person_exc_message() -> None:
    """Test a person's bad exception range names the exception."""
    person = Person(name='Ada', exceptions=[
        ExceptionWorkHours(date(2026, 2, 1), date(2026, 1, 1), 0.0)])
    workforce = AvailableTeams(persons={'ada': person}, teams=[])
    err = StringIO()
    with pytest.raises(ValueError):
        workforce.check_consistency(err)
    message = err.getvalue()
    assert 'Work hours exception' in message
    assert 'Backlog item' not in message
    assert 'start_date is after end_date' in message


def test_unknown_ref_message() -> None:
    """Test an unknown person reference names the team and the key."""
    team = Team(name='Phoenix', velocity=1.0, sum_fte_at_velocity=1.0,
                sprint_length=10, members=[Membership(person_name='Cory')])
    err = StringIO()
    with pytest.raises(KeyError):
        _available([team]).check_consistency(err)
    message = err.getvalue()
    assert message.startswith("Team 'Phoenix' field 'person_name'")
    assert "'Cory'" in message
    assert 'Backlog item' not in message


def test_over_alloc_message() -> None:
    """Test the over-allocation message names the person and the day."""
    team_a = Team(name='Alpha', velocity=1.0, sum_fte_at_velocity=1.0,
                  sprint_length=10,
                  members=[Membership(person_name='Ada', fte=0.6)])
    team_b = Team(name='Beta', velocity=1.0, sum_fte_at_velocity=1.0,
                  sprint_length=10,
                  members=[Membership(person_name='Ada', fte=0.6)])
    err = StringIO()
    with pytest.raises(ValueError):
        _available([team_a, team_b]).check_consistency(err)
    message = err.getvalue()
    assert message.startswith("Person field 'fte'")
    assert "'ada'" in message
    assert 'more than 1.0' in message
    assert 'Backlog item' not in message
