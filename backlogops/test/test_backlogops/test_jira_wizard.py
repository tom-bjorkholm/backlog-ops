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
from tableio_cfg_json import AskPathField, AskTextField, \
    WizardPathKind, WizardUiBridgeConsole
from backlogops.backlog import Status
from backlogops.backlog_ops_wizard import backlog_ops_wizard
from backlogops.jira_io_config import (
    JiraAttrPath, JiraAttrType, default_jira_filter)
from backlogops.jira_io_config import JiraConnectConfig, JiraIssueTypeMap, \
    JiraPreset, TokenStorage
from backlogops.jira_wizard import (
    _PresetChoices, _build_connections, _build_issue_type_maps,
    _build_preset_list, _connection_disabled, _connection_fields,
    _connection_rule, _preset_rule, _preset_seed, _store_token)
from backlogops.levels import DEFAULT_LEVELS
from backlogops.wizard_forms import FormResult
from backlogops.wizard_helpers import (
    _attr_from_cells, _jira_map_check, _merge_status_defaults,
    _parse_jira_map)
from backlogops.wizard_navigator import _Navigator

_PREFIX = [''] * 7 + ['', '0', '0', '0', '0'] + ['', '', '', '', '']
"""Default answers for the wizard stages that precede the Jira stage."""

JIRA_FULL = (['1', 'main', 'cloud', 'https://x.atlassian.net', 'me@x.com',
              'clear_internal', 'TOK']
             + ['1', 'bk', '']
             + ['1', 'rel', '']
             + ['0']
             + ['1', 'scrum', 'main', 'bk', 'no', 'rel', 'SCRUM', 'P = 1'])
"""Jira-stage answers for a connection, a backlog map, a release map, no
issue-type map and one preset that reuses the read map for writing."""

JIRA_WITH_ISSUE = (['1', 'main', 'cloud', 'https://x.atlassian.net',
                    'me@x.com', 'clear_internal', 'TOK']
                   + ['1', 'bk', '']
                   + ['1', 'rel', '']
                   + ['1', 'im', '']
                   + ['1', 'scrum', 'main', 'bk', 'no', 'rel', 'yes', 'im',
                      'SCRUM', 'P = 1'])
"""Jira-stage answers that also add one issue-type map named 'im' and a
preset that selects it for writing."""


def _choices(conn: list[str], backlog: list[str], release: list[str],
             issue: Optional[list[str]] = None) -> _PresetChoices:
    """Return preset choices, defaulting to no issue-type maps."""
    return _PresetChoices(connections=conn, backlog_maps=backlog,
                          release_maps=release,
                          issue_type_maps=[] if issue is None else issue)


def _console(answers: list[str],
             errors: Optional[io.StringIO] = None) -> WizardUiBridgeConsole:
    """Return a console bridge scripted with answers and an error sink."""
    text = '\n'.join(answers) + '\n'
    sink = errors if errors is not None else io.StringIO()
    return WizardUiBridgeConsole(io.StringIO(), io.StringIO(text), sink)


def test_jira_skip() -> None:
    """Test a run with no Jira connections leaves the Jira config empty."""
    config = backlog_ops_wizard(_console(_PREFIX + ['0', '0', '0', '0']))
    jira = config.get_jira_config()
    assert not jira.connections
    assert not jira.backlog_column_maps
    assert not jira.release_column_maps
    assert not jira.issue_type_maps
    assert not jira.presets


def test_jira_full() -> None:
    """Test the wizard builds a connection, maps and one preset."""
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
    preset = jira.get_preset('scrum')
    assert preset.def_project == 'SCRUM'
    assert preset.write_backlog_map_name() == 'bk'
    assert 'WARNING' in errors.getvalue()


def test_conn_encrypted() -> None:
    """Test an encrypted-internal connection stores the token encrypted.

    The connection form asks the pass phrase twice, masked, so both the
    pass phrase and its matching confirmation are supplied.
    """
    answers = ['1', 'enc', 'cloud', 'https://x', 'me@x',
               'encrypted_internal', 'SECRET', 'phrase', 'phrase']
    conn = _Navigator(_console(answers)).run(_build_connections)['enc']
    assert conn.uses_encryption()
    assert conn.stored_token not in (None, 'SECRET')
    assert conn.get_token() == 'SECRET'


