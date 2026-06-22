#! /usr/local/bin/python3
"""Order the releases by date and write the result.

The command reads a backlog and its releases from an input file and orders
the releases by their planned date, or by their estimated date when
``--by-estimated`` is given. A release with no date of the chosen kind is
placed at the end, and releases that share a date keep their original
order. The backlog is written back unchanged together with the ordered
releases. The input and output formats are inferred from the file name
extensions, but can be overridden by a configuration file or by a named
preset.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from backlogops import BacklogReleases
from backlogops_cli._command_io import (
    add_input_args, add_output_args, parsed_args, read_input, run_write)

DESCRIPTION = 'Order the releases by their planned or estimated date'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the order_releases command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_input_args(parser)
    parser.add_argument('-e', '--by-estimated', dest='by_estimated',
                        action='store_true',
                        help='Order by the estimated date instead of the '
                        'planned date.')
    add_output_args(parser)
    return parser


def _ordered(parsed: argparse.Namespace) -> BacklogReleases:
    """Read the data and return it with the releases ordered by date."""
    data = read_input(parsed)
    data.order_releases_by_date(by_estimated=parsed.by_estimated)
    return data


def main(args: Optional[list[str]] = None) -> int:
    """Order the releases by date and write the output file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read, ordered or
        written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_write(parsed, lambda: _ordered(parsed))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
