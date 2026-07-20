#! /usr/local/bin/python3
"""Tests for the interactive workforce collection of the wizard.

These end-to-end tests drive the workforce wizard through a scripted
console bridge: the company schedule and holiday table, the persons and
their exception forms, and the teams with their combined form, members,
full-time-equivalent sum and aliases.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
import pytest
from tableio_cfg_json import WizardUiBridgeConsole
from backlogops.backlog_ops_wizard import available_teams_wizard, \
    _exc_seed, _fte_seed, _member_seed
from backlogops.team import FteException, Membership
from backlogops.work_hours import DEFAULT_WORK_WEEK, ExceptionWorkHours, \
    WeekDay
from .wizard_test_helpers import COMPANY, SCHED, run_workforce


def test_minimal_workforce() -> None:
    """Test an all-default run yields an empty workforce with defaults."""
    teams = run_workforce(SCHED + ['', '', ''])
    assert not teams.persons
    assert not teams.teams
    assert teams.company_work_hours.work_hours == DEFAULT_WORK_WEEK


def test_schedule_edit() -> None:
    """Test an edited work-hours cell overrides that day's default."""
    teams = run_workforce(['6'] + [''] * 6 + ['', '', ''])
    work_hours = teams.company_work_hours.work_hours
    assert work_hours[WeekDay.MONDAY] == 6.0
    assert work_hours[WeekDay.TUESDAY] == 8.0


def test_full_workforce() -> None:
    """Test a full run builds the persons, team, and memberships.

    The team form gives the name, member and alias counts, velocity and
    sprint length; the members follow, then the full-time-equivalent sum,
    which defaults to the two members entered.
    """
    answers = (COMPANY
               + ['2']
               + ['Ada', '0']
               + ['Bo', '0']
               + ['1']
               + ['Phoenix', '2', '0', '30', '']
               + ['1', '', '', '', '0']
               + ['1', '0.5', '', '', '0']
               + [''])
    teams = run_workforce(answers)
    assert sorted(teams.persons) == ['ada', 'bo']
    team = teams.teams[0]
    assert team.name == 'Phoenix'
    assert team.velocity == 30.0
    assert team.sum_fte_at_velocity == 2.0
    assert [(m.person_name, m.fte) for m in team.members] == \
        [('Ada', 1.0), ('Bo', 0.5)]


def test_choose_by_name() -> None:
    """Test a membership can select a person by typing the name."""
    answers = (COMPANY
               + ['1']
               + ['Ada', '0']
               + ['1']
               + ['T', '1', '0', '', '']
               + ['ada', '', '', '', '0']
               + [''])
    teams = run_workforce(answers)
    assert teams.teams[0].members[0].person_name == 'Ada'


def test_duplicate_name() -> None:
    """Test a duplicate person name re-asks the whole person form.

    The name and exception count are one form, so the duplicate name
    re-asks both fields; the second attempt enters a free name.
    """
    answers = (COMPANY
               + ['2']
               + ['Ada', '0']
               + ['ada', '0', 'Bo', '0']
               + ['0'])
    teams = run_workforce(answers)
    assert sorted(teams.persons) == ['ada', 'bo']


def test_reask_number() -> None:
    """Test a non-numeric velocity re-asks the whole team form.

    The team name, counts, velocity and sprint length are one form, so a
    non-numeric velocity re-asks every field; the second attempt enters a
    valid velocity and keeps the other defaults.
    """
    answers = (COMPANY
               + ['0']
               + ['1']
               + ['Phoenix', '0', '0', 'abc', '']
               + ['Phoenix', '0', '0', '5', '']
               + [''])
    teams = run_workforce(answers)
    assert teams.teams[0].velocity == 5.0


def test_company_holidays() -> None:
    """Test a company holiday period is captured through its table.

    The period is one added row: an unparseable start date is re-asked in
    the cell, then a valid start and end date, blank hours (which mean
    zero) and 'no' for adding free-day work are accepted.
    """
    answers = (SCHED
               + [':+', 'bad', '2026-01-01', '2026-01-05', '', 'no', '']
               + ['0', '0'])
    teams = run_workforce(answers)
    exception = teams.company_work_hours.exceptions[0]
    assert exception.start_date == date(2026, 1, 1)
    assert exception.end_date == date(2026, 1, 5)
    assert exception.hours_per_day == 0.0
    assert exception.new_work_days is False


def test_vacation() -> None:
    """Test a personal vacation exception is captured for the person."""
    answers = (COMPANY
               + ['1']
               + ['Ada', '1']
               + ['2026-07-01', '2026-07-20', '0', 'n']
               + ['0'])
    teams = run_workforce(answers)
    vacation = teams.persons['ada'].exceptions[0]
    assert vacation.start_date == date(2026, 7, 1)
    assert vacation.end_date == date(2026, 7, 20)
    assert teams.company_work_hours.work_hours[WeekDay.MONDAY] == 8.0


