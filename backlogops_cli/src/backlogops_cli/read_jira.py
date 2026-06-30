#! /usr/local/bin/python3
"""Read a backlog and its releases from Jira and store them to a file.

The command reads the backlog items and the releases from Jira using a
named from-Jira preset of the backlog-ops configuration, then writes them
to an output file like the other commands (the output format is inferred
from the file name or taken from an output preset or config file).

The ``--preset`` flag names the Jira preset to use; the optional
``--filter`` flag supplies a Jira Query Language filter to use instead of
the preset's default. An encrypted Jira token is unlocked by a pass
phrase asked on the terminal only when it is needed.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from getpass import getpass
from typing import Optional
from backlogops import (
    BacklogOpsConfig, BacklogReleases, read_jira_from_config)
from backlogops_cli._command_io import (
    build_io_parser, parsed_args, run_write)

DESCRIPTION = 'Read a backlog and releases from Jira and store to a file'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the read-from-Jira command."""
    parser = build_io_parser(DESCRIPTION, with_input=False)
    parser.add_argument('-p', '--preset', dest='preset', required=True,
                        help='Name of the from-Jira preset in the '
                        'configuration.')
    parser.add_argument('--filter', dest='filter', metavar='JQL',
                        help='Jira filter to use instead of the preset '
                        'default.')
    return parser


def _passphrase() -> str:
    """Ask for the Jira token pass phrase on the terminal."""
    return getpass('Jira API token pass phrase: ')


def _warn_if_inconsistent(data: BacklogReleases) -> None:
    """Warn when the data read from Jira is not fully consistent.

    A filtered read can leave a cross reference dangling, for example a
    parent or release that the filter excluded. The problem is reported
    but the file is still written, so a partial read still produces output.
    """
    try:
        data.check_consistency(sys.stderr)
    except (TypeError, ValueError, KeyError):
        print('Warning: the data read from Jira is not fully consistent '
              '(see above); writing the file anyway.', file=sys.stderr)


def _read_jira(parsed: argparse.Namespace,
               config: Optional[BacklogOpsConfig]) -> BacklogReleases:
    """Read the backlog and releases from Jira for the named preset."""
    assert isinstance(config, BacklogOpsConfig)
    print(f"Reading from Jira using preset '{parsed.preset}'...",
          file=sys.stderr)
    data = read_jira_from_config(config, parsed.preset,
                                 filter_override=parsed.filter,
                                 passphrase=_passphrase)
    print(f'Read {len(data.backlog)} backlog items and '
          f'{len(data.releases)} releases from Jira.', file=sys.stderr)
    _warn_if_inconsistent(data)
    return data


def main(args: Optional[list[str]] = None) -> int:
    """Read a backlog and releases from Jira and write them to a file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read or written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_write(parsed, lambda config: _read_jira(parsed, config),
                     require_config=True)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
