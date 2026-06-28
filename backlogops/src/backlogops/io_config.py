#! /usr/local/bin/python3
"""Configuration for reading and writing tables with TableIO.

A backlog and its releases are read from and written to tabular files
(Excel, ODS, CSV, and more) using TableIO. The durable TableIO settings
for one input or one output are stored as a :class:`TioJsonConfig`. On
top of that this module adds per-table column-name maps, so the columns
in a user's file can have other names than the internal field names of
the data model.

An input endpoint is described by an :class:`InputFormatConfig` and an
output endpoint by an :class:`OutputFormatConfig`. Both wrap one
``TioJsonConfig`` and the direction-specific column-name maps:

* an input endpoint carries one map per table, ``backlog_to_internal``
  and ``release_to_internal``, each translating an external file column
  name to an internal field name; several external names may map to the
  same internal field;
* an output endpoint carries one map per table, ``backlog_to_external``
  and ``release_to_external``, each translating an internal field name to
  the external column name to write.

Every input, output and GUI map honours three cases for a column name: a
name absent from the map is read, written or shown unchanged, a name
mapped to another string is renamed, and a name mapped to None drops that
column (for an input map the named file column is discarded).
The :class:`GuiDisplayConfig` carries the same per-table maps and level
display, but no TableIO endpoint, deciding how a backlog and its releases
are shown on screen.

:func:`resolve_input_config` and :func:`resolve_output_config` turn a
command-line value into such a configuration. The value may be empty
(then the format is inferred from the data file name extension), a preset
name (looked up among named presets stored elsewhere, typically in the
teams configuration file), or the name of a stand-alone configuration
file.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar, NoReturn, Optional, TextIO, override
from config_as_json import Config, ConfigAutoChangeHook, ConfigNesting, \
    ConfigNestingKind, ConfigPath, InvalidConfiguration, \
    MemberValidationStep, MemberValidator, NestedConfigs, ParseConverter, \
    PathOrStr, ReadOldConfiguration, RocfKeyMove, RocfValueMigration, \
    RocfValueWrite, ValidationPlan
from tableio import Capabilities, FileAccess, access_capabilities
from tableio_cfg_json import TioJsonConfig, tio_json_config_default
from backlogops.backlog import Status
from backlogops.backlog_helpers import convert_to_enum, report_bad_value, \
    report_wrong_type
from backlogops.levels import LevelDisplay
from backlogops.table_rows import RELEASE_FIELDS

EXTENSION_FORMATS: dict[str, str] = {
    '.csv': 'CSV', '.xlsx': 'Excel', '.xls': 'Excel', '.ods': 'ODS',
    '.html': 'HTML', '.htm': 'HTML', '.tex': 'LaTeX', '.md': 'md',
    '.docx': 'docx', '.odt': 'odt', '.pdf': 'pdf', '.rst': 'reST',
    '.rtf': 'rtf', '.txt': 'txt'}
"""Map a data file name extension to a TableIO format name."""

PRESET_NAME_RE = re.compile(r'^[A-Za-z0-9]+$')
"""A configuration value made only of letters and digits is a preset."""


class _DisplayMapReadOldConfig(ReadOldConfiguration):
    """Migrate older output or GUI display files to the split maps.

    The single ``to_external`` map of an older output file is moved to the
    backlog map; this move is a no-op for a GUI file or a file that never
    had a map. Any absent backlog or release map then defaults to empty,
    and a missing level display defaults to BOTH. The enum member itself
    is supplied, not its name, because the missing value is inserted after
    the read-side scalar converters have run and so would otherwise stay
    an unconverted string.
    """

    def get_json_key_moves(self) -> list[RocfKeyMove]:
        """Move an older single output map into the backlog map."""
        return [RocfKeyMove(old_path=('to_external',),
                            new_path=('backlog_to_external',))]

    def get_missing_path_values(self) -> dict[ConfigPath, object]:
        """Supply default maps and level display for an older file."""
        return {('backlog_to_external',): {}, ('release_to_external',): {},
                ('level_display',): LevelDisplay.BOTH}


# pylint: disable-next=too-few-public-methods
class _ColumnMapValidator(MemberValidator):
    """Validate a column-name map of string keys to string-or-None values.

    Each key is an internal field name and each value is either the
    external column name to use or None to drop the column. The member
    must be a dict; every key must be a string and every value must be a
    string or None.
    """

    @override
    def validate_member(self, config: Config, member_name: str,
                        member_value: object,
                        stderr_file: TextIO = sys.stderr) -> object:
        """Check the map is a dict of string keys to string-or-None values."""
        _ = config
        if not isinstance(member_value, dict):
            self._reject(f'{member_name} must be a mapping', stderr_file)
        for key, value in member_value.items():
            if not isinstance(key, str) or not (value is None
                                                or isinstance(value, str)):
                self._reject(f'{member_name} maps {key!r} to {value!r}; keys '
                             'must be strings and values a string or null',
                             stderr_file)
        return member_value

    @staticmethod
    def _reject(detail: str, stderr_file: TextIO) -> NoReturn:
        """Report an invalid column-name map and raise."""
        message = f'Invalid configuration: {detail}.'
        print(message, file=stderr_file)
        raise InvalidConfiguration(message)


def parse_status_input_map(member_name: str, raw: object,
                           stderr_file: TextIO = sys.stderr
                           ) -> dict[str, Status]:
    """Return a validated status-name map from raw configuration data.

    Each key is an external status name and each value is a Status (or a
    Status member name such as ``'IN_PROGRESS'``). Keys must be non-empty
    strings and must be unique case-insensitively, because a status name
    is matched without regard to case when reading a backlog. Each value
    is converted to a Status member.

    Args:
        member_name: The member name used in any error message.
        raw: The raw configuration value to validate and convert.
        stderr_file: The file to report errors to.

    Returns:
        The status names mapped to their Status members.

    Raises:
        TypeError: If ``raw`` is not a dict or a value is not a Status.
        ValueError: If a key is empty or duplicates another (case-insensitive).
    """
    if not isinstance(raw, dict):
        report_wrong_type(member_name, raw, dict, stderr_file, 'Status map')
    result: dict[str, Status] = {}
    seen: dict[str, str] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or key == '':
            report_bad_value(member_name, key,
                             'status name must be a non-empty string',
                             stderr_file, 'Status map')
        lowered = key.lower()
        if lowered in seen:
            report_bad_value(member_name, key,
                             f'duplicates {seen[lowered]!r} '
                             '(case-insensitive)', stderr_file, 'Status map')
        seen[lowered] = key
        status = convert_to_enum(f'{member_name}[{key}]', value, Status,
                                 stderr_file)
        assert isinstance(status, Status)
        result[key] = status
    return result


# pylint: disable-next=too-few-public-methods
class _StatusMapValidator(MemberValidator):
    """Convert and validate a status-name-to-Status map member.

    The member maps each external status name to a Status member. It is
    used for the global map on the top-level configuration and for the
    per-input-preset override map.
    """

    @override
    def validate_member(self, config: Config, member_name: str,
                        member_value: object,
                        stderr_file: TextIO = sys.stderr) -> object:
        """Return the member as a validated ``dict[str, Status]``."""
        _ = config
        return parse_status_input_map(member_name, member_value, stderr_file)


def _capabilities(file_access: FileAccess, stderr_file: TextIO
                  ) -> Capabilities:
    """Return the TableIO capabilities implied by a file access mode."""
    return access_capabilities(file_access, error_file=stderr_file)


def _tio_default(file_access: FileAccess, format_name: Optional[str] = None,
                 stderr_file: TextIO = sys.stderr) -> TioJsonConfig:
    """Return a default TableIO config for a format and file access."""
    return tio_json_config_default(
        capabilities=_capabilities(file_access, stderr_file),
        file_access=file_access, format_name=format_name,
        stderr_file=stderr_file)


def _tio_from_json(file_access: FileAccess, from_json_data_text: Optional[str],
                   from_json_filename: Optional[PathOrStr],
                   stderr_file: TextIO) -> TioJsonConfig:
    """Return a TableIO config read from JSON for a file access mode."""
    return TioJsonConfig(capabilities=_capabilities(file_access, stderr_file),
                         file_access=file_access,
                         from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename,
                         stderr_file=stderr_file)


class _FormatConfig(Config):
    """Shared behavior for one input or output TableIO endpoint config.

    A concrete subclass fixes the file access mode and the names of its
    column-name map members, and declares those map members before calling
    the constructor. The wrapped ``TioJsonConfig`` is created here and
    declared as a nested configuration so it reads and writes itself.
    """

    _FILE_ACCESS: ClassVar[FileAccess]
    _MAP_NAMES: ClassVar[tuple[str, ...]]
    _UNCHECKED_EXTRA: ClassVar[tuple[str, ...]] = ()

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create default settings or read them from a JSON source."""
        self.tableio: TioJsonConfig = _tio_default(self._FILE_ACCESS,
                                                   stderr_file=stderr_file)
        self._unchecked_dicts = list(self._MAP_NAMES) + \
            list(self._UNCHECKED_EXTRA)
        Config.__init__(self, from_json_data_text=from_json_data_text,
                        from_json_filename=from_json_filename,
                        auto_ch_hook=auto_ch_hook, stderr_file=stderr_file)

    def _tio_factory(self, *, from_json_data_text: Optional[str] = None,
                     from_json_filename: Optional[PathOrStr] = None,
                     stderr_file: TextIO = sys.stderr) -> TioJsonConfig:
        """Construct the nested TableIO config from JSON when reading."""
        return _tio_from_json(self._FILE_ACCESS, from_json_data_text,
                              from_json_filename, stderr_file)

    def _map_validator(self) -> MemberValidator:
        """Return the validator applied to each column-name map member."""
        return _ColumnMapValidator()

    @override
    def nested_configs(self) -> NestedConfigs:
        """Declare the wrapped TableIO config as a nested configuration."""
        return {'tableio': ConfigNesting(kind=ConfigNestingKind.MEMBER,
                                         config_type=TioJsonConfig,
                                         factory_function=self._tio_factory)}

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check each column-name map with this endpoint's validator."""
        _ = stderr_file
        return [MemberValidationStep(member_names=list(self._MAP_NAMES),
                                     validator=self._map_validator())]


