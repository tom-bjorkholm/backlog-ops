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
from pathlib import Path
from collections.abc import Callable
from typing import Optional, TextIO
import argcomplete
from backlogops_cli._migrate_warn import (
    CliMigrateWarnHook, CliPresetMigrateWarnHook)
from backlogops_cli.bloc_version_reporter import BloCliVersionReporter
from backlogops import (
    BacklogOpsConfig, BacklogReleases, FileExistsCb, FormatRules, Levels,
    ReleaseChanges, ReleaseDateChanges, allow_overwrite,
    format_content_changes, format_date_changes, get_backlog_ops_config,
    read_backlog_releases, resolve_input_config, resolve_output_config,
    write_backlog_releases, write_content_changes, write_date_changes)


def overwrite_callback(force: bool, in_stream: Optional[TextIO] = None,
                       out_stream: Optional[TextIO] = None) -> FileExistsCb:
    """Return a file-exists callback for writing CLI output files.

    A writer calls the returned callback only when the target file
    already exists. With ``force`` the overwrite is allowed silently.
    Otherwise the user is asked on ``out_stream``/``in_stream`` and the
    overwrite is allowed only on an explicit yes; any other answer, an
    empty answer, or end of input refuses it with ``FileExistsError``.

    Args:
        force: Allow the overwrite without asking when True.
        in_stream: Stream the answer is read from, or None for stdin.
        out_stream: Stream the prompt is written to, or None for stdout.

    Returns:
        A callback suitable as ``file_exists_callback`` for the writers.
    """
    if force:
        return allow_overwrite
    reader = sys.stdin if in_stream is None else in_stream
    writer = sys.stdout if out_stream is None else out_stream

    def ask(file_name: str) -> None:
        """Ask whether to overwrite ``file_name``; raise when refused."""
        prompt = f'Output file {file_name} already exists. Overwrite? [y/N]: '
        print(prompt, end='', file=writer)
        writer.flush()
        if reader.readline().strip().lower() in ('y', 'yes'):
            return
        raise FileExistsError(f'Did not overwrite existing file {file_name}.')
    return ask


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


def add_config_arg(parser: argparse.ArgumentParser) -> None:
    """Add the ``-c``/``--config`` backlog-ops configuration argument.

    The configuration file holds the workforce, the named input and output
    presets, the levels and the global status map. Without ``-c`` the file
    is discovered the same way as the GUI.
    """
    parser.add_argument('-c', '--config', dest='config',
                        help='Backlog-ops configuration file (workforce, '
                        'named presets, levels, status map). Without -c the '
                        'file is found from $BACKLOGOPS_CFG, else '
                        'backlogops.cfg in $BACKLOGOPS_DIR, else '
                        '$HOME/.backlogops.cfg.')


def _resolve_config(parsed: argparse.Namespace) -> BacklogOpsConfig:
    """Return the backlog-ops configuration from ``-c`` or by discovery.

    With ``-c`` the named file is read; an old file triggers a migration
    warning. Without ``-c`` the file is discovered the same way as the GUI
    (``$BACKLOGOPS_CFG``, then ``backlogops.cfg`` in ``$BACKLOGOPS_DIR``,
    then ``$HOME/.backlogops.cfg``).

    Raises:
        ValueError: If ``-c`` names a file that does not exist.
        RuntimeError: If no ``-c`` is given and no file is discovered.
    """
    config_file = parsed.config
    if config_file is not None:
        if not Path(config_file).is_file():
            raise ValueError(f'Configuration file not found: {config_file}')
        return get_backlog_ops_config(config_file, sys.stderr,
                                      auto_ch_hook=CliMigrateWarnHook())
    return get_backlog_ops_config(None, sys.stderr,
                                  auto_ch_hook=CliMigrateWarnHook())


