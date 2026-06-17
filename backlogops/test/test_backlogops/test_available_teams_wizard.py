#! /usr/local/bin/python3
"""Tests for the interactive AvailableTeams wizard."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
import pytest
from backlogops.available_teams import AvailableTeams
from backlogops.available_teams_config import AvailableTeamsConfig
from backlogops.available_teams_wizard import (
    YesNoUiBridge, available_teams_wizard, teams_config_wizard)
from backlogops.available_teams_wizard import (
    _ask_choice, _ask_int, _ask_number, _ask_opt_date, _ask_text)
from backlogops.console_yes_no_bridge import ConsoleYesNoUiBridge
from backlogops.work_hours import DEFAULT_WORK_WEEK, WeekDay


def _bridge(answers: list[str]) -> ConsoleYesNoUiBridge:
    """Return a console bridge scripted with the given answers."""
    stdin = io.StringIO('\n'.join(answers) + '\n')
    return ConsoleYesNoUiBridge(io.StringIO(), stdin, io.StringIO())


def _run(answers: list[str]) -> AvailableTeams:
    """Run the wizard with scripted console answers and return the result."""
    return available_teams_wizard(_bridge(answers))


def test_minimal_workforce() -> None:
    """Test an all-default run yields an empty workforce with defaults."""
    answers = ['', '', '', '', '', '', '', '', '', '']
    teams = _run(answers)
    assert not teams.persons
    assert not teams.teams
    assert teams.company_work_hours.work_hours == DEFAULT_WORK_WEEK


def test_full_workforce() -> None:
    """Test a full run builds the persons, team, and memberships."""
    answers = [
        '', '', '', '', '', '', '',
        '',
        'y', 'Ada', '',
        'y', 'Bo', '',
        '',
        'y', 'Phoenix', '30', '2', '',
        '',
        'y', '1', '', '', '', '',
        'y', '1', '0.5', '', '', '',
        '']
    teams = _run(answers)
    assert sorted(teams.persons) == ['ada', 'bo']
    team = teams.teams[0]
    assert team.name == 'Phoenix'
    assert team.velocity == 30.0
    assert [(m.person_name, m.fte) for m in team.members] == \
        [('Ada', 1.0), ('Bo', 0.5)]


def test_choose_by_name() -> None:
    """Test a membership can select a person by typing the name."""
    answers = [
        '', '', '', '', '', '', '',
        '',
        'y', 'Ada', '',
        '',
        'y', 'T', '', '', '', '',
        'y', 'ada', '', '', '', '',
        '',
        '']
    teams = _run(answers)
    assert teams.teams[0].members[0].person_name == 'Ada'


def test_duplicate_name() -> None:
    """Test entering a duplicate person name is rejected and re-asked."""
    answers = [
        '', '', '', '', '', '', '',
        '',
        'y', 'Ada', '',
        'y', 'ada', 'Bo', '',
        '',
        '']
    teams = _run(answers)
    assert sorted(teams.persons) == ['ada', 'bo']


def test_reask_number() -> None:
    """Test a non-numeric velocity is rejected and then accepted."""
    answers = [
        '', '', '', '', '', '', '',
        '',
        '',
        'y', 'Phoenix', 'abc', '5', '', '',
        '',
        '']
    teams = _run(answers)
    assert teams.teams[0].velocity == 5.0


def test_company_exc() -> None:
    """Test a company exception with re-asked invalid date and end order."""
    answers = [
        '', '', '', '', '', '', '',
        'y', 'bad', '2026-01-01', '2025-12-31', '2026-01-05', '', 'maybe',
        'n',
        '',
        '',
        '']
    teams = _run(answers)
    exception = teams.company_work_hours.exceptions[0]
    assert exception.start_date == date(2026, 1, 1)
    assert exception.end_date == date(2026, 1, 5)
    assert exception.new_work_days is False


def test_vacation() -> None:
    """Test a personal vacation exception is captured for the person."""
    answers = [
        '', '', '', '', '', '', '',
        '',
        'y', 'Ada', 'y', '2026-07-01', '2026-07-20', '0', 'n', '',
        '',
        '']
    teams = _run(answers)
    vacation = teams.persons['ada'].exceptions[0]
    assert vacation.start_date == date(2026, 7, 1)
    assert vacation.end_date == date(2026, 7, 20)
    assert teams.company_work_hours.work_hours[WeekDay.MONDAY] == 8.0


def test_base_yes_no() -> None:
    """Test the base bridge leaves ask_yes_no for subclasses to implement."""
    bridge = _bridge([])
    with pytest.raises(NotImplementedError):
        YesNoUiBridge.ask_yes_no(bridge, 'Sure?', False)


def test_ask_text_default() -> None:
    """Test an empty answer returns the given default."""
    assert _ask_text(_bridge(['']), 'Q', default='D') == 'D'


def test_ask_text_allow_empty() -> None:
    """Test an empty answer is accepted when empty is allowed."""
    assert _ask_text(_bridge(['']), 'Q', allow_empty=True) == ''


def test_ask_text_reask() -> None:
    """Test an empty required answer is re-asked until non-empty."""
    assert _ask_text(_bridge(['', 'value']), 'Q') == 'value'


def test_ask_number_minimum() -> None:
    """Test a value below the minimum is re-asked."""
    assert _ask_number(_bridge(['-1', '5']), 'Q', 1.0, 0.0, None) == 5.0


def test_ask_number_maximum() -> None:
    """Test a value above the maximum is re-asked."""
    assert _ask_number(_bridge(['2', '0.5']), 'Q', 1.0, 0.0, 1.0) == 0.5


def test_ask_int_reask() -> None:
    """Test a non-integer and a too-small value are both re-asked."""
    assert _ask_int(_bridge(['x', '0', '5']), 'Q', 10, 1) == 5


def test_ask_opt_date() -> None:
    """Test an empty answer gives None and a bad date is re-asked."""
    assert _ask_opt_date(_bridge(['']), 'Q') is None
    assert _ask_opt_date(_bridge(['bad', '2026-01-02']), 'Q') == \
        date(2026, 1, 2)


def test_ask_choice_bad_index() -> None:
    """Test an out-of-range numeric choice is re-asked."""
    assert _ask_choice(_bridge(['9', '1']), 'Q', ['a', 'b']) == 'a'


def test_ask_choice_bad_name() -> None:
    """Test an unmatched name choice is re-asked until it matches."""
    assert _ask_choice(_bridge(['zzz', 'a']), 'Q', ['a', 'b']) == 'a'


def test_team_with_extras() -> None:
    """Test a team with an alias, a dated member and an fte exception.

    This exercises adding an alias, re-asking a membership end date that
    is before the start date, and adding a full-time-equivalent exception.
    """
    answers = [
        '', '', '', '', '', '', '',
        '',
        'y', 'Ada', '',
        '',
        'y', 'T', '', '', '',
        'y', 'Alpha', '',
        'y',
        'Ada', '',
        '2026-07-01',
        '2026-06-01', '2026-07-10',
        'y', '2026-07-02', '2026-07-05', '0.5',
        '',
        '']
    teams = _run(answers)
    team = teams.teams[0]
    assert team.aliases == ['Alpha']
    member = team.members[0]
    assert member.start_date == date(2026, 7, 1)
    assert member.end_date == date(2026, 7, 10)
    assert member.fte_exceptions[0].fte == 0.5


CSV_OPTS = [''] * 7
"""Blank answers for the seven CSV TableIO options."""


def test_preset_wizard() -> None:
    """Test the config wizard collects input and output TableIO presets.

    The run rejects an invalid preset name and a duplicate name, and adds
    one column-name mapping, covering the preset-collection helpers.
    """
    answers = (['', '', '', '', '', '', '', '', '', '']
               + ['y', 'in name', 'in1', '1'] + CSV_OPTS
               + ['y', 'Type', 'level', '']
               + ['y', 'in1', 'in2', '1'] + CSV_OPTS + ['']
               + ['']
               + ['y', 'out1', '1'] + CSV_OPTS + ['']
               + [''])
    config = teams_config_wizard(_bridge(answers))
    assert isinstance(config, AvailableTeamsConfig)
    assert sorted(config.input_configs) == ['in1', 'in2']
    assert list(config.output_configs) == ['out1']
    assert config.input_configs['in1'].to_internal == {'Type': 'level'}
