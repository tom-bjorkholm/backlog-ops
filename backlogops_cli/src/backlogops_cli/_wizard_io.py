#! /usr/local/bin/python3
"""Shared helpers for the configuration and preset wizard commands.

Both wizard commands write a JSON configuration file built interactively
through a ``WizardUiBridge``. They share the same command line shape (an
output file, an optional input file whose contents pre-fill the wizard, a
switch forcing the plain console interface, and a force flag), the same
overwrite check, the same read-run-write-report flow, and the same
crash-safe write. That shared logic lives here; the leading underscore in
the module name keeps it out of the command listing.
"""
# PYTHON_ARGCOMPLETE_OK

# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Optional, TypeVar
from config_as_json import Config
from config_as_json.file_extension import fix_file_extension
from tableio_cfg_json import WizardUiBridge, WizardUiBridgeConsole, \
    make_text_ui_bridge
from backlogops_cli._command_io import add_force_arg, overwrite_callback

CONFIG_EXTENSION = '.cfg'
IN_PROGRESS_SUFFIX = '.in_progress'
_ConfigT = TypeVar('_ConfigT', bound=Config)


def build_wizard_parser(description: str) -> argparse.ArgumentParser:
    """Build a wizard parser with output, input, no-textual and force."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-o', '--output', dest='output', required=True,
                        help='Configuration file to write; the '
                        f'{CONFIG_EXTENSION} extension is added if missing.')
    parser.add_argument('-i', '--input', dest='input',
                        help='Existing configuration file whose contents '
                        'pre-fill the wizard as the starting answers, so you '
                        'edit them instead of starting empty. Use the same '
                        'path as -o to edit that file in place; you are then '
                        f'asked to confirm overwriting it. The '
                        f'{CONFIG_EXTENSION} extension is assumed when the '
                        'file is not found as named.')
    parser.add_argument('--no-textual', dest='no_textual', action='store_true',
                        help='Force the plain console interface instead of '
                        'the Textual full-screen interface.')
    add_force_arg(parser)
    return parser


def _check_overwrite(output: str, force: bool) -> None:
    """Ask before overwriting an existing configuration file.

    The check runs before the wizard, so the user is not asked to confirm
    an overwrite only after entering the whole configuration.
    """
    if Path(output).exists():
        overwrite_callback(force)(output)


def _make_bridge(no_textual: bool) -> WizardUiBridge:
    """Return the console bridge when forced, else the best text bridge.

    Without ``--no-textual`` the factory returns a Textual full-screen
    bridge in a real terminal and a console bridge otherwise, such as when
    input is redirected or under tests.
    """
    if no_textual:
        return WizardUiBridgeConsole(sys.stdout, sys.stdin, sys.stderr)
    return make_text_ui_bridge(sys.stdout, sys.stdin, sys.stderr)


def _read_default(input_file: Optional[str],
                  reader: Callable[[str], _ConfigT]) -> Optional[_ConfigT]:
    """Read the pre-fill file, or return None when none is requested.

    The ``.cfg`` extension is assumed when the named file is not found as
    given, matching how the output filename is completed.
    """
    if input_file is None:
        return None
    path = fix_file_extension(input_file, CONFIG_EXTENSION, for_reading=True)
    if not Path(path).is_file():
        raise ValueError(f'File to read initial values from not found: {path}')
    return reader(path)


def _safe_write(config: Config, output: str) -> None:
    """Write the configuration crash-safely, then move it into place.

    The configuration is first written to a sibling file with an extra
    ``.in_progress`` extension and only then renamed onto the output file.
    The rename replaces the old output file in one atomic step, so a crash
    or a kill at any moment leaves the full configuration in either the old
    output file or the ``.in_progress`` file, never lost between the two.
    """
    in_progress = output + IN_PROGRESS_SUFFIX
    config.write(to_json_filename=in_progress, stderr_file=sys.stderr)
    os.replace(in_progress, output)


def run_wizard_to_file(parsed: argparse.Namespace,
                       wizard: Callable[..., _ConfigT],
                       reader: Callable[[str], _ConfigT], label: str) -> int:
    """Run a wizard, write its configuration to the output file, report.

    When ``parsed.input`` names an existing file it is read first and used
    to pre-fill the wizard, so the user edits those values instead of
    starting from scratch. The output filename receives the ``.cfg``
    extension when it is not already present, an existing output file is
    only overwritten after confirmation (or with ``--force``), and the
    result is written crash-safely through a ``.in_progress`` sibling file.

    Args:
        parsed: Parsed arguments holding ``output``, ``input``, ``force``
            and ``no_textual``.
        wizard: Wizard called with the chosen UI bridge and the pre-fill
            default; it returns a configuration object that knows how to
            write itself.
        reader: Reads the ``input`` file into a default for the wizard.
        label: Human-readable name of what was written, for the message.

    Returns:
        ``0`` on success, ``1`` when the wizard is abandoned or the
        configuration is rejected or cannot be read or written.
    """
    output = fix_file_extension(parsed.output, CONFIG_EXTENSION)
    try:
        default = _read_default(parsed.input, reader)
        _check_overwrite(output, parsed.force)
        config = wizard(_make_bridge(parsed.no_textual), default=default)
        _safe_write(config, output)
    except (ValueError, TypeError, KeyError, EOFError, OSError) as error:
        print(f'Could not create the configuration: {error}', file=sys.stderr)
        return 1
    print(f'{label} written to {output}')
    return 0
