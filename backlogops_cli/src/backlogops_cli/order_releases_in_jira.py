#! /usr/local/bin/python3
"""Order releases in Jira, changing the order of a project's versions.

The command reorders the Jira versions of a named preset of the backlog-ops
configuration. Exactly one order source must be given: ``--by-date`` orders
the versions by their own release date, earliest first, with undated versions
at the end; ``--name-list`` names a file whose names give the wanted order,
like a key list; and ``--from-input`` uses the order of the releases in the
backlog-and-releases input file named with ``-i``/``--input``.

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
    read_key_list)
from backlogops_cli._command_io import (
    add_config_arg, parsed_args, read_input, required_config)

DESCRIPTION = 'Order releases in Jira by date, a name list or the input order'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the order-releases command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_config_arg(parser)
    parser.add_argument('-p', '--preset', dest='preset', required=True,
                        help='Name of the Jira preset in the configuration.')
    parser.add_argument('--by-date', dest='by_date', action='store_true',
                        help='Order the versions by their release date, '
                        'earliest first, undated versions last.')
    parser.add_argument('--name-list', dest='name_list', metavar='FILE',
                        help='File whose names give the wanted order, like a '
                        'key list. One name per row of a table, or whitespace '
                        'separated in a text file.')
    parser.add_argument('--from-input', dest='from_input', action='store_true',
                        help='Use the order of the releases in the input file '
                        'named with -i/--input.')
    parser.add_argument('-i', '--input', dest='input',
                        help='Input data file, needed with --from-input.')
    parser.add_argument('-I', '--input-config', dest='input_config',
                        help='Input format: a config file or a preset name.')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='Do not print the result lists to stdout.')
    return parser


def _passphrase() -> str:
    """Ask for the Jira token pass phrase on the terminal."""
    return getpass('Jira API token pass phrase: ')


def _check_mode(parsed: argparse.Namespace) -> None:
    """Check exactly one order source is given, with its needed options.

    Raises:
        ValueError: If not exactly one of the three order sources is given,
            or if ``--from-input`` is given without ``-i``/``--input``.
    """
    chosen = [parsed.by_date, parsed.name_list is not None, parsed.from_input]
    if sum(1 for source in chosen if source) != 1:
        raise ValueError('Give exactly one of --by-date, --name-list or '
                         '--from-input.')
    if parsed.from_input and parsed.input is None:
        raise ValueError('--from-input needs -i/--input to name the file.')


def _names(parsed: argparse.Namespace, config: BacklogOpsConfig) -> list[str]:
    """Return the wanted order of names from the chosen name source."""
    if parsed.name_list is not None:
        return read_key_list(parsed.name_list)
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
        _check_mode(parsed)
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
