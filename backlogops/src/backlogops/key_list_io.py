#! /usr/bin/env python3
"""Read and write a key list as its own file.

A key list is an ordered list of backlog item keys stored on its own,
separate from the backlog. The file format is chosen from the file name
extension: a ``.txt`` or ``.dat`` file is plain UTF-8 text, and any
extension that TableIO supports (such as ``.csv``, ``.ods`` or ``.xlsx``)
is a one column table.

Two options apply to both shapes and describe whether the file carries a
column name. ``skip_column_names`` tells the reader that the first
row/line is a column name to skip, and ``add_column_name`` tells the
writer to write such a column name (``Keys``).

For a text file without a column name every whitespace separated word is
a key, in the order the words appear; with a column name the heading line
is skipped and every following non empty line holds exactly one key.

For a table file without a column name every row is data (read with list
reading); with a column name the first row names the column (read with
dict reading). A single column table usually has no column name, but it
may have one. Either way the table must have exactly one column.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Optional, TextIO
from collections.abc import Sequence
import sys
from config_as_json import PathOrStr
from tableio import DictData, ListData, Value
from backlogops.backlog_helpers import report_bad_value
from backlogops.table_create import (
    FileExistsCb, create_output_table, open_input_table)

TEXT_EXTENSIONS = {'.txt', '.dat'}
"""File name extensions read and written as plain UTF-8 text."""

KEY_COLUMN_NAME = 'Keys'
"""Column name of the single column of a key list table."""


def _is_text(file_name: PathOrStr) -> bool:
    """Return whether a key list file is plain text rather than a table."""
    return Path(file_name).suffix.lower() in TEXT_EXTENSIONS


def _column_keys(text: str, stderr_file: TextIO) -> list[str]:
    """Return one key per line of a column text file, after the heading.

    The first line is the column heading and is skipped. Every following
    non empty line must hold exactly one word, which is the key.
    """
    keys: list[str] = []
    for line in text.splitlines()[1:]:
        words = line.split()
        if not words:
            continue
        if len(words) > 1:
            report_bad_value('key', line.strip(),
                             'a column key list allows only one key per line',
                             stderr_file, 'Key list')
        keys.append(words[0])
    return keys


def _read_text(file_name: PathOrStr, skip_column_names: bool,
               stderr_file: TextIO) -> list[str]:
    """Return the keys of a plain text key list file."""
    text = Path(file_name).read_text(encoding='utf-8')
    if skip_column_names:
        return _column_keys(text, stderr_file)
    return text.split()


def _check_one_column(width: int, stderr_file: TextIO) -> None:
    """Report a table that does not have exactly one column."""
    if width > 1:
        report_bad_value('columns', width,
                         'a key list table must have exactly one column',
                         stderr_file, 'Key list')


def _cell_keys(values: list[Value]) -> list[str]:
    """Return the non empty cell values of one table column as strings."""
    return [str(value) for value in values
            if value is not None and str(value) != '']


def _keys_from_dict(rows: DictData[Value], stderr_file: TextIO) -> list[str]:
    """Return the keys of a one column table read with dict reading."""
    if not rows:
        return []
    _check_one_column(len(rows[0]), stderr_file)
    column = next(iter(rows[0]))
    return _cell_keys([row[column] for row in rows])


def _keys_from_list(rows: ListData[Value], stderr_file: TextIO) -> list[str]:
    """Return the keys of a one column table read with list reading."""
    if not rows:
        return []
    _check_one_column(len(rows[0]), stderr_file)
    return _cell_keys([row[0] for row in rows])


def _read_table(file_name: PathOrStr, skip_column_names: bool,
                stderr_file: TextIO) -> list[str]:
    """Return the keys of a key list stored as a one column table."""
    with open_input_table(file_name, stderr_file) as tableio:
        if skip_column_names:
            keys = _keys_from_dict(tableio.read_table_dictdata().data,
                                   stderr_file)
        else:
            keys = _keys_from_list(tableio.read_table_listdata().data,
                                   stderr_file)
    return keys


def read_key_list(file_name: PathOrStr, *, skip_column_names: bool = False,
                  stderr_file: TextIO = sys.stderr) -> list[str]:
    """Read a key list from a file.

    The file type is chosen from the file name extension. A ``.txt`` or
    ``.dat`` file is read as UTF-8 text; any other extension is read as a
    TableIO table whose single column holds the keys.

    ``skip_column_names`` tells whether the file starts with a column
    name. For a text file, when it is False the file is a free word list
    and every whitespace separated word is a key, in the order the words
    appear; when it is True the first line is a column heading and is
    skipped, and every following non empty line must hold exactly one
    word, which is a key. For a table file, when it is False every row is
    data (list reading); when it is True the first row names the column
    and is skipped (dict reading). A table must have exactly one column.

    Args:
        file_name: The file to read the key list from.
        skip_column_names: Whether the file starts with a column name to
            skip.
        stderr_file: The stream to report errors to.

    Returns:
        The keys in the order they appear in the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the file is a directory.
        PermissionError: If the file is not readable.
        UnicodeDecodeError: If a text file is not valid UTF-8.
        ValueError: If a column text line holds more than one word, if a
            table has more than one column, or if the extension is not a
            supported table format.
    """
    if _is_text(file_name):
        return _read_text(file_name, skip_column_names, stderr_file)
    return _read_table(file_name, skip_column_names, stderr_file)


def _ensure_absent(file_name: PathOrStr, stderr_file: TextIO,
                   file_exists_callback: Optional[FileExistsCb]) -> None:
    """Handle an existing target file before a plain text write.

    When the file is absent nothing happens. When it exists the
    ``file_exists_callback`` decides: returning allows the overwrite and
    raising refuses it. Without a callback an existing file is refused
    with ``FileExistsError``.
    """
    if not Path(file_name).exists():
        return
    if file_exists_callback is not None:
        file_exists_callback(str(file_name))
        return
    message = f'File already exists: {file_name}'
    print(message, file=stderr_file)
    raise FileExistsError(message)


def _write_text(key_list: Sequence[str], file_name: PathOrStr,
                add_column_name: bool) -> None:
    """Write a key list as plain text, one key per line."""
    lines = [KEY_COLUMN_NAME, *key_list] if add_column_name else list(key_list)
    text = ''.join(f'{line}\n' for line in lines)
    Path(file_name).write_text(text, encoding='utf-8')


def _write_table(key_list: Sequence[str], file_name: PathOrStr,
                 add_column_name: bool, stderr_file: TextIO,
                 file_exists_callback: Optional[FileExistsCb]) -> None:
    """Write a key list as a one column TableIO table."""
    with create_output_table(file_name, stderr_file,
                             file_exists_callback) as tableio:
        if add_column_name:
            dict_rows: DictData[Value] = [{KEY_COLUMN_NAME: key}
                                          for key in key_list]
            tableio.write_table_dictdata(dict_rows,
                                         column_order=[KEY_COLUMN_NAME])
        else:
            tableio.write_table_listdata([[key] for key in key_list])


def write_key_list(key_list: Sequence[str], file_name: PathOrStr, *,
                   add_column_name: bool = False,
                   stderr_file: TextIO = sys.stderr,
                   file_exists_callback: Optional[FileExistsCb]
                   = None) -> None:
    """Write a key list to a file.

    The file type is chosen from the file name extension. A ``.txt`` or
    ``.dat`` file is written as UTF-8 text with one key per line; any
    other extension is written as a TableIO table with a single column.

    ``add_column_name`` decides whether the column name ``Keys`` is
    written before the keys: as a heading line for a text file, and as a
    header row for a table file. When it is False a text file holds only
    the keys and a table file holds only data rows (list writing).

    Args:
        key_list: The keys to write, in order.
        file_name: The file to create.
        add_column_name: Whether to write the column name ``Keys`` first.
        stderr_file: The stream to report errors to.
        file_exists_callback: Called when the file already exists, as
                              documented for :mod:`backlogops.table_create`.
                              None refuses an existing file.

    Raises:
        FileExistsError: If the file exists and the callback refuses it.
        IsADirectoryError: If the file is a directory.
        PermissionError: If the file is not writable.
        ValueError: If the extension is not a supported table format.
    """
    if _is_text(file_name):
        _ensure_absent(file_name, stderr_file, file_exists_callback)
        _write_text(key_list, file_name, add_column_name)
    else:
        _write_table(key_list, file_name, add_column_name, stderr_file,
                     file_exists_callback)
