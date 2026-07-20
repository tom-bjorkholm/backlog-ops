#! /usr/local/bin/python3
"""Tests for the full-config and preset stages of the wizard.

These end-to-end tests drive the full backlog-ops configuration wizard
and the stand-alone preset wizard through a scripted console bridge,
covering the input and output presets, the levels, the status maps, the
GUI rename tables, the stage headings and the package re-exports.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import importlib
import pytest
import backlogops
from backlogops import InputFormatConfig, OutputFormatConfig, Status
from backlogops.backlog_ops_config import BacklogOpsConfig, \
    DEF_STATUS_INPUT_MAP
from backlogops.backlog_ops_wizard import (
    backlog_ops_wizard, _WORKFORCE_HEAD, _INPUT_PRESETS_HEAD,
    _OUTPUT_PRESETS_HEAD)
from backlogops.io_preset_wizard import preset_wizard, _preset_direction
from backlogops.levels import DEFAULT_LEVELS, LevelDisplay
from .wizard_test_helpers import (
    COMPANY, CONFIG_HEADS, CSV_OPTS, GUI_MAPS_KEEP, JIRA_SKIP, LEVELS_KEEP,
    MAPS_KEEP, SCHED, STATUS_KEEP, bridge, config_stdout, run_config,
    teams_stdout)


def test_preset_direction() -> None:
    """Test a default preset's type selects the stand-alone direction."""
    assert _preset_direction(InputFormatConfig()) == 'input'
    assert _preset_direction(OutputFormatConfig()) == 'output'
    assert _preset_direction(None) is None


