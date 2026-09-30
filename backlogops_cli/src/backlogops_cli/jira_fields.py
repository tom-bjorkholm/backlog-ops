#! /usr/local/bin/python3
"""Print Jira field information for a preset, to diagnose write mappings.

The command prints the custom field id to display name map that the reader
fetches from Jira, so a column-map name such as 'Story point estimate' can
be matched to its field id. With ``--issue`` it also prints the fields the
given issue's edit screen offers, which explains why a mapped field cannot
be set on that issue's type: a field missing from the edit screen cannot be
set through the issue edit REST endpoint. Each ``--field`` (which needs
``--issue``) prints the raw Jira JSON at a field id or dotted path of that
issue, such as ``timetracking.remainingEstimateSeconds``, and the field's
edit screen entry, so a column map path can be checked against what Jira
really holds and how it may be written.

An encrypted Jira token is unlocked by a pass phrase asked on the terminal
only when it is needed.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import json
import sys
from typing import Optional
from jira import JIRAError
from backlogops import (
    JiraConnections, JiraFieldJson, jira_custom_fields, jira_editable_fields,
    jira_field_json)
from backlogops_cli._command_io import (
    build_jira_parser, jira_passphrase, parsed_args, required_config)

DESCRIPTION = "Print Jira custom fields, an issue's editable fields and JSON"


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the field diagnostic command."""
    parser = build_jira_parser(DESCRIPTION, with_input=False)
    parser.add_argument('--issue', dest='issue', metavar='KEY',
                        help="Also print the fields this issue's edit "
                        'screen offers (for example SCRUM-15).')
    parser.add_argument('--field', dest='fields', action='append',
                        metavar='NAME', default=[],
                        help='Also print the raw Jira JSON of this field of '
                        'the --issue: a field id, a custom field name, or a '
                        'dotted path such as '
                        'timetracking.remainingEstimateSeconds. Repeatable.')
    return parser


def _print_pairs(heading: str, pairs: list[tuple[str, str]]) -> None:
    """Print a heading and each field id and display name pair."""
    print(heading)
    if not pairs:
        print('  (none)')
    for field_id, name in pairs:
        print(f'  {field_id}  {name}')


def _print_json(heading: str, value: object) -> None:
    """Print a heading and the value as indented JSON below it."""
    print(f'  {heading}:')
    text = json.dumps(value, indent=2, ensure_ascii=False, default=str)
    for line in text.splitlines():
        print(f'    {line}')


def _print_field(issue: str, found: JiraFieldJson) -> None:
    """Print one field path's JSON value and its edit screen entry."""
    print(f"\nField '{found.name}' of {issue} (Jira field {found.field_id}):")
    if found.present:
        _print_json('value', found.value)
    else:
        print('  value: (no such path in the issue)')
    if found.edit_entry is None:
        print('  edit screen: (not offered, so not writable by an edit)')
    else:
        _print_json('edit screen', found.edit_entry)


def _read_all(parsed: argparse.Namespace) -> tuple[
        list[tuple[str, str]], Optional[list[tuple[str, str]]],
        list[JiraFieldJson]]:
    """Read the custom fields, edit screen fields and field JSON asked for."""
    config = required_config(parsed)
    connections = JiraConnections(config.get_jira_config(), jira_passphrase)
    customs = jira_custom_fields(connections, parsed.preset)
    if parsed.issue is None:
        return customs, None, []
    editable = jira_editable_fields(connections, parsed.preset, parsed.issue)
    found = jira_field_json(connections, parsed.preset, parsed.issue,
                            parsed.fields)
    return customs, editable, found


def _run(parsed: argparse.Namespace) -> int:
    """Print the custom field map and, optionally, the issue's fields."""
    try:
        customs, editable, found = _read_all(parsed)
    except (ValueError, TypeError, KeyError, OSError, JIRAError) as error:
        print(f'Could not read Jira fields: {error}', file=sys.stderr)
        return 1
    _print_pairs(f"Custom fields for preset '{parsed.preset}':", customs)
    if editable is not None:
        print()
        _print_pairs(f'Fields settable on the edit screen of '
                     f'{parsed.issue}:', editable)
    for field in found:
        _print_field(parsed.issue, field)
    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Print Jira field information for a preset.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the fields cannot be read.

    Raises:
        SystemExit: With status ``2`` when ``--field`` is given without
            ``--issue``, as for any other command line usage error.
    """
    parser = build_parser()
    parsed = parsed_args(parser, args)
    if parsed.fields and parsed.issue is None:
        parser.error('--field needs --issue')
    return _run(parsed)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
