#! /usr/local/bin/python3
"""Estimate the ready date of backlog items from remaining time.

Estimating in story points is recommended, but some development efforts
are required to estimate in remaining time. :func:`estimate_rt_ready_date`
is for them: it dates the backlog items like
:func:`backlogops.estimate_ready_date` does, but from the remaining time
of the items and the focused work hours of the teams instead of from
story points and velocity.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from datetime import date
from typing import Callable, Optional, TextIO
from backlogops.backlog import Backlog, BacklogItem, Status
from backlogops.available_teams import AvailableTeams
from backlogops.ready_date_schedule import WorkModel, schedule_ready_dates, \
    team_hours
from backlogops.remaining_time_config import RemainingTimeConfig
from backlogops.team import Team
from backlogops.use_story_points import find_keys_with_children

_SECONDS_PER_HOUR = 3600.0
"""Seconds in one hour, to turn work hours into scheduled seconds."""

_RT_DISABLED = (
    'Remaining time estimates are not enabled in the configuration, so no '
    'ready date can be estimated from remaining time. Set '
    '"enable_remaining_time" to true in the "remaining_time" section of '
    'the configuration (for example with the configuration wizard), or '
    'estimate the ready date from story points instead.')
"""Why estimating from remaining time is refused while it is disabled."""


class FeatureDisabled(ValueError):
    """An operation was asked for that the configuration switches off.

    It is a ``ValueError``, so that code that reports bad input also
    reports asking for a feature that is not enabled.
    """


def _seconds_of(item: BacklogItem, config: RemainingTimeConfig,
                with_children: set[str]) -> float:
    """Return the remaining time to work one backlog item with, in seconds.

    A done or rejected item is no work left to do. An item that has a
    remaining time of its own is worked with it, whether or not it has
    children, because that is the work on the item itself beside the work
    in its children. An item without a remaining time that has children
    is a container for them and is no work of its own. Any other item is
    worked with what the configuration guesses for its level, or with no
    time when it guesses nothing. Like the default story points, the
    guess is used only here and is never stored on the item.
    """
    if item.status in (Status.DONE, Status.REJECTED):
        return 0.0
    if item.remaining_time is not None:
        return item.remaining_time.total_seconds()
    if item.key in with_children:
        return 0.0
    guess = config.get_default_time(item.level)
    return guess.total_seconds() if guess is not None else 0.0


def _focused_seconds(teams: AvailableTeams, config: RemainingTimeConfig
                     ) -> Callable[[Team, date], float]:
    """Return how many seconds of remaining time a team does on one day.

    A remaining time is ideal focused work time of one person, so a team
    does its person work hours of the day scaled by its focus factor. The
    focus factor is the team's own, or the default focus factor of the
    configuration for a team that has none.
    """
    def seconds_on(team: Team, day: date) -> float:
        """Return the seconds of remaining time the team does on the day."""
        focus = team.focus_factor
        if focus is None:
            focus = config.default_focus_factor
        return team_hours(teams, team, day) * focus * _SECONDS_PER_HOUR
    return seconds_on


def estimate_rt_ready_date(backlog: Backlog, available_teams: AvailableTeams,
                           remaining_time_config: RemainingTimeConfig,
                           start_date: Optional[date] = None,
                           stderr_file: TextIO = sys.stderr) -> Backlog:
    """Estimate the ready date of backlog items from remaining time.

    The items are scheduled like :func:`backlogops.estimate_ready_date`
    does: the teams start working on the start date, which defaults to
    today when None is given, and work the items in backlog order. Each
    item is worked by its assigned team, or, when it names no team, by
    the team that becomes free earliest. Only one team works an item, and
    a team works one item at a time. When a team's capacity on a day
    covers more than one item, several items finish on the same day. A
    parent's date is lifted to be no earlier than its latest child's,
    and a finished child does not delay its parent. Dependencies between
    items are not considered.

    What differs is how much work an item is and how fast a team does
    it. An item is worked with its remaining time, which is ideal focused
    work time of one person. A team does, on each day, the work hours of
    its members that day, scaled by each member's full-time equivalent in
    the team and by the team's focus factor. That follows weekends,
    company holidays, personal vacation, part-time and learning periods
    and ordered over-time. The focus factor is the team's own
    ``focus_factor``, or the ``default_focus_factor`` of the remaining
    time configuration for a team that has none. The velocity and the
    sprint length of a team are not used.

    The remaining time of TODO and IN_PROGRESS items is all treated as
    still left to do; DONE and REJECTED items need no work and get no
    estimated date. An item that has no remaining time of its own is a
    container for its children and is no work of its own when it has
    children, and is otherwise guessed at from its level by the remaining
    time configuration, or is no work when nothing is guessed for its
    level. Story points are not used at all.

    When an item names a team that is not in the workforce, when no team
    is available, or when the chosen team has no capacity for the item,
    the item gets no estimated date and a warning is reported.

    Args:
        backlog: The backlog to estimate the ready date of. The argument
                 is not modified. The backlog must be ordered so that the
                 teams can work the items in order.
        available_teams: The available teams used to estimate the ready
                         date, including absence, focus factor and work
                         hours.
        remaining_time_config: The remaining time configuration, which
            must enable remaining time estimates. It gives the default
            focus factor and what an item nobody has estimated counts as.
        start_date: The day the teams start working, or None for today.
        stderr_file: The file to report warnings to.

    Returns:
        A new backlog whose items carry the estimated ready date. The
        other fields are copied unchanged from the given items.

    Raises:
        FeatureDisabled: Remaining time estimates are not enabled in the
            remaining time configuration.
    """
    if not remaining_time_config.enable_remaining_time:
        raise FeatureDisabled(_RT_DISABLED)
    start = date.today() if start_date is None else start_date
    with_children = find_keys_with_children(backlog)
    work = {item.key: _seconds_of(item, remaining_time_config, with_children)
            for item in backlog}
    rate = _focused_seconds(available_teams, remaining_time_config)
    return schedule_ready_dates(backlog, available_teams, start, stderr_file,
                                WorkModel(work, rate))