def test_preset_wizard() -> None:
    """Test the config wizard collects input and output TableIO presets.

    The run rejects an invalid preset name, adds one input preset whose
    backlog rename table reads file column ``Type`` into ``level`` while
    its releases table is kept, adds one output preset that accepts both
    pre-filled rename tables and a numeric level display, accepts the
    default levels, accepts both GUI rename tables, and finally selects a
    name-only GUI level display.
    """
    answers = (COMPANY + ['0', '0']
               + ['1']
               + ['in name', 'in1'] + ['1'] + CSV_OPTS
               + ['2', 'Type', ''] + [''] + STATUS_KEEP
               + ['1']
               + ['out1'] + ['1'] + CSV_OPTS
               + MAPS_KEEP + ['numeric']
               + LEVELS_KEEP + STATUS_KEEP
               + MAPS_KEEP + ['name'] + JIRA_SKIP)
    config = backlog_ops_wizard(bridge(answers))
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
    answers = (COMPANY + ['0', '0', '0']
               + ['1']
               + ['out1'] + ['1'] + CSV_OPTS
               + edit_backlog + [''] + ['both']
               + LEVELS_KEEP + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(bridge(answers))
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
    answers = (COMPANY + ['0', '0', '0', '0']
               + LEVELS_KEEP + STATUS_KEEP
               + edit_backlog + [''] + ['both'] + JIRA_SKIP)
    config = backlog_ops_wizard(bridge(answers))
    gui = config.gui_display
    assert gui.backlog_to_external == {'key': 'Id', 'team': None}
    assert gui.release_to_external == {}


def test_levels_default() -> None:
    """Test accepting the pre-filled default levels stores None."""
    answers = (COMPANY + ['0', '0', '0', '0'] + LEVELS_KEEP
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(bridge(answers))
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
    answers = (COMPANY + ['0', '0', '0', '0'] + edit_first + ['']
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(bridge(answers))
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
    answers = (COMPANY + ['0', '0', '0', '0'] + add_row + ['']
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(bridge(answers))
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
    answers = (COMPANY + ['0', '0', '0', '0'] + fix
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config, errors = run_config(answers)
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
    answers = (COMPANY + ['0', '0', '0', '0'] + fix
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config, errors = run_config(answers)
    assert 'duplicates' in errors
    assert config.get_levels()[0].name == 'Chore'


def test_input_rename_wizard() -> None:
    """Test an input preset maps, drops and adds backlog file columns.

    Row 1 (key) reads file column ``Issue ID``; an added blank-field row
    drops file column ``Junk``; another added row reads ``My Note`` into
    the extra field ``note``. The releases table is kept unchanged.
    """
    edit_backlog = ['1', 'Issue ID', ':+', '', 'Junk', ':+', 'note',
                    'My Note']
    answers = (COMPANY + ['0', '0']
               + ['1'] + ['in1'] + ['1'] + CSV_OPTS
               + edit_backlog + [''] + [''] + STATUS_KEEP
               + ['0']
               + LEVELS_KEEP + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(bridge(answers))
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
    answers = (COMPANY + ['0', '0', '0', '0'] + LEVELS_KEEP
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    out = config_stdout(answers)
    positions = [out.find(head) for head in CONFIG_HEADS]
    assert all(out.count(head) == 1 for head in CONFIG_HEADS)
    assert positions == sorted(positions)


def test_stage_heads_presets() -> None:
    """Test the stage headings still appear with input and output presets.

    A run that adds one input and one output preset shows every stage
    heading once and in the order the stages are collected.
    """
    answers = (COMPANY + ['0', '0']
               + ['1'] + ['in name', 'in1'] + ['1'] + CSV_OPTS
               + ['2', 'Type', ''] + [''] + STATUS_KEEP
               + ['1'] + ['out1'] + ['1'] + CSV_OPTS
               + MAPS_KEEP + ['numeric']
               + LEVELS_KEEP + STATUS_KEEP + MAPS_KEEP + ['name'] + JIRA_SKIP)
    out = config_stdout(answers)
    positions = [out.find(head) for head in CONFIG_HEADS]
    assert all(out.count(head) == 1 for head in CONFIG_HEADS)
    assert positions == sorted(positions)


def test_workforce_head_only() -> None:
    """Test the workforce wizard shows only the workforce heading.

    The workforce-only wizard collects just the workforce, so it announces
    that one stage and none of the later full-config stage headings.
    """
    out = teams_stdout(SCHED + ['', '', ''])
    assert out.count(_WORKFORCE_HEAD) == 1
    assert all(head not in out for head in CONFIG_HEADS[1:])


def test_head_repeats_on_back() -> None:
    """Test a back step re-announces the stage it steps back into.

    Going back from the output-preset count re-enters the input-preset
    stage, so the trail shows the workforce heading once but the input and
    output headings twice, and still reaches every stage.
    """
    answers = (COMPANY + ['0', '0', '0'] + [':b'] + ['0', '0']
               + LEVELS_KEEP + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    out = config_stdout(answers)
    assert out.count(_WORKFORCE_HEAD) == 1
    assert out.count(_INPUT_PRESETS_HEAD) == 2
    assert out.count(_OUTPUT_PRESETS_HEAD) == 2
    assert all(head in out for head in CONFIG_HEADS)


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
    config = preset_wizard(bridge(answers))
    assert isinstance(config, InputFormatConfig)
    assert config.backlog_to_internal == {'Type': 'level'}
    assert not config.release_to_internal


def test_preset_output() -> None:
    """Test the preset wizard builds an output preset with a display.

    The direction is output; the CSV format is kept; both rename tables
    are accepted unchanged and the level display is set to numeric.
    """
    answers = ['output', '1'] + CSV_OPTS + MAPS_KEEP + ['numeric']
    config = preset_wizard(bridge(answers))
    assert isinstance(config, OutputFormatConfig)
    assert config.level_display == LevelDisplay.NUMERIC
    assert not config.backlog_to_external
    assert not config.release_to_external


def test_preset_default_input() -> None:
    """Test a blank direction answer defaults to an empty input preset."""
    answers = [''] + ['1'] + CSV_OPTS + MAPS_KEEP + STATUS_KEEP
    config = preset_wizard(bridge(answers))
    assert isinstance(config, InputFormatConfig)
    assert not config.backlog_to_internal
    assert not config.release_to_internal


def test_preset_abort() -> None:
    """Test aborting the preset wizard ends with an end-of-input error."""
    with pytest.raises(EOFError):
        preset_wizard(bridge([':q']))


def test_preset_reexport() -> None:
    """Test the package re-exports the preset wizard."""
    assert backlogops.preset_wizard is preset_wizard
    assert 'preset_wizard' in backlogops.__all__


def test_global_status_wizard() -> None:
    """Test the wizard captures a global status map with an added row."""
    add = [':+', 'Reviewing', 'IN_PROGRESS', '']
    answers = (COMPANY + ['0', '0', '0', '0'] + LEVELS_KEEP
               + add + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(bridge(answers))
    expected = {**DEF_STATUS_INPUT_MAP, 'Reviewing': Status.IN_PROGRESS}
    assert config.status_input_map == expected


def test_global_status_def() -> None:
    """Test accepting the global status table keeps the default map."""
    answers = (COMPANY + ['0', '0', '0', '0'] + LEVELS_KEEP
               + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(bridge(answers))
    assert config.status_input_map == DEF_STATUS_INPUT_MAP


def test_in_preset_status() -> None:
    """Test an input preset captures its own status override map."""
    add = [':+', 'Spike', 'TODO', '']
    answers = (COMPANY + ['0', '0']
               + ['1'] + ['in1'] + ['1'] + CSV_OPTS
               + MAPS_KEEP + add
               + ['0']
               + LEVELS_KEEP + STATUS_KEEP + GUI_MAPS_KEEP + JIRA_SKIP)
    config = backlog_ops_wizard(bridge(answers))
    assert config.input_configs['in1'].status_input_map == {
        'Spike': Status.TODO}


def test_preset_input_status() -> None:
    """Test the stand-alone input preset wizard captures a status map."""
    add = [':+', 'Testing', 'DONE', '']
    answers = ['input', '1'] + CSV_OPTS + MAPS_KEEP + add
    config = preset_wizard(bridge(answers))
    assert isinstance(config, InputFormatConfig)
    assert config.status_input_map == {'Testing': Status.DONE}


def test_config_abort() -> None:
    """Test aborting the full config wizard ends with an end-of-input error."""
    with pytest.raises(EOFError):
        backlog_ops_wizard(bridge([':q']))
