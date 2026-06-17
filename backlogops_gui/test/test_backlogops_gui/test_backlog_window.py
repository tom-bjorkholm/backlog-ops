#! /usr/local/bin/python3
"""Tests for the backlog window action and save helpers."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from datetime import date, timedelta
from typing import Callable, Optional, Sequence, TextIO, cast
import pytest
from backlogops import (
    AvailableTeams, BacklogReleases, DependencyMode, NoTextIO,
    get_demo_backlog)
from backlogops_gui import backlog_window
from backlogops_gui.backlog_window import (
    BacklogWindow, adjust_content, estimate_date, extract_keys, order_by_deps,
    order_by_keys, plan_dates, save_backlog, save_changes, set_plan,
    show_changes)
from backlogops_gui.io_dialogs import (
    DepOptions, StartChoice, WriteOptions, show_change_list)


class _MsgRecorder:
    """Record the message-box calls made over a backlog window."""

    def __init__(self) -> None:
        """Start with an empty record of calls."""
        self.calls: list[tuple[str, str]] = []

    def showerror(self, title: str, message: str, parent: object) -> None:
        """Record a shown error message."""
        assert parent is not None
        self.calls.append((title, message))

    def showinfo(self, title: str, message: str, parent: object) -> None:
        """Record a shown informational message."""
        assert parent is not None
        self.calls.append((title, message))


def _key_write_fail(keys: object, path: object, **_kw: object) -> None:
    """Raise as if writing a key list failed."""
    raise OSError('disk full')


def _log_call(label: str, store: list[str]) -> Callable[..., None]:
    """Return a stub that records the label whenever it is invoked."""
    def call(*_args: object, **_kw: object) -> None:
        store.append(label)
    return call


def _none() -> None:
    """Return None, standing in for a presets or teams provider."""
    return None


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

    def estimate_ready_date(self, _teams: object, start_date: object,
                            _sink: TextIO) -> list[object]:
        """Record an estimate-ready-date call and return no changes."""
        self._record(f'estimate:{start_date}')
        return []

    def set_plan_from_estimate(self, _sink: TextIO) -> None:
        """Record a set-plan-from-estimate call."""
        self._record('plan')

    def adjust_release_content(self, buffer: timedelta,
                               _sink: TextIO) -> list[object]:
        """Record an adjust-release-content call and return no changes."""
        self._record(f'adjust:{buffer.days}')
        return []

    def release_plan_on_estimate(self, buffer: timedelta,
                                 _sink: TextIO) -> list[object]:
        """Record a release-plan-on-estimate call and return no changes."""
        self._record(f'plandates:{buffer.days}')
        return []


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


def _path_writer(store: list[str]) -> Callable[[str], None]:
    """Return a change-write stub recording the destination path."""
    def write(path: str) -> None:
        store.append(path)
    return write


def _key_writer(store: list[tuple[list[str], str]]) -> Callable[..., None]:
    """Return a key-list write stub recording the keys and path."""
    def write(keys: Sequence[str], path: str, **_kw: object) -> None:
        store.append((list(keys), path))
    return write


def _changes_recorder(store: list[tuple[str, str, object]]
                      ) -> Callable[..., None]:
    """Return a show-changes stub recording its title, text and writer."""
    def show(_parent: object, title: str, text: str, write_changes: object,
             _on_error: object, _on_info: object) -> None:
        store.append((title, text, write_changes))
    return show


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


def test_save_cancel_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the write-options dialog writes nothing."""
    monkeypatch.setattr(backlog_window, 'choose_output_file', _out_csv)
    monkeypatch.setattr(backlog_window, 'ask_write_options', _no_options)
    monkeypatch.setattr(backlog_window, 'write_backlog', _no_write)
    infos: list[tuple[str, str]] = []
    save_backlog(_parent(), DATA, None, SINK, _record([]), _record(infos))
    assert not infos


def test_order_keys_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the keys dialog leaves the backlog unchanged."""
    monkeypatch.setattr(backlog_window, 'ask_keys', lambda _p, _s: None)
    done: list[bool] = []
    data = _FakeData()
    order_by_keys(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
                  _record([]))
    assert not data.calls and not done


def test_order_deps_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the dependency options changes nothing."""
    monkeypatch.setattr(backlog_window, 'ask_dep_options', lambda _p: None)
    done: list[bool] = []
    data = _FakeData()
    order_by_deps(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
                  _record([]))
    assert not data.calls and not done


