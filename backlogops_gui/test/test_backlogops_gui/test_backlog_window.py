#! /usr/local/bin/python3
"""Tests for the backlog window widget and its menu wiring."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable
import pytest
from backlogops import (
    BacklogReleases, GuiDisplayConfig, NoTextIO, get_demo_backlog)
from backlogops_gui import backlog_window
from backlogops_gui.backlog_window import BacklogWindow, JiraHandlers
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
