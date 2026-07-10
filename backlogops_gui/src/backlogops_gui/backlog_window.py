#! /usr/local/bin/python3
"""A window that shows one backlog and its releases as two tables.

The window shows the backlog and the releases as two read-only tables and
carries a menu with the actions that can be done to the backlog. The
backlog table fills the window, while the releases table, which has only a
few columns, is kept narrow so its columns are not spread out. The menu
offers reordering, ready-date estimation, release planning, key
extraction, the Jira operations, saving to a file and closing the window.
The operations themselves live in :mod:`backlogops_gui.backlog_actions`,
so they can be tested without a display.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Callable, Literal, Optional, TextIO
from tableio import ValueFmt
from backlogops import (
    AddedReleasesToJira, AddedToJira, AvailableTeams, BacklogReleases,
    GuiDisplayConfig, Levels, OrderedReleasesInJira, OutputFormatConfig,
    RankedInJira, RenamedReleasesInJira, UpdatedBacklogInJira,
    UpdatedReleasesInJira, format_order_result, format_rank_result,
    format_release_result, format_release_updates, format_rename_result)
from backlogops_gui.backlog_actions import (
    adjust_content, apply_add_result, apply_update_result, estimate_date,
    extract_keys, order_by_deps, order_by_keys, order_by_release, order_dates,
    plan_dates, save_backlog, set_plan)
from backlogops_gui.close_binding import CLOSE_ACCELERATOR, bind_close
from backlogops_gui.report_windows import show_text_report
from backlogops_gui.table_view import (
    backlog_table, make_table, release_table)

RELEASE_COLUMN_WIDTH = 110
WARNING_WRAP = 760


@dataclass
class JiraHandlers:
    """The optional Jira menu handlers a backlog window offers.

    Each handler runs one Jira operation and calls back with its result, or
    is None when that operation is unavailable (no configuration or no Jira
    presets), which disables its menu item. Passing the handlers as one
    group keeps the window constructor small.
    """

    add_backlog: Optional[Callable[
        [BacklogReleases, Callable[[AddedToJira], None]], None]] = None
    add_releases: Optional[Callable[
        [BacklogReleases, Callable[[AddedReleasesToJira], None]],
        None]] = None
    update_releases: Optional[Callable[
        [BacklogReleases, Callable[[UpdatedReleasesInJira], None]],
        None]] = None
    update_backlog: Optional[Callable[
        [BacklogReleases, Callable[[UpdatedBacklogInJira], None]],
        None]] = None
    rank: Optional[Callable[
        [Callable[[RankedInJira], None]], None]] = None
    order_releases: Optional[Callable[
        [BacklogReleases, Callable[[OrderedReleasesInJira], None]],
        None]] = None
    rename_releases: Optional[Callable[
        [BacklogReleases, Callable[[RenamedReleasesInJira], None]],
        None]] = None


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
                 jira: Optional[JiraHandlers] = None) -> None:
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
            jira: The Jira menu handlers to offer, or None for none. Each
                handler is None when its operation is unavailable, which
                disables its menu item.
        """
        handlers = jira if jira is not None else JiraHandlers()
        self._data = data
        self._presets = presets
        self._teams = teams
        self._sink = sink
        self._levels = levels
        self._gui_display = gui_display
        self._warning = warning
        self._add_to_jira = handlers.add_backlog
        self._add_releases = handlers.add_releases
        self._update_releases = handlers.update_releases
        self._update_backlog = handlers.update_backlog
        self._rank_in_jira = handlers.rank
        self._order_releases = handlers.order_releases
        self._rename_releases = handlers.rename_releases
        self._win = tk.Toplevel(root)
        self._win.title(title)
        bind_close(self._win)
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
        backlog_menu.add_command(label='Close', command=self._win.destroy,
                                 accelerator=CLOSE_ACCELERATOR)
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
        order_state: Literal['normal', 'disabled']
        order_state = ('normal' if self._order_releases is not None
                       and self._warning is None else 'disabled')
        menu.add_command(label='Order releases in Jira…',
                         command=self._releases_order, state=order_state)
        rename_state: Literal['normal', 'disabled']
        rename_state = ('normal' if self._rename_releases is not None
                        and self._warning is None else 'disabled')
        menu.add_command(label='Rename releases in Jira…',
                         command=self._releases_rename, state=rename_state)
        rank_state: Literal['normal', 'disabled']
        rank_state = ('normal' if self._rank_in_jira is not None
                      and self._warning is None else 'disabled')
        menu.add_command(label='Rank items in Jira…', command=self._rank_jira,
                         state=rank_state)

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

    def _rank_jira(self) -> None:
        """Move chosen issues in the Jira rank order and show the result."""
        if self._rank_in_jira is not None:
            self._rank_in_jira(self._on_ranked)

    def _on_ranked(self, result: RankedInJira) -> None:
        """Show the ranked and skipped keys in a copy-pasteable pop-up.

        Ranking changes only the Jira rank of issues, not the shown
        backlog, so no rebuild of the tables is needed.
        """
        show_text_report(self._win, 'Rank items in Jira',
                         format_rank_result(result))

    def _releases_order(self) -> None:
        """Order the releases in Jira and show the result lists."""
        if self._order_releases is not None:
            self._order_releases(self._data, self._on_releases_ordered)

    def _on_releases_ordered(self, result: OrderedReleasesInJira) -> None:
        """Show the ordered and skipped release names in a pop-up.

        Ordering changes only the Jira version order, not the shown
        releases, so no rebuild of the tables is needed.
        """
        show_text_report(self._win, 'Order releases in Jira',
                         format_order_result(result))

    def _releases_rename(self) -> None:
        """Rename the shown releases in Jira and show the result lists."""
        if self._rename_releases is not None:
            self._rename_releases(self._data, self._on_releases_renamed)

    def _on_releases_renamed(self, result: RenamedReleasesInJira) -> None:
        """Show the rename outcome per release in a pop-up.

        Renaming changes only the Jira version names, not the shown
        releases, so no rebuild of the tables is needed.
        """
        show_text_report(self._win, 'Rename releases in Jira',
                         format_rename_result(result))
