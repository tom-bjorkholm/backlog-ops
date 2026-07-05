#! /usr/local/bin/python3
"""Update a backlog in Jira from an input file, matching issues by key.

The command reads a backlog (or a backlog and its releases) from the input
file, then updates the matching Jira issues using a named preset of the
backlog-ops configuration, changing only a chosen subset of the mapped
fields. The subset is chosen with exactly one of two flags: ``-s``/``--store``
lists the columns to update (or the single word ``all`` for every mapped
writable column), while ``-e``/``--exclude`` updates every mapped writable
column except the listed ones.

``--on-missing`` chooses what to do with an item whose key is not present in
Jira: ``raise`` (the default) stops with an error, ``ignore`` leaves it
alone, and ``add`` creates it with all of its fields. ``--links`` chooses how
the parent and dependency links are updated: ``reconcile`` (the default) makes
the Jira links match the backlog exactly, removing a Jira link the backlog no
longer has and clearing a dropped parent, while ``add`` only adds the missing
links and never removes one. ``--links`` governs only the links; the other
selected fields are updated the same way under either value.

The updated, already-correct, ignored, added and failed items are printed
to stdout as labelled lists, unless ``-q``/``--quiet`` is given. An
encrypted Jira token is unlocked by a pass phrase asked on the terminal
only when it is needed.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from getpass import getpass
from typing import Optional
from backlogops import (
    BacklogOpsConfig, ItemNotInJiraError, JiraConnections, LinkUpdate,
    OnMissingKey, UpdatedBacklogInJira, format_backlog_updates,
    update_backlog_in_jira, updatable_backlog_fields)
from backlogops_cli._command_io import (
    add_config_arg, add_input_args, parsed_args, read_input, required_config)

DESCRIPTION = 'Update a backlog in Jira, changing only the chosen columns'

_MISSING_MODES = {'raise': OnMissingKey.RAISE, 'ignore': OnMissingKey.IGNORE,
                  'add': OnMissingKey.ADD}
_LINK_MODES = {'reconcile': LinkUpdate.RECONCILE,
               'add': LinkUpdate.ADD_MISSING}
_STORE_ALL = 'all'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the update-backlog command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_input_args(parser)
    add_config_arg(parser)
    parser.add_argument('-p', '--preset', dest='preset', required=True,
                        help='Name of the Jira preset in the configuration.')
    _add_column_flags(parser)
    parser.add_argument('--on-missing', dest='on_missing',
                        choices=sorted(_MISSING_MODES), default='raise',
                        help='What to do with an item whose key is not in '
                        'Jira: raise (default), ignore, or add it.')
    parser.add_argument('--links', dest='links', choices=sorted(_LINK_MODES),
                        default='reconcile',
                        help='How to update parent and dependency links: '
                        'reconcile (default) makes Jira match the backlog, '
                        'removing links it no longer has; add only adds '
                        'missing links.')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='Do not print the result lists to stdout.')
    return parser


def _add_column_flags(parser: argparse.ArgumentParser) -> None:
    """Add the mutually exclusive, required column-selection flags."""
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--store', dest='store', nargs='+',
                       metavar='COLUMN',
                       help='Columns to update, or the single word "all" for '
                       'every mapped writable column.')
    group.add_argument('-e', '--exclude', dest='exclude', nargs='+',
                       metavar='COLUMN',
                       help='Update every mapped writable column but these.')


def _passphrase() -> str:
    """Ask for the Jira token pass phrase on the terminal."""
    return getpass('Jira API token pass phrase: ')


def _resolve_fields(parsed: argparse.Namespace,
                    connections: JiraConnections) -> list[str]:
    """Return the internal field names to update from the -s/-e flags.

    ``-s all`` and ``-e`` are resolved against the preset's updatable
    columns. A ``-s`` name that is not an updatable column is reported and
    dropped, so a typo does not silently update nothing.
    """
    updatable = updatable_backlog_fields(connections, parsed.preset)
    if parsed.store is not None:
        if parsed.store == [_STORE_ALL]:
            return updatable
        unknown = [name for name in parsed.store if name not in updatable]
        if unknown:
            print('Ignoring columns not updatable in this preset: '
                  + ', '.join(unknown), file=sys.stderr)
        return [name for name in parsed.store if name in updatable]
    excluded = set(parsed.exclude)
    return [name for name in updatable if name not in excluded]


def _update(parsed: argparse.Namespace, config: BacklogOpsConfig,
            data_backlog: object) -> UpdatedBacklogInJira:
    """Update the input backlog in Jira using the named preset."""
    print(f"Updating backlog in Jira using preset '{parsed.preset}'...",
          file=sys.stderr)
    connections = JiraConnections(config.get_jira_config(), _passphrase)
    fields = _resolve_fields(parsed, connections)
    mode = _MISSING_MODES[parsed.on_missing]
    link_update = _LINK_MODES[parsed.links]
    assert isinstance(data_backlog, list)
    result = update_backlog_in_jira(connections, parsed.preset, data_backlog,
                                    on_missing_key=mode,
                                    fields_to_update=fields,
                                    link_update=link_update,
                                    levels=config.get_levels(),
                                    status_map=config.get_status_input_map())
    _report_summary(result)
    return result


def _report_summary(result: UpdatedBacklogInJira) -> None:
    """Print a one-line summary of the update outcome to stderr."""
    print(f'Updated {len(result.updated)} items in Jira; '
          f'{len(result.already_correct)} already correct; '
          f'{len(result.ignored)} ignored; {len(result.added.stored)} added; '
          f'{len(result.failed)} failed.', file=sys.stderr)


def _run(parsed: argparse.Namespace) -> int:
    """Read the input, update the backlog and print the result lists."""
    try:
        config = required_config(parsed)
        data = read_input(parsed, config)
        result = _update(parsed, config, data.backlog)
    except ItemNotInJiraError:
        print('Nothing updated in Jira.', file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f'Could not update backlog in Jira: {error}', file=sys.stderr)
        return 1
    if not parsed.quiet:
        print(format_backlog_updates(result))
    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Update a backlog in Jira and report the outcome per item.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the backlog cannot be updated or a key
        is not present in Jira with the raise policy.
    """
    parsed = parsed_args(build_parser(), args)
    return _run(parsed)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
