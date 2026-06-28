#! /usr/local/bin/python3
"""Migrate a configuration file to the current file format.

The command reads an existing configuration file through the normal
backward-compatibility (Reading an Old Configuration File) rules and
writes the same configuration back in the current format to a new file.
The ``--kind`` option selects what the input file is: the backlog-ops
configuration file, a stand-alone input format preset file, or a
stand-alone output format preset file. The library refuses to overwrite an
existing output file, so the destination must not exist.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from config_as_json import Config, migrate_cfg
from backlogops import (
    BacklogOpsConfig, InputFormatConfig, OutputFormatConfig)
from backlogops_cli._command_io import parsed_args

DESCRIPTION = 'Migrate a configuration file to the current file format'

KIND_CLASSES: dict[str, type[Config]] = {
    'config': BacklogOpsConfig, 'input': InputFormatConfig,
    'output': OutputFormatConfig}
"""Map a ``--kind`` value to the configuration class used to migrate it."""

MIGRATE_ERRORS = (ValueError, TypeError, KeyError, OSError)
"""Errors raised when an input file cannot be read or written."""


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the migrate_cfg command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-i', '--input', dest='input', required=True,
                        help='Existing configuration file to migrate.')
    parser.add_argument('-o', '--output', dest='output', required=True,
                        help='New configuration file to create. It must '
                        'not already exist.')
    parser.add_argument('-k', '--kind', dest='kind', default='config',
                        choices=sorted(KIND_CLASSES),
                        help="What the input file is: 'config' (default, a "
                        "backlog-ops configuration file), 'input' (an input "
                        "format preset file), or 'output' (an output format "
                        'preset file).')
    return parser


def _exit_code(error: SystemExit) -> int:
    """Return the integer exit code carried by a SystemExit."""
    return error.code if isinstance(error.code, int) else 1


def main(args: Optional[list[str]] = None) -> int:
    """Migrate a configuration file to the current format.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the input cannot be read, the output
        already exists, or the data cannot be written.
    """
    parsed = parsed_args(build_parser(), args)
    config_class = KIND_CLASSES[parsed.kind]
    try:
        migrate_cfg(parsed.input, parsed.output, config_class)
    except SystemExit as error:
        return _exit_code(error)
    except MIGRATE_ERRORS as error:
        print(f'Could not migrate {parsed.input}: {error}', file=sys.stderr)
        return 1
    print(f'Wrote {parsed.output}')
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
