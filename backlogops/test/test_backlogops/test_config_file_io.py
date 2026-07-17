#! /usr/local/bin/python3
"""Tests for reading a preset file and crash-safe configuration writing.

:func:`read_io_preset` reads a stand-alone preset file and detects its
direction from the file contents, terminating with ``SystemExit`` when the
file is missing or is not a preset. :func:`safe_write_config` writes a
configuration through a ``.in_progress`` sibling and an atomic move, so a
crash before the move leaves the old file intact and the new configuration
in the sibling.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import os
from pathlib import Path
from typing import Optional
import pytest
from config_as_json import ConfigAutoChangeHook
from backlogops import (
    InputFormatConfig, LevelDisplay, NoTextIO, OutputFormatConfig,
    read_io_preset, safe_write_config)


def _write_input(path: Path) -> None:
    """Write an input preset whose backlog map renames one column."""
    config = InputFormatConfig(stderr_file=NoTextIO())
    config.backlog_to_internal = {'Type': 'level'}
    config.write(to_json_filename=path, stderr_file=NoTextIO())


def _write_output(path: Path) -> None:
    """Write an output preset with the numeric level display."""
    config = OutputFormatConfig(stderr_file=NoTextIO())
    config.level_display = LevelDisplay.NUMERIC
    config.write(to_json_filename=path, stderr_file=NoTextIO())


def _hook() -> ConfigAutoChangeHook:
    """Return a plain auto-change hook that reacts to nothing."""
    return ConfigAutoChangeHook()


def test_read_input_preset(tmp_path: Path) -> None:
    """Test an input preset file is detected and read as an input config."""
    source = tmp_path / 'in.cfg'
    _write_input(source)
    config = read_io_preset(str(source), _hook(), NoTextIO())
    assert isinstance(config, InputFormatConfig)
    assert config.backlog_to_internal == {'Type': 'level'}


def test_read_output_preset(tmp_path: Path) -> None:
    """Test an output preset file is detected and read as output config."""
    source = tmp_path / 'out.cfg'
    _write_output(source)
    config = read_io_preset(str(source), _hook(), NoTextIO())
    assert isinstance(config, OutputFormatConfig)
    assert config.level_display == LevelDisplay.NUMERIC


def test_read_missing_exits(tmp_path: Path) -> None:
    """Test reading a missing preset file terminates with SystemExit."""
    with pytest.raises(SystemExit):
        read_io_preset(str(tmp_path / 'nope.cfg'), _hook(), NoTextIO())


def test_read_not_preset(tmp_path: Path) -> None:
    """Test a file that is neither input nor output preset is rejected."""
    bad = tmp_path / 'bad.cfg'
    bad.write_text('{"foo": 1}', encoding='utf-8')
    with pytest.raises(SystemExit):
        read_io_preset(str(bad), _hook(), NoTextIO())


def _map_of(path: Path) -> dict[str, Optional[str]]:
    """Return the backlog map of the input preset stored in the file."""
    config = InputFormatConfig(from_json_filename=path, stderr_file=NoTextIO())
    return config.backlog_to_internal


def test_safe_write_new_file(tmp_path: Path) -> None:
    """Test writing to a fresh path creates it and leaves no sibling."""
    config = InputFormatConfig(stderr_file=NoTextIO())
    config.backlog_to_internal = {'Type': 'level'}
    output = tmp_path / 'new.cfg'
    safe_write_config(config, str(output), NoTextIO())
    assert _map_of(output) == {'Type': 'level'}
    assert not (tmp_path / 'new.cfg.in_progress').exists()


def test_safe_write_replaces(tmp_path: Path) -> None:
    """Test writing over an existing file replaces its contents."""
    output = tmp_path / 'old.cfg'
    _write_input(output)
    config = OutputFormatConfig(stderr_file=NoTextIO())
    config.level_display = LevelDisplay.NUMERIC
    safe_write_config(config, str(output), NoTextIO())
    loaded = OutputFormatConfig(from_json_filename=output,
                                stderr_file=NoTextIO())
    assert loaded.level_display == LevelDisplay.NUMERIC
    assert not (tmp_path / 'old.cfg.in_progress').exists()


def test_safe_write_crash(tmp_path: Path,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a crash before the atomic move loses no information.

    The move is made to fail to simulate a kill at the worst moment. The
    old output file must then still hold its original contents and the new
    configuration must be fully present in the ``.in_progress`` sibling.
    """
    output = tmp_path / 'teams.cfg'
    _write_input(output)
    new_config = InputFormatConfig(stderr_file=NoTextIO())
    new_config.backlog_to_internal = {'Story': 'level'}

    def _boom(_src: object, _dst: object) -> None:
        """Fail the atomic move to simulate a crash before it completes."""
        raise OSError('simulated crash before move')
    monkeypatch.setattr(os, 'replace', _boom)
    with pytest.raises(OSError):
        safe_write_config(new_config, str(output), NoTextIO())
    assert _map_of(output) == {'Type': 'level'}
    assert _map_of(tmp_path / 'teams.cfg.in_progress') == {'Story': 'level'}
