#! /usr/local/bin/python3
"""Tests for the backlog window action and save helpers."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from datetime import date, timedelta
from pathlib import Path
from typing import Callable, Optional, Sequence, TextIO, cast
import pytest
from backlogops import (
    AddedToJira, AvailableTeams, BacklogItem, BacklogReleases, DependencyMode,
    GuiDisplayConfig, NoTextIO, Release, ReleaseChange, ReleaseDateChange,
    Status, get_demo_backlog)
from backlogops_gui import backlog_window
from backlogops_gui.backlog_window import (
    BacklogWindow, adjust_content, apply_add_result, estimate_date,
    extract_keys, order_by_deps, order_by_keys, order_by_release, order_dates,
    plan_dates, save_backlog, save_changes, set_plan, show_changes)
from backlogops_gui.backlog_window import _content_report, _date_report
from backlogops_gui.io_dialogs import (
    DepOptions, ReleaseOrderOptions, StartChoice, WriteOptions,
    show_change_list)
from .gui_test_helpers import MsgRecorder


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

    def backlog_in_release_order(self, *, honor_dependencies: bool = False,
                                 later: bool = False, **_kw: object) -> None:
        """Record a backlog-in-release-order call."""
        self._record(f'release:{honor_dependencies}:{later}')

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

    def order_releases_by_date(self, by_estimated: bool,
                               _sink: TextIO) -> None:
        """Record an order-releases-by-date call."""
        self._record(f'orderdates:{by_estimated}')


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


def _release_item(key: str, release: str,
                  deps: Optional[list[str]] = None) -> BacklogItem:
    """Return a minimal item for release-order action tests."""
    return BacklogItem(key=key, level=1, title=key, story_points=1,
                       status=Status.TODO, release=release,
                       depends_on_f2s=deps or [])


def _keys(data: BacklogReleases) -> list[str]:
    """Return the backlog keys from a backlog-and-releases object."""
    return [item.key for item in data.backlog]


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
    save_backlog(_parent(), DATA, None, None, SINK, _record(errors),
                 _record(infos))
    assert written == ['out.csv']
    assert infos == [('Wrote file', 'Wrote out.csv')]
    assert not errors


def test_save_cancel_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the file selection writes nothing."""
    monkeypatch.setattr(backlog_window, 'choose_output_file', _no_file)
    monkeypatch.setattr(backlog_window, 'write_backlog', _no_write)
    infos: list[tuple[str, str]] = []
    save_backlog(_parent(), DATA, None, None, SINK, _record([]),
                 _record(infos))
    assert not infos


def test_save_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a write failure is reported through the error callback."""
    monkeypatch.setattr(backlog_window, 'choose_output_file', _out_csv)
    monkeypatch.setattr(backlog_window, 'ask_write_options', _ok_options)
    monkeypatch.setattr(backlog_window, 'write_backlog', _write_fail)
    errors: list[tuple[str, str]] = []
    infos: list[tuple[str, str]] = []
    save_backlog(_parent(), DATA, None, None, SINK, _record(errors),
                 _record(infos))
    assert errors == [('Could not write file', 'disk full')]
    assert not infos


def test_save_cancel_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the write-options dialog writes nothing."""
    monkeypatch.setattr(backlog_window, 'choose_output_file', _out_csv)
    monkeypatch.setattr(backlog_window, 'ask_write_options', _no_options)
    monkeypatch.setattr(backlog_window, 'write_backlog', _no_write)
    infos: list[tuple[str, str]] = []
    save_backlog(_parent(), DATA, None, None, SINK, _record([]),
                 _record(infos))
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


def test_order_release_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling release-order options changes nothing."""
    monkeypatch.setattr(backlog_window, 'ask_release_order', lambda _p: None)
    done: list[bool] = []
    data = _FakeData()
    order_by_release(PARENT, _as_data(data), SINK, _refresher(done),
                     _record([]), _record([]))
    assert not data.calls and not done


def _release_opts(honor: bool, later: bool
                  ) -> Callable[[object], ReleaseOrderOptions]:
    """Return a stub that yields the given release-order options."""
    options = ReleaseOrderOptions(honor_dependencies=honor, later=later)
    return lambda _p: options


def test_order_release_plain(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test plain release ordering is passed on and reported."""
    monkeypatch.setattr(backlog_window, 'ask_release_order',
                        _release_opts(False, False))
    done: list[bool] = []
    data = _FakeData()
    infos: list[tuple[str, str]] = []
    order_by_release(PARENT, _as_data(data), SINK, _refresher(done),
                     _record([]), _record(infos))
    assert data.calls == ['release:False:False']
    assert done == [True]
    assert infos == [
        ('Ordered backlog',
         'Ordered the backlog by release order without honoring '
         'dependencies.')]


