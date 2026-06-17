#! /usr/local/bin/python3
"""Run the available-teams wizard and store the result to a file."""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from config_as_json.file_extension import fix_file_extension
from backlogops import ConsoleYesNoUiBridge, teams_config_wizard
from backlogops_cli._command_io import parsed_args

DESCRIPTION = 'Create an AvailableTeams configuration file via a wizard'
CONFIG_EXTENSION = '.cfg'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the teams wizard command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-o', '--output', dest='output', required=True,
                        help='Configuration file to write; the '
                        f'{CONFIG_EXTENSION} extension is added if missing.')
    return parser


def main(args: Optional[list[str]] = None) -> int:
    """Run the interactive wizard and write the workforce configuration.

    The output filename receives the ``.cfg`` extension when it is not
    already present.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the entered workforce is rejected or
        cannot be written.
    """
    parsed = parsed_args(build_parser(), args)
    output = fix_file_extension(parsed.output, CONFIG_EXTENSION)
    bridge = ConsoleYesNoUiBridge(sys.stdout, sys.stdin, sys.stderr)
    try:
        config = teams_config_wizard(bridge)
        config.write(to_json_filename=output, stderr_file=sys.stderr)
    except (ValueError, TypeError, KeyError, EOFError, OSError) as error:
        print(f'Could not create the configuration: {error}', file=sys.stderr)
        return 1
    print(f'Workforce configuration written to {output}')
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
