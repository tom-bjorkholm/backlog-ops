#! /usr/local/bin/python3
"""Estimate ready dates for a backlog and write the result.

The command reads a backlog and its releases from an input file and
estimates the ready date of each backlog item from the available teams,
as documented for :func:`backlogops.estimate_ready_date`. The teams
configuration (velocity, work hours, vacations and so on) is taken from
the file given by ``--config`` or, when that is absent, from the
configured teams file. The backlog with the estimated dates and the
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
from pathlib import Path
from typing import Optional
from backlogops import AvailableTeams, BacklogReleases, get_available_teams
from backlogops_cli._command_io import (
    add_input_args, add_output_args, parsed_args, read_input, run_write)

DESCRIPTION = 'Estimate ready dates for the backlog items'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the estimate command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_input_args(parser)
    parser.add_argument('-c', '--config', dest='config',
                        help='Teams configuration file (velocity, work '
                        'hours, vacations). Default: the configured file.')
    parser.add_argument('-d', '--start-date', dest='start_date',
                        metavar='ISO_DATE',
                        help='Day the teams start working (default today).')
    parser.add_argument('--set-plan', dest='set_plan', action='store_true',
                        help='Also copy each estimated date to the planned '
                        'date.')
    add_output_args(parser)
    return parser


def _start_date(parsed: argparse.Namespace) -> Optional[date]:
    """Return the start date from the command line, or None for today."""
    if parsed.start_date is None:
        return None
    return date.fromisoformat(parsed.start_date)


def _load_teams(config: Optional[str]) -> AvailableTeams:
    """Return the available teams, mapping a missing file to ValueError."""
    if config is not None and not Path(config).is_file():
        raise ValueError(f'Teams configuration file not found: {config}')
    try:
        return get_available_teams(config)
    except RuntimeError as error:
        raise ValueError(str(error)) from error


def _estimated(parsed: argparse.Namespace) -> BacklogReleases:
    """Read the backlog and return it with estimated ready dates."""
    data = read_input(parsed)
    teams = _load_teams(parsed.config)
    data.estimate_ready_date(teams, _start_date(parsed))
    if parsed.set_plan:
        data.set_plan_from_estimate()
    return data


def main(args: Optional[list[str]] = None) -> int:
    """Estimate the ready dates and write the output file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read, estimated
        or written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_write(parsed, lambda: _estimated(parsed))


if __name__ == '__main__':
    sys.exit(main())
