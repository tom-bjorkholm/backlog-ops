#! /usr/local/bin/python3
"""Tests for the wizard field readers, table parsers and navigator basics.

The focused tests check the single-value readers, the whole-table parsers
and per-cell checks, and the navigator's back-at-start and diagnostics
stream. The :class:`TableScript` bridge feeds the read helpers an invalid
table then a valid one, so their whole-table re-ask paths run.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
from typing import Optional
import pytest
from tableio_cfg_json import TableCell, WizardBack, WizardUiBridgeConsole
from backlogops import Status
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType
from backlogops.levels import DEFAULT_LEVELS
from backlogops.work_hours import ExceptionWorkHours, WeekDay
from backlogops.wizard_navigator import _Navigator
from backlogops.wizard_helpers import (
    _backlog_map_fields, _parse_column_renames, _parse_input_renames,
    _parse_status_map, _read_int, _read_jira_map, _read_text, _status_target)
from backlogops.wizard_helpers import (
    _RenameKind, _is_nonneg, _parse_level_int, _parse_levels, _parse_schedule,
    _read_exceptions, _read_levels, _read_preset_name, _read_renames,
    _read_schedule, _read_status_map, _rename_check, _sched_check,
    _split_aliases, _status_check)
from backlogops.wizard_helpers import (
    _issue_type_cells, _parse_issue_types, _read_issue_type_map)
from .wizard_test_helpers import TableScript, bridge


def test_read_text_default() -> None:
    """Test an empty answer returns the given default."""
    assert _read_text(bridge(['']), 'Q', 'D', False) == 'D'


def test_read_text_empty() -> None:
    """Test an empty answer is accepted when empty is allowed."""
    assert _read_text(bridge(['']), 'Q', None, True) == ''


def test_read_text_reask() -> None:
    """Test an empty required answer is re-asked until non-empty."""
    assert _read_text(bridge(['', 'value']), 'Q', None, False) == 'value'


def test_read_int_reask() -> None:
    """Test a non-integer and a too-small value are both re-asked."""
    assert _read_int(bridge(['x', '0', '5']), 'Q', 10, 1, None) == 5


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


def test_back_at_start() -> None:
    """Test a back request before any answer simply restarts the body."""
    nav = _Navigator(bridge([]))
    calls: list[int] = []

    def body(_nav: _Navigator, _default: object) -> str:
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
    scripted = WizardUiBridgeConsole(io.StringIO(), io.StringIO(), errors)
    assert _Navigator(scripted).error_file() is errors


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


def test_read_preset_dup() -> None:
    """Test a preset name already in use is re-asked until it is free."""
    assert _read_preset_name(bridge(['used', 'fresh']), 'Q', {'used'}) == \
        'fresh'


def test_sched_reask() -> None:
    """Test an invalid schedule table is re-asked until it parses."""
    scripted = TableScript([[['Mon', 'x']], [['Mon', '8']]])
    assert _read_schedule(scripted) == {WeekDay.MONDAY: 8.0}


def test_exceptions_reask() -> None:
    """Test an end-before-start exception table is re-asked until valid."""
    scripted = TableScript([[['2026-01-06', '2026-01-05', '', 'no']],
                            [['2026-01-01', '2026-01-05', '', 'no']]])
    result = _read_exceptions(scripted, 'Periods?')
    assert result[0].start_date == date(2026, 1, 1)
    assert result[0].end_date == date(2026, 1, 5)


def test_levels_reask() -> None:
    """Test an unparseable levels table is re-asked until it is valid."""
    scripted = TableScript([[['x', 'N', '']], [['1', 'Story', '']]])
    assert [level.name for level in _read_levels(scripted)] == ['Story']


def test_renames_reask() -> None:
    """Test a rename table with a repeated field is re-asked until valid.

    The valid table keeps every field at its own name, so it renames
    nothing and the resulting map is empty.
    """
    scripted = TableScript([[['key', 'X'], ['key', 'Y']], [['key', 'key']]])
    kind = _RenameKind(['key', 'title'], False, 'External', False)
    assert not _read_renames(scripted, kind)


def test_status_reask() -> None:
    """Test a status table missing its target is re-asked until valid."""
    scripted = TableScript([[['Name', '']], [['Name', 'TODO']]])
    assert _read_status_map(scripted, 'Q?') == {'Name': Status.TODO}


def test_status_default_cells() -> None:
    """Test a status map question starts with its default rows."""
    scripted = TableScript([[['To Do', 'TODO']]])
    assert _read_status_map(scripted, 'Q?', {'To Do': Status.TODO}) == {
        'To Do': Status.TODO}
    assert scripted.seen[0] == [[TableCell(value='To Do'),
                                 TableCell(value='TODO')]]


def test_jira_map_reask() -> None:
    """Test an invalid Jira column-map table is re-asked until it parses."""
    scripted = TableScript([[['key', 'ATTRIBUTE', '']],
                            [['key', 'ATTRIBUTE', 'key']]])
    result = _read_jira_map(scripted, ['key'], {})
    assert result == {
        'key': (JiraAttrPath(JiraAttrType.ATTRIBUTE, ('key',)),)}


def test_itmap_cells() -> None:
    """Test the issue-type table seeds a row per level, name as default."""
    cells = _issue_type_cells(DEFAULT_LEVELS)
    assert cells[0] == [TableCell(value='0'), TableCell(value='Sub-Task'),
                        TableCell(value='Sub-Task')]
    assert [row[0].value for row in cells] == ['0', '1', '2', '3']


def test_itmap_read() -> None:
    """Test an edited issue type overrides the level name for that level."""
    scripted = TableScript([[['0', 'Sub-Task', 'Deluppgift'],
                             ['1', 'Story', 'Story']]])
    assert _read_issue_type_map(scripted, DEFAULT_LEVELS) == {0: 'Deluppgift'}


@pytest.mark.parametrize('table, expected', [
    ([['0', 'Sub-Task', 'Deluppgift']], {0: 'Deluppgift'}),
    ([['1', 'Story', 'Story']], {}),
    ([['2', 'Epic', '']], {}),
    ([['2', 'Epic', '  Epos  ']], {2: 'Epos'}),
    ([['x', 'Bad', 'Type']], {})])
def test_itmap_parse(table: list[list[Optional[str]]],
                     expected: dict[int, str]) -> None:
    """Test only real overrides are kept and identity rows are dropped."""
    assert _parse_issue_types(table) == expected


def test_exceptions_seeded() -> None:
    """Test a seed period pre-fills the exception table rows shown."""
    seed = [ExceptionWorkHours(start_date=date(2026, 1, 1),
                               end_date=date(2026, 1, 5), hours_per_day=4.0,
                               new_work_days=True)]
    scripted = TableScript([[['2026-01-01', '2026-01-05', '4', 'yes']]])
    assert _read_exceptions(scripted, 'Periods?', seed) == seed
    assert scripted.seen[0] == [[TableCell(value='2026-01-01'),
                                 TableCell(value='2026-01-05'),
                                 TableCell(value='4'),
                                 TableCell(value='yes')]]


def test_output_rename_seeded() -> None:
    """Test a stored output map pre-fills rows and blanks a dropped one.

    A field present in the seed shows its stored target, a dropped field
    shows a blank target, a field absent from the seed keeps its own name,
    and a stored key that is no longer a field is kept as an extra row.
    """
    fields = ['key', 'title', 'note']
    seed: dict[str, Optional[str]] = {'key': 'Key', 'title': None,
                                      'extra': 'Extra'}
    kind = _RenameKind(fields, True, 'External', False)
    scripted = TableScript([[['key', 'key']]])
    _read_renames(scripted, kind, seed)
    assert scripted.seen[0] == [
        [TableCell(value='key'), TableCell(value='Key')],
        [TableCell(value='title'), TableCell(value='')],
        [TableCell(value='note'), TableCell(value='note')],
        [TableCell(value='extra'), TableCell(value='Extra')]]


def test_input_rename_seeded() -> None:
    """Test a stored input map pre-fills rows, incl. shared and dropped.

    Each file column shows against its internal field, a field with no
    stored source keeps its own name, a source for a no-longer field is
    kept as an extra row, and a dropped source shows a blank field.
    """
    fields = ['key', 'title']
    seed: dict[str, Optional[str]] = {'Key col': 'key',
                                      'Extra src': 'gone', 'Junk': None}
    kind = _RenameKind(fields, True, 'File column', True)
    scripted = TableScript([[['key', 'key']]])
    _read_renames(scripted, kind, seed)
    assert scripted.seen[0] == [
        [TableCell(value='key'), TableCell(value='Key col')],
        [TableCell(value='title'), TableCell(value='title')],
        [TableCell(value='gone'), TableCell(value='Extra src')],
        [TableCell(value=''), TableCell(value='Junk')]]
