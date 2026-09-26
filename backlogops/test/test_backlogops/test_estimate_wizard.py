#! /usr/local/bin/python3
"""Tests for the wizard questions about how backlog items are estimated.

The table readers of a guess by level are fed tables by the
:class:`TableScript` bridge, so their whole-table re-ask paths run. The
remaining time section, the focus factor of a team and the display forms
are driven through the full configuration wizard with a scripted console.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import timedelta
from typing import Optional
import pytest
from wizard_ui_bridge import TableCell, WizardUiBridgeConsole
from backlogops import BacklogOpsConfig, DefaultStoryPoints, LevelDisplay, \
    RemainingTimeConfig
from backlogops.backlog_ops_wizard import backlog_ops_wizard
from backlogops.estimate_wizard import _POINTS_KIND, _guess_check, \
    _parse_points, _parse_time, _read_def_points, _read_guess, \
    _remaining_rule, _team_focus_rule, _time_kind
from backlogops.no_text_io import NoTextIO
from backlogops.wizard_forms import FormResult
from .shared_test_data import def_times
from .wizard_test_helpers import COMPANY, CSV_OPTS, GUI_KEEP, GUI_MAPS_KEEP, \
    JIRA_SKIP, LEVELS_KEEP, MAPS_KEEP, POINTS_SKIP, REMAINING_OFF, \
    STATUS_KEEP, TableScript, bridge

AFTER_TEAMS = (['0', '0'] + LEVELS_KEEP + POINTS_SKIP + STATUS_KEEP
               + GUI_MAPS_KEEP + JIRA_SKIP)
"""No presets, then every later stage of the wizard kept at its default."""

NO_TEAMS = COMPANY + ['0', '0'] + AFTER_TEAMS
"""A workforce of no persons and no teams, then every later default."""


def one_team(team_form: list[str]) -> list[str]:
    """Return the answers of a workforce of Ada in one team, then defaults.

    Args:
        team_form: The answers of the team form: name, member and alias
            counts, velocity, sprint length, and the focus fields when
            they are asked.

    Returns:
        The answers from the company work hours to the end of the wizard.
    """
    return (COMPANY + ['1', 'Ada', '0', '1'] + team_form
            + ['ada', '', '', '', '0'] + [''] + AFTER_TEAMS)


@pytest.mark.parametrize('text, expected', [
    ('2', 2.0),
    (' 0.5 ', 0.5),
    ('x', None),
    ('', None),
    (None, None)])
def test_parse_points(text: Optional[str], expected: Optional[float]) -> None:
    """Test a story points cell is read as a number, or not at all."""
    assert _parse_points(text) == expected


@pytest.mark.parametrize('text, expected', [
    ('1:30:00', timedelta(hours=1, minutes=30)),
    (' 1d ', timedelta(days=1)),
    ('1:30', None),
    ('', None),
    (None, None)])
def test_parse_time(text: Optional[str],
                    expected: Optional[timedelta]) -> None:
    """Test a remaining time cell is read as a time, or not at all."""
    assert _parse_time(text) == expected


@pytest.mark.parametrize('position, ok', [
    ((0, 0), True),
    ((1, 0), False),
    ((0, 1), True),
    ((1, 1), False)])
def test_def_points_check(position: tuple[int, int], ok: bool) -> None:
    """Test each cell of the guess table is checked as it is entered."""
    table: list[list[Optional[str]]] = [['1', '2'], ['x', 'y']]
    assert _guess_check(_POINTS_KIND, table, position)[0] is ok


@pytest.mark.parametrize('position, ok', [
    ((0, 1), True),
    ((1, 1), False)])
def test_time_check(position: tuple[int, int], ok: bool) -> None:
    """Test a remaining time cell is checked as it is entered."""
    table: list[list[Optional[str]]] = [['1', '1d 2:00:00'], ['2', '2h']]
    assert _guess_check(_time_kind(0.3), table, position)[0] is ok


def test_def_points_reask() -> None:
    """Test an unreadable guess table is re-asked until it parses."""
    scripted = TableScript([[['x', '2']], [['1', 'y']], [['1', '2']]])
    points = _read_def_points(scripted, False, False)
    assert points.get_default_story_points(1) == 2.0


def test_def_points_seeded() -> None:
    """Test a stored guess pre-fills a row per level it gives."""
    scripted = TableScript([[['1', '2']], [['1', '2.5']]])
    stored = _read_def_points(scripted, False, False)
    _read_def_points(scripted, False, False, stored)
    assert scripted.seen[1] == [[TableCell(value='1'), TableCell(value='2')]]


def test_def_points_no_seed() -> None:
    """Test a guess that gives no level starts the table empty.

    Two empty rows are offered when a level is to be filled in, because
    a factor is worked out from two levels.
    """
    scripted = TableScript([[['1', '2'], ['3', '8']]])
    empty = DefaultStoryPoints(stderr_file=NoTextIO())
    _read_def_points(scripted, True, False, empty)
    assert scripted.seen[0] == [[TableCell(value=''), TableCell(value='')],
                                [TableCell(value=''), TableCell(value='')]]


def test_time_table_reask() -> None:
    """Test an unreadable or refused time table is re-asked.

    The first table has a time that cannot be read, and the second gives
    one level twice, which validating the configuration refuses.
    """
    scripted = TableScript([[['1', '1:30']],
                            [['1', '1:00:00'], ['1', '2:00:00']],
                            [['1', '1:30:00']]])
    config = _read_guess(scripted, _time_kind(0.4), False, False)
    assert config.enable_remaining_time is True
    assert config.default_focus_factor == 0.4
    assert config.get_default_time(1) == timedelta(hours=1, minutes=30)
    assert len(scripted.seen) == 3


def test_time_seeded_as_hours() -> None:
    """Test a stored time pre-fills its row as hours:minutes:seconds."""
    scripted = TableScript([[['1', '1:00:00']]])
    seed = def_times({1: 25.5})
    _read_guess(scripted, _time_kind(0.3), False, False, seed)
    assert scripted.seen[0] == [[TableCell(value='1'),
                                 TableCell(value='25:30:00')]]


@pytest.mark.parametrize('values, disabled', [
    ({'enable': False, 'guess': True},
     {'focus', 'guess', 'interpolate', 'extrapolate'}),
    ({'enable': True, 'guess': False}, {'interpolate', 'extrapolate'}),
    ({'enable': True, 'guess': True}, set())])
def test_remaining_rule(values: dict[str, object], disabled: set[str]) -> None:
    """Test the remaining time form disables what is not used."""
    assert _remaining_rule(FormResult(values)) == (None, disabled)


@pytest.mark.parametrize('values, disabled', [
    ({}, {'focus'}),
    ({'own_focus': False}, {'focus'}),
    ({'own_focus': True}, set())])
def test_team_focus_rule(values: dict[str, object],
                         disabled: set[str]) -> None:
    """Test the team form asks a focus factor only for a team's own."""
    assert _team_focus_rule(FormResult(values)) == (None, disabled)


