#! /usr/local/bin/python3
"""Estimate ready dates for a backlog and write the result.

The command reads a backlog and its releases from an input file and
estimates the ready date of each backlog item from the available teams,
as documented for :func:`backlogops.estimate_ready_date`. The teams
configuration (velocity, work hours, vacations and so on) is taken from
the file given by ``--config`` or, when that is absent, from the
configured backlog-ops file. The backlog with the estimated dates and the
releases are written to the output file. The input and output formats are
inferred from the file name extensions, but can be overridden by a
configuration file or by a named preset.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from datetime import date
from functools import partial
from typing import Callable, Optional
from backlogops import BacklogOpsConfig, BacklogReleases
from backlogops_cli._command_io import (
    add_changes_arg, build_io_parser, date_report, overwrite_callback,
    parsed_args, run_change_command)

DESCRIPTION = 'Estimate ready dates for the backlog items'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the estimate command."""
    parser = build_io_parser(DESCRIPTION)
    parser.add_argument('-d', '--start-date', dest='start_date',
                        metavar='ISO_DATE',
                        help='Day the teams start working (default today).')
    parser.add_argument('--set-plan', dest='set_plan', action='store_true',
                        help='Also copy each estimated date to the planned '
                        'date.')
    add_changes_arg(parser)
    return parser


def _start_date(parsed: argparse.Namespace) -> Optional[date]:
    """Return the start date from the command line, or None for today."""
    if parsed.start_date is None:
        return None
    return date.fromisoformat(parsed.start_date)


def _estimate(parsed: argparse.Namespace, config: Optional[BacklogOpsConfig],
              data: BacklogReleases
              ) -> tuple[str, Optional[Callable[[str], None]]]:
    """Estimate the dates and return the release date change report.

    The configuration is required for this command, so ``config`` is never
    None here; the assertion makes that explicit for the type checker.
    """
    assert isinstance(config, BacklogOpsConfig)
    changes = data.estimate_ready_date(config.available_teams,
                                       _start_date(parsed))
    if parsed.set_plan:
        data.set_plan_from_estimate()
    return date_report(changes, overwrite_callback(parsed.force))


def main(args: Optional[list[str]] = None) -> int:
    """Estimate the ready dates and write the output file.

    The backlog with the estimated dates and the releases are written to
    the output file. The estimated release dates are updated as well, and
    the list of release date changes is printed to stdout, or also saved
    to a file when ``--changes-file`` is given.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read, estimated
        or written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_change_command(parsed, partial(_estimate, parsed),
                              require_config=True)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
