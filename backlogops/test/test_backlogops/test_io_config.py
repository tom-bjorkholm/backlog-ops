#! /usr/local/bin/python3
"""Tests for the TableIO input and output configuration module."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from config_as_json import InvalidConfiguration
from backlogops import (
    GuiDisplayConfig, InputFormatConfig, LevelDisplay, OutputFormatConfig,
    make_input_config, make_output_config, resolve_input_config,
    resolve_output_config)
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()


@pytest.mark.parametrize('suffix,format_name', [
    ('.csv', 'CSV'), ('.xlsx', 'Excel'), ('.ods', 'ODS')])
def test_input_format(suffix: str, format_name: str) -> None:
    """Test the input format is inferred from the data file extension."""
    config = resolve_input_config(None, data_file=Path('data' + suffix),
                                  stderr_file=NO_OUTPUT)
    assert config.tableio.format_name == format_name
    assert not config.backlog_to_internal
    assert not config.release_to_internal


@pytest.mark.parametrize('suffix,format_name', [
    ('.csv', 'CSV'), ('.xlsx', 'Excel'), ('.ods', 'ODS'),
    ('.html', 'HTML'), ('.tex', 'LaTeX'), ('.md', 'md')])
def test_output_format(suffix: str, format_name: str) -> None:
    """Test the output format is inferred from the data file extension."""
    config = resolve_output_config(None, data_file='data' + suffix,
                                   stderr_file=NO_OUTPUT)
    assert config.tableio.format_name == format_name
    assert not config.backlog_to_external
    assert not config.release_to_external


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
        {'Type': 'level'}, {}, stderr_file=NO_OUTPUT)
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
        {'level': 'Type'}, {'name': 'Release'}, stderr_file=NO_OUTPUT)
    config_file = tmp_path / 'out.cfg'
    source.write(to_json_filename=config_file, stderr_file=NO_OUTPUT)
    resolved = resolve_output_config(str(config_file), data_file='x.csv',
                                     stderr_file=NO_OUTPUT)
    assert resolved.backlog_to_external == {'level': 'Type'}
    assert resolved.release_to_external == {'name': 'Release'}
    assert resolved.tableio.format_name == 'CSV'


def test_in_config_path(tmp_path: Path) -> None:
    """Test an input value with punctuation is read as a config file."""
    source = make_input_config(
        resolve_input_config(None, data_file='x.csv',
                             stderr_file=NO_OUTPUT).tableio,
        {'Type': 'level'}, {'Rel': 'name'}, stderr_file=NO_OUTPUT)
    config_file = tmp_path / 'in.cfg'
    source.write(to_json_filename=config_file, stderr_file=NO_OUTPUT)
    resolved = resolve_input_config(str(config_file), data_file='x.csv',
                                    stderr_file=NO_OUTPUT)
    assert resolved.backlog_to_internal == {'Type': 'level'}
    assert resolved.release_to_internal == {'Rel': 'name'}
    assert resolved.tableio.format_name == 'CSV'


def test_in_cfg_roundtrip(tmp_path: Path) -> None:
    """Test both input maps, including a dropped column, survive a file."""
    config = make_input_config(
        resolve_input_config(None, data_file='x.ods',
                             stderr_file=NO_OUTPUT).tableio,
        {'Type': 'level', 'Junk': None}, {'Rel': 'name'},
        stderr_file=NO_OUTPUT)
    config_file = tmp_path / 'in.cfg'
    config.write(to_json_filename=config_file, stderr_file=NO_OUTPUT)
    loaded = InputFormatConfig(from_json_filename=config_file,
                               stderr_file=NO_OUTPUT)
    assert loaded.backlog_to_internal == {'Type': 'level', 'Junk': None}
    assert loaded.release_to_internal == {'Rel': 'name'}
    assert loaded.tableio.format_name == 'ODS'


def test_in_map_types() -> None:
    """Test an input column-name map of the wrong value type is rejected."""
    with pytest.raises(InvalidConfiguration):
        InputFormatConfig(
            from_json_data_text='{"tableio": {"format_name": "CSV"}, '
            '"backlog_to_internal": {"Type": 5}}', stderr_file=NO_OUTPUT)


def test_in_old_single_map() -> None:
    """Test an older single input map splits into the two per-table maps.

    The full map is copied into the backlog map, while the releases map
    keeps only the entries whose target is a release field.
    """
    config = InputFormatConfig(
        from_json_data_text='{"tableio": {"format_name": "CSV"}, '
        '"to_internal": {"Type": "level", "Rel": "name"}}',
        stderr_file=NO_OUTPUT)
    assert config.backlog_to_internal == {'Type': 'level', 'Rel': 'name'}
    assert config.release_to_internal == {'Rel': 'name'}


def test_in_old_empty() -> None:
    """Test an older input file without any map gets two empty maps."""
    config = InputFormatConfig(
        from_json_data_text='{"tableio": {"format_name": "CSV"}}',
        stderr_file=NO_OUTPUT)
    assert not config.backlog_to_internal
    assert not config.release_to_internal


@pytest.mark.parametrize('member', [
    'backlog_to_external', 'release_to_external'])
def test_map_types(member: str) -> None:
    """Test a column-name map of the wrong value type is rejected."""
    with pytest.raises(InvalidConfiguration):
        OutputFormatConfig(
            from_json_data_text='{"tableio": {"format_name": "CSV"}, '
            f'"{member}": {{"level": 5}}}}', stderr_file=NO_OUTPUT)


def test_out_maps_rt(tmp_path: Path) -> None:
    """Test both output maps, including a dropped column, survive a file."""
    tableio = resolve_output_config(None, data_file='x.csv',
                                    stderr_file=NO_OUTPUT).tableio
    source = make_output_config(tableio, {'level': 'Size',
                                          'story_points': None},
                                {'name': 'Release'}, stderr_file=NO_OUTPUT)
    config_file = tmp_path / 'out.cfg'
    source.write(to_json_filename=config_file, stderr_file=NO_OUTPUT)
    loaded = OutputFormatConfig(from_json_filename=config_file,
                                stderr_file=NO_OUTPUT)
    assert loaded.backlog_to_external == {'level': 'Size',
                                          'story_points': None}
    assert loaded.release_to_external == {'name': 'Release'}


def test_out_old_single_map() -> None:
    """Test an older single output map becomes the backlog map."""
    config = OutputFormatConfig(
        from_json_data_text='{"tableio": {"format_name": "CSV"}, '
        '"to_external": {"level": "Type"}}', stderr_file=NO_OUTPUT)
    assert config.backlog_to_external == {'level': 'Type'}
    assert not config.release_to_external


def test_out_display_default() -> None:
    """Test a default output config shows both number and name."""
    config = resolve_output_config(None, data_file='x.csv',
                                   stderr_file=NO_OUTPUT)
    assert config.level_display is LevelDisplay.BOTH


def test_make_output_display() -> None:
    """Test the level display passed to make_output_config is kept."""
    tableio = resolve_output_config(None, data_file='x.csv',
                                    stderr_file=NO_OUTPUT).tableio
    config = make_output_config(tableio, {}, {}, LevelDisplay.NAME,
                                stderr_file=NO_OUTPUT)
    assert config.level_display is LevelDisplay.NAME


def test_out_display_rt(tmp_path: Path) -> None:
    """Test the level display survives a write and read of the config."""
    tableio = resolve_output_config(None, data_file='x.csv',
                                    stderr_file=NO_OUTPUT).tableio
    source = make_output_config(tableio, {}, {}, LevelDisplay.NUMERIC,
                                stderr_file=NO_OUTPUT)
    config_file = tmp_path / 'out.cfg'
    source.write(to_json_filename=config_file, stderr_file=NO_OUTPUT)
    loaded = OutputFormatConfig(from_json_filename=config_file,
                                stderr_file=NO_OUTPUT)
    assert loaded.level_display is LevelDisplay.NUMERIC


def test_out_old_no_display() -> None:
    """Test an older output config without a display defaults to both."""
    config = OutputFormatConfig(
        from_json_data_text='{"tableio": {"format_name": "CSV"}, '
        '"to_external": {}}', stderr_file=NO_OUTPUT)
    assert config.level_display is LevelDisplay.BOTH


def test_gui_display_default() -> None:
    """Test a default GUI display config shows both and renames nothing."""
    config = GuiDisplayConfig(stderr_file=NO_OUTPUT)
    assert config.level_display is LevelDisplay.BOTH
    assert not config.backlog_to_external
    assert not config.release_to_external


def test_gui_display_rt(tmp_path: Path) -> None:
    """Test the GUI display, maps and a dropped column survive a file."""
    source = GuiDisplayConfig(stderr_file=NO_OUTPUT)
    source.level_display = LevelDisplay.NAME
    source.backlog_to_external = {'key': 'Id', 'team': None}
    source.release_to_external = {'name': 'Release'}
    config_file = tmp_path / 'gui.cfg'
    source.write(to_json_filename=config_file, stderr_file=NO_OUTPUT)
    loaded = GuiDisplayConfig(from_json_filename=config_file,
                              stderr_file=NO_OUTPUT)
    assert loaded.level_display is LevelDisplay.NAME
    assert loaded.backlog_to_external == {'key': 'Id', 'team': None}
    assert loaded.release_to_external == {'name': 'Release'}


def test_gui_bad_map() -> None:
    """Test a GUI column-name map of the wrong value type is rejected."""
    with pytest.raises(InvalidConfiguration):
        GuiDisplayConfig(
            from_json_data_text='{"backlog_to_external": {"key": 5}}',
            stderr_file=NO_OUTPUT)


def test_gui_old_default() -> None:
    """Test a GUI display config without members defaults to empty maps."""
    config = GuiDisplayConfig(from_json_data_text='{}', stderr_file=NO_OUTPUT)
    assert config.level_display is LevelDisplay.BOTH
    assert not config.backlog_to_external
    assert not config.release_to_external
