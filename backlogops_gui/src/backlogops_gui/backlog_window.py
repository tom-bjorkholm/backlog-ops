#! /usr/local/bin/python3
"""A window that shows one backlog and its releases as two tables.

The window shows the backlog and the releases as two read-only tables and
carries a menu with the actions that can be done to the backlog. The
backlog table fills the window, while the releases table, which has only a
few columns, is kept narrow so its columns are not spread out. The menu
offers reordering, ready-date estimation, release planning, key
extraction, saving to a file and closing the window. Saving is kept in a
module function so it can be tested without a display.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from datetime import timedelta
from tkinter import messagebox, ttk
from typing import Callable, Literal, Optional, TextIO
from tableio import ValueFmt
from backlogops import (
    AddedReleasesToJira, AddedToJira, AvailableTeams, BacklogReleases,
    GuiDisplayConfig, Levels, OutputFormatConfig, ReleaseChanges,
    ReleaseDateChanges, UpdatedBacklogInJira, UpdatedReleasesInJira,
    allow_overwrite, apply_jira_keys, format_add_result,
    format_backlog_updates, format_content_changes, format_date_changes,
    format_release_result, format_release_updates, get_keys_in_order,
    write_content_changes, write_date_changes, write_key_list)
from backlogops_gui.backlog_io import write_backlog
from backlogops_gui.io_dialogs import (
    ask_buffer_days, ask_date_order, ask_dep_options, ask_keys, ask_levels,
    ask_release_order, ask_start_date, ask_write_options,
    choose_changes_output, choose_key_list_output, choose_output_file,
    show_change_list, show_text_report)
from backlogops_gui.table_view import (
    backlog_table, make_table, release_table)

WRITE_ERRORS = (ValueError, TypeError, KeyError, OSError)
ACTION_ERRORS = (ValueError, TypeError, KeyError, RuntimeError, OSError)
RELEASE_COLUMN_WIDTH = 110
WARNING_WRAP = 760


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def save_backlog(parent: tk.Misc, data: BacklogReleases,
                 presets: Optional[dict[str, OutputFormatConfig]],
                 levels: Optional[Levels], sink: TextIO,
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None:
    """Ask where and how to save a backlog and write it.

    Args:
        parent: The window the dialogs are shown over.
        data: The backlog and releases to write.
        presets: Named output presets, or None when none are configured.
        levels: The levels used to write level names, or None for the
            default levels.
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
                      options.releases_first, sink, levels)
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


