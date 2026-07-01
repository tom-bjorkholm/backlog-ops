#! /usr/local/bin/python3
"""Tests for the interactive backlog-ops configuration wizard."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import importlib
import io
from datetime import date
from typing import Optional, Sequence, TextIO
import pytest
from tableio_cfg_json import TableCell, TableColumn, WizardBack, \
    WizardUiBridge, WizardUiBridgeConsole
import backlogops
from backlogops import InputFormatConfig, OutputFormatConfig, Status
from backlogops.available_teams import AvailableTeams
from backlogops.backlog_ops_config import BacklogOpsConfig
from backlogops.backlog_ops_wizard import (
    available_teams_wizard, backlog_ops_wizard, _WORKFORCE_HEAD,
    _INPUT_PRESETS_HEAD, _OUTPUT_PRESETS_HEAD, _LEVELS_HEAD, _STATUS_MAP_HEAD,
    _GUI_DISPLAY_HEAD, _JIRA_HEAD)
from backlogops.io_preset_wizard import preset_wizard
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType
from backlogops.wizard_helpers import (
    _backlog_map_fields, _parse_column_renames, _parse_input_renames,
    _parse_status_map, _read_int, _read_jira_map, _read_number,
    _read_opt_date, _read_text, _status_target)
from backlogops.wizard_helpers import (
    _Navigator, _is_nonneg, _parse_level_int, _parse_levels, _parse_schedule,
    _read_end_date, _read_levels, _read_preset_name, _read_renames,
    _read_schedule, _read_status_map, _read_unique_name, _rename_check,
    _sched_check, _split_aliases, _status_check)
from backlogops.levels import DEFAULT_LEVELS, LevelDisplay
from backlogops.work_hours import DEFAULT_WORK_WEEK, WeekDay

GUI_KEEP = ['']
"""A blank answer that keeps the default GUI level display (both)."""

MAPS_KEEP = ['', '']
"""Blank answers that accept a pre-filled backlog and releases map."""

GUI_MAPS_KEEP = MAPS_KEEP + GUI_KEEP
"""Accept both GUI rename tables, then keep the GUI level display."""

JIRA_SKIP = ['0', '0']
"""Zero Jira connections and zero column maps, which skips presets too."""

LEVELS_KEEP = ['']
"""A blank answer that accepts the pre-filled default levels table."""

STATUS_KEEP = ['']
"""A blank answer that accepts an empty (no extra names) status map."""

SCHED = [''] * 7
"""Blank answers that keep the seven default daily work hours."""

CSV_OPTS = [''] * 7
"""Blank answers for the CSV format encoding and six option cells."""

_CONFIG_HEADS = [
    _WORKFORCE_HEAD, _INPUT_PRESETS_HEAD, _OUTPUT_PRESETS_HEAD,
    _LEVELS_HEAD, _STATUS_MAP_HEAD, _GUI_DISPLAY_HEAD, _JIRA_HEAD]
"""The full-config wizard stage headings, in collection order."""


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
    return backlog_ops_wizard(bridge), stderr.getvalue()


def _config_stdout(answers: list[str]) -> str:
    """Run the config wizard and return what was shown on stdout."""
    stdout = io.StringIO()
    stdin = io.StringIO('\n'.join(answers) + '\n')
    backlog_ops_wizard(WizardUiBridgeConsole(stdout, stdin, io.StringIO()))
    return stdout.getvalue()


def _teams_stdout(answers: list[str]) -> str:
    """Run the workforce wizard and return what was shown on stdout."""
    stdout = io.StringIO()
    stdin = io.StringIO('\n'.join(answers) + '\n')
    available_teams_wizard(WizardUiBridgeConsole(stdout, stdin, io.StringIO()))
    return stdout.getvalue()


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

    The run rejects an invalid preset name, adds one input preset whose
    backlog rename table reads file column ``Type`` into ``level`` while
    its releases table is kept, adds one output preset that accepts both
    pre-filled rename tables and a numeric level display, accepts the
    default levels, accepts both GUI rename tables, and finally selects a
    name-only GUI level display.
    """
    answers = (SCHED + ['0', '0', '0']
               + ['1']
               + ['in name', 'in1'] + ['1'] + CSV_OPTS
               + ['2', 'Type', ''] + [''] + STATUS_KEEP
               + ['1']
               + ['out1'] + ['1'] + CSV_OPTS
               + MAPS_KEEP + ['numeric']
               + LEVELS_KEEP + STATUS_KEEP
               + MAPS_KEEP + ['name'] + JIRA_SKIP)
    config = backlog_ops_wizard(_bridge(answers))
    assert isinstance(config, BacklogOpsConfig)
    assert sorted(config.input_configs) == ['in1']
    assert list(config.output_configs) == ['out1']
    in_config = config.input_configs['in1']
    assert in_config.backlog_to_internal == {'Type': 'level'}
    assert in_config.release_to_internal == {}
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
               + LEVELS_KEEP + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(_bridge(answers))
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
               + LEVELS_KEEP + STATUS_KEEP
               + edit_backlog + [''] + ['both'] + JIRA_SKIP)
    config = backlog_ops_wizard(_bridge(answers))
    gui = config.gui_display
    assert gui.backlog_to_external == {'key': 'Id', 'team': None}
    assert gui.release_to_external == {}


