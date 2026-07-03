#! /usr/local/bin/python3
"""Update releases in Jira from an input file, matching versions by name.

The command reads a backlog and its releases from the input file, then
updates the matching Jira versions using a named preset of the backlog-ops
configuration, changing each version's mapped fields (most importantly the
release date) to match the internal release. ``--on-missing`` chooses what
to do with a release whose name is not present in Jira: ``raise`` (the
default) stops with an error, ``ignore`` leaves it alone, and ``add``
creates it. ``--release`` names releases and may be given several times;
``--only-listed`` limits the update to just those named releases, while
without it every input release is updated.

The updated, ignored, added and failed releases are printed to stdout as
labelled lists, unless ``-q``/``--quiet`` is given. An encrypted Jira token
is unlocked by a pass phrase asked on the terminal only when it is needed.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from getpass import getpass
from typing import Optional
from backlogops import (
    BacklogOpsConfig, ItemNotInJiraError, JiraConnections, OnMissingKey,
    Releases, UpdatedReleasesInJira, format_release_updates,
    update_releases_in_jira)
from backlogops_cli._command_io import (
    add_config_arg, add_input_args, parsed_args, read_input, required_config)

DESCRIPTION = 'Update releases in Jira, setting dates to the planned dates'

_MISSING_MODES = {'raise': OnMissingKey.RAISE, 'ignore': OnMissingKey.IGNORE,
                  'add': OnMissingKey.ADD}


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the update-releases command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_input_args(parser)
    add_config_arg(parser)
    parser.add_argument('-p', '--preset', dest='preset', required=True,
                        help='Name of the Jira preset in the configuration.')
    parser.add_argument('--on-missing', dest='on_missing',
                        choices=sorted(_MISSING_MODES), default='raise',
                        help='What to do with a release whose name is not in '
                        'Jira: raise (default), ignore, or add it.')
    parser.add_argument('--release', dest='releases', action='append',
                        metavar='NAME',
                        help='Name a release to update; may be given several '
                        'times. Only used together with --only-listed.')
    parser.add_argument('--only-listed', dest='only_listed',
                        action='store_true',
                        help='Update only the releases named with --release; '
                        'without it every input release is updated.')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='Do not print the result lists to stdout.')
    return parser


def _passphrase() -> str:
    """Ask for the Jira token pass phrase on the terminal."""
    return getpass('Jira API token pass phrase: ')


def _select(parsed: argparse.Namespace, releases: Releases) -> Releases:
    """Return the releases to update, limited to --release when asked.

    Without ``--only-listed`` every input release is returned. With it,
    only the releases whose name was named with ``--release`` are kept, and
    any named release missing from the input is reported.
    """
    if not parsed.only_listed:
        return releases
    wanted = set(parsed.releases or [])
    missing = sorted(wanted - {release.name for release in releases})
    if missing:
        print('Named releases not in the input: ' + ', '.join(missing),
              file=sys.stderr)
    return [release for release in releases if release.name in wanted]


def _update(parsed: argparse.Namespace, config: BacklogOpsConfig,
            releases: Releases) -> UpdatedReleasesInJira:
    """Update the selected releases in Jira using the named preset."""
    print(f"Updating releases in Jira using preset '{parsed.preset}'...",
          file=sys.stderr)
    connections = JiraConnections(config.get_jira_config(), _passphrase)
    mode = _MISSING_MODES[parsed.on_missing]
    result = update_releases_in_jira(connections, parsed.preset, releases,
                                     on_missing_key=mode)
    print(f'Updated {len(result.updated)} releases in Jira; '
          f'{len(result.ignored)} ignored; {len(result.added)} added; '
          f'{len(result.failed)} failed.', file=sys.stderr)
    return result


def _run(parsed: argparse.Namespace) -> int:
    """Read the input, update the releases and print the result lists."""
    try:
        config = required_config(parsed)
        data = read_input(parsed, config)
        result = _update(parsed, config, _select(parsed, data.releases))
    except ItemNotInJiraError:
        print('Nothing updated in Jira.', file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f'Could not update releases in Jira: {error}', file=sys.stderr)
        return 1
    if not parsed.quiet:
        print(format_release_updates(result))
    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Update releases in Jira and report the outcome per release.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the releases cannot be updated or a
        name is not present in Jira with the raise policy.
    """
    parsed = parsed_args(build_parser(), args)
    return _run(parsed)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
