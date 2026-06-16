#! /usr/local/bin/python3
"""A window that shows one backlog and its releases as two tables.

The window shows the backlog and the releases as two read-only tables and
carries a menu with the actions that can be done to the backlog. The
backlog table fills the window, while the releases table, which has only a
few columns, is kept narrow so its columns are not spread out. The first
version offers saving to a file and closing the window. Saving is kept in a
module function so it can be tested without a display.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional, TextIO
from tableio import ValueFmt
from backlogops import (
    AvailableTeams, BacklogReleases, OutputFormatConfig, get_keys_in_order,
    write_key_list)
from backlogops_gui.backlog_io import write_backlog
from backlogops_gui.io_dialogs import (
    ask_dep_options, ask_keys, ask_levels, ask_start_date, ask_write_options,
    choose_key_list_output, choose_output_file)
from backlogops_gui.table_view import (
    backlog_table, make_table, release_table)

WRITE_ERRORS = (ValueError, TypeError, KeyError, OSError)
ACTION_ERRORS = (ValueError, TypeError, KeyError, RuntimeError, OSError)
RELEASE_COLUMN_WIDTH = 110


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def save_backlog(parent: tk.Misc, data: BacklogReleases,
                 presets: Optional[dict[str, OutputFormatConfig]],
                 sink: TextIO, on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None:
    """Ask where and how to save a backlog and write it.

    Args:
        parent: The window the dialogs are shown over.
        data: The backlog and releases to write.
        presets: Named output presets, or None when none are configured.
        sink: Stream that receives low-level write diagnostics.
        on_error: Callback used to report a write failure.
        on_info: Callback used to report a successful write.
    """
    path = choose_output_file(parent)
    if path is None:
        return
    names = sorted(presets) if presets else None
    options = ask_write_options(parent, names)
    if options is None:
        return
    try:
        write_backlog(data, path, options.config_value, presets,
                      options.releases_first, sink)
    except WRITE_ERRORS as error:
        on_error('Could not write file', str(error))
        return
    on_info('Wrote file', f'Wrote {path}')


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _apply_change(change: Callable[[], None], refresh: Callable[[], None],
                  on_error: Callable[[str, str], None],
                  on_info: Callable[[str, str], None], fail_title: str,
                  ok_title: str, ok_message: str) -> None:
    """Run a backlog change, refresh the view and report the outcome.

    A change that raises one of the known data errors is reported through
    ``on_error`` and leaves the view unchanged. A successful change
    refreshes the view and is reported through ``on_info``.
    """
    try:
        change()
    except ACTION_ERRORS as error:
        on_error(fail_title, str(error))
        return
    refresh()
    on_info(ok_title, ok_message)


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def order_by_keys(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                  refresh: Callable[[], None],
                  on_error: Callable[[str, str], None],
                  on_info: Callable[[str, str], None]) -> None:
    """Ask for leading keys and move those items to the front."""
    keys = ask_keys(parent, sink)
    if keys is None:
        return
    _apply_change(lambda: data.move_keys_first(keys, sink), refresh, on_error,
                  on_info, 'Could not order by keys', 'Ordered backlog',
                  'Moved the keys to the front.')


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def order_by_deps(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                  refresh: Callable[[], None],
                  on_error: Callable[[str, str], None],
                  on_info: Callable[[str, str], None]) -> None:
    """Ask for the options and order the backlog by dependencies."""
    options = ask_dep_options(parent)
    if options is None:
        return
    later, mode = options.later, options.mode
    space = options.space_around

    def change() -> None:
        """Order the backlog by dependencies with the chosen options."""
        data.order_by_dependencies(later=later, mode=mode, space_around=space,
                                   stderr_file=sink)
    _apply_change(change, refresh, on_error, on_info,
                  'Could not order by dependencies', 'Ordered backlog',
                  'Ordered the backlog by dependencies.')


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def estimate_date(parent: tk.Misc, data: BacklogReleases,
                  teams: Optional[AvailableTeams], sink: TextIO,
                  refresh: Callable[[], None],
                  on_error: Callable[[str, str], None],
                  on_info: Callable[[str, str], None]) -> None:
    """Ask for the start date and estimate the ready dates."""
    if teams is None:
        on_error('No configuration',
                 'There is no teams configuration to estimate from.')
        return
    choice = ask_start_date(parent)
    if choice is None:
        return
    ready_teams, start = teams, choice.start_date

    def change() -> None:
        """Estimate the ready dates from the chosen start date."""
        data.estimate_ready_date(ready_teams, start, sink)
    _apply_change(change, refresh, on_error, on_info,
                  'Could not estimate ready date', 'Estimated ready date',
                  'Filled in the estimated ready dates.')


def set_plan(data: BacklogReleases, sink: TextIO, refresh: Callable[[], None],
             on_error: Callable[[str, str], None],
             on_info: Callable[[str, str], None]) -> None:
    """Copy the estimated ready dates to the planned ready dates."""
    _apply_change(lambda: data.set_plan_from_estimate(sink), refresh, on_error,
                  on_info, 'Could not set planned date', 'Set planned date',
                  'Copied the estimated dates to the planned dates.')


def extract_keys(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None:
    """Ask for levels and a file, then write the backlog keys to it."""
    levels = ask_levels(parent)
    if levels is None:
        return
    path = choose_key_list_output(parent)
    if path is None:
        return
    try:
        keys = get_keys_in_order(data.backlog, levels)
        write_key_list(keys, path, stderr_file=sink)
    except ACTION_ERRORS as error:
        on_error('Could not extract keys', str(error))
        return
    on_info('Wrote keys', f'Wrote {path}')


# pylint: disable-next=too-few-public-methods,too-many-instance-attributes
class BacklogWindow:
    """A top-level window showing one backlog and its releases."""

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __init__(self, root: tk.Misc, data: BacklogReleases, title: str,
                 presets: Callable[
                     [], Optional[dict[str, OutputFormatConfig]]],
                 teams: Callable[[], Optional[AvailableTeams]],
                 sink: TextIO) -> None:
        """Build the window, its menu and the two tables.

        Args:
            root: The parent window the new window belongs to.
            data: The backlog and releases to show.
            title: The window title, typically the source file name.
            presets: Callable returning the current output presets.
            teams: Callable returning the loaded teams configuration.
            sink: Stream that receives low-level write diagnostics.
        """
        self._data = data
        self._presets = presets
        self._teams = teams
        self._sink = sink
        self._win = tk.Toplevel(root)
        self._win.title(title)
        self._tables: list[tk.Widget] = []
        self._add_menu()
        self._build_tables()

    def _report_error(self, title: str, message: str) -> None:
        """Show an error message over this backlog window."""
        messagebox.showerror(title, message, parent=self._win)

    def _report_info(self, title: str, message: str) -> None:
        """Show an informational message over this backlog window."""
        messagebox.showinfo(title, message, parent=self._win)

    def _build_tables(self) -> None:
        """Build the backlog and releases tables from the current data."""
        self._tables.append(
            self._add_table('Backlog', *backlog_table(self._data),
                            narrow=False))
        self._tables.append(
            self._add_table('Releases', *release_table(self._data),
                            narrow=True))

    def _refresh_tables(self) -> None:
        """Rebuild the tables after the backlog data has changed."""
        for table in self._tables:
            table.destroy()
        self._tables = []
        self._build_tables()

    def _add_menu(self) -> None:
        """Add the backlog menu with the action, save and close items."""
        menubar = tk.Menu(self._win)
        backlog_menu = tk.Menu(menubar, tearoff=False)
        self._add_actions(backlog_menu)
        backlog_menu.add_separator()
        backlog_menu.add_command(label='Save to file…', command=self._save)
        backlog_menu.add_command(label='Close', command=self._win.destroy)
        menubar.add_cascade(label='Backlog', menu=backlog_menu)
        self._win.config(menu=menubar)

    def _add_actions(self, menu: tk.Menu) -> None:
        """Add the backlog operation items to the menu."""
        menu.add_command(label='Order by keys…', command=self._order_by_keys)
        menu.add_command(label='Order by dependencies…',
                         command=self._order_by_deps)
        menu.add_command(label='Estimate ready date…',
                         command=self._estimate_date)
        menu.add_command(label='Set planned date from estimated',
                         command=self._set_plan)
        menu.add_command(label='Extract keys…', command=self._extract_keys)

    def _add_table(self, heading: str, columns: list[str],
                   rows: list[list[ValueFmt]], narrow: bool) -> tk.Widget:
        """Add one labeled, scrollable table and return its frame.

        The narrow table keeps its few columns at a fixed width and does
        not take the spare space, so it stays clearly narrower than the
        backlog table that fills the window.
        """
        frame = tk.LabelFrame(self._win, text=heading)
        tree = self._make_tree(frame, columns, rows, narrow)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        if narrow:
            frame.pack(padx=8, pady=6, anchor='w')
            tree.pack(side='left')
        else:
            frame.pack(padx=8, pady=6, fill='both', expand=True)
            tree.pack(side='left', fill='both', expand=True)
        return frame

    @staticmethod
    def _make_tree(frame: tk.Misc, columns: list[str],
                   rows: list[list[ValueFmt]], narrow: bool) -> ttk.Treeview:
        """Build the Treeview, keeping a narrow table from stretching."""
        if narrow:
            return make_table(frame, columns, rows, width=RELEASE_COLUMN_WIDTH,
                              stretch=False)
        return make_table(frame, columns, rows)

    def _save(self) -> None:
        """Save the backlog through the shared save helper."""
        save_backlog(self._win, self._data, self._presets(), self._sink,
                     self._report_error, self._report_info)

    def _order_by_keys(self) -> None:
        """Order the backlog by leading keys and refresh the tables."""
        order_by_keys(self._win, self._data, self._sink, self._refresh_tables,
                      self._report_error, self._report_info)

    def _order_by_deps(self) -> None:
        """Order the backlog by dependencies and refresh the tables."""
        order_by_deps(self._win, self._data, self._sink, self._refresh_tables,
                      self._report_error, self._report_info)

    def _estimate_date(self) -> None:
        """Estimate the ready dates and refresh the tables."""
        estimate_date(self._win, self._data, self._teams(), self._sink,
                      self._refresh_tables, self._report_error,
                      self._report_info)

    def _set_plan(self) -> None:
        """Copy the estimated dates to the planned dates and refresh."""
        set_plan(self._data, self._sink, self._refresh_tables,
                 self._report_error, self._report_info)

    def _extract_keys(self) -> None:
        """Extract backlog keys at chosen levels to a key list file."""
        extract_keys(self._win, self._data, self._sink, self._report_error,
                     self._report_info)
