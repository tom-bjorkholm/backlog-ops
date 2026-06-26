#! /usr/local/bin/python3
"""Tests for backlog levels and level name resolution."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from io import StringIO

import pytest

from backlogops.levels import Level, LevelDisplay, Levels, DEFAULT_LEVELS
from backlogops.levels import check_levels_consistency, level_name
from backlogops.levels import level_number_from_name
from backlogops.no_text_io import NoTextIO


def _levels() -> Levels:
    """Return a small consistent set of levels for testing."""
    return {1: Level(level=1, name='Story', aliases=['Task', 'Bug']),
            2: Level(level=2, name='Epic', aliases=[])}


def test_level_name_known() -> None:
    """Test a configured level number resolves to its name."""
    assert level_name(2, _levels()) == 'Epic'


def test_level_name_unknown() -> None:
    """Test an unconfigured level number resolves to None."""
    assert level_name(7, _levels()) is None


def test_level_display_kinds() -> None:
    """Test the level display enum offers numeric, name and both."""
    assert {member.name for member in LevelDisplay} == \
        {'NUMERIC', 'NAME', 'BOTH'}


def test_level_ok() -> None:
    """Test a valid level passes its own consistency check."""
    Level(level=1, name='Story', aliases=['Task']).check_consistency(
        NoTextIO())


@pytest.mark.parametrize('level_value', [1.0, True, 'one'])
def test_level_bad_type(level_value: object) -> None:
    """Test a non-integer level number is reported as a TypeError."""
    level = Level(level=1, name='Story')
    level.level = level_value  # type: ignore[assignment]
    with pytest.raises(TypeError):
        level.check_consistency(NoTextIO())


@pytest.mark.parametrize('name', ['', 'a b', 'a,b', 'a(b)'])
def test_level_bad_name(name: str) -> None:
    """Test an invalid level name is reported as a ValueError."""
    with pytest.raises(ValueError):
        Level(level=1, name=name).check_consistency(NoTextIO())


@pytest.mark.parametrize('alias', ['', 'a b', 'a;b'])
def test_level_bad_alias(alias: str) -> None:
    """Test an invalid alias is reported as a ValueError."""
    with pytest.raises(ValueError):
        Level(level=1, name='Story', aliases=[alias]).check_consistency(
            NoTextIO())


def test_level_alias_bad_type() -> None:
    """Test a non-string alias is reported as a TypeError."""
    level = Level(level=1, name='Story', aliases=['ok'])
    level.aliases = [7]  # type: ignore[list-item]
    with pytest.raises(TypeError):
        level.check_consistency(NoTextIO())


def test_aliases_not_a_list() -> None:
    """Test an aliases value that is not a list is a TypeError."""
    level = Level(level=1, name='Story')
    level.aliases = 'Task'  # type: ignore[assignment]
    with pytest.raises(TypeError):
        level.check_consistency(NoTextIO())


def test_levels_ok() -> None:
    """Test consistent levels pass the levels consistency check."""
    check_levels_consistency(_levels(), NoTextIO())


def test_default_levels_ok() -> None:
    """Test the default levels are internally consistent."""
    check_levels_consistency(DEFAULT_LEVELS, NoTextIO())


def test_levels_key_mismatch() -> None:
    """Test a dict key not matching its level number is a ValueError."""
    levels = {5: Level(level=1, name='Story')}
    with pytest.raises(ValueError):
        check_levels_consistency(levels, NoTextIO())


@pytest.mark.parametrize('duplicate', ['Epic', 'epic', 'TASK', 'story'])
def test_levels_dup_label(duplicate: str) -> None:
    """Test a name or alias colliding (any case) is a KeyError."""
    levels = _levels()
    levels[2].aliases = [duplicate]
    with pytest.raises(KeyError):
        check_levels_consistency(levels, NoTextIO())


@pytest.mark.parametrize('name, expected', [
    ('Story', 1), ('story', 1), ('STORY', 1), ('Task', 1), ('bug', 1),
    ('Epic', 2)])
def test_name_to_number(name: str, expected: int) -> None:
    """Test names and aliases resolve case-insensitively to numbers."""
    assert level_number_from_name(name, _levels()) == expected


def test_name_unknown() -> None:
    """Test an unknown level name is reported as a ValueError."""
    stderr_file = StringIO()
    with pytest.raises(ValueError):
        level_number_from_name('Missing', _levels(), stderr_file)
    assert 'Missing' in stderr_file.getvalue()
