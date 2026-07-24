#! /usr/local/bin/python3
"""Add a backlog to Jira from an input file, creating one issue per item.

The command reads a backlog (or a backlog and its releases) from the input
file, then adds the backlog items to Jira using a named preset of the
backlog-ops configuration. By default it stops with an error when an
item's key already exists in Jira; ``--skip-existing`` skips those items
instead. With ``--rank`` the items are also ranked in Jira to match the
supplied backlog order, at the chosen anchor.

The added items (carrying their new Jira keys) and the items already in
Jira are printed to stdout as two labelled lists, unless ``-q``/``--quiet``
is given. Each list is also written to a file when ``--added-file`` or
``--existing-file`` names one; without a file name the list is not written.
An encrypted Jira token is unlocked by a pass phrase asked on the terminal
only when it is needed.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from backlogops import (
    AddedToJira, BacklogOpsConfig, BacklogReleases, ExistsInJiraError,
    JiraConnections, OnExistingKey, add_backlog_to_jira, format_add_result)
from backlogops_cli._command_io import (
    add_force_arg, add_quiet_arg, add_rank_arg, build_jira_parser,
    jira_passphrase, parsed_args, rank_anchor, run_added_to_jira,
    write_result_file)

DESCRIPTION = 'Add a backlog to Jira, creating a new issue per item'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the add-to-Jira command."""
    parser = build_jira_parser(DESCRIPTION)
    parser.add_argument('--skip-existing', dest='skip_existing',
                        action='store_true',
                        help='Skip items whose key already exists in Jira '
                        '(the default stops with an error instead).')
    add_rank_arg(parser)
    parser.add_argument('--added-file', dest='added_file', metavar='FILE',
                        help='Write the added items, with their new Jira '
                        'keys, to this file. Omit to not write it.')
    parser.add_argument('--existing-file', dest='existing_file',
                        metavar='FILE',
                        help='Write the items already in Jira to this file. '
                        'Omit to not write it.')
    add_quiet_arg(parser)
    add_force_arg(parser)
    return parser


def _add(parsed: argparse.Namespace, config: BacklogOpsConfig,
         data: BacklogReleases) -> AddedToJira:
    """Add the input backlog to Jira using the named write preset."""
    print(f"Adding backlog to Jira using preset '{parsed.preset}'...",
          file=sys.stderr)
    connections = JiraConnections(config.get_jira_config(), jira_passphrase)
    mode = (OnExistingKey.SKIP if parsed.skip_existing
            else OnExistingKey.RAISE)
    result = add_backlog_to_jira(connections, parsed.preset, data.backlog,
                                 on_existing_key=mode,
                                 rank_anchor=rank_anchor(parsed.rank),
                                 levels=config.get_levels(),
                                 status_map=config.get_status_input_map())
    print(f'Added {len(result.stored)} items to Jira; '
          f'{len(result.already_present)} already present; '
          f'{len(result.failed)} failed; '
          f'{len(result.failed_links)} links not written.', file=sys.stderr)
    return result


def _write_result_files(parsed: argparse.Namespace, config: BacklogOpsConfig,
                        data: BacklogReleases, result: AddedToJira) -> None:
    """Write the added and already-present backlogs to any named files."""
    releases = list(data.releases)
    if parsed.added_file is not None:
        added = BacklogReleases(backlog=result.stored, releases=releases)
        write_result_file(config, parsed.added_file, added, parsed.force)
    if parsed.existing_file is not None:
        present = BacklogReleases(backlog=result.already_present,
                                  releases=releases)
        write_result_file(config, parsed.existing_file, present, parsed.force)


def _add_and_write(parsed: argparse.Namespace, config: BacklogOpsConfig,
                   data: BacklogReleases) -> AddedToJira:
    """Add the backlog to Jira and write any requested result files."""
    result = _add(parsed, config, data)
    _write_result_files(parsed, config, data, result)
    return result


def _run(parsed: argparse.Namespace) -> int:
    """Read the input, add it to Jira, write files and print the lists."""
    return run_added_to_jira(parsed, _add_and_write, format_add_result,
                             ExistsInJiraError, 'Could not add to Jira')


def main(args: Optional[list[str]] = None) -> int:
    """Add a backlog to Jira and report the added and present items.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the backlog cannot be added or a key
        already exists in Jira without ``--skip-existing``.
    """
    return _run(parsed_args(build_parser(), args))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
