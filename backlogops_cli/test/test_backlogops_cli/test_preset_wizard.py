#! /usr/local/bin/python3
"""Tests for the backlogops_cli preset_wizard command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from pathlib import Path
import pytest
from backlogops import (
    InputFormatConfig, LevelDisplay, NoTextIO, OutputFormatConfig)
from backlogops_cli.list import command_modules
from backlogops_cli import preset_wizard

CSV_OPTS = [''] * 7
"""Blank answers for the CSV format encoding and six option cells."""


def test_in_command_list() -> None:
    """Test preset_wizard is discovered as a command."""
    names = [name for name, _ in command_modules()]
    assert 'preset_wizard' in names


def test_requires_output() -> None:
    """Test the command requires the output file argument."""
    with pytest.raises(SystemExit):
        preset_wizard.build_parser().parse_args([])


def test_no_textual_flag() -> None:
    """Test the --no-textual switch is parsed as a boolean flag."""
    parser = preset_wizard.build_parser()
    assert parser.parse_args(['-o', 'x']).no_textual is False
    assert parser.parse_args(['-o', 'x', '--no-textual']).no_textual is True


def test_writes_input_preset(tmp_path: Path,
                             monkeypatch: pytest.MonkeyPatch) -> None:
    """Test creating an input preset writes a readable preset file.

    The ``.cfg`` extension is added, and the file reads back as an input
    config whose backlog map reads file column ``Type`` into ``level``.
    """
    answers = ['input', '1'] + CSV_OPTS + ['2', 'Type', ''] + ['', '']
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'.join(answers) + '\n'))
    assert preset_wizard.main(
        ['-o', str(tmp_path / 'in'), '--no-textual']) == 0
    written = tmp_path / 'in.cfg'
    assert written.exists()
    loaded = InputFormatConfig(from_json_filename=written,
                               stderr_file=NoTextIO())
    assert loaded.backlog_to_internal == {'Type': 'level'}


def test_writes_output_preset(tmp_path: Path,
                              monkeypatch: pytest.MonkeyPatch) -> None:
    """Test creating an output preset writes a readable preset file.

    The file reads back as an output config whose level display is the
    numeric one selected in the wizard.
    """
    answers = ['output', '1'] + CSV_OPTS + ['', ''] + ['numeric']
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'.join(answers) + '\n'))
    assert preset_wizard.main(
        ['-o', str(tmp_path / 'out'), '--no-textual']) == 0
    loaded = OutputFormatConfig(from_json_filename=tmp_path / 'out.cfg',
                                stderr_file=NoTextIO())
    assert loaded.level_display == LevelDisplay.NUMERIC


def test_abort_returns_one(tmp_path: Path,
                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Test aborting the wizard returns 1 and writes no file."""
    monkeypatch.setattr('sys.stdin', io.StringIO(':q\n'))
    assert preset_wizard.main(
        ['-o', str(tmp_path / 'in'), '--no-textual']) == 1
    assert not (tmp_path / 'in.cfg').exists()


def test_overwrite_declined(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test declining the overwrite keeps the file and skips the wizard."""
    target = tmp_path / 'in.cfg'
    target.write_text('OLD', encoding='utf-8')
    monkeypatch.setattr('sys.stdin', io.StringIO('n\n'))
    assert preset_wizard.main(
        ['-o', str(tmp_path / 'in'), '--no-textual']) == 1
    assert target.read_text(encoding='utf-8') == 'OLD'


def test_overwrite_force(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the force flag overwrites the existing file without asking."""
    target = tmp_path / 'in.cfg'
    target.write_text('OLD', encoding='utf-8')
    answers = ['input', '1'] + CSV_OPTS + ['', '', '']
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'.join(answers) + '\n'))
    assert preset_wizard.main(
        ['-o', str(tmp_path / 'in'), '--no-textual', '-f']) == 0
    loaded = InputFormatConfig(from_json_filename=target,
                               stderr_file=NoTextIO())
    assert not loaded.backlog_to_internal
