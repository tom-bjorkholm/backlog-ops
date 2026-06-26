#! /usr/local/bin/python3
"""Tests for the top-level BacklogOpsConfig configuration object.

The tests cover the nested workforce, the named TableIO presets, the
optional levels member (its JSON shape, the omit-when-default behaviour
and the rebuilt levels mapping) and the migration of older files that
stored the workforce members at the top level.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import json
from pathlib import Path
import pytest
from backlogops import (
    AvailableTeams, BacklogOpsConfig, DEFAULT_LEVELS, Level, LevelDisplay,
    make_input_config, make_output_config, read_backlog_ops_config,
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
        {'Type': 'level'}, stderr_file=NO_OUTPUT)}
    config.output_configs = {'report': make_output_config(
        resolve_output_config(None, data_file='x.xlsx',
                              stderr_file=NO_OUTPUT).tableio,
        {'level': 'Type'}, stderr_file=NO_OUTPUT)}
    config_file = tmp_path / 'ops.cfg'
    write_backlog_ops_config(config, config_file, NO_OUTPUT)
    loaded = read_backlog_ops_config(config_file, NO_OUTPUT)
    assert loaded.input_configs['sheet'].to_internal == {'Type': 'level'}
    assert loaded.output_configs['report'].tableio.format_name == 'Excel'


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
