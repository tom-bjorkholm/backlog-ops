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

from functools import partial
from typing import Optional
from tableio import FileAccess
from tableio_cfg_json import WizardAbort, WizardUiBridge
from backlogops.io_config import InputFormatConfig, OutputFormatConfig, \
    _FormatConfig, make_input_config, make_output_config
from backlogops.table_rows import RELEASE_FIELDS
from backlogops.wizard_helpers import _backlog_map_fields
from backlogops.wizard_navigator import _Navigator, _ask_level_display


_OUT_LEVEL_QUESTION = 'How to write levels (numeric, name or both)'
"""Wizard prompt for how an output preset writes levels."""


_OUT_COLUMN_HEADER = 'Output column (blank drops it)'
"""Header of the renamed-column column in an output rename table."""


_IN_COLUMN_HEADER = 'Input file column (blank field drops it)'
"""Header of the file-column column in an input rename table."""


_IN_STATUS_QUESTION = 'Extra status name mapping for this input preset:'
"""Wizard prompt for an input preset's status-name override map."""


def preset_wizard(ui_bridge: WizardUiBridge, *,
                  default: Optional[InputFormatConfig | OutputFormatConfig]
                  = None, backward: bool = False
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
        default: Input or output preset whose values pre-fill the wizard.
            This can be what a preset file already holds, what the user
            answered before going back in an enclosing wizard, or a
            starting point the application suggests.
        backward: When True, the wizard starts at its last question instead
            of the first. This is set to True when the user asked to go back
            into this wizard from a later question in an enclosing wizard.

    Returns:
        The input or output format configuration, ready to be written to a
        stand-alone configuration file.

    Raises:
        EOFError: The input ended, or the user abandoned the wizard.
    """
    navigator = _Navigator(ui_bridge)
    try:
        return navigator.run(_collect_preset, default, backward)
    except WizardAbort as abort:
        raise EOFError('Configuration abandoned by the user.') from abort


_DIRECTION_QUESTION = 'Create an input or an output preset'
"""Wizard prompt choosing the direction of a stand-alone preset."""


def _preset_direction(default: object) -> Optional[str]:
    """Return the direction of a default preset, or None when unknown."""
    if isinstance(default, InputFormatConfig):
        return 'input'
    if isinstance(default, OutputFormatConfig):
        return 'output'
    return None


def _collect_preset(nav: _Navigator, default: Optional[_FormatConfig]
                    ) -> InputFormatConfig | OutputFormatConfig:
    """Ask the preset direction, then collect that preset's settings."""
    direction = nav.ask_choice(_DIRECTION_QUESTION, ['input', 'output'],
                               default='input',
                               seed=_preset_direction(default))
    if direction == 'input':
        seed = default if isinstance(default, InputFormatConfig) else None
        return _ask_input_config(nav, seed)
    out = default if isinstance(default, OutputFormatConfig) else None
    return _ask_output_config(nav, out)


def _build_input_presets(nav: _Navigator,
                         defaults: Optional[dict[str, InputFormatConfig]]
                         ) -> dict[str, InputFormatConfig]:
    """Ask for a counted list of named input presets."""
    items = list((defaults or {}).items())
    count = nav.ask_count('Number of named input configurations',
                          seed=len(items))
    used: set[str] = set()
    result: dict[str, InputFormatConfig] = {}
    for k in range(count):
        seed = items[k] if k < len(items) else (None, None)
        name, config = nav.level(partial(_ask_input_preset, nav, used, seed))
        used.add(name)
        result[name] = config
    return result


def _build_output_presets(nav: _Navigator,
                          defaults: Optional[dict[str, OutputFormatConfig]]
                          ) -> dict[str, OutputFormatConfig]:
    """Ask for a counted list of named output presets."""
    items = list((defaults or {}).items())
    count = nav.ask_count('Number of named output configurations',
                          seed=len(items))
    used: set[str] = set()
    result: dict[str, OutputFormatConfig] = {}
    for k in range(count):
        seed = items[k] if k < len(items) else (None, None)
        name, config = nav.level(partial(_ask_output_preset, nav, used, seed))
        used.add(name)
        result[name] = config
    return result


def _ask_input_config(nav: _Navigator,
                      default: Optional[InputFormatConfig] = None
                      ) -> InputFormatConfig:
    """Ask one input preset's format, file-to-internal maps and status map."""
    tableio = nav.ask_tableio(FileAccess.READ,
                              seed=default.tableio if default else None)
    backlog_map = nav.level(lambda: nav.ask_renames(
        _backlog_map_fields(), True, _IN_COLUMN_HEADER, is_input=True,
        seed=default.backlog_to_internal if default else None))
    release_map = nav.level(lambda: nav.ask_renames(
        list(RELEASE_FIELDS), False, _IN_COLUMN_HEADER, is_input=True,
        seed=default.release_to_internal if default else None))
    status_map = nav.level(lambda: nav.ask_status_map(
        _IN_STATUS_QUESTION,
        seed=default.status_input_map if default else None))
    return make_input_config(tableio, backlog_map, release_map, status_map)


def _ask_output_config(nav: _Navigator,
                       default: Optional[OutputFormatConfig] = None
                       ) -> OutputFormatConfig:
    """Ask one output preset's format, both maps and level display."""
    tableio = nav.ask_tableio(FileAccess.CREATE,
                              seed=default.tableio if default else None)
    backlog_map = nav.level(lambda: nav.ask_renames(
        _backlog_map_fields(), True, _OUT_COLUMN_HEADER,
        seed=default.backlog_to_external if default else None))
    release_map = nav.level(lambda: nav.ask_renames(
        list(RELEASE_FIELDS), False, _OUT_COLUMN_HEADER,
        seed=default.release_to_external if default else None))
    display = _ask_level_display(nav, _OUT_LEVEL_QUESTION,
                                 default.level_display if default else None)
    return make_output_config(tableio, backlog_map, release_map, display)


def _ask_input_preset(nav: _Navigator, used: set[str],
                      seed: tuple[Optional[str], Optional[InputFormatConfig]]
                      = (None, None)) -> tuple[str, InputFormatConfig]:
    """Ask one named input preset: name, format and both rename maps."""
    name = nav.ask_preset_name('Preset name (letters and digits)', used,
                               seed=seed[0])
    return name, _ask_input_config(nav, seed[1])


def _ask_output_preset(nav: _Navigator, used: set[str],
                       seed: tuple[Optional[str], Optional[OutputFormatConfig]]
                       = (None, None)) -> tuple[str, OutputFormatConfig]:
    """Ask one named output preset: name, format, maps and level display."""
    name = nav.ask_preset_name('Preset name (letters and digits)', used,
                               seed=seed[0])
    return name, _ask_output_config(nav, seed[1])