def _release_only_map(value: object) -> object:
    """Keep only old input mappings whose target is a release field.

    A release table has no extra fields, so a mapping that targets a
    backlog-only field is meaningless for the releases input map and is
    dropped when an older single map is split.
    """
    assert isinstance(value, dict)
    result: dict[object, object] = {}
    for source, target in value.items():
        if target in RELEASE_FIELDS:
            result[source] = target
    return result


class _InputMapReadOldConfig(ReadOldConfiguration):
    """Split an older single input map into the two per-table maps.

    An older input file stored one ``to_internal`` map applied to every
    table. That map is copied into ``backlog_to_internal`` unchanged and
    into ``release_to_internal`` with only the entries that target a
    release field kept. A file that lacks the old map gets both maps
    defaulted to empty.
    """

    def get_value_migrations(self) -> list[RocfValueMigration]:
        """Copy the old single input map into the two per-table maps."""
        return [RocfValueMigration(
            old_path=('to_internal',),
            writes=[RocfValueWrite(new_path=('backlog_to_internal',)),
                    RocfValueWrite(new_path=('release_to_internal',),
                                   transform_value=_release_only_map)])]

    def get_missing_path_values(self) -> dict[ConfigPath, object]:
        """Supply empty input and status maps when an old file omits them."""
        return {('backlog_to_internal',): {}, ('release_to_internal',): {},
                ('status_input_map',): {}}


