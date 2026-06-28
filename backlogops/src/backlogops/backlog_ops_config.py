#! /usr/local/bin/python3
"""Top-level backlog-ops configuration stored as config-as-json.

The :class:`BacklogOpsConfig` is the single configuration object an
application reads and writes. It groups together the available workforce,
the named TableIO input and output presets, and an optional set of
backlog item levels:

* ``available_teams`` is the workforce (persons, teams and company work
  hours), bridged to JSON by :class:`AvailableTeamsConfig`;
* ``input_configs`` and ``output_configs`` are named TableIO presets;
* ``levels`` is the optional list of backlog item levels. It is omitted
  from the file while it is ``None``; :meth:`BacklogOpsConfig.get_levels`
  then falls back to :data:`backlogops.levels.DEFAULT_LEVELS`.

Earlier file versions stored the workforce members (``persons``,
``teams`` and ``company_work_hours``) at the top level next to the
presets. :class:`_BacklogOpsReadOldConfig` moves those into the nested
``available_teams`` object so old files keep loading.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import os
import sys
from pathlib import Path
from typing import Optional, TextIO, override
from config_as_json import CallingWholeConfigValidator, Config, \
    ConfigAutoChangeHook, ConfigNesting, ConfigNestingKind, ConfigPath, \
    JsonType, MemberValidationStep, MemberValidator, NestedConfigs, \
    PathOrStr, ReadOldConfiguration, RocfKeyMove, SerializeConverter, \
    SerializeConverters, ValidationPlan, WholeConfigValidationStep
from backlogops.available_teams import AvailableTeams
from backlogops.available_teams_config import AvailableTeamsConfig
from backlogops.backlog import Status
from backlogops.backlog_helpers import report_bad_value, report_wrong_type
from backlogops.io_config import GuiDisplayConfig, InputFormatConfig, \
    OutputFormatConfig, _StatusMapValidator
from backlogops.levels import DEFAULT_LEVELS, Level, Levels, LevelDisplay, \
    levels_from_list


def _as_int(name: str, value: object, stderr_file: TextIO) -> int:
    """Return ``value`` as an int, rejecting booleans and other types."""
    if isinstance(value, bool) or not isinstance(value, int):
        report_wrong_type(name, value, int, stderr_file, 'Level')
    return value


def _as_str(name: str, value: object, stderr_file: TextIO) -> str:
    """Return ``value`` as a string, rejecting other types."""
    if not isinstance(value, str):
        report_wrong_type(name, value, str, stderr_file, 'Level')
    return value


def _as_str_list(name: str, value: object, stderr_file: TextIO) -> list[str]:
    """Return ``value`` as a list of strings, rejecting other types."""
    if not isinstance(value, list):
        report_wrong_type(name, value, list, stderr_file, 'Level')
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_as_str(f'{name}[{index}]', item, stderr_file))
    return result


def _level_from_dict(data: dict[str, object], stderr_file: TextIO) -> Level:
    """Return one Level from its JSON object, checking the field shape."""
    unknown = sorted(set(data) - {'level', 'name', 'aliases'})
    if unknown:
        report_bad_value('level', data, f'unknown level fields {unknown}',
                         stderr_file, 'Level')
    if 'level' not in data or 'name' not in data:
        report_bad_value('level', data, 'requires "level" and "name"',
                         stderr_file, 'Level')
    return Level(level=_as_int('level', data['level'], stderr_file),
                 name=_as_str('name', data['name'], stderr_file),
                 aliases=_as_str_list('aliases', data.get('aliases', []),
                                      stderr_file))


def _level_from_obj(name: str, value: object, stderr_file: TextIO) -> Level:
    """Return one Level from a JSON object or pass a Level through."""
    if isinstance(value, Level):
        return value
    if not isinstance(value, dict):
        report_wrong_type(name, value, dict, stderr_file, 'Level')
    return _level_from_dict(value, stderr_file)


# pylint: disable-next=too-few-public-methods
class _LevelsMember(MemberValidator):
    """Convert the optional ``levels`` member into a list of ``Level``."""

    @override
    def validate_member(self, config: Config, member_name: str,
                        member_value: object,
                        stderr_file: TextIO = sys.stderr) -> Optional[object]:
        """Return the levels as a list of ``Level``, or ``None``."""
        _ = config
        if member_value is None:
            return None
        if not isinstance(member_value, list):
            report_wrong_type(member_name, member_value, list, stderr_file,
                              'BacklogOps config')
        return [_level_from_obj(f'{member_name}[{index}]', element,
                                stderr_file)
                for index, element in enumerate(member_value)]


def _levels_to_json(value: object, *, path_text: str, stderr_file: TextIO,
                    **_extra: object) -> JsonType:
    """Convert a list of ``Level`` into JSON objects for output."""
    _ = path_text, stderr_file
    assert isinstance(value, list)
    result: list[JsonType] = []
    for element in value:
        assert isinstance(element, Level)
        result.append({'level': element.level, 'name': element.name,
                       'aliases': list(element.aliases)})
    return result


class _BacklogOpsReadOldConfig(ReadOldConfiguration):
    """Normalize older backlog-ops configuration files on read.

    Two shape changes are accepted. The named input and output preset
    maps were added after the first released file; an empty map is
    supplied when an old file omits them. The workforce members were
    later moved from the top level into a nested ``available_teams``
    object; the move rules relocate them so old files keep loading.
    """

    def get_json_key_moves(self) -> list[RocfKeyMove]:
        """Move the old top-level workforce members under available_teams."""
        return [RocfKeyMove(old_path=('persons',),
                            new_path=('available_teams', 'persons')),
                RocfKeyMove(old_path=('teams',),
                            new_path=('available_teams', 'teams')),
                RocfKeyMove(old_path=('company_work_hours',),
                            new_path=('available_teams',
                                      'company_work_hours'))]

    def get_missing_path_values(self) -> dict[ConfigPath, object]:
        """Return defaults for the members old files may omit."""
        return {('input_configs',): {}, ('output_configs',): {},
                ('gui_display',): {}, ('status_input_map',): {}}


class BacklogOpsConfig(Config):
    """Top-level backlog-ops configuration stored as config-as-json."""

    def __init__(self, *, available_teams: Optional[AvailableTeams] = None,
                 from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create defaults, or read the configuration from JSON.

        The supplied workforce establishes the schema of the nested
        ``available_teams`` member; the library's auto-wrap step turns it
        into an :class:`AvailableTeamsConfig`. The presets default to
        empty maps and the levels default to ``None`` (use the defaults).
        The ``auto_ch_hook`` is notified when an old file needed
        backward-compatible normalization while reading.
        """
        self.available_teams: AvailableTeams = (
            AvailableTeams(persons={}, teams=[]) if available_teams is None
            else available_teams)
        self.input_configs: dict[str, InputFormatConfig] = {}
        self.output_configs: dict[str, OutputFormatConfig] = {}
        self.gui_display: GuiDisplayConfig = GuiDisplayConfig(
            stderr_file=stderr_file)
        self.status_input_map: dict[str, Status] = {}
        self.levels: Optional[list[Level]] = None
        self._unchecked_dicts = ['status_input_map']
        Config.__init__(self, from_json_data_text=from_json_data_text,
                        from_json_filename=from_json_filename,
                        auto_ch_hook=auto_ch_hook, stderr_file=stderr_file)

    @override
    def _get_read_old_config(self) -> ReadOldConfiguration:
        """Accept old files with a flat workforce or no preset maps."""
        return _BacklogOpsReadOldConfig()

    @override
    def nested_configs(self) -> NestedConfigs:
        """Declare the workforce and the named TableIO preset maps."""
        member = ConfigNesting(kind=ConfigNestingKind.MEMBER,
                               config_type=AvailableTeamsConfig)
        in_cfg = ConfigNesting(kind=ConfigNestingKind.DICT_VALUE,
                               config_type=InputFormatConfig)
        out_cfg = ConfigNesting(kind=ConfigNestingKind.DICT_VALUE,
                                config_type=OutputFormatConfig)
        gui = ConfigNesting(kind=ConfigNestingKind.MEMBER,
                            config_type=GuiDisplayConfig)
        return {'available_teams': member, 'input_configs': in_cfg,
                'output_configs': out_cfg, 'gui_display': gui}

    @override
    def _omit_none_from_json(self) -> list[str]:
        """Omit the levels member from the file while it is ``None``."""
        return ['levels']

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Convert the levels and status map, then check consistency."""
        _ = stderr_file
        consistency = CallingWholeConfigValidator('check_consistency')
        return [MemberValidationStep(member_names=['levels'],
                                     validator=_LevelsMember()),
                MemberValidationStep(member_names=['status_input_map'],
                                     validator=_StatusMapValidator()),
                WholeConfigValidationStep(validator=consistency)]

    @override
    def serialize_converters(self) -> SerializeConverters:
        """Write the levels member as a list of JSON objects."""
        return {'levels': SerializeConverter(value_type=list,
                                             func=_levels_to_json, args={})}

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the consistency of the configured levels, when present.

        The workforce and the preset maps are validated by their own
        nested configurations. Only the optional levels need a check
        here, and only when they are configured.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a level field has the wrong type.
            ValueError: If a level value violates a constraint or a level
                number is used more than once.
            KeyError: If a level name or alias is not unique.
        """
        if self.levels is not None:
            levels_from_list(self.levels, stderr_file)

    def get_levels(self) -> Levels:
        """Return the configured levels, or the default levels.

        Returns:
            The levels keyed by level number, taken from the
            configuration, or :data:`DEFAULT_LEVELS` when no levels are
            configured.
        """
        if self.levels is None:
            return DEFAULT_LEVELS
        return levels_from_list(self.levels)

    def get_status_input_map(self) -> dict[str, Status]:
        """Return the library-wide status input map.

        Returns:
            The extra status names mapped to Status members, as configured
            at the top level. Empty when no extra names are configured.
        """
        return self.status_input_map

    def get_gui_level_display(self) -> LevelDisplay:
        """Return how levels should be shown in the GUI.

        Returns:
            The :class:`LevelDisplay` configured for the GUI display.
        """
        return self.gui_display.level_display


