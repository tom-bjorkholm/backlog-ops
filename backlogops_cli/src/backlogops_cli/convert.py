#! /usr/local/bin/python3
"""Read a backlog and releases from one file and write them to another.

The command reads a backlog, releases, or both from an input file and
writes them to an output file, possibly in another format and with other
column names. The input and output formats are inferred from the file
name extensions, but can be overridden by a configuration file or by a
named preset stored in the teams configuration file.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from backlogops import BacklogReleases, InputFormatConfig, \
    read_available_teams, read_backlog_releases, resolve_input_config
from backlogops_cli._command_io import add_output_args, run_write

DESCRIPTION = 'Convert a backlog and releases between table file formats'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the convert command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-i', '--input', dest='input', required=True,
                        help='Input data file to read.')
    parser.add_argument('-I', '--input-config', dest='input_config',
                        help='Input format: a config file or a preset name.')
    add_output_args(parser)
    return parser


def _input_presets(io_config: Optional[str]
                   ) -> Optional[dict[str, InputFormatConfig]]:
    """Return the named input presets from a presets file, if given."""
    if io_config is None:
        return None
    return read_available_teams(io_config, sys.stderr).input_configs


def _read(parsed: argparse.Namespace) -> BacklogReleases:
    """Read and validate the backlog and releases from the input file."""
    presets = _input_presets(parsed.io_config)
    input_config = resolve_input_config(parsed.input_config,
                                        data_file=parsed.input,
                                        presets=presets)
    data = read_backlog_releases(parsed.input, input_config)
    data.check_consistency(sys.stderr)
    return data


def main(args: Optional[list[str]] = None) -> int:
    """Convert a backlog and releases from the input to the output file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read, validated
        or written.
    """
    parsed = build_parser().parse_args(args)
    return run_write(parsed, lambda: _read(parsed))


if __name__ == '__main__':
    sys.exit(main())
