#! /usr/local/bin/python3
"""Tests for the backlog save helper."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from datetime import date
from typing import Callable, Optional, Sequence, TextIO, cast
import pytest
from backlogops import (
    AvailableTeams, BacklogReleases, DependencyMode, NoTextIO)
from backlogops_gui import backlog_window
from backlogops_gui.backlog_window import (
    extract_keys, order_by_deps, order_by_keys, estimate_date, save_backlog,
    set_plan)
from backlogops_gui.io_dialogs import DepOptions, StartChoice, WriteOptions

DATA = BacklogReleases(backlog=[], releases=[])
SINK = NoTextIO()
PARENT = cast(tk.Misc, object())
TEAMS = cast(AvailableTeams, object())


class _FakeData:
    """Records the backlog operations the actions invoke."""

    def __init__(self, error: Optional[Exception] = None) -> None:
        """Start the call log and store an optional error to raise."""
        self.backlog: list[object] = []
        self.calls: list[str] = []
        self._error = error

    def _record(self, name: str) -> None:
        """Record one call, raising the stored error when present."""
        self.calls.append(name)
        if self._error is not None:
            raise self._error

    def move_keys_first(self, keys: Sequence[str], _sink: TextIO) -> None:
        """Record a move-keys-first call."""
        self._record(f'keys:{list(keys)}')

    def order_by_dependencies(self, *, later: bool, mode: DependencyMode,
                              space_around: Optional[list[str]],
                              **_kw: object) -> None:
        """Record an order-by-dependencies call."""
        self._record(f'deps:{later}:{mode.name}:{space_around}')

    def estimate_ready_date(self, _teams: object, start_date: Optional[date],
                            _sink: TextIO) -> None:
        """Record an estimate-ready-date call."""
        self._record(f'estimate:{start_date}')

    def set_plan_from_estimate(self, _sink: TextIO) -> None:
        """Record a set-plan-from-estimate call."""
        self._record('plan')


def _refresher(store: list[bool]) -> Callable[[], None]:
    """Return a refresh callback recording that it ran."""
    def refresh() -> None:
        store.append(True)
    return refresh


def _as_data(fake: _FakeData) -> BacklogReleases:
    """Return the recording stub typed as a backlog for the actions."""
    return cast(BacklogReleases, fake)


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


def _key_writer(store: list[tuple[list[str], str]]) -> Callable[..., None]:
    """Return a key-list write stub recording the keys and path."""
    def write(keys: Sequence[str], path: str, **_kw: object) -> None:
        store.append((list(keys), path))
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


def test_order_keys_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test confirmed keys reorder the backlog and refresh the view."""
    monkeypatch.setattr(backlog_window, 'ask_keys', lambda _p, _s: ['A', 'B'])
    done: list[bool] = []
    data = _FakeData()
    infos: list[tuple[str, str]] = []
    order_by_keys(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
                  _record(infos))
    assert data.calls == ["keys:['A', 'B']"]
    assert done == [True]
    assert infos == [('Ordered backlog', 'Moved the keys to the front.')]


def test_order_keys_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the key dialog changes and refreshes nothing."""
    monkeypatch.setattr(backlog_window, 'ask_keys', lambda _p, _s: None)
    done: list[bool] = []
    data = _FakeData()
    infos: list[tuple[str, str]] = []
    order_by_keys(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
                  _record(infos))
    assert not data.calls
    assert not done
    assert not infos


def test_order_keys_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a reorder failure is reported and skips the refresh."""
    monkeypatch.setattr(backlog_window, 'ask_keys', lambda _p, _s: ['X'])
    done: list[bool] = []
    data = _FakeData(KeyError('X'))
    errors: list[tuple[str, str]] = []
    infos: list[tuple[str, str]] = []
    order_by_keys(PARENT, _as_data(data), SINK, _refresher(done),
                  _record(errors), _record(infos))
    assert errors == [('Could not order by keys', "'X'")]
    assert not done
    assert not infos


