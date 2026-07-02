#! /usr/local/bin/python3
"""Print Jira field information for a preset, to diagnose write mappings.

The command prints the custom field id to display name map that the reader
fetches from Jira, so a column-map name such as 'Story point estimate' can
be matched to its field id. With ``--issue`` it also prints the fields the
given issue's edit screen offers, which explains why a mapped field cannot
be set on that issue's type: a field missing from the edit screen cannot be
set through the issue edit REST endpoint.

An encrypted Jira token is unlocked by a pass phrase asked on the terminal
only when it is needed.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from getpass import getpass
from typing import Optional
from jira import JIRAError
from backlogops import (
    JiraConnections, jira_custom_fields, jira_editable_fields)
from backlogops_cli._command_io import (
    add_config_arg, parsed_args, required_config)

DESCRIPTION = "Print Jira custom fields and an issue's editable fields"


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the field diagnostic command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_config_arg(parser)
    parser.add_argument('-p', '--preset', dest='preset', required=True,
                        help='Name of the Jira preset in the configuration.')
    parser.add_argument('--issue', dest='issue', metavar='KEY',
                        help="Also print the fields this issue's edit "
                        'screen offers (for example SCRUM-15).')
    return parser


def _passphrase() -> str:
    """Ask for the Jira token pass phrase on the terminal."""
    return getpass('Jira API token pass phrase: ')


def _print_pairs(heading: str, pairs: list[tuple[str, str]]) -> None:
    """Print a heading and each field id and display name pair."""
    print(heading)
    if not pairs:
        print('  (none)')
    for field_id, name in pairs:
        print(f'  {field_id}  {name}')


def _run(parsed: argparse.Namespace) -> int:
    """Print the custom field map and, optionally, editable fields."""
    try:
        config = required_config(parsed)
        connections = JiraConnections(config.get_jira_config(), _passphrase)
        customs = jira_custom_fields(connections, parsed.preset)
        editable = (jira_editable_fields(connections, parsed.preset,
                                         parsed.issue)
                    if parsed.issue is not None else None)
    except (ValueError, TypeError, KeyError, OSError, JIRAError) as error:
        print(f'Could not read Jira fields: {error}', file=sys.stderr)
        return 1
    _print_pairs(f"Custom fields for preset '{parsed.preset}':", customs)
    if editable is not None:
        print()
        _print_pairs(f'Fields settable on the edit screen of '
                     f'{parsed.issue}:', editable)
    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Print Jira field information for a preset.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the fields cannot be read.
    """
    return _run(parsed_args(build_parser(), args))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
