#! /usr/local/bin/python3
"""Define the available workforce: persons and teams."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import TextIO
from backlogops.backlog_helpers import check_field_types, report_bad_value
from backlogops.backlog_helpers import report_unknown_reference
from backlogops.date_ranges import check_no_overlap
from backlogops.person import Person
from backlogops.team import Membership, Team
from backlogops.work_hours import CompanyWorkHours


def membership_fte_on(membership: Membership, day: date) -> float:
    """Return the full-time equivalent of a membership on a given day.

    Days outside the membership date range give 0.0. A day covered by an
    fte_exception gives that exception's full-time equivalent. Otherwise
    the membership's base full-time equivalent applies.

    Args:
        membership: The membership to evaluate.
        day: The day to evaluate the membership on.

    Returns:
        The full-time equivalent the person gives to the team on the day.
    """
    if membership.start_date is not None and day < membership.start_date:
        return 0.0
    if membership.end_date is not None and day > membership.end_date:
        return 0.0
    for exception in membership.fte_exceptions:
        if exception.start_date <= day <= exception.end_date:
            return exception.fte
    return membership.fte


def candidate_days(memberships: list[Membership]) -> set[date]:
    """Return the days where the summed full-time equivalent can change.

    The summed full-time equivalent is constant between the start and end
    boundaries of the memberships and their fte_exceptions, so checking
    those boundary days is enough to find its maximum. When there are no
    boundaries (all memberships are fully open) a single day is returned,
    on which every membership contributes its base full-time equivalent.

    Args:
        memberships: The memberships of one person across all teams.

    Returns:
        The set of days on which to evaluate the summed full-time
        equivalent.
    """
    days: set[date] = set()
    for membership in memberships:
        if membership.start_date is not None:
            days.add(membership.start_date)
        if membership.end_date is not None:
            days.add(membership.end_date + timedelta(days=1))
        for exception in membership.fte_exceptions:
            days.add(exception.start_date)
            days.add(exception.end_date + timedelta(days=1))
    return days or {date.min}


def check_person_capacity(person_name: str, memberships: list[Membership],
                          stderr_file: TextIO = sys.stderr) -> None:
    """Check a person is not allocated more than full time on any day.

    The summed full-time equivalent over all of the person's memberships
    is evaluated on every boundary day and must not exceed 1.0.

    Args:
        person_name: The name of the person, for error messages.
        memberships: The memberships of the person across all teams.
        stderr_file: The file to report errors to.

    Raises:
        ValueError: If the summed full-time equivalent exceeds 1.0 on any
            day.
    """
    for day in candidate_days(memberships):
        total: float = sum((membership_fte_on(m, day) for m in memberships),
                           0.0)
        if total > 1.0 + 1e-9:
            report_bad_value('fte', total,
                             f'person {person_name!r} is allocated {total} '
                             f'FTE (more than 1.0) on {day.isoformat()}',
                             stderr_file, 'Person')


@dataclass
class AvailableTeams:
    """Define the available workforce that can do work.

    The persons registry holds every person once, keyed by the lower-case
    person name, so that personal availability is entered in a single
    place. Teams reference their members by person name into this
    registry. This lets a person move between teams or split time across
    teams without duplicating the person.

    Fields:
        persons: The registry of persons, keyed by lower-case person name.
        teams: The list of teams that are available to do work.
        company_work_hours: The company work hours that apply to everyone.
    """

    persons: dict[str, Person]
    teams: list[Team]
    company_work_hours: CompanyWorkHours = field(
        default_factory=CompanyWorkHours)

    def _check_persons(self, stderr_file: TextIO) -> None:
        """Check each person's key, name and work hour exceptions."""
        for key, person in self.persons.items():
            check_field_types(person, stderr_file, 'Person')
            if person.name == '':
                report_bad_value('name', person.name, 'must not be empty',
                                 stderr_file, 'Person')
            if key != person.name.lower():
                report_bad_value('persons', key,
                                 f'key does not match person name '
                                 f'{person.name!r}', stderr_file,
                                 'Available teams')
            for exception in person.exceptions:
                exception.check_consistency(stderr_file)
            check_no_overlap('exceptions',
                             [(e.start_date, e.end_date)
                              for e in person.exceptions], stderr_file,
                             'Person')

    def _add_team_label(self, label: str, seen_labels: dict[str, str],
                        stderr_file: TextIO) -> None:
        """Add one team label and reject a case-insensitive duplicate."""
        if label == '':
            report_bad_value('aliases', label, 'must not be empty',
                             stderr_file, 'Team')
        lowered = label.lower()
        if lowered in seen_labels:
            report_bad_value('name', label,
                             f'duplicates team label '
                             f'{seen_labels[lowered]!r} (case-insensitive)',
                             stderr_file, 'Team')
        seen_labels[lowered] = label

    def _check_teams(self, stderr_file: TextIO) -> None:
        """Check every team and that names and aliases are unique."""
        seen_labels: dict[str, str] = {}
        for team in self.teams:
            team.check_consistency(stderr_file)
            for label in [team.name, *team.aliases]:
                self._add_team_label(label, seen_labels, stderr_file)

    def _check_member_refs(self, stderr_file: TextIO) -> None:
        """Check each membership references a known person."""
        for team in self.teams:
            for member in team.members:
                if member.person_name.lower() not in self.persons:
                    report_unknown_reference('person_name', team.name,
                                             member.person_name, stderr_file,
                                             'Team')

    def _memberships_by_person(self) -> dict[str, list[Membership]]:
        """Group memberships across all teams by lower-case person name."""
        result: dict[str, list[Membership]] = {}
        for team in self.teams:
            for member in team.members:
                key = member.person_name.lower()
                result.setdefault(key, []).append(member)
        return result

    def _check_capacity(self, stderr_file: TextIO) -> None:
        """Check no person is allocated more than full time on any day."""
        for person_name, memberships in self._memberships_by_person().items():
            check_person_capacity(person_name, memberships, stderr_file)

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the consistency of the available workforce.

        Field types are verified, the company work hours and every person
        and team are checked, team names and aliases are checked to be
        unique case-insensitively across all teams, every membership is
        checked to reference a known person, and no person is allocated
        more than full time on any day.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If a field value violates a constraint, if team
                labels are not unique, or if a person is over-allocated.
            KeyError: If a membership references an unknown person.
        """
        check_field_types(self, stderr_file, 'Available teams')
        self.company_work_hours.check_consistency(stderr_file)
        self._check_persons(stderr_file)
        self._check_teams(stderr_file)
        self._check_member_refs(stderr_file)
        self._check_capacity(stderr_file)
