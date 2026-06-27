#! /usr/local/bin/python3
"""Interactively create a stand-alone TableIO input or output preset.

The public :func:`preset_wizard` asks whether to build an input or an
output preset and then the same questions the full configuration wizard
asks for one preset of that direction: the TableIO endpoint format and
options, how the backlog and releases file columns relate to the internal
fields, and, for an output preset, how levels are written. A stand-alone
preset has no name of its own; the file it is written to is the preset.

The ``_build_input_presets`` and ``_build_output_presets`` collectors ask a
counted list of *named* presets and are reused by the full configuration
wizard, where each preset additionally has a name.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from tableio import FileAccess
from tableio_cfg_json import WizardAbort, WizardUiBridge
from backlogops.io_config import InputFormatConfig, OutputFormatConfig, \
    make_input_config, make_output_config
from backlogops.table_rows import RELEASE_FIELDS
from backlogops.wizard_helpers import _Navigator, _ask_level_display, \
    _backlog_map_fields


_OUT_LEVEL_QUESTION = 'How to write levels (numeric, name or both)'
"""Wizard prompt for how an output preset writes levels."""


_OUT_COLUMN_HEADER = 'Output column (blank drops it)'
"""Header of the renamed-column column in an output rename table."""


_IN_COLUMN_HEADER = 'Input file column (blank field drops it)'
"""Header of the file-column column in an input rename table."""


_IN_STATUS_QUESTION = 'Extra status name mapping for this input preset:'
"""Wizard prompt for an input preset's status-name override map."""


def preset_wizard(ui_bridge: WizardUiBridge
                  ) -> InputFormatConfig | OutputFormatConfig:
    """Interactively create a stand-alone input or output TableIO preset.

    The wizard first asks whether to build an input or an output preset,
    then asks exactly the questions the full configuration wizard asks for
    one preset of that direction: the TableIO endpoint format and options,
    how the backlog and releases file columns relate to the internal
    fields, and, for an output preset, how levels are written. A
    stand-alone preset has no name of its own; the file it is written to is
    the preset, referred to by its file name where an input or output
    configuration is taken.

    Args:
        ui_bridge: Bridge between the wizard and the user interface.

    Returns:
        The input or output format configuration, ready to be written to a
        stand-alone configuration file.

    Raises:
        EOFError: The input ended, or the user abandoned the wizard.
    """
    navigator = _Navigator(ui_bridge)
    try:
        return navigator.run(_collect_preset)
    except WizardAbort as abort:
        raise EOFError('Configuration abandoned by the user.') from abort


_DIRECTION_QUESTION = 'Create an input or an output preset'
"""Wizard prompt choosing the direction of a stand-alone preset."""


def _collect_preset(nav: _Navigator) -> InputFormatConfig | OutputFormatConfig:
    """Ask the preset direction, then collect that preset's settings."""
    direction = nav.ask_choice(_DIRECTION_QUESTION, ['input', 'output'],
                               default='input')
    if direction == 'input':
        return _ask_input_config(nav)
    return _ask_output_config(nav)


def _build_input_presets(nav: _Navigator) -> dict[str, InputFormatConfig]:
    """Ask for a counted list of named input presets."""
    count = nav.ask_count('Number of named input configurations')
    used: set[str] = set()
    result: dict[str, InputFormatConfig] = {}
    for _ in range(count):
        name, config = nav.level(lambda: _ask_input_preset(nav, used))
        used.add(name)
        result[name] = config
    return result


def _build_output_presets(nav: _Navigator) -> dict[str, OutputFormatConfig]:
    """Ask for a counted list of named output presets."""
    count = nav.ask_count('Number of named output configurations')
    used: set[str] = set()
    result: dict[str, OutputFormatConfig] = {}
    for _ in range(count):
        name, config = nav.level(lambda: _ask_output_preset(nav, used))
        used.add(name)
        result[name] = config
    return result


def _ask_input_config(nav: _Navigator) -> InputFormatConfig:
    """Ask one input preset's format, file-to-internal maps and status map."""
    tableio = nav.ask_tableio(FileAccess.READ)
    backlog_map = nav.level(
        lambda: nav.ask_renames(_backlog_map_fields(), True, _IN_COLUMN_HEADER,
                                is_input=True))
    release_map = nav.level(
        lambda: nav.ask_renames(list(RELEASE_FIELDS), False, _IN_COLUMN_HEADER,
                                is_input=True))
    status_map = nav.level(lambda: nav.ask_status_map(_IN_STATUS_QUESTION))
    return make_input_config(tableio, backlog_map, release_map, status_map)


def _ask_output_config(nav: _Navigator) -> OutputFormatConfig:
    """Ask one output preset's format, both maps and level display."""
    tableio = nav.ask_tableio(FileAccess.CREATE)
    backlog_map = nav.level(
        lambda: nav.ask_renames(_backlog_map_fields(), True,
                                _OUT_COLUMN_HEADER))
    release_map = nav.level(
        lambda: nav.ask_renames(list(RELEASE_FIELDS), False,
                                _OUT_COLUMN_HEADER))
    display = _ask_level_display(nav, _OUT_LEVEL_QUESTION)
    return make_output_config(tableio, backlog_map, release_map, display)


def _ask_input_preset(nav: _Navigator,
                      used: set[str]) -> tuple[str, InputFormatConfig]:
    """Ask one named input preset: name, format and both rename maps."""
    name = nav.ask_preset_name('Preset name (letters and digits)', used)
    return name, _ask_input_config(nav)


def _ask_output_preset(nav: _Navigator,
                       used: set[str]) -> tuple[str, OutputFormatConfig]:
    """Ask one named output preset: name, format, maps and level display."""
    name = nav.ask_preset_name('Preset name (letters and digits)', used)
    return name, _ask_output_config(nav)
