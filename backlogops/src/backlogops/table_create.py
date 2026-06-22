#! /usr/local/bin/python3
"""Open a TableIO file for creating a single table output.

Several writers create a file that holds one table whose format follows
the file name extension (a key list, a list of changes, and so on). They
all resolve the output configuration from the file name, request CREATE
capabilities, and open a TableIO context. This helper holds that shared
setup so each writer only describes the rows it writes.

The writers accept an optional ``file_exists_callback``. TableIO calls it
with the file name when a CREATE would overwrite an existing file:
returning from the callback allows the overwrite, raising refuses it.
Without a callback an existing file is refused. :func:`allow_overwrite` is
a ready callback that always allows the overwrite.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Callable, Optional, TextIO
from config_as_json import PathOrStr
from tableio import FileAccess, TableIO, access_capabilities, \
    tio_config_create
from backlogops.io_config import resolve_output_config

type FileExistsCb = Callable[[str], None]
"""Callback invoked with the file name when a CREATE would overwrite.

Returning from the callback allows the overwrite; raising refuses it. It
is used as ``Optional[FileExistsCb]`` in the write functions (None refuses
an existing file) and as a plain ``FileExistsCb`` for a concrete callback.
"""


def allow_overwrite(file_name: str) -> None:
    """File-exists callback that always allows overwriting the file."""
    _ = file_name


@contextmanager
def create_output_table(file_name: PathOrStr, stderr_file: TextIO = sys.stderr,
                        file_exists_callback: Optional[FileExistsCb] = None
                        ) -> Iterator[TableIO]:
    """Yield a TableIO opened to create a one table file.

    The output format is resolved from the file name extension and the
    file is opened with CREATE access. The yielded TableIO is used to
    write the table inside the ``with`` block.

    Args:
        file_name: The file to create.
        stderr_file: The stream to report errors to.
        file_exists_callback: Called when the file already exists, as
                              documented for the module. None refuses an
                              existing file.

    Yields:
        The TableIO ready to write one table to the file.
    """
    config = resolve_output_config(None, data_file=file_name,
                                   stderr_file=stderr_file).tableio
    capabilities = access_capabilities(FileAccess.CREATE,
                                       error_file=stderr_file)
    with tio_config_create(config=config, file_name=file_name,
                           file_access=FileAccess.CREATE,
                           capabilities=capabilities,
                           file_exists_callback=file_exists_callback
                           ) as tableio:
        yield tableio