class InputFormatConfig(_FormatConfig):
    """TableIO input endpoint with per-table file-to-internal maps.

    The backlog table and the releases table each have their own map from
    a file column name to an internal field name (``backlog_to_internal``
    and ``release_to_internal``); each honours the three cases of
    :func:`backlogops.table_rows.apply_column_map`: a file column absent
    from the map is read unchanged, a mapped file column is renamed to the
    internal field, and a file column mapped to None is discarded. Several
    file columns may map to the same internal field. The maps default to
    empty; an older file storing a single ``to_internal`` map has it copied
    into both maps, keeping only release-field targets in the releases map.

    The ``status_input_map`` maps extra external status names to Status
    members (matched case-insensitively when reading), overriding the
    global map of the top-level configuration for this preset. It defaults
    to empty and is absent from an older file.
    """

    _FILE_ACCESS = FileAccess.READ
    _MAP_NAMES = ('backlog_to_internal', 'release_to_internal')
    _UNCHECKED_EXTRA = ('status_input_map',)
    backlog_to_internal: dict[str, Optional[str]]
    release_to_internal: dict[str, Optional[str]]
    status_input_map: dict[str, Status]

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create the input map defaults, then run the shared constructor."""
        self.backlog_to_internal = {}
        self.release_to_internal = {}
        self.status_input_map = {}
        _FormatConfig.__init__(self, from_json_data_text=from_json_data_text,
                               from_json_filename=from_json_filename,
                               auto_ch_hook=auto_ch_hook,
                               stderr_file=stderr_file)

    @override
    def _get_read_old_config(self) -> ReadOldConfiguration:
        """Return the migration that splits an older single input map."""
        return _InputMapReadOldConfig()

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check the column maps, then convert the status input map."""
        plan = _FormatConfig.get_validation_plan(self, stderr_file)
        validator = _StatusMapValidator()
        step = MemberValidationStep(member_names=['status_input_map'],
                                    validator=validator)
        return plan + [step]


