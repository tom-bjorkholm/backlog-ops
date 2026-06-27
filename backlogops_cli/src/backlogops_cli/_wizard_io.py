#! /usr/local/bin/python3
"""Shared helpers for the configuration and preset wizard commands.

Both wizard commands write a JSON configuration file built interactively
through a ``WizardUiBridge``. They share the same command line shape (an
output file, a switch forcing the plain console interface, and a force
flag), the same overwrite check, and the same run-write-report flow. That
shared logic lives here; the leading underscore in the module name keeps
it out of the command listing.
"""
# PYTHON_ARGCOMPLETE_OK

# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from collections.abc import Callable
from pathlib import Path
from config_as_json import Config
from config_as_json.file_extension import fix_file_extension
from tableio_cfg_json import WizardUiBridge, WizardUiBridgeConsole, \
    make_text_ui_bridge
from backlogops_cli._command_io import add_force_arg, overwrite_callback

CONFIG_EXTENSION = '.cfg'


def build_wizard_parser(description: str) -> argparse.ArgumentParser:
    """Build a wizard parser with output, no-textual and force options."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-o', '--output', dest='output', required=True,
                        help='Configuration file to write; the '
                        f'{CONFIG_EXTENSION} extension is added if missing.')
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


def run_wizard_to_file(parsed: argparse.Namespace,
                       wizard: Callable[[WizardUiBridge], Config],
                       label: str) -> int:
    """Run a wizard, write its configuration to the output file, report.

    The output filename receives the ``.cfg`` extension when it is not
    already present.

    Args:
        parsed: Parsed arguments holding ``output``, ``force`` and
            ``no_textual``.
        wizard: Wizard called with the chosen UI bridge; it returns a
            configuration object that knows how to write itself.
        label: Human-readable name of what was written, for the message.

    Returns:
        ``0`` on success, ``1`` when the wizard is abandoned or the
        configuration is rejected or cannot be written.
    """
    output = fix_file_extension(parsed.output, CONFIG_EXTENSION)
    try:
        _check_overwrite(output, parsed.force)
        config = wizard(_make_bridge(parsed.no_textual))
        config.write(to_json_filename=output, stderr_file=sys.stderr)
    except (ValueError, TypeError, KeyError, EOFError, OSError) as error:
        print(f'Could not create the configuration: {error}', file=sys.stderr)
        return 1
    print(f'{label} written to {output}')
    return 0
