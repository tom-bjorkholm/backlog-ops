#! /usr/local/bin/python3
"""Tests for the TableIO presets stored in the teams configuration."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import json
from pathlib import Path
from backlogops import (
    AvailableTeams, AvailableTeamsConfig, make_input_config,
    make_output_config, read_available_teams, resolve_input_config,
    resolve_output_config)
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()


def _empty_config() -> AvailableTeamsConfig:
    """Return a teams configuration for an empty workforce."""
    return AvailableTeamsConfig(neutral=AvailableTeams(persons={}, teams=[]),
                                stderr_file=NO_OUTPUT)


def test_new_file_presets(tmp_path: Path) -> None:
    """Test a written teams file holds empty preset maps by default."""
    config_file = tmp_path / 'teams.cfg'
    _empty_config().write(to_json_filename=config_file, stderr_file=NO_OUTPUT)
    data = json.loads(config_file.read_text(encoding='UTF-8'))
    assert data['input_configs'] == {}
    assert data['output_configs'] == {}


def test_old_file_loads(tmp_path: Path) -> None:
    """Test a file written before the presets existed still loads."""
    config_file = tmp_path / 'old.cfg'
    full = json.loads(_empty_config().as_json_string(NO_OUTPUT))
    old = {key: value for key, value in full.items()
           if key not in ('input_configs', 'output_configs')}
    config_file.write_text(json.dumps(old), encoding='UTF-8')
    loaded = read_available_teams(config_file, NO_OUTPUT)
    assert not loaded.input_configs
    assert not loaded.output_configs


def test_presets_round_trip(tmp_path: Path) -> None:
    """Test named input and output presets survive a write and read."""
    config = _empty_config()
    input_preset = make_input_config(
        resolve_input_config(None, data_file='x.csv',
                             stderr_file=NO_OUTPUT).tableio,
        {'Type': 'level'}, stderr_file=NO_OUTPUT)
    output_preset = make_output_config(
        resolve_output_config(None, data_file='x.xlsx',
                              stderr_file=NO_OUTPUT).tableio,
        {'level': 'Type'}, stderr_file=NO_OUTPUT)
    config.input_configs = {'sheet': input_preset}
    config.output_configs = {'report': output_preset}
    config_file = tmp_path / 'teams.cfg'
    config.write(to_json_filename=config_file, stderr_file=NO_OUTPUT)
    loaded = read_available_teams(config_file, NO_OUTPUT)
    assert loaded.input_configs['sheet'].to_internal == {'Type': 'level'}
    assert loaded.output_configs['report'].tableio.format_name == 'Excel'
    resolved = resolve_input_config('sheet', data_file='x.csv',
                                    presets=loaded.input_configs,
                                    stderr_file=NO_OUTPUT)
    assert resolved.to_internal == {'Type': 'level'}
