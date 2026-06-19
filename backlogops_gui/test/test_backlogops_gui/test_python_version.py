#! /usr/local/bin/python3
"""Tests for the GUI Python version support check."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable, Optional, TextIO
import pytest
from backlogops.blo_version_reporter import BloVersionReporter
from backlogops_gui import python_version
from backlogops_gui.python_version import check_python_version


def _writer(message: str) -> Callable[..., None]:
    """Return a support-check stub writing the given message."""
    def write(out_file: Optional[TextIO] = None) -> None:
        """Write the configured message to the stream, if any."""
        if message:
            print(message, file=out_file)
    return write


def _stub_reporter(monkeypatch: pytest.MonkeyPatch,
                   message: str) -> BloVersionReporter:
    """Return a reporter whose support check writes the message."""
    reporter = BloVersionReporter()
    monkeypatch.setattr(reporter, 'check_if_unsupported_python',
                        _writer(message))
    return reporter


def test_warns_unsupported(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the captured warning text is returned when present."""
    reporter = _stub_reporter(monkeypatch, 'Old Python in use')
    assert check_python_version(reporter) == 'Old Python in use'


def test_silent_when_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test no warning is returned when nothing is written."""
    assert check_python_version(_stub_reporter(monkeypatch, '')) is None


@pytest.mark.parametrize('blank', ['', '\n', '  \n  '])
def test_blank_is_none(monkeypatch: pytest.MonkeyPatch, blank: str) -> None:
    """Test blank or whitespace output yields no warning."""
    assert check_python_version(_stub_reporter(monkeypatch, blank)) is None


def test_default_reporter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the GUI reporter is constructed when none is given."""
    reporter = _stub_reporter(monkeypatch, 'default reporter used')
    monkeypatch.setattr(python_version, 'BloGuiVersionReporter',
                        lambda: reporter)
    assert check_python_version() == 'default reporter used'