def test_remaining_off() -> None:
    """Test not also estimating in remaining time leaves it unused."""
    config = backlog_ops_wizard(bridge(REMAINING_OFF + NO_TEAMS))
    remaining = config.remaining_time
    assert remaining.enable_remaining_time is False
    assert not remaining.levels
    assert remaining.default_focus_factor == 0.3


def test_remaining_no_guess() -> None:
    """Test remaining time can be used without a guess by level."""
    answers = ['y', '0.5', ''] + NO_TEAMS
    remaining = backlog_ops_wizard(bridge(answers)).remaining_time
    assert remaining.enable_remaining_time is True
    assert remaining.default_focus_factor == 0.5
    assert not remaining.levels
    assert remaining.get_default_time(1) is None


def test_remaining_table() -> None:
    """Test the time table stores two levels and fills in between them.

    The two empty rows are filled with level 1 at two hours and level 3
    at one day, which is written back as hours, and both filling-in
    questions are left at yes, so level 2 is guessed at between.
    """
    fill = ['y', '', 'y', '', '', '1', '1', '2:00:00', '2', '3', '1d', '']
    remaining = backlog_ops_wizard(bridge(fill + NO_TEAMS)).remaining_time
    assert remaining.enable_remaining_time is True
    assert remaining.default_focus_factor == 0.3
    assert [(one.level, one.remaining_time) for one in remaining.levels] \
        == [(1, timedelta(hours=2)), (3, timedelta(hours=24))]
    guess = remaining.get_default_time(2)
    assert guess is not None
    assert guess / timedelta(hours=1) == pytest.approx(48 ** 0.5)


