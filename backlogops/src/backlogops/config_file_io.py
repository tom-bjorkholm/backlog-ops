#! /usr/local/bin/python3
"""Read a stand-alone preset file and write a configuration crash-safely.

Two helpers shared by the command line and the graphical interface. Both
interfaces let the user build a configuration or a stand-alone preset file
through a wizard, optionally pre-filled from an existing file, and then
write the result. :func:`read_io_preset` reads a stand-alone preset file
and detects whether it is an input or an output preset from its own
contents. :func:`safe_write_config` writes any configuration so that a
crash or a kill at any moment leaves the whole configuration in either the
old file or a sibling ``.in_progress`` file, never lost between the two.

The detection uses ``config_as_json.config_factory_from_json``, which
terminates the process with ``SystemExit`` when the file is missing, is not
valid JSON, or matches no known direction. That suits the command line; a
graphical caller should catch ``SystemExit`` and report it.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import json
import os
import sys
from typing import TextIO
from config_as_json import Config, ConfigAutoChangeHook, MatchConfig, \
    config_factory_from_json
from backlogops.io_config import InputFormatConfig, OutputFormatConfig

IN_PROGRESS_SUFFIX = '.in_progress'
"""Extra extension of the sibling file written before the atomic move."""

_INPUT_KEYS = ('backlog_to_internal', 'release_to_internal',
               'status_input_map', 'to_internal')
"""Top-level keys that mark a stand-alone input preset file (new or old)."""

_OUTPUT_KEYS = ('backlog_to_external', 'release_to_external',
                'level_display', 'to_external')
"""Top-level keys that mark a stand-alone output preset file (new or old)."""


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


def read_io_preset(filename: str, auto_ch_hook: ConfigAutoChangeHook,
                   stderr_file: TextIO = sys.stderr
                   ) -> InputFormatConfig | OutputFormatConfig:
    """Read a stand-alone preset file, auto-detecting its direction.

    The direction is chosen by inspecting the file itself: the
    file-column-to-internal maps or a status map mark an input preset,
    while the internal-to-file maps or a level display mark an output
    preset.

    Args:
        filename: The stand-alone preset file to read.
        auto_ch_hook: Hook notified when an old file needed
            backward-compatible normalization while reading.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The input or output preset read from the file.

    Raises:
        SystemExit: The file is missing, is not valid JSON, or matches
            neither an input nor an output preset.
    """
    matchers = [
        MatchConfig(_DirectionMatcher(_INPUT_KEYS), InputFormatConfig),
        MatchConfig(_DirectionMatcher(_OUTPUT_KEYS), OutputFormatConfig)]
    config = config_factory_from_json(matchers, auto_ch_hook,
                                      from_json_filename=filename,
                                      stderr_file=stderr_file)
    assert isinstance(config, (InputFormatConfig, OutputFormatConfig))
    return config


def safe_write_config(config: Config, output: str,
                      stderr_file: TextIO = sys.stderr) -> None:
    """Write the configuration crash-safely, then move it into place.

    The configuration is first written to a sibling file with an extra
    ``.in_progress`` extension and only then renamed onto the output file.
    The rename replaces the old output file in one atomic step, so a crash
    or a kill at any moment leaves the full configuration in either the old
    output file or the ``.in_progress`` file, never lost between the two.

    Args:
        config: The configuration that knows how to write itself.
        output: The destination file to create or replace.
        stderr_file: Stream used for user-facing diagnostics.
    """
    in_progress = output + IN_PROGRESS_SUFFIX
    config.write(to_json_filename=in_progress, stderr_file=stderr_file)
    os.replace(in_progress, output)
