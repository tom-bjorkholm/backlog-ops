#! /usr/local/bin/python3
"""Tests for the Jira input and output configuration.

The tests cover the empty default shape, the round trip of connections,
split backlog and release column maps and unified presets through a
written file, the JSON shapes of the attribute paths and the enum
members, the rejection of dangling preset references and malformed
attribute paths, the four token storage modes with their clear-text
warning and pass-phrase handling, and the loading of an old file that
omits a sub-section, still holds the old combined column-map section, or
splits the presets into the old read and write sections.
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
from backlogops.jira_io_config import (
    _ColumnMapsValidator, _IssueTypeMapsValidator, _issue_type_map_from_obj)
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


def _preset(conn: str, cmap: str, rmap: str, wmap: str = '') -> JiraPreset:
    """Return a preset naming a connection and its column maps."""
    preset = JiraPreset(stderr_file=NO)
    preset.connection_name = conn
    preset.backlog_column_map_name = cmap
    preset.release_column_map_name = rmap
    preset.backlog_write_map_name = wmap
    preset.def_project = 'SCRUM'
    preset.def_filter = 'project = "SCRUM"'
    return preset


def _full() -> JiraIOConfig:
    """Return a configuration with one connection, two maps and presets."""
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
    config.backlog_column_maps = {'bk': backlog}
    config.release_column_maps = {'rel': release}
    config.presets = {'scrum': _preset('main', 'bk', 'rel')}
    return config


def test_empty_shape() -> None:
    """Test a fresh configuration serializes to five empty maps."""
    assert _json(_empty()) == {
        'connections': {}, 'backlog_column_maps': {},
        'release_column_maps': {}, 'issue_type_maps': {}, 'presets': {}}


def test_round_trip(tmp_path: Path) -> None:
    """Test connections, column maps and presets survive a write and read."""
    path = tmp_path / 'jira.cfg'
    _full().write(to_json_filename=path, stderr_file=NO)
    loaded = JiraIOConfig(from_json_filename=path, stderr_file=NO)
    conn = loaded.connections['main']
    assert conn.jira_type is JiraType.SERVER
    assert conn.stored_token == 'TOK'
    backlog = loaded.backlog_column_maps['bk']
    assert backlog['status'] == (
        _attr(JiraAttrType.FIELD, 'status', 'name'),)
    assert backlog['story_points'][0].kind is JiraAttrType.CUSTOM_FIELD
    assert 'name' in loaded.release_column_maps['rel']
    preset = loaded.get_preset('scrum')
    assert preset.def_project == 'SCRUM'
    assert preset.connection_name == 'main'
    assert preset.write_backlog_map_name() == 'bk'


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
    data = _json(_full())
    backlog = data['backlog_column_maps']
    release = data['release_column_maps']
    assert isinstance(backlog, dict)
    assert isinstance(release, dict)
    assert backlog['bk']['status'] == ['FIELD', 'status', 'name']
    assert release['rel']['name'] == ['ATTRIBUTE', 'name']


def test_multi_attr_path_json() -> None:
    """Test several paths for one internal field write as nested lists."""
    config = _full()
    config.backlog_column_maps['bk']['parent_key'] = (
        _attr(JiraAttrType.FIELD, 'parent', 'key'),
        _attr(JiraAttrType.CUSTOM_FIELD, 'Epic Link'))
    maps = _json(config)['backlog_column_maps']
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
    config.backlog_column_maps = {'bk': {}}
    config.release_column_maps = {'rel': {}}
    config.presets = {'p': _preset('nope', 'bk', 'rel')}
    with pytest.raises(KeyError):
        config.as_json_string(NO)


def test_bad_cmap() -> None:
    """Test a preset naming an unknown backlog column map is rejected."""
    config = _empty()
    config.connections = {'main': JiraConnectConfig(stderr_file=NO)}
    config.release_column_maps = {'rel': {}}
    config.presets = {'p': _preset('main', 'nope', 'rel')}
    with pytest.raises(KeyError):
        config.as_json_string(NO)


def test_bad_rmap() -> None:
    """Test a preset naming an unknown release column map is rejected."""
    config = _empty()
    config.connections = {'main': JiraConnectConfig(stderr_file=NO)}
    config.backlog_column_maps = {'bk': {}}
    config.presets = {'p': _preset('main', 'bk', 'nope')}
    with pytest.raises(KeyError):
        config.as_json_string(NO)


def test_bad_write_ref() -> None:
    """Test a preset naming an unknown backlog write map is rejected."""
    config = _empty()
    config.connections = {'main': JiraConnectConfig(stderr_file=NO)}
    config.backlog_column_maps = {'bk': {}}
    config.release_column_maps = {'rel': {}}
    config.presets = {'p': _preset('main', 'bk', 'rel', 'nope')}
    with pytest.raises(KeyError):
        config.as_json_string(NO)


def test_write_map() -> None:
    """Test the write map is used when set and falls back to the read map."""
    config = _empty()
    config.connections = {'main': JiraConnectConfig(stderr_file=NO)}
    config.backlog_column_maps = {'bk': {}, 'wr': {}}
    config.release_column_maps = {'rel': {}}
    config.presets = {'p': _preset('main', 'bk', 'rel', 'wr')}
    config.as_json_string(NO)
    assert config.presets['p'].write_backlog_map_name() == 'wr'
    assert _preset('main', 'bk', 'rel').write_backlog_map_name() == 'bk'


def _issue_config(mapping: dict[int, str], ref: str = 'it') -> JiraIOConfig:
    """Return a full config whose preset names an issue-type map."""
    config = _full()
    config.issue_type_maps = {ref: mapping}
    config.presets['scrum'].issue_type_map_name = ref
    return config


def test_itmap_round_trip(tmp_path: Path) -> None:
    """Test a level-to-issue-type map survives a write and read as ints."""
    path = tmp_path / 'jira.cfg'
    _issue_config({0: 'Deluppgift'}).write(to_json_filename=path,
                                           stderr_file=NO)
    loaded = JiraIOConfig(from_json_filename=path, stderr_file=NO)
    assert loaded.issue_type_maps['it'] == {0: 'Deluppgift'}
    assert loaded.get_preset('scrum').issue_type_map_name == 'it'


def test_itmap_json_keys() -> None:
    """Test the level number keys are written as JSON string keys."""
    data = _json(_issue_config({0: 'Deluppgift', 2: 'Epos'}))
    maps = data['issue_type_maps']
    assert isinstance(maps, dict)
    assert maps['it'] == {'0': 'Deluppgift', '2': 'Epos'}


def test_itmap_parse_keys() -> None:
    """Test JSON string keys parse back to integer level numbers."""
    text = json.dumps({'connections': {}, 'backlog_column_maps': {},
                       'release_column_maps': {},
                       'issue_type_maps': {'m': {'0': 'Deluppgift'}}})
    config = _from_text(text)
    assert config.issue_type_maps['m'] == {0: 'Deluppgift'}


def test_itmap_optional() -> None:
    """Test a preset with no issue-type map writes an empty map name."""
    presets = _json(_full())['presets']
    assert isinstance(presets, dict)
    assert presets['scrum']['issue_type_map_name'] == ''


def test_itmap_bad_ref() -> None:
    """Test a preset naming an unknown issue type map is rejected."""
    config = _empty()
    config.connections = {'main': JiraConnectConfig(stderr_file=NO)}
    config.backlog_column_maps = {'bk': {}}
    config.release_column_maps = {'rel': {}}
    preset = _preset('main', 'bk', 'rel')
    preset.issue_type_map_name = 'nope'
    config.presets = {'p': preset}
    with pytest.raises(KeyError):
        config.as_json_string(NO)


@pytest.mark.parametrize('bad_map', [
    {'x': 'Deluppgift'}, {'0': 5}, {'0': ['Deluppgift']}, 'notadict'])
def test_itmap_bad_value(bad_map: object) -> None:
    """Test a non-integer key or non-string value is rejected on read."""
    text = json.dumps({'connections': {}, 'backlog_column_maps': {},
                       'release_column_maps': {},
                       'issue_type_maps': {'m': bad_map}})
    with pytest.raises((TypeError, ValueError)):
        _from_text(text)


def test_bad_one_map() -> None:
    """Test a single column map that is not a dict is rejected on read."""
    with pytest.raises((TypeError, ValueError)):
        _from_text(json.dumps({'backlog_column_maps': {'m': 'notadict'}}))


def test_bad_maps_member() -> None:
    """Test a non-dict column-maps member is rejected by the validator."""
    validator = _ColumnMapsValidator()
    with pytest.raises(TypeError):
        validator.validate_member(_empty(), 'backlog_column_maps', 'notadict',
                                  NO)


def test_bad_itmaps_member() -> None:
    """Test a non-dict issue-type maps member is rejected by the validator."""
    validator = _IssueTypeMapsValidator()
    with pytest.raises(TypeError):
        validator.validate_member(_empty(), 'issue_type_maps', 'notadict', NO)


@pytest.mark.parametrize('mapping', [{True: 'x'}, {1.5: 'x'}])
def test_bad_itmap_key(mapping: dict[object, str]) -> None:
    """Test a boolean or non-integer level key is rejected."""
    with pytest.raises(TypeError):
        _issue_type_map_from_obj('m', mapping, NO)


def test_no_stored_token() -> None:
    """Test reading an internal token that is not stored is rejected."""
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = TokenStorage.CLEAR_INTERNAL
    conn.stored_token = None
    with pytest.raises(ValueError):
        conn.get_token()


def test_no_token_file() -> None:
    """Test reading a file token with no path configured is rejected."""
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = TokenStorage.CLEAR_FILE
    conn.token_file_path = None
    with pytest.raises(ValueError):
        conn.get_token()


def test_itmap_old_none() -> None:
    """Test a preset from an old file gets an empty issue-type map name."""
    conn = {'jira_type': 'CLOUD', 'base_url': 'u', 'login_email': 'e',
            'token_storage': 'CLEAR_FILE'}
    preset = {'connection_name': 'c', 'backlog_column_map_name': 'bk',
              'release_column_map_name': 'rel', 'def_project': 'P',
              'def_filter': 'f'}
    old = json.dumps({'connections': {'c': conn},
                      'backlog_column_maps': {'bk': {}},
                      'release_column_maps': {'rel': {}},
                      'presets': {'p': preset}})
    config = _from_text(old)
    assert not config.issue_type_maps
    assert config.get_preset('p').issue_type_map_name == ''


def _cmap_text(path_value: object) -> str:
    """Return jira JSON text with one column map holding a path value."""
    return json.dumps({'connections': {},
                       'backlog_column_maps': {'m': {'c': path_value}}})


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
    assert not config.backlog_column_maps
    assert not config.release_column_maps
    assert not config.presets


def test_old_partial() -> None:
    """Test a jira section with only connections defaults the rest."""
    config = _from_text(json.dumps({'connections': {}}))
    assert not config.backlog_column_maps
    assert not config.release_column_maps
    assert not config.presets


def test_old_cmap_dropped() -> None:
    """Test an old combined column-map section is dropped, not an error."""
    old = json.dumps({'connections': {},
                      'column_maps': {'m': {'key': ['ATTRIBUTE', 'key']}}})
    config = _from_text(old)
    assert not config.backlog_column_maps
    assert not config.release_column_maps
    assert 'column_maps' not in _json(config)


def test_old_presets_migrated() -> None:
    """Test old read presets move to presets and write presets are dropped."""
    conn = {'jira_type': 'CLOUD', 'base_url': 'u', 'login_email': 'e',
            'token_storage': 'CLEAR_FILE'}
    preset = {'connection_name': 'c', 'backlog_column_map_name': 'bk',
              'release_column_map_name': 'rel', 'def_project': 'P',
              'def_filter': 'f'}
    old = json.dumps({'connections': {'c': conn},
                      'backlog_column_maps': {'bk': {}},
                      'release_column_maps': {'rel': {}},
                      'from_jira_presets': {'r': preset},
                      'to_jira_presets': {'w': preset}})
    config = _from_text(old)
    assert sorted(config.presets) == ['r']
    data = _json(config)
    assert 'from_jira_presets' not in data
    assert 'to_jira_presets' not in data


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