def test_conn_phrase_mismatch() -> None:
    """Test two differing pass phrases re-ask the whole connection form.

    The first attempt enters two different pass phrases, which the form's
    rule rejects, so the whole form is re-asked and then completed with two
    identical pass phrases.
    """
    answers = ['1', 'enc', 'cloud', 'https://x', 'me@x',
               'encrypted_internal', 'SECRET', 'aa', 'bb',
               'enc', 'cloud', 'https://x', 'me@x',
               'encrypted_internal', 'SECRET', 'pp', 'pp']
    conn = _Navigator(_console(answers)).run(_build_connections)['enc']
    assert conn.get_token() == 'SECRET'


def test_conn_file() -> None:
    """Test a file-storage connection records the path and asks no token."""
    answers = ['1', 'f', 'cloud', 'https://x', 'me@x', 'clear_file',
               '/tmp/tok.txt']
    conn = _Navigator(_console(answers)).run(_build_connections)['f']
    assert conn.uses_token_file()
    assert conn.token_file_path == '/tmp/tok.txt'
    assert conn.stored_token is None


def test_preset() -> None:
    """Test the preset collector ties a connection, maps and filter."""
    answers = ['1', 'p1', 'c1', 'm1', 'no', 'm2', 'PROJ', 'filter']
    nav = _Navigator(_console(answers))
    presets = nav.run(
        lambda n, _d: _build_preset_list(n, _choices(['c1'], ['m1'], ['m2']),
                                         None))
    preset = presets['p1']
    assert preset.connection_name == 'c1'
    assert preset.backlog_column_map_name == 'm1'
    assert preset.release_column_map_name == 'm2'
    assert preset.write_backlog_map_name() == 'm1'
    assert preset.issue_type_map_name == ''
    assert preset.def_project == 'PROJ'
    assert preset.def_filter == 'filter'


def test_preset_def_filter() -> None:
    """Test a blank preset filter defaults to the project rank filter."""
    answers = ['1', 'p1', 'c1', 'm1', 'no', 'm2', 'PROJ', '']
    nav = _Navigator(_console(answers))
    presets = nav.run(
        lambda n, _d: _build_preset_list(n, _choices(['c1'], ['m1'], ['m2']),
                                         None))
    assert presets['p1'].def_filter == default_jira_filter('PROJ')


@pytest.mark.parametrize('storage, disabled', [
    (TokenStorage.CLEAR_FILE, {'api_token', 'passphrase', 'confirm'}),
    (TokenStorage.ENCRYPTED_FILE, {'api_token', 'passphrase', 'confirm'}),
    (TokenStorage.CLEAR_INTERNAL,
     {'token_file_path', 'passphrase', 'confirm'}),
    (TokenStorage.ENCRYPTED_INTERNAL, {'token_file_path'})])
def test_conn_disabled(storage: TokenStorage, disabled: set[str]) -> None:
    """Test each storage mode disables exactly the irrelevant token rows."""
    file_mode = storage.name.endswith('_FILE')
    encrypted = storage is TokenStorage.ENCRYPTED_INTERNAL
    assert _connection_disabled(file_mode, encrypted) == disabled


def _conn_result(storage: str, passphrase: str, confirm: str) -> FormResult:
    """Return a connection FormResult with a new token and token answers."""
    return FormResult({'token_storage': storage, 'api_token': 'TOK',
                       'passphrase': passphrase, 'confirm': confirm})


def test_conn_rule_mismatch() -> None:
    """Test the connection rule flags two differing pass phrases."""
    message, disabled = _connection_rule(None)(
        _conn_result('encrypted_internal', 'aa', 'bb'))
    assert message is not None
    assert 'token_file_path' in disabled


def test_conn_rule_match() -> None:
    """Test the connection rule passes two identical pass phrases."""
    message, _ = _connection_rule(None)(
        _conn_result('encrypted_internal', 'pp', 'pp'))
    assert message is None


