#! /usr/local/bin/python3
"""Tests for the Jira input and output configuration.

The tests cover the empty default shape, the round trip of connections,
column maps and presets through a written file, the JSON shapes of the
attribute paths and the enum members, the rejection of dangling preset
references and malformed attribute paths, the four token storage modes
with their clear-text warning and pass-phrase handling, and the loading
of an old file that omits a sub-section.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
import json
from pathlib import Path
import pytest
from backlogops import (
    DEF_BACKLOG_COLUMN_MAP, DEF_RELEASE_COLUMN_MAP, JiraAttrPath,
    JiraAttrType, JiraConnectConfig, JiraIOConfig, JiraPreset, JiraType,
    TokenStorage)
from backlogops.jira_token import encrypt_token
from backlogops.no_text_io import NoTextIO

NO = NoTextIO()


def _attr(kind: JiraAttrType, *steps: str) -> JiraAttrPath:
    """Return a JiraAttrPath of a kind and path steps."""
    return JiraAttrPath(kind, tuple(steps))


def _paths(*attrs: JiraAttrPath) -> tuple[JiraAttrPath, ...]:
    """Return Jira attribute paths as a column-map value."""
    return attrs


def _empty() -> JiraIOConfig:
    """Return a fresh, empty Jira configuration."""
    return JiraIOConfig(stderr_file=NO)


def _from_text(text: str) -> JiraIOConfig:
    """Return a Jira configuration parsed from JSON text."""
    return JiraIOConfig(from_json_data_text=text, stderr_file=NO)


def _json(config: JiraIOConfig) -> dict[str, object]:
    """Return the configuration serialized to a JSON dictionary."""
    data = json.loads(config.as_json_string(NO))
    assert isinstance(data, dict)
    return data


def _preset(conn: str, cmap: str, rmap: str) -> JiraPreset:
    """Return a preset naming a connection and two column maps."""
    preset = JiraPreset(stderr_file=NO)
    preset.connection_name = conn
    preset.column_map_name = cmap
    preset.release_column_map_name = rmap
    preset.def_project = 'SCRUM'
    preset.def_filter = 'project = "SCRUM"'
    return preset


def _full() -> JiraIOConfig:
    """Return a configuration with one connection, two maps and a preset."""
    config = _empty()
    conn = JiraConnectConfig(stderr_file=NO)
    conn.base_url = 'https://x.atlassian.net'
    conn.login_email = 'me@x.com'
    conn.jira_type = JiraType.SERVER
    conn.token_storage = TokenStorage.CLEAR_INTERNAL
    conn.stored_token = 'TOK'
    config.connections = {'main': conn}
    backlog = {'key': _paths(_attr(JiraAttrType.ATTRIBUTE, 'key')),
               'status': _paths(_attr(JiraAttrType.FIELD, 'status', 'name')),
               'story_points': _paths(_attr(JiraAttrType.CUSTOM_FIELD,
                                            'Story point estimate'))}
    release = {'name': _paths(_attr(JiraAttrType.ATTRIBUTE, 'name'))}
    config.column_maps = {'bk': backlog, 'rel': release}
    config.from_jira_presets = {'scrum': _preset('main', 'bk', 'rel')}
    return config


def test_empty_shape() -> None:
    """Test a fresh configuration serializes to three empty maps."""
    assert _json(_empty()) == {'connections': {}, 'column_maps': {},
                               'from_jira_presets': {}}


def test_round_trip(tmp_path: Path) -> None:
    """Test connections, column maps and presets survive a write and read."""
    path = tmp_path / 'jira.cfg'
    _full().write(to_json_filename=path, stderr_file=NO)
    loaded = JiraIOConfig(from_json_filename=path, stderr_file=NO)
    conn = loaded.connections['main']
    assert conn.jira_type is JiraType.SERVER
    assert conn.stored_token == 'TOK'
    backlog = loaded.column_maps['bk']
    assert backlog['status'] == (
        _attr(JiraAttrType.FIELD, 'status', 'name'),)
    assert backlog['story_points'][0].kind is JiraAttrType.CUSTOM_FIELD
    preset = loaded.get_preset('scrum')
    assert preset.def_project == 'SCRUM'
    assert preset.connection_name == 'main'


def test_stable_write(tmp_path: Path) -> None:
    """Test writing a configuration twice yields equal files."""
    first = tmp_path / 'a.cfg'
    second = tmp_path / 'b.cfg'
    _full().write(to_json_filename=first, stderr_file=NO)
    loaded = JiraIOConfig(from_json_filename=first, stderr_file=NO)
    loaded.write(to_json_filename=second, stderr_file=NO)
    assert first.read_text() == second.read_text()


def test_attr_path_json() -> None:
    """Test an attribute path is written as a kind and its path steps."""
    maps = _json(_full())['column_maps']
    assert isinstance(maps, dict)
    assert maps['bk']['status'] == ['FIELD', 'status', 'name']
    assert maps['rel']['name'] == ['ATTRIBUTE', 'name']


def test_multi_attr_path_json() -> None:
    """Test several paths for one internal field write as nested lists."""
    config = _full()
    config.column_maps['bk']['parent_key'] = (
        _attr(JiraAttrType.FIELD, 'parent', 'key'),
        _attr(JiraAttrType.CUSTOM_FIELD, 'Epic Link'))
    maps = _json(config)['column_maps']
    assert isinstance(maps, dict)
    assert maps['bk']['parent_key'] == [
        ['FIELD', 'parent', 'key'], ['CUSTOM_FIELD', 'Epic Link']]


def test_enum_names_json() -> None:
    """Test the connection enum members are written as their names."""
    connections = _json(_full())['connections']
    assert isinstance(connections, dict)
    conn = connections['main']
    assert conn['jira_type'] == 'SERVER'
    assert conn['token_storage'] == 'CLEAR_INTERNAL'


def test_bad_connection() -> None:
    """Test a preset naming an unknown connection is rejected."""
    config = _empty()
    config.column_maps = {'bk': {}, 'rel': {}}
    config.from_jira_presets = {'p': _preset('nope', 'bk', 'rel')}
    with pytest.raises(KeyError):
        config.as_json_string(NO)


def test_bad_cmap() -> None:
    """Test a preset naming an unknown column map is rejected."""
    config = _empty()
    config.connections = {'main': JiraConnectConfig(stderr_file=NO)}
    config.column_maps = {'rel': {}}
    config.from_jira_presets = {'p': _preset('main', 'nope', 'rel')}
    with pytest.raises(KeyError):
        config.as_json_string(NO)


def test_bad_rmap() -> None:
    """Test a preset naming an unknown release column map is rejected."""
    config = _empty()
    config.connections = {'main': JiraConnectConfig(stderr_file=NO)}
    config.column_maps = {'bk': {}}
    config.from_jira_presets = {'p': _preset('main', 'bk', 'nope')}
    with pytest.raises(KeyError):
        config.as_json_string(NO)


def _cmap_text(path_value: object) -> str:
    """Return jira JSON text with one column map holding a path value."""
    return json.dumps({'connections': {}, 'from_jira_presets': {},
                       'column_maps': {'m': {'c': path_value}}})


@pytest.mark.parametrize('bad', [
    'notalist', ['FIELD'], [], ['BOGUS', 'x'], ['FIELD', 1],
    ['ATTRIBUTE', 'a', 'b'], ['CUSTOM_FIELD', 'a', 'b'],
    ['FILTERED_FIELD', 'a', 'b', 'c']])
def test_bad_attr_path(bad: object) -> None:
    """Test a malformed attribute path is rejected on read."""
    with pytest.raises((TypeError, ValueError)):
        _from_text(_cmap_text(bad))


def test_bad_jira_type() -> None:
    """Test a connection with an unknown jira type is rejected."""
    text = json.dumps({
        'column_maps': {}, 'from_jira_presets': {},
        'connections': {'c': {'jira_type': 'BOGUS', 'base_url': 'u',
                              'login_email': 'e',
                              'token_storage': 'CLEAR_FILE'}}})
    with pytest.raises((TypeError, ValueError, KeyError)):
        _from_text(text)


def _pf() -> str:
    """Return a fixed pass phrase for the encrypted token modes."""
    return 'pw'


def _reload(conn: JiraConnectConfig) -> JiraConnectConfig:
    """Return a fresh connection with the same storage and no cache."""
    fresh = JiraConnectConfig(stderr_file=NO)
    fresh.token_storage = conn.token_storage
    fresh.token_file_path = conn.token_file_path
    fresh.stored_token = conn.stored_token
    return fresh


@pytest.mark.parametrize('storage', list(TokenStorage))
def test_token_modes(storage: TokenStorage, tmp_path: Path) -> None:
    """Test every storage mode stores and reads back a token."""
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = storage
    conn.token_file_path = str(tmp_path / 'tok.txt')
    conn.set_token('SECRET', passphrase=_pf, stderr_file=NO)
    assert _reload(conn).get_token(passphrase=_pf) == 'SECRET'


@pytest.mark.parametrize('storage', [TokenStorage.CLEAR_FILE,
                                     TokenStorage.CLEAR_INTERNAL])
def test_clear_warns(storage: TokenStorage, tmp_path: Path) -> None:
    """Test storing a clear-text token prints a strong warning."""
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = storage
    conn.token_file_path = str(tmp_path / 't.txt')
    out = io.StringIO()
    conn.set_token('x', stderr_file=out)
    assert 'WARNING' in out.getvalue()


def test_enc_no_warn() -> None:
    """Test storing an encrypted token prints no clear-text warning."""
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = TokenStorage.ENCRYPTED_INTERNAL
    out = io.StringIO()
    conn.set_token('x', passphrase=_pf, stderr_file=out)
    assert out.getvalue() == ''


def test_enc_needs_pass() -> None:
    """Test reading an encrypted token without a pass phrase is rejected."""
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = TokenStorage.ENCRYPTED_INTERNAL
    conn.stored_token = encrypt_token('x', 'pw')
    with pytest.raises(ValueError):
        conn.get_token()


def test_token_cache_state() -> None:
    """Test the token cache reports whether a token is materialized."""
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = TokenStorage.ENCRYPTED_INTERNAL
    conn.stored_token = encrypt_token('x', 'pw')
    assert not conn.has_cached_token()
    assert conn.get_token(_pf) == 'x'
    assert conn.has_cached_token()


def test_file_no_leak(tmp_path: Path) -> None:
    """Test a file storage mode keeps the token out of the configuration."""
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = TokenStorage.CLEAR_FILE
    conn.token_file_path = str(tmp_path / 't.txt')
    conn.set_token('SECRET', stderr_file=NO)
    text = conn.as_json_string(NO)
    assert 'stored_token' not in text
    assert 'SECRET' not in text


def test_old_empty() -> None:
    """Test an empty jira section loads with every sub-section empty."""
    config = _from_text('{}')
    assert not config.connections
    assert not config.column_maps
    assert not config.from_jira_presets


def test_old_partial() -> None:
    """Test a jira section with only connections defaults the rest."""
    config = _from_text(json.dumps({'connections': {}}))
    assert not config.column_maps
    assert not config.from_jira_presets


def test_def_maps() -> None:
    """Test the shipped default column maps hold the expected paths."""
    assert DEF_BACKLOG_COLUMN_MAP['status'] == (
        JiraAttrPath(JiraAttrType.FIELD, ('status', 'name')),)
    assert DEF_BACKLOG_COLUMN_MAP['release'] == (
        JiraAttrPath(JiraAttrType.FIELD, ('fixVersions',)),)
    assert DEF_BACKLOG_COLUMN_MAP['team'][0].kind is JiraAttrType.CUSTOM_FIELD
    assert DEF_BACKLOG_COLUMN_MAP['parent_key'] == (
        JiraAttrPath(JiraAttrType.FIELD, ('parent', 'key')),
        JiraAttrPath(JiraAttrType.CUSTOM_FIELD, ('Epic Link',)))
    assert DEF_BACKLOG_COLUMN_MAP['depends_on_f2s'][0] == JiraAttrPath(
        JiraAttrType.FILTERED_FIELD,
        ('issuelinks', 'type.name', 'Blocks', 'inwardIssue.key'))
    assert DEF_BACKLOG_COLUMN_MAP['description'] == (
        JiraAttrPath(JiraAttrType.FIELD, ('description',)),)
    assert DEF_RELEASE_COLUMN_MAP['planned_date'][0].kind is \
        JiraAttrType.ATTRIBUTE
