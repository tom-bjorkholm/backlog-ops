#! /usr/local/bin/python3
"""Tests for the backlog window widget and its menu wiring."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Callable, Optional, cast
import pytest
from backlogops import (
    AddedToJira, BacklogReleases, GuiDisplayConfig, NoTextIO, get_demo_backlog)
from backlogops_gui import backlog_window
from backlogops_gui.backlog_window import (
    BacklogSource, BacklogWindow, JiraHandlers, MODIFIED_MARK)
from .gui_test_helpers import MsgRecorder, gui_root, press_close

DATA = BacklogReleases(backlog=[], releases=[])
SINK = NoTextIO()

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


def _log_call(label: str, store: list[str]) -> Callable[..., None]:
    """Return a stub that records the label whenever it is invoked."""
    def call(*_args: object, **_kw: object) -> None:
        store.append(label)
    return call


def _none() -> None:
    """Return None, standing in for a presets or teams provider."""
    return None


def _backlog_menu(window: BacklogWindow) -> tk.Menu:
    """Return the backlog menu of a backlog window."""
    # pylint: disable-next=protected-access
    menubar = window._win.nametowidget(window._win.cget('menu'))
    assert isinstance(menubar, tk.Menu)
    menu = menubar.nametowidget(menubar.entrycget(0, 'menu'))
    assert isinstance(menu, tk.Menu)
    return menu


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


def _jira_menu_labels(window: BacklogWindow) -> list[str]:
    """Return the labels in the Jira menu of a backlog window."""
    # pylint: disable-next=protected-access
    menubar = window._win.nametowidget(window._win.cget('menu'))
    assert isinstance(menubar, tk.Menu)
    menu = menubar.nametowidget(menubar.entrycget(1, 'menu'))
    assert isinstance(menu, tk.Menu)
    last = menu.index('end')
    assert last is not None
    return [menu.entrycget(index, 'label') for index in range(last + 1)
            if menu.type(index) != 'separator']


def _bl_update_recorder(store: list[object]) -> Callable[..., None]:
    """Return an update-backlog handler recording the data it is given."""
    def handler(data: object, _on_done: object) -> None:
        store.append(data)
    return handler


def _rank_recorder(store: list[object]) -> Callable[..., None]:
    """Return a rank handler recording that it was invoked."""
    def handler(on_done: object) -> None:
        store.append(on_done)
    return handler


def test_window_uses_gui_maps(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the window passes the GUI column maps to both tables."""
    with gui_root() as root:
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


