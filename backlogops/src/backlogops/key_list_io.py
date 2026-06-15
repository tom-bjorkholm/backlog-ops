#! /usr/bin/env python3
"""IO for key lists."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import TextIO
from collections.abc import Sequence
import sys
from config_as_json import PathOrStr


def read_key_list(file_name: PathOrStr, *, skip_column_names: bool = False,
                  stderr_file: TextIO = sys.stderr) -> list[str]:
    """Read a key list from a file.

    Read a key list from a file.

    The file type is determined by the file extension. If the file extension
    is .txt or .dat, the file is read as a text file, using utf-8 encoding.
    If skip_column_names is False a text file every work found in the text
    file is added to the key list in the order they appear in the file.
    If skip_column_names is True the first line of the text file is skipped,
    and the first word in each subsequent line is added to the key list.

    If the file extension is one of the supported tableio file extensions,
    the file is read as a table and the first column is read as the key list.

    Args:
        file_name: The name of the file to read the key list from.
        skip_column_names: Whether to skip the first line of the text file.
        stderr_file: The file to report errors to.

    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the file is a directory.
        PermissionError: If the file is not readable.
        ValueError: If the file is not a valid key list file.
                    If the file is a table with more than one column.
        UnicodeDecodeError: If the file is not a valid UTF-8 encoded text file.

    Returns:
        The key list.
    """
    # implement this
    return []


def write_key_list(key_list: Sequence[str], file_name: PathOrStr, *,
                   add_column_name: bool = False,
                   stderr_file: TextIO = sys.stderr) -> None:
    """Write a key list to a file.

    Write a key list to a file.
    The file type is determined by the file extension. If the file extension
    is .txt or .dat, the file is written as a text file, using utf-8 encoding.
    The key list is written to the file one per line in the order of the keys.

    If the file extension is one of the supported tableio file extensions,
    the key list is written as a table with only one column.

    If add_column_name is True the first row of the table or text file is the
    column name "Keys".

    Args:
        key_list: The key list to write.
        file_name: The name of the file to write the key list to.
        add_column_names: Whether to add the column name "Keys"
                          as the first row of the table or text file.
        stderr_file: The file to report errors to.

    Raises:
        FileExistsError: If the file already exists.
        IsADirectoryError: If the file is a directory.
        PermissionError: If the file is not writable.
    """
    # implement this