def test_conn_fields_masked() -> None:
    """Test the connection form masks both pass-phrase fields."""
    fields = {field.key: field for field in _connection_fields(set(), False)}
    for key in ('passphrase', 'confirm'):
        ask = fields[key].ask
        assert isinstance(ask, AskTextField)
        assert ask.sensitive is True


def test_conn_path_field() -> None:
    """Test the token file path is asked as a file-picker path field."""
    fields = {field.key: field for field in _connection_fields(set(), False)}
    ask = fields['token_file_path'].ask
    assert isinstance(ask, AskPathField)
    assert ask.path_options.kind is WizardPathKind.FILE


def test_preset_rule_disables() -> None:
    """Test the preset rule disables the write and issue-type rows when off."""
    values = FormResult({'separate_write': False, 'use_issue_type': False})
    assert _preset_rule(True)(values) == (None, {'write_map',
                                                 'issue_type_map'})
    both_on = FormResult({'separate_write': True, 'use_issue_type': True})
    assert _preset_rule(True)(both_on) == (None, set())


def test_preset_skipped() -> None:
    """Test partial Jira prerequisites skip the presets with a note."""
    answers = (_PREFIX + ['1', 'main', 'cloud', 'https://x', 'me@x',
                          'clear_internal', 'TOK', '0', '0', '0'])
    out = io.StringIO()
    text = '\n'.join(answers) + '\n'
    console = WizardUiBridgeConsole(out, io.StringIO(text), io.StringIO())
    config = backlog_ops_wizard(console)
    assert not config.get_jira_config().presets
    assert 'skipping presets' in out.getvalue()


def test_preset_write_map() -> None:
    """Test choosing a separate backlog column map for writing."""
    answers = ['1', 'p1', 'c1', 'm1', 'yes', 'wr', 'm2', 'PROJ', 'filter']
    nav = _Navigator(_console(answers))
    presets = nav.run(
        lambda n, _d: _build_preset_list(
            n, _choices(['c1'], ['m1', 'wr'], ['m2']), None))
    preset = presets['p1']
    assert preset.backlog_column_map_name == 'm1'
    assert preset.backlog_write_map_name == 'wr'
    assert preset.write_backlog_map_name() == 'wr'


def test_preset_itmap() -> None:
    """Test selecting a level-to-issue-type map for a preset."""
    answers = ['1', 'p1', 'c1', 'm1', 'no', 'm2', 'yes', 'im', 'PROJ', 'f']
    nav = _Navigator(_console(answers))
    presets = nav.run(
        lambda n, _d: _build_preset_list(
            n, _choices(['c1'], ['m1'], ['m2'], ['im']), None))
    assert presets['p1'].issue_type_map_name == 'im'


def test_preset_no_itmap() -> None:
    """Test declining the issue-type map leaves the preset without one."""
    answers = ['1', 'p1', 'c1', 'm1', 'no', 'm2', 'no', 'PROJ', 'f']
    nav = _Navigator(_console(answers))
    presets = nav.run(
        lambda n, _d: _build_preset_list(
            n, _choices(['c1'], ['m1'], ['m2'], ['im']), None))
    assert presets['p1'].issue_type_map_name == ''


def _itmap_body(nav: _Navigator,
                _default: object) -> dict[str, JiraIssueTypeMap]:
    """Collect issue-type maps seeded from the default levels."""
    return _build_issue_type_maps(nav, DEFAULT_LEVELS, None)


def test_itmap_collect() -> None:
    """Test the issue-type map collector names a map seeded from levels."""
    nav = _Navigator(_console(['1', 'im', '']))
    maps = nav.run(_itmap_body)
    assert sorted(maps) == ['im']
    assert maps['im'] == {}


def test_full_itmap() -> None:
    """Test the full wizard collects an issue-type map and its preset."""
    config = backlog_ops_wizard(_console(_PREFIX + JIRA_WITH_ISSUE))
    jira = config.get_jira_config()
    assert sorted(jira.issue_type_maps) == ['im']
    assert jira.get_preset('scrum').issue_type_map_name == 'im'


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


