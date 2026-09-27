#! /usr/local/bin/python3
"""Configuration for using remaining time in backlog operations.

Estimating in story points is recommended, but some development efforts
are required to estimate in remaining time. Enabling remaining time does
not disable story points: a development effort most likely uses one of
them, but may use both, such as while it moves from remaining time to
story points. :class:`RemainingTimeConfig` says whether remaining time is
used at all, what the focus factor of a team without its own is, and what
a backlog item that nobody has estimated counts as: a remaining time for
a backlog item level, and two settings that fill in the levels that are
not given, as described in :mod:`backlogops.level_defaults`. A level
given less than 10 minutes takes no part in any factor.

A remaining time is ideal focused person work time, written as hours,
minutes and seconds, as described in :mod:`backlogops.duration_text`.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import sys
from datetime import timedelta
from typing import Optional, TextIO, override
from config_as_json import Config, ConfigAutoChangeHook, ConfigPath, \
    JsonType, MemberValidationStep, MemberValidator, \
    MemberValidatorSequence, PathOrStr, SerializeConverter, \
    SerializeConverters, ValidationPlan, ValueAsTypeValidator, \
    ValueTypeValidator
from backlogops.backlog_helpers import report_bad_value, report_wrong_type
from backlogops.duration_text import format_duration, parse_duration
from backlogops.level_defaults import LevelDefaults, level_validator
from backlogops.team import check_focus_factor

_TIME_FORMAT = ('hours:minutes:seconds, optionally after weeks and days, '
                'not a bare number and not negative')
"""How a remaining time is written, used in an error message."""


# pylint: disable-next=too-few-public-methods
class _DurationMember(MemberValidator):
    """Convert a remaining time text member into a ``timedelta``.

    A ``timedelta`` is kept as it is, so that a configuration built in
    code validates too, but a negative one is refused.
    """

    @override
    def validate_member(self, config: Config, member_name: str,
                        member_value: object,
                        stderr_file: TextIO = sys.stderr) -> object:
        """Return the member value as a non-negative ``timedelta``."""
        _ = config
        if isinstance(member_value, str):
            duration = parse_duration(member_value)
            if duration is None:
                report_bad_value(member_name, member_value, _TIME_FORMAT,
                                 stderr_file, 'Default remaining time')
            return duration
        if not isinstance(member_value, timedelta):
            report_wrong_type(member_name, member_value, str, stderr_file,
                              'Default remaining time')
        if member_value < timedelta(0):
            report_bad_value(member_name, member_value, 'must not be negative',
                             stderr_file, 'Default remaining time')
        return member_value


def _duration_to_json(value: object, *, path_text: str, stderr_file: TextIO,
                      **_extra: object) -> JsonType:
    """Convert a remaining time member into its text for JSON output."""
    _ = path_text, stderr_file
    assert isinstance(value, timedelta)
    return format_duration(value)


def _fraction_validator() -> MemberValidator:
    """Return the validator converting a focus factor to a decimal.

    A whole number in the file is accepted and stored as a decimal, while
    ``true`` is refused although Python counts a boolean as a whole
    number. The range is checked with the rest of the configuration.
    """
    return MemberValidatorSequence([
        ValueTypeValidator(value_type=[int, float], not_allowed_type=bool),
        ValueAsTypeValidator(value_type=float, direct_types=[int])])


class DefaultRemainingTimeLevel(Config):
    """The default remaining time of a backlog item at one level."""

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr, *,
                 member_name: Optional[str] = None) -> None:
        """Create the default of one level, or read it from JSON.

        Args:
            from_json_data_text: Optional JSON text to parse directly.
            from_json_filename: Optional JSON file to read.
            auto_ch_hook: Hook notified about backward-compatible changes
                made while reading.
            stderr_file: Stream used for user-facing diagnostics.
            member_name: Path for reaching this object from the top level,
                so that a diagnostic names the whole path. None for an
                object that is a member of nothing.

        Attributes:
            level: The backlog item level this default is for.
            remaining_time: What an item of that level counts as in ideal
                focused person work time. (``0:30:00`` means one person
                working focused on only this item for 30 minutes.) In the
                file it is hours, minutes and seconds, such as
                ``02:30:00``. When read it may start with whole weeks and
                days, such as ``1w 1d 2:30:00``, where ``1d`` is 24 hours
                and ``1w`` is 7 days, but the hours, minutes and seconds
                are always given; it is always written as hours, so that
                is written as ``194:30:00``. A bare number is refused.
        """
        self.level: int = 0
        self.remaining_time: timedelta = timedelta(hours=1, minutes=30)
        super().__init__(from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename,
                         auto_ch_hook=auto_ch_hook, stderr_file=stderr_file,
                         member_name=member_name)

    def as_float(self) -> float:
        """Return the remaining time in seconds, for growth to work on."""
        return self.remaining_time.total_seconds()

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check the level number and the remaining time of one default."""
        _ = stderr_file
        return [MemberValidationStep(member_names=['level'],
                                     validator=level_validator()),
                MemberValidationStep(member_names=['remaining_time'],
                                     validator=_DurationMember())]

    @override
    def serialize_converters(self) -> SerializeConverters:
        """Write the remaining time as hours, minutes and seconds."""
        converter = SerializeConverter(value_type=timedelta,
                                       func=_duration_to_json, args={})
        return {'remaining_time': converter}


