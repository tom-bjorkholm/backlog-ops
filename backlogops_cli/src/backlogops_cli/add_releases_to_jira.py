#! /usr/local/bin/python3
"""Add releases to Jira from an input file, creating one version per name.

The command reads a backlog and its releases from the input file, then
adds the releases to Jira using a named preset of the backlog-ops
configuration. By default it stops with an error when a release name
already exists in Jira; ``--skip-existing`` skips those releases instead.

The added releases and the releases already in Jira are printed to stdout
as two labelled lists, unless ``-q``/``--quiet`` is given. Each list is
also written, together with the unchanged input backlog, to a file when
``--added-file`` or ``--existing-file`` names one; without a file name the
list is not written. An encrypted Jira token is unlocked by a pass phrase
asked on the terminal only when it is needed.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from getpass import getpass
from typing import Optional
from backlogops import (
    AddedReleasesToJira, BacklogOpsConfig, BacklogReleases, FormatRules,
    JiraConnections, OnExistingKey, ReleaseExistsError, add_releases_to_jira,
    format_release_result, resolve_output_config, write_backlog_releases)
from backlogops_cli._command_io import (
    add_config_arg, add_input_args, overwrite_callback, parsed_args,
    read_input, required_config)
from backlogops_cli._migrate_warn import CliPresetMigrateWarnHook

DESCRIPTION = 'Add releases to Jira, creating a new version per release'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the add-releases command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_input_args(parser)
    add_config_arg(parser)
    parser.add_argument('-p', '--preset', dest='preset', required=True,
                        help='Name of the Jira preset in the configuration.')
    parser.add_argument('--skip-existing', dest='skip_existing',
                        action='store_true',
                        help='Skip releases whose name already exists in Jira '
                        '(the default stops with an error instead).')
    parser.add_argument('--added-file', dest='added_file', metavar='FILE',
                        help='Write the added releases, with the input '
                        'backlog, to this file. Omit to not write it.')
    parser.add_argument('--existing-file', dest='existing_file',
                        metavar='FILE',
                        help='Write the releases already in Jira, with the '
                        'input backlog, to this file. Omit to not write it.')
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
         data: BacklogReleases) -> AddedReleasesToJira:
    """Add the input releases to Jira using the named preset."""
    print(f"Adding releases to Jira using preset '{parsed.preset}'...",
          file=sys.stderr)
    connections = JiraConnections(config.get_jira_config(), _passphrase)
    mode = (OnExistingKey.SKIP if parsed.skip_existing
            else OnExistingKey.RAISE)
    result = add_releases_to_jira(connections, parsed.preset, data.releases,
                                  on_existing_key=mode)
    print(f'Added {len(result.stored)} releases to Jira; '
          f'{len(result.already_present)} already present; '
          f'{len(result.failed)} failed.', file=sys.stderr)
    return result


def _write_file(config: BacklogOpsConfig, path: str, data: BacklogReleases,
                force: bool) -> None:
    """Write one backlog-and-releases result to a file."""
    out_config = resolve_output_config(None, data_file=path,
                                       presets=config.output_configs,
                                       auto_ch_hook=CliPresetMigrateWarnHook())
    write_backlog_releases(data, path, out_config, FormatRules(),
                           levels=config.get_levels(),
                           file_exists_callback=overwrite_callback(force))
    print(f'Wrote {path}')


def _write_result_files(parsed: argparse.Namespace, config: BacklogOpsConfig,
                        data: BacklogReleases,
                        result: AddedReleasesToJira) -> None:
    """Write the added and already-present releases to any named files."""
    backlog = list(data.backlog)
    if parsed.added_file is not None:
        added = BacklogReleases(backlog=backlog, releases=result.stored)
        _write_file(config, parsed.added_file, added, parsed.force)
    if parsed.existing_file is not None:
        present = BacklogReleases(backlog=backlog,
                                  releases=result.already_present)
        _write_file(config, parsed.existing_file, present, parsed.force)


def _run(parsed: argparse.Namespace) -> int:
    """Read the input, add the releases, write files and print the lists."""
    try:
        config = required_config(parsed)
        data = read_input(parsed, config)
        result = _add(parsed, config, data)
        _write_result_files(parsed, config, data, result)
    except ReleaseExistsError:
        print('Nothing added to Jira.', file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f'Could not add releases to Jira: {error}', file=sys.stderr)
        return 1
    if not parsed.quiet:
        print(format_release_result(result))
    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Add releases to Jira and report the added and present releases.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the releases cannot be added or a name
        already exists in Jira without ``--skip-existing``.
    """
    parsed = parsed_args(build_parser(), args)
    return _run(parsed)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