def write_backlog_ops_config(config: BacklogOpsConfig, filename: PathOrStr,
                             stderr_file: TextIO = sys.stderr) -> None:
    """Validate and write a backlog-ops configuration to a JSON file.

    Args:
        config: The configuration to store.
        filename: Destination JSON configuration file.
        stderr_file: Stream used for user-facing diagnostics.
    """
    config.write(to_json_filename=filename, stderr_file=stderr_file)


def read_backlog_ops_config(filename: PathOrStr,
                            stderr_file: TextIO = sys.stderr,
                            auto_ch_hook: Optional[ConfigAutoChangeHook] = None
                            ) -> BacklogOpsConfig:
    """Read a backlog-ops configuration from a JSON configuration file.

    Args:
        filename: Source JSON configuration file.
        stderr_file: Stream used for user-facing diagnostics.
        auto_ch_hook: Hook notified when an old file needed
            backward-compatible normalization while reading.

    Returns:
        The loaded configuration.
    """
    return BacklogOpsConfig(from_json_filename=filename,
                            auto_ch_hook=auto_ch_hook, stderr_file=stderr_file)


# pylint: disable-next=too-few-public-methods
class _ConfigStore:
    """Hold the most recently loaded configuration for reuse in a process.

    The current configuration is kept in RAM so that a later call to
    :func:`get_backlog_ops_config` without a filename can reuse it
    instead of reading a file again.
    """

    current: Optional[BacklogOpsConfig] = None


