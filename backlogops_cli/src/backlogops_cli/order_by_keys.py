#! /usr/local/bin/python3
"""Reorder a backlog from a key list and write the result.

The command reads a backlog and its releases from an input file, reads a
key list from another file, and reorders the backlog so that the items
named by the key list come first, as documented for
:func:`backlogops.move_keys_first`. The reordered backlog and the
releases are written to the output file. The input and output formats are
inferred from the file name extensions, but can be overridden by a
configuration file or by a named preset.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from backlogops import BacklogOpsConfig, BacklogReleases, read_key_list
from backlogops_cli._command_io import (
    build_io_parser, parsed_args, read_input, run_write)

DESCRIPTION = 'Reorder a backlog so that key-list items come first'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the order_by_keys command."""
    parser = build_io_parser(DESCRIPTION)
    parser.add_argument('-k', '--key-list', dest='key_list', required=True,
                        help='Key list file giving the new leading order.')
    return parser


def _reordered(parsed: argparse.Namespace,
               config: Optional[BacklogOpsConfig]) -> BacklogReleases:
    """Read the backlog and key list and return the reordered data."""
    data = read_input(parsed, config)
    data.move_keys_first(read_key_list(parsed.key_list))
    return data


def main(args: Optional[list[str]] = None) -> int:
    """Reorder the backlog from the key list and write the output file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read, reordered
        or written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_write(parsed, lambda config: _reordered(parsed, config))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