class RemainingTimeConfig(LevelDefaults[DefaultRemainingTimeLevel]):
    """Configuration for remaining time in backlog operations."""

    _LEVEL_TYPE = DefaultRemainingTimeLevel
    """The class of the default remaining time of one level."""
    _SUBJECT = 'Remaining time'
    """What owns the members, used to start an error message."""
    _NEAR_ZERO = 600.0
    """Fewest seconds a level may have and still fix a growth factor.

    Opening a backlog item to find out what to do takes about 10 minutes,
    so a level of less than that is no more usable for a factor than a
    level of nothing at all: dividing by it makes every level above it
    absurdly large. A level below this counts as what it says where it is
    given, and is passed over when a factor is worked out.
    """
    _NO_FACTOR = ('needs two levels with at least 0:10:00 remaining time '
                  'each to work out a factor from')
    """Why filling in levels is refused when too few levels are given."""

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr, *,
                 member_name: Optional[str] = None) -> None:
        """Create the remaining time configuration, or read it from JSON.

        Args:
            from_json_data_text: Optional JSON text to parse directly.
            from_json_filename: Optional JSON file to read.
            auto_ch_hook: Hook notified about backward-compatible changes
                made while reading.
            stderr_file: Stream used for user-facing diagnostics.
            member_name: Path for reaching this object from the top level,
                so that a diagnostic names the whole path. None for an
                object that is a member of nothing.

        Attributes:
            enable_remaining_time: Whether remaining time estimates are
                handled at all in backlog operations. If False, the other
                settings are ignored, although they are still validated,
                and no completion is estimated from remaining time. Story
                points are used either way, so True means that both kinds
                of estimates are used. Most development efforts are
                better off estimating in story points than in remaining
                time.
            levels: The remaining time given for a level, sorted by level
                number while the configuration is validated.
            interpolate: Whether a level between two given levels is
                guessed from them.
            extrapolate: Whether a level above the highest or below the
                lowest given level is guessed from the two nearest ones.
            default_focus_factor: The fraction of the working time of a
                team that counts as focused work on the backlog items,
                for a team that has no focus factor of its own. For
                example, 0.3 means that 30% of the working time counts as
                focused work. The factor also makes up for optimism, or
                pessimism, in the estimates, and common values are from
                0.1 to 0.5. It is from 0.005 to 3.0.
            _value_for_level: What each level asked for counts as, in
                seconds, by level number. :meth:`build_cache` puts the
                given levels in it, and a level worked out from them is
                added to it the first time it is asked for.
        """
        self.enable_remaining_time: bool = False
        self.levels = []
        self.interpolate = False
        self.extrapolate = False
        self.default_focus_factor: float = 0.3
        super().__init__(from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename,
                         auto_ch_hook=auto_ch_hook, stderr_file=stderr_file,
                         member_name=member_name)

    @override
    def _missing_members(self) -> dict[ConfigPath, object]:
        """Return the unused remaining time an older file leaves out.

        A file that has no remaining time section at all, and one that
        has an empty section, both mean the same thing: remaining time is
        not used, nothing is guessed, and the focus factor has its usual
        default.
        """
        return {('enable_remaining_time',): False,
                **super()._missing_members(), ('default_focus_factor',): 0.3}

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check the switch and the focus factor, then the levels."""
        switch = MemberValidationStep(
            member_names=['enable_remaining_time'],
            validator=ValueTypeValidator(value_type=bool))
        focus = MemberValidationStep(member_names=['default_focus_factor'],
                                     validator=_fraction_validator())
        return [switch, focus] + super().get_validation_plan(stderr_file)

    @override
    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the focus factor and the given levels.

        Besides the checks of the levels, the default focus factor must be
        within :data:`backlogops.team.FOCUS_FACTOR_RANGE`.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            ValueError: The focus factor is out of range, a level is given
                twice, or a filled-in level is asked for without two
                levels to work the factor from.
        """
        check_focus_factor('default_focus_factor', self.default_focus_factor,
                           stderr_file, self._SUBJECT)
        super().check_consistency(stderr_file)

    def get_default_time(self, level: int) -> Optional[timedelta]:
        """Return the remaining time a backlog item of one level counts as.

        A level given a remaining time of its own counts as that, and any
        other level is filled in in seconds as :class:`LevelDefaults`
        describes.

        Args:
            level: The level of the backlog item to guess the size of.

        Returns:
            The remaining time to count such an item as, or None when the
            configuration says nothing about that level or the guess is
            too large for a ``timedelta``.
        """
        seconds = self._value_of_level(level)
        if seconds is None:
            return None
        try:
            return timedelta(seconds=seconds)
        except OverflowError:
            return None
