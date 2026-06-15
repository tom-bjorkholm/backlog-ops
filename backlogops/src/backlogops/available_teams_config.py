#! /usr/local/bin/python3
"""Store and load AvailableTeams as a config-as-json configuration.

This module bridges the framework-neutral workforce data model in
:mod:`backlogops.available_teams` to the ``config_as_json`` library, in
the same way ``tableio_cfg_json`` bridges TableIO ``ConfigData`` with
``TioJsonConfig``. Each neutral data class gets a small bridge class that
multiply inherits from the data class and from ``Config``. The bridge
classes add JSON reading, writing, and validation, while the neutral data
classes stay the single source of truth for the data shape and the
consistency rules.

Application code that only wants to persist an ``AvailableTeams`` can use
:func:`write_available_teams` and :func:`read_available_teams` and never
touch the bridge classes directly.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from datetime import date
from typing import Optional, Sequence, TextIO, override
from config_as_json import CallingWholeConfigValidator, Config, \
    ConfigNesting, ConfigNestingKind, ConfigPath, JsonType, \
    MemberValidationStep, MemberValidator, NestedConfigs, ParseConverter, \
    PathOrStr, ReadOldConfiguration, SerializeConverter, SerializeConverters, \
    ValidationPlan, WholeConfigValidationStep
from backlogops.available_teams import AvailableTeams
from backlogops.io_config import InputFormatConfig, OutputFormatConfig
from backlogops.backlog_helpers import convert_to_date, convert_to_enum, \
    report_wrong_type
from backlogops.person import Person
from backlogops.team import FteException, Membership, Team
from backlogops.work_hours import CompanyWorkHours, ExceptionWorkHours, \
    ScheduleWorkHours, WeekDay


def _date_to_iso(value: object, *, path_text: str, stderr_file: TextIO,
                 **_extra: object) -> JsonType:
    """Convert a date member into an ISO 8601 string for JSON output."""
    _ = path_text, stderr_file
    assert isinstance(value, date)
    return value.isoformat()


def _week_day_name(day: object) -> str:
    """Return the JSON name used for one work-hours schedule key."""
    if isinstance(day, WeekDay):
        return day.name
    return str(day)


def _schedule_to_json(value: object, *, path_text: str, stderr_file: TextIO,
                      **_extra: object) -> JsonType:
    """Convert a week-day schedule into a name-keyed JSON object."""
    _ = path_text, stderr_file
    assert isinstance(value, dict)
    return {_week_day_name(day): float(hours)
            for day, hours in value.items()}


def _as_hours(member_name: str, value: object, stderr_file: TextIO) -> float:
    """Return work hours as a float, rejecting non-numeric values."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        report_wrong_type(member_name, value, float, stderr_file,
                          'Company work hours')
    return float(value)


# pylint: disable-next=too-few-public-methods
class _IsoDateMember(MemberValidator):
    """Convert an ISO date string member into a ``datetime.date``."""

    def __init__(self, optional: bool) -> None:
        """Remember whether an empty (``None``) value is allowed."""
        super().__init__()
        self._optional = optional

    @override
    def validate_member(self, config: Config, member_name: str,
                        member_value: object,
                        stderr_file: TextIO = sys.stderr) -> Optional[object]:
        """Return the member value as a date, or ``None`` when optional."""
        _ = config
        if member_value is None and self._optional:
            return None
        return convert_to_date(member_name, member_value, stderr_file)


# pylint: disable-next=too-few-public-methods
class _ScheduleMember(MemberValidator):
    """Normalize a work-hours schedule to ``WeekDay`` keyed floats."""

    @override
    def validate_member(self, config: Config, member_name: str,
                        member_value: object,
                        stderr_file: TextIO = sys.stderr) -> Optional[object]:
        """Return the schedule keyed by ``WeekDay`` with float hours."""
        _ = config
        if not isinstance(member_value, dict):
            report_wrong_type(member_name, member_value, dict, stderr_file,
                              'Company work hours')
        result: ScheduleWorkHours = {}
        for day, hours in member_value.items():
            week_day = convert_to_enum(member_name, day, WeekDay, stderr_file)
            assert isinstance(week_day, WeekDay)
            result[week_day] = _as_hours(member_name, hours, stderr_file)
        return result


