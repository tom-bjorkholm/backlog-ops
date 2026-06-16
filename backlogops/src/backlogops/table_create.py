#! /usr/local/bin/python3
"""Open a TableIO file for creating a single table output.

Several writers create a file that holds one table whose format follows
the file name extension (a key list, a list of changes, and so on). They
all resolve the output configuration from the file name, request CREATE
capabilities, and open a TableIO context. This helper holds that shared
setup so each writer only describes the rows it writes.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TextIO
from config_as_json import PathOrStr
from tableio import FileAccess, TableIO, access_capabilities, \
    tio_config_create
from backlogops.io_config import resolve_output_config


@contextmanager
def create_output_table(file_name: PathOrStr,
                        stderr_file: TextIO = sys.stderr) -> Iterator[TableIO]:
    """Yield a TableIO opened to create a one table file.

    The output format is resolved from the file name extension and the
    file is opened with CREATE access. The yielded TableIO is used to
    write the table inside the ``with`` block.

    Args:
        file_name: The file to create.
        stderr_file: The stream to report errors to.

    Yields:
        The TableIO ready to write one table to the file.
    """
    config = resolve_output_config(None, data_file=file_name,
                                   stderr_file=stderr_file).tableio
    capabilities = access_capabilities(FileAccess.CREATE,
                                       error_file=stderr_file)
    with tio_config_create(config=config, file_name=file_name,
                           file_access=FileAccess.CREATE,
                           capabilities=capabilities) as tableio:
        yield tableio