def test_window_acts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the window builds its tables and delegates each menu action."""
    with gui_root() as root:
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


def test_warning_disables_ops() -> None:
    """Test a warning window disables operations but still allows saving."""
    with gui_root() as root:
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


def test_backlog_update_menu() -> None:
    """Test the update-backlog menu item is present and delegates."""
    with gui_root() as root:
        got: list[object] = []
        handlers = JiraHandlers(update_backlog=_bl_update_recorder(got))
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK,
                               jira=handlers)
        assert 'Update backlog in Jira…' in _jira_menu_labels(window)
        # pylint: disable-next=protected-access
        window._backlog_update()
        assert got and got[0] is DATA


def test_tables_have_hscroll() -> None:
    """Test each table wires a Treeview to an auto-hiding x-scrollbar."""
    with gui_root() as root:
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK)
        # pylint: disable-next=protected-access
        frames = [w for w in window._win.winfo_children()
                  if isinstance(w, tk.LabelFrame)]
        assert frames
        for frame in frames:
            kids = frame.winfo_children()
            trees = [w for w in kids if isinstance(w, ttk.Treeview)]
            hbars = [w for w in kids if isinstance(w, ttk.Scrollbar)
                     and str(w.cget('orient')) == 'horizontal']
            assert len(trees) == 1 and len(hbars) == 1
            assert trees[0].cget('xscrollcommand') != ''


def test_rank_menu() -> None:
    """Test the rank-items menu item is present and delegates."""
    with gui_root() as root:
        got: list[object] = []
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK,
                               jira=JiraHandlers(rank=_rank_recorder(got)))
        assert 'Rank items in Jira…' in _jira_menu_labels(window)
        # pylint: disable-next=protected-access
        window._rank_jira()
        assert len(got) == 1


def test_order_menu() -> None:
    """Test the order-releases menu item is present and delegates."""
    with gui_root() as root:
        got: list[object] = []
        handlers = JiraHandlers(order_releases=_bl_update_recorder(got))
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK,
                               jira=handlers)
        assert 'Order releases in Jira…' in _jira_menu_labels(window)
        # pylint: disable-next=protected-access
        window._releases_order()
        assert got and got[0] is DATA


def test_rename_menu() -> None:
    """Test the rename-releases menu item is present and delegates."""
    with gui_root() as root:
        got: list[object] = []
        handlers = JiraHandlers(rename_releases=_bl_update_recorder(got))
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK,
                               jira=handlers)
        assert 'Rename releases in Jira…' in _jira_menu_labels(window)
        # pylint: disable-next=protected-access
        window._releases_rename()
        assert got and got[0] is DATA


def test_rank_absent() -> None:
    """Test the rank-items item is disabled without a handler."""
    with gui_root() as root:
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK)
        # pylint: disable-next=protected-access
        menubar = window._win.nametowidget(window._win.cget('menu'))
        menu = menubar.nametowidget(menubar.entrycget(1, 'menu'))
        last = menu.index('end')
        assert last is not None
        states = {menu.entrycget(index, 'label'):
                  menu.entrycget(index, 'state')
                  for index in range(last + 1)
                  if menu.type(index) != 'separator'}
        assert states['Rank items in Jira…'] == 'disabled'


@pytest.mark.focus_sensitive
def test_cmd_w_closes() -> None:
    """Test Cmd-W closes a backlog window."""
    with gui_root() as root:
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK)
        # pylint: disable-next=protected-access
        press_close(window._win)
        # pylint: disable-next=protected-access
        assert not window._win.winfo_exists()


def test_close_accelerator() -> None:
    """Test the Close menu item shows the Cmd-W accelerator."""
    with gui_root() as root:
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK)
        menu = _backlog_menu(window)
        last = menu.index('end')
        assert last is not None
        accels = {menu.entrycget(index, 'label'):
                  menu.entrycget(index, 'accelerator')
                  for index in range(last + 1)
                  if menu.type(index) != 'separator'}
        assert accels['Close'] == 'Command-W'


def test_bl_update_absent() -> None:
    """Test the update-backlog item is disabled without a handler."""
    with gui_root() as root:
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK)
        # pylint: disable-next=protected-access
        menubar = window._win.nametowidget(window._win.cget('menu'))
        menu = menubar.nametowidget(menubar.entrycget(1, 'menu'))
        last = menu.index('end')
        assert last is not None
        states = {menu.entrycget(index, 'label'):
                  menu.entrycget(index, 'state')
                  for index in range(last + 1)
                  if menu.type(index) != 'separator'}
        assert states['Update backlog in Jira…'] == 'disabled'


def test_jira_add_menu() -> None:
    """Test the add-to-Jira action delegates to its handler."""
    with gui_root() as root:
        got: list[object] = []
        handlers = JiraHandlers(add_backlog=_bl_update_recorder(got))
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK,
                               jira=handlers)
        # pylint: disable-next=protected-access
        window._jira_add()
        assert got and got[0] is DATA


def test_releases_add_menu() -> None:
    """Test the add-releases action delegates to its handler."""
    with gui_root() as root:
        got: list[object] = []
        handlers = JiraHandlers(add_releases=_bl_update_recorder(got))
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK,
                               jira=handlers)
        # pylint: disable-next=protected-access
        window._releases_add()
        assert got and got[0] is DATA


def test_releases_update_menu() -> None:
    """Test the update-releases action delegates to its handler."""
    with gui_root() as root:
        got: list[object] = []
        handlers = JiraHandlers(update_releases=_bl_update_recorder(got))
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK,
                               jira=handlers)
        # pylint: disable-next=protected-access
        window._releases_update()
        assert got and got[0] is DATA


_JIRA_ACTIONS = ['_jira_add', '_releases_add', '_releases_update',
                 '_backlog_update', '_rank_jira', '_releases_order',
                 '_releases_rename']
"""The Jira action methods, each a no-op without its handler."""

_JIRA_CALLBACKS = ['_on_jira_added', '_on_releases_added',
                   '_on_releases_updated', '_on_backlog_updated',
                   '_on_ranked', '_on_releases_ordered',
                   '_on_releases_renamed']
"""The Jira result callbacks, each reporting through a text pop-up."""


def test_jira_no_handlers() -> None:
    """Test each Jira action is a safe no-op without its handler."""
    with gui_root() as root:
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK)
        for name in _JIRA_ACTIONS:
            getattr(window, name)()


def test_result_callbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test each Jira result callback reports through a text pop-up."""
    titles: list[str] = []

    def report(_win: object, title: str, _text: object) -> None:
        titles.append(title)

    def apply_result(_data: object, _result: object, _refresh: object,
                     show: Callable[[str], None]) -> None:
        show('t')
    monkeypatch.setattr(backlog_window, 'show_text_report', report)
    monkeypatch.setattr(backlog_window, 'apply_add_result', apply_result)
    monkeypatch.setattr(backlog_window, 'apply_update_result', apply_result)
    for name in ('format_release_result', 'format_release_updates',
                 'format_rank_result', 'format_order_result',
                 'format_rename_result'):
        monkeypatch.setattr(backlog_window, name, lambda result: 'txt')
    with gui_root() as root:
        window = BacklogWindow(root, DATA, 'Title', _none, _none, SINK)
        for name in _JIRA_CALLBACKS:
            getattr(window, name)(object())
    assert len(titles) == 7


