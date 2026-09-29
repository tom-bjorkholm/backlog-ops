#! /usr/local/bin/python3
"""Tests for estimating the ready date of backlog items from remaining time.

Unless a test says otherwise, the one team member works the default
eight hour weekdays at a focus factor of one half, so the team does four
hours of remaining time on each weekday.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from dataclasses import replace
from datetime import date, timedelta
from typing import Optional
import pytest
from backlogops import (
    AvailableTeams, BacklogItem, BacklogReleases, ExceptionWorkHours,
    FeatureDisabled, Release, RemainingTimeConfig, Status, Team,
    estimate_rt_ready_date)
from backlogops.no_text_io import NoTextIO
from .estimate_helpers import MON, member, person, workforce
from .shared_test_data import def_times

NO = NoTextIO()
TUE, WED, THU = date(2026, 6, 16), date(2026, 6, 17), date(2026, 6, 18)
"""The weekdays after the Monday the tests start on."""


def rt_config(guess: Optional[dict[int, float]] = None,
              enabled: bool = True) -> RemainingTimeConfig:
    """Return remaining time at a default focus factor of one half.

    Args:
        guess: The hours an unestimated item counts as, by level, or None
            to guess nothing.
        enabled: Whether remaining time estimates are enabled.
    """
    config = def_times(guess or {})
    config.enable_remaining_time = enabled
    config.default_focus_factor = 0.5
    return config


def team(name: str = 'T', focus: Optional[float] = None,
         fte: float = 1.0) -> Team:
    """Build a team of Ann, with its own focus factor when given."""
    return Team(name=name, velocity=10.0, sum_fte_at_velocity=1.0,
                sprint_length=10, focus_factor=focus,
                members=[member('Ann', fte)])


def one_team(focus: Optional[float] = None, fte: float = 1.0,
             exceptions: Optional[list[ExceptionWorkHours]] = None
             ) -> AvailableTeams:
    """Build a workforce of the one team of Ann."""
    return workforce([team('T', focus, fte)], [person('Ann', exceptions)])


def item(key: str, hours: Optional[float] = 1.0, status: Status = Status.TODO,
         parent: Optional[str] = None, level: int = 1) -> BacklogItem:
    """Build a backlog item with a remaining time in hours, or none."""
    time = None if hours is None else timedelta(hours=hours)
    return BacklogItem(key=key, level=level, title=key, story_points=None,
                       status=status, parent_key=parent, remaining_time=time)


def run(backlog: list[BacklogItem], force: Optional[AvailableTeams] = None,
        config: Optional[RemainingTimeConfig] = None
        ) -> dict[str, Optional[date]]:
    """Estimate the backlog from Monday and return the date by key."""
    result = estimate_rt_ready_date(backlog, force or one_team(),
                                    config or rt_config(), MON, NO)
    return {i.key: i.estimated_ready_date for i in result}


def test_sequence_dates() -> None:
    """One team works the items back to back at four hours a day."""
    backlog = [item('a', 4), item('b', 8), item('c', 2)]
    assert run(backlog) == {'a': MON, 'b': WED, 'c': THU}


def test_same_day_carryover() -> None:
    """Small items share a day and the leftover carries to the next."""
    backlog = [item('a', 1), item('b', 2), item('c', 2)]
    assert run(backlog) == {'a': MON, 'b': MON, 'c': TUE}


@pytest.mark.parametrize('focus, fte, ready', [
    (None, 1.0, MON), (0.5, 1.0, MON), (0.25, 1.0, TUE), (1.0, 1.0, MON),
    (None, 0.5, TUE), (0.25, 0.5, THU)])
def test_focus_and_fte(focus: Optional[float], fte: float,
                       ready: date) -> None:
    """The team's own focus factor, or the default, and FTE set the pace."""
    assert run([item('a', 4)], one_team(focus, fte)) == {'a': ready}


def test_weekend_skipped() -> None:
    """No work is done on the weekend."""
    assert run([item('a', 24)]) == {'a': date(2026, 6, 22)}


def test_vacation_delays() -> None:
    """A member's vacation pushes the ready date later."""
    off = ExceptionWorkHours(start_date=MON, end_date=TUE, hours_per_day=0.0)
    assert run([item('a', 4)], one_team(exceptions=[off])) == {'a': WED}


def test_story_points_unused() -> None:
    """Story points are not remaining time, so they add no work."""
    backlog = [replace(item('s', None), story_points=8.0), item('a', 4)]
    assert run(backlog) == {'s': MON, 'a': MON}


@pytest.mark.parametrize('status', [Status.DONE, Status.REJECTED])
def test_terminal_no_date(status: Status) -> None:
    """A done or rejected item gets no date and leaves the team free."""
    backlog = [item('t', 40, status), item('a', 4)]
    assert run(backlog) == {'t': None, 'a': MON}


