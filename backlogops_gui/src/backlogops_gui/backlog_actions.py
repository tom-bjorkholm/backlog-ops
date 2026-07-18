#! /usr/local/bin/python3
"""Backlog operations driven from a backlog window.

Each function asks for the options an operation needs, runs the operation
on the backlog data, refreshes the view, and reports the outcome through
``on_error`` and ``on_info`` callbacks. Keeping the operations in module
functions lets them be tested without a display and keeps the window class
focused on its widgets. Saving to a file and the Jira result appliers live
here too, so the same reporting pattern is shared.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from datetime import timedelta
from typing import Callable, Optional, TextIO
from backlogops import (
    AddedToJira, AvailableTeams, BacklogReleases, Levels, OutputFormatConfig,
    ReleaseChanges, ReleaseDateChanges, UpdatedBacklogInJira, allow_overwrite,
    apply_jira_keys, format_add_result, format_backlog_updates,
    format_content_changes, format_date_changes, get_keys_in_order,
    write_content_changes, write_date_changes, write_key_list)
from backlogops_gui.backlog_io import write_backlog
from backlogops_gui.backlog_dialogs import (
    ask_buffer_days, ask_date_order, ask_dep_options, ask_keys, ask_levels,
    ask_release_order, ask_start_date)
from backlogops_gui.file_choosers import (
    choose_changes_output, choose_key_list_output, choose_output_file)
from backlogops_gui.format_dialogs import ask_write_options
from backlogops_gui.report_windows import show_change_list

WRITE_ERRORS = (ValueError, TypeError, KeyError, OSError)
ACTION_ERRORS = (ValueError, TypeError, KeyError, RuntimeError, OSError)


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def save_backlog(parent: tk.Misc, data: BacklogReleases,
                 presets: Optional[dict[str, OutputFormatConfig]],
                 levels: Optional[Levels], sink: TextIO,
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> Optional[str]:
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

    Returns:
        The path written, or None when the save was cancelled or failed.
    """
    path = choose_output_file(parent)
    if path is None:
        return None
    names = sorted(presets) if presets else None
    options = ask_write_options(parent, names)
    if options is None:
        return None
    try:
        write_backlog(data, path, options.config_value, presets,
                      options.releases_first, sink, levels)
    except WRITE_ERRORS as error:
        on_error('Could not write file', str(error))
        return None
    on_info('Wrote file', f'Wrote {path}')
    return path


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
