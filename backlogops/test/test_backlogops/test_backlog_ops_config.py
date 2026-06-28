#! /usr/local/bin/python3
"""Tests for the top-level BacklogOpsConfig configuration object.

The tests cover the nested workforce, the named TableIO presets, the
optional levels member (its JSON shape, the omit-when-default behaviour
and the rebuilt levels mapping) and the migration of older files that
stored the workforce members at the top level.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
import json
from pathlib import Path
import pytest
from config_as_json import MigrateCfgWarnHook
from backlogops import (
    AvailableTeams, BacklogOpsConfig, DEFAULT_LEVELS, Level, LevelDisplay,
    Status, make_input_config, make_output_config, read_backlog_ops_config,
    resolve_input_config, resolve_output_config, write_backlog_ops_config)
from backlogops.no_text_io import NoTextIO
from backlogops.work_hours import WeekDay

NO_OUTPUT = NoTextIO()


def _empty() -> BacklogOpsConfig:
    """Return a configuration for an empty workforce and no presets."""
    return BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]),
        stderr_file=NO_OUTPUT)


def _config_json(config: BacklogOpsConfig) -> dict[str, object]:
    """Return the configuration serialized to a JSON dictionary."""
    data = json.loads(config.as_json_string(NO_OUTPUT))
    assert isinstance(data, dict)
    return data


def test_new_file_shape(tmp_path: Path) -> None:
    """Test a fresh file nests the workforce and holds empty presets."""
    config_file = tmp_path / 'ops.cfg'
    write_backlog_ops_config(_empty(), config_file, NO_OUTPUT)
    data = json.loads(config_file.read_text(encoding='UTF-8'))
    assert 'available_teams' in data
    assert 'persons' in data['available_teams']
    assert data['input_configs'] == {}
    assert data['output_configs'] == {}
    assert 'levels' not in data


def test_presets_round_trip(tmp_path: Path) -> None:
    """Test named input and output presets survive a write and read."""
    config = _empty()
    config.input_configs = {'sheet': make_input_config(
        resolve_input_config(None, data_file='x.csv',
                             stderr_file=NO_OUTPUT).tableio,
        {'Type': 'level'}, {'Rel': 'name'}, stderr_file=NO_OUTPUT)}
    config.output_configs = {'report': make_output_config(
        resolve_output_config(None, data_file='x.xlsx',
                              stderr_file=NO_OUTPUT).tableio,
        {'level': 'Type'}, {'name': 'Release'}, stderr_file=NO_OUTPUT)}
    config_file = tmp_path / 'ops.cfg'
    write_backlog_ops_config(config, config_file, NO_OUTPUT)
    loaded = read_backlog_ops_config(config_file, NO_OUTPUT)
    sheet = loaded.input_configs['sheet']
    assert sheet.backlog_to_internal == {'Type': 'level'}
    assert sheet.release_to_internal == {'Rel': 'name'}
    report = loaded.output_configs['report']
    assert report.tableio.format_name == 'Excel'
    assert report.backlog_to_external == {'level': 'Type'}
    assert report.release_to_external == {'name': 'Release'}


def test_levels_omitted() -> None:
    """Test a configuration with no levels omits the member from JSON."""
    assert 'levels' not in _config_json(_empty())


def test_get_levels_default() -> None:
    """Test get_levels returns the default levels when none are set."""
    assert _empty().get_levels() == DEFAULT_LEVELS


def test_levels_json_shape() -> None:
    """Test configured levels are written as a list of level objects."""
    config = _empty()
    config.levels = [Level(level=0, name='Sub-Task'),
                     Level(level=1, name='Story', aliases=['Task', 'Bug'])]
    data = _config_json(config)
    assert data['levels'] == [
        {'level': 0, 'name': 'Sub-Task', 'aliases': []},
        {'level': 1, 'name': 'Story', 'aliases': ['Task', 'Bug']}]


def test_levels_round_trip(tmp_path: Path) -> None:
    """Test configured levels survive a write and read and rebuild a map."""
    config = _empty()
    config.levels = [Level(level=-1, name='Spike', aliases=['Research']),
                     Level(level=0, name='Sub-Task')]
    config_file = tmp_path / 'ops.cfg'
    write_backlog_ops_config(config, config_file, NO_OUTPUT)
    loaded = read_backlog_ops_config(config_file, NO_OUTPUT)
    levels = loaded.get_levels()
    assert sorted(levels) == [-1, 0]
    assert levels[-1].name == 'Spike'
    assert levels[-1].aliases == ['Research']


def test_levels_stable(tmp_path: Path) -> None:
    """Test writing a configuration with levels twice yields equal files."""
    config = _empty()
    config.levels = [Level(level=2, name='Epic')]
    first = tmp_path / 'first.cfg'
    second = tmp_path / 'second.cfg'
    write_backlog_ops_config(config, first, NO_OUTPUT)
    loaded = read_backlog_ops_config(first, NO_OUTPUT)
    write_backlog_ops_config(loaded, second, NO_OUTPUT)
    assert first.read_text() == second.read_text()


def test_old_file_migrates(tmp_path: Path) -> None:
    """Test an old top-level-workforce file loads into available_teams."""
    new = _config_json(_empty())
    workforce = new['available_teams']
    assert isinstance(workforce, dict)
    old: dict[str, object] = dict(workforce)
    old['input_configs'] = new['input_configs']
    old['output_configs'] = new['output_configs']
    config_file = tmp_path / 'old.cfg'
    config_file.write_text(json.dumps(old), encoding='UTF-8')
    loaded = read_backlog_ops_config(config_file, NO_OUTPUT)
    assert not loaded.available_teams.persons
    assert not loaded.available_teams.teams


def test_old_no_presets(tmp_path: Path) -> None:
    """Test a very old file without preset maps loads with empty maps."""
    new = _config_json(_empty())
    old = new['available_teams']
    config_file = tmp_path / 'old.cfg'
    config_file.write_text(json.dumps(old), encoding='UTF-8')
    loaded = read_backlog_ops_config(config_file, NO_OUTPUT)
    assert not loaded.input_configs
    assert not loaded.output_configs


def _write_old_config(path: Path) -> None:
    """Write an old top-level-workforce file that needs ROCF on read."""
    old = _config_json(_empty())['available_teams']
    path.write_text(json.dumps(old), encoding='UTF-8')


def test_warn_hook_old_file(tmp_path: Path) -> None:
    """Test reading an old file notifies the backward-compatibility hook."""
    config_file = tmp_path / 'old.cfg'
    _write_old_config(config_file)
    out = io.StringIO()
    read_backlog_ops_config(config_file, out,
                            auto_ch_hook=MigrateCfgWarnHook())
    assert 'Backward compatibility' in out.getvalue()


def test_warn_hook_current(tmp_path: Path) -> None:
    """Test reading a current file leaves the warning hook silent."""
    config_file = tmp_path / 'ops.cfg'
    write_backlog_ops_config(_empty(), config_file, NO_OUTPUT)
    out = io.StringIO()
    read_backlog_ops_config(config_file, out,
                            auto_ch_hook=MigrateCfgWarnHook())
    assert out.getvalue() == ''


def test_gui_display_default() -> None:
    """Test a fresh configuration shows both number and name in the GUI."""
    assert _empty().get_gui_level_display() is LevelDisplay.BOTH


def test_gui_display_rt(tmp_path: Path) -> None:
    """Test the GUI level display survives a write and read."""
    config = _empty()
    config.gui_display.level_display = LevelDisplay.NUMERIC
    config_file = tmp_path / 'ops.cfg'
    write_backlog_ops_config(config, config_file, NO_OUTPUT)
    loaded = read_backlog_ops_config(config_file, NO_OUTPUT)
    assert loaded.get_gui_level_display() is LevelDisplay.NUMERIC


def test_gui_maps_rt(tmp_path: Path) -> None:
    """Test the GUI column maps survive a write and read of the config."""
    config = _empty()
    config.gui_display.backlog_to_external = {'key': 'Id', 'team': None}
    config.gui_display.release_to_external = {'name': 'Release'}
    config_file = tmp_path / 'ops.cfg'
    write_backlog_ops_config(config, config_file, NO_OUTPUT)
    loaded = read_backlog_ops_config(config_file, NO_OUTPUT).gui_display
    assert loaded.backlog_to_external == {'key': 'Id', 'team': None}
    assert loaded.release_to_external == {'name': 'Release'}


def test_old_no_gui_display(tmp_path: Path) -> None:
    """Test an old file without a GUI display loads with the default."""
    new = _config_json(_empty())
    workforce = new['available_teams']
    assert isinstance(workforce, dict)
    old: dict[str, object] = dict(workforce)
    old['input_configs'] = {}
    old['output_configs'] = {}
    config_file = tmp_path / 'old.cfg'
    config_file.write_text(json.dumps(old), encoding='UTF-8')
    loaded = read_backlog_ops_config(config_file, NO_OUTPUT)
    assert loaded.get_gui_level_display() is LevelDisplay.BOTH


def _ops_text(levels: object) -> str:
    """Return configuration JSON text with the given levels and no teams."""
    return json.dumps({
        'available_teams': {
            'persons': {}, 'teams': [],
            'company_work_hours': {
                'work_hours': {day.name: 8.0 for day in WeekDay},
                'exceptions': []}},
        'input_configs': {}, 'output_configs': {}, 'levels': levels})


def _levels_text(levels: list[dict[str, object]]) -> str:
    """Return configuration JSON text with the given list of levels."""
    return _ops_text(levels)


def test_dup_level_number() -> None:
    """Test two levels with the same number are rejected."""
    text = _levels_text([{'level': 0, 'name': 'A'},
                         {'level': 0, 'name': 'B'}])
    with pytest.raises(ValueError):
        BacklogOpsConfig(from_json_data_text=text, stderr_file=NO_OUTPUT)


def test_duplicate_level_name() -> None:
    """Test two levels sharing a name are rejected as a KeyError."""
    text = _levels_text([{'level': 0, 'name': 'Same'},
                         {'level': 1, 'name': 'Same'}])
    with pytest.raises(KeyError):
        BacklogOpsConfig(from_json_data_text=text, stderr_file=NO_OUTPUT)


def test_level_missing_name() -> None:
    """Test a level object without a name is rejected."""
    text = _levels_text([{'level': 0}])
    with pytest.raises(ValueError):
        BacklogOpsConfig(from_json_data_text=text, stderr_file=NO_OUTPUT)


def test_level_unknown_field() -> None:
    """Test a level object with an unknown field is rejected."""
    text = _levels_text([{'level': 0, 'name': 'A', 'extra': 1}])
    with pytest.raises(ValueError):
        BacklogOpsConfig(from_json_data_text=text, stderr_file=NO_OUTPUT)


def test_level_number_not_int() -> None:
    """Test a non-integer level number is rejected as a TypeError."""
    text = _levels_text([{'level': 'zero', 'name': 'A'}])
    with pytest.raises(TypeError):
        BacklogOpsConfig(from_json_data_text=text, stderr_file=NO_OUTPUT)


def test_levels_not_a_list() -> None:
    """Test a scalar levels member is rejected as a TypeError."""
    with pytest.raises(TypeError):
        BacklogOpsConfig(from_json_data_text=_ops_text('oops'),
                         stderr_file=NO_OUTPUT)


def test_level_name_not_str() -> None:
    """Test a non-string level name is rejected as a TypeError."""
    text = _levels_text([{'level': 0, 'name': 123}])
    with pytest.raises(TypeError):
        BacklogOpsConfig(from_json_data_text=text, stderr_file=NO_OUTPUT)


def test_alias_not_list() -> None:
    """Test a non-list aliases member is rejected as a TypeError."""
    text = _levels_text([{'level': 0, 'name': 'A', 'aliases': 'oops'}])
    with pytest.raises(TypeError):
        BacklogOpsConfig(from_json_data_text=text, stderr_file=NO_OUTPUT)


def test_level_not_dict() -> None:
    """Test a levels element that is not an object is rejected."""
    text = _ops_text([{'level': 0, 'name': 'A'}, 'notadict'])
    with pytest.raises(TypeError):
        BacklogOpsConfig(from_json_data_text=text, stderr_file=NO_OUTPUT)


def test_status_map_default() -> None:
    """Test the global status input map defaults to empty."""
    assert _empty().get_status_input_map() == {}


def test_status_map_roundtrip(tmp_path: Path) -> None:
    """Test the global status input map survives a write-and-read.

    The map is written with Status member names and read back as Status
    members, reachable through ``get_status_input_map``.
    """
    config = _empty()
    config.status_input_map = {'Implementing': Status.IN_PROGRESS,
                               'Verifying': Status.DONE}
    target = tmp_path / 'cfg.cfg'
    write_backlog_ops_config(config, target, NO_OUTPUT)
    stored = json.loads(target.read_text(encoding='utf-8'))
    assert stored['status_input_map'] == {'Implementing': 'IN_PROGRESS',
                                          'Verifying': 'DONE'}
    loaded = read_backlog_ops_config(target, NO_OUTPUT)
    assert loaded.get_status_input_map() == {
        'Implementing': Status.IN_PROGRESS, 'Verifying': Status.DONE}


def test_status_map_old_file() -> None:
    """Test an older file without a status map defaults to empty."""
    data = json.loads(_empty().as_json_string(NO_OUTPUT))
    del data['status_input_map']
    config = BacklogOpsConfig(from_json_data_text=json.dumps(data),
                              stderr_file=NO_OUTPUT)
    assert config.get_status_input_map() == {}


def test_status_map_bad_value() -> None:
    """Test reading a global status map with a bad value is rejected."""
    data = json.loads(_empty().as_json_string(NO_OUTPUT))
    data['status_input_map'] = {'Testing': 'Nonsense'}
    with pytest.raises(TypeError):
        BacklogOpsConfig(from_json_data_text=json.dumps(data),
                         stderr_file=NO_OUTPUT)
