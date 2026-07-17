#! /usr/local/bin/python3
"""Run the IO preset wizard and store the created preset file.

The created file holds a single input or output TableIO preset (a format
configuration with its column-name maps, and a level display for an output
preset). Such a stand-alone file is used wherever an input or output
configuration is taken, by giving its file name.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from backlogops import InputFormatConfig, OutputFormatConfig, preset_wizard, \
    read_io_preset
from backlogops_cli._command_io import parsed_args
from backlogops_cli._migrate_warn import CliPresetMigrateWarnHook
from backlogops_cli._wizard_io import build_wizard_parser, run_wizard_to_file

DESCRIPTION = 'Create an input or output preset config file via a wizard'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the preset wizard command."""
    return build_wizard_parser(DESCRIPTION)


def _read_preset(filename: str) -> InputFormatConfig | OutputFormatConfig:
    """Read a stand-alone preset file, auto-detecting its direction.

    The direction is detected from the file contents; the wizard still
    lets the user switch direction afterwards.
    """
    return read_io_preset(filename, CliPresetMigrateWarnHook(), sys.stderr)


def main(args: Optional[list[str]] = None) -> int:
    """Run the interactive IO preset wizard and write the preset file.

    The wizard asks whether to build an input or an output preset and then
    the settings for it. With ``-i`` an existing preset file is read first
    and used to pre-fill the wizard; its direction (input or output) is
    detected from the file, and pointing ``-i`` at the same file as ``-o``
    edits it in place after confirming the overwrite. The output filename
    receives the ``.cfg`` extension when it is not already present.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the wizard is abandoned or the preset
        cannot be read or written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_wizard_to_file(parsed, preset_wizard, _read_preset,
                              'IO preset configuration')


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