def test_plan_dates_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the buffer dialog leaves planned dates unchanged."""
    monkeypatch.setattr(backlog_window, 'ask_buffer_days', lambda _p: None)
    done: list[bool] = []
    data = _FakeData()
    plan_dates(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
               _record([]))
    assert not data.calls and not done


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


def test_order_keys_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a reorder failure is reported and skips the refresh."""
    monkeypatch.setattr(backlog_window, 'ask_keys', lambda _p, _s: ['X'])
    done: list[bool] = []
    data = _FakeData(KeyError('X'))
    errors: list[tuple[str, str]] = []
    order_by_keys(PARENT, _as_data(data), SINK, _refresher(done),
                  _record(errors), _record([]))
    assert errors == [('Could not order by keys', "'X'")]
    assert not done


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
    """Test a confirmed start date estimates and shows the changes."""
    choice = StartChoice(date(2026, 6, 15))
    monkeypatch.setattr(backlog_window, 'ask_start_date', lambda _p: choice)
    shown: list[tuple[str, str, object]] = []
    monkeypatch.setattr(backlog_window, 'show_changes',
                        _changes_recorder(shown))
    done: list[bool] = []
    data = _FakeData()
    estimate_date(PARENT, _as_data(data), TEAMS, SINK, _refresher(done),
                  _record([]), _record([]))
    assert data.calls == ['estimate:2026-06-15']
    assert done == [True]
    assert shown == [('Release date changes', 'No release date changes.',
                      None)]


def test_estimate_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the start date dialog changes nothing."""
    monkeypatch.setattr(backlog_window, 'ask_start_date', lambda _p: None)
    monkeypatch.setattr(backlog_window, 'show_changes', _no_write)
    done: list[bool] = []
    data = _FakeData()
    estimate_date(PARENT, _as_data(data), TEAMS, SINK, _refresher(done),
                  _record([]), _record([]))
    assert not data.calls
    assert not done


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


def test_adjust_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a confirmed buffer adjusts content and shows the changes."""
    monkeypatch.setattr(backlog_window, 'ask_buffer_days', lambda _p: 7)
    shown: list[tuple[str, str, object]] = []
    monkeypatch.setattr(backlog_window, 'show_changes',
                        _changes_recorder(shown))
    done: list[bool] = []
    data = _FakeData()
    adjust_content(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
                   _record([]))
    assert data.calls == ['adjust:7']
    assert done == [True]
    assert shown == [('Release content changes',
                      'No release content changes.', None)]


def test_adjust_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the buffer dialog changes nothing."""
    monkeypatch.setattr(backlog_window, 'ask_buffer_days', lambda _p: None)
    monkeypatch.setattr(backlog_window, 'show_changes', _no_write)
    done: list[bool] = []
    data = _FakeData()
    adjust_content(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
                   _record([]))
    assert not data.calls
    assert not done


def test_adjust_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an adjust failure is reported and shows no changes."""
    monkeypatch.setattr(backlog_window, 'ask_buffer_days', lambda _p: 5)
    monkeypatch.setattr(backlog_window, 'show_changes', _no_write)
    done: list[bool] = []
    data = _FakeData(ValueError('bad'))
    errors: list[tuple[str, str]] = []
    adjust_content(PARENT, _as_data(data), SINK, _refresher(done),
                   _record(errors), _record([]))
    assert errors == [('Could not adjust release content', 'bad')]
    assert not done


def test_plan_dates_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a confirmed buffer sets planned dates and shows changes."""
    monkeypatch.setattr(backlog_window, 'ask_buffer_days', lambda _p: 3)
    shown: list[tuple[str, str, object]] = []
    monkeypatch.setattr(backlog_window, 'show_changes',
                        _changes_recorder(shown))
    done: list[bool] = []
    data = _FakeData()
    plan_dates(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
               _record([]))
    assert data.calls == ['plandates:3']
    assert done == [True]
    assert shown == [('Release date changes', 'No release date changes.',
                      None)]


def _saver(_parent: object) -> str:
    """Return a changes file name as if the chooser was confirmed."""
    return 'changes.csv'


def test_save_changes_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a confirmed changes save writes the file and reports it."""
    monkeypatch.setattr(backlog_window, 'choose_changes_output', _saver)
    written: list[str] = []
    infos: list[tuple[str, str]] = []
    save_changes(_parent(), _path_writer(written), _record([]), _record(infos))
    assert written == ['changes.csv']
    assert infos == [('Wrote file', 'Wrote changes.csv')]


