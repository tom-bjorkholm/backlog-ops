#! /usr/local/bin/python3
"""Define a team."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass, field
from datetime import date
from backlogops.person import Person


@dataclass
class FteException:
    """Define a full-time equivalent exception.

    The full-time equivalent exception is used to override the default
    full-time equivalent for a specific period. This can be used to mark
    a learning period for a new team member, or a period of time when the
    team member work part-time outside of this team.
    """

    start_date: date
    end_date: date
    fte: float
    """The full-time equivalent of the team member."""


@dataclass
class TeamMember:
    """Define a team member."""

    person: Person
    """The person is the team member."""

    fte: float = 1.0
    """The full-time equivalent of the team member."""

    fte_exceptions: list[FteException] = field(default_factory=list)
    """The list of full-time equivalent exceptions for the team member.

    These exceptions are used to mark periods of time when the team member
    has a different full-time equivalent, compared to the default full-time
    equivalent. For instance, a team member may work part-time outside of this
    team, or a new team member may be learning the team's processes.
    """


@dataclass
class Team:
    """Define a team."""

    name: str
    """The name of the team. Case insensitive comparison. Must be unique."""

    velocity: float
    """The velocity of the team."""

    sum_fte_at_velocity: float
    """The sum of the full-time equivalents when velocity measured.

    This is the recorded sum of the full-time equivalents of the team
    members when velocity was measured. It is used to adjust the velocity
    if the team members have changed since the velocity was measured.
    """

    sprint_length: int
    """The length of the sprint in working days."""

    aliases: list[str] = field(default_factory=list)
    """The aliases for the team.

    A backlog might refer to the team using the team name or an alias.
    Case insensitive comparison. Each alias must be unique."""

    members: list[TeamMember] = field(default_factory=list)
    """The list of team members."""
