#! /usr/local/bin/python3
"""Move key-list items to a chosen anchor of a Jira backlog by rank.

The command reads a key list from a file and moves the named issues to a
chosen anchor of the backlog read by a named preset of the backlog-ops
configuration. ``--anchor`` places them at the top (the default) or the
bottom end of the backlog, or relative to the first or last key of the list.
The backlog is the issues the preset filter reads in their Jira rank order;
``--filter`` overrides that filter for one run and may only order by rank.

By default only the named issues are ranked, in the listed order. With
``--honor-relations`` the named issues, their descendants and their
dependencies are moved as one block, ordered so that a parent is ranked
before its child and a prerequisite before its dependent. Every other issue
keeps its Jira rank order. The re-ranked keys and the named keys that are
not part of the backlog are printed to stdout unless ``-q``/``--quiet`` is
given. An encrypted Jira token is unlocked by a pass phrase asked on the
terminal only when it is needed.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from jira import JIRAError
from backlogops import (
    BacklogOpsConfig, JiraConnections, RankedInJira, format_rank_result,
    jira_rank_move_keys, read_key_list)
from backlogops_cli._command_io import (
    RANK_ANCHOR_CHOICES, add_quiet_arg, build_jira_parser, jira_passphrase,
    parsed_args, required_config)

DESCRIPTION = 'Move key-list items to a chosen anchor in the Jira rank order'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the rank-in-Jira command."""
    parser = build_jira_parser(DESCRIPTION, with_input=False)
    parser.add_argument('-k', '--key-list', dest='key_list', required=True,
                        help='Key list file naming the issues to move.')
    parser.add_argument('--anchor', dest='anchor',
                        choices=sorted(RANK_ANCHOR_CHOICES),
                        default='backlog-top',
                        help="Where to place the moved items: the "
                        "'backlog-top' (default) or 'backlog-bottom' end of "
                        "the backlog, or relative to the 'first-key' or "
                        "'last-key' of the key list.")
    parser.add_argument('--honor-relations', dest='honor_relations',
                        action='store_true',
                        help='Also move descendants and dependencies and '
                        'order parent before child; by default only the '
                        'listed keys are ranked, in the listed order.')
    parser.add_argument('--filter', dest='filter', metavar='JQL', default=None,
                        help='JQL filter reading the backlog; it may only '
                        'order by rank. Omit to use the preset filter.')
    add_quiet_arg(parser)
    return parser


def _rank(parsed: argparse.Namespace,
          config: BacklogOpsConfig) -> RankedInJira:
    """Move the key-list items in the Jira rank order using the preset."""
    print(f"Ranking items in Jira using preset '{parsed.preset}'...",
          file=sys.stderr)
    connections = JiraConnections(config.get_jira_config(), jira_passphrase)
    keys = read_key_list(parsed.key_list)
    result = jira_rank_move_keys(connections, parsed.preset, keys,
                                 filter_override=parsed.filter,
                                 anchor=RANK_ANCHOR_CHOICES[parsed.anchor],
                                 honor_relations=parsed.honor_relations,
                                 levels=config.get_levels(),
                                 status_map=config.get_status_input_map())
    print(f'Ranked {len(result.keys_ranked_ok)} items in Jira; '
          f'{len(result.keys_not_in_jira)} not in Jira; '
          f'{len(result.keys_not_in_filter)} not in the filter result.',
          file=sys.stderr)
    return result


def _run(parsed: argparse.Namespace) -> int:
    """Read the key list, rank the items in Jira and print the result."""
    try:
        config = required_config(parsed)
        result = _rank(parsed, config)
    except (ValueError, TypeError, KeyError, RuntimeError, OSError,
            JIRAError) as error:
        print(f'Could not rank in Jira: {error}', file=sys.stderr)
        return 1
    if not parsed.quiet:
        print(format_rank_result(result))
    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Move key-list items in the Jira rank order and report the outcome.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the items cannot be ranked.
    """
    return _run(parsed_args(build_parser(), args))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