def required_config(parsed: argparse.Namespace) -> BacklogOpsConfig:
    """Return the configuration, reporting a missing one as a ValueError.

    Used by commands that cannot work without a configuration, such as the
    estimate command, which needs the workforce.
    """
    try:
        return _resolve_config(parsed)
    except RuntimeError as error:
        raise ValueError(str(error)) from error


def optional_config(parsed: argparse.Namespace) -> Optional[BacklogOpsConfig]:
    """Return the configuration, or None with a note when none is found.

    Used by commands that fall back to the built-in defaults (formats
    inferred from the file name, no presets) when no configuration file is
    available.
    """
    try:
        return _resolve_config(parsed)
    except RuntimeError:
        print('No backlog-ops configuration file found; using built-in '
              'defaults.', file=sys.stderr)
        return None


def io_levels(config: Optional[BacklogOpsConfig]) -> Optional[Levels]:
    """Return the configured levels from ``config``, or None.

    Args:
        config: The resolved backlog-ops configuration, or None to use the
            default levels.

    Returns:
        The levels configured in ``config``, or None when no configuration
        is given.
    """
    return config.get_levels() if config is not None else None


def read_input(parsed: argparse.Namespace,
               config: Optional[BacklogOpsConfig]) -> BacklogReleases:
    """Read and validate the backlog and releases from the input file.

    The input format is resolved from the ``--input-config`` value, which
    may be empty (inferred from the file name), a preset name looked up in
    ``config``, or a config file path. When ``config`` is given its levels
    and its library-wide status input map are honoured while reading the
    items; the input configuration's own status map overrides the global
    one per name.

    Args:
        parsed: Parsed command line arguments holding the input options
            added by :func:`add_input_args`.
        config: The resolved backlog-ops configuration, or None to use the
            built-in defaults.

    Returns:
        The validated backlog and releases read from the input file.
    """
    presets = config.input_configs if config is not None else None
    levels = config.get_levels() if config is not None else None
    status_map = (config.get_status_input_map() if config is not None
                  else None)
    in_config = resolve_input_config(parsed.input_config,
                                     data_file=parsed.input, presets=presets,
                                     auto_ch_hook=CliPresetMigrateWarnHook())
    data = read_backlog_releases(parsed.input, in_config, levels, status_map)
    data.check_consistency(sys.stderr)
    return data


def add_force_arg(parser: argparse.ArgumentParser) -> None:
    """Add the force flag that overwrites output files without asking."""
    parser.add_argument('-f', '--force', dest='force', action='store_true',
                        help='Overwrite existing output files without '
                        'asking.')


def add_output_args(parser: argparse.ArgumentParser) -> None:
    """Add the output-file, output-config and ordering arguments."""
    parser.add_argument('-o', '--output', dest='output', required=True,
                        help='Output data file to create.')
    parser.add_argument('-O', '--output-config', dest='output_config',
                        help='Output format: a config file or a preset name.')
    parser.add_argument('--releases-first', dest='releases_first',
                        action='store_true',
                        help='Write the releases before the backlog.')
    add_force_arg(parser)


def build_io_parser(description: str, *, with_input: bool = True,
                    with_config: bool = True,
                    with_output: bool = True) -> argparse.ArgumentParser:
    """Create a parser with the common input, config and output options.

    Most data commands read a file, take the backlog-ops configuration,
    and write a file, so this builds the parser with those option groups
    already added. A command adds only its own extra options to the
    returned parser. A group is left out when its flag is False, for a
    command that does not read (or does not write) a backlog file.

    Args:
        description: The command description shown in the help text.
        with_input: Add the input-file and input-config options.
        with_config: Add the ``-c`` backlog-ops configuration option.
        with_output: Add the output-file, output-config, ordering and
            force options.

    Returns:
        The parser with the requested common options added.
    """
    parser = argparse.ArgumentParser(description=description)
    if with_input:
        add_input_args(parser)
    if with_config:
        add_config_arg(parser)
    if with_output:
        add_output_args(parser)
    return parser


