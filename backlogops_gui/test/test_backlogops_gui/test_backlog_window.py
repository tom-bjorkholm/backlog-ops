#! /usr/local/bin/python3
"""Tests for the backlog save helper."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable, cast
import pytest
from backlogops import BacklogReleases, NoTextIO
from backlogops_gui import backlog_window
from backlogops_gui.backlog_window import save_backlog
from backlogops_gui.io_dialogs import WriteOptions

DATA = BacklogReleases(backlog=[], releases=[])
SINK = NoTextIO()


def _parent() -> tk.Misc:
    """Return a dummy parent window for save-helper tests."""
    return cast(tk.Misc, object())


def _record(store: list[tuple[str, str]]) -> Callable[[str, str], None]:
    """Return a callback recording its title and message."""
    def recorder(title: str, message: str) -> None:
        store.append((title, message))
    return recorder


def _writer(store: list[str]) -> Callable[..., None]:
    """Return a write stub recording the destination path."""
    def write(_data: object, path: str, *_rest: object) -> None:
        store.append(path)
    return write


def _no_write(*_args: object) -> None:
    """Fail the test if a write is attempted."""
    raise AssertionError('write should not happen')


def _write_fail(*_args: object) -> None:
    """Raise as if writing the file failed."""
    raise OSError('disk full')


def _ok_options(_parent: object, _names: object) -> WriteOptions:
    """Return write options as if the dialog was confirmed."""
    return WriteOptions(None, False)


def _no_options(_parent: object, _names: object) -> None:
    """Return nothing as if the options dialog was cancelled."""
    return None


def _out_csv(_parent: object) -> str:
    """Return an output file name as if the chooser was confirmed."""
    return 'out.csv'


def _no_file(_parent: object) -> None:
    """Return nothing as if the file chooser was cancelled."""
    return None


def test_save_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a confirmed save writes the file and reports success."""
    monkeypatch.setattr(backlog_window, 'choose_output_file', _out_csv)
    monkeypatch.setattr(backlog_window, 'ask_write_options', _ok_options)
    written: list[str] = []
    monkeypatch.setattr(backlog_window, 'write_backlog', _writer(written))
    errors: list[tuple[str, str]] = []
    infos: list[tuple[str, str]] = []
    save_backlog(_parent(), DATA, None, SINK, _record(errors), _record(infos))
    assert written == ['out.csv']
    assert infos == [('Wrote file', 'Wrote out.csv')]
    assert not errors


def test_save_cancel_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the file selection writes nothing."""
    monkeypatch.setattr(backlog_window, 'choose_output_file', _no_file)
    monkeypatch.setattr(backlog_window, 'write_backlog', _no_write)
    infos: list[tuple[str, str]] = []
    save_backlog(_parent(), DATA, None, SINK, _record([]), _record(infos))
    assert not infos


def test_save_cancel_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the options dialog writes nothing."""
    monkeypatch.setattr(backlog_window, 'choose_output_file', _out_csv)
    monkeypatch.setattr(backlog_window, 'ask_write_options', _no_options)
    monkeypatch.setattr(backlog_window, 'write_backlog', _no_write)
    infos: list[tuple[str, str]] = []
    save_backlog(_parent(), DATA, None, SINK, _record([]), _record(infos))
    assert not infos


def test_save_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a write failure is reported through the error callback."""
    monkeypatch.setattr(backlog_window, 'choose_output_file', _out_csv)
    monkeypatch.setattr(backlog_window, 'ask_write_options', _ok_options)
    monkeypatch.setattr(backlog_window, 'write_backlog', _write_fail)
    errors: list[tuple[str, str]] = []
    infos: list[tuple[str, str]] = []
    save_backlog(_parent(), DATA, None, SINK, _record(errors), _record(infos))
    assert errors == [('Could not write file', 'disk full')]
    assert not infos
