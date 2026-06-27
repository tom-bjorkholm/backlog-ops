#! /usr/local/bin/python3
"""Tests for the interactive AvailableTeams wizard."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
from typing import Optional
import pytest
from tableio_cfg_json import WizardUiBridgeConsole
from backlogops.available_teams import AvailableTeams
from backlogops.backlog_ops_config import BacklogOpsConfig
from backlogops.available_teams_wizard import (
    available_teams_wizard, teams_config_wizard)
from backlogops.available_teams_wizard import (
    _backlog_map_fields, _parse_column_renames, _read_int, _read_number,
    _read_opt_date, _read_text)
from backlogops.levels import DEFAULT_LEVELS, LevelDisplay
from backlogops.work_hours import DEFAULT_WORK_WEEK, WeekDay

GUI_KEEP = ['']
"""A blank answer that keeps the default GUI level display (both)."""

MAPS_KEEP = ['', '']
"""Blank answers that accept a pre-filled backlog and releases map."""

GUI_MAPS_KEEP = MAPS_KEEP + GUI_KEEP
"""Accept both GUI rename tables, then keep the GUI level display."""

LEVELS_KEEP = ['']
"""A blank answer that accepts the pre-filled default levels table."""

SCHED = [''] * 7
"""Blank answers that keep the seven default daily work hours."""

CSV_OPTS = [''] * 7
"""Blank answers for the CSV format encoding and six option cells."""


def _bridge(answers: list[str]) -> WizardUiBridgeConsole:
    """Return a console bridge scripted with the given answers."""
    stdin = io.StringIO('\n'.join(answers) + '\n')
    return WizardUiBridgeConsole(io.StringIO(), stdin, io.StringIO())


def _run(answers: list[str]) -> AvailableTeams:
    """Run the wizard with scripted console answers and return the result."""
    return available_teams_wizard(_bridge(answers))


def _run_config(answers: list[str]) -> tuple[BacklogOpsConfig, str]:
    """Run the config wizard, returning the config and the stderr text."""
    stderr = io.StringIO()
    stdin = io.StringIO('\n'.join(answers) + '\n')
    bridge = WizardUiBridgeConsole(io.StringIO(), stdin, stderr)
    return teams_config_wizard(bridge), stderr.getvalue()


def test_minimal_workforce() -> None:
    """Test an all-default run yields an empty workforce with defaults."""
    teams = _run(SCHED + ['', '', ''])
    assert not teams.persons
    assert not teams.teams
    assert teams.company_work_hours.work_hours == DEFAULT_WORK_WEEK


def test_schedule_edit() -> None:
    """Test an edited work-hours cell overrides that day's default."""
    teams = _run(['6'] + [''] * 6 + ['', '', ''])
    work_hours = teams.company_work_hours.work_hours
    assert work_hours[WeekDay.MONDAY] == 6.0
    assert work_hours[WeekDay.TUESDAY] == 8.0


def test_full_workforce() -> None:
    """Test a full run builds the persons, team, and memberships."""
    answers = (SCHED + ['0']
               + ['2', 'Ada', '0', 'Bo', '0']
               + ['1']
               + ['Phoenix']
               + ['2']
               + ['1', '', '', '', '0']
               + ['1', '0.5', '', '', '0']
               + ['30', '', '']
               + ['0'])
    teams = _run(answers)
    assert sorted(teams.persons) == ['ada', 'bo']
    team = teams.teams[0]
    assert team.name == 'Phoenix'
    assert team.velocity == 30.0
    assert team.sum_fte_at_velocity == 2.0
    assert [(m.person_name, m.fte) for m in team.members] == \
        [('Ada', 1.0), ('Bo', 0.5)]


def test_choose_by_name() -> None:
    """Test a membership can select a person by typing the name."""
    answers = (SCHED + ['0']
               + ['1', 'Ada', '0']
               + ['1']
               + ['T']
               + ['1']
               + ['ada', '', '', '', '0']
               + ['', '', '']
               + ['0'])
    teams = _run(answers)
    assert teams.teams[0].members[0].person_name == 'Ada'


def test_duplicate_name() -> None:
    """Test entering a duplicate person name is rejected and re-asked."""
    answers = (SCHED + ['0']
               + ['2', 'Ada', '0', 'ada', 'Bo', '0']
               + ['0'])
    teams = _run(answers)
    assert sorted(teams.persons) == ['ada', 'bo']


