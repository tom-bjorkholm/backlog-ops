#! /usr/local/bin/python3
"""Estimate the ready date of backlog items."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from dataclasses import dataclass, replace
from datetime import date, timedelta
from typing import Optional, TextIO
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
"""Tolerance for treating accumulated story points as fully done."""


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


@dataclass(frozen=True, order=True)
class _Cursor:
    """A team's progress: the day it works and points spent that day.

    Keeping the points already spent on the current day lets a team
    finish several small items on the same day instead of losing the
    rest of the day to one item. Cursors order by day and then by spent
    points, so a smaller cursor is the team that is free earlier.
    """

    day: date
    used: float


@dataclass(frozen=True)
class _Workforce:
    """The workforce together with the length of a full work day.

    The standard work day is the longest day in the company weekly
    schedule. It is the reference a person's actual work hours are
    measured against, so that a normal full day counts as one full-time
    equivalent, a half day as one half, and ordered over-time as more.
    """

    teams: AvailableTeams
    standard_hours: float

    @staticmethod
    def create(teams: AvailableTeams) -> '_Workforce':
        """Create a workforce, deriving the standard full work day."""
        hours = teams.company_work_hours.work_hours.values()
        return _Workforce(teams, max(hours, default=0.0))

    def _team_fte(self, team: Team, day: date) -> float:
        """Return the team's effective full-time equivalent on a day.

        Each member contributes the full-time equivalent it gives the
        team that day, scaled by how much of a standard work day the
        person actually works. Weekends, holidays and vacation make a
        member contribute nothing.
        """
        if self.standard_hours <= 0.0:
            return 0.0
        company = self.teams.company_work_hours
        total = 0.0
        for member in team.members:
            person = self.teams.persons.get(member.person_name.lower())
            if person is None:
                continue
            fte = membership_fte_on(member, day)
            if fte <= 0.0:
                continue
            hours = _person_hours(person, company, day)
            total += fte * hours / self.standard_hours
        return total

    def points_on(self, team: Team, day: date) -> float:
        """Return the story points the team completes on one day.

        The team velocity is the story points done in one sprint at the
        recorded summed full-time equivalent. It is rescaled by the
        team's effective full-time equivalent on the day and spread over
        the working days of a sprint.
        """
        if team.sprint_length <= 0 or team.sum_fte_at_velocity <= 0.0:
            return 0.0
        per_day = team.velocity / team.sprint_length
        return per_day * self._team_fte(team, day) / team.sum_fte_at_velocity

    def advance(self, team: Team, points: int,
                cursor: _Cursor) -> Optional[tuple[date, _Cursor]]:
        """Return the ready date and new cursor after doing some work.

        The team works from the cursor, which is the day it is on and
        the story points already spent on that day, so the day's leftover
        capacity carries to the next item and several small items can
        finish on the same day. The ready date is the day the work is
        finished. Work with no story points is ready at the cursor day
        and leaves the cursor unchanged. None is returned when the work
        does not finish within the horizon, which means the team has no
        capacity for it.
        """
        if points <= 0:
            return cursor.day, cursor
        remaining = float(points)
        day, used = cursor.day, cursor.used
        limit = day + _HORIZON
        while day <= limit:
            available = self.points_on(team, day) - used
            if available > 0.0:
                if remaining <= available + _EPSILON:
                    return day, _Cursor(day, used + remaining)
                remaining -= available
            day += _ONE_DAY
            used = 0.0
        return None


@dataclass
class _Estimator:
    """Assign teams to backlog items and date the team's own work.

    The estimator keeps, for each team, a cursor with the day and the
    points spent that day. It dates the work a team itself does on an
    item; lifting a parent's date to its children is done afterwards by
    :class:`_ParentRollup`.
    """

    workforce: _Workforce
    cursor: dict[str, _Cursor]
    by_label: dict[str, Team]
    stderr_file: TextIO

    @staticmethod
    def create(teams: AvailableTeams, start: date,
               stderr_file: TextIO) -> '_Estimator':
        """Create an estimator with every team free on the start date."""
        cursor = {team.name: _Cursor(start, 0.0) for team in teams.teams}
        by_label: dict[str, Team] = {}
        for team in teams.teams:
            for label in [team.name, *team.aliases]:
                by_label[label.lower()] = team
        return _Estimator(_Workforce.create(teams), cursor, by_label,
                          stderr_file)

    def _warn(self, item: BacklogItem, reason: str) -> None:
        """Report that an item cannot be dated and why."""
        print(f'Cannot estimate {item.key!r}: {reason}', file=self.stderr_file)

    def _earliest_team(self) -> Optional[Team]:
        """Return the team that becomes free earliest, or None."""
        teams = self.workforce.teams.teams
        if not teams:
            return None
        best = teams[0]
        for team in teams[1:]:
            if self.cursor[team.name] < self.cursor[best.name]:
                best = team
        return best

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

    def own_date(self, item: BacklogItem) -> Optional[date]:
        """Return the date the team finishes the item's own work.

        Done and rejected items consume no team time and get no date.
        Other items are worked by their assigned team, or by the team
        that is free earliest, from where that team's cursor stands. When
        the team has no capacity for the item, or no team is available,
        the item gets no date and a warning is reported.
        """
        if item.status in (Status.DONE, Status.REJECTED):
            return None
        team = self._team_for(item)
        if team is None:
            return None
        position = self.cursor[team.name]
        result = self.workforce.advance(team, item.story_points, position)
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


def estimate_ready_date(backlog: Backlog, available_teams: AvailableTeams,
                        start_date: Optional[date] = None,
                        stderr_file: TextIO = sys.stderr) -> Backlog:
    """Estimate the ready date of backlog items.

    The teams start working on the start date, which defaults to today
    when None is given. The backlog items are worked in their given
    order. Each item is worked by its assigned team, or, when it names
    no team, by the team that becomes free earliest. Only one team works
    an item, and a team works one item at a time, in backlog order. When
    a team's daily capacity covers more than one item, several items
    finish on the same day, and the next item carries on from the
    leftover capacity of the day the current one finished.

    The story points an item still needs are turned into calendar time
    from the team's velocity, rescaled by the team's effective capacity
    on each day. That capacity follows every member's full-time
    equivalent and actual work hours, so weekends, company holidays,
    personal vacation, learning periods and ordered over-time all change
    the pace. A standard work day is the longest day in the company
    weekly schedule. The story points of TODO and IN_PROGRESS items are
    all treated as still left to do; DONE and REJECTED items need no work
    and get no estimated date. See also the Status enum.

    A parent's estimated date is lifted to be no earlier than its latest
    child's, applied through the whole hierarchy, because a parent cannot
    be ready before its children even though work on the parent itself
    may be scheduled earlier. A finished child does not delay its parent.

    Dependencies between items are not considered; the backlog is assumed
    to be ordered so that the teams can work the items in order. When an
    item names a team that is not in the workforce, when no team is
    available, or when the chosen team has no capacity for the item, the
    item gets no estimated date and a warning is reported.

    Args:
        backlog: The backlog to estimate the ready date of. The argument
                 is not modified. The backlog must be ordered so that the
                 teams can work the items in order.
        available_teams: The available teams used to estimate the ready
                         date, including absence, velocity and work hours.
        start_date: The day the teams start working, or None for today.
        stderr_file: The file to report warnings to.

    Returns:
        A new backlog whose items carry the estimated ready date. The
        other fields are copied unchanged from the given items.
    """
    start = date.today() if start_date is None else start_date
    estimator = _Estimator.create(available_teams, start, stderr_file)
    own = {item.key: estimator.own_date(item) for item in backlog}
    status = {item.key: item.status for item in backlog}
    rollup = _ParentRollup.create(backlog, own, status)
    return [replace(item, estimated_ready_date=rollup.effective(item.key))
            for item in backlog]


def set_plan_from_estimate(backlog: Backlog,
                           stderr_file: TextIO = sys.stderr) -> Backlog:
    """Set the planned ready dates from the estimated ready dates.

    For each backlog item the planned ready date is set to the estimated
    ready date, copying None when the estimated ready date is None.

    Args:
        backlog: The backlog to set the planned ready dates of. The
                 argument is not modified.
        stderr_file: The file to report errors to.

    Returns:
        A new backlog whose items carry the planned ready date taken from
        the estimated ready date. The other fields are copied unchanged.
    """
    _ = stderr_file
    return [replace(item, planned_ready_date=item.estimated_ready_date)
            for item in backlog]