def _write_output(parsed: argparse.Namespace,
                  config: Optional[BacklogOpsConfig],
                  data: BacklogReleases) -> None:
    """Write the backlog and releases to the configured output file."""
    presets = config.output_configs if config is not None else None
    out_config = resolve_output_config(parsed.output_config,
                                       data_file=parsed.output,
                                       presets=presets,
                                       auto_ch_hook=CliPresetMigrateWarnHook())
    rules = FormatRules(backlog_first=not parsed.releases_first)
    write_backlog_releases(data, parsed.output, out_config, rules,
                           levels=io_levels(config),
                           file_exists_callback=overwrite_callback(
                               parsed.force))


def run_write(parsed: argparse.Namespace,
              data_source: Callable[[Optional[BacklogOpsConfig]],
                                    BacklogReleases]) -> int:
    """Build the data, write it to the output file, and report the result.

    The configuration is resolved once from ``-c`` or by discovery, falling
    back to the built-in defaults when none is found.

    Args:
        parsed: Parsed command line arguments holding the output options
            added by :func:`add_output_args` and the ``-c`` option added by
            :func:`add_config_arg`.
        data_source: Callable that receives the resolved configuration (or
            None) and returns the backlog and releases to write. It is
            called inside the error handling so that reading failures are
            reported like writing failures.

    Returns:
        ``0`` on success, ``1`` when the data cannot be built or written.
    """
    try:
        config = optional_config(parsed)
        _write_output(parsed, config, data_source(config))
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
    """Build a parser with input, config, output, buffer and changes."""
    parser = build_io_parser(description)
    add_buffer_arg(parser)
    add_changes_arg(parser)
    return parser


def date_report(changes: ReleaseDateChanges, file_exists_cb: FileExistsCb
                ) -> tuple[str, Optional[Callable[[str], None]]]:
    """Return the date change listing and a writer, None when empty.

    The writer overwrites an existing changes file as decided by
    ``file_exists_cb``.
    """
    def write(path: str) -> None:
        """Write the date changes, overwriting as the callback decides."""
        write_date_changes(changes, path, file_exists_callback=file_exists_cb)
    return format_date_changes(changes), (write if changes else None)


def content_report(changes: ReleaseChanges, file_exists_cb: FileExistsCb
                   ) -> tuple[str, Optional[Callable[[str], None]]]:
    """Return the content change listing and a writer, None when empty.

    The writer overwrites an existing changes file as decided by
    ``file_exists_cb``.
    """
    def write(path: str) -> None:
        """Write the content changes, overwriting as the callback decides."""
        write_content_changes(changes, path,
                              file_exists_callback=file_exists_cb)
    return format_content_changes(changes), (write if changes else None)


def run_change_command(
        parsed: argparse.Namespace,
        produce: Callable[[Optional[BacklogOpsConfig], BacklogReleases],
                          tuple[str, Optional[Callable[[str], None]]]],
        require_config: bool = False) -> int:
    """Read, change, write the data, and emit the list of changes.

    The configuration is resolved once, the input is read and validated,
    ``produce`` changes it in place and returns the change listing as text
    together with a callback that writes the same changes to a file. The
    changed data is written to the output file, the listing is printed to
    stdout, and, when ``--changes-file`` is given, the changes are also
    written to that file.

    Args:
        parsed: Parsed command line arguments holding the input, output,
            ``-c`` and ``--changes-file`` options.
        produce: Callable that receives the resolved configuration (or
            None) and the data, changes the data, and returns the change
            listing text and a writer for the change file.
        require_config: When True a missing configuration is reported as an
            error instead of falling back to the built-in defaults.

    Returns:
        ``0`` on success, ``1`` when any step fails.
    """
    try:
        config = (required_config(parsed) if require_config
                  else optional_config(parsed))
        data = read_input(parsed, config)
        listing, write_changes = produce(config, data)
        _write_output(parsed, config, data)
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