def test_reask_number() -> None:
    """Test a non-numeric velocity is rejected and then accepted."""
    answers = (SCHED + ['0', '0']
               + ['1']
               + ['Phoenix']
               + ['abc', '5']
               + ['', '']
               + ['0'])
    teams = _run(answers)
    assert teams.teams[0].velocity == 5.0


def test_company_exc() -> None:
    """Test a company exception with re-asked invalid date and end order."""
    answers = (SCHED
               + ['1']
               + ['bad', '2026-01-01']
               + ['2025-12-31', '2026-01-05']
               + ['']
               + ['maybe', 'n']
               + ['0', '0'])
    teams = _run(answers)
    exception = teams.company_work_hours.exceptions[0]
    assert exception.start_date == date(2026, 1, 1)
    assert exception.end_date == date(2026, 1, 5)
    assert exception.new_work_days is False


def test_vacation() -> None:
    """Test a personal vacation exception is captured for the person."""
    answers = (SCHED + ['0']
               + ['1', 'Ada']
               + ['1']
               + ['2026-07-01', '2026-07-20', '0', 'n']
               + ['0'])
    teams = _run(answers)
    vacation = teams.persons['ada'].exceptions[0]
    assert vacation.start_date == date(2026, 7, 1)
    assert vacation.end_date == date(2026, 7, 20)
    assert teams.company_work_hours.work_hours[WeekDay.MONDAY] == 8.0


def test_team_with_extras() -> None:
    """Test a team with an alias, a dated member and an fte exception.

    This exercises adding an alias, re-asking a membership end date that
    is before the start date, and adding a full-time-equivalent exception.
    """
    answers = (SCHED + ['0']
               + ['1', 'Ada', '0']
               + ['1']
               + ['T']
               + ['1']
               + ['Ada', '']
               + ['2026-07-01']
               + ['2026-06-01', '2026-07-10']
               + ['1']
               + ['2026-07-02', '2026-07-05', '0.5']
               + ['', '', '']
               + ['1', 'Alpha'])
    teams = _run(answers)
    team = teams.teams[0]
    assert team.aliases == ['Alpha']
    member = team.members[0]
    assert member.start_date == date(2026, 7, 1)
    assert member.end_date == date(2026, 7, 10)
    assert member.fte_exceptions[0].fte == 0.5


def test_back_navigation() -> None:
    """Test a back request re-asks the most recently answered question."""
    answers = (SCHED + ['0']
               + ['1', 'Wrong', ':b', 'Ada', '0']
               + ['0'])
    teams = _run(answers)
    assert sorted(teams.persons) == ['ada']


def test_cancel_level() -> None:
    """Test cancelling a level restarts that item from its first question."""
    answers = (SCHED + ['0']
               + ['1', 'Tmp', ':c', 'Ada', '0']
               + ['0'])
    teams = _run(answers)
    assert sorted(teams.persons) == ['ada']


def test_cancel_to_count() -> None:
    """Test cancelling a level from an item re-asks the group's count.

    Cancelling at the second person's name returns to the person count
    question and re-asks the whole group, so the first person entered is
    discarded.
    """
    answers = (SCHED + ['0']
               + ['2', 'Sam', '0', ':c', '1', 'Ada', '0']
               + ['0'])
    teams = _run(answers)
    assert sorted(teams.persons) == ['ada']


def test_no_outer_level() -> None:
    """Test cancelling at a top-level count reports there is no outer level."""
    stdin = io.StringIO('\n'.join(SCHED + ['0', ':c', '0', '0']) + '\n')
    stdout = io.StringIO()
    teams = available_teams_wizard(
        WizardUiBridgeConsole(stdout, stdin, io.StringIO()))
    assert not teams.persons
    assert 'no outer level' in stdout.getvalue().lower()


def test_abort() -> None:
    """Test an abort request ends the wizard with an end-of-input error."""
    with pytest.raises(EOFError):
        _run([':q'])


def test_read_text_default() -> None:
    """Test an empty answer returns the given default."""
    assert _read_text(_bridge(['']), 'Q', 'D', False) == 'D'


def test_read_text_empty() -> None:
    """Test an empty answer is accepted when empty is allowed."""
    assert _read_text(_bridge(['']), 'Q', None, True) == ''