def test_order_release_honor(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test honoring deps pulls a prerequisite to an earlier release."""
    monkeypatch.setattr(backlog_window, 'ask_release_order',
                        _release_opts(True, False))
    backlog = [_release_item('dep', 'R1', ['pre']),
               _release_item('pre', 'R2'), _release_item('other', 'R1')]
    data = BacklogReleases(backlog, [Release('R1'), Release('R2')])
    done: list[bool] = []
    infos: list[tuple[str, str]] = []
    order_by_release(PARENT, data, SINK, _refresher(done), _record([]),
                     _record(infos))
    assert _keys(data) == ['pre', 'dep', 'other']
    assert done == [True]
    assert infos == [
        ('Ordered backlog',
         'Ordered the backlog by release order, honoring dependencies '
         'by pulling prerequisites earlier.')]


def test_order_release_later(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the later option pushes the dependent to a later release."""
    monkeypatch.setattr(backlog_window, 'ask_release_order',
                        _release_opts(True, True))
    backlog = [_release_item('dep', 'R1', ['pre']),
               _release_item('pre', 'R2'), _release_item('other', 'R1')]
    data = BacklogReleases(backlog, [Release('R1'), Release('R2')])
    done: list[bool] = []
    infos: list[tuple[str, str]] = []
    order_by_release(PARENT, data, SINK, _refresher(done), _record([]),
                     _record(infos))
    assert _keys(data) == ['other', 'pre', 'dep']
    assert done == [True]
    assert infos == [
        ('Ordered backlog',
         'Ordered the backlog by release order, honoring dependencies '
         'by pushing dependents later.')]


def test_order_release_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a release-order failure is reported and skips the refresh."""
    monkeypatch.setattr(backlog_window, 'ask_release_order',
                        _release_opts(True, False))
    done: list[bool] = []
    data = _FakeData(ValueError('bad release'))
    errors: list[tuple[str, str]] = []
    order_by_release(PARENT, _as_data(data), SINK, _refresher(done),
                     _record(errors), _record([]))
    assert errors == [('Could not order by release order', 'bad release')]
    assert not done


def test_order_dates_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the date order dialog changes nothing."""
    monkeypatch.setattr(backlog_window, 'ask_date_order', lambda _p: None)
    done: list[bool] = []
    data = _FakeData()
    order_dates(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
                _record([]))
    assert not data.calls and not done


def test_order_dates_planned(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the planned-date choice orders the releases and refreshes."""
    monkeypatch.setattr(backlog_window, 'ask_date_order', lambda _p: False)
    done: list[bool] = []
    data = _FakeData()
    infos: list[tuple[str, str]] = []
    order_dates(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
                _record(infos))
    assert data.calls == ['orderdates:False']
    assert done == [True]
    assert infos == [('Ordered releases',
                      'Ordered the releases by planned date.')]


def test_order_dates_est(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the estimated-date choice is passed on and reported."""
    monkeypatch.setattr(backlog_window, 'ask_date_order', lambda _p: True)
    done: list[bool] = []
    data = _FakeData()
    infos: list[tuple[str, str]] = []
    order_dates(PARENT, _as_data(data), SINK, _refresher(done), _record([]),
                _record(infos))
    assert data.calls == ['orderdates:True']
    assert infos == [('Ordered releases',
                      'Ordered the releases by estimated date.')]


def test_order_dates_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an ordering failure is reported and skips the refresh."""
    monkeypatch.setattr(backlog_window, 'ask_date_order', lambda _p: False)
    done: list[bool] = []
    data = _FakeData(TypeError('bad'))
    errors: list[tuple[str, str]] = []
    order_dates(PARENT, _as_data(data), SINK, _refresher(done),
                _record(errors), _record([]))
    assert errors == [('Could not order releases', 'bad')]
    assert not done


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


def test_date_writer(tmp_path: Path) -> None:
    """Test the date-change report yields a writer that writes the file.

    A non-empty change list returns a writer; calling it writes the
    listing to the chosen file, overwriting it as the save dialog has
    already confirmed.
    """
    changes = [ReleaseDateChange('R1', None, date(2026, 1, 15))]
    text, writer = _date_report(changes, SINK)
    assert 'R1' in text
    assert writer is not None
    target = tmp_path / 'd.csv'
    writer(str(target))
    assert target.exists()


def test_content_writer(tmp_path: Path) -> None:
    """Test the content-change report yields a writer that writes a file."""
    changes = [ReleaseChange('a', 'R1', 'R2')]
    text, writer = _content_report(changes, SINK)
    assert 'a' in text
    assert writer is not None
    target = tmp_path / 'c.csv'
    writer(str(target))
    assert target.exists()


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
        root = tk.Tk()
    except tk.TclError:
        pytest.skip('no display available')
    return root


def _menu_labels(window: BacklogWindow) -> list[str]:
    """Return the labels in the backlog menu of a backlog window."""
    menu = _backlog_menu(window)
    last = menu.index('end')
    assert last is not None
    labels: list[str] = []
    for index in range(last + 1):
        if menu.type(index) != 'separator':
            labels.append(menu.entrycget(index, 'label'))
    return labels


def _backlog_menu(window: BacklogWindow) -> tk.Menu:
    """Return the backlog menu of a backlog window."""
    # pylint: disable-next=protected-access
    menubar = window._win.nametowidget(window._win.cget('menu'))
    assert isinstance(menubar, tk.Menu)
    menu = menubar.nametowidget(menubar.entrycget(0, 'menu'))
    assert isinstance(menu, tk.Menu)
    return menu


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
    '_save', '_order_by_keys', '_order_by_deps', '_order_by_release',
    '_estimate_date', '_set_plan', '_adjust_content', '_plan_dates',
    '_order_dates', '_extract_keys']
"""The window action methods that delegate to a module helper."""

_DELEGATES = [
    'save_backlog', 'order_by_keys', 'order_by_deps', 'order_by_release',
    'estimate_date', 'set_plan', 'adjust_content', 'plan_dates',
    'order_dates', 'extract_keys']
"""The module helpers each action method delegates to, in the same order."""


def test_window_uses_gui_maps(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the window passes the GUI column maps to both tables."""
    root = _root()
    try:
        captured: dict[str, object] = {}

        def fake_backlog(_data: object, _levels: object, _display: object,
                         names: object, _sink: object
                         ) -> tuple[list[str], list[object]]:
            captured['backlog'] = names
            return ([], [])

        def fake_release(_data: object, names: object
                         ) -> tuple[list[str], list[object]]:
            captured['release'] = names
            return ([], [])
        monkeypatch.setattr(backlog_window, 'backlog_table', fake_backlog)
        monkeypatch.setattr(backlog_window, 'release_table', fake_release)
        gui = GuiDisplayConfig()
        gui.backlog_to_external = {'key': 'Id'}
        gui.release_to_external = {'name': 'Release'}
        BacklogWindow(root, DATA, 'T', _none, _none, SINK,
                      gui_display=lambda: gui)
        assert captured['backlog'] == {'key': 'Id'}
        assert captured['release'] == {'name': 'Release'}
    finally:
        root.destroy()


def test_window_acts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the window builds its tables and delegates each menu action."""
    root = _root()
    try:
        calls: list[str] = []
        for name in _DELEGATES:
            monkeypatch.setattr(backlog_window, name, _log_call(name, calls))
        recorder = MsgRecorder()
        monkeypatch.setattr(backlog_window, 'messagebox', recorder)
        data = get_demo_backlog()
        window = BacklogWindow(root, data, 'Title', _none, _none, SINK)
        assert 'Order by release order…' in _menu_labels(window)
        # pylint: disable-next=protected-access
        window._refresh_tables()
        # pylint: disable-next=protected-access
        window._report_error('E', 'err')
        # pylint: disable-next=protected-access
        window._report_info('I', 'info')
        for method in _ACTION_METHODS:
            getattr(window, method)()
        assert sorted(calls) == sorted(_DELEGATES)
        assert recorder.calls == [('E', 'err'), ('I', 'info')]
    finally:
        root.destroy()


def test_warning_disables_ops() -> None:
    """Test a warning window disables operations but still allows saving."""
    root = _root()
    try:
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK,
                               warning='Broken Jira data')
        menu = _backlog_menu(window)
        last = menu.index('end')
        assert last is not None
        states = {menu.entrycget(index, 'label'):
                  menu.entrycget(index, 'state')
                  for index in range(last + 1)
                  if menu.type(index) != 'separator'}
        assert states['Order by keys…'] == 'disabled'
        assert states['Estimate ready date…'] == 'disabled'
        assert states['Extract keys…'] == 'disabled'
        assert states['Save to file…'] == 'normal'
        # pylint: disable-next=protected-access
        labels = [w for w in window._win.winfo_children()
                  if isinstance(w, tk.Label)]
        assert labels and labels[0].cget('text') == 'Broken Jira data'
    finally:
        root.destroy()


def test_apply_add_result() -> None:
    """Test rekeying updates the shown backlog and reports the lists."""
    item = BacklogItem(key='A', level=1, title='First', story_points=5,
                       status=Status.TODO)
    data = BacklogReleases(backlog=[item], releases=[])
    added = BacklogItem(key='PROJ-1', level=1, title='First', story_points=5,
                        status=Status.TODO)
    result = AddedToJira(stored=[added], already_present=[],
                         key_map={'A': 'PROJ-1'})
    calls: list[str] = []
    reports: list[str] = []
    apply_add_result(data, result, lambda: calls.append('refresh'),
                     reports.append)
    assert data.backlog[0].key == 'PROJ-1'
    assert calls == ['refresh']
    assert 'Added to Jira' in reports[0]