def _config_from_named_file() -> Optional[Path]:
    """Return the config file named by $BACKLOGOPS_CFG, if that is set."""
    named = os.environ.get('BACKLOGOPS_CFG')
    if named is None:
        return None
    path = Path(named)
    if not path.is_file():
        raise FileNotFoundError(f'$BACKLOGOPS_CFG file not found: {named}')
    return path


def _config_from_named_dir() -> Optional[Path]:
    """Return backlogops.cfg in $BACKLOGOPS_DIR, if that directory is set."""
    named = os.environ.get('BACKLOGOPS_DIR')
    if named is None:
        return None
    directory = Path(named)
    if not directory.is_dir():
        raise NotADirectoryError(f'$BACKLOGOPS_DIR not found: {named}')
    path = directory / 'backlogops.cfg'
    return path if path.is_file() else None


def _config_from_home() -> Optional[Path]:
    """Return $HOME/.backlogops.cfg if that file exists."""
    path = Path.home() / '.backlogops.cfg'
    return path if path.is_file() else None


def _searched_locations() -> str:
    """Describe the locations searched for a configuration file."""
    named_dir = os.environ.get('BACKLOGOPS_DIR')
    in_dir = (str(Path(named_dir) / 'backlogops.cfg') if named_dir is not None
              else '$BACKLOGOPS_DIR (not set)')
    return ('  $BACKLOGOPS_CFG (not set)\n'
            f'  {in_dir}\n'
            f'  {Path.home() / ".backlogops.cfg"}')


