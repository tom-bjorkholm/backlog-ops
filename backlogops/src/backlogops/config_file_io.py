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

The direction is chosen from the top-level keys of the file. A common
mistake is to pick a complete backlog-ops configuration file where a
stand-alone preset is expected; such a file carries its own identifying
keys and :func:`read_io_preset` rejects it with a clear ``ValueError``
instead of silently reading an empty preset. A missing file, invalid JSON,
or a file that is neither a preset nor a complete configuration is
rejected the same way, so both interfaces can report the mistake.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import json
import os
import sys
from pathlib import Path
from typing import TextIO
from config_as_json import Config, ConfigAutoChangeHook
from backlogops.io_config import InputFormatConfig, OutputFormatConfig

IN_PROGRESS_SUFFIX = '.in_progress'
"""Extra extension of the sibling file written before the atomic move."""

_INPUT_KEYS = ('backlog_to_internal', 'release_to_internal',
               'status_input_map', 'to_internal')
"""Top-level keys that mark a stand-alone input preset file (new or old)."""

_OUTPUT_KEYS = ('backlog_to_external', 'release_to_external',
                'level_display', 'to_external')
"""Top-level keys that mark a stand-alone output preset file (new or old)."""

_COMPLETE_KEYS = ('input_configs', 'output_configs', 'available_teams',
                  'jira', 'gui_display', 'persons', 'teams',
                  'company_work_hours')
"""Top-level keys that mark a complete backlog-ops config (new or old)."""


def _load_preset_json(filename: str) -> dict[str, object]:
    """Return the JSON object stored in a preset file.

    Raises:
        ValueError: The file is missing or unreadable, does not hold valid
            JSON, or its top level is not a JSON object.
    """
    path = Path(filename)
    if not path.is_file():
        raise ValueError(f'Preset file not found: {filename}')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ValueError(f'Cannot read preset file {filename}: '
                         f'{error}') from error
    if not isinstance(data, dict):
        raise ValueError(f'{filename} does not hold a configuration object.')
    return data


def _preset_direction(data: dict[str, object], filename: str) -> str:
    """Return ``'input'`` or ``'output'`` for a stand-alone preset file.

    Raises:
        ValueError: The file is a complete backlog-ops configuration, or is
            neither an input nor an output preset.
    """
    if any(key in data for key in _COMPLETE_KEYS):
        raise ValueError(
            f'{filename} is a complete backlog-ops configuration file, not '
            'a stand-alone input or output preset. Edit it with the '
            'configuration wizard, or choose a stand-alone preset file.')
    if any(key in data for key in _INPUT_KEYS):
        return 'input'
    if any(key in data for key in _OUTPUT_KEYS):
        return 'output'
    raise ValueError(f'{filename} is not a recognised input preset, output '
                     'preset, or backlog-ops configuration file.')


def read_io_preset(filename: str, auto_ch_hook: ConfigAutoChangeHook,
                   stderr_file: TextIO = sys.stderr
                   ) -> InputFormatConfig | OutputFormatConfig:
    """Read a stand-alone preset file, auto-detecting its direction.

    The direction is chosen by inspecting the top-level keys of the file:
    the file-column-to-internal maps or a status map mark an input preset,
    while the internal-to-file maps or a level display mark an output
    preset. A complete backlog-ops configuration file carries its own
    identifying keys and is rejected, as is a file that matches no
    direction, so the caller can report the mistake.

    Args:
        filename: The stand-alone preset file to read.
        auto_ch_hook: Hook notified when an old file needed
            backward-compatible normalization while reading.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The input or output preset read from the file.

    Raises:
        ValueError: The file is missing, is not valid JSON, is a complete
            backlog-ops configuration, or matches neither direction.
    """
    direction = _preset_direction(_load_preset_json(filename), filename)
    config_class = (InputFormatConfig if direction == 'input'
                    else OutputFormatConfig)
    return config_class(from_json_filename=filename, auto_ch_hook=auto_ch_hook,
                        stderr_file=stderr_file)


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
