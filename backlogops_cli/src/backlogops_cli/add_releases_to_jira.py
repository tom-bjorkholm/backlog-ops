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
from typing import Optional
from backlogops import (
    AddedReleasesToJira, BacklogOpsConfig, BacklogReleases, JiraConnections,
    OnExistingKey, ReleaseExistsError, add_releases_to_jira,
    format_release_result)
from backlogops_cli._command_io import (
    add_force_arg, add_quiet_arg, build_jira_parser, jira_passphrase,
    parsed_args, run_added_to_jira, write_result_file)

DESCRIPTION = 'Add releases to Jira, creating a new version per release'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the add-releases command."""
    parser = build_jira_parser(DESCRIPTION)
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
    add_quiet_arg(parser)
    add_force_arg(parser)
    return parser


def _add(parsed: argparse.Namespace, config: BacklogOpsConfig,
         data: BacklogReleases) -> AddedReleasesToJira:
    """Add the input releases to Jira using the named preset."""
    print(f"Adding releases to Jira using preset '{parsed.preset}'...",
          file=sys.stderr)
    connections = JiraConnections(config.get_jira_config(), jira_passphrase)
    mode = (OnExistingKey.SKIP if parsed.skip_existing
            else OnExistingKey.RAISE)
    result = add_releases_to_jira(connections, parsed.preset, data.releases,
                                  on_existing_key=mode)
    print(f'Added {len(result.stored)} releases to Jira; '
          f'{len(result.already_present)} already present; '
          f'{len(result.failed)} failed.', file=sys.stderr)
    return result


def _write_result_files(parsed: argparse.Namespace, config: BacklogOpsConfig,
                        data: BacklogReleases,
                        result: AddedReleasesToJira) -> None:
    """Write the added and already-present releases to any named files."""
    backlog = list(data.backlog)
    if parsed.added_file is not None:
        added = BacklogReleases(backlog=backlog, releases=result.stored)
        write_result_file(config, parsed.added_file, added, parsed.force)
    if parsed.existing_file is not None:
        present = BacklogReleases(backlog=backlog,
                                  releases=result.already_present)
        write_result_file(config, parsed.existing_file, present, parsed.force)


def _add_and_write(parsed: argparse.Namespace, config: BacklogOpsConfig,
                   data: BacklogReleases) -> AddedReleasesToJira:
    """Add the releases to Jira and write any requested result files."""
    result = _add(parsed, config, data)
    _write_result_files(parsed, config, data, result)
    return result


def _run(parsed: argparse.Namespace) -> int:
    """Read the input, add the releases, write files and print the lists."""
    return run_added_to_jira(parsed, _add_and_write, format_release_result,
                             ReleaseExistsError,
                             'Could not add releases to Jira')


def main(args: Optional[list[str]] = None) -> int:
    """Add releases to Jira and report the added and present releases.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the releases cannot be added or a name
        already exists in Jira without ``--skip-existing``.
    """
    return _run(parsed_args(build_parser(), args))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
