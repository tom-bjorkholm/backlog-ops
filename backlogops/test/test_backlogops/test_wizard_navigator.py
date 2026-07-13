#! /usr/local/bin/python3
"""Tests for the re-runnable wizard navigator and its pre-filling.

The synthetic-body tests drive a counted-name body directly to check that
going back pre-fills, that raising a count keeps the entered items and
lowering it drops (and forgets) the surplus. The workforce tests check the
same pre-filling and the ``default`` and ``backward`` parameters through
:func:`available_teams_wizard`.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from functools import partial
from typing import Optional
from tableio_cfg_json import WizardUiBridgeConsole
from backlogops.available_teams import AvailableTeams
from backlogops.backlog_ops_wizard import available_teams_wizard
from backlogops.person import Person
from backlogops.team import Team
from backlogops.work_hours import CompanyWorkHours, DEFAULT_WORK_WEEK
from backlogops.wizard_navigator import _Navigator

SCHED = [''] * 7
"""Blank answers that keep the seven default daily work hours."""


def _bridge(answers: list[str]) -> WizardUiBridgeConsole:
    """Return a console bridge scripted with the given answers."""
    stdin = io.StringIO('\n'.join(answers) + '\n')
    return WizardUiBridgeConsole(io.StringIO(), stdin, io.StringIO())


def _run(answers: list[str]) -> AvailableTeams:
    """Run the workforce wizard with scripted answers and return it."""
    return available_teams_wizard(_bridge(answers))


def _names(nav: _Navigator, seq: list[str]) -> list[str]:
    """Ask a count then that many pre-fillable, blank-keepable names."""
    count = nav.ask_count('How many', seed=len(seq))
    return [nav.ask_text('Name', allow_empty=True,
                         seed=seq[k] if k < len(seq) else None)
            for k in range(count)]


def _names_body(nav: _Navigator, default: Optional[list[str]]) -> list[str]:
    """Collect a counted name list in its own level, then a tail field."""
    seq = default or []
    names = nav.level(partial(_names, nav, seq))
    nav.ask_text('Tail', default='T', allow_empty=True)
    return names


def _run_names(answers: list[str]) -> list[str]:
    """Run the counted-names body with scripted console answers."""
    return _Navigator(_bridge(answers)).run(_names_body)


def test_count_increase_keeps() -> None:
    """Test raising a count keeps the already-entered items pre-filled.

    After entering two names the user goes back to the count, raises it to
    three, accepts the two earlier names by leaving them blank, and adds a
    third; all three are collected.
    """
    names = _run_names(['2', 'Ada', 'Bo', ':b', ':b', ':b', '3',
                        '', '', 'Cy', ''])
    assert names == ['Ada', 'Bo', 'Cy']


def test_count_decrease_drops() -> None:
    """Test lowering a count drops the surplus items from the result."""
    names = _run_names(['3', 'Ada', 'Bo', 'Cy', ':b', ':b', ':b', ':b',
                        '2', '', '', ''])
    assert names == ['Ada', 'Bo']


def test_decrease_forgets() -> None:
    """Test a dropped item is not resurrected when the count rises again.

    Lowering the count from three to two forgets the third item, so raising
    it back to three offers no pre-fill for the third item, which is left
    blank and comes back empty rather than as the earlier value.
    """
    names = _run_names(['3', 'Ada', 'Bo', 'Cy', ':b', ':b', ':b', ':b',
                        '2', '', '', ':b', ':b', ':b', '3', '', '', '', ''])
    assert names == ['Ada', 'Bo', '']


def test_back_prefill_name() -> None:
    """Test a re-asked person name is pre-filled with the earlier answer.

    The user enters a name, goes back to it, and leaves the re-asked
    question blank, which keeps the pre-filled name instead of re-asking.
    """
    teams = _run(SCHED + ['0', '1', 'Ada', ':b', '', '0', '0'])
    assert sorted(teams.persons) == ['ada']


def _one_person() -> AvailableTeams:
    """Return a workforce with the default schedule and one person."""
    company = CompanyWorkHours(work_hours=DEFAULT_WORK_WEEK, exceptions=[])
    return AvailableTeams(persons={'ada': Person(name='Ada', exceptions=[])},
                          teams=[], company_work_hours=company)


def test_default_person() -> None:
    """Test a default workforce pre-fills every question for a blank run."""
    teams = available_teams_wizard(_bridge(SCHED + [''] * 5),
                                   default=_one_person())
    assert sorted(teams.persons) == ['ada']


def test_default_team_form() -> None:
    """Test a default team pre-fills its form and alias, kept when blank."""
    company = CompanyWorkHours(work_hours=DEFAULT_WORK_WEEK, exceptions=[])
    team = Team(name='Phoenix', velocity=30.0, sum_fte_at_velocity=2.0,
                sprint_length=15, aliases=['pnx'], members=[])
    default = AvailableTeams(persons={}, teams=[team],
                             company_work_hours=company)
    teams = available_teams_wizard(_bridge(SCHED + [''] * 10), default=default)
    built = teams.teams[0]
    assert built.name == 'Phoenix'
    assert built.velocity == 30.0
    assert built.sprint_length == 15
    assert built.aliases == ['pnx']


def test_backward_opens_last() -> None:
    """Test a backward run opens on the last question, earlier ones filled.

    With a default workforce the wizard replays every earlier answer and
    asks only its last question, so answering it alone reproduces the
    default.
    """
    teams = available_teams_wizard(_bridge(['']), default=_one_person(),
                                   backward=True)
    assert sorted(teams.persons) == ['ada']