def test_order_deps_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test confirmed options order by dependencies and refresh."""
    options = DepOptions(False, DependencyMode.KEEP, None)
    monkeypatch.setattr(backlog_window, 'ask_dep_options', lambda _p: options)
    done: list[bool] = []
    data = _FakeData()
    infos: list[tuple[str, str]] = []
    order_by_deps(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
                  _record(infos))
    assert data.calls == ['deps:False:KEEP:None']
    assert done == [True]
    assert infos == [('Ordered backlog',
                      'Ordered the backlog by dependencies.')]


def test_order_deps_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the dependency options changes nothing."""
    monkeypatch.setattr(backlog_window, 'ask_dep_options', lambda _p: None)
    done: list[bool] = []
    data = _FakeData()
    infos: list[tuple[str, str]] = []
    order_by_deps(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
                  _record(infos))
    assert not data.calls
    assert not done
    assert not infos


def test_estimate_no_teams() -> None:
    """Test estimating without a configuration reports an error."""
    done: list[bool] = []
    data = _FakeData()
    errors: list[tuple[str, str]] = []
    estimate_date(PARENT, _as_data(data), None, SINK, _refresher(done),
                  _record(errors), _record([]))
    assert errors == [('No configuration',
                       'There is no teams configuration to estimate from.')]
    assert not data.calls
    assert not done


def test_estimate_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a confirmed start date estimates dates and refreshes."""
    choice = StartChoice(date(2026, 6, 15))
    monkeypatch.setattr(backlog_window, 'ask_start_date', lambda _p: choice)
    done: list[bool] = []
    data = _FakeData()
    infos: list[tuple[str, str]] = []
    estimate_date(PARENT, _as_data(data), TEAMS, SINK, _refresher(done),
                  _record([]), _record(infos))
    assert data.calls == ['estimate:2026-06-15']
    assert done == [True]
    assert infos == [('Estimated ready date',
                      'Filled in the estimated ready dates.')]


def test_estimate_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the start date dialog changes nothing."""
    monkeypatch.setattr(backlog_window, 'ask_start_date', lambda _p: None)
    done: list[bool] = []
    data = _FakeData()
    infos: list[tuple[str, str]] = []
    estimate_date(PARENT, _as_data(data), TEAMS, SINK, _refresher(done),
                  _record([]), _record(infos))
    assert not data.calls
    assert not done
    assert not infos


def test_set_plan_success() -> None:
    """Test setting the planned date copies dates and refreshes."""
    done: list[bool] = []
    data = _FakeData()
    infos: list[tuple[str, str]] = []
    set_plan(_as_data(data), SINK, _refresher(done), _record([]),
             _record(infos))
    assert data.calls == ['plan']
    assert done == [True]
    assert infos == [('Set planned date',
                      'Copied the estimated dates to the planned dates.')]


def test_set_plan_error() -> None:
    """Test a set-planned-date failure is reported and skips refresh."""
    done: list[bool] = []
    data = _FakeData(ValueError('no estimate'))
    errors: list[tuple[str, str]] = []
    infos: list[tuple[str, str]] = []
    set_plan(_as_data(data), SINK, _refresher(done), _record(errors),
             _record(infos))
    assert errors == [('Could not set planned date', 'no estimate')]
    assert not done
    assert not infos


def test_extract_keys_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test chosen levels and a file write the keys and report it."""
    monkeypatch.setattr(backlog_window, 'ask_levels', lambda _p: [1])
    monkeypatch.setattr(backlog_window, 'choose_key_list_output',
                        lambda _p: 'keys.txt')
    written: list[tuple[list[str], str]] = []
    monkeypatch.setattr(backlog_window, 'write_key_list', _key_writer(written))
    infos: list[tuple[str, str]] = []
    extract_keys(PARENT, DATA, SINK, _record([]), _record(infos))
    assert written == [([], 'keys.txt')]
    assert infos == [('Wrote keys', 'Wrote keys.txt')]


def test_extract_no_levels(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the level selection writes nothing."""
    monkeypatch.setattr(backlog_window, 'ask_levels', lambda _p: None)
    monkeypatch.setattr(backlog_window, 'write_key_list', _no_write)
    infos: list[tuple[str, str]] = []
    extract_keys(PARENT, DATA, SINK, _record([]), _record(infos))
    assert not infos


def test_extract_no_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the file chooser writes nothing."""
    monkeypatch.setattr(backlog_window, 'ask_levels', lambda _p: [1])
    monkeypatch.setattr(backlog_window, 'choose_key_list_output',
                        lambda _p: None)
    monkeypatch.setattr(backlog_window, 'write_key_list', _no_write)
    infos: list[tuple[str, str]] = []
    extract_keys(PARENT, DATA, SINK, _record([]), _record(infos))
    assert not infos
