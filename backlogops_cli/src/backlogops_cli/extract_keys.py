#! /usr/local/bin/python3
"""Extract the keys of a backlog at the given levels.

The command reads a backlog from an input file and extracts the keys of
the items at the levels named on the command line, in backlog order, as
documented for :func:`backlogops.get_keys_in_order`. A level is given by
name, alias or number. The keys are written to the key list file given by
``-o``, or to standard output when ``-o`` is omitted.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from backlogops import get_keys_in_order, write_key_list
from backlogops_cli._command_io import (
    add_force_arg, add_input_args, io_levels, overwrite_callback,
    parsed_args, read_input)

DESCRIPTION = 'Extract backlog keys at the given levels to a key list'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the extract-keys command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_input_args(parser)
    parser.add_argument('-l', '--levels', dest='levels', nargs='+',
                        required=True, metavar='LEVEL',
                        help='Levels to extract keys at, by name or number.')
    parser.add_argument('-o', '--output', dest='output',
                        help='Key list file to create; stdout if omitted.')
    parser.add_argument('--io-config', dest='io_config',
                        help='Configuration file holding the named presets.')
    add_force_arg(parser)
    return parser


def _level_value(text: str) -> int | str:
    """Return a level token as an int when numeric, else as a name."""
    try:
        return int(text)
    except ValueError:
        return text


def _emit(keys: list[str], output: Optional[str], force: bool) -> None:
    """Write the keys to the output file, or to stdout when none is given."""
    if output is None:
        for key in keys:
            print(key)
    else:
        write_key_list(keys, output,
                       file_exists_callback=overwrite_callback(force))


def main(args: Optional[list[str]] = None) -> int:
    """Extract the backlog keys at the given levels and emit them.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the backlog cannot be read or the
        keys cannot be written.
    """
    parsed = parsed_args(build_parser(), args)
    try:
        data = read_input(parsed)
        only_levels = [_level_value(text) for text in parsed.levels]
        keys = get_keys_in_order(data.backlog, only_levels, io_levels(parsed))
        _emit(keys, parsed.output, parsed.force)
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f'Could not extract keys: {error}', file=sys.stderr)
        return 1
    if parsed.output is not None:
        print(f'Wrote {parsed.output}')
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
