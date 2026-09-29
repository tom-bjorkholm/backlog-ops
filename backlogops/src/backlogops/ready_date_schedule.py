#! /usr/local/bin/python3
"""Schedule the work on backlog items onto the teams, day by day.

The ready date of a backlog item can be estimated from story points or
from remaining time. Both are the same schedule: the items are worked in
backlog order, each by one team, and a team completes a certain amount
of work on each calendar day. Only the unit of the work differs, so the
estimators describe it with a :class:`WorkModel` and share
:func:`schedule_ready_dates`.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass, replace
from datetime import date, timedelta
from typing import Callable, Optional, TextIO
from backlogops.backlog import Backlog, BacklogItem, Status
from backlogops.available_teams import AvailableTeams, membership_fte_on
from backlogops.person import Person
from backlogops.team import Team
from backlogops.work_hours import CompanyWorkHours, ExceptionWorkHours, WeekDay

_ONE_DAY = timedelta(days=1)
"""One calendar day, the step used when working through a schedule."""

_HORIZON = timedelta(days=366 * 100)
"""How far ahead work is followed before it counts as never finished."""

_EPSILON = 1e-9
"""Tolerance for treating accumulated work as fully done."""


def _week_day(day: date) -> WeekDay:
    """Return the WeekDay value of a calendar day (Monday is first)."""
    return WeekDay(day.weekday() + 1)


def _exception_on(exceptions: list[ExceptionWorkHours],
                  day: date) -> Optional[ExceptionWorkHours]:
    """Return the work-hours exception covering a day, or None.

    The exceptions in one list do not overlap, so at most one of them
    covers any given day.
    """
    for exception in exceptions:
        if exception.start_date <= day <= exception.end_date:
            return exception
    return None


def _apply_exception(base: float, exception: ExceptionWorkHours) -> float:
    """Return the work hours after applying an exception to a baseline.

    On a day that is closed in the baseline the exception only adds
    hours when its new_work_days flag is set; otherwise the closed day
    stays closed.
    """
    if base > 0.0 or exception.new_work_days:
        return exception.hours_per_day
    return base


def _scheduled_hours(company: CompanyWorkHours, day: date) -> float:
    """Return the company work hours on a day, with company exceptions."""
    base = company.work_hours.get(_week_day(day), 0.0)
    exception = _exception_on(company.exceptions, day)
    if exception is None:
        return base
    return _apply_exception(base, exception)


def _person_hours(person: Person, company: CompanyWorkHours,
                  day: date) -> float:
    """Return the work hours of one person on a day.

    The company schedule, including the company exceptions, is the
    person's baseline. A personal work-hours exception overrides that
    baseline, modelling vacation, part-time or ordered over-time.
    """
    base = _scheduled_hours(company, day)
    exception = _exception_on(person.exceptions, day)
    if exception is None:
        return base
    return _apply_exception(base, exception)


def team_hours(teams: AvailableTeams, team: Team, day: date) -> float:
    """Return the person work hours a team has on one day.

    Each member contributes the hours the person works that day, scaled
    by the full-time equivalent the person gives the team that day.
    Weekends, holidays and vacation make a member contribute nothing, and
    a member who is not a known person contributes nothing either.

    Args:
        teams: The workforce holding the persons and the company hours.
        team: The team to sum the hours of.
        day: The calendar day.

    Returns:
        The summed person work hours, which is never negative.
    """
    company = teams.company_work_hours
    total = 0.0
    for member in team.members:
        person = teams.persons.get(member.person_name.lower())
        if person is None:
            continue
        fte = membership_fte_on(member, day)
        if fte <= 0.0:
            continue
        total += fte * _person_hours(person, company, day)
    return total


@dataclass(frozen=True)
class WorkModel:
    """How much work each backlog item is and how fast the teams work.

    Fields:
        work: The work still to do on each backlog item, by item key, in
            the unit of the capacity. It is never negative, and an item
            whose key is missing is no work.
        capacity: Return the work a team completes on one calendar day,
            in the unit of the work. It is never negative.
    """

    work: dict[str, float]
    capacity: Callable[[Team, date], float]


@dataclass(frozen=True, order=True)
class _Cursor:
    """A team's progress: the day it works and the work done that day.

    Keeping the work already done on the current day lets a team finish
    several small items on the same day instead of losing the rest of the
    day to one item. Cursors order by day and then by the work done, so a
    smaller cursor is the team that is free earlier.
    """

    day: date
    used: float


@dataclass
class _Estimator:
    """Assign teams to backlog items and date the team's own work.

    The estimator keeps, for each team, a cursor with the day and the
    work done that day. It dates the work a team itself does on an item;
    lifting a parent's date to its children is done afterwards by
    :class:`_ParentRollup`.
    """

    teams: list[Team]
    model: WorkModel
    cursor: dict[str, _Cursor]
    by_label: dict[str, Team]
    stderr_file: TextIO

    @staticmethod
    def create(teams: AvailableTeams, start: date, stderr_file: TextIO,
               model: WorkModel) -> '_Estimator':
        """Create an estimator with every team free on the start date."""
        cursor = {team.name: _Cursor(start, 0.0) for team in teams.teams}
        by_label: dict[str, Team] = {}
        for team in teams.teams:
            for label in [team.name, *team.aliases]:
                by_label[label.lower()] = team
        return _Estimator(teams.teams, model, cursor, by_label, stderr_file)

    def _warn(self, item: BacklogItem, reason: str) -> None:
        """Report that an item cannot be dated and why."""
        print(f'Cannot estimate {item.key!r}: {reason}', file=self.stderr_file)

    def _earliest_team(self) -> Optional[Team]:
        """Return the team that becomes free earliest, or None."""
        if not self.teams:
            return None
        return min(self.teams, key=lambda team: self.cursor[team.name])

    def _team_for(self, item: BacklogItem) -> Optional[Team]:
        """Return the team that works the item, or None when unknown."""
        if item.team is None:
            team = self._earliest_team()
            if team is None:
                self._warn(item, 'no team is available')
            return team
        team = self.by_label.get(item.team.lower())
        if team is None:
            self._warn(item, f'team {item.team!r} is not in the workforce')
        return team

    def _advance(self, team: Team, work: float,
                 cursor: _Cursor) -> Optional[tuple[date, _Cursor]]:
        """Return the ready date and new cursor after doing some work.

        The team works from the cursor, which is the day it is on and
        the work already done on that day, so the day's leftover capacity
        carries to the next item and several small items can finish on
        the same day. The ready date is the day the work is finished. No
        work is ready at the cursor day and leaves the cursor unchanged.
        None is returned when the work does not finish within the
        horizon, which means the team has no capacity for it.
        """
        if work <= 0.0:
            return cursor.day, cursor
        remaining = work
        day, used = cursor.day, cursor.used
        limit = day + _HORIZON
        while day <= limit:
            available = self.model.capacity(team, day) - used
            if available > 0.0:
                if remaining <= available + _EPSILON:
                    return day, _Cursor(day, used + remaining)
                remaining -= available
            day += _ONE_DAY
            used = 0.0
        return None

    def own_date(self, item: BacklogItem) -> Optional[date]:
        """Return the date the team finishes the item's own work.

        Done and rejected items consume no team time and get no date.
        Other items are worked by their assigned team, or by the team
        that is free earliest, from where that team's cursor stands, for
        the work the work model gives the item. When the team has no
        capacity for the item, or no team is available, the item gets no
        date and a warning is reported.
        """
        if item.status in (Status.DONE, Status.REJECTED):
            return None
        team = self._team_for(item)
        if team is None:
            return None
        work = self.model.work.get(item.key, 0.0)
        result = self._advance(team, work, self.cursor[team.name])
        if result is None:
            self._warn(item, f'team {team.name!r} has no capacity for it')
            return None
        ready, moved = result
        self.cursor[team.name] = moved
        return ready


@dataclass
class _ParentRollup:
    """Lift each parent's date to be no earlier than its children.

    A parent cannot be ready before its latest child, even though the
    work on the parent itself may be scheduled earlier. The effective
    date of an item is therefore the latest of its own date and the
    effective dates of its children, found recursively. Done and
    rejected items keep no date and never delay their parent.
    """

    children: dict[str, list[str]]
    own: dict[str, Optional[date]]
    status: dict[str, Status]
    memo: dict[str, Optional[date]]
    active: set[str]

    @staticmethod
    def create(backlog: Backlog, own: dict[str, Optional[date]],
               status: dict[str, Status]) -> '_ParentRollup':
        """Create a rollup, grouping the item keys by their parent key."""
        children: dict[str, list[str]] = {}
        for item in backlog:
            if item.parent_key is not None:
                children.setdefault(item.parent_key, []).append(item.key)
        return _ParentRollup(children, own, status, {}, set())

    def effective(self, key: str) -> Optional[date]:
        """Return the effective ready date of one item key."""
        if key in self.memo:
            return self.memo[key]
        if self.status.get(key) in (Status.DONE, Status.REJECTED):
            self.memo[key] = None
            return None
        if key in self.active:
            return self.own.get(key)
        self.active.add(key)
        dates = [self.own.get(key)]
        dates += [self.effective(child)
                  for child in self.children.get(key, [])]
        self.active.discard(key)
        known = [day for day in dates if day is not None]
        result = max(known) if known else None
        self.memo[key] = result
        return result


def schedule_ready_dates(backlog: Backlog, available_teams: AvailableTeams,
                         start: date, stderr_file: TextIO,
                         model: WorkModel) -> Backlog:
    """Return the backlog with ready dates from scheduling its work.

    The backlog items are worked in their given order, from the start
    date. Each item is worked by its assigned team, or, when it names no
    team, by the team that becomes free earliest. Only one team works an
    item, and a team works one item at a time. When a team's capacity on
    a day covers more than one item, several items finish on the same
    day. A parent's date is lifted to be no earlier than its latest
    child's, and done and rejected items get no date. An item that
    cannot be dated gets no date and a warning.

    Args:
        backlog: The backlog to date. The argument is not modified.
        available_teams: The teams that work the backlog.
        start: The day the teams start working.
        stderr_file: The file to report warnings to.
        model: The work of each item and the daily capacity of a team.

    Returns:
        A new backlog whose items carry the estimated ready date. The
        other fields are copied unchanged from the given items.
    """
    estimator = _Estimator.create(available_teams, start, stderr_file, model)
    own = {item.key: estimator.own_date(item) for item in backlog}
    status = {item.key: item.status for item in backlog}
    rollup = _ParentRollup.create(backlog, own, status)
    return [replace(item, estimated_ready_date=rollup.effective(item.key))
            for item in backlog]
