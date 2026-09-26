#! /usr/local/bin/python3
"""Best guess of a value by backlog item level, shared by its users.

A backlog item nobody has estimated still takes time, and a completion
date worked out as if it took none is wrong in the one direction that
matters. :class:`LevelDefaults` is the shared part of what the
configuration says such an item counts as: a value for a backlog item
level, and two settings that fill in the levels that are not given. The
value is story points in :class:`backlogops.DefaultStoryPoints` and
remaining time in :class:`backlogops.RemainingTimeConfig`; the growth
works on it as a float either way.

Filling in works with a factor, which is what one level up multiplies the
size by. Level 1 with 2 story points and level 3 with 8 grow by a factor
of 2 per level, so an interpolated level 2 is 4. Extrapolation continues
past the given levels with the factor of the two highest of them upwards
and the factor of the two lowest of them downwards, so level 4 is 16 and
level 0 is 1. A level given a value near zero counts as that value where
it is given, but takes no part in any factor, because a ratio to nearly
nothing says nothing about how sizes grow: it would make every level
above it absurdly large.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import sys
from typing import Callable, ClassVar, Generic, Optional, Protocol, \
    Sequence, TextIO, TypeVar, override
from config_as_json import CallingWholeConfigValidator, Config, \
    ConfigAutoChangeHook, ConfigNesting, ConfigNestingKind, ConfigPath, \
    IntFloatValidator, MemberValidationStep, MemberValidator, \
    MemberValidatorSequence, NestedConfigs, PathOrStr, \
    ReadOldConfiguration, ValidationPlan, ValueTypeValidator, \
    WholeConfigValidationStep
from backlogops.backlog_helpers import report_bad_value

type Anchor = tuple[int, float]
"""The level number and value of a level a factor may be worked out from."""

_LEVEL_LIMIT = 100
"""How far from zero a level number of a default may be."""


def level_validator() -> MemberValidator:
    """Return the validator of the level number of one default."""
    return MemberValidatorSequence([
        ValueTypeValidator(value_type=int, not_allowed_type=bool),
        IntFloatValidator(min_value=-_LEVEL_LIMIT, max_value=_LEVEL_LIMIT,
                          allowed_values=None)])


# pylint: disable-next=too-few-public-methods
class LevelDefault(Protocol):
    """What a default of one level offers to the shared growth."""

    level: int

    def as_float(self) -> float:
        """Return the value of this level as the number growth works on."""


_L = TypeVar('_L', bound=LevelDefault)
"""The class of the default of one level."""


def _anchors(levels: Sequence[LevelDefault], least: float) -> list[Anchor]:
    """Return the level and value pairs a factor may be worked out from.

    The pairs are sorted by level and hold only the levels of a value of
    at least ``least``, because a factor is a ratio and a ratio to
    nearly nothing says nothing about how sizes grow from one level to
    the next.

    Args:
        levels: The configured defaults, in any order.
        least: The smallest value that may take part in a factor.

    Returns:
        The level number and value of each usable level, sorted.
    """
    return sorted((level.level, level.as_float()) for level in levels
                  if level.as_float() >= least)


def _grown(low: Anchor, high: Anchor, level: int) -> Optional[float]:
    """Return the value at one level on the curve through two anchors.

    The two anchors fix a factor per level: the ratio of their values
    spread evenly over the levels between them. The answer is the lower
    anchor grown by that factor once per level, which reaches the higher
    anchor again at its own level.

    Args:
        low: The level and value of the lower anchor.
        high: The level and value of the higher anchor, which is at a
            higher level than ``low``.
        level: The level to work out the value for.

    Returns:
        The value at that level, or None when the level is so far from
        the anchors that the answer is out of the range of a float.
    """
    factor: float = (high[1] / low[1]) ** (1.0 / (high[0] - low[0]))
    try:
        value: float = low[1] * factor ** (level - low[0])
    except OverflowError:
        return None
    return value


def _interpolated(anchors: list[Anchor], level: int) -> Optional[float]:
    """Return the guess between the anchors around a level, or None.

    Args:
        anchors: The usable levels, sorted, at least two of them.
        level: The level to work out the value for.

    Returns:
        The value grown from the nearest anchor below to the nearest
        anchor above, or None when the level has no anchor on both sides
        of it.
    """
    below = [anchor for anchor in anchors if anchor[0] < level]
    above = [anchor for anchor in anchors if anchor[0] > level]
    if not below or not above:
        return None
    return _grown(below[-1], above[0], level)


def _extrapolated(anchors: list[Anchor], level: int) -> Optional[float]:
    """Return the guess beyond the highest or lowest anchor, or None.

    Args:
        anchors: The usable levels, sorted, at least two of them.
        level: The level to work out the value for.

    Returns:
        The value grown on from the two highest anchors above them and
        from the two lowest anchors below them, or None when the level
        lies within the anchors.
    """
    if level > anchors[-1][0]:
        return _grown(anchors[-2], anchors[-1], level)
    if level < anchors[0][0]:
        return _grown(anchors[0], anchors[1], level)
    return None


class _MissingReadOldConfig(ReadOldConfiguration):
    """Read a configuration written before its members were configurable.

    What the older file leaves out is asked from the configuration being
    read each time, so that every read gets fresh values to put into it.
    """

    def __init__(self, missing: Callable[[], dict[ConfigPath, object]]
                 ) -> None:
        """Remember how to get the values an older file leaves out."""
        super().__init__()
        self._missing = missing

    def get_missing_path_values(self) -> dict[ConfigPath, object]:
        """Return the values an older file leaves out."""
        return self._missing()


class LevelDefaults(Config, Generic[_L]):
    """The shared guess of a value by level, and its fill-in settings.

    A subclass creates ``levels``, ``interpolate`` and ``extrapolate`` in
    its constructor, in the order it wants them in the file, before it
    calls the constructor of this class. It names its level class in
    :attr:`_LEVEL_TYPE` and itself in :attr:`_SUBJECT`, sets the smallest
    value a factor may be worked out from in :attr:`_NEAR_ZERO`, and says
    why filling in is refused without two such levels in
    :attr:`_NO_FACTOR`.

    Attributes:
        levels: The value given for a level, sorted by level number
            while the configuration is validated.
        interpolate: Whether a level between two given levels is guessed
            from them.
        extrapolate: Whether a level above the highest or below the
            lowest given level is guessed from the two nearest ones.
        _value_for_level: What each level asked for counts as, by level
            number, as the float growth works on. :meth:`build_cache`
            puts the given levels in it, and a level worked out from them
            is added to it the first time it is asked for.
    """

    _LEVEL_TYPE: ClassVar[type[Config]]
    _SUBJECT: ClassVar[str]
    _NEAR_ZERO: ClassVar[float]
    _NO_FACTOR: ClassVar[str]
    levels: list[_L]
    interpolate: bool
    extrapolate: bool
    _value_for_level: dict[int, Optional[float]]

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr, *,
                 member_name: Optional[str] = None) -> None:
        """Create the empty level lookup, then read the configuration.

        Args:
            from_json_data_text: Optional JSON text to parse directly.
            from_json_filename: Optional JSON file to read.
            auto_ch_hook: Hook notified about backward-compatible changes
                made while reading.
            stderr_file: Stream used for user-facing diagnostics.
            member_name: Path for reaching this object from the top level,
                so that a diagnostic names the whole path. None for an
                object that is a member of nothing.
        """
        self._value_for_level = {}
        super().__init__(from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename,
                         auto_ch_hook=auto_ch_hook, stderr_file=stderr_file,
                         member_name=member_name)

    def _missing_members(self) -> dict[ConfigPath, object]:
        """Return the empty guess an older file leaves out.

        A file that has no section of this configuration at all, and one
        that has an empty section, both mean the same thing: nothing is
        guessed. A subclass adds the members of its own. A fresh
        dictionary and list are returned on every call, because the
        values are put into the configuration that is read.
        """
        return {('levels',): [], ('interpolate',): False,
                ('extrapolate',): False}

    @override
    def _get_read_old_config(self) -> ReadOldConfiguration:
        """Accept an older file that leaves the whole section out."""
        return _MissingReadOldConfig(self._missing_members)

    @override
    def nested_configs(self) -> NestedConfigs:
        """Declare the given levels as nested configuration objects."""
        return {'levels': ConfigNesting(kind=ConfigNestingKind.LIST_ELEMENT,
                                        config_type=self._LEVEL_TYPE)}

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
        """Build the lookup afresh from the levels that are given.

        The levels worked out from the given ones are not built here.
        Each of them is added to the same lookup the first time it is
        asked for, so a backlog of many items works out a level once
        however many items are at that level.

        This is called whenever the configuration is validated, and
        starting afresh is what forgets the levels worked out from the
        earlier ones. An application that changes the levels afterwards
        validates the configuration again, or calls this, before the
        changed levels are used.
        """
        self._value_for_level = {level.level: level.as_float()
                                 for level in self.levels}

    def _check_unique_levels(self, stderr_file: TextIO) -> None:
        """Check that no level number is given a value twice."""
        seen: set[int] = set()
        for level in self.levels:
            if level.level in seen:
                report_bad_value('levels', level.level,
                                 'the same level given twice', stderr_file,
                                 self._SUBJECT)
            seen.add(level.level)

    def _anchors(self) -> list[Anchor]:
        """Return the given levels a factor may be worked out from."""
        return _anchors(self.levels, self._NEAR_ZERO)

    def _check_fill_in_levels(self, stderr_file: TextIO) -> None:
        """Check that filling in levels has two levels to work from."""
        for name in ('interpolate', 'extrapolate'):
            if getattr(self, name) and len(self._anchors()) < 2:
                report_bad_value(name, True, self._NO_FACTOR, stderr_file,
                                 self._SUBJECT)

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

    def _worked_out(self, level: int) -> Optional[float]:
        """Return what a level that is given no value counts as."""
        anchors = self._anchors()
        if len(anchors) < 2:
            return None
        if self.interpolate:
            guess = _interpolated(anchors, level)
            if guess is not None:
                return guess
        if self.extrapolate:
            return _extrapolated(anchors, level)
        return None

    def _value_of_level(self, level: int) -> Optional[float]:
        """Return what a backlog item of one level counts as, as a float.

        A level that is given its own value counts as that, zero
        included. A level that is not given any is filled in from the
        given ones as far as the two settings allow: between them when
        interpolation is allowed, and beyond them when extrapolation is.
        What a level counts as is worked out once and then kept, so a
        backlog of many items costs one lookup for each of them.

        Args:
            level: The level of the backlog item to guess the size of.

        Returns:
            The value to count such an item as, or None when the
            configuration says nothing about that level.
        """
        if level not in self._value_for_level:
            self._value_for_level[level] = self._worked_out(level)
        return self._value_for_level[level]
