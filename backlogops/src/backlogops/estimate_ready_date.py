#! /usr/local/bin/python3
"""Estimate the ready date of backlog items."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
import warnings
from dataclasses import replace
from datetime import date
from typing import Callable, Optional, TextIO
from backlogops.backlog import Backlog
from backlogops.available_teams import AvailableTeams
from backlogops.default_story_points import DefaultStoryPoints
from backlogops.ready_date_schedule import WorkModel, schedule_ready_dates, \
    team_hours
from backlogops.team import Team
from backlogops.use_story_points import find_keys_with_children, \
    use_story_points


def _points_per_day(teams: AvailableTeams) -> Callable[[Team, date], float]:
    """Return how many story points a team completes on one day.

    The team velocity is the story points done in one sprint at the
    recorded summed full-time equivalent. Because sprint_length is a
    count of working days (not calendar days) and a non-working day
    contributes no capacity, dividing the velocity by sprint_length gives
    the story points per working day. That daily rate is rescaled by the
    team's effective full-time equivalent on the day: its person work
    hours measured in standard work days. The standard work day is the
    longest day in the company weekly schedule, so that a normal full day
    counts as one full-time equivalent, a half day as one half, and
    ordered over-time as more.
    """
    standard = max(teams.company_work_hours.work_hours.values(), default=0.0)

    def points_on(team: Team, day: date) -> float:
        """Return the story points the team completes on the day."""
        if standard <= 0.0 or team.sprint_length <= 0 or \
                team.sum_fte_at_velocity <= 0.0:
            return 0.0
        per_day = team.velocity / team.sprint_length
        fte = team_hours(teams, team, day) / standard
        return per_day * fte / team.sum_fte_at_velocity
    return points_on


_NO_DEFAULTS = (
    'estimate_ready_date() without default_story_points is deprecated; '
    'pass the default_story_points of the configuration. Until it is '
    'passed, a backlog item that nobody has estimated is worked with no '
    'story points at all.')
"""What is said about an estimate that is given no default story points."""


def _defaults_or_warn(defaults: Optional[DefaultStoryPoints]
                      ) -> DefaultStoryPoints:
    """Return the given defaults, or empty ones with a deprecation.

    Args:
        defaults: What the caller passed, or None for the temporary
            backward-compatible behaviour.

    Returns:
        The defaults to guess with, which guess nothing when None was
        passed.
    """
    if defaults is not None:
        return defaults
    warnings.warn(_NO_DEFAULTS, DeprecationWarning, stacklevel=3)
    return DefaultStoryPoints()


def _points_of(backlog: Backlog,
               defaults: DefaultStoryPoints) -> dict[str, float]:
    """Return the story points to work each item with, by item key.

    The keys of the items that have children are found once for the
    whole backlog, so that pricing it is one pass over it.
    """
    with_children = find_keys_with_children(backlog)
    return {item.key: use_story_points(backlog, item, defaults, with_children)
            for item in backlog}


def estimate_ready_date(backlog: Backlog, available_teams: AvailableTeams,
                        start_date: Optional[date] = None,
                        stderr_file: TextIO = sys.stderr, *,
                        default_story_points: Optional[
                            DefaultStoryPoints] = None) -> Backlog:
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

    What an item that carries no story points of its own is worked with
    is decided by :func:`backlogops.use_story_points` from the given
    default story points: an item with children is a container and is no
    work of its own, and an item without children is guessed at from its
    level.

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
        default_story_points: What a backlog item that nobody has
            estimated is worked with. None is deprecated and only kept
            for backward compatibility: it works such an item with no
            story points at all and reports a DeprecationWarning.

    Returns:
        A new backlog whose items carry the estimated ready date. The
        other fields are copied unchanged from the given items.
    """
    start = date.today() if start_date is None else start_date
    points = _points_of(backlog, _defaults_or_warn(default_story_points))
    model = WorkModel(points, _points_per_day(available_teams))
    return schedule_ready_dates(backlog, available_teams, start, stderr_file,
                                model)


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
