#! /usr/local/bin/python3
"""Rename releases in Jira, changing Jira version names.

The command renames Jira versions of a named preset of the backlog-ops
configuration. A single rename is given with ``--old`` and ``--new``; a
batch of renames is read from a two column file named with ``--rename-file``,
whose first column holds the old names and second column the new names.
Exactly one of the two ways must be given.

Each version is matched by its old name. An old name that is not a version, a
new name that equals the old name, and a new name that is already a version
name are reported rather than applied, and a rename Jira refuses is reported
with its reason; the other renames are still applied. The renamed, unchanged,
missing, colliding and failed renames are printed to stdout unless
``-q``/``--quiet`` is given. An encrypted Jira token is unlocked by a pass
phrase asked on the terminal only when it is needed.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from getpass import getpass
from typing import Optional, Sequence
from backlogops import (
    BacklogOpsConfig, JiraConnections, ReleaseRename, RenamedReleasesInJira,
    format_rename_result, read_renames, rename_releases_in_jira)
from backlogops_cli._command_io import (
    add_config_arg, parsed_args, required_config)

DESCRIPTION = 'Rename releases in Jira, changing Jira version names'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the rename-releases command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_config_arg(parser)
    parser.add_argument('-p', '--preset', dest='preset', required=True,
                        help='Name of the Jira preset in the configuration.')
    parser.add_argument('--old', dest='old', metavar='NAME',
                        help='Current name of the version to rename; use '
                        'together with --new for a single rename.')
    parser.add_argument('--new', dest='new', metavar='NAME',
                        help='New name to give the version named by --old.')
    parser.add_argument('--rename-file', dest='rename_file', metavar='FILE',
                        help='Two column file of old and new names for a '
                        'batch of renames, with columns separated by tab.'
                        '(Spaces are allowed in a relase name.)')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='Do not print the result lists to stdout.')
    return parser


def _passphrase() -> str:
    """Ask for the Jira token pass phrase on the terminal."""
    return getpass('Jira API token pass phrase: ')


def _renames(parsed: argparse.Namespace) -> Sequence[ReleaseRename]:
    """Return the renames from --old/--new or the --rename-file.

    Exactly one way must be given: both an old and a new name, or a rename
    file, but not both and not neither.

    Raises:
        ValueError: If neither or both ways are given, or only one of the
            old and new names is given.
    """
    single = parsed.old is not None or parsed.new is not None
    if single and parsed.rename_file is not None:
        raise ValueError('Give either --old/--new or --rename-file, not both.')
    if single:
        if parsed.old is None or parsed.new is None:
            raise ValueError('Give both --old and --new for a single rename.')
        return [ReleaseRename(parsed.old, parsed.new)]
    if parsed.rename_file is None:
        raise ValueError('Give --old and --new, or --rename-file.')
    return read_renames(parsed.rename_file)


def _rename(parsed: argparse.Namespace, config: BacklogOpsConfig,
            renames: Sequence[ReleaseRename]) -> RenamedReleasesInJira:
    """Rename the releases in Jira using the named preset."""
    print(f"Renaming releases in Jira using preset '{parsed.preset}'...",
          file=sys.stderr)
    connections = JiraConnections(config.get_jira_config(), _passphrase)
    result = rename_releases_in_jira(connections, parsed.preset, renames)
    print(f'Renamed {len(result.renamed)} releases in Jira; '
          f'{len(result.unchanged)} unchanged; {len(result.missing)} not in '
          f'Jira; {len(result.collisions)} name collisions; '
          f'{len(result.failed)} failed.', file=sys.stderr)
    return result


def _run(parsed: argparse.Namespace) -> int:
    """Read the renames, rename the releases and print the result lists."""
    try:
        config = required_config(parsed)
        result = _rename(parsed, config, _renames(parsed))
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f'Could not rename releases in Jira: {error}', file=sys.stderr)
        return 1
    if not parsed.quiet:
        print(format_rename_result(result))
    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Rename releases in Jira and report the outcome per rename.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the renames cannot be read or applied.
    """
    parsed = parsed_args(build_parser(), args)
    return _run(parsed)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
