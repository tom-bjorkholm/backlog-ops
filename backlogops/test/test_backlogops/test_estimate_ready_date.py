#! /usr/local/bin/python3
"""Tests for estimating the ready date of backlog items."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
from typing import Optional
import pytest
from backlogops import (
    AvailableTeams, BacklogItem, CompanyWorkHours, ExceptionWorkHours,
    Membership, Person, Status, Team, estimate_ready_date,
    set_plan_from_estimate)
from backlogops.no_text_io import NoTextIO

MON = date(2026, 6, 15)
"""A Monday used as the start date in the tests."""
NO = NoTextIO()


def person(name: str,
           exceptions: Optional[list[ExceptionWorkHours]] = None) -> Person:
    """Build a person, optionally with work-hours exceptions."""
    return Person(name=name, exceptions=exceptions or [])


def member(name: str, fte: float = 1.0) -> Membership:
    """Build a full-membership for a person by name."""
    return Membership(person_name=name, fte=fte)


def team(name: str, members: list[Membership], sum_fte: float = 1.0,
         aliases: Optional[list[str]] = None) -> Team:
    """Build a team whose velocity is ten points over a ten-day sprint.

    The velocity is the whole team's output. With one full-time member
    at the summed FTE the velocity was measured at, the team completes
    one story point each working day.
    """
    return Team(name=name, velocity=10.0, sum_fte_at_velocity=sum_fte,
                sprint_length=10, aliases=aliases or [], members=members)


def workforce(team_list: list[Team], persons: list[Person],
              company: Optional[CompanyWorkHours] = None) -> AvailableTeams:
    """Build the available workforce from teams and persons."""
    registry = {p.name.lower(): p for p in persons}
    if company is None:
        return AvailableTeams(persons=registry, teams=team_list)
    return AvailableTeams(persons=registry, teams=team_list,
                          company_work_hours=company)


def one_team(company: Optional[CompanyWorkHours] = None,
             fte: float = 1.0) -> AvailableTeams:
    """Build a workforce of one full-time team member named Ann."""
    ann = person('Ann')
    return workforce([team('T', [member('Ann', fte)])], [ann], company)


def item(key: str, sp: int = 1, status: Status = Status.TODO,
         assigned: Optional[str] = None,
         parent: Optional[str] = None) -> BacklogItem:
    """Build a backlog item with the fields the tests vary."""
    return BacklogItem(key=key, level=1, title=key, story_points=sp,
                       status=status, team=assigned, parent_key=parent)


def run(backlog: list[BacklogItem], force: AvailableTeams,
        start: Optional[date] = MON) -> dict[str, Optional[date]]:
    """Estimate the backlog and return a key to ready-date mapping."""
    result = estimate_ready_date(backlog, force, start, NO)
    return {i.key: i.estimated_ready_date for i in result}


def test_sequence_dates() -> None:
    """One team works three items back to back at one point a day."""
    backlog = [item('a', 3), item('b', 5), item('c', 6)]
    assert run(backlog, one_team()) == {'a': date(2026, 6, 17),
                                        'b': date(2026, 6, 24),
                                        'c': date(2026, 7, 2)}


def test_in_progress() -> None:
    """An in-progress item is dated from its full story points."""
    todo = run([item('a', 3, Status.TODO)], one_team())
    doing = run([item('a', 3, Status.IN_PROGRESS)], one_team())
    assert doing == todo == {'a': date(2026, 6, 17)}


def test_done_rejected_none() -> None:
    """Done and rejected items get no estimated date."""
    backlog = [item('d', 3, Status.DONE), item('r', 3, Status.REJECTED)]
    assert run(backlog, one_team()) == {'d': None, 'r': None}


def test_zero_points() -> None:
    """A zero-point item is ready at once and frees the team at once."""
    backlog = [item('z', 0), item('a', 3)]
    assert run(backlog, one_team()) == {'z': MON, 'a': date(2026, 6, 17)}


def test_input_unchanged() -> None:
    """Estimating does not modify the given backlog items."""
    backlog = [item('a', 3)]
    estimate_ready_date(backlog, one_team(), MON, NO)
    assert backlog[0].estimated_ready_date is None


def test_default_today() -> None:
    """A None start date estimates from today, like passing today."""
    by_none = run([item('a', 1)], one_team(), None)
    by_today = run([item('a', 1)], one_team(), date.today())
    assert by_none == by_today


def test_vacation_delays() -> None:
    """A member's vacation pushes the ready date later."""
    off = ExceptionWorkHours(start_date=MON, end_date=date(2026, 6, 16),
                             hours_per_day=0.0)
    ann = person('Ann', [off])
    force = workforce([team('T', [member('Ann')])], [ann])
    assert run([item('a', 3)], force) == {'a': date(2026, 6, 19)}