def test_read_text_reask() -> None:
    """Test an empty required answer is re-asked until non-empty."""
    assert _read_text(_bridge(['', 'value']), 'Q', None, False) == 'value'


def test_read_number_minimum() -> None:
    """Test a value below the minimum is re-asked."""
    assert _read_number(_bridge(['-1', '5']), 'Q', 1.0, 0.0, None) == 5.0


def test_read_number_maximum() -> None:
    """Test a value above the maximum is re-asked."""
    assert _read_number(_bridge(['2', '0.5']), 'Q', 1.0, 0.0, 1.0) == 0.5


def test_read_int_reask() -> None:
    """Test a non-integer and a too-small value are both re-asked."""
    assert _read_int(_bridge(['x', '0', '5']), 'Q', 10, 1, None) == 5


def test_read_opt_date() -> None:
    """Test an empty answer gives None and a bad date is re-asked."""
    assert _read_opt_date(_bridge(['']), 'Q', None) is None
    assert _read_opt_date(_bridge(['bad', '2026-01-02']), 'Q', None) == \
        date(2026, 1, 2)


def test_preset_wizard() -> None:
    """Test the config wizard collects input and output TableIO presets.

    The run rejects an invalid preset name, adds one input preset with one
    column-name mapping, adds one output preset that accepts both
    pre-filled rename tables and a numeric level display, accepts the
    default levels, accepts both GUI rename tables, and finally selects a
    name-only GUI level display.
    """
    answers = (SCHED + ['0', '0', '0']
               + ['1']
               + ['in name', 'in1'] + ['1'] + CSV_OPTS
               + ['1', 'Type', 'level']
               + ['1']
               + ['out1'] + ['1'] + CSV_OPTS
               + MAPS_KEEP + ['numeric']
               + LEVELS_KEEP
               + MAPS_KEEP + ['name'])
    config = teams_config_wizard(_bridge(answers))
    assert isinstance(config, BacklogOpsConfig)
    assert sorted(config.input_configs) == ['in1']
    assert list(config.output_configs) == ['out1']
    assert config.input_configs['in1'].to_internal == {'Type': 'level'}
    output = config.output_configs['out1']
    assert output.level_display == LevelDisplay.NUMERIC
    assert output.backlog_to_external == {}
    assert output.release_to_external == {}
    assert config.gui_display.level_display == LevelDisplay.NAME


def test_output_rename_wizard() -> None:
    """Test an output preset renames, drops and adds backlog columns.

    The internal-field column is read-only, so editing a known row asks
    only its output column. Row 1 (key) is renamed to ``Id``, row 5
    (story_points) is erased to drop it, and an added row maps the extra
    field ``note`` to ``Notes``, while the releases table is kept as-is.
    """
    edit_backlog = ['1', 'Id', '5', ':e', ':+', 'note', 'Notes', '']
    answers = (SCHED + ['0', '0', '0', '0']
               + ['1']
               + ['out1'] + ['1'] + CSV_OPTS
               + edit_backlog + [''] + ['both']
               + LEVELS_KEEP + GUI_MAPS_KEEP)
    config = teams_config_wizard(_bridge(answers))
    output = config.output_configs['out1']
    assert output.backlog_to_external == {'key': 'Id', 'story_points': None,
                                          'note': 'Notes'}
    assert output.release_to_external == {}


def test_gui_rename_wizard() -> None:
    """Test the GUI rename tables store a backlog rename and a drop.

    Editing the read-only known rows asks only the shown-column cell, so
    row 1 (key) is renamed to ``Id`` and row 9 (team) is erased to hide it.
    """
    edit_backlog = ['1', 'Id', '9', ':e', '']
    answers = (SCHED + ['0', '0', '0', '0', '0']
               + LEVELS_KEEP
               + edit_backlog + [''] + ['both'])
    config = teams_config_wizard(_bridge(answers))
    gui = config.gui_display
    assert gui.backlog_to_external == {'key': 'Id', 'team': None}
    assert gui.release_to_external == {}