T0 = datetime(2026, 7, 18, 14, 30, 45)
T1 = datetime(2026, 7, 18, 15, 0, 0)


def _win_of(window: BacklogWindow) -> tk.Misc:
    """Return the toplevel window of a backlog window."""
    # pylint: disable-next=protected-access
    return window._win


def _time_of(window: BacklogWindow) -> str:
    """Return the info-region time line of a backlog window."""
    # pylint: disable-next=protected-access
    var = window._time_var
    assert var is not None
    return var.get()


def _mark_of(window: BacklogWindow) -> str:
    """Return the info-region modified marker of a backlog window."""
    # pylint: disable-next=protected-access
    var = window._mark_var
    assert var is not None
    return var.get()


def _label_texts(win: tk.Misc) -> list[str]:
    """Return the text of every label in a window subtree."""
    texts: list[str] = []
    for child in win.winfo_children():
        if isinstance(child, tk.Label):
            texts.append(str(child.cget('text')))
        texts.extend(_label_texts(child))
    return texts


def _has_read_again(win: tk.Misc) -> bool:
    """Return whether a 'Read again' button exists in a subtree."""
    for child in win.winfo_children():
        if (isinstance(child, tk.Button)
                and str(child.cget('text')) == 'Read again'):
            return True
        if _has_read_again(child):
            return True
    return False


def _reload_stub(store: list[object]) -> Callable[..., None]:
    """Return a reload capturing the apply callback it is given."""
    def reload(apply: object) -> None:
        store.append(apply)
    return reload


def _saver(path: Optional[str]) -> Callable[..., Optional[str]]:
    """Return a save_backlog stub returning a fixed path."""
    def save(*_args: object, **_kw: object) -> Optional[str]:
        return path
    return save


def _file_source() -> BacklogSource:
    """Return a file backlog source read at a fixed time."""
    return BacklogSource(kind='file', read_time=T0, file_name='/tmp/b.csv')


def _jira_source() -> BacklogSource:
    """Return a Jira backlog source read at a fixed time."""
    return BacklogSource(kind='jira', read_time=T0, preset_name='scrum',
                         issue_filter='project = SCRUM')


def _make_win(root: tk.Misc, source: BacklogSource,
              captured: Optional[list[object]] = None) -> BacklogWindow:
    """Build a backlog window on a source with a capturing reload."""
    store = captured if captured is not None else []
    return BacklogWindow(root, DATA, 'T', _none, _none, SINK, source=source,
                         reload=_reload_stub(store))


def test_file_info_region() -> None:
    """Test a file window shows the read time and the file name."""
    with gui_root() as root:
        window = _make_win(root, _file_source())
        assert _time_of(window) == 'Read from file at 2026-07-18 14:30:45'
        assert 'File: /tmp/b.csv' in _label_texts(_win_of(window))
        assert _has_read_again(_win_of(window))
        assert _mark_of(window) == ''


def test_jira_info_region() -> None:
    """Test a Jira window shows the read time and the filter."""
    with gui_root() as root:
        window = _make_win(root, _jira_source())
        assert _time_of(window) == 'Read from Jira at 2026-07-18 14:30:45'
        assert 'Filter: project = SCRUM' in _label_texts(_win_of(window))


def test_demo_info_region() -> None:
    """Test a demo window shows the time but offers no Read again."""
    with gui_root() as root:
        source = BacklogSource(kind='demo', read_time=T0)
        window = BacklogWindow(root, DATA, 'Demo', _none, _none, SINK,
                               source=source)
        assert _time_of(window) == ('Demo backlog created at '
                                    '2026-07-18 14:30:45')
        assert not _has_read_again(_win_of(window))


def test_no_source_no_info() -> None:
    """Test a window without a source shows no information region."""
    with gui_root() as root:
        window = BacklogWindow(root, DATA, 'T', _none, _none, SINK)
        # pylint: disable-next=protected-access
        assert window._time_var is None
        assert not _has_read_again(_win_of(window))


