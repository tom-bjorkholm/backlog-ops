#! /usr/local/bin/python3
"""Tests for the shared command IO helpers."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import io
from datetime import date
from pathlib import Path
from typing import Optional
import pytest
from packaging.version import Version
from backlogops import AvailableTeams, BacklogOpsConfig, allow_overwrite
from backlogops.no_text_io import NoTextIO
from backlogops_cli import _command_io
from backlogops_cli.bloc_version_reporter import BloCliVersionReporter

NO_OUTPUT = NoTextIO()


def _write_config(path: Path) -> None:
    """Write a current-format backlog-ops configuration file."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]),
        stderr_file=NO_OUTPUT)
    config.write(to_json_filename=path, stderr_file=NO_OUTPUT)


def _parsed(config: Optional[str]) -> argparse.Namespace:
    """Return a parsed namespace holding only the ``config`` value."""
    return argparse.Namespace(config=config)


def _set_pyver(monkeypatch: pytest.MonkeyPatch, pyver: str) -> None:
    """Make the reporter see the given Python version, past the cutoffs."""
    monkeypatch.setattr(BloCliVersionReporter, '_today',
                        lambda self: date(2027, 10, 1))
    monkeypatch.setattr(BloCliVersionReporter, '_python_version',
                        staticmethod(lambda: Version(pyver)))


def _parser() -> argparse.ArgumentParser:
    """Return a tiny parser with one optional argument."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-x', dest='x')
    return parser


def test_checks_python(monkeypatch: pytest.MonkeyPatch,
                       capsys: pytest.CaptureFixture[str]) -> None:
    """Test parsing warns when the running Python is unsupported."""
    _set_pyver(monkeypatch, '3.11')
    result = _command_io.parsed_args(_parser(), ['-x', 'v'])
    assert result.x == 'v'
    assert 'old version of Python' in capsys.readouterr().out


def test_no_warn_supported(monkeypatch: pytest.MonkeyPatch,
                           capsys: pytest.CaptureFixture[str]) -> None:
    """Test parsing is quiet when the running Python is supported."""
    _set_pyver(monkeypatch, '3.14')
    _command_io.parsed_args(_parser(), [])
    assert capsys.readouterr().out == ''


def test_force_allows() -> None:
    """Test force returns the always-allow callback that never asks."""
    assert _command_io.overwrite_callback(True) is allow_overwrite


@pytest.mark.parametrize('answer', ['y\n', 'Y\n', 'yes\n', ' YES \n'])
def test_prompt_yes(answer: str) -> None:
    """Test a yes answer allows the overwrite and the prompt is shown."""
    out = io.StringIO()
    callback = _command_io.overwrite_callback(False, io.StringIO(answer), out)
    callback('file.csv')
    assert 'file.csv' in out.getvalue()


@pytest.mark.parametrize('answer', ['n\n', '\n', 'no\n', 'maybe\n', ''])
def test_prompt_no(answer: str) -> None:
    """Test a non-yes, empty, or end-of-input answer refuses the write."""
    callback = _command_io.overwrite_callback(False, io.StringIO(answer),
                                              io.StringIO())
    with pytest.raises(FileExistsError):
        callback('file.csv')


def test_add_force_arg() -> None:
    """Test the force flag defaults to False and is set by -f/--force."""
    parser = argparse.ArgumentParser()
    _command_io.add_force_arg(parser)
    assert parser.parse_args([]).force is False
    assert parser.parse_args(['-f']).force is True
    assert parser.parse_args(['--force']).force is True


def test_add_config_arg() -> None:
    """Test -c/--config sets the config path and defaults to None."""
    parser = argparse.ArgumentParser()
    _command_io.add_config_arg(parser)
    assert parser.parse_args([]).config is None
    assert parser.parse_args(['-c', 'f.cfg']).config == 'f.cfg'
    assert parser.parse_args(['--config', 'f.cfg']).config == 'f.cfg'


def test_io_parser_full() -> None:
    """Test the parser has input, config and output options by default."""
    parser = _command_io.build_io_parser('desc')
    parsed = parser.parse_args(['-i', 'in', '-o', 'out', '-c', 'cfg',
                                '-I', 'ic', '-O', 'oc'])
    assert parsed.input == 'in'
    assert parsed.output == 'out'
    assert parsed.config == 'cfg'
    assert parsed.input_config == 'ic'
    assert parsed.output_config == 'oc'


def test_io_parser_no_input() -> None:
    """Test with_input=False drops the input options."""
    parser = _command_io.build_io_parser('desc', with_input=False)
    assert parser.parse_args(['-o', 'out']).output == 'out'
    with pytest.raises(SystemExit):
        parser.parse_args(['-i', 'in', '-o', 'out'])


def test_io_parser_no_output() -> None:
    """Test with_output=False drops the output options."""
    parser = _command_io.build_io_parser('desc', with_output=False)
    assert parser.parse_args(['-i', 'in']).input == 'in'
    with pytest.raises(SystemExit):
        parser.parse_args(['-i', 'in', '-o', 'out'])


def test_io_parser_no_config() -> None:
    """Test with_config=False drops the -c option."""
    parser = _command_io.build_io_parser('desc', with_config=False)
    with pytest.raises(SystemExit):
        parser.parse_args(['-i', 'in', '-o', 'out', '-c', 'cfg'])


def test_opt_config_named(tmp_path: Path) -> None:
    """Test optional_config reads the file named by -c."""
    path = tmp_path / 'cfg.cfg'
    _write_config(path)
    assert _command_io.optional_config(_parsed(str(path))) is not None


def test_opt_config_found(tmp_path: Path,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Test optional_config discovers $BACKLOGOPS_CFG when -c is absent."""
    path = tmp_path / 'cfg.cfg'
    _write_config(path)
    monkeypatch.setenv('BACKLOGOPS_CFG', str(path))
    assert _command_io.optional_config(_parsed(None)) is not None


def test_opt_config_none(capsys: pytest.CaptureFixture[str]) -> None:
    """Test optional_config returns None with a note when none is found."""
    assert _command_io.optional_config(_parsed(None)) is None
    assert 'using built-in defaults' in capsys.readouterr().err


def test_opt_config_missing(tmp_path: Path) -> None:
    """Test a -c file that does not exist raises ValueError."""
    with pytest.raises(ValueError, match='not found'):
        _command_io.optional_config(_parsed(str(tmp_path / 'no.cfg')))


def test_req_config_named(tmp_path: Path) -> None:
    """Test required_config reads the file named by -c."""
    path = tmp_path / 'cfg.cfg'
    _write_config(path)
    assert _command_io.required_config(_parsed(str(path))) is not None


def test_req_config_none() -> None:
    """Test required_config raises ValueError when none is found."""
    with pytest.raises(ValueError, match='No backlog-ops configuration'):
        _command_io.required_config(_parsed(None))


def test_req_config_missing(tmp_path: Path) -> None:
    """Test required_config raises ValueError for a missing -c file."""
    with pytest.raises(ValueError, match='not found'):
        _command_io.required_config(_parsed(str(tmp_path / 'no.cfg')))


def test_io_levels_none() -> None:
    """Test io_levels returns None when there is no configuration."""
    assert _command_io.io_levels(None) is None


def test_io_levels_config() -> None:
    """Test io_levels returns the configured levels from a config."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]),
        stderr_file=NO_OUTPUT)
    assert _command_io.io_levels(config) is not None
