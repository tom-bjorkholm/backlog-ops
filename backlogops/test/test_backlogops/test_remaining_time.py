#! /usr/local/bin/python3
"""Tests for the remaining time configuration and its guess by level.

The configuration is read from JSON the way a configuration file carries
it, so these tests both check what a level is worked out as and what a
file is allowed to say.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import json
from datetime import timedelta
from pathlib import Path
from typing import Optional
import pytest
from backlogops import DefaultRemainingTimeLevel, RemainingTimeConfig
from backlogops.no_text_io import NoTextIO

NO = NoTextIO()


def time_text(levels: list[tuple[int, str]], interpolate: bool = False,
              extrapolate: bool = False) -> str:
    """Return the JSON text of remaining time in use, as a file holds it."""
    return json.dumps({
        'enable_remaining_time': True,
        'levels': [{'level': number, 'remaining_time': text}
                   for number, text in levels],
        'interpolate': interpolate, 'extrapolate': extrapolate,
        'default_focus_factor': 0.3})


def read(levels: list[tuple[int, str]], interpolate: bool = False,
         extrapolate: bool = False) -> RemainingTimeConfig:
    """Return the configuration read from the JSON of the given levels."""
    return RemainingTimeConfig(
        from_json_data_text=time_text(levels, interpolate, extrapolate),
        stderr_file=NO)


def hours(config: RemainingTimeConfig, span: range) -> list[Optional[float]]:
    """Return what each level of the span is worked out as, in hours."""
    times = [config.get_default_time(level) for level in span]
    return [None if time is None else time / timedelta(hours=1)
            for time in times]


def test_default_unused() -> None:
    """Test remaining time is off, and guesses nothing, by default."""
    config = RemainingTimeConfig(stderr_file=NO)
    assert config.enable_remaining_time is False
    assert config.default_focus_factor == 0.3
    assert hours(config, range(-1, 4)) == [None] * 5


def test_old_file_unused() -> None:
    """Test an empty section of an older file reads as not used."""
    config = RemainingTimeConfig(from_json_data_text='{}', stderr_file=NO)
    assert config.enable_remaining_time is False
    assert not config.levels
    assert config.interpolate is False
    assert config.extrapolate is False
    assert config.default_focus_factor == 0.3


def test_given_level_used() -> None:
    """Test a level given a remaining time is worked out as that time."""
    config = read([(1, '2:00:00'), (3, '8:00:00')])
    assert config.get_default_time(3) == timedelta(hours=8)


def test_only_given_levels() -> None:
    """Test only the given levels are worked out without filling in."""
    assert hours(read([(1, '2:00:00'), (3, '8:00:00')]), range(0, 5)) == \
        [None, 2.0, None, 8.0, None]


def test_filled_in_both_ways() -> None:
    """Test filling in both ways grows the time by the factor per level."""
    config = read([(1, '2:00:00'), (3, '8:00:00')], interpolate=True,
                  extrapolate=True)
    assert hours(config, range(-1, 6)) == pytest.approx(
        [0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0])


def test_zero_level_kept() -> None:
    """Test a level given no time at all is worked out as no time."""
    config = read([(0, '0:00:00'), (2, '4:00:00'), (3, '8:00:00')],
                  interpolate=True, extrapolate=True)
    assert config.get_default_time(0) == timedelta(0)


@pytest.mark.parametrize('given', ['0:00:00', '0:09:59'])
def test_small_no_factor(given: str) -> None:
    """Test a level under 10 minutes takes no part in the growth.

    Levels 2 and 3 grow by a factor of two, and level 1 is worked out
    from them as if nothing had been said about level 0.
    """
    config = read([(0, given), (2, '4:00:00'), (3, '8:00:00')],
                  interpolate=True, extrapolate=True)
    assert config.levels[0].remaining_time < timedelta(minutes=10)
    assert config.get_default_time(1) == timedelta(hours=2)


def test_small_level_usable() -> None:
    """Test a level of exactly 10 minutes is a full anchor."""
    config = read([(1, '0:10:00'), (2, '0:20:00')], extrapolate=True)
    assert config.get_default_time(3) == timedelta(minutes=40)


def test_days_as_hours(tmp_path: Path) -> None:
    """Test weeks and days in a file are written back as hours."""
    path = tmp_path / 'time.json'
    config = read([(1, '1d 1:30:45'), (2, '1w 0:00:00')])
    config.write(to_json_filename=path, stderr_file=NO)
    data = json.loads(path.read_text(encoding='UTF-8'))
    assert [level['remaining_time'] for level in data['levels']] == \
        ['25:30:45', '168:00:00']


def test_round_trip(tmp_path: Path) -> None:
    """Test remaining time survives being written and read back."""
    path = tmp_path / 'time.json'
    stored = read([(1, '2:00:00'), (3, '8:00:00')], interpolate=True)
    stored.default_focus_factor = 0.5
    stored.write(to_json_filename=path, stderr_file=NO)
    loaded = RemainingTimeConfig(from_json_filename=path, stderr_file=NO)
    assert loaded.enable_remaining_time is True
    assert loaded.default_focus_factor == 0.5
    assert loaded.get_default_time(2) == timedelta(hours=4)


def test_levels_sorted() -> None:
    """Test the levels are sorted by level number while they are checked."""
    config = read([(3, '8:00:00'), (1, '2:00:00')])
    assert [level.level for level in config.levels] == [1, 3]


def test_whole_focus_decimal() -> None:
    """Test a focus factor written as a whole number is kept as decimal."""
    text = json.dumps({'default_focus_factor': 1})
    config = RemainingTimeConfig(from_json_data_text=text, stderr_file=NO)
    assert isinstance(config.default_focus_factor, float)
    assert config.default_focus_factor == 1.0


def test_far_level_overflows() -> None:
    """Test a level so far away that the time overflows has no guess."""
    config = read([(1, '1:00:00'), (2, '10:00:00')], extrapolate=True)
    assert config.get_default_time(100) is None


def test_disabled_validated() -> None:
    """Test the levels are checked although remaining time is off."""
    data = json.loads(time_text([(1, '2:00:00'), (1, '3:00:00')]))
    data['enable_remaining_time'] = False
    with pytest.raises(ValueError):
        RemainingTimeConfig(from_json_data_text=json.dumps(data),
                            stderr_file=NO)


def test_level_in_code() -> None:
    """Test a level built in code with a timedelta validates."""
    config = RemainingTimeConfig(stderr_file=NO)
    level = DefaultRemainingTimeLevel(stderr_file=NO)
    level.level = 2
    level.remaining_time = timedelta(hours=3)
    config.levels.append(level)
    config.validate(NO)
    assert config.get_default_time(2) == timedelta(hours=3)


def test_negative_in_code() -> None:
    """Test a negative remaining time built in code is refused."""
    level = DefaultRemainingTimeLevel(stderr_file=NO)
    level.remaining_time = timedelta(hours=-1)
    with pytest.raises(ValueError):
        level.validate(NO)


@pytest.mark.parametrize('levels,interpolate,extrapolate', [
    ([(1, '2:00:00'), (1, '3:00:00')], False, False),
    ([(1, '2:00:00')], True, False),
    ([(1, '2:00:00')], False, True),
    ([], True, False),
    ([(1, '0:09:59'), (2, '0:09:59')], True, False),
    ([(1, '0:05:00'), (2, '2:00:00')], False, True)])
def test_refused_guess(levels: list[tuple[int, str]], interpolate: bool,
                       extrapolate: bool) -> None:
    """Test a repeated level, and filling in without two levels, refused."""
    with pytest.raises(ValueError):
        read(levels, interpolate, extrapolate)


@pytest.mark.parametrize('member,value', [
    ('remaining_time', '1:30'),
    ('remaining_time', ''),
    ('remaining_time', '-1:00:00'),
    ('remaining_time', 5400),
    ('remaining_time', True),
    ('remaining_time', None),
    ('level', 500),
    ('level', 1.5),
    ('level', True)])
def test_refused_level(member: str, value: object) -> None:
    """Test a level or a remaining time outside its rules is refused."""
    data: dict[str, object] = {'level': 1, 'remaining_time': '2:00:00'}
    data[member] = value
    text = json.dumps({'levels': [data]})
    with pytest.raises((TypeError, ValueError)):
        RemainingTimeConfig(from_json_data_text=text, stderr_file=NO)


@pytest.mark.parametrize('member,value', [
    ('enable_remaining_time', 'yes'),
    ('enable_remaining_time', 1),
    ('interpolate', 'yes'),
    ('default_focus_factor', 0.0),
    ('default_focus_factor', 0.0049),
    ('default_focus_factor', -0.1),
    ('default_focus_factor', 3.01),
    ('default_focus_factor', True),
    ('default_focus_factor', '0.3')])
def test_refused_setting(member: str, value: object) -> None:
    """Test a setting of the wrong type or out of range is refused."""
    text = json.dumps({member: value})
    with pytest.raises((TypeError, ValueError)):
        RemainingTimeConfig(from_json_data_text=text, stderr_file=NO)


@pytest.mark.parametrize('focus', [0.005, 0.3, 1.5, 3.0])
def test_focus_bounds(focus: float) -> None:
    """Test a focus factor from 0.005 to 3.0 is accepted."""
    text = json.dumps({'default_focus_factor': focus})
    config = RemainingTimeConfig(from_json_data_text=text, stderr_file=NO)
    assert config.default_focus_factor == focus
