#! /usr/local/bin/python3
"""Print and write release-change records as text or table files.

A release-change record is the small log produced by the release update
operations: which backlog item moved between releases
(:class:`ReleaseChange`) and how a release date moved
(:class:`ReleaseDateChange`). These functions render such a log as text
for the console and write it to a one-table file with TableIO, choosing
the file format from the file name extension.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from datetime import date
from pathlib import Path
from typing import Optional, Sequence, TextIO
from config_as_json import PathOrStr
from tableio import Value
from backlogops.table_create import create_output_table
from backlogops.release_backlog_updates import ReleaseChanges, \
    ReleaseDateChanges

CONTENT_HEADER = ['backlog_key', 'old_release', 'new_release']
"""Column names of a release content change table."""

DATE_HEADER = ['release', 'old_date', 'new_date']
"""Column names of a release date change table."""


def _text(value: Optional[str]) -> str:
    """Return a release name for display, or ``(none)`` when absent."""
    return value if value is not None else '(none)'


def _date_text(value: Optional[date]) -> str:
    """Return a date for display, or ``(none)`` when absent."""
    return value.isoformat() if value is not None else '(none)'


def _listing(title: str, empty: str, rows: Sequence[str]) -> str:
    """Return a titled multi line listing, or the empty message."""
    if not rows:
        return empty
    return '\n'.join([title, *rows])


def format_content_changes(changes: ReleaseChanges) -> str:
    """Return release content changes as text for the console."""
    rows = [f'  {change.backlog_key}: {_text(change.old_release)} -> '
            f'{_text(change.new_release)}' for change in changes]
    return _listing('Release content changes:', 'No release content changes.',
                    rows)


def format_date_changes(changes: ReleaseDateChanges) -> str:
    """Return release date changes as text for the console."""
    rows = [f'  {change.release}: {_date_text(change.old_date)} -> '
            f'{_date_text(change.new_date)}' for change in changes]
    return _listing('Release date changes:', 'No release date changes.', rows)


def _date_cell(value: Optional[date]) -> Value:
    """Return a date as an ISO string cell, or None when absent."""
    return value.isoformat() if value is not None else None


def _ensure_absent(file_name: PathOrStr, stderr_file: TextIO) -> None:
    """Raise ``FileExistsError`` when the target file already exists."""
    if Path(file_name).exists():
        message = f'File already exists: {file_name}'
        print(message, file=stderr_file)
        raise FileExistsError(message)


def _write_table(header: list[str], rows: list[list[Value]],
                 file_name: PathOrStr, stderr_file: TextIO) -> None:
    """Write a header row and the change rows as a one table file.

    The rows are written with list writing, so the header is the first
    data row. An empty change list still writes the header row, recording
    that there were no changes.
    """
    _ensure_absent(file_name, stderr_file)
    with create_output_table(file_name, stderr_file) as tableio:
        tableio.write_table_listdata([header, *rows])


def write_content_changes(changes: ReleaseChanges, file_name: PathOrStr,
                          stderr_file: TextIO = sys.stderr) -> None:
    """Write release content changes to a one table file.

    The file format is chosen from the file name extension, as for any
    TableIO table. The single table has the columns ``backlog_key``,
    ``old_release`` and ``new_release``; an absent release is an empty
    cell.

    Args:
        changes: The release content changes to write, in order.
        file_name: The file to create.
        stderr_file: The stream to report errors to.

    Raises:
        FileExistsError: If the file already exists.
        ValueError: If the extension is not a supported table format.
    """
    rows: list[list[Value]] = \
        [[change.backlog_key, change.old_release, change.new_release]
         for change in changes]
    _write_table(CONTENT_HEADER, rows, file_name, stderr_file)


def write_date_changes(changes: ReleaseDateChanges, file_name: PathOrStr,
                       stderr_file: TextIO = sys.stderr) -> None:
    """Write release date changes to a one table file.

    The file format is chosen from the file name extension, as for any
    TableIO table. The single table has the columns ``release``,
    ``old_date`` and ``new_date``; an absent date is an empty cell.

    Args:
        changes: The release date changes to write, in order.
        file_name: The file to create.
        stderr_file: The stream to report errors to.

    Raises:
        FileExistsError: If the file already exists.
        ValueError: If the extension is not a supported table format.
    """
    rows: list[list[Value]] = \
        [[change.release, _date_cell(change.old_date),
          _date_cell(change.new_date)] for change in changes]
    _write_table(DATE_HEADER, rows, file_name, stderr_file)
