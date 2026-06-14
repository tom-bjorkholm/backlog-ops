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
from backlogops import InputFormatConfig, OutputFormatConfig, \
    read_available_teams, read_backlog_releases, resolve_input_config, \
    resolve_output_config, write_backlog_releases

DESCRIPTION = 'Convert a backlog and releases between table file formats'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the convert command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-i', '--input', dest='input', required=True,
                        help='Input data file to read.')
    parser.add_argument('-I', '--input-config', dest='input_config',
                        help='Input format: a config file or a preset name.')
    parser.add_argument('-o', '--output', dest='output', required=True,
                        help='Output data file to create.')
    parser.add_argument('-O', '--output-config', dest='output_config',
                        help='Output format: a config file or a preset name.')
    parser.add_argument('--io-config', dest='io_config',
                        help='Configuration file holding the named presets '
                        '(by default the teams configuration file).')
    parser.add_argument('--releases-first', dest='releases_first',
                        action='store_true',
                        help='Write the releases before the backlog.')
    return parser


def _input_presets(io_config: Optional[str]
                   ) -> Optional[dict[str, InputFormatConfig]]:
    """Return the named input presets from a presets file, if given."""
    if io_config is None:
        return None
    return read_available_teams(io_config, sys.stderr).input_configs


def _output_presets(io_config: Optional[str]
                    ) -> Optional[dict[str, OutputFormatConfig]]:
    """Return the named output presets from a presets file, if given."""
    if io_config is None:
        return None
    return read_available_teams(io_config, sys.stderr).output_configs


def _convert(parsed: argparse.Namespace) -> None:
    """Read the input file and write the output file."""
    input_config = resolve_input_config(
        parsed.input_config, data_file=parsed.input,
        presets=_input_presets(parsed.io_config))
    output_config = resolve_output_config(
        parsed.output_config, data_file=parsed.output,
        presets=_output_presets(parsed.io_config))
    data = read_backlog_releases(parsed.input, input_config)
    data.check_consistency(sys.stderr)
    write_backlog_releases(data, parsed.output, output_config,
                           backlog_first=not parsed.releases_first)


def main(args: Optional[list[str]] = None) -> int:
    """Convert a backlog and releases from the input to the output file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read, validated
        or written.
    """
    parsed = build_parser().parse_args(args)
    try:
        _convert(parsed)
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f'Could not convert: {error}', file=sys.stderr)
        return 1
    print(f'Wrote {parsed.output}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