def test_levels_default() -> None:
    """Test accepting the pre-filled default levels stores None."""
    answers = (SCHED + ['0', '0', '0', '0', '0'] + LEVELS_KEEP
               + GUI_MAPS_KEEP)
    config = teams_config_wizard(_bridge(answers))
    assert config.levels is None
    assert config.get_levels() == DEFAULT_LEVELS
    assert config.gui_display.level_display == LevelDisplay.BOTH
    assert config.gui_display.backlog_to_external == {}
    assert config.gui_display.release_to_external == {}


def test_levels_edited_stored() -> None:
    """Test editing a level name stores the levels and keeps the rest.

    Row 1 of the pre-filled default table is edited to rename the level,
    keeping its number and aliases, so the stored levels differ from the
    defaults and are kept as a list.
    """
    edit_first = ['1', '', 'Chore', '']
    answers = (SCHED + ['0', '0', '0', '0', '0'] + edit_first + ['']
               + GUI_MAPS_KEEP)
    config = teams_config_wizard(_bridge(answers))
    assert config.levels is not None
    levels = config.get_levels()
    assert levels[0].name == 'Chore'
    assert levels[1].name == 'Story'
    assert levels[1].aliases == ['Task', 'Bug', 'Defect']


def test_levels_added() -> None:
    """Test a negative-numbered level can be added in the wizard.

    A new row is appended and filled with a negative level number, a
    name and a two-alias comma separated cell, then the table is
    accepted.
    """
    add_row = [':+', '-1', 'Spike', 'Research, Investigation']
    answers = (SCHED + ['0', '0', '0', '0', '0'] + add_row + ['']
               + GUI_MAPS_KEEP)
    config = teams_config_wizard(_bridge(answers))
    assert config.levels is not None
    levels = config.get_levels()
    assert levels[-1].name == 'Spike'
    assert levels[-1].aliases == ['Research', 'Investigation']


def test_levels_dup_number() -> None:
    """Test a repeated level number is reported and re-asked.

    Row 2 is edited to reuse level number 0, which the whole-table check
    rejects, then re-edited to a free number, so the table is accepted.
    """
    fix = ['2', '0', '', '', '', '2', '7', '', '', '']
    answers = SCHED + ['0', '0', '0', '0', '0'] + fix + GUI_MAPS_KEEP
    config, errors = _run_config(answers)
    assert 'more than once' in errors
    levels = config.get_levels()
    assert levels[7].name == 'Story'
    assert levels[7].aliases == ['Task', 'Bug', 'Defect']


def test_levels_dup_name() -> None:
    """Test a duplicate level name is reported and re-asked.

    Row 1 is renamed to an existing level name, which the whole-table
    check rejects, then renamed to a unique name, so it is accepted.
    """
    fix = ['1', '', 'Story', '', '', '1', '', 'Chore', '', '']
    answers = SCHED + ['0', '0', '0', '0', '0'] + fix + GUI_MAPS_KEEP
    config, errors = _run_config(answers)
    assert 'duplicates' in errors
    assert config.get_levels()[0].name == 'Chore'


def test_backlog_map_fields() -> None:
    """Test the backlog rename fields offer level and level name first."""
    fields = _backlog_map_fields()
    assert fields[0] == 'key'
    assert fields[1:3] == ['level', 'level name']
    assert 'extra_fields' not in fields


def test_rename_three_cases() -> None:
    """Test equal keeps, a change renames and a blank drops a column."""
    table: list[list[Optional[str]]] = [['key', 'key'], ['level', 'Size'],
                                        ['title', None]]
    assert _parse_column_renames(table) == {'level': 'Size', 'title': None}


def test_rename_blank_source() -> None:
    """Test a row without an internal field name is ignored."""
    table: list[list[Optional[str]]] = [[None, 'X'], ['key', 'key']]
    assert _parse_column_renames(table) == {}


def test_rename_empty_target() -> None:
    """Test an empty-string output column drops the field."""
    table: list[list[Optional[str]]] = [['key', '']]
    assert _parse_column_renames(table) == {'key': None}


def test_rename_dup_source() -> None:
    """Test a repeated internal field rejects the whole table."""
    table: list[list[Optional[str]]] = [['key', 'A'], ['key', 'B']]
    assert _parse_column_renames(table) is None


def test_rename_dup_target() -> None:
    """Test two columns sharing a name rejects the whole table."""
    table: list[list[Optional[str]]] = [['key', 'X'], ['title', 'X']]
    assert _parse_column_renames(table) is None
