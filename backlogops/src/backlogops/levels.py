#! /usr/local/bin/python3
"""Levels of a backlog item."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass, field
import sys
from typing import NoReturn, TextIO
from backlogops.backlog_helpers import check_key_syntax, report_bad_value
from backlogops.backlog_helpers import report_wrong_type


@dataclass
class Level:
    """A level of a backlog item.

    Fields:
        level: The level of the backlog item. Required. Must be an integer.
               Usually a positive integer, but can be negative for special
               cases. A higher level means a bigger backlog item.
               A lower level means a smaller, more detailed backlog item.
        name: The name of the level. Required. Must be a string.
              Must not be empty, must not contain whitespace and must
              not contain any of the characters , . ; : ( ) [ ] { }.
              Must be unique within the Levels.
        aliases: The aliases of the level. Optional. Must be a list of strings.
                 For instance if level 1 is called "Story", it may have the
                 aliases "Task" and "Bug".
                 The aliases are used if a backlog item is converted from a
                 tool that have different names for the same level.
                 Each alias must not be empty, must not contain whitespace and
                 must not contain any of the characters , . ; : ( ) [ ] { }.
                 Must be unique within the Levels and must not be the same
                 as any name used in the Levels.
    """

    level: int
    name: str
    aliases: list[str] = field(default_factory=list)

    def _check_level_type(self, stderr_file: TextIO) -> None:
        """Check that the level number is an integer (not a bool)."""
        if not isinstance(self.level, int) or isinstance(self.level, bool):
            report_wrong_type('level', self.level, int, stderr_file, 'Level')

    def _check_labels(self, stderr_file: TextIO) -> None:
        """Check the name and each alias for valid label syntax."""
        check_key_syntax('name', self.name, stderr_file, 'Level')
        if not isinstance(self.aliases, list):
            report_wrong_type('aliases', self.aliases, list, stderr_file,
                              'Level')
        for index, alias in enumerate(self.aliases):
            check_key_syntax(f'aliases[{index}]', alias, stderr_file, 'Level')

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the consistency of the level.

        The documented constraints are checked on all member variables.
        The name and aliases follow the same character rules as a backlog
        item key. Uniqueness across levels is checked by
        :func:`check_levels_consistency`, not here.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If a field value violates a constraint.
        """
        self._check_level_type(stderr_file)
        self._check_labels(stderr_file)


type Levels = dict[int, Level]
"""A dictionary of levels by level number."""

DEFAULT_LEVELS: Levels = {
    0: Level(level=0, name='Sub-Task', aliases=[]),
    1: Level(level=1, name='Story', aliases=['Task', 'Bug']),
    2: Level(level=2, name='Epic', aliases=[]),
    3: Level(level=3, name='Initiative', aliases=[]),
}
"""The default levels for backlog items."""


def report_duplicate_label(label: str, existing: str,
                           stderr_file: TextIO = sys.stderr) -> NoReturn:
    """Report a duplicate level name or alias and raise ``KeyError``.

    Args:
        label: The label that duplicates an earlier one.
        existing: The earlier label it collides with.
        stderr_file: The file to report the error to.

    Raises:
        KeyError: Always, after reporting the message.
    """
    message = (f'Level name or alias {label!r} duplicates {existing!r} '
               f'(case-insensitive)')
    print(message, file=stderr_file)
    raise KeyError(message)


def check_levels_consistency(levels: Levels,
                             stderr_file: TextIO = sys.stderr) -> None:
    """Check the consistency of the levels.

    The documented constraints are checked on all levels. Each dict key
    must match the ``level`` field of its value. Names and aliases are
    checked for uniqueness across all levels using case-insensitive
    comparison, so that a name and an alias may not differ only in case.

    Args:
        levels: The levels to check.
        stderr_file: The file to report errors to.

    Raises:
        TypeError: If a field has the wrong type.
        ValueError: If a field value violates a constraint, or a dict key
            does not match its level number.
        KeyError: If a name or alias is not unique (case-insensitive).
    """
    seen_labels: dict[str, str] = {}
    for number, level in levels.items():
        level.check_consistency(stderr_file)
        if level.level != number:
            report_bad_value('level', level.level,
                             f'does not match dict key {number}', stderr_file,
                             'Level')
        for label in [level.name, *level.aliases]:
            lowered = label.lower()
            if lowered in seen_labels:
                report_duplicate_label(label, seen_labels[lowered],
                                       stderr_file)
            seen_labels[lowered] = label


def level_number_from_name(name: str, levels: Levels,
                           stderr_file: TextIO = sys.stderr) -> int:
    """Return the level number whose name or alias matches ``name``.

    Matching is case-insensitive but otherwise exact (no prefix or
    fuzzy matching). The level name and all of its aliases are
    considered. The levels are assumed to be consistent, as checked by
    :func:`check_levels_consistency`.

    Args:
        name: The level name or alias to look up.
        levels: The levels to search.
        stderr_file: The file to report errors to.

    Returns:
        The level number of the matching level.

    Raises:
        ValueError: If no level name or alias matches ``name``.
    """
    lowered = name.lower()
    for level in levels.values():
        if any(label.lower() == lowered
               for label in [level.name, *level.aliases]):
            return level.level
    report_bad_value('level', name, 'unknown level name or alias', stderr_file,
                     'Level')