def test_holiday_delays() -> None:
    """A company holiday in the middle pushes the ready date later."""
    holiday = ExceptionWorkHours(start_date=date(2026, 6, 17),
                                 end_date=date(2026, 6, 17), hours_per_day=0.0)
    company = CompanyWorkHours(exceptions=[holiday])
    assert run([item('a', 3)], one_team(company)) == {'a': date(2026, 6, 18)}


def test_part_time_slower() -> None:
    """A half-time member needs twice the calendar time."""
    assert run([item('a', 3)], one_team(fte=0.5)) == {'a': date(2026, 6, 22)}


def fast_team(persons: list[Person]) -> AvailableTeams:
    """Build a workforce of one team doing ten story points a day."""
    members = [member(p.name) for p in persons]
    quick = Team(name='F', velocity=10.0, sum_fte_at_velocity=1.0,
                 sprint_length=1, members=members)
    return workforce([quick], persons)


def test_many_per_day() -> None:
    """A team with spare daily capacity finishes items the same day."""
    force = fast_team([person('Ann')])
    backlog = [item('a', 1), item('b', 1), item('c', 1)]
    assert run(backlog, force) == {'a': MON, 'b': MON, 'c': MON}


def test_carryover() -> None:
    """Leftover capacity of a finishing day is used by the next item."""
    force = fast_team([person('Ann')])
    backlog = [item('a', 7), item('b', 7)]
    assert run(backlog, force) == {'a': MON, 'b': date(2026, 6, 16)}


def test_velocity_rescale() -> None:
    """Velocity measured at a higher summed FTE scales the pace down."""
    ann = person('Ann')
    force = workforce([team('T', [member('Ann')], sum_fte=2.0)], [ann])
    assert run([item('a', 3)], force) == {'a': date(2026, 6, 22)}


def test_two_teams() -> None:
    """Unassigned items go to whichever team is free earliest."""
    ann, bob = person('Ann'), person('Bob')
    force = workforce([team('T1', [member('Ann')]),
                       team('T2', [member('Bob')])], [ann, bob])
    backlog = [item('a', 3), item('b', 3), item('c', 3)]
    assert run(backlog, force) == {'a': date(2026, 6, 17),
                                   'b': date(2026, 6, 17),
                                   'c': date(2026, 6, 22)}


def test_assigned_team() -> None:
    """An assigned team works its items even while another is idle."""
    ann, bob = person('Ann'), person('Bob')
    force = workforce([team('T1', [member('Ann')]),
                       team('T2', [member('Bob')])], [ann, bob])
    backlog = [item('a', 3, assigned='T2'), item('b', 3, assigned='T2')]
    assert run(backlog, force) == {'a': date(2026, 6, 17),
                                   'b': date(2026, 6, 22)}


def test_alias_resolved() -> None:
    """An item may name its team by an alias, case-insensitively."""
    ann = person('Ann')
    force = workforce([team('T', [member('Ann')], aliases=['Alpha'])], [ann])
    assert run([item('a', 3, assigned='alpha')], force) == \
        {'a': date(2026, 6, 17)}


def test_unknown_team_none() -> None:
    """An item naming an unknown team gets no date and a warning."""
    out = io.StringIO()
    backlog = [item('a', 3, assigned='Ghost')]
    result = estimate_ready_date(backlog, one_team(), MON, out)
    assert result[0].estimated_ready_date is None
    assert 'Ghost' in out.getvalue()


