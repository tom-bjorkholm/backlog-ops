#! /usr/local/bin/python3
"""Best guess story points for backlog items that have none.

A backlog item nobody has estimated yet still takes time, and a completion
date worked out as if it took none is wrong in the one direction that
matters. :class:`DefaultStoryPoints` is what the configuration says such
an item counts as: a story point value for a backlog item level, and two
settings that fill in the levels that are not given.

Filling in works with a factor, which is what one level up multiplies the
size by, as described in :mod:`backlogops.level_defaults`. A level given
fewer than 0.05 story points takes no part in any factor.

Which backlog items this guess applies to is decided by
:func:`backlogops.use_story_points`, not here.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import sys
from typing import Optional, TextIO, override
from config_as_json import Config, ConfigAutoChangeHook, IntFloatValidator, \
    MemberValidationStep, MemberValidator, MemberValidatorSequence, \
    PathOrStr, ValidationPlan, ValueAsTypeValidator, ValueTypeValidator
from backlogops.level_defaults import LevelDefaults, level_validator


def _points_validator() -> MemberValidator:
    """Return the validator of the story points of one default.

    A whole number in the file is accepted and stored as a decimal, so
    that ``4`` and ``4.0`` say the same thing, while ``true`` is refused
    although Python counts a boolean as a whole number.
    """
    return MemberValidatorSequence([
        ValueTypeValidator(value_type=[int, float], not_allowed_type=bool),
        ValueAsTypeValidator(value_type=float, direct_types=[int]),
        IntFloatValidator(min_value=0.0, max_value=None, allowed_values=None)])


class DefaultStoryPointLevel(Config):
    """The default story points of a backlog item at one level."""

    def as_float(self) -> float:
        """Return the story points, as the number growth works on."""
        return self.story_points

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
            story_points: What an item of that level counts as.
        """
        self.level: int = 0
        self.story_points: float = 1.0
        super().__init__(from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename,
                         auto_ch_hook=auto_ch_hook, stderr_file=stderr_file,
                         member_name=member_name)

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check the level number and the story points of one default."""
        _ = stderr_file
        return [MemberValidationStep(member_names=['level'],
                                     validator=level_validator()),
                MemberValidationStep(member_names=['story_points'],
                                     validator=_points_validator())]


class DefaultStoryPoints(LevelDefaults[DefaultStoryPointLevel]):
    """What a backlog item with no story points of its own counts as."""

    _LEVEL_TYPE = DefaultStoryPointLevel
    """The class of the default story points of one level."""
    _SUBJECT = 'Default story points'
    """What owns the members, used to start an error message."""
    _NEAR_ZERO = 0.05
    """Fewest story points a level may have and still fix a growth factor.

    A factor is the ratio between two levels, so a level of nearly no
    story points is no more usable than a level of none at all: dividing
    by it makes every level above it absurdly large. A level below this
    counts as what it says where it is given, and is passed over when a
    factor is worked out.
    """
    _NO_FACTOR = ('needs two levels with at least 0.05 story points each '
                  'to work out a factor from')
    """Why filling in levels is refused when too few levels are given."""

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr, *,
                 member_name: Optional[str] = None) -> None:
        """Create defaults that guess nothing, or read them from JSON.

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
            levels: The story points given for a level, sorted by level
                number while the configuration is validated.
            interpolate: Whether a level between two given levels is
                guessed from them.
            extrapolate: Whether a level above the highest or below the
                lowest given level is guessed from the two nearest ones.
            _value_for_level: What each level asked for counts as, by
                level number. :meth:`build_cache` puts the given levels
                in it, and a level worked out from them is added to it
                the first time it is asked for.
        """
        self.interpolate = False
        self.extrapolate = False
        self.levels = []
        super().__init__(from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename,
                         auto_ch_hook=auto_ch_hook, stderr_file=stderr_file,
                         member_name=member_name)

    def get_default_story_points(self, level: int) -> Optional[float]:
        """Return the story points a backlog item of one level counts as.

        A level given story points of its own counts as those, and any
        other level is filled in as :class:`LevelDefaults` describes.

        Args:
            level: The level of the backlog item to guess the size of.

        Returns:
            The story points to count such an item as, or None when the
            configuration says nothing about that level.
        """
        return self._value_of_level(level)
