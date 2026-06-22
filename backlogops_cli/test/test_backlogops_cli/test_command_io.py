#! /usr/local/bin/python3
"""Tests for the shared command IO helpers."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import io
from datetime import date
import pytest
from packaging.version import Version
from backlogops import allow_overwrite
from backlogops_cli import _command_io
from backlogops_cli.bloc_version_reporter import BloCliVersionReporter


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