def test_save_changes_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test saving with no changes reports that nothing is written."""
    monkeypatch.setattr(backlog_window, 'choose_changes_output', _no_write)
    infos: list[tuple[str, str]] = []
    save_changes(_parent(), None, _record([]), _record(infos))
    assert infos == [('No changes', 'There are no changes to write.')]


def test_save_changes_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the changes file chooser writes nothing."""
    monkeypatch.setattr(backlog_window, 'choose_changes_output', _no_file)
    infos: list[tuple[str, str]] = []
    save_changes(_parent(), _no_write, _record([]), _record(infos))
    assert not infos


def test_save_changes_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a changes write failure is reported through on_error."""
    monkeypatch.setattr(backlog_window, 'choose_changes_output', _saver)
    errors: list[tuple[str, str]] = []
    save_changes(_parent(), _write_fail, _record(errors), _record([]))
    assert errors == [('Could not write file', 'disk full')]


def test_show_changes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test show_changes hands the title and text to the list pop-up."""
    shown: list[tuple[str, str]] = []

    def fake_list(_parent: object, title: str, text: str,
                  _on_save: object) -> object:
        shown.append((title, text))
        return object()
    monkeypatch.setattr(backlog_window, 'show_change_list', fake_list)
    show_changes(_parent(), 'Title', 'Body', None, _record([]), _record([]))
    assert shown == [('Title', 'Body')]


def _root() -> tk.Tk:
    """Return a Tk root, or skip the test when no display is available."""
    try:
        return tk.Tk()
    except tk.TclError:
        pytest.skip('no display available')


def test_change_list_build() -> None:
    """Test the change list pop-up builds and can be dismissed."""
    root = _root()
    try:
        window = show_change_list(root, 'Changes', 'a: R1 -> R2', lambda: None)
        assert isinstance(window, tk.Toplevel)
        assert window.title() == 'Changes'
        window.destroy()
    finally:
        root.destroy()


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


def test_extract_cancel_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the output file selection writes nothing."""
    monkeypatch.setattr(backlog_window, 'ask_levels', lambda _p: [1])
    monkeypatch.setattr(backlog_window, 'choose_key_list_output',
                        lambda _p: None)
    monkeypatch.setattr(backlog_window, 'write_key_list', _no_write)
    infos: list[tuple[str, str]] = []
    extract_keys(PARENT, DATA, SINK, _record([]), _record(infos))
    assert not infos


def test_extract_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a key-list write failure is reported through on_error."""
    monkeypatch.setattr(backlog_window, 'ask_levels', lambda _p: [1])
    monkeypatch.setattr(backlog_window, 'choose_key_list_output',
                        lambda _p: 'keys.txt')
    monkeypatch.setattr(backlog_window, 'write_key_list', _key_write_fail)
    errors: list[tuple[str, str]] = []
    extract_keys(PARENT, DATA, SINK, _record(errors), _record([]))
    assert errors == [('Could not extract keys', 'disk full')]


_ACTION_METHODS = [
    '_save', '_order_by_keys', '_order_by_deps', '_estimate_date',
    '_set_plan', '_adjust_content', '_plan_dates', '_extract_keys']
"""The window action methods that delegate to a module helper."""

_DELEGATES = [
    'save_backlog', 'order_by_keys', 'order_by_deps', 'estimate_date',
    'set_plan', 'adjust_content', 'plan_dates', 'extract_keys']
"""The module helpers each action method delegates to, in the same order."""


def test_window_acts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the window builds its tables and delegates each menu action."""
    root = _root()
    try:
        calls: list[str] = []
        for name in _DELEGATES:
            monkeypatch.setattr(backlog_window, name, _log_call(name, calls))
        recorder = _MsgRecorder()
        monkeypatch.setattr(backlog_window, 'messagebox', recorder)
        data = get_demo_backlog()
        window = BacklogWindow(root, data, 'Title', _none, _none, SINK)
        window._refresh_tables()
        window._report_error('E', 'err')
        window._report_info('I', 'info')
        for method in _ACTION_METHODS:
            getattr(window, method)()
        assert sorted(calls) == sorted(_DELEGATES)
        assert recorder.calls == [('E', 'err'), ('I', 'info')]
    finally:
        root.destroy()