def _config_path_from_env() -> Path:
    """Return the configuration file found by the documented precedence.

    Raises:
        FileNotFoundError: If $BACKLOGOPS_CFG is set but the file is
            missing.
        NotADirectoryError: If $BACKLOGOPS_DIR is set but is not a
            directory.
        RuntimeError: If no configuration file is found.
    """
    path = _config_from_named_file()
    if path is not None:
        return path
    path = _config_from_named_dir()
    if path is not None:
        return path
    path = _config_from_home()
    if path is not None:
        return path
    raise RuntimeError('No backlog-ops configuration file found. Looked '
                       'for:\n' + _searched_locations())


def get_backlog_ops_config(filename: Optional[PathOrStr],
                           stderr_file: TextIO = sys.stderr,
                           auto_ch_hook: Optional[ConfigAutoChangeHook] = None
                           ) -> BacklogOpsConfig:
    """Return the BacklogOpsConfig to use, reading or reusing as needed.

    If a filename is provided, the file is read and the BacklogOpsConfig
    is stored and returned. If no filename is provided and there is a
    stored BacklogOpsConfig, it is returned. If no filename is provided
    and there is no stored BacklogOpsConfig, this function looks for one
    in order of precedence:
    - File named in $BACKLOGOPS_CFG environment variable
    - File backlogops.cfg in folder specified by $BACKLOGOPS_DIR
      environment variable
    - $HOME/.backlogops.cfg
    If a file is found, it is read and the BacklogOpsConfig is stored and
    returned. If no file is found, an exception is raised.

    Args:
        filename: Source JSON configuration file.
        stderr_file: Stream used for user-facing diagnostics.
        auto_ch_hook: Hook notified when an old file needed
            backward-compatible normalization while reading.

    Raises:
        FileNotFoundError: If $BACKLOGOPS_CFG is set but the file does not
                           exist.
        NotADirectoryError: If $BACKLOGOPS_DIR is set but the directory
                            does not exist.
        RuntimeError: If no filename is provided and no stored
                      BacklogOpsConfig is found and no file is found in
                      the order of precedence.
    Returns:
        The loaded configuration.
    """
    if filename is not None:
        _ConfigStore.current = read_backlog_ops_config(filename, stderr_file,
                                                       auto_ch_hook)
        return _ConfigStore.current
    if _ConfigStore.current is not None:
        return _ConfigStore.current
    path = _config_path_from_env()
    _ConfigStore.current = read_backlog_ops_config(path, stderr_file,
                                                   auto_ch_hook)
    return _ConfigStore.current