class _BridgeConfig(Config):
    """Shared behavior for the AvailableTeams bridge classes."""

    @override
    def parse_converters(self) -> dict[str, ParseConverter]:
        """Use member validators instead of read-side scalar conversions."""
        return {}

    def __init__(self, from_json_data_text: Optional[str],
                 from_json_filename: Optional[PathOrStr],
                 stderr_file: TextIO) -> None:
        """Run the Config lifecycle for a bridge instance.

        Each bridge first creates its data class attributes, then calls
        this constructor to read JSON, apply defaults, and validate.
        """
        Config.__init__(self, from_json_data_text=from_json_data_text,
                        from_json_filename=from_json_filename,
                        stderr_file=stderr_file)

    @staticmethod
    def _consistency() -> WholeConfigValidationStep:
        """Return the step that calls the data class consistency check."""
        return WholeConfigValidationStep(
            validator=CallingWholeConfigValidator('check_consistency'))

    @staticmethod
    def _date_step(names: Sequence[str],
                   optional: bool) -> MemberValidationStep:
        """Return a step that parses ISO date members into dates."""
        return MemberValidationStep(member_names=list(names),
                                    validator=_IsoDateMember(optional))

    @staticmethod
    def _date_writers(names: Sequence[str]) -> SerializeConverters:
        """Return write-side converters that format dates as ISO strings."""
        converter = SerializeConverter(value_type=date, func=_date_to_iso,
                                       args={})
        return {name: converter for name in names}


class FteExceptionConfig(FteException, _BridgeConfig):
    """JSON bridge for one full-time-equivalent exception."""

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create placeholder defaults, then read one FTE exception."""
        FteException.__init__(self, start_date=date(2000, 1, 1),
                              end_date=date(2000, 1, 1), fte=1.0)
        _BridgeConfig.__init__(self, from_json_data_text, from_json_filename,
                               stderr_file)

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Parse the date members, then check exception consistency."""
        _ = stderr_file
        return [self._date_step(['start_date', 'end_date'], False),
                self._consistency()]

    @override
    def serialize_converters(self) -> SerializeConverters:
        """Format the date members as ISO strings on write."""
        return self._date_writers(['start_date', 'end_date'])


class ExceptionWorkHoursConfig(ExceptionWorkHours, _BridgeConfig):
    """JSON bridge for one work-hours exception (holiday or special)."""

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create placeholder defaults, then read one work-hours exception."""
        ExceptionWorkHours.__init__(self, start_date=date(2000, 1, 1),
                                    end_date=date(2000, 1, 1),
                                    hours_per_day=0.0)
        _BridgeConfig.__init__(self, from_json_data_text, from_json_filename,
                               stderr_file)

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Parse the date members, then check exception consistency."""
        _ = stderr_file
        return [self._date_step(['start_date', 'end_date'], False),
                self._consistency()]

    @override
    def serialize_converters(self) -> SerializeConverters:
        """Format the date members as ISO strings on write."""
        return self._date_writers(['start_date', 'end_date'])


class MembershipConfig(Membership, _BridgeConfig):
    """JSON bridge for one team membership."""

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create placeholder defaults, then read one membership."""
        Membership.__init__(self, person_name='person')
        _BridgeConfig.__init__(self, from_json_data_text, from_json_filename,
                               stderr_file)

    @override
    def nested_configs(self) -> NestedConfigs:
        """Declare the fte_exceptions list as nested Config objects."""
        return {'fte_exceptions': ConfigNesting(
            kind=ConfigNestingKind.LIST_ELEMENT,
            config_type=FteExceptionConfig)}

    @override
    def _omit_none_from_json(self) -> list[str]:
        """Allow the optional membership date range to be omitted."""
        return ['start_date', 'end_date']

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Parse the optional dates, then check membership consistency."""
        _ = stderr_file
        return [self._date_step(['start_date', 'end_date'], True),
                self._consistency()]

    @override
    def serialize_converters(self) -> SerializeConverters:
        """Format the date members as ISO strings on write."""
        return self._date_writers(['start_date', 'end_date'])


