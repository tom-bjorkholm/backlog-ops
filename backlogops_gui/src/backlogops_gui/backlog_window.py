#! /usr/local/bin/python3
"""A window that shows one backlog and its releases as two tables.

The window shows the backlog and the releases as two read-only tables and
carries a menu with the actions that can be done to the backlog. The first
version offers saving to a file and closing the window. Saving is kept in a
module function so it can be tested without a display.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from backlogops import BacklogReleases, OutputFormatConfig
from backlogops_gui.backlog_io import write_backlog
from backlogops_gui.io_dialogs import ask_write_options, choose_output_file
from backlogops_gui.table_view import (
    backlog_table, make_table, release_table)

WRITE_ERRORS = (ValueError, TypeError, KeyError, OSError)


def save_backlog(parent: tk.Misc, data: BacklogReleases,
                 presets: Optional[dict[str, OutputFormatConfig]],
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None:
    """Ask where and how to save a backlog and write it.

    Args:
        parent: The window the dialogs are shown over.
        data: The backlog and releases to write.
        presets: Named output presets, or None when none are configured.
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
                      options.releases_first)
    except WRITE_ERRORS as error:
        on_error('Could not write file', str(error))
        return
    on_info('Wrote file', f'Wrote {path}')


# pylint: disable-next=too-few-public-methods
class BacklogWindow:
    """A top-level window showing one backlog and its releases."""

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __init__(self, root: tk.Misc, data: BacklogReleases, title: str,
                 presets: Callable[
                     [], Optional[dict[str, OutputFormatConfig]]],
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None:
        """Build the window, its menu and the two tables.

        Args:
            root: The parent window the new window belongs to.
            data: The backlog and releases to show.
            title: The window title, typically the source file name.
            presets: Callable returning the current output presets.
            on_error: Callback used to report a write failure.
            on_info: Callback used to report a successful write.
        """
        self._data = data
        self._presets = presets
        self._on_error = on_error
        self._on_info = on_info
        self._win = tk.Toplevel(root)
        self._win.title(title)
        self._add_menu()
        self._add_table('Backlog', *backlog_table(data))
        self._add_table('Releases', *release_table(data))

    def _add_menu(self) -> None:
        """Add the backlog menu with the save and close actions."""
        menubar = tk.Menu(self._win)
        backlog_menu = tk.Menu(menubar, tearoff=False)
        backlog_menu.add_command(label='Save to file…', command=self._save)
        backlog_menu.add_separator()
        backlog_menu.add_command(label='Close', command=self._win.destroy)
        menubar.add_cascade(label='Backlog', menu=backlog_menu)
        self._win.config(menu=menubar)

    def _add_table(self, heading: str, columns: list[str],
                   rows: list[list[str]]) -> None:
        """Add one labeled, scrollable table to the window."""
        frame = tk.LabelFrame(self._win, text=heading)
        frame.pack(padx=8, pady=6, fill='both', expand=True)
        tree = make_table(frame, columns, rows)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)

    def _save(self) -> None:
        """Save the backlog through the shared save helper."""
        save_backlog(self._win, self._data, self._presets(), self._on_error,
                     self._on_info)