def test_parse_blank_field() -> None:
    """Test a row with a blank internal field name is ignored."""
    table: list[list[Optional[str]]] = [
        ['', 'FIELD', 'status.name'], ['key', 'ATTRIBUTE', 'key']]
    assert _parse_jira_map(table) == {
        'key': (JiraAttrPath(JiraAttrType.ATTRIBUTE, ('key',)),)}


def test_parse_jira_bad_kind() -> None:
    """Test a row with both cells set but an invalid kind rejects it."""
    assert _parse_jira_map([['key', 'BOGUS', 'x']]) is None


def test_merge_status_recase() -> None:
    """Test a re-cased default status name replaces the old casing."""
    result = _merge_status_defaults({'Done': Status.DONE},
                                    {'done': Status.IN_PROGRESS})
    assert result == {'done': Status.IN_PROGRESS}


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


def _encrypted_default() -> JiraConnectConfig:
    """Return a connection with an encrypted, internally stored token."""
    conn = JiraConnectConfig()
    conn.token_storage = TokenStorage.ENCRYPTED_INTERNAL
    conn.base_url = 'https://x'
    conn.login_email = 'me@x'
    conn.set_token('SECRET', lambda: 'phrase')
    return conn


def test_conn_keep_token() -> None:
    """Test editing a connection with a blank token keeps the stored one.

    The default connection has an encrypted internal token whose clear text
    cannot be shown, so the token field is left blank and the stored,
    encrypted token is kept unchanged.
    """
    default = _encrypted_default()
    answers = [''] * 7
    nav = _Navigator(_console(answers))
    conn = nav.run(_build_connections, {'enc': default})['enc']
    assert conn.stored_token == default.stored_token
    assert conn.get_token(lambda: 'phrase') == 'SECRET'


def test_blank_token_fresh() -> None:
    """Test a blank token on a fresh connection leaves it without a token.

    A new internally stored connection has no default to fall back on, so a
    blank token field neither stores a new token nor keeps an old one.
    """
    nav = _Navigator(_console([]))
    connection = JiraConnectConfig(stderr_file=nav.error_file())
    connection.token_storage = TokenStorage.CLEAR_INTERNAL
    _store_token(nav, connection, FormResult({'api_token': None}), None)
    assert connection.stored_token is None


def _seed_preset(write_map: str, issue_map: str) -> JiraPreset:
    """Return a stored preset with the given write and issue-type maps."""
    preset = JiraPreset()
    preset.connection_name = 'c1'
    preset.backlog_column_map_name = 'm1'
    preset.backlog_write_map_name = write_map
    preset.release_column_map_name = 'm2'
    preset.issue_type_map_name = issue_map
    preset.def_project = 'PROJ'
    preset.def_filter = 'flt'
    return preset


def test_preset_seed_none() -> None:
    """Test no stored preset yields no seeded form values."""
    assert _preset_seed(None, None, _choices(['c1'], ['m1'], ['m2'])) is None


def test_preset_seed_full() -> None:
    """Test a stored preset fills each form value, incl. the issue map."""
    choices = _choices(['c1'], ['m1', 'wr'], ['m2'], ['im'])
    result = _preset_seed('p1', _seed_preset('wr', 'im'), choices)
    assert result is not None
    assert result.text('name') == 'p1'
    assert result.text('connection') == 'c1'
    assert result.text('backlog_map') == 'm1'
    assert result.flag('separate_write') is True
    assert result.text('write_map') == 'wr'
    assert result.text('release_map') == 'm2'
    assert result.text('def_project') == 'PROJ'
    assert result.text('def_filter') == 'flt'
    assert result.flag('use_issue_type') is True
    assert result.text('issue_type_map') == 'im'


def test_preset_seed_defaults() -> None:
    """Test empty write and issue maps fall back to the first choices.

    A preset that reuses its read map for writing offers the first backlog
    map as the disabled write map. With no issue-type maps configured, the
    issue-type form rows are left out of the seed entirely.
    """
    result = _preset_seed('p1', _seed_preset('', ''),
                          _choices(['c1'], ['m1'], ['m2']))
    assert result is not None
    assert result.flag('separate_write') is False
    assert result.text('write_map') == 'm1'
    assert result.raw('use_issue_type') is None
