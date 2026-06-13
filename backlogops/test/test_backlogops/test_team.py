#! /usr/local/bin/python3
"""Tests for teams, memberships and full-time equivalent exceptions."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from io import StringIO

import pytest

from backlogops.team import FteException, Membership, Team
from backlogops.no_text_io import NoTextIO


def _team() -> Team:
    """Return a valid team with one full-time member."""
    return Team(name='Phoenix', velocity=30.0, sum_fte_at_velocity=3.0,
                sprint_length=10, aliases=['PHX'],
                members=[Membership(person_name='Ada')])


def test_fte_exception_ok() -> None:
    """Test a valid full-time equivalent exception passes."""
    FteException(start_date=date(2026, 1, 1), end_date=date(2026, 1, 31),
                 fte=0.5).check_consistency(NoTextIO())


def test_fte_exc_negative() -> None:
    """Test a negative full-time equivalent is a ValueError."""
    exception = FteException(start_date=date(2026, 1, 1),
                             end_date=date(2026, 1, 31), fte=-0.5)
    with pytest.raises(ValueError):
        exception.check_consistency(NoTextIO())


def test_membership_ok() -> None:
    """Test a valid membership passes its consistency check."""
    Membership(person_name='Ada', fte=0.5, start_date=date(2026, 1, 1),
               end_date=date(2026, 6, 30)).check_consistency(NoTextIO())


def test_member_empty_name() -> None:
    """Test an empty person name is a ValueError."""
    with pytest.raises(ValueError):
        Membership(person_name='').check_consistency(NoTextIO())


def test_member_neg_fte() -> None:
    """Test a negative full-time equivalent is a ValueError."""
    with pytest.raises(ValueError):
        Membership(person_name='Ada', fte=-1.0).check_consistency(NoTextIO())


def test_membership_bad_range() -> None:
    """Test a membership with start after end is a ValueError."""
    membership = Membership(person_name='Ada', start_date=date(2026, 6, 30),
                            end_date=date(2026, 1, 1))
    with pytest.raises(ValueError):
        membership.check_consistency(NoTextIO())


def test_member_exc_overlap() -> None:
    """Test overlapping full-time equivalent exceptions are reported."""
    first = FteException(start_date=date(2026, 1, 1),
                         end_date=date(2026, 2, 1), fte=0.5)
    second = FteException(start_date=date(2026, 2, 1),
                          end_date=date(2026, 3, 1), fte=0.5)
    membership = Membership(person_name='Ada', fte_exceptions=[first, second])
    with pytest.raises(ValueError):
        membership.check_consistency(NoTextIO())


def test_team_ok() -> None:
    """Test a valid team passes its consistency check."""
    _team().check_consistency(NoTextIO())


def test_team_empty_name() -> None:
    """Test an empty team name is a ValueError."""
    team = _team()
    team.name = ''
    with pytest.raises(ValueError):
        team.check_consistency(NoTextIO())


@pytest.mark.parametrize('field_name, value', [
    ('velocity', -1.0), ('sum_fte_at_velocity', 0.0),
    ('sprint_length', 0)])
def test_team_bad_numbers(field_name: str, value: float) -> None:
    """Test out-of-range numeric team fields are a ValueError."""
    team = _team()
    setattr(team, field_name, value)
    with pytest.raises(ValueError):
        team.check_consistency(NoTextIO())


def test_sprint_bad_type() -> None:
    """Test a non-integer sprint length is reported as a TypeError."""
    team = _team()
    team.sprint_length = 10.0  # type: ignore[assignment]
    with pytest.raises(TypeError):
        team.check_consistency(NoTextIO())


def test_team_message() -> None:
    """Test a bad team value names the team, not a backlog item."""
    err = StringIO()
    team = _team()
    team.velocity = -1.0
    with pytest.raises(ValueError):
        team.check_consistency(err)
    message = err.getvalue()
    assert message.startswith("Team field 'velocity'")
    assert 'Backlog item' not in message


def test_member_message() -> None:
    """Test a membership error names the membership."""
    err = StringIO()
    with pytest.raises(ValueError):
        Membership(person_name='').check_consistency(err)
    message = err.getvalue()
    assert message.startswith("Membership field 'person_name'")
    assert 'Backlog item' not in message
