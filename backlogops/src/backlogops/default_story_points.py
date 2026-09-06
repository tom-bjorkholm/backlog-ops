#! /usr/local/bin/python3
"""Best guess story points for backlog items that have none.

A backlog item nobody has estimated yet still takes time, and a completion
date worked out as if it took none is wrong in the one direction that
matters. :class:`DefaultStoryPoints` is what the configuration says such
an item counts as: a story point value for a backlog item level, and two
settings that fill in the levels that are not given.

Filling in works with a factor, which is what one level up multiplies the
size by. Level 1 with 2 story points and level 3 with 8 grow by a factor
of 2 per level, so an interpolated level 2 is 4. Extrapolation continues
past the given levels with the factor of the two highest of them upwards
and the factor of the two lowest of them downwards, so level 4 is 16 and
level 0 is 1. A level given zero story points counts as zero where it is
given, but takes no part in any factor, because a ratio to zero says
nothing about how sizes grow.

Which backlog items this guess applies to is decided by
:func:`backlogops.use_story_points`, not here.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import sys
from typing import Optional, TextIO, override
from config_as_json import CallingWholeConfigValidator, Config, \
    ConfigAutoChangeHook, ConfigNesting, ConfigNestingKind, ConfigPath, \
    IntFloatValidator, MemberValidationStep, MemberValidator, \
    MemberValidatorSequence, NestedConfigs, PathOrStr, \
    ReadOldConfiguration, ValidationPlan, ValueAsTypeValidator, \
    ValueTypeValidator, WholeConfigValidationStep
from backlogops.backlog_helpers import report_bad_value

_SUBJECT = 'Default story points'
"""What owns the members, used to start an error message."""

_LEVEL_LIMIT = 100
"""How far from zero a level number of a default may be."""

_NO_FACTOR = ('needs two levels with story points above zero to work out a '
              'factor from')
"""Why filling in levels is refused when too few levels are given."""


def _level_validator() -> MemberValidator:
    """Return the validator of the level number of one default."""
    return MemberValidatorSequence([
        ValueTypeValidator(value_type=int, not_allowed_type=bool),
        IntFloatValidator(min_value=-_LEVEL_LIMIT, max_value=_LEVEL_LIMIT,
                          allowed_values=None)])


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
                                     validator=_level_validator()),
                MemberValidationStep(member_names=['story_points'],
                                     validator=_points_validator())]


def _anchors(levels: list[DefaultStoryPointLevel]) -> list[tuple[int, float]]:
    """Return the level and points pairs a factor may be worked out from.

    The pairs are sorted by level and hold only the levels with story
    points above zero, because a factor is a ratio and a ratio to zero
    says nothing about how sizes grow from one level to the next.

    Args:
        levels: The configured defaults, in any order.

    Returns:
        The level number and story points of each usable level, sorted.
    """
    return sorted((level.level, level.story_points) for level in levels
                  if level.story_points > 0.0)


def _grown(low: tuple[int, float], high: tuple[int, float],
           level: int) -> Optional[float]:
    """Return the story points at one level on the curve through two.

    The two anchors fix a factor per level: the ratio of their story
    points spread evenly over the levels between them. The answer is the
    lower anchor grown by that factor once per level, which reaches the
    higher anchor again at its own level.

    Args:
        low: The level and story points of the lower anchor.
        high: The level and story points of the higher anchor, which is
            at a higher level than ``low``.
        level: The level to work out the story points for.

    Returns:
        The story points at that level, or None when the level is so far
        from the anchors that the answer is out of the range of a float.
    """
    factor: float = (high[1] / low[1]) ** (1.0 / (high[0] - low[0]))
    try:
        points: float = low[1] * factor ** (level - low[0])
    except OverflowError:
        return None
    return points


def _interpolated(anchors: list[tuple[int, float]],
                  level: int) -> Optional[float]:
    """Return the guess between the anchors around a level, or None.

    Args:
        anchors: The usable levels, sorted, at least two of them.
        level: The level to work out the story points for.

    Returns:
        The story points grown from the nearest anchor below to the
        nearest anchor above, or None when the level has no anchor on
        both sides of it.
    """
    below = [anchor for anchor in anchors if anchor[0] < level]
    above = [anchor for anchor in anchors if anchor[0] > level]
    if not below or not above:
        return None
    return _grown(below[-1], above[0], level)


def _extrapolated(anchors: list[tuple[int, float]],
                  level: int) -> Optional[float]:
    """Return the guess beyond the highest or lowest anchor, or None.

    Args:
        anchors: The usable levels, sorted, at least two of them.
        level: The level to work out the story points for.

    Returns:
        The story points grown on from the two highest anchors above them
        and from the two lowest anchors below them, or None when the
        level lies within the anchors.
    """
    if level > anchors[-1][0]:
        return _grown(anchors[-2], anchors[-1], level)
    if level < anchors[0][0]:
        return _grown(anchors[0], anchors[1], level)
    return None


class _DefPointsReadOldConfig(ReadOldConfiguration):
    """Read a configuration written before the guess was configurable.

    A file that has no default story points at all, and one that has an
    empty section of them, both mean the same thing: nothing is guessed,
    and an unestimated backlog item is worked with no story points.
    """

    def get_missing_path_values(self) -> dict[ConfigPath, object]:
        """Return the empty guess an older file leaves out."""
        return {('levels',): [], ('interpolate',): False,
                ('extrapolate',): False}


class DefaultStoryPoints(Config):
    """What a backlog item with no story points of its own counts as."""

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
            _points_for_level: What each given level counts as, by level
                number, built by :meth:`build_cache`.
        """
        self.interpolate: bool = False
        self.extrapolate: bool = False
        self.levels: list[DefaultStoryPointLevel] = []
        self._points_for_level: dict[int, float] = {}
        super().__init__(from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename,
                         auto_ch_hook=auto_ch_hook, stderr_file=stderr_file,
                         member_name=member_name)

    @override
    def _get_read_old_config(self) -> ReadOldConfiguration:
        """Accept an older file that leaves the whole guess out."""
        return _DefPointsReadOldConfig()

    @override
    def nested_configs(self) -> NestedConfigs:
        """Declare the given levels as nested configuration objects."""
        return {'levels': ConfigNesting(kind=ConfigNestingKind.LIST_ELEMENT,
                                        config_type=DefaultStoryPointLevel)}

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check the two settings, then the levels as a whole.

        The consistency check is given the stream of this validation, so
        that what it reports goes where the caller asked for it.
        """
        consistency = CallingWholeConfigValidator(
            'check_consistency', other_args={'stderr_file': stderr_file})
        flags = ValueTypeValidator(value_type=bool)
        return [MemberValidationStep(member_names=['interpolate',
                                                   'extrapolate'],
                                     validator=flags),
                WholeConfigValidationStep(validator=consistency)]

    def build_cache(self) -> None:
        """Build what each given level counts as, by level number.

        This is called whenever the configuration is validated. An
        application that changes the levels afterwards validates the
        configuration again, or calls this, before the changed levels are
        used.
        """
        self._points_for_level = {level.level: level.story_points
                                  for level in self.levels}

    def _check_unique_levels(self, stderr_file: TextIO) -> None:
        """Check that no level number is given story points twice."""
        seen: set[int] = set()
        for level in self.levels:
            if level.level in seen:
                report_bad_value('levels', level.level,
                                 'the same level given twice', stderr_file,
                                 _SUBJECT)
            seen.add(level.level)

    def _check_fill_in_levels(self, stderr_file: TextIO) -> None:
        """Check that filling in levels has two levels to work from."""
        for name in ('interpolate', 'extrapolate'):
            if getattr(self, name) and len(_anchors(self.levels)) < 2:
                report_bad_value(name, True, _NO_FACTOR, stderr_file, _SUBJECT)

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the given levels and build the level lookup.

        The levels are sorted by level number, so that a stored file reads
        from the smallest item upwards. Giving the same level twice is an
        error, and so is asking for levels to be filled in without the two
        levels a factor is worked out from.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            ValueError: A level is given twice, or a filled-in level is
                asked for without two levels to work the factor from.
        """
        self.levels.sort(key=lambda level: level.level)
        self._check_unique_levels(stderr_file)
        self._check_fill_in_levels(stderr_file)
        self.build_cache()

    def get_default_story_points(self, level: int) -> Optional[float]:
        """Return what a backlog item of one level counts as.

        A level that is given its own story points counts as those, zero
        included. A level that is not given any is filled in from the
        given ones as far as the two settings allow: between them when
        interpolation is allowed, and beyond them when extrapolation is.

        Args:
            level: The level of the backlog item to guess the size of.

        Returns:
            The story points to count such an item as, or None when the
            configuration says nothing about that level.
        """
        points = self._points_for_level.get(level)
        if points is not None:
            return points
        anchors = _anchors(self.levels)
        if len(anchors) < 2:
            return None
        if self.interpolate:
            guess = _interpolated(anchors, level)
            if guess is not None:
                return guess
        if self.extrapolate:
            return _extrapolated(anchors, level)
        return None
