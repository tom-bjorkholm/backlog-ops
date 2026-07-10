#! /usr/local/bin/python3
"""Read a release name list as its own file.

A name list is an ordered list of Jira release names stored on its own,
separate from the backlog. The file format is chosen from the file name
extension: a ``.txt`` or ``.dat`` file is plain UTF-8 text with one release
name per line, and any extension that TableIO supports (such as ``.csv``,
``.ods`` or ``.xlsx``) is a one column table whose only column holds the
names.

A release name may contain spaces, so a text file gives each name its own
line rather than splitting on whitespace. A blank line is skipped and the
whitespace around a name is removed. This is what separates a name list from
a key list, whose text form splits on whitespace because a key never holds a
space. A table name list is read exactly like a one column key list.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from pathlib import Path
from typing import TextIO
from config_as_json import PathOrStr
from backlogops.key_list_io import TEXT_EXTENSIONS, read_key_list


def _is_text(file_name: PathOrStr) -> bool:
    """Return whether a name list file is plain text rather than a table."""
    return Path(file_name).suffix.lower() in TEXT_EXTENSIONS


def _read_text(file_name: PathOrStr) -> list[str]:
    """Return one release name per non-blank line of a plain text file."""
    text = Path(file_name).read_text(encoding='utf-8')
    names = (line.strip() for line in text.splitlines())
    return [name for name in names if name]


def read_name_list(file_name: PathOrStr, *,
                   stderr_file: TextIO = sys.stderr) -> list[str]:
    """Read a release name list from a file.

    The file type is chosen from the file name extension. A ``.txt`` or
    ``.dat`` file is read as UTF-8 text with one release name per line, so a
    name may contain spaces; a blank line is skipped and the surrounding
    whitespace is trimmed. Any other extension is read as a one column
    TableIO table, the same as a one column key list, so every non empty
    cell is a name.

    Args:
        file_name: The file to read the name list from.
        stderr_file: The stream to report errors to.

    Returns:
        The release names in the order they appear in the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the file is a directory.
        PermissionError: If the file is not readable.
        UnicodeDecodeError: If a text file is not valid UTF-8.
        ValueError: If a table has more than one column, or if the
            extension is not a supported table format.
    """
    if _is_text(file_name):
        return _read_text(file_name)
    return read_key_list(file_name, stderr_file=stderr_file)