def test_action_modifies() -> None:
    """Test a data-changing refresh marks the window modified."""
    with gui_root() as root:
        window = _make_win(root, _file_source())
        # pylint: disable-next=protected-access
        window._changed_refresh()
        assert _mark_of(window) == MODIFIED_MARK


def test_jira_rekey_marks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test applying a Jira add result marks the window modified."""
    def apply_result(_data: object, _result: object,
                     refresh: Callable[[], None], _show: object) -> None:
        refresh()
    monkeypatch.setattr(backlog_window, 'apply_add_result', apply_result)
    with gui_root() as root:
        window = _make_win(root, _jira_source())
        # pylint: disable-next=protected-access
        window._on_jira_added(cast(AddedToJira, object()))
        assert _mark_of(window) == MODIFIED_MARK


def test_read_again_reloads(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test Read again replaces data, updates time and clears the mark."""
    monkeypatch.setattr(backlog_window, 'current_time', lambda: T1)
    monkeypatch.setattr(backlog_window, 'messagebox', MsgRecorder(True))
    with gui_root() as root:
        captured: list[object] = []
        window = _make_win(root, _file_source(), captured)
        # pylint: disable-next=protected-access
        window._changed_refresh()
        # pylint: disable-next=protected-access
        window._read_again()
        assert len(captured) == 1
        new_data = get_demo_backlog()
        apply = captured[0]
        assert callable(apply)
        apply(new_data, None)
        # pylint: disable-next=protected-access
        assert window._data is new_data
        assert _mark_of(window) == ''
        assert _time_of(window) == 'Read from file at 2026-07-18 15:00:00'


def test_read_again_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the discard confirm skips the re-read."""
    monkeypatch.setattr(backlog_window, 'messagebox', MsgRecorder(False))
    with gui_root() as root:
        captured: list[object] = []
        window = _make_win(root, _file_source(), captured)
        # pylint: disable-next=protected-access
        window._changed_refresh()
        # pylint: disable-next=protected-access
        window._read_again()
        assert not captured


def test_reread_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test Read again without changes re-reads without confirming."""
    monkeypatch.setattr(backlog_window, 'messagebox', MsgRecorder(False))
    with gui_root() as root:
        captured: list[object] = []
        window = _make_win(root, _file_source(), captured)
        # pylint: disable-next=protected-access
        window._read_again()
        assert len(captured) == 1


def test_save_clears_mark(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test saving to the source file clears the modified mark."""
    monkeypatch.setattr(backlog_window, 'save_backlog', _saver('/tmp/b.csv'))
    with gui_root() as root:
        window = _make_win(root, _file_source())
        # pylint: disable-next=protected-access
        window._changed_refresh()
        # pylint: disable-next=protected-access
        window._save()
        assert _mark_of(window) == ''


def test_save_keeps_mark(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test saving to a different file keeps the modified mark."""
    monkeypatch.setattr(backlog_window, 'save_backlog', _saver('/tmp/x.csv'))
    with gui_root() as root:
        window = _make_win(root, _file_source())
        # pylint: disable-next=protected-access
        window._changed_refresh()
        # pylint: disable-next=protected-access
        window._save()
        assert _mark_of(window) == MODIFIED_MARK


def test_save_cancel_keeps(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled save leaves the modified mark in place."""
    monkeypatch.setattr(backlog_window, 'save_backlog', _saver(None))
    with gui_root() as root:
        window = _make_win(root, _jira_source())
        # pylint: disable-next=protected-access
        window._changed_refresh()
        # pylint: disable-next=protected-access
        window._save()
        assert _mark_of(window) == MODIFIED_MARK


def test_reload_adds_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a re-read that returns a warning disables the operations."""
    monkeypatch.setattr(backlog_window, 'current_time', lambda: T1)
    with gui_root() as root:
        captured: list[object] = []
        window = _make_win(root, _jira_source(), captured)
        # pylint: disable-next=protected-access
        window._read_again()
        apply = captured[0]
        assert callable(apply)
        apply(DATA, 'Broken data')
        assert 'Broken data' in _label_texts(_win_of(window))
        menu = _backlog_menu(window)
        last = menu.index('end')
        assert last is not None
        states = {menu.entrycget(i, 'label'): menu.entrycget(i, 'state')
                  for i in range(last + 1)
                  if menu.type(i) != 'separator'}
        assert states['Order by keys…'] == 'disabled'
        assert states['Save to file…'] == 'normal'
