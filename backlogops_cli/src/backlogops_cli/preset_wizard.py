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
import json
import sys
from typing import Optional, TextIO
from config_as_json import MatchConfig, config_factory_from_json
from backlogops import InputFormatConfig, OutputFormatConfig, preset_wizard
from backlogops_cli._command_io import parsed_args
from backlogops_cli._migrate_warn import CliPresetMigrateWarnHook
from backlogops_cli._wizard_io import build_wizard_parser, run_wizard_to_file

DESCRIPTION = 'Create an input or output preset config file via a wizard'

_INPUT_KEYS = ('backlog_to_internal', 'release_to_internal',
               'status_input_map', 'to_internal')
"""Top-level keys that mark a stand-alone input preset file (new or old)."""

_OUTPUT_KEYS = ('backlog_to_external', 'release_to_external',
                'level_display', 'to_external')
"""Top-level keys that mark a stand-alone output preset file (new or old)."""


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the preset wizard command."""
    return build_wizard_parser(DESCRIPTION)


# pylint: disable-next=too-few-public-methods
class _DirectionMatcher:
    """Match a preset file by the presence of any of its direction keys."""

    def __init__(self, keys: tuple[str, ...]) -> None:
        """Store the identifying top-level keys of one preset direction."""
        self._keys = keys

    def __call__(self, json_text: str, _stderr: TextIO) -> bool:
        """Return True when the JSON object holds any identifying key."""
        data = json.loads(json_text)
        return isinstance(data, dict) and any(k in data for k in self._keys)


def _read_preset(filename: str) -> InputFormatConfig | OutputFormatConfig:
    """Read a stand-alone preset file, auto-detecting its direction.

    The direction is chosen by inspecting the file itself: the
    file-column-to-internal maps or a status map mark an input preset,
    while the internal-to-file maps or a level display mark an output
    preset. The wizard still lets the user switch direction afterwards.
    """
    matchers = [
        MatchConfig(_DirectionMatcher(_INPUT_KEYS), InputFormatConfig),
        MatchConfig(_DirectionMatcher(_OUTPUT_KEYS), OutputFormatConfig)]
    config = config_factory_from_json(matchers, CliPresetMigrateWarnHook(),
                                      from_json_filename=filename,
                                      stderr_file=sys.stderr)
    assert isinstance(config, (InputFormatConfig, OutputFormatConfig))
    return config


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