def _release_order_message(honor: bool, later: bool) -> str:
    """Return the success message describing a release-order action."""
    if not honor:
        return ('Ordered the backlog by release order without honoring '
                'dependencies.')
    if later:
        return ('Ordered the backlog by release order, honoring '
                'dependencies by pushing dependents later.')
    return ('Ordered the backlog by release order, honoring dependencies '
            'by pulling prerequisites earlier.')


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def order_by_release(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                     refresh: Callable[[], None],
                     on_error: Callable[[str, str], None],
                     on_info: Callable[[str, str], None]) -> None:
    """Ask for options and order the backlog by release order."""
    options = ask_release_order(parent)
    if options is None:
        return
    honor, later = options.honor_dependencies, options.later
    message = _release_order_message(honor, later)

    def change() -> None:
        """Order the backlog by release order with the chosen options."""
        data.backlog_in_release_order(honor_dependencies=honor, later=later,
                                      stderr_file=sink)
    _apply_change(change, refresh, on_error, on_info,
                  'Could not order by release order', 'Ordered backlog',
                  message)


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def save_changes(parent: tk.Misc,
                 write_changes: Optional[Callable[[str], None]],
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None:
    """Ask for a file and write the change list to it.

    A ``write_changes`` of None means there are no changes, so nothing is
    written and that is reported through ``on_info`` instead.
    """
    if write_changes is None:
        on_info('No changes', 'There are no changes to write.')
        return
    path = choose_changes_output(parent)
    if path is None:
        return
    try:
        write_changes(path)
    except WRITE_ERRORS as error:
        on_error('Could not write file', str(error))
        return
    on_info('Wrote file', f'Wrote {path}')


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def show_changes(parent: tk.Misc, title: str, text: str,
                 write_changes: Optional[Callable[[str], None]],
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None:
    """Show the change listing in a pop-up that can save it to a file."""
    show_change_list(parent, title, text,
                     lambda: save_changes(parent, write_changes, on_error,
                                          on_info))


def _date_report(changes: ReleaseDateChanges, sink: TextIO
                 ) -> tuple[str, Optional[Callable[[str], None]]]:
    """Return the date change listing and a writer, None when empty.

    The native save dialog has already confirmed the overwrite, so the
    writer allows overwriting an existing file.
    """
    def write(path: str) -> None:
        """Write the date changes; the dialog confirmed the overwrite."""
        write_date_changes(changes, path, sink,
                           file_exists_callback=allow_overwrite)
    return format_date_changes(changes), (write if changes else None)


def _content_report(changes: ReleaseChanges, sink: TextIO
                    ) -> tuple[str, Optional[Callable[[str], None]]]:
    """Return the content change listing and a writer, None when empty.

    The native save dialog has already confirmed the overwrite, so the
    writer allows overwriting an existing file.
    """
    def write(path: str) -> None:
        """Write the content changes; the dialog confirmed the overwrite."""
        write_content_changes(changes, path, sink,
                              file_exists_callback=allow_overwrite)
    return format_content_changes(changes), (write if changes else None)


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _run_change(parent: tk.Misc,
                change: Callable[[], tuple[str,
                                           Optional[Callable[[str], None]]]],
                refresh: Callable[[], None],
                on_error: Callable[[str, str], None],
                on_info: Callable[[str, str], None], fail_title: str,
                title: str) -> None:
    """Run a change returning a report, refresh, then show the pop-up.

    A change that raises one of the known data errors is reported and
    leaves the view unchanged. A successful change refreshes the view and
    shows the change listing in a pop-up that can save it to a file.
    """
    try:
        text, write_changes = change()
    except ACTION_ERRORS as error:
        on_error(fail_title, str(error))
        return
    refresh()
    show_changes(parent, title, text, write_changes, on_error, on_info)


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

    def change() -> tuple[str, Optional[Callable[[str], None]]]:
        """Estimate the dates and return the release date change report."""
        changes = data.estimate_ready_date(ready_teams, start, sink)
        return _date_report(changes, sink)
    _run_change(parent, change, refresh, on_error, on_info,
                'Could not estimate ready date', 'Release date changes')


def set_plan(data: BacklogReleases, sink: TextIO, refresh: Callable[[], None],
             on_error: Callable[[str, str], None],
             on_info: Callable[[str, str], None]) -> None:
    """Copy the estimated ready dates to the planned ready dates."""
    _apply_change(lambda: data.set_plan_from_estimate(sink), refresh, on_error,
                  on_info, 'Could not set planned date', 'Set planned date',
                  'Copied the estimated dates to the planned dates.')


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def adjust_content(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                   refresh: Callable[[], None],
                   on_error: Callable[[str, str], None],
                   on_info: Callable[[str, str], None]) -> None:
    """Ask for a buffer and adjust the release content to the estimate."""
    days = ask_buffer_days(parent)
    if days is None:
        return

    def change() -> tuple[str, Optional[Callable[[str], None]]]:
        """Adjust the release content and return the change report."""
        changes = data.adjust_release_content(timedelta(days=days), sink)
        return _content_report(changes, sink)
    _run_change(parent, change, refresh, on_error, on_info,
                'Could not adjust release content', 'Release content changes')


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def plan_dates(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
               refresh: Callable[[], None],
               on_error: Callable[[str, str], None],
               on_info: Callable[[str, str], None]) -> None:
    """Ask for a buffer and set planned release dates from the estimate."""
    days = ask_buffer_days(parent)
    if days is None:
        return

    def change() -> tuple[str, Optional[Callable[[str], None]]]:
        """Set the planned release dates and return the change report."""
        changes = data.release_plan_on_estimate(timedelta(days=days), sink)
        return _date_report(changes, sink)
    _run_change(parent, change, refresh, on_error, on_info,
                'Could not set planned release dates', 'Release date changes')


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def order_dates(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                refresh: Callable[[], None],
                on_error: Callable[[str, str], None],
                on_info: Callable[[str, str], None]) -> None:
    """Ask for the date kind and order the releases by that date."""
    by_estimated = ask_date_order(parent)
    if by_estimated is None:
        return
    kind = 'estimated' if by_estimated else 'planned'
    _apply_change(lambda: data.order_releases_by_date(by_estimated, sink),
                  refresh, on_error, on_info, 'Could not order releases',
                  'Ordered releases', f'Ordered the releases by {kind} date.')


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
        write_key_list(keys, path, stderr_file=sink,
                       file_exists_callback=allow_overwrite)
    except ACTION_ERRORS as error:
        on_error('Could not extract keys', str(error))
        return
    on_info('Wrote keys', f'Wrote {path}')


def apply_add_result(data: BacklogReleases, result: AddedToJira,
                     refresh: Callable[[], None],
                     show_report: Callable[[str], None]) -> None:
    """Rekey the shown backlog, refresh the view and show the two lists.

    The added items take their new Jira keys (order preserved), the view
    is rebuilt, and the added and already-present lists are shown to the
    user through ``show_report``.
    """
    apply_jira_keys(data.backlog, result.key_map)
    refresh()
    show_report(format_add_result(result))


def apply_update_result(data: BacklogReleases, result: UpdatedBacklogInJira,
                        refresh: Callable[[], None],
                        show_report: Callable[[str], None]) -> None:
    """Rekey any added items, refresh the view and show the update lists.

    Only the items added under the ``ADD`` policy took new Jira keys, so
    the shown backlog is rekeyed with the add result's key map, the view is
    rebuilt, and the update outcome is shown through ``show_report``.
    """
    apply_jira_keys(data.backlog, result.added.key_map)
    refresh()
    show_report(format_backlog_updates(result))


# pylint: disable-next=too-few-public-methods,too-many-instance-attributes
class BacklogWindow:
    """A top-level window showing one backlog and its releases."""

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __init__(self, root: tk.Misc, data: BacklogReleases, title: str,
                 presets: Callable[
                     [], Optional[dict[str, OutputFormatConfig]]],
                 teams: Callable[[], Optional[AvailableTeams]], sink: TextIO,
                 levels: Callable[[], Optional[Levels]] = lambda: None,
                 gui_display: Callable[
                     [], GuiDisplayConfig] = GuiDisplayConfig,
                 warning: Optional[str] = None,
                 add_to_jira: Optional[Callable[
                     [BacklogReleases, Callable[[AddedToJira], None]],
                     None]] = None,
                 add_releases: Optional[Callable[
                     [BacklogReleases, Callable[[AddedReleasesToJira], None]],
                     None]] = None,
                 update_releases: Optional[Callable[
                     [BacklogReleases,
                      Callable[[UpdatedReleasesInJira], None]],
                     None]] = None,
                 update_backlog: Optional[Callable[
                     [BacklogReleases,
                      Callable[[UpdatedBacklogInJira], None]],
                     None]] = None) -> None:
        """Build the window, its menu and the two tables.

        Args:
            root: The parent window the new window belongs to.
            data: The backlog and releases to show.
            title: The window title, typically the source file name.
            presets: Callable returning the current output presets.
            teams: Callable returning the loaded teams configuration.
            sink: Stream that receives low-level write diagnostics.
            levels: Callable returning the configured levels, or None for
                the default levels.
            gui_display: Callable returning the GUI display configuration,
                which decides the level display and the per-table column
                renaming for the tables.
            warning: Warning text to show over the tables. When present,
                backlog operations are disabled and only saving remains.
            add_to_jira: Handler that adds the shown backlog to Jira and
                calls back with the result, or None when adding is
                unavailable (no configuration or no write presets).
            add_releases: Handler that adds the shown releases to Jira and
                calls back with the result, or None when adding is
                unavailable (no configuration or no write presets).
            update_releases: Handler that updates the shown releases in Jira
                and calls back with the result, or None when updating is
                unavailable (no configuration or no write presets).
            update_backlog: Handler that updates the shown backlog in Jira
                and calls back with the result, or None when updating is
                unavailable (no configuration or no write presets).
        """
        self._data = data
        self._presets = presets
        self._teams = teams
        self._sink = sink
        self._levels = levels
        self._gui_display = gui_display
        self._warning = warning
        self._add_to_jira = add_to_jira
        self._add_releases = add_releases
        self._update_releases = update_releases
        self._update_backlog = update_backlog
        self._win = tk.Toplevel(root)
        self._win.title(title)
        self._tables: list[tk.Widget] = []
        self._add_menu()
        self._add_warning()
        self._build_tables()

    def _report_error(self, title: str, message: str) -> None:
        """Show an error message over this backlog window."""
        messagebox.showerror(title, message, parent=self._win)

    def _report_info(self, title: str, message: str) -> None:
        """Show an informational message over this backlog window."""
        messagebox.showinfo(title, message, parent=self._win)

    def _build_tables(self) -> None:
        """Build the backlog and releases tables from the current data."""
        display = self._gui_display()
        backlog = backlog_table(self._data, self._levels(),
                                display.level_display,
                                display.backlog_to_external, self._sink)
        table = self._add_table('Backlog', *backlog, narrow=False)
        self._tables.append(table)
        releases = release_table(self._data, display.release_to_external)
        self._tables.append(
            self._add_table('Releases', *releases, narrow=True))

    def _refresh_tables(self) -> None:
        """Rebuild the tables after the backlog data has changed."""
        for table in self._tables:
            table.destroy()
        self._tables = []
        self._build_tables()

    def _add_warning(self) -> None:
        """Show a highly visible warning over restricted backlog data."""
        if self._warning is None:
            return
        color = 'yellow'
        label = tk.Label(self._win, text=self._warning, bg=color, fg='black',
                         justify='left', wraplength=WARNING_WRAP)
        label.pack(fill='x', padx=8, pady=(8, 2))

    def _add_menu(self) -> None:
        """Add the backlog menu with the action, save and close items."""
        menubar = tk.Menu(self._win)
        backlog_menu = tk.Menu(menubar, tearoff=False)
        jira_menu = tk.Menu(menubar, tearoff=False)
        self._add_actions(backlog_menu)
        self._add_jira_actions(jira_menu)
        backlog_menu.add_separator()
        backlog_menu.add_command(label='Save to file…', command=self._save)
        backlog_menu.add_command(label='Close', command=self._win.destroy)
        menubar.add_cascade(label='Backlog', menu=backlog_menu)
        menubar.add_cascade(label='Jira', menu=jira_menu)
        self._win.config(menu=menubar)

    def _add_actions(self, menu: tk.Menu) -> None:
        """Add the backlog operation items to the menu."""
        state: Literal['normal', 'disabled']
        state = 'disabled' if self._warning is not None else 'normal'
        menu.add_command(label='Order by keys…', command=self._order_by_keys,
                         state=state)
        menu.add_command(label='Order by dependencies…',
                         command=self._order_by_deps, state=state)
        menu.add_command(label='Order by release order…',
                         command=self._order_by_release, state=state)
        menu.add_command(label='Estimate ready date…',
                         command=self._estimate_date, state=state)
        menu.add_command(label='Set planned date from estimated',
                         command=self._set_plan, state=state)
        menu.add_command(label='Adjust release content…',
                         command=self._adjust_content, state=state)
        menu.add_command(label='Adjust planned release dates…',
                         command=self._plan_dates, state=state)
        menu.add_command(label='Order releases by date…',
                         command=self._order_dates, state=state)
        menu.add_command(label='Extract keys…', command=self._extract_keys,
                         state=state)

    def _add_jira_actions(self, menu: tk.Menu) -> None:
        """Add the Jira operation items to the menu."""
        jira_state: Literal['normal', 'disabled']
        jira_state = ('normal' if self._add_to_jira is not None
                      and self._warning is None else 'disabled')
        menu.add_command(label='Add backlog to Jira…', command=self._jira_add,
                         state=jira_state)
        upd_bl_state: Literal['normal', 'disabled']
        upd_bl_state = ('normal' if self._update_backlog is not None
                        and self._warning is None else 'disabled')
        menu.add_command(label='Update backlog in Jira…',
                         command=self._backlog_update, state=upd_bl_state)
        rel_state: Literal['normal', 'disabled']
        rel_state = ('normal' if self._add_releases is not None
                     and self._warning is None else 'disabled')
        menu.add_command(label='Add releases to Jira…',
                         command=self._releases_add, state=rel_state)
        upd_state: Literal['normal', 'disabled']
        upd_state = ('normal' if self._update_releases is not None
                     and self._warning is None else 'disabled')
        menu.add_command(label='Update releases in Jira…',
                         command=self._releases_update, state=upd_state)

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
        save_backlog(self._win, self._data, self._presets(), self._levels(),
                     self._sink, self._report_error, self._report_info)

    def _order_by_keys(self) -> None:
        """Order the backlog by leading keys and refresh the tables."""
        order_by_keys(self._win, self._data, self._sink, self._refresh_tables,
                      self._report_error, self._report_info)

    def _order_by_deps(self) -> None:
        """Order the backlog by dependencies and refresh the tables."""
        order_by_deps(self._win, self._data, self._sink, self._refresh_tables,
                      self._report_error, self._report_info)

    def _order_by_release(self) -> None:
        """Order the backlog by release order and refresh the tables."""
        order_by_release(self._win, self._data, self._sink,
                         self._refresh_tables, self._report_error,
                         self._report_info)

    def _estimate_date(self) -> None:
        """Estimate the ready dates and refresh the tables."""
        estimate_date(self._win, self._data, self._teams(), self._sink,
                      self._refresh_tables, self._report_error,
                      self._report_info)

    def _set_plan(self) -> None:
        """Copy the estimated dates to the planned dates and refresh."""
        set_plan(self._data, self._sink, self._refresh_tables,
                 self._report_error, self._report_info)

    def _adjust_content(self) -> None:
        """Adjust the release content to the estimate and refresh."""
        adjust_content(self._win, self._data, self._sink, self._refresh_tables,
                       self._report_error, self._report_info)

    def _plan_dates(self) -> None:
        """Set planned release dates from the estimate and refresh."""
        plan_dates(self._win, self._data, self._sink, self._refresh_tables,
                   self._report_error, self._report_info)

    def _order_dates(self) -> None:
        """Order the releases by date and refresh the tables."""
        order_dates(self._win, self._data, self._sink, self._refresh_tables,
                    self._report_error, self._report_info)

    def _extract_keys(self) -> None:
        """Extract backlog keys at chosen levels to a key list file."""
        extract_keys(self._win, self._data, self._sink, self._report_error,
                     self._report_info)

    def _jira_add(self) -> None:
        """Add the shown backlog to Jira, adjusting the view on success."""
        if self._add_to_jira is not None:
            self._add_to_jira(self._data, self._on_jira_added)

    def _on_jira_added(self, result: AddedToJira) -> None:
        """Rekey the shown backlog and show the two result lists."""
        apply_add_result(self._data, result, self._refresh_tables,
                         self._show_add_report)

    def _show_add_report(self, text: str) -> None:
        """Show the add result text in a copy-pasteable pop-up."""
        show_text_report(self._win, 'Added to Jira', text)

    def _releases_add(self) -> None:
        """Add the shown releases to Jira and show the result lists."""
        if self._add_releases is not None:
            self._add_releases(self._data, self._on_releases_added)

    def _on_releases_added(self, result: AddedReleasesToJira) -> None:
        """Show the added, present and failed release lists.

        A release name never changes, so the shown releases already match
        what was added and no rebuild of the tables is needed.
        """
        show_text_report(self._win, 'Add releases to Jira',
                         format_release_result(result))

    def _releases_update(self) -> None:
        """Update the shown releases in Jira and show the result lists."""
        if self._update_releases is not None:
            self._update_releases(self._data, self._on_releases_updated)

    def _on_releases_updated(self, result: UpdatedReleasesInJira) -> None:
        """Show the update outcome per release in a pop-up.

        The lists are the updated, already-correct, ignored, added and
        failed releases. An update changes only the Jira versions, not the
        shown releases, so no rebuild of the tables is needed.
        """
        show_text_report(self._win, 'Update releases in Jira',
                         format_release_updates(result))

    def _backlog_update(self) -> None:
        """Update the shown backlog in Jira and show the result lists."""
        if self._update_backlog is not None:
            self._update_backlog(self._data, self._on_backlog_updated)

    def _on_backlog_updated(self, result: UpdatedBacklogInJira) -> None:
        """Rekey any added items, refresh the view and show the outcome.

        Only items added under the ``ADD`` policy took new Jira keys, so the
        shown backlog is rekeyed for them, the tables are rebuilt, and the
        update outcome is shown in a copy-pasteable pop-up.
        """
        apply_update_result(self._data, result, self._refresh_tables,
                            self._show_update_report)

    def _show_update_report(self, text: str) -> None:
        """Show the backlog update result text in a copy-pasteable pop-up."""
        show_text_report(self._win, 'Update backlog in Jira', text)
