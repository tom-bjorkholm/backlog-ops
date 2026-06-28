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
from typing import Callable, Optional
from backlogops import AvailableTeams, BacklogReleases, \
    get_backlog_ops_config
from backlogops_cli._migrate_warn import CliMigrateWarnHook
from backlogops_cli._command_io import (
    add_changes_arg, add_input_args, add_output_args, date_report,
    overwrite_callback, parsed_args, run_change_command)

DESCRIPTION = 'Estimate ready dates for the backlog items'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the estimate command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_input_args(parser)
    parser.add_argument('-c', '--config', dest='config',
                        help='Teams configuration file (velocity, work '
                        'hours, vacations). Without -c the file is found '
                        'from $BACKLOGOPS_CFG, else backlogops.cfg in '
                        '$BACKLOGOPS_DIR, else $HOME/.backlogops.cfg.')
    parser.add_argument('-d', '--start-date', dest='start_date',
                        metavar='ISO_DATE',
                        help='Day the teams start working (default today).')
    parser.add_argument('--set-plan', dest='set_plan', action='store_true',
                        help='Also copy each estimated date to the planned '
                        'date.')
    add_output_args(parser)
    add_changes_arg(parser)
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
        return get_backlog_ops_config(
            config, auto_ch_hook=CliMigrateWarnHook()).available_teams
    except RuntimeError as error:
        raise ValueError(str(error)) from error


def _estimate(parsed: argparse.Namespace, data: BacklogReleases
              ) -> tuple[str, Optional[Callable[[str], None]]]:
    """Estimate the dates and return the release date change report."""
    teams = _load_teams(parsed.config)
    changes = data.estimate_ready_date(teams, _start_date(parsed))
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
    return run_change_command(parsed, lambda data: _estimate(parsed, data))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