class OutputFormatConfig(_FormatConfig):
    """TableIO output endpoint with per-table internal-to-external maps.

    The backlog table and the releases table each have their own
    internal-to-external column-name map (``backlog_to_external`` and
    ``release_to_external``); each honours the three cases of
    :func:`backlogops.table_rows.apply_column_map`. The endpoint also
    carries a :class:`LevelDisplay`, deciding whether a backlog item level
    is written as its number, its name, or both. The maps default to empty
    and the display defaults to :data:`LevelDisplay.BOTH`; any of them may
    be absent from an older file, in which case the default applies.
    """

    _FILE_ACCESS = FileAccess.CREATE
    _MAP_NAMES = ('backlog_to_external', 'release_to_external')
    backlog_to_external: dict[str, Optional[str]]
    release_to_external: dict[str, Optional[str]]
    level_display: LevelDisplay

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create the output defaults, then run the shared constructor."""
        self.backlog_to_external = {}
        self.release_to_external = {}
        self.level_display = LevelDisplay.BOTH
        _FormatConfig.__init__(self, from_json_data_text=from_json_data_text,
                               from_json_filename=from_json_filename,
                               auto_ch_hook=auto_ch_hook,
                               stderr_file=stderr_file)

    @override
    def parse_converters(self) -> dict[str, ParseConverter]:
        """Parse the level display member from its enum member name."""
        return {'level_display': self.get_converter_dict(LevelDisplay)}

    @override
    def _get_read_old_config(self) -> ReadOldConfiguration:
        """Return the migration that splits the map and defaults display."""
        return _DisplayMapReadOldConfig()


def make_input_config(tableio: TioJsonConfig,
                      backlog_to_internal: dict[str, Optional[str]],
                      release_to_internal: dict[str, Optional[str]],
                      status_input_map: Optional[dict[str, Status]] = None,
                      stderr_file: TextIO = sys.stderr) -> InputFormatConfig:
    """Return an input config from a TableIO config, maps and status map."""
    config = InputFormatConfig(stderr_file=stderr_file)
    config.tableio = tableio
    config.backlog_to_internal = dict(backlog_to_internal)
    config.release_to_internal = dict(release_to_internal)
    config.status_input_map = dict(status_input_map) if status_input_map \
        else {}
    return config


def make_output_config(tableio: TioJsonConfig,
                       backlog_to_external: dict[str, Optional[str]],
                       release_to_external: dict[str, Optional[str]],
                       level_display: LevelDisplay = LevelDisplay.BOTH,
                       stderr_file: TextIO = sys.stderr) -> OutputFormatConfig:
    """Return an output config from a TableIO config, maps and display."""
    config = OutputFormatConfig(stderr_file=stderr_file)
    config.tableio = tableio
    config.backlog_to_external = dict(backlog_to_external)
    config.release_to_external = dict(release_to_external)
    config.level_display = level_display
    return config


class GuiDisplayConfig(Config):
    """How a backlog and its releases are shown in the GUI.

    This mirrors the display part of an :class:`OutputFormatConfig`,
    without the TableIO endpoint configuration. It carries the per-table
    column-name maps ``backlog_to_external`` and ``release_to_external``
    (each honouring the three cases of
    :func:`backlogops.table_rows.apply_column_map`) and a
    :class:`LevelDisplay`. The maps default to empty and the display
    defaults to :data:`LevelDisplay.BOTH`; any of them may be absent from
    an older file, in which case the default applies.
    """

    backlog_to_external: dict[str, Optional[str]]
    release_to_external: dict[str, Optional[str]]
    level_display: LevelDisplay

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create the display defaults, then read them from JSON."""
        self.backlog_to_external = {}
        self.release_to_external = {}
        self.level_display = LevelDisplay.BOTH
        self._unchecked_dicts = ['backlog_to_external', 'release_to_external']
        Config.__init__(self, from_json_data_text=from_json_data_text,
                        from_json_filename=from_json_filename,
                        stderr_file=stderr_file)

    @override
    def parse_converters(self) -> dict[str, ParseConverter]:
        """Parse the level display member from its enum member name."""
        return {'level_display': self.get_converter_dict(LevelDisplay)}

    @override
    def _get_read_old_config(self) -> ReadOldConfiguration:
        """Return the migration that defaults the maps and the display."""
        return _DisplayMapReadOldConfig()

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check each column-name map allows a string or None value."""
        _ = stderr_file
        return [MemberValidationStep(
            member_names=['backlog_to_external', 'release_to_external'],
            validator=_ColumnMapValidator())]


def _format_from_suffix(data_file: PathOrStr) -> str:
    """Return the TableIO format name implied by a data file extension."""
    suffix = Path(data_file).suffix.lower()
    format_name = EXTENSION_FORMATS.get(suffix)
    if format_name is None:
        known = ', '.join(sorted(EXTENSION_FORMATS))
        raise ValueError(f'Cannot infer a TableIO format from {suffix!r}. '
                         f'Known extensions: {known}.')
    return format_name


def _default_input(data_file: PathOrStr,
                   stderr_file: TextIO) -> InputFormatConfig:
    """Return an input config with the format inferred from the file name."""
    config = InputFormatConfig(stderr_file=stderr_file)
    config.tableio = _tio_default(FileAccess.READ,
                                  _format_from_suffix(data_file), stderr_file)
    return config


def _default_output(data_file: PathOrStr,
                    stderr_file: TextIO) -> OutputFormatConfig:
    """Return an output config with the format inferred from the file name."""
    config = OutputFormatConfig(stderr_file=stderr_file)
    config.tableio = _tio_default(FileAccess.CREATE,
                                  _format_from_suffix(data_file), stderr_file)
    return config


def _preset(value: str, presets: Optional[Mapping[str, _FormatConfig]]
            ) -> _FormatConfig:
    """Return the named preset, or raise when it cannot be found."""
    if presets is None or value not in presets:
        available = ', '.join(sorted(presets)) if presets else 'none'
        raise ValueError(f'Unknown configuration preset {value!r}. '
                         f'Available presets: {available}.')
    return presets[value]


def resolve_input_config(
        value: Optional[str], *, data_file: PathOrStr,
        presets: Optional[dict[str, InputFormatConfig]] = None,
        auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
        stderr_file: TextIO = sys.stderr) -> InputFormatConfig:
    """Resolve a command-line input config value to an input config.

    An empty ``value`` infers the format from ``data_file``. A value of
    only letters and digits is a preset name looked up in ``presets``.
    Any other value is the path of a stand-alone input config file.

    Args:
        value: The ``--input-config`` value, or None for inference.
        data_file: The input data file, used for format inference.
        presets: Named input presets, typically from the teams config.
        auto_ch_hook: Hook notified when a stand-alone input config file
            needed backward-compatible normalization while reading.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The resolved input configuration.

    Raises:
        ValueError: The format cannot be inferred or the preset is unknown.
    """
    if value is None:
        return _default_input(data_file, stderr_file)
    if PRESET_NAME_RE.match(value):
        preset = _preset(value, presets)
        assert isinstance(preset, InputFormatConfig)
        return preset
    return InputFormatConfig(from_json_filename=value,
                             auto_ch_hook=auto_ch_hook,
                             stderr_file=stderr_file)


def resolve_output_config(
        value: Optional[str], *, data_file: PathOrStr,
        presets: Optional[dict[str, OutputFormatConfig]] = None,
        auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
        stderr_file: TextIO = sys.stderr) -> OutputFormatConfig:
    """Resolve a command-line output config value to an output config.

    An empty ``value`` infers the format from ``data_file``. A value of
    only letters and digits is a preset name looked up in ``presets``.
    Any other value is the path of a stand-alone output config file.

    Args:
        value: The ``--output-config`` value, or None for inference.
        data_file: The output data file, used for format inference.
        presets: Named output presets, typically from the teams config.
        auto_ch_hook: Hook notified when a stand-alone output config file
            needed backward-compatible normalization while reading.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The resolved output configuration.

    Raises:
        ValueError: The format cannot be inferred or the preset is unknown.
    """
    if value is None:
        return _default_output(data_file, stderr_file)
    if PRESET_NAME_RE.match(value):
        preset = _preset(value, presets)
        assert isinstance(preset, OutputFormatConfig)
        return preset
    return OutputFormatConfig(from_json_filename=value,
                              auto_ch_hook=auto_ch_hook,
                              stderr_file=stderr_file)