def test_remaining_seeded() -> None:
    """Test stored remaining time pre-fills the form and the table."""
    fill = ['y', '0.4', 'y', 'n', 'n', '1', '5', '3:00:00', '']
    first = backlog_ops_wizard(bridge(fill + NO_TEAMS))
    kept = ['', '', '', '', '', ''] + NO_TEAMS
    again = backlog_ops_wizard(bridge(kept), default=first).remaining_time
    assert again.enable_remaining_time is True
    assert again.default_focus_factor == 0.4
    assert [(one.level, one.remaining_time) for one in again.levels] == \
        [(5, timedelta(hours=3))]


def test_focus_out_of_range() -> None:
    """Test a focus factor out of range is asked again.

    Zero and 3.5 are outside the range from 0.005 to 3.0, which the
    question names, and 2.5 is inside it.
    """
    answers = ['y', '0', '3.5', '2.5', ''] + NO_TEAMS
    shown = io.StringIO()
    stdin = io.StringIO('\n'.join(answers) + '\n')
    config = backlog_ops_wizard(WizardUiBridgeConsole(shown, stdin,
                                                      io.StringIO()))
    assert shown.getvalue().count('Focus factor (0.005 to 3.0)') == 3
    assert config.remaining_time.default_focus_factor == 2.5


def test_team_own_focus() -> None:
    """Test a team is asked for, and keeps, a focus factor of its own."""
    team_form = ['T', '1', '0', '', '', 'y', '0.6']
    config = backlog_ops_wizard(bridge(['y', '', ''] + one_team(team_form)))
    assert config.available_teams.teams[0].focus_factor == 0.6


def test_team_default_focus() -> None:
    """Test a team without a focus factor of its own stores none."""
    team_form = ['T', '1', '0', '', '', '']
    config = backlog_ops_wizard(bridge(['y', '', ''] + one_team(team_form)))
    assert config.available_teams.teams[0].focus_factor is None


def test_team_focus_not_asked() -> None:
    """Test a team is not asked for a focus factor without remaining time.

    A team that had a focus factor of its own keeps it, because nothing
    was asked about it.
    """
    team_form = ['T', '1', '0', '', '', 'y', '0.6']
    first = backlog_ops_wizard(bridge(['y', '', ''] + one_team(team_form)))
    first.remaining_time = RemainingTimeConfig(stderr_file=NoTextIO())
    kept = REMAINING_OFF + one_team(['', '', '', '', ''])
    again = backlog_ops_wizard(bridge(kept), default=first)
    assert again.remaining_time.enable_remaining_time is False
    assert again.available_teams.teams[0].focus_factor == 0.6


def _output_run(display: list[str]) -> BacklogOpsConfig:
    """Return a configuration of one output preset and the given GUI."""
    answers = (REMAINING_OFF + COMPANY + ['0', '0', '0', '1', 'out1', '1']
               + CSV_OPTS + MAPS_KEEP + ['numeric', 'y'] + LEVELS_KEEP
               + POINTS_SKIP + STATUS_KEEP + MAPS_KEEP + display + JIRA_SKIP)
    return backlog_ops_wizard(bridge(answers))


def test_display_omit_asked() -> None:
    """Test the output and GUI display forms store the omit setting.

    The output preset is told to leave out empty columns, and the GUI to
    show them, the opposite of what each of them does by default.
    """
    config = _output_run(['name', 'n'])
    output = config.output_configs['out1']
    assert output.level_display is LevelDisplay.NUMERIC
    assert output.omit_none_column is True
    assert config.gui_display.level_display is LevelDisplay.NAME
    assert config.gui_display.omit_none_column is False


def test_display_omit_default() -> None:
    """Test a kept GUI display form leaves out empty columns."""
    gui = _output_run(GUI_KEEP).gui_display
    assert gui.level_display is LevelDisplay.BOTH
    assert gui.omit_none_column is True
