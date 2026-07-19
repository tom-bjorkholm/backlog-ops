#! /usr/local/bin/python3
"""Define a team, its memberships and their availability over time."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, TextIO
from backlogops.backlog_helpers import check_field_types, report_bad_value
from backlogops.date_ranges import check_date_range, check_no_overlap


@dataclass
class FteException:
    """Define a full-time equivalent exception.

    The full-time equivalent exception is used to override the default
    full-time equivalent for a specific period. This can be used to mark
    a learning period for a new team member, or a period of time when the
    team member works part-time outside of this team.

    Fields:
        start_date: The first day of the exception (inclusive).
        end_date: The last day of the exception (inclusive). Must not be
                  before start_date.
        fte: The full-time equivalent during the exception. Must not be
             negative.
    """

    start_date: date
    end_date: date
    fte: float

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the consistency of the full-time equivalent exception.

        Field types are verified, the date range must be non-empty, and
        the full-time equivalent must not be negative.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If the range is empty or the fte is negative.
        """
        check_field_types(self, stderr_file, 'FTE exception')
        check_date_range('fte exception', self.start_date, self.end_date,
                         stderr_file, 'FTE exception')
        if self.fte < 0.0:
            report_bad_value('fte', self.fte, 'must not be negative',
                             stderr_file, 'FTE exception')


@dataclass
class Membership:
    """Define how a person belongs to a team over a period of time.

    A membership links a person, by name, to the team that holds it. The
    person name is looked up in the central person registry of
    :class:`~backlogops.available_teams.AvailableTeams`. A person may have
    several memberships, in the same or in different teams, which models a
    person moving between teams or splitting time across teams over time.

    Fields:
        person_name: The name of the person, used as a key into the
                     person registry. Compared case-insensitively. Must
                     not be empty.
        fte: The full-time equivalent the person gives to this team
             outside of any fte_exceptions. 1.0 means full time. Must not
             be negative.
        start_date: The first day of the membership (inclusive), or None
                    for a membership that is open at the start.
        end_date: The last day of the membership (inclusive), or None for
                  a membership that is open at the end.
        fte_exceptions: Periods with a full-time equivalent that differs
                        from fte, for example a learning period or a period
                        of part-time work in another team. The periods must
                        not overlap.
    """

    person_name: str
    fte: float = 1.0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    fte_exceptions: list[FteException] = field(default_factory=list)

    def _check_values(self, stderr_file: TextIO) -> None:
        """Check the person name, full-time equivalent and date range."""
        if self.person_name == '':
            report_bad_value('person_name', self.person_name,
                             'must not be empty', stderr_file, 'Membership')
        if self.fte < 0.0:
            report_bad_value('fte', self.fte, 'must not be negative',
                             stderr_file, 'Membership')
        if self.start_date is not None and self.end_date is not None:
            check_date_range('membership', self.start_date, self.end_date,
                             stderr_file, 'Membership')

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the consistency of the membership.

        Field types are verified, the person name must not be empty, the
        full-time equivalent must not be negative, the membership date
        range (when both ends are given) must be non-empty, every
        fte_exception must be consistent, and the fte_exceptions must not
        overlap.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If a value is invalid or two fte_exceptions
                overlap.
        """
        check_field_types(self, stderr_file, 'Membership')
        self._check_values(stderr_file)
        for exception in self.fte_exceptions:
            exception.check_consistency(stderr_file)
        check_no_overlap('fte_exceptions',
                         [(e.start_date, e.end_date)
                          for e in self.fte_exceptions], stderr_file,
                         'Membership')


@dataclass
class Team:
    """Define a team.

    Fields:
        name: The name of the team. Compared case-insensitively. Must be
              unique across all teams and must not be empty.
        velocity: The velocity of the team. Must not be negative.
        sum_fte_at_velocity: The sum of the full-time equivalents of the
                             team members when velocity was measured. Used
                             to rescale the velocity when the team capacity
                             changes. Must be positive.
        sprint_length: The length of the sprint counted in working days,
                       not calendar days. Must be positive.
        aliases: The aliases for the team. A backlog might refer to the
                 team using the team name or an alias. Compared
                 case-insensitively. Each alias must be unique and not
                 empty.
        members: The list of memberships of the team.
    """

    name: str
    velocity: float
    sum_fte_at_velocity: float
    sprint_length: int
    aliases: list[str] = field(default_factory=list)
    members: list[Membership] = field(default_factory=list)

    def _check_values(self, stderr_file: TextIO) -> None:
        """Check the name, velocity, capacity and sprint length."""
        if self.name == '':
            report_bad_value('name', self.name, 'must not be empty',
                             stderr_file, 'Team')
        if self.velocity < 0.0:
            report_bad_value('velocity', self.velocity, 'must not be negative',
                             stderr_file, 'Team')
        if self.sum_fte_at_velocity <= 0.0:
            report_bad_value('sum_fte_at_velocity', self.sum_fte_at_velocity,
                             'must be positive', stderr_file, 'Team')
        if self.sprint_length <= 0:
            report_bad_value('sprint_length', self.sprint_length,
                             'must be a positive number of working days',
                             stderr_file, 'Team')

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the consistency of the team.

        Field types are verified, the numeric fields must be within their
        documented ranges, and every membership must be consistent.
        Uniqueness of the name and aliases across teams is checked by
        :meth:`AvailableTeams.check_consistency`, not here.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If a field value violates a constraint.
        """
        check_field_types(self, stderr_file, 'Team')
        self._check_values(stderr_file)
        for member in self.members:
            member.check_consistency(stderr_file)