def test_no_teams_none() -> None:
    """With no teams available an item gets no date and a warning."""
    out = io.StringIO()
    empty = AvailableTeams(persons={}, teams=[])
    result = estimate_ready_date([item('a', 3)], empty, MON, out)
    assert result[0].estimated_ready_date is None
    assert 'a' in out.getvalue()


def test_no_capacity_none() -> None:
    """A team with no members never finishes, so the item has no date."""
    out = io.StringIO()
    force = workforce([team('T', [])], [])
    result = estimate_ready_date([item('a', 3)], force, MON, out)
    assert result[0].estimated_ready_date is None


def test_parent_rollup() -> None:
    """A parent is dated no earlier than its latest child, recursively."""
    backlog = [item('g', 1), item('p', 1, parent='g'),
               item('c', 10, parent='p')]
    dates = run(backlog, one_team())
    assert dates['c'] == date(2026, 6, 30)
    assert dates['p'] == dates['c']
    assert dates['g'] == dates['c']


def test_done_child_no_delay() -> None:
    """A finished child does not delay its parent's date."""
    backlog = [item('p', 1), item('c', 10, Status.DONE, parent='p')]
    assert run(backlog, one_team()) == {'p': MON, 'c': None}


def test_set_plan_copies() -> None:
    """Setting the plan copies the estimated date, including None."""
    backlog = [item('a', 3), item('d', 3, Status.DONE)]
    estimated = estimate_ready_date(backlog, one_team(), MON, NO)
    planned = set_plan_from_estimate(estimated, NO)
    assert planned[0].planned_ready_date == date(2026, 6, 17)
    assert planned[1].planned_ready_date is None


def test_set_plan_unchanged() -> None:
    """Setting the plan does not modify the given backlog items."""
    estimated = estimate_ready_date([item('a', 3)], one_team(), MON, NO)
    set_plan_from_estimate(estimated, NO)
    assert estimated[0].planned_ready_date is None


def test_zero_standard_hours() -> None:
    """A company with an empty work week completes no work."""
    company = CompanyWorkHours(work_hours={})
    result = estimate_ready_date([item('a', 3)], one_team(company), MON, NO)
    assert result[0].estimated_ready_date is None


def test_zero_fte_member() -> None:
    """A member giving zero full-time equivalent contributes nothing."""
    ann, bob = person('Ann'), person('Bob')
    force = workforce([team('T', [member('Ann', 1.0), member('Bob', 0.0)])],
                      [ann, bob])
    assert run([item('a', 3)], force) == {'a': date(2026, 6, 17)}


def test_unknown_person() -> None:
    """A membership for an unregistered person is skipped."""
    ann = person('Ann')
    force = workforce([team('T', [member('Ann'), member('Ghost')])], [ann])
    assert run([item('a', 3)], force) == {'a': date(2026, 6, 17)}


def test_weekend_exc() -> None:
    """An exception over a closed weekend day keeps the day closed."""
    off = ExceptionWorkHours(start_date=date(2026, 6, 20),
                             end_date=date(2026, 6, 21), hours_per_day=0.0)
    ann = person('Ann', [off])
    force = workforce([team('T', [member('Ann')])], [ann])
    assert run([item('a', 6)], force) == {'a': date(2026, 6, 22)}


def test_zero_sprint_length() -> None:
    """A team with a non-positive sprint length completes no points."""
    ann = person('Ann')
    bad = Team(name='T', velocity=10.0, sum_fte_at_velocity=1.0,
               sprint_length=0, members=[member('Ann')])
    force = workforce([bad], [ann])
    result = estimate_ready_date([item('a', 3)], force, MON, NO)
    assert result[0].estimated_ready_date is None


def test_parent_cycle() -> None:
    """A parent cycle is handled without infinite recursion."""
    backlog = [item('p', 1, parent='c'), item('c', 1, parent='p')]
    result = estimate_ready_date(backlog, one_team(), MON, NO)
    assert all(i.estimated_ready_date is not None for i in result)


@pytest.mark.parametrize('status', [Status.DONE, Status.REJECTED])
def test_terminal_frees_team(status: Status) -> None:
    """A done or rejected item before another leaves the team free."""
    backlog = [item('t', 3, status), item('a', 3)]
    assert run(backlog, one_team())['a'] == date(2026, 6, 17)
