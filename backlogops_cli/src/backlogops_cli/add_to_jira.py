#! /usr/local/bin/python3
"""Add a backlog to Jira from an input file, creating one issue per item.

The command reads a backlog (or a backlog and its releases) from the input
file, then adds the backlog items to Jira using a named preset of the
backlog-ops configuration. By default it stops with an error when an
item's key already exists in Jira; ``--skip-existing`` skips those items
instead.

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
from getpass import getpass
from typing import Optional
from backlogops import (
    AddedToJira, BacklogOpsConfig, BacklogReleases, ExistsInJiraError,
    FormatRules, JiraConnections, OnExistingKey, add_backlog_to_jira,
    format_add_result, resolve_output_config, write_backlog_releases)
from backlogops_cli._command_io import (
    add_config_arg, add_input_args, overwrite_callback, parsed_args,
    read_input, required_config)
from backlogops_cli._migrate_warn import CliPresetMigrateWarnHook

DESCRIPTION = 'Add a backlog to Jira, creating a new issue per item'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the add-to-Jira command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_input_args(parser)
    add_config_arg(parser)
    parser.add_argument('-p', '--preset', dest='preset', required=True,
                        help='Name of the Jira preset in the configuration.')
    parser.add_argument('--skip-existing', dest='skip_existing',
                        action='store_true',
                        help='Skip items whose key already exists in Jira '
                        '(the default stops with an error instead).')
    parser.add_argument('--added-file', dest='added_file', metavar='FILE',
                        help='Write the added items, with their new Jira '
                        'keys, to this file. Omit to not write it.')
    parser.add_argument('--existing-file', dest='existing_file',
                        metavar='FILE',
                        help='Write the items already in Jira to this file. '
                        'Omit to not write it.')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='Do not print the added and already-present '
                        'lists to stdout.')
    parser.add_argument('-f', '--force', dest='force', action='store_true',
                        help='Overwrite existing output files without '
                        'asking.')
    return parser


def _passphrase() -> str:
    """Ask for the Jira token pass phrase on the terminal."""
    return getpass('Jira API token pass phrase: ')


def _add(parsed: argparse.Namespace, config: BacklogOpsConfig,
         data: BacklogReleases) -> AddedToJira:
    """Add the input backlog to Jira using the named write preset."""
    print(f"Adding backlog to Jira using preset '{parsed.preset}'...",
          file=sys.stderr)
    connections = JiraConnections(config.get_jira_config(), _passphrase)
    mode = (OnExistingKey.SKIP if parsed.skip_existing
            else OnExistingKey.RAISE)
    result = add_backlog_to_jira(connections, parsed.preset, data.backlog,
                                 on_existing_key=mode,
                                 levels=config.get_levels())
    print(f'Added {len(result.stored)} items to Jira; '
          f'{len(result.already_present)} already present.', file=sys.stderr)
    return result


def _write_backlog_file(config: BacklogOpsConfig, path: str,
                        data: BacklogReleases, force: bool) -> None:
    """Write one returned backlog and the input releases to a file."""
    out_config = resolve_output_config(None, data_file=path,
                                       presets=config.output_configs,
                                       auto_ch_hook=CliPresetMigrateWarnHook())
    write_backlog_releases(data, path, out_config, FormatRules(),
                           levels=config.get_levels(),
                           file_exists_callback=overwrite_callback(force))
    print(f'Wrote {path}')


def _write_result_files(parsed: argparse.Namespace, config: BacklogOpsConfig,
                        data: BacklogReleases, result: AddedToJira) -> None:
    """Write the added and already-present backlogs to any named files."""
    releases = list(data.releases)
    if parsed.added_file is not None:
        added = BacklogReleases(backlog=result.stored, releases=releases)
        _write_backlog_file(config, parsed.added_file, added, parsed.force)
    if parsed.existing_file is not None:
        present = BacklogReleases(backlog=result.already_present,
                                  releases=releases)
        _write_backlog_file(config, parsed.existing_file, present,
                            parsed.force)


def _run(parsed: argparse.Namespace) -> int:
    """Read the input, add it to Jira, write files and print the lists."""
    try:
        config = required_config(parsed)
        data = read_input(parsed, config)
        result = _add(parsed, config, data)
        _write_result_files(parsed, config, data, result)
    except ExistsInJiraError:
        print('Nothing added to Jira.', file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f'Could not add to Jira: {error}', file=sys.stderr)
        return 1
    if not parsed.quiet:
        print(format_add_result(result))
    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Add a backlog to Jira and report the added and present items.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the backlog cannot be added or a key
        already exists in Jira without ``--skip-existing``.
    """
    parsed = parsed_args(build_parser(), args)
    return _run(parsed)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
