#! /usr/local/bin/python3
"""Shared command helpers for resolving output configs and writing.

The helpers here are used by more than one command (for example by the
``convert`` command and the ``demo_backlog`` command). The leading
underscore in the module name keeps it out of the command listing.
"""
# PYTHON_ARGCOMPLETE_OK

# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from collections.abc import Callable
from typing import Optional
import argcomplete
from backlogops import (
    BacklogReleases, FormatRules, InputFormatConfig, OutputFormatConfig,
    read_available_teams, read_backlog_releases, resolve_input_config,
    resolve_output_config, write_backlog_releases)


def parsed_args(parser: argparse.ArgumentParser,
                args: Optional[list[str]]) -> argparse.Namespace:
    """Enable shell completion and parse the command line arguments."""
    argcomplete.autocomplete(parser)
    return parser.parse_args(args)


def add_input_args(parser: argparse.ArgumentParser) -> None:
    """Add the input-file and input-config arguments."""
    parser.add_argument('-i', '--input', dest='input', required=True,
                        help='Input data file to read.')
    parser.add_argument('-I', '--input-config', dest='input_config',
                        help='Input format: a config file or a preset name.')


def _input_presets(io_config: Optional[str]
                   ) -> Optional[dict[str, InputFormatConfig]]:
    """Return the named input presets from a presets file, if given."""
    if io_config is None:
        return None
    return read_available_teams(io_config, sys.stderr).input_configs


def read_input(parsed: argparse.Namespace) -> BacklogReleases:
    """Read and validate the backlog and releases from the input file.

    The input format is resolved from the ``--input-config`` value, which
    may be empty (inferred from the file name), a preset name looked up in
    the presets file given by ``--io-config``, or a config file path.

    Args:
        parsed: Parsed command line arguments holding the input options
            added by :func:`add_input_args` and, optionally, the
            ``--io-config`` option added by :func:`add_output_args`.

    Returns:
        The validated backlog and releases read from the input file.
    """
    io_config = getattr(parsed, 'io_config', None)
    presets = _input_presets(io_config)
    config = resolve_input_config(parsed.input_config, data_file=parsed.input,
                                  presets=presets)
    data = read_backlog_releases(parsed.input, config)
    data.check_consistency(sys.stderr)
    return data


def add_output_args(parser: argparse.ArgumentParser) -> None:
    """Add the output-file, output-config and ordering arguments."""
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


def _output_presets(io_config: Optional[str]
                    ) -> Optional[dict[str, OutputFormatConfig]]:
    """Return the named output presets from a presets file, if given."""
    if io_config is None:
        return None
    return read_available_teams(io_config, sys.stderr).output_configs


def run_write(parsed: argparse.Namespace,
              data_source: Callable[[], BacklogReleases]) -> int:
    """Build the data, write it to the output file, and report the result.

    Args:
        parsed: Parsed command line arguments holding the output options
            added by :func:`add_output_args`.
        data_source: Callable that returns the backlog and releases to
            write. It is called inside the error handling so that reading
            failures are reported like writing failures.

    Returns:
        ``0`` on success, ``1`` when the data cannot be built or written.
    """
    try:
        data = data_source()
        presets = _output_presets(parsed.io_config)
        config = resolve_output_config(parsed.output_config,
                                       data_file=parsed.output,
                                       presets=presets)
        rules = FormatRules(backlog_first=not parsed.releases_first)
        write_backlog_releases(data, parsed.output, config, rules)
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f'Could not write {parsed.output}: {error}', file=sys.stderr)
        return 1
    print(f'Wrote {parsed.output}')
    return 0