def test_in_progress() -> None:
    """An in-progress item is dated from all of its remaining time."""
    backlog = [item('a', 8, Status.IN_PROGRESS)]
    assert run(backlog) == {'a': TUE}


def test_zero_time() -> None:
    """An item with no remaining time left is ready at once."""
    assert run([item('z', 0), item('a', 8)]) == {'z': MON, 'a': TUE}


def test_guessed_by_level() -> None:
    """An unestimated item is worked with the guess for its level."""
    backlog = [item('a', None, level=2), item('b', 4)]
    config = rt_config({2: 8.0})
    assert run(backlog, config=config) == {'a': TUE, 'b': WED}


def test_no_guess_is_free() -> None:
    """An unestimated item is no work when nothing guesses for it."""
    assert run([item('a', None), item('b', 4)]) == {'a': MON, 'b': MON}


def test_container_no_guess() -> None:
    """An unestimated parent is a container, dated by its child."""
    backlog = [item('p', None, level=2), item('c', 8, parent='p')]
    config = rt_config({2: 40.0})
    assert run(backlog, config=config) == {'p': TUE, 'c': TUE}


def test_parent_own_time() -> None:
    """A parent's own remaining time is worked beside its child's."""
    backlog = [item('p', 4, level=2), item('c', 4, parent='p')]
    assert run(backlog) == {'p': TUE, 'c': TUE}


def test_done_child_no_delay() -> None:
    """A finished child does not delay its parent's date."""
    backlog = [item('p', 4), item('c', 40, Status.DONE, parent='p')]
    assert run(backlog) == {'p': MON, 'c': None}


def test_two_teams() -> None:
    """Unassigned items go to whichever team is free earliest."""
    force = workforce([team('T1'), team('T2', 0.25)], [person('Ann')])
    backlog = [item('a', 4), item('b', 4), replace(item('c', 2), team='t2')]
    assert run(backlog, force) == {'a': MON, 'b': TUE, 'c': WED}


@pytest.mark.parametrize('force, assigned, text', [
    (one_team(), 'Ghost', 'Ghost'),
    (AvailableTeams(persons={}, teams=[]), None, 'no team'),
    (workforce([Team(name='T', velocity=1.0, sum_fte_at_velocity=1.0,
                     sprint_length=1)], []), None, 'no capacity')])
def test_undated_warns(force: AvailableTeams, assigned: Optional[str],
                       text: str) -> None:
    """An item that cannot be worked gets no date and a warning."""
    out = io.StringIO()
    backlog = [replace(item('a', 4), team=assigned)]
    result = estimate_rt_ready_date(backlog, force, rt_config(), MON, out)
    assert result[0].estimated_ready_date is None
    assert text in out.getvalue()


def test_input_unchanged() -> None:
    """Estimating does not modify the given backlog items."""
    backlog = [item('a', 4)]
    estimate_rt_ready_date(backlog, one_team(), rt_config(), MON, NO)
    assert backlog[0].estimated_ready_date is None


def test_default_today() -> None:
    """A None start date estimates from today, like passing today."""
    backlog, force = [item('a', 4)], one_team()
    by_none = estimate_rt_ready_date(backlog, force, rt_config(), None, NO)
    by_today = estimate_rt_ready_date(backlog, force, rt_config(),
                                      date.today(), NO)
    assert by_none == by_today


def test_empty_backlog() -> None:
    """An empty backlog is estimated as an empty backlog."""
    assert not estimate_rt_ready_date([], one_team(), rt_config(), MON, NO)


def test_disabled_refused() -> None:
    """Estimating is refused, saying how to enable it, when it is off."""
    with pytest.raises(FeatureDisabled, match='enable_remaining_time') as info:
        estimate_rt_ready_date([item('a', 4)], one_team(),
                               rt_config(enabled=False), MON, NO)
    assert isinstance(info.value, ValueError)


def _releases(backlog: list[BacklogItem]) -> BacklogReleases:
    """Return the backlog with the one release its items are in."""
    return BacklogReleases(backlog=backlog, releases=[Release(name='R')])


def test_releases_estimated() -> None:
    """The backlog and releases method dates both items and release."""
    data = _releases([replace(item('a', 8), release='R')])
    changes = data.estimate_rt_ready_date(one_team(), rt_config(), MON, NO)
    assert data.backlog[0].estimated_ready_date == TUE
    assert data.releases[0].estimated_date == TUE
    assert changes


def test_releases_disabled() -> None:
    """A refused estimate leaves the backlog and releases unchanged."""
    data = _releases([item('a', 8)])
    with pytest.raises(FeatureDisabled):
        data.estimate_rt_ready_date(one_team(), rt_config(enabled=False))
    assert data == _releases([item('a', 8)])
