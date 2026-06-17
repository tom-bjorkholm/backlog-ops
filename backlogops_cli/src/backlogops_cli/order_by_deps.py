#! /usr/local/bin/python3
"""Reorder a backlog by its dependencies and write the result.

The command reads a backlog and its releases from an input file and
reorders the backlog so that a team can start the items in backlog order
without starting an item before the items it depends on, as documented
for :func:`backlogops.order_by_dependencies`. The reordered backlog and
the releases are written to the output file. The input and output formats
are inferred from the file name extensions, but can be overridden by a
configuration file or by a named preset.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from backlogops import BacklogReleases, DependencyMode
from backlogops_cli._command_io import (
    add_input_args, add_output_args, parsed_args, read_input, run_write)

DESCRIPTION = 'Reorder a backlog so that dependencies are fulfilled'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the order_by_deps command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_input_args(parser)
    parser.add_argument('-s', '--space-around', dest='space_around',
                        action='append', metavar='KEY',
                        help='Key to keep far from its dependencies. May '
                        'be given more than once.')
    parser.add_argument('-L', '--later', dest='later', action='store_true',
                        help='Push dependent items later instead of pulling '
                        'prerequisites earlier.')
    parser.add_argument('-m', '--mode', dest='mode',
                        choices=[mode.name for mode in DependencyMode],
                        default=DependencyMode.KEEP.name,
                        help='Placement of dependency items (default KEEP).')
    add_output_args(parser)
    return parser


def _ordered(parsed: argparse.Namespace) -> BacklogReleases:
    """Read the backlog and return it reordered by dependencies."""
    data = read_input(parsed)
    data.order_by_dependencies(later=parsed.later,
                               mode=DependencyMode[parsed.mode],
                               space_around=parsed.space_around)
    return data


def main(args: Optional[list[str]] = None) -> int:
    """Reorder the backlog by dependencies and write the output file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read, reordered
        or written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_write(parsed, lambda: _ordered(parsed))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