class TeamConfig(Team, _BridgeConfig):
    """JSON bridge for one team."""

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create placeholder defaults, then read one team."""
        Team.__init__(self, name='team', velocity=0.0, sum_fte_at_velocity=1.0,
                      sprint_length=1)
        _BridgeConfig.__init__(self, from_json_data_text, from_json_filename,
                               stderr_file)

    @override
    def nested_configs(self) -> NestedConfigs:
        """Declare the members list as nested Config objects."""
        return {'members': ConfigNesting(kind=ConfigNestingKind.LIST_ELEMENT,
                                         config_type=MembershipConfig)}

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check the team consistency."""
        _ = stderr_file
        return [self._consistency()]


class PersonConfig(Person, _BridgeConfig):
    """JSON bridge for one person."""

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create placeholder defaults, then read one person."""
        Person.__init__(self, name='person')
        _BridgeConfig.__init__(self, from_json_data_text, from_json_filename,
                               stderr_file)

    @override
    def nested_configs(self) -> NestedConfigs:
        """Declare the work-hour exceptions as nested Config objects."""
        return {'exceptions': ConfigNesting(
            kind=ConfigNestingKind.LIST_ELEMENT,
            config_type=ExceptionWorkHoursConfig)}

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """No extra person-level checks beyond the nested exceptions."""
        _ = stderr_file
        return []


class CompanyWorkHoursConfig(CompanyWorkHours, _BridgeConfig):
    """JSON bridge for the company work hours."""

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create defaults, then read the company work hours."""
        CompanyWorkHours.__init__(self)
        self._unchecked_dicts = ['work_hours']
        _BridgeConfig.__init__(self, from_json_data_text, from_json_filename,
                               stderr_file)

    @override
    def nested_configs(self) -> NestedConfigs:
        """Declare the work-hour exceptions as nested Config objects."""
        return {'exceptions': ConfigNesting(
            kind=ConfigNestingKind.LIST_ELEMENT,
            config_type=ExceptionWorkHoursConfig)}

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Normalize the week-day schedule, then check consistency."""
        _ = stderr_file
        return [MemberValidationStep(member_names=['work_hours'],
                                     validator=_ScheduleMember()),
                self._consistency()]

    @override
    def serialize_converters(self) -> SerializeConverters:
        """Write the week-day schedule with day-name keys."""
        return {'work_hours': SerializeConverter(value_type=dict,
                                                 func=_schedule_to_json,
                                                 args={})}


class _TeamsReadOldConfig(ReadOldConfiguration):
    """Fill the input/output preset maps when an old file omits them.

    The named input and output configuration presets were added to the
    workforce file after the first released file shape. Files written
    before that addition have neither member. This supplies an empty
    preset map for each missing member so old files keep loading.
    """

    def get_missing_path_values(self) -> dict[ConfigPath, object]:
        """Return empty preset maps for the members old files may omit."""
        return {('input_configs',): {}, ('output_configs',): {}}


class AvailableTeamsConfig(AvailableTeams, _BridgeConfig):
    """JSON bridge for the available workforce (persons and teams)."""

    # pylint: disable-next=super-init-not-called
    def __init__(self, *, neutral: Optional[AvailableTeams] = None,
                 from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create the bridge from a neutral workforce or from JSON.

        ``AvailableTeams.__init__`` is intentionally not invoked because
        it requires ``persons`` and ``teams`` arguments that the bridge
        does not duplicate. ``Config.copy_initial_data`` establishes the
        schema from the supplied or default neutral workforce instead.
        The named input and output TableIO presets are not part of the
        neutral workforce; they are added here as the bridge's own
        members.
        """
        if neutral is None:
            neutral = AvailableTeams(persons={}, teams=[])
        Config.copy_initial_data(neutral, self)
        self.input_configs: dict[str, InputFormatConfig] = {}
        self.output_configs: dict[str, OutputFormatConfig] = {}
        _BridgeConfig.__init__(self, from_json_data_text, from_json_filename,
                               stderr_file)

    @override
    def _get_read_old_config(self) -> ReadOldConfiguration:
        """Accept old files written before the preset members existed."""
        return _TeamsReadOldConfig()

    @override
    def nested_configs(self) -> NestedConfigs:
        """Declare the persons, teams, work hours and TableIO presets."""
        return {
            'persons': ConfigNesting(kind=ConfigNestingKind.DICT_VALUE,
                                     config_type=PersonConfig),
            'teams': ConfigNesting(kind=ConfigNestingKind.LIST_ELEMENT,
                                   config_type=TeamConfig),
            'company_work_hours': ConfigNesting(
                kind=ConfigNestingKind.MEMBER,
                config_type=CompanyWorkHoursConfig),
            'input_configs': ConfigNesting(kind=ConfigNestingKind.DICT_VALUE,
                                           config_type=InputFormatConfig),
            'output_configs': ConfigNesting(kind=ConfigNestingKind.DICT_VALUE,
                                            config_type=OutputFormatConfig)}

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check the whole-workforce consistency."""
        _ = stderr_file
        return [self._consistency()]


def write_available_teams(teams: AvailableTeams, filename: PathOrStr,
                          stderr_file: TextIO = sys.stderr) -> None:
    """Validate and write an available workforce to a JSON file.

    Args:
        teams: The workforce to store.
        filename: Destination JSON configuration file.
        stderr_file: Stream used for user-facing diagnostics.
    """
    config = AvailableTeamsConfig(neutral=teams, stderr_file=stderr_file)
    config.write(to_json_filename=filename, stderr_file=stderr_file)


def read_available_teams(filename: PathOrStr, stderr_file: TextIO = sys.stderr
                         ) -> AvailableTeamsConfig:
    """Read an available workforce from a JSON configuration file.

    Args:
        filename: Source JSON configuration file.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The loaded workforce. The returned object is an ``AvailableTeams``.
    """
    return AvailableTeamsConfig(from_json_filename=filename,
                                stderr_file=stderr_file)


def get_available_teams(filename: Optional[PathOrStr],
                        stderr_file: TextIO = sys.stderr
                        ) -> AvailableTeamsConfig:
    """Convinience get the AvailableTeamsConfig to use.

    If a filename is provided, the file is read and the AvailableTeamsConfig
    is stored and returned.
    If no filename is provided and there is a stored AvailableTeamsConfig,
    it is returned.
    If no filename is provided and there is no stored AvailableTeamsConfig,
    this function will look for these in order of precedence:
    - File named in $BACKLOGOPS_CFG environment variable
    - File backlogops.cfg in folder specified by $BACKLOGOPS_DIR
      environment variable
    - $HOME/.backlogops.cfg
    If a file is found, it is read and the AvailableTeamsConfig is stored and
    returned. If no file is found, an exception is raised.

    Args:
        filename: Source JSON configuration file.
        stderr_file: Stream used for user-facing diagnostics.

    Raises:
        FileNotFoundError: If $BACKLOGOPS_CFG is set but the file does not
                           exist.
        DirectoryNotFoundError: If $BACKLOGOPS_DIR is set but the directory
                               does not exist.
        RuntimeError: If no filename is provided and no stored
                      AvailableTeamsConfig is found and no file is found in
                      the order of precedence.
    Returns:
        The loaded workforce. The returned object is an
        ``AvailableTeamsConfig``.
    """
    # implement this
