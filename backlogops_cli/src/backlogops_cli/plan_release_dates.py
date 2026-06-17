#! /usr/local/bin/python3
"""Set planned release dates from the estimated release dates.

The command reads a backlog and its releases whose estimated release
dates are already filled in, then sets each planned release date to the
estimated release date plus a slack buffer, as documented for
:func:`backlogops.release_plan_on_estimate`. The backlog and the releases
with the new planned dates are written to the output file, and the list of
planned date changes is printed to stdout, or also saved to a file when
``--changes-file`` is given.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from datetime import timedelta
from typing import Callable, Optional
from backlogops import BacklogReleases
from backlogops_cli._command_io import (
    build_change_parser, date_report, parsed_args, run_change_command)

DESCRIPTION = 'Set planned release dates from the estimated release dates'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the plan-dates command."""
    return build_change_parser(DESCRIPTION)


def _plan(parsed: argparse.Namespace, data: BacklogReleases
          ) -> tuple[str, Optional[Callable[[str], None]]]:
    """Set the planned release dates and return the change report."""
    changes = data.release_plan_on_estimate(timedelta(days=parsed.buffer_days))
    return date_report(changes)


def main(args: Optional[list[str]] = None) -> int:
    """Set the planned release dates and write the output file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read, planned or
        written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_change_command(parsed, lambda data: _plan(parsed, data))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
