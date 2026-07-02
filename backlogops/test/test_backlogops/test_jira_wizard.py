#! /usr/local/bin/python3
"""Tests for the Jira section of the configuration wizard.

The full-config tests drive the wizard from a default prefix of answers
into the Jira stage. The focused tests drive the connection and preset
collectors directly, and the unit tests check the column-map table
parsing and the per-cell validation.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from typing import Optional
import pytest
from tableio_cfg_json import WizardUiBridgeConsole
from backlogops.backlog_ops_wizard import backlog_ops_wizard
from backlogops.jira_io_config import (
    JiraAttrPath, JiraAttrType, default_jira_filter)
from backlogops.jira_wizard import (
    _build_connections, _build_from_presets, _build_to_presets)
from backlogops.wizard_helpers import (
    _Navigator, _attr_from_cells, _jira_map_check, _parse_jira_map)

_PREFIX = [''] * 7 + ['0', '0', '0', '0', '0'] + ['', '', '', '', '']
"""Default answers for the wizard stages that precede the Jira stage."""

JIRA_FULL = (['1', 'main', 'cloud', 'https://x.atlassian.net', 'me@x.com',
              'clear_internal', 'TOK']
             + ['1', 'bk', '']
             + ['1', 'rel', '']
             + ['1', 'scrum', 'main', 'bk', 'rel', 'SCRUM', 'P = 1']
             + ['1', 'scrumw', 'main', 'bk', 'rel', 'SCRUM'])
"""Jira-stage answers for a connection, a backlog map, a release map and
one read and one write preset."""


def _console(answers: list[str],
             errors: Optional[io.StringIO] = None) -> WizardUiBridgeConsole:
    """Return a console bridge scripted with answers and an error sink."""
    text = '\n'.join(answers) + '\n'
    sink = errors if errors is not None else io.StringIO()
    return WizardUiBridgeConsole(io.StringIO(), io.StringIO(text), sink)


def test_jira_skip() -> None:
    """Test a run with no Jira connections leaves the Jira config empty."""
    config = backlog_ops_wizard(_console(_PREFIX + ['0', '0', '0']))
    jira = config.get_jira_config()
    assert not jira.connections
    assert not jira.backlog_column_maps
    assert not jira.release_column_maps
    assert not jira.from_jira_presets
    assert not jira.to_jira_presets


def test_jira_full() -> None:
    """Test the wizard builds a connection, maps and read/write presets."""
    errors = io.StringIO()
    config = backlog_ops_wizard(_console(_PREFIX + JIRA_FULL, errors))
    jira = config.get_jira_config()
    assert sorted(jira.connections) == ['main']
    assert sorted(jira.backlog_column_maps) == ['bk']
    assert sorted(jira.release_column_maps) == ['rel']
    conn = jira.connections['main']
    assert conn.base_url == 'https://x.atlassian.net'
    assert conn.get_token() == 'TOK'
    status_path = JiraAttrPath(JiraAttrType.FIELD, ('status', 'name'))
    assert jira.backlog_column_maps['bk']['status'] == (status_path,)
    assert jira.get_preset('scrum').def_project == 'SCRUM'
    write_preset = jira.get_write_preset('scrumw')
    assert write_preset.backlog_column_map_name == 'bk'
    assert write_preset.def_project == 'SCRUM'
    assert 'WARNING' in errors.getvalue()


def test_conn_encrypted() -> None:
    """Test an encrypted-internal connection stores the token encrypted."""
    answers = ['1', 'enc', 'cloud', 'https://x', 'me@x',
               'encrypted_internal', 'SECRET', 'phrase']
    conn = _Navigator(_console(answers)).run(_build_connections)['enc']
    assert conn.uses_encryption()
    assert conn.stored_token not in (None, 'SECRET')
    assert conn.get_token() == 'SECRET'


def test_conn_file() -> None:
    """Test a file-storage connection records the path and asks no token."""
    answers = ['1', 'f', 'cloud', 'https://x', 'me@x', 'clear_file',
               '/tmp/tok.txt']
    conn = _Navigator(_console(answers)).run(_build_connections)['f']
    assert conn.uses_token_file()
    assert conn.token_file_path == '/tmp/tok.txt'
    assert conn.stored_token is None


def test_from_preset() -> None:
    """Test the read-preset collector ties a connection and two maps."""
    answers = ['1', 'p1', 'c1', 'm1', 'm2', 'PROJ', 'filter']
    nav = _Navigator(_console(answers))
    presets = nav.run(lambda n: _build_from_presets(n, ['c1'], ['m1'], ['m2']))
    preset = presets['p1']
    assert preset.connection_name == 'c1'
    assert preset.backlog_column_map_name == 'm1'
    assert preset.release_column_map_name == 'm2'
    assert preset.def_project == 'PROJ'
    assert preset.def_filter == 'filter'


def test_preset_def_filter() -> None:
    """Test a blank preset filter defaults to the project rank filter."""
    answers = ['1', 'p1', 'c1', 'm1', 'm2', 'PROJ', '']
    nav = _Navigator(_console(answers))
    presets = nav.run(lambda n: _build_from_presets(n, ['c1'], ['m1'], ['m2']))
    assert presets['p1'].def_filter == default_jira_filter('PROJ')


def test_to_preset() -> None:
    """Test the write-preset collector asks no issue filter."""
    answers = ['1', 'p1', 'c1', 'm1', 'm2', 'PROJ']
    nav = _Navigator(_console(answers))
    presets = nav.run(lambda n: _build_to_presets(n, ['c1'], ['m1'], ['m2']))
    preset = presets['p1']
    assert preset.connection_name == 'c1'
    assert preset.backlog_column_map_name == 'm1'
    assert preset.release_column_map_name == 'm2'
    assert preset.def_project == 'PROJ'
    assert not hasattr(preset, 'def_filter')


@pytest.mark.parametrize('kind, path, expected', [
    ('ATTRIBUTE', 'key', ('key',)),
    ('field', 'status.name', ('status', 'name')),
    ('CUSTOM_FIELD', 'Story point estimate', ('Story point estimate',)),
    ('FILTERED_FIELD', 'issuelinks;type.name;Blocks;inwardIssue.key',
     ('issuelinks', 'type.name', 'Blocks', 'inwardIssue.key'))])
def test_attr_from_cells(kind: str, path: str,
                         expected: tuple[str, ...]) -> None:
    """Test a kind cell and a path cell parse into a JiraAttrPath."""
    attr = _attr_from_cells(kind, path)
    assert attr is not None
    assert attr.path == expected


@pytest.mark.parametrize('kind, path', [
    ('BOGUS', 'x'), ('FIELD', ''), ('ATTRIBUTE', '   '),
    ('FILTERED_FIELD', 'issuelinks;type.name;Blocks')])
def test_attr_bad(kind: str, path: str) -> None:
    """Test an unknown kind or an empty path gives no JiraAttrPath."""
    assert _attr_from_cells(kind, path) is None


def test_parse_jira_map() -> None:
    """Test a table parses mapped rows and ignores a blank row."""
    table: list[list[Optional[str]]] = [
        ['key', 'ATTRIBUTE', 'key'], ['status', 'FIELD', 'status.name'],
        ['title', '', '']]
    assert _parse_jira_map(table) == {
        'key': (JiraAttrPath(JiraAttrType.ATTRIBUTE, ('key',)),),
        'status': (JiraAttrPath(JiraAttrType.FIELD, ('status', 'name')),)}


def test_parse_jira_half() -> None:
    """Test a row with a kind but no path rejects the whole table."""
    assert _parse_jira_map([['key', 'ATTRIBUTE', '']]) is None


def test_parse_jira_dup() -> None:
    """Test a repeated internal field becomes multiple paths."""
    table: list[list[Optional[str]]] = [['key', 'ATTRIBUTE', 'key'],
                                        ['key', 'ATTRIBUTE', 'id']]
    assert _parse_jira_map(table) == {
        'key': (JiraAttrPath(JiraAttrType.ATTRIBUTE, ('key',)),
                JiraAttrPath(JiraAttrType.ATTRIBUTE, ('id',)))}


@pytest.mark.parametrize('table, pos, ok', [
    ([['key', 'BOGUS', 'x']], (0, 1), False),
    ([['key', 'FIELD', 'x']], (0, 1), True),
    ([['key', '', 'x']], (0, 2), False),
    ([['key', 'FIELD', 'x']], (0, 2), True)])
def test_jira_map_check(table: list[list[Optional[str]]], pos: tuple[int, int],
                        ok: bool) -> None:
    """Test the per-cell check flags a bad kind or a path without a kind."""
    assert _jira_map_check(table, pos)[0] is ok
