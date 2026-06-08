#! /usr/local/bin/python3
"""Tests for Tcl/Tk version checks."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Optional

import pytest

from backlogops_gui.tcltk_version import check_tcltk_version
from backlogops_gui.tcltk_version import warning_for_version


class FakeTcl:  # pylint: disable=too-few-public-methods
    """Fake Tcl interpreter returning a configured patch level."""

    def __init__(self, version_text: str,
                 error_text: Optional[str] = None) -> None:
        """Store the configured version text or read error."""
        self.version_text = version_text
        self.error_text = error_text

    def call(self, *args: object) -> object:
        """Return the fake patch level or raise the fake read error."""
        assert args == ('info', 'patchlevel')
        if self.error_text is not None:
            raise tk.TclError(self.error_text)
        return self.version_text


def _make_root(fake_tcl: FakeTcl) -> tk.Tk:
    """Return a Tk root shell with a fake Tcl interpreter."""
    root = object.__new__(tk.Tk)
    setattr(root, 'tk', fake_tcl)
    return root


@pytest.mark.parametrize('version_text', ['9.0.2', '9.1.0', '10.0.0'])
def test_new_versions_ok(version_text: str) -> None:
    """Test current and newer Tcl/Tk versions do not warn."""
    assert warning_for_version(version_text) is None


@pytest.mark.parametrize('version_text', ['8.6.13', '9.0.1'])
def test_old_versions_warn(version_text: str) -> None:
    """Test old Tcl/Tk versions warn with the running version."""
    warning_text = warning_for_version(version_text)
    assert warning_text is not None
    assert version_text in warning_text
    assert 'malformed' not in warning_text


@pytest.mark.parametrize('version_text', ['', '9.0', '9.0.beta'])
def test_bad_versions_warn(version_text: str) -> None:
    """Test malformed Tcl/Tk versions get a clear warning."""
    warning_text = warning_for_version(version_text)
    assert warning_text is not None
    assert repr(version_text) in warning_text
    assert 'malformed or cannot be read' in warning_text


def test_check_reads_root() -> None:
    """Test Tcl/Tk checking reads the root patch level."""
    warning_text = check_tcltk_version(_make_root(FakeTcl('8.6.13')))
    assert warning_text is not None
    assert '8.6.13' in warning_text


def test_check_read_error() -> None:
    """Test Tcl/Tk checking warns when the version cannot be read."""
    root = _make_root(FakeTcl('', 'no patchlevel'))
    warning_text = check_tcltk_version(root)
    assert warning_text is not None
    assert 'no patchlevel' in warning_text
    assert 'malformed or cannot be read' in warning_text
