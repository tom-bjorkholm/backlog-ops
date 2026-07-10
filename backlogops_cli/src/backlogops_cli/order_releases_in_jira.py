#! /usr/local/bin/python3
"""Order releases in Jira, changing the order of a project's versions.

The command reorders the Jira versions of a named preset of the backlog-ops
configuration. Exactly one order source must be given, and the three are
mutually exclusive: ``--by-date`` orders the versions by their own release
date, earliest first, with undated versions at the end; ``--name-list`` names
a file whose lines give the wanted order, one release name per line; and
``-i``/``--input`` names a backlog-and-releases input file whose release order
is used. argparse enforces that exactly one of the three is given.

With ``--by-date`` every version is ordered. With a name source, the named
versions are moved to the front in the listed order and every other version
keeps its existing relative order and trails them; a name that is not a
version is reported. The ordered names and the names not in Jira are printed
to stdout unless ``-q``/``--quiet`` is given. An encrypted Jira token is
unlocked by a pass phrase asked on the terminal only when it is needed.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from getpass import getpass
from typing import Optional
from backlogops import (
    BacklogOpsConfig, JiraConnections, OrderedReleasesInJira,
    format_order_result, order_jira_rel_by_date, order_releases_in_jira,
    read_name_list)
from backlogops_cli._command_io import (
    add_config_arg, parsed_args, read_input, required_config)

DESCRIPTION = 'Order releases in Jira by date, a name list or the input order'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the order-releases command.

    The three order sources form a required, mutually exclusive group, so
    argparse checks that exactly one of them is given. Giving the input file
    with ``-i``/``--input`` is itself the third source; ``-I`` only names its
    format.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_config_arg(parser)
    parser.add_argument('-p', '--preset', dest='preset', required=True,
                        help='Name of the Jira preset in the configuration.')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--by-date', dest='by_date', action='store_true',
                        help='Order the versions by their release date, '
                        'earliest first, undated versions last.')
    source.add_argument('--name-list', dest='name_list', metavar='FILE',
                        help='File whose lines give the wanted order, one '
                        'release name per line (a name may contain spaces); '
                        'a table file uses one name per row.')
    source.add_argument('-i', '--input', dest='input', metavar='FILE',
                        help='Backlog-and-releases input file; ordering '
                        'follows the release order in this file.')
    parser.add_argument('-I', '--input-config', dest='input_config',
                        help='Format of the -i/--input file: a config file '
                        'or a preset name.')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='Do not print the result lists to stdout.')
    return parser


def _passphrase() -> str:
    """Ask for the Jira token pass phrase on the terminal."""
    return getpass('Jira API token pass phrase: ')


def _names(parsed: argparse.Namespace, config: BacklogOpsConfig) -> list[str]:
    """Return the wanted order of names from the chosen name source.

    Used only when ``--by-date`` is not given, so the source is either the
    ``--name-list`` file or, otherwise, the ``-i``/``--input`` file.
    """
    if parsed.name_list is not None:
        return read_name_list(parsed.name_list)
    return [release.name for release in read_input(parsed, config).releases]


def _order(parsed: argparse.Namespace,
           config: BacklogOpsConfig) -> OrderedReleasesInJira:
    """Order the releases in Jira using the chosen order source."""
    print(f"Ordering releases in Jira using preset '{parsed.preset}'...",
          file=sys.stderr)
    connections = JiraConnections(config.get_jira_config(), _passphrase)
    if parsed.by_date:
        result = order_jira_rel_by_date(connections, parsed.preset)
    else:
        result = order_releases_in_jira(connections, parsed.preset,
                                        _names(parsed, config))
    print(f'Ordered {len(result.ordered)} releases in Jira; '
          f'{len(result.not_in_jira)} not in Jira.', file=sys.stderr)
    return result


def _run(parsed: argparse.Namespace) -> int:
    """Resolve the order source, order the releases and print the result."""
    try:
        config = required_config(parsed)
        result = _order(parsed, config)
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f'Could not order releases in Jira: {error}', file=sys.stderr)
        return 1
    if not parsed.quiet:
        print(format_order_result(result))
    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Order releases in Jira and report the ordered and skipped names.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the order cannot be resolved or applied.
    """
    parsed = parsed_args(build_parser(), args)
    return _run(parsed)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
