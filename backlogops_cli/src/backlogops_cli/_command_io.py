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
from backlogops_cli.bloc_version_reporter import BloCliVersionReporter
from backlogops import (
    BacklogReleases, FormatRules, InputFormatConfig, OutputFormatConfig,
    ReleaseChanges, ReleaseDateChanges, format_content_changes,
    format_date_changes, read_available_teams, read_backlog_releases,
    resolve_input_config, resolve_output_config, write_backlog_releases,
    write_content_changes, write_date_changes)


def parsed_args(parser: argparse.ArgumentParser,
                args: Optional[list[str]]) -> argparse.Namespace:
    """Enable shell completion and parse the command line arguments."""
    argcomplete.autocomplete(parser)
    BloCliVersionReporter().check_if_unsupported_python()
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


def _write_output(parsed: argparse.Namespace, data: BacklogReleases) -> None:
    """Write the backlog and releases to the configured output file."""
    presets = _output_presets(parsed.io_config)
    config = resolve_output_config(parsed.output_config,
                                   data_file=parsed.output, presets=presets)
    rules = FormatRules(backlog_first=not parsed.releases_first)
    write_backlog_releases(data, parsed.output, config, rules)


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
        _write_output(parsed, data_source())
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f'Could not write {parsed.output}: {error}', file=sys.stderr)
        return 1
    print(f'Wrote {parsed.output}')
    return 0


DEFAULT_BUFFER_DAYS = 5
"""Default slack in calendar days added when fitting dates."""


def add_buffer_arg(parser: argparse.ArgumentParser) -> None:
    """Add the buffer-days argument with the default slack."""
    parser.add_argument('--buffer-days', dest='buffer_days', type=int,
                        default=DEFAULT_BUFFER_DAYS, metavar='DAYS',
                        help='Slack in calendar days kept against the planned '
                        f'dates (default {DEFAULT_BUFFER_DAYS}). Must not be '
                        'negative.')


def add_changes_arg(parser: argparse.ArgumentParser) -> None:
    """Add the optional file to also save the list of changes to."""
    parser.add_argument('--changes-file', dest='changes_file', metavar='FILE',
                        help='Also save the list of changes to a TableIO '
                        'file. Without it the changes are only printed to '
                        'stdout.')


def build_change_parser(description: str) -> argparse.ArgumentParser:
    """Build a parser with input, buffer, output and changes arguments."""
    parser = argparse.ArgumentParser(description=description)
    add_input_args(parser)
    add_buffer_arg(parser)
    add_output_args(parser)
    add_changes_arg(parser)
    return parser


def date_report(changes: ReleaseDateChanges
                ) -> tuple[str, Optional[Callable[[str], None]]]:
    """Return the date change listing and a writer, None when empty."""
    writer = None if not changes else \
        (lambda path: write_date_changes(changes, path))
    return format_date_changes(changes), writer


def content_report(changes: ReleaseChanges
                   ) -> tuple[str, Optional[Callable[[str], None]]]:
    """Return the content change listing and a writer, None when empty."""
    writer = None if not changes else \
        (lambda path: write_content_changes(changes, path))
    return format_content_changes(changes), writer


def run_change_command(parsed: argparse.Namespace,
                       produce: Callable[[BacklogReleases], tuple[
                           str, Optional[Callable[[str], None]]]]) -> int:
    """Read, change, write the data, and emit the list of changes.

    The input is read and validated, ``produce`` changes it in place and
    returns the change listing as text together with a callback that
    writes the same changes to a file. The changed data is written to the
    output file, the listing is printed to stdout, and, when
    ``--changes-file`` is given, the changes are also written to that file.

    Args:
        parsed: Parsed command line arguments holding the input, output
            and ``--changes-file`` options.
        produce: Callable that changes the data and returns the change
            listing text and a writer for the change file.

    Returns:
        ``0`` on success, ``1`` when any step fails.
    """
    try:
        data = read_input(parsed)
        listing, write_changes = produce(data)
        _write_output(parsed, data)
        print(f'Wrote {parsed.output}')
        print(listing)
        _save_changes(parsed, write_changes)
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f'Could not complete: {error}', file=sys.stderr)
        return 1
    return 0


def _save_changes(parsed: argparse.Namespace,
                  write_changes: Optional[Callable[[str], None]]) -> None:
    """Save the changes to ``--changes-file`` when one is requested.

    A ``write_changes`` of None means there were no changes, so nothing is
    written and a short note is printed instead.
    """
    if parsed.changes_file is None:
        return
    if write_changes is None:
        print('No changes to write.')
        return
    write_changes(parsed.changes_file)
    print(f'Wrote {parsed.changes_file}')
