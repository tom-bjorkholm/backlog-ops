#! /usr/local/bin/python3
"""Read a backlog and releases from one file and write them to another.

The command reads a backlog, releases, or both from an input file and
writes them to an output file, possibly in another format and with other
column names. The input and output formats are inferred from the file
name extensions, but can be overridden by a configuration file or by a
named preset stored in the teams configuration file.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from backlogops_cli._command_io import (
    add_input_args, add_output_args, parsed_args, read_input, run_write)

DESCRIPTION = 'Convert a backlog and releases between table file formats'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the convert command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_input_args(parser)
    add_output_args(parser)
    return parser


def main(args: Optional[list[str]] = None) -> int:
    """Convert a backlog and releases from the input to the output file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read, validated
        or written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_write(parsed, lambda: read_input(parsed))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
