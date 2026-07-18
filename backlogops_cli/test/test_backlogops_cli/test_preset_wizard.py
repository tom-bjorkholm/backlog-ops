#! /usr/local/bin/python3
"""Tests for the backlogops_cli preset_wizard command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from pathlib import Path
from typing import Optional, TypeVar
import pytest
from backlogops import (
    BacklogOpsConfig, InputFormatConfig, LevelDisplay, NoTextIO,
    OutputFormatConfig)
from backlogops_cli.list import command_modules
from backlogops_cli import preset_wizard

CSV_OPTS = [''] * 7
"""Blank answers for the CSV format encoding and six option cells."""

_Cfg = TypeVar('_Cfg')


def _write_input(path: Path) -> None:
    """Write a readable input preset whose backlog map renames one column."""
    config = InputFormatConfig(stderr_file=NoTextIO())
    config.backlog_to_internal = {'Type': 'level'}
    config.write(to_json_filename=path, stderr_file=NoTextIO())


def _write_output(path: Path) -> None:
    """Write a readable output preset with the numeric level display."""
    config = OutputFormatConfig(stderr_file=NoTextIO())
    config.level_display = LevelDisplay.NUMERIC
    config.write(to_json_filename=path, stderr_file=NoTextIO())


def _echo_preset(_bridge: object, *, default: Optional[_Cfg] = None,
                 backward: bool = False) -> Optional[_Cfg]:
    """Return the pre-fill default unchanged (a no-op wizard for tests)."""
    _ = backward
    return default


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


def test_input_flag() -> None:
    """Test the optional -i/--input pre-fill file argument is parsed."""
    parser = preset_wizard.build_parser()
    assert parser.parse_args(['-o', 'x']).input is None
    assert parser.parse_args(['-o', 'x', '-i', 'y']).input == 'y'
    assert parser.parse_args(['-o', 'x', '--input', 'y']).input == 'y'


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


def test_prefill_input(tmp_path: Path,
                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Test -i on an input preset detects it and pre-fills the wizard.

    The no-op wizard returns the pre-fill unchanged, so the output file
    reads back as an input preset with the map from the input file.
    """
    source = tmp_path / 'source.cfg'
    _write_input(source)
    monkeypatch.setattr(preset_wizard, 'preset_wizard', _echo_preset)
    out = tmp_path / 'out.cfg'
    assert preset_wizard.main(
        ['-i', str(source), '-o', str(out), '--no-textual']) == 0
    loaded = InputFormatConfig(from_json_filename=out, stderr_file=NoTextIO())
    assert loaded.backlog_to_internal == {'Type': 'level'}


def test_prefill_output(tmp_path: Path,
                        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test -i on an output preset detects it and pre-fills the wizard."""
    source = tmp_path / 'source.cfg'
    _write_output(source)
    monkeypatch.setattr(preset_wizard, 'preset_wizard', _echo_preset)
    out = tmp_path / 'out.cfg'
    assert preset_wizard.main(
        ['-i', str(source), '-o', str(out), '--no-textual']) == 0
    loaded = OutputFormatConfig(from_json_filename=out, stderr_file=NoTextIO())
    assert loaded.level_display == LevelDisplay.NUMERIC


def test_edit_in_place(tmp_path: Path,
                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Test -i and -o naming the same preset file edits it in place."""
    target = tmp_path / 'in.cfg'
    _write_input(target)
    monkeypatch.setattr(preset_wizard, 'preset_wizard', _echo_preset)
    monkeypatch.setattr('sys.stdin', io.StringIO('y\n'))
    assert preset_wizard.main(
        ['-i', str(target), '-o', str(target), '--no-textual']) == 0
    loaded = InputFormatConfig(from_json_filename=target,
                               stderr_file=NoTextIO())
    assert loaded.backlog_to_internal == {'Type': 'level'}
    assert not (tmp_path / 'in.cfg.in_progress').exists()


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing pre-fill file makes the command fail cleanly."""
    out = tmp_path / 'out.cfg'
    assert preset_wizard.main(
        ['-i', str(tmp_path / 'nope.cfg'), '-o', str(out),
         '--no-textual']) == 1
    assert not out.exists()


def test_not_preset(tmp_path: Path,
                    capsys: pytest.CaptureFixture[str]) -> None:
    """Test a file that is neither preset is reported and returns 1."""
    bad = tmp_path / 'bad.cfg'
    bad.write_text('{"foo": 1}', encoding='utf-8')
    out = tmp_path / 'out.cfg'
    assert preset_wizard.main(['-i', str(bad), '-o', str(out),
                               '--no-textual']) == 1
    assert not out.exists()
    assert 'not a recognised' in capsys.readouterr().err


def test_prefill_complete(tmp_path: Path,
                          capsys: pytest.CaptureFixture[str]) -> None:
    """Test basing a preset on a complete config file is reported.

    Pointing ``-i`` at a whole backlog-ops configuration file where a
    stand-alone preset is expected must fail cleanly with a clear message,
    write no output, and never silently start an empty wizard.
    """
    source = tmp_path / 'full.cfg'
    config = BacklogOpsConfig(stderr_file=NoTextIO())
    config.write(to_json_filename=source, stderr_file=NoTextIO())
    out = tmp_path / 'out.cfg'
    assert preset_wizard.main(['-i', str(source), '-o', str(out),
                               '--no-textual']) == 1
    assert not out.exists()
    assert 'complete backlog-ops' in capsys.readouterr().err
