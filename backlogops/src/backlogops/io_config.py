#! /usr/local/bin/python3
"""Configuration for reading and writing tables with TableIO.

A backlog and its releases are read from and written to tabular files
(Excel, ODS, CSV, and more) using TableIO. The durable TableIO settings
for one input or one output are stored as a :class:`TioJsonConfig`. On
top of that this module adds a per-endpoint column-name map, so the
columns shown to a user can have other names than the internal field
names of the data model.

An input endpoint is described by an :class:`InputFormatConfig` and an
output endpoint by an :class:`OutputFormatConfig`. Both wrap one
``TioJsonConfig`` and one direction-specific name map:

* an input map (``to_internal``) translates an external column name to
  an internal field name, and several external names may map to the same
  internal field;
* an output map (``to_external``) translates an internal field name to
  the external column name to write.

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
from typing import ClassVar, Optional, TextIO, override
from config_as_json import Config, ConfigNesting, ConfigNestingKind, \
    DictKeyValueTypesValidator, MemberValidationStep, NestedConfigs, \
    PathOrStr, ValidationPlan
from tableio import Capabilities, FileAccess, access_capabilities
from tableio_cfg_json import TioJsonConfig, tio_json_config_default

EXTENSION_FORMATS: dict[str, str] = {
    '.csv': 'CSV', '.xlsx': 'Excel', '.xls': 'Excel', '.ods': 'ODS',
    '.html': 'HTML', '.htm': 'HTML', '.tex': 'LaTeX', '.md': 'md',
    '.docx': 'docx', '.odt': 'odt', '.pdf': 'pdf', '.rst': 'reST',
    '.rtf': 'rtf', '.txt': 'txt'}
"""Map a data file name extension to a TableIO format name."""

PRESET_NAME_RE = re.compile(r'^[A-Za-z0-9]+$')
"""A configuration value made only of letters and digits is a preset."""


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

    A concrete subclass fixes the file access mode and the name of its
    column-name map member, and declares that map member before calling
    the constructor. The wrapped ``TioJsonConfig`` is created here and
    declared as a nested configuration so it reads and writes itself.
    """

    _FILE_ACCESS: ClassVar[FileAccess]
    _MAP_NAME: ClassVar[str]

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create default settings or read them from a JSON source."""
        self.tableio: TioJsonConfig = _tio_default(self._FILE_ACCESS,
                                                   stderr_file=stderr_file)
        self._unchecked_dicts = [self._MAP_NAME]
        Config.__init__(self, from_json_data_text=from_json_data_text,
                        from_json_filename=from_json_filename,
                        stderr_file=stderr_file)

    def _tio_factory(self, *, from_json_data_text: Optional[str] = None,
                     from_json_filename: Optional[PathOrStr] = None,
                     stderr_file: TextIO = sys.stderr) -> TioJsonConfig:
        """Construct the nested TableIO config from JSON when reading."""
        return _tio_from_json(self._FILE_ACCESS, from_json_data_text,
                              from_json_filename, stderr_file)

    @override
    def nested_configs(self) -> NestedConfigs:
        """Declare the wrapped TableIO config as a nested configuration."""
        return {'tableio': ConfigNesting(kind=ConfigNestingKind.MEMBER,
                                         config_type=TioJsonConfig,
                                         factory_function=self._tio_factory)}

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check that the column-name map is a mapping of string to string."""
        _ = stderr_file
        return [MemberValidationStep(
            member_names=[self._MAP_NAME],
            validator=DictKeyValueTypesValidator(str, str))]


class InputFormatConfig(_FormatConfig):
    """TableIO input endpoint with an external-to-internal column map."""

    _FILE_ACCESS = FileAccess.READ
    _MAP_NAME = 'to_internal'
    to_internal: dict[str, str]

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create the input map default, then run the shared constructor."""
        self.to_internal = {}
        _FormatConfig.__init__(self, from_json_data_text=from_json_data_text,
                               from_json_filename=from_json_filename,
                               stderr_file=stderr_file)


class OutputFormatConfig(_FormatConfig):
    """TableIO output endpoint with an internal-to-external column map."""

    _FILE_ACCESS = FileAccess.CREATE
    _MAP_NAME = 'to_external'
    to_external: dict[str, str]

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create the output map default, then run the shared constructor."""
        self.to_external = {}
        _FormatConfig.__init__(self, from_json_data_text=from_json_data_text,
                               from_json_filename=from_json_filename,
                               stderr_file=stderr_file)


def make_input_config(tableio: TioJsonConfig, to_internal: dict[str, str],
                      stderr_file: TextIO = sys.stderr) -> InputFormatConfig:
    """Return an input config from a TableIO config and a column map."""
    config = InputFormatConfig(stderr_file=stderr_file)
    config.tableio = tableio
    config.to_internal = dict(to_internal)
    return config


def make_output_config(tableio: TioJsonConfig, to_external: dict[str, str],
                       stderr_file: TextIO = sys.stderr) -> OutputFormatConfig:
    """Return an output config from a TableIO config and a column map."""
    config = OutputFormatConfig(stderr_file=stderr_file)
    config.tableio = tableio
    config.to_external = dict(to_external)
    return config


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
        stderr_file: TextIO = sys.stderr) -> InputFormatConfig:
    """Resolve a command-line input config value to an input config.

    An empty ``value`` infers the format from ``data_file``. A value of
    only letters and digits is a preset name looked up in ``presets``.
    Any other value is the path of a stand-alone input config file.

    Args:
        value: The ``--input-config`` value, or None for inference.
        data_file: The input data file, used for format inference.
        presets: Named input presets, typically from the teams config.
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
    return InputFormatConfig(from_json_filename=value, stderr_file=stderr_file)


def resolve_output_config(
        value: Optional[str], *, data_file: PathOrStr,
        presets: Optional[dict[str, OutputFormatConfig]] = None,
        stderr_file: TextIO = sys.stderr) -> OutputFormatConfig:
    """Resolve a command-line output config value to an output config.

    An empty ``value`` infers the format from ``data_file``. A value of
    only letters and digits is a preset name looked up in ``presets``.
    Any other value is the path of a stand-alone output config file.

    Args:
        value: The ``--output-config`` value, or None for inference.
        data_file: The output data file, used for format inference.
        presets: Named output presets, typically from the teams config.
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
                              stderr_file=stderr_file)
