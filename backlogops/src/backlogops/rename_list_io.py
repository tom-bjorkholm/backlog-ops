#! /usr/local/bin/python3
"""Read a release rename list as its own two column file.

A rename list pairs an old release name with the new name it should get.
The file format is chosen from the file name extension: a ``.txt`` or
``.dat`` file is plain UTF-8 text with one rename per line, the old and new
name separated by a tab, and any extension that TableIO supports (such as
``.csv``, ``.ods`` or ``.xlsx``) is a two column table whose first column
holds the old names and second column the new names.

A blank line, or a table row whose two cells are both empty, is skipped, so
trailing empty rows a spreadsheet leaves are ignored. A tab is used to
separate the two text fields because a release name may contain spaces but
not a tab. Leading and trailing whitespace around a name is removed.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from pathlib import Path
from typing import Optional, TextIO
from config_as_json import PathOrStr
from tableio import ListData, Value
from backlogops.backlog_helpers import report_bad_value
from backlogops.jira_rename_releases import ReleaseRename
from backlogops.key_list_io import TEXT_EXTENSIONS
from backlogops.table_create import open_input_table


def _is_text(file_name: PathOrStr) -> bool:
    """Return whether a rename list file is plain text rather than a table."""
    return Path(file_name).suffix.lower() in TEXT_EXTENSIONS


def _text_rename(line: str, stderr_file: TextIO) -> Optional[ReleaseRename]:
    """Return the rename on one text line, or None for a blank line."""
    if not line.strip():
        return None
    fields = [field.strip() for field in line.split('\t')]
    if len(fields) != 2 or not fields[0] or not fields[1]:
        report_bad_value('rename', line.strip(),
                         'a rename line needs an old and a new name '
                         'separated by a tab', stderr_file, 'Rename list')
    return ReleaseRename(fields[0], fields[1])


def _read_text(file_name: PathOrStr,
               stderr_file: TextIO) -> list[ReleaseRename]:
    """Return the renames of a plain text rename list file."""
    text = Path(file_name).read_text(encoding='utf-8')
    renames: list[ReleaseRename] = []
    for line in text.splitlines():
        rename = _text_rename(line, stderr_file)
        if rename is not None:
            renames.append(rename)
    return renames


def _check_two_columns(width: int, stderr_file: TextIO) -> None:
    """Report a table that does not have exactly two columns."""
    if width != 2:
        report_bad_value('columns', width,
                         'a rename table must have exactly two columns',
                         stderr_file, 'Rename list')


def _cell(value: Value) -> str:
    """Return a table cell as a stripped string, empty for a None cell."""
    return '' if value is None else str(value).strip()


def _table_rename(row: list[Value],
                  stderr_file: TextIO) -> Optional[ReleaseRename]:
    """Return the rename in one table row, or None for an empty row.

    A shorter row (such as a blank row a spreadsheet leaves) is read as
    empty cells, so it is skipped rather than causing an index error.
    """
    old = _cell(row[0]) if len(row) > 0 else ''
    new = _cell(row[1]) if len(row) > 1 else ''
    if not old and not new:
        return None
    if not old or not new:
        report_bad_value('rename', f'{old!r}, {new!r}',
                         'a rename row needs both an old and a new name',
                         stderr_file, 'Rename list')
    return ReleaseRename(old, new)


def _read_table(file_name: PathOrStr,
                stderr_file: TextIO) -> list[ReleaseRename]:
    """Return the renames of a rename list stored as a two column table."""
    with open_input_table(file_name, stderr_file) as tableio:
        rows: ListData[Value] = tableio.read_table_listdata().data
    if not rows:
        return []
    _check_two_columns(len(rows[0]), stderr_file)
    renames: list[ReleaseRename] = []
    for row in rows:
        rename = _table_rename(row, stderr_file)
        if rename is not None:
            renames.append(rename)
    return renames


def read_renames(file_name: PathOrStr, *,
                 stderr_file: TextIO = sys.stderr) -> list[ReleaseRename]:
    """Read a release rename list from a file.

    The file type is chosen from the file name extension. A ``.txt`` or
    ``.dat`` file is read as UTF-8 text with one tab-separated old and new
    name per line; any other extension is read as a two column TableIO
    table. A blank line, or a row whose two cells are both empty, is
    skipped.

    Args:
        file_name: The file to read the rename list from.
        stderr_file: The stream to report errors to.

    Returns:
        The renames in the order they appear in the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the file is a directory.
        PermissionError: If the file is not readable.
        UnicodeDecodeError: If a text file is not valid UTF-8.
        ValueError: If a line or row does not hold both an old and a new
            name, if a table does not have exactly two columns, or if the
            extension is not a supported table format.
    """
    if _is_text(file_name):
        return _read_text(file_name, stderr_file)
    return _read_table(file_name, stderr_file)
