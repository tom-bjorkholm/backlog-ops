#! /usr/local/bin/python3
"""Write a demonstration backlog and releases to a file.

The data comes from :func:`backlogops.get_demo_backlog`. The output
format is inferred from the output file name extension, but can be
overridden by a configuration file or by a named preset stored in the
teams configuration file.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from backlogops import get_demo_backlog
from backlogops_cli._command_io import add_output_args, parsed_args, run_write

DESCRIPTION = 'Write a demonstration backlog and releases to a file'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the demo backlog command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_output_args(parser)
    return parser


def main(args: Optional[list[str]] = None) -> int:
    """Write the demonstration backlog and releases to the output file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_write(parsed, get_demo_backlog)


if __name__ == '__main__':
    sys.exit(main())