def test_team_with_extras() -> None:
    """Test a team with an alias, a dated member and an fte exception.

    This exercises adding an alias and an fte exception, and re-asking the
    membership form whose end date is before its start date. The
    membership form asks person, fte, dates and the fte-exception count
    together, so the bad end order re-asks all of them.
    """
    answers = (COMPANY
               + ['1']
               + ['Ada', '0']
               + ['1']
               + ['T', '1', '1', '', '']
               + ['Ada', '', '2026-07-01', '2026-06-01', '1']
               + ['Ada', '', '2026-07-01', '2026-07-10', '1']
               + ['2026-07-02', '2026-07-05', '0.5']
               + ['']
               + ['Alpha'])
    teams = run_workforce(answers)
    team = teams.teams[0]
    assert team.aliases == ['Alpha']
    member = team.members[0]
    assert member.start_date == date(2026, 7, 1)
    assert member.end_date == date(2026, 7, 10)
    assert member.fte_exceptions[0].fte == 0.5


def test_back_navigation() -> None:
    """Test a back request re-asks the previous question, pre-filled.

    After the person form the user steps back from the team count and
    leaves the re-asked form blank, keeping the pre-filled person.
    """
    answers = (COMPANY
               + ['1']
               + ['Ada', '0']
               + [':b', '', '']
               + ['0'])
    teams = run_workforce(answers)
    assert sorted(teams.persons) == ['ada']


def test_cancel_level() -> None:
    """Test cancelling a level restarts that item from its first question.

    Cancelling at the first personal exception re-asks the whole person,
    so the temporary name is replaced.
    """
    answers = (COMPANY
               + ['1']
               + ['Tmp', '1']
               + [':c']
               + ['Ada', '0']
               + ['0'])
    teams = run_workforce(answers)
    assert sorted(teams.persons) == ['ada']


def test_cancel_to_count() -> None:
    """Test cancelling a level from an item re-asks the group's count.

    Cancelling at the second person's form returns to the person count
    question and re-asks the whole group, so the first person entered is
    discarded.
    """
    answers = (COMPANY
               + ['2', 'Sam', '0', ':c', '1', 'Ada', '0']
               + ['0'])
    teams = run_workforce(answers)
    assert sorted(teams.persons) == ['ada']


def test_no_outer_level() -> None:
    """Test cancelling at a top-level count reports there is no outer level."""
    stdin = io.StringIO('\n'.join(SCHED + ['', ':c', '0', '0']) + '\n')
    stdout = io.StringIO()
    teams = available_teams_wizard(
        WizardUiBridgeConsole(stdout, stdin, io.StringIO()))
    assert not teams.persons
    assert 'no outer level' in stdout.getvalue().lower()


def test_abort() -> None:
    """Test an abort request ends the wizard with an end-of-input error."""
    with pytest.raises(EOFError):
        run_workforce([':q'])


def test_exc_seed() -> None:
    """Test a stored exception pre-fills the work-hour exception form."""
    exc = ExceptionWorkHours(start_date=date(2026, 1, 1),
                             end_date=date(2026, 1, 5), hours_per_day=4.0,
                             new_work_days=True)
    result = _exc_seed(exc)
    assert result is not None
    assert result.day('start') == date(2026, 1, 1)
    assert result.day('end') == date(2026, 1, 5)
    assert result.number('hours') == 4.0
    assert result.flag('new_days') is True


def test_member_seed() -> None:
    """Test a stored membership pre-fills the membership form values."""
    member = Membership(person_name='Ada', fte=0.5,
                        start_date=date(2026, 1, 1), end_date=None,
                        fte_exceptions=[_fte_exc()])
    result = _member_seed(member)
    assert result is not None
    assert result.text('person') == 'Ada'
    assert result.number('fte') == 0.5
    assert result.opt_day('start') == date(2026, 1, 1)
    assert result.opt_day('end') is None
    assert result.whole('n_fte') == 1


def _fte_exc() -> FteException:
    """Return a full-time-equivalent exception period for seeding."""
    return FteException(start_date=date(2026, 2, 1), end_date=date(2026, 2, 5),
                        fte=0.5)


def test_fte_seed() -> None:
    """Test a stored fte exception pre-fills the fte-exception form."""
    result = _fte_seed(_fte_exc())
    assert result is not None
    assert result.day('start') == date(2026, 2, 1)
    assert result.day('end') == date(2026, 2, 5)
    assert result.number('fte') == 0.5


def test_seed_none() -> None:
    """Test each workforce seed helper returns None for no source."""
    assert _exc_seed(None) is None
    assert _member_seed(None) is None
    assert _fte_seed(None) is None
