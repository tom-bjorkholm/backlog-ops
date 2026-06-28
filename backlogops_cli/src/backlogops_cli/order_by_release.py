#! /usr/local/bin/python3
"""Order the backlog to follow the release order and write the result.

The command reads a backlog and its releases from an input file and orders
the backlog items so that they follow the order of the releases. The
releases are taken in their current file order and are written back
unchanged; order the releases first (for example with the order_releases
command) when a date order is wanted. By default the items are only grouped
by release, keeping their original relative order within a release. With
``--honor-deps`` no item is placed before an item that must be delivered
before it. The input and output formats are inferred from the file name
extensions, but can be overridden by a configuration file or by a named
preset.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from backlogops import BacklogOpsConfig, BacklogReleases
from backlogops_cli._command_io import (
    build_io_parser, parsed_args, read_input, run_write)

DESCRIPTION = 'Order the backlog to follow the release order'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the order_by_release command."""
    parser = build_io_parser(DESCRIPTION)
    parser.add_argument('-d', '--honor-deps', dest='honor_deps',
                        action='store_true',
                        help='Never place an item before an item that must '
                        'be delivered before it (a child before its parent, '
                        'or a finish dependency before its dependent).')
    return parser


def _ordered(parsed: argparse.Namespace,
             config: Optional[BacklogOpsConfig]) -> BacklogReleases:
    """Read the data and order the backlog by the release order."""
    data = read_input(parsed, config)
    data.backlog_in_release_order(honor_dependencies=parsed.honor_deps)
    return data


def main(args: Optional[list[str]] = None) -> int:
    """Order the backlog by release order and write the output file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read, ordered or
        written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_write(parsed, lambda config: _ordered(parsed, config))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
