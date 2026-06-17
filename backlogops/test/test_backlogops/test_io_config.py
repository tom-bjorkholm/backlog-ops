#! /usr/local/bin/python3
"""Tests for the TableIO input and output configuration module."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from config_as_json import InvalidConfiguration
from backlogops import (
    InputFormatConfig, OutputFormatConfig, make_input_config,
    make_output_config, resolve_input_config, resolve_output_config)
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()


@pytest.mark.parametrize('suffix,format_name', [
    ('.csv', 'CSV'), ('.xlsx', 'Excel'), ('.ods', 'ODS')])
def test_input_format(suffix: str, format_name: str) -> None:
    """Test the input format is inferred from the data file extension."""
    config = resolve_input_config(None, data_file=Path('data' + suffix),
                                  stderr_file=NO_OUTPUT)
    assert config.tableio.format_name == format_name
    assert config.to_internal == {}


@pytest.mark.parametrize('suffix,format_name', [
    ('.csv', 'CSV'), ('.xlsx', 'Excel'), ('.ods', 'ODS'),
    ('.html', 'HTML'), ('.tex', 'LaTeX'), ('.md', 'md')])
def test_output_format(suffix: str, format_name: str) -> None:
    """Test the output format is inferred from the data file extension."""
    config = resolve_output_config(None, data_file='data' + suffix,
                                   stderr_file=NO_OUTPUT)
    assert config.tableio.format_name == format_name
    assert config.to_external == {}


def test_unknown_ext() -> None:
    """Test an unknown extension cannot be inferred to a format."""
    with pytest.raises(ValueError):
        resolve_output_config(None, data_file='data.unknown',
                              stderr_file=NO_OUTPUT)


def test_preset_name() -> None:
    """Test an all-alphanumeric value is looked up among the presets."""
    preset = make_input_config(
        resolve_input_config(None, data_file='x.csv',
                             stderr_file=NO_OUTPUT).tableio,
        {'Type': 'level'}, stderr_file=NO_OUTPUT)
    resolved = resolve_input_config('excel', data_file='x.csv',
                                    presets={'excel': preset},
                                    stderr_file=NO_OUTPUT)
    assert resolved is preset


@pytest.mark.parametrize('value', ['missing', 'unknown'])
def test_bad_preset(value: str) -> None:
    """Test an unknown preset name is reported as an error."""
    with pytest.raises(ValueError):
        resolve_output_config(value, data_file='x.csv', presets={},
                              stderr_file=NO_OUTPUT)


def test_config_path(tmp_path: Path) -> None:
    """Test a value with punctuation is read as a stand-alone config file."""
    source = make_output_config(
        resolve_output_config(None, data_file='x.csv',
                              stderr_file=NO_OUTPUT).tableio,
        {'level': 'Type'}, stderr_file=NO_OUTPUT)
    config_file = tmp_path / 'out.cfg'
    source.write(to_json_filename=config_file, stderr_file=NO_OUTPUT)
    resolved = resolve_output_config(str(config_file), data_file='x.csv',
                                     stderr_file=NO_OUTPUT)
    assert resolved.to_external == {'level': 'Type'}
    assert resolved.tableio.format_name == 'CSV'


def test_in_config_path(tmp_path: Path) -> None:
    """Test an input value with punctuation is read as a config file."""
    source = make_input_config(
        resolve_input_config(None, data_file='x.csv',
                             stderr_file=NO_OUTPUT).tableio,
        {'Type': 'level'}, stderr_file=NO_OUTPUT)
    config_file = tmp_path / 'in.cfg'
    source.write(to_json_filename=config_file, stderr_file=NO_OUTPUT)
    resolved = resolve_input_config(str(config_file), data_file='x.csv',
                                    stderr_file=NO_OUTPUT)
    assert resolved.to_internal == {'Type': 'level'}
    assert resolved.tableio.format_name == 'CSV'


def test_in_cfg_roundtrip(tmp_path: Path) -> None:
    """Test an input config keeps its map and format across a file."""
    config = make_input_config(
        resolve_input_config(None, data_file='x.ods',
                             stderr_file=NO_OUTPUT).tableio,
        {'Type': 'level', 'Item type': 'level'}, stderr_file=NO_OUTPUT)
    config_file = tmp_path / 'in.cfg'
    config.write(to_json_filename=config_file, stderr_file=NO_OUTPUT)
    loaded = InputFormatConfig(from_json_filename=config_file,
                               stderr_file=NO_OUTPUT)
    assert loaded.to_internal == {'Type': 'level', 'Item type': 'level'}
    assert loaded.tableio.format_name == 'ODS'


def test_map_types() -> None:
    """Test a column-name map of the wrong value type is rejected."""
    with pytest.raises(InvalidConfiguration):
        OutputFormatConfig(
            from_json_data_text='{"tableio": {"format_name": "CSV"}, '
            '"to_external": {"level": 5}}', stderr_file=NO_OUTPUT)