def test_levels_default() -> None:
    """Test accepting the pre-filled default levels stores None."""
    answers = (SCHED + ['0', '0', '0', '0', '0'] + LEVELS_KEEP
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(_bridge(answers))
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
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(_bridge(answers))
    assert config.levels is not None
    levels = config.get_levels()
    assert levels[0].name == 'Chore'
    assert levels[1].name == 'Story'
    assert levels[1].aliases == ['Task', 'Bug', 'Defect', 'Uppgift']


def test_levels_added() -> None:
    """Test a negative-numbered level can be added in the wizard.

    A new row is appended and filled with a negative level number, a
    name and a two-alias comma separated cell, then the table is
    accepted.
    """
    add_row = [':+', '-1', 'Spike', 'Research, Investigation']
    answers = (SCHED + ['0', '0', '0', '0', '0'] + add_row + ['']
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(_bridge(answers))
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
    answers = (SCHED + ['0', '0', '0', '0', '0'] + fix
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config, errors = _run_config(answers)
    assert 'more than once' in errors
    levels = config.get_levels()
    assert levels[7].name == 'Story'
    assert levels[7].aliases == ['Task', 'Bug', 'Defect', 'Uppgift']


def test_levels_dup_name() -> None:
    """Test a duplicate level name is reported and re-asked.

    Row 1 is renamed to an existing level name, which the whole-table
    check rejects, then renamed to a unique name, so it is accepted.
    """
    fix = ['1', '', 'Story', '', '', '1', '', 'Chore', '', '']
    answers = (SCHED + ['0', '0', '0', '0', '0'] + fix
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
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


def test_in_rename_cases() -> None:
    """Test equal omits, a change maps and a blank field drops a column."""
    table: list[list[Optional[str]]] = [['key', 'key'], ['level', 'Type'],
                                        ['', 'Junk']]
    assert _parse_input_renames(table) == {'Type': 'level', 'Junk': None}


def test_in_rename_extra() -> None:
    """Test an added row reads a file column into an extra field."""
    table: list[list[Optional[str]]] = [['note', 'My Note']]
    assert _parse_input_renames(table) == {'My Note': 'note'}


def test_in_rename_absent() -> None:
    """Test a field with a blank file column is left unmapped."""
    table: list[list[Optional[str]]] = [['key', ''], ['level', 'L']]
    assert _parse_input_renames(table) == {'L': 'level'}


def test_in_rename_shared() -> None:
    """Test several file columns may map to the same internal field."""
    table: list[list[Optional[str]]] = [['level', 'Size'], ['level', 'Type']]
    assert _parse_input_renames(table) == {'Size': 'level', 'Type': 'level'}


def test_in_rename_dup_src() -> None:
    """Test a repeated file column rejects the whole table."""
    table: list[list[Optional[str]]] = [['key', 'X'], ['level', 'X']]
    assert _parse_input_renames(table) is None


def test_input_rename_wizard() -> None:
    """Test an input preset maps, drops and adds backlog file columns.

    Row 1 (key) reads file column ``Issue ID``; an added blank-field row
    drops file column ``Junk``; another added row reads ``My Note`` into
    the extra field ``note``. The releases table is kept unchanged.
    """
    edit_backlog = ['1', 'Issue ID', ':+', '', 'Junk', ':+', 'note',
                    'My Note']
    answers = (SCHED + ['0', '0', '0']
               + ['1'] + ['in1'] + ['1'] + CSV_OPTS
               + edit_backlog + [''] + [''] + STATUS_KEEP
               + ['0']
               + LEVELS_KEEP + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(_bridge(answers))
    in_config = config.input_configs['in1']
    assert in_config.backlog_to_internal == {'Issue ID': 'key', 'Junk': None,
                                             'My Note': 'note'}
    assert in_config.release_to_internal == {}


def test_stage_heads_order() -> None:
    """Test a default config run shows each stage heading once, in order.

    A fully default run announces the workforce, the input and output
    presets, the levels, the status map and the GUI display, each exactly
    once and in the order the stages are collected.
    """
    answers = (SCHED + ['0', '0', '0', '0', '0'] + LEVELS_KEEP
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    out = _config_stdout(answers)
    positions = [out.find(head) for head in _CONFIG_HEADS]
    assert all(out.count(head) == 1 for head in _CONFIG_HEADS)
    assert positions == sorted(positions)


def test_stage_heads_presets() -> None:
    """Test the stage headings still appear with input and output presets.

    A run that adds one input and one output preset shows every stage
    heading once and in the order the stages are collected.
    """
    answers = (SCHED + ['0', '0', '0']
               + ['1'] + ['in name', 'in1'] + ['1'] + CSV_OPTS
               + ['2', 'Type', ''] + [''] + STATUS_KEEP
               + ['1'] + ['out1'] + ['1'] + CSV_OPTS
               + MAPS_KEEP + ['numeric']
               + LEVELS_KEEP + STATUS_KEEP + MAPS_KEEP + ['name'] + JIRA_SKIP)
    out = _config_stdout(answers)
    positions = [out.find(head) for head in _CONFIG_HEADS]
    assert all(out.count(head) == 1 for head in _CONFIG_HEADS)
    assert positions == sorted(positions)


def test_workforce_head_only() -> None:
    """Test the workforce wizard shows only the workforce heading.

    The workforce-only wizard collects just the workforce, so it announces
    that one stage and none of the later full-config stage headings.
    """
    out = _teams_stdout(SCHED + ['', '', ''])
    assert out.count(_WORKFORCE_HEAD) == 1
    assert all(head not in out for head in _CONFIG_HEADS[1:])


def test_head_repeats_on_back() -> None:
    """Test a back step re-announces the stage it steps back into.

    Going back from the output-preset count re-enters the input-preset
    stage, so the trail shows the workforce heading once but the input and
    output headings twice, and still reaches every stage.
    """
    answers = (SCHED + ['0', '0', '0', '0'] + [':b'] + ['0', '0']
               + LEVELS_KEEP + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    out = _config_stdout(answers)
    assert out.count(_WORKFORCE_HEAD) == 1
    assert out.count(_INPUT_PRESETS_HEAD) == 2
    assert out.count(_OUTPUT_PRESETS_HEAD) == 2
    assert all(head in out for head in _CONFIG_HEADS)


def test_wizard_reexport() -> None:
    """Test the package re-exports the wizard under its new name only.

    The full-config wizard is reachable from the top-level package and is
    the very function defined in the renamed module, while the old
    ``teams_config_wizard`` name is no longer exported.
    """
    assert backlogops.backlog_ops_wizard is backlog_ops_wizard
    assert 'backlog_ops_wizard' in backlogops.__all__
    assert not hasattr(backlogops, 'teams_config_wizard')
    assert 'teams_config_wizard' not in backlogops.__all__


def test_old_module_gone() -> None:
    """Test the misleadingly named old wizard module no longer exists."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module('backlogops.available_teams_wizard')


def test_preset_input() -> None:
    """Test the preset wizard builds an input preset with a rename.

    The direction is input; the CSV format is kept; the backlog table
    reads file column ``Type`` into ``level`` and the releases table is
    kept unchanged.
    """
    answers = ['input', '1'] + CSV_OPTS + ['2', 'Type', ''] + [''] \
        + STATUS_KEEP
    config = preset_wizard(_bridge(answers))
    assert isinstance(config, InputFormatConfig)
    assert config.backlog_to_internal == {'Type': 'level'}
    assert not config.release_to_internal


def test_preset_output() -> None:
    """Test the preset wizard builds an output preset with a display.

    The direction is output; the CSV format is kept; both rename tables
    are accepted unchanged and the level display is set to numeric.
    """
    answers = ['output', '1'] + CSV_OPTS + MAPS_KEEP + ['numeric']
    config = preset_wizard(_bridge(answers))
    assert isinstance(config, OutputFormatConfig)
    assert config.level_display == LevelDisplay.NUMERIC
    assert not config.backlog_to_external
    assert not config.release_to_external


def test_preset_default_input() -> None:
    """Test a blank direction answer defaults to an empty input preset."""
    answers = [''] + ['1'] + CSV_OPTS + MAPS_KEEP + STATUS_KEEP
    config = preset_wizard(_bridge(answers))
    assert isinstance(config, InputFormatConfig)
    assert not config.backlog_to_internal
    assert not config.release_to_internal


def test_preset_abort() -> None:
    """Test aborting the preset wizard ends with an end-of-input error."""
    with pytest.raises(EOFError):
        preset_wizard(_bridge([':q']))


def test_preset_reexport() -> None:
    """Test the package re-exports the preset wizard."""
    assert backlogops.preset_wizard is preset_wizard
    assert 'preset_wizard' in backlogops.__all__


@pytest.mark.parametrize('text,expected', [
    ('TODO', 'TODO'), ('todo', 'TODO'), (' In_Progress ', 'IN_PROGRESS'),
    ('done', 'DONE'), ('bogus', None), (None, None)])
def test_status_target(text: Optional[str], expected: Optional[str]) -> None:
    """Test the internal status name is matched, trimmed and case-folded."""
    assert _status_target(text) == expected


def test_parse_status_ok() -> None:
    """Test a status table maps names to Status, accepting any case."""
    table: list[list[Optional[str]]] = [['Testing', 'IN_PROGRESS'],
                                        ['Spike', 'todo']]
    assert _parse_status_map(table) == {'Testing': Status.IN_PROGRESS,
                                        'Spike': Status.TODO}


def test_parse_status_blank() -> None:
    """Test a row with a blank file status name is ignored."""
    table: list[list[Optional[str]]] = [[None, 'TODO'], ['Testing', 'DONE']]
    assert _parse_status_map(table) == {'Testing': Status.DONE}


def test_parse_status_empty() -> None:
    """Test an empty status table yields an empty map."""
    assert _parse_status_map([]) == {}


def test_parse_status_bad() -> None:
    """Test an unknown internal status rejects the whole table."""
    assert _parse_status_map([['Testing', 'Nonsense']]) is None


def test_parse_status_dup() -> None:
    """Test a case-insensitive duplicate file status name is rejected."""
    table: list[list[Optional[str]]] = [['Testing', 'DONE'],
                                        ['TESTING', 'TODO']]
    assert _parse_status_map(table) is None


def test_global_status_wizard() -> None:
    """Test the wizard captures the global status map from a added row."""
    add = [':+', 'Testing', 'IN_PROGRESS', '']
    answers = (SCHED + ['0', '0', '0', '0', '0'] + LEVELS_KEEP
               + add + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(_bridge(answers))
    assert config.status_input_map == {'Testing': Status.IN_PROGRESS}


def test_in_preset_status() -> None:
    """Test an input preset captures its own status override map."""
    add = [':+', 'Spike', 'TODO', '']
    answers = (SCHED + ['0', '0', '0']
               + ['1'] + ['in1'] + ['1'] + CSV_OPTS
               + MAPS_KEEP + add
               + ['0']
               + LEVELS_KEEP + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(_bridge(answers))
    assert config.input_configs['in1'].status_input_map == {
        'Spike': Status.TODO}


def test_preset_input_status() -> None:
    """Test the stand-alone input preset wizard captures a status map."""
    add = [':+', 'Testing', 'DONE', '']
    answers = ['input', '1'] + CSV_OPTS + MAPS_KEEP + add
    config = preset_wizard(_bridge(answers))
    assert isinstance(config, InputFormatConfig)
    assert config.status_input_map == {'Testing': Status.DONE}


def test_config_abort() -> None:
    """Test aborting the full config wizard ends with an end-of-input error."""
    with pytest.raises(EOFError):
        backlog_ops_wizard(_bridge([':q']))


def test_back_at_start() -> None:
    """Test a back request before any answer simply restarts the body."""
    nav = _Navigator(_bridge([]))
    calls: list[int] = []

    def body(_nav: _Navigator) -> str:
        """Raise back once, then return on the replayed run."""
        calls.append(1)
        if len(calls) == 1:
            raise WizardBack()
        return 'done'
    assert nav.run(body) == 'done'
    assert len(calls) == 2


def test_nav_error_file() -> None:
    """Test the navigator exposes the bridge's diagnostics stream."""
    errors = io.StringIO()
    bridge = WizardUiBridgeConsole(io.StringIO(), io.StringIO(), errors)
    assert _Navigator(bridge).error_file() is errors


@pytest.mark.parametrize('text, expected', [
    (None, False), ('abc', False), ('-1', False), ('0', True),
    ('3.5', True)])
def test_is_nonneg(text: Optional[str], expected: bool) -> None:
    """Test only a parseable number that is at least zero is accepted."""
    assert _is_nonneg(text) is expected


@pytest.mark.parametrize('table, pos, ok', [
    ([['Mon', '8']], (0, 0), True),
    ([['Mon', '8']], (0, 1), True),
    ([['Mon', 'x']], (0, 1), False)])
def test_sched_check(table: list[list[Optional[str]]], pos: tuple[int, int],
                     ok: bool) -> None:
    """Test only the work-hours column is checked, rejecting non-numbers."""
    assert _sched_check(table, pos)[0] is ok


def test_parse_sched_bad() -> None:
    """Test a non-numeric work-hours cell makes the schedule invalid."""
    assert _parse_schedule([WeekDay.MONDAY], [['Mon', 'x']]) is None


@pytest.mark.parametrize('table, pos, ok', [
    ([['', 'X']], (0, 1), False),
    ([['key', 'X']], (0, 1), True),
    ([['', 'X']], (0, 0), True)])
def test_rename_check(table: list[list[Optional[str]]], pos: tuple[int, int],
                      ok: bool) -> None:
    """Test an output column with no internal field name is rejected."""
    assert _rename_check(table, pos)[0] is ok


@pytest.mark.parametrize('text, expected', [
    (None, None), ('abc', None), (' 5 ', 5), ('-2', -2)])
def test_parse_level_int(text: Optional[str], expected: Optional[int]) -> None:
    """Test a signed whole number parses, anything else gives None."""
    assert _parse_level_int(text) == expected


@pytest.mark.parametrize('text, expected', [
    (None, []), ('', []), (' a , , b ', ['a', 'b'])])
def test_split_aliases(text: Optional[str], expected: list[str]) -> None:
    """Test aliases split on commas, trimming blanks; None gives empty."""
    assert _split_aliases(text) == expected


def test_parse_levels_bad() -> None:
    """Test a level row with a bad number or a blank name is invalid."""
    assert _parse_levels([['x', 'Name', '']]) is None
    assert _parse_levels([['1', '', '']]) is None


@pytest.mark.parametrize('table, pos, ok', [
    ([['n', 'BAD']], (0, 1), False),
    ([['', 'TODO']], (0, 1), False),
    ([['n', 'TODO']], (0, 1), True),
    ([['', '']], (0, 1), True)])
def test_status_check(table: list[list[Optional[str]]], pos: tuple[int, int],
                      ok: bool) -> None:
    """Test a status row is flagged for a bad target or a missing name."""
    assert _status_check(table, pos)[0] is ok


def test_read_end_date_bad() -> None:
    """Test an unparseable end date is re-asked until it is a valid date."""
    bridge = _bridge(['nope', '2026-01-05'])
    assert _read_end_date(bridge, 'Q', date(2026, 1, 1)) == date(2026, 1, 5)


def test_read_name_empty() -> None:
    """Test an empty person name is re-asked until a name is entered."""
    assert _read_unique_name(_bridge(['', 'Ada']), 'Q', {}) == 'Ada'


def test_read_preset_dup() -> None:
    """Test a preset name already in use is re-asked until it is free."""
    assert _read_preset_name(_bridge(['used', 'fresh']), 'Q', {'used'}) == \
        'fresh'


class _TableScript(WizardUiBridge):
    """A bridge that returns queued raw tables for each ask_table call.

    It hands the wizard an invalid table first and a valid one next,
    which the real console bridge's per-cell checks never produce, so the
    whole-table re-ask path of the read helpers can be exercised.
    """

    def __init__(self, tables: list[list[list[Optional[str]]]]) -> None:
        """Store the tables to return in order and a diagnostics sink."""
        self._tables = tables
        self._index = 0
        self._errors = io.StringIO()

    def ask_table(self, columns: Sequence[TableColumn],
                  cells: list[list[TableCell]], question: str,
                  **kwargs: object) -> list[list[Optional[str]]]:
        """Return the next queued table, ignoring the prompt details."""
        _ = (columns, cells, question, kwargs)
        table = self._tables[self._index]
        self._index += 1
        return table

    def error_file(self) -> TextIO:
        """Return the diagnostics stream used for level validation."""
        return self._errors

    def show(self, message: str) -> None:
        """Ignore any message shown while a table is being re-asked."""
        _ = message


def test_sched_reask() -> None:
    """Test an invalid schedule table is re-asked until it parses."""
    bridge = _TableScript([[['Mon', 'x']], [['Mon', '8']]])
    assert _read_schedule(bridge) == {WeekDay.MONDAY: 8.0}


def test_levels_reask() -> None:
    """Test an unparseable levels table is re-asked until it is valid."""
    bridge = _TableScript([[['x', 'N', '']], [['1', 'Story', '']]])
    assert [level.name for level in _read_levels(bridge)] == ['Story']


def test_renames_reask() -> None:
    """Test a rename table with a repeated field is re-asked until valid.

    The valid table keeps every field at its own name, so it renames
    nothing and the resulting map is empty.
    """
    bridge = _TableScript([[['key', 'X'], ['key', 'Y']], [['key', 'key']]])
    assert not _read_renames(bridge, ['key', 'title'], False, 'External',
                             False)


def test_status_reask() -> None:
    """Test a status table missing its target is re-asked until valid."""
    bridge = _TableScript([[['Name', '']], [['Name', 'TODO']]])
    assert _read_status_map(bridge, 'Q?') == {'Name': Status.TODO}


def test_jira_map_reask() -> None:
    """Test an invalid Jira column-map table is re-asked until it parses."""
    bridge = _TableScript([[['key', 'ATTRIBUTE', '']],
                           [['key', 'ATTRIBUTE', 'key']]])
    result = _read_jira_map(bridge, ['key'], {})
    assert result == {'key': JiraAttrPath(JiraAttrType.ATTRIBUTE, ('key',))}
