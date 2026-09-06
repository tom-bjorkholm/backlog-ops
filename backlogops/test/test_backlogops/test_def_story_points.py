#! /usr/local/bin/python3
"""Tests for the configured guess at an unestimated item's size.

The guess is read from JSON the way a configuration file carries it, so
these tests both check what a level is worked out as and what a file is
allowed to say.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import json
from pathlib import Path
from typing import Optional
import pytest
from backlogops import DefaultStoryPointLevel, DefaultStoryPoints
from backlogops.no_text_io import NoTextIO

NO = NoTextIO()


def points_text(levels: list[tuple[int, float]], interpolate: bool = False,
                extrapolate: bool = False) -> str:
    """Return the JSON text of a guess, as a file would hold it."""
    return json.dumps({
        'levels': [{'level': number, 'story_points': size}
                   for number, size in levels],
        'interpolate': interpolate, 'extrapolate': extrapolate})


def read(levels: list[tuple[int, float]], interpolate: bool = False,
         extrapolate: bool = False) -> DefaultStoryPoints:
    """Return the guess read from the JSON of the given levels."""
    return DefaultStoryPoints(
        from_json_data_text=points_text(levels, interpolate, extrapolate),
        stderr_file=NO)


def sizes(points: DefaultStoryPoints, levels: range) -> list[Optional[float]]:
    """Return what each of the levels is worked out as."""
    return [points.get_default_story_points(level) for level in levels]


def test_empty_guesses_none() -> None:
    """A guess with no levels says nothing about any level."""
    points = DefaultStoryPoints(stderr_file=NO)
    assert sizes(points, range(-1, 4)) == [None] * 5


def test_given_level_used() -> None:
    """A level that is given story points is worked out as those."""
    assert read([(1, 2.0), (3, 8.0)]).get_default_story_points(3) == 8.0


def test_only_given_levels() -> None:
    """Without filling in, only the given levels are worked out."""
    assert sizes(read([(1, 2.0), (3, 8.0)]), range(0, 5)) == \
        [None, 2.0, None, 8.0, None]


def test_interpolated_level() -> None:
    """A level between two given levels grows by their factor."""
    points = read([(1, 2.0), (3, 8.0)], interpolate=True)
    assert sizes(points, range(0, 5)) == [None, 2.0, 4.0, 8.0, None]


def test_extrapolated_levels() -> None:
    """Levels beyond the given ones continue with the same factor."""
    points = read([(1, 2.0), (3, 8.0)], extrapolate=True)
    assert sizes(points, range(-1, 6)) == \
        [0.5, 1.0, 2.0, None, 8.0, 16.0, 32.0]


def test_filled_in_both_ways() -> None:
    """Filling in both ways covers every level around the given ones."""
    points = read([(1, 2.0), (3, 8.0)], interpolate=True, extrapolate=True)
    assert sizes(points, range(-1, 6)) == \
        [0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]


def test_nearest_levels_used() -> None:
    """Each gap grows by the factor of the levels around that gap."""
    points = read([(0, 1.0), (2, 4.0), (5, 4.0)], interpolate=True)
    assert sizes(points, range(0, 6)) == [1.0, 2.0, 4.0, 4.0, 4.0, 4.0]


def test_zero_level_kept() -> None:
    """A level given zero story points is worked out as zero."""
    points = read([(0, 0.0), (2, 4.0), (3, 8.0)], interpolate=True,
                  extrapolate=True)
    assert points.get_default_story_points(0) == 0.0


@pytest.mark.parametrize('given', [0.0, 0.04])
def test_small_no_factor(given: float) -> None:
    """A level of nearly nothing takes no part in the growth.

    Levels 2 and 3 grow by a factor of two, and level 1 is worked out
    from them as if nothing had been said about level 0, which is under
    the story points a factor may be taken from.
    """
    points = read([(0, given), (2, 4.0), (3, 8.0)], interpolate=True,
                  extrapolate=True)
    assert points.get_default_story_points(0) == given
    assert points.get_default_story_points(1) == 2.0


def test_small_level_usable() -> None:
    """A level at the smallest usable story points is a full anchor."""
    points = read([(1, 0.05), (2, 0.1)], interpolate=True, extrapolate=True)
    assert points.get_default_story_points(3) == pytest.approx(0.2)


def test_levels_sorted() -> None:
    """The levels are sorted by level number while they are checked."""
    points = read([(3, 8.0), (1, 2.0), (2, 4.0)])
    assert [level.level for level in points.levels] == [1, 2, 3]


def test_whole_points_decimal() -> None:
    """Story points written as a whole number are kept as a decimal."""
    stored = read([(1, 2)]).levels[0].story_points
    assert isinstance(stored, float)
    assert stored == 2.0


def test_far_level_overflows() -> None:
    """A level so far away that the guess overflows has no guess."""
    points = read([(1, 2.0), (2, 4.0)], extrapolate=True)
    assert points.get_default_story_points(5000) is None


def test_far_level_below() -> None:
    """A level far below the given ones shrinks towards nothing."""
    points = read([(1, 2.0), (2, 4.0)], extrapolate=True)
    guess = points.get_default_story_points(-100)
    assert guess is not None
    assert 0.0 < guess < 1e-30


def test_round_trip(tmp_path: Path) -> None:
    """A guess survives being written to a file and read back."""
    path = tmp_path / 'points.json'
    stored = read([(1, 2.0), (3, 8.0)], interpolate=True)
    stored.write(to_json_filename=path, stderr_file=NO)
    loaded = DefaultStoryPoints(from_json_filename=path, stderr_file=NO)
    assert loaded.interpolate is True
    assert loaded.extrapolate is False
    assert loaded.get_default_story_points(2) == 4.0


def test_old_file_empty(tmp_path: Path) -> None:
    """A file written before the guess existed reads as no guess."""
    path = tmp_path / 'points.json'
    path.write_text('{}', encoding='UTF-8')
    loaded = DefaultStoryPoints(from_json_filename=path, stderr_file=NO)
    assert not loaded.levels
    assert loaded.interpolate is False
    assert loaded.extrapolate is False


def test_worked_out_kept() -> None:
    """A level worked out from the given ones is kept for the next ask."""
    points = read([(1, 2.0), (3, 8.0)], interpolate=True)
    assert points.get_default_story_points(2) == 4.0
    # pylint: disable-next=protected-access
    assert points._points_for_level[2] == 4.0


def test_kept_level_forgotten() -> None:
    """A level worked out earlier is forgotten when the levels change."""
    points = read([(1, 2.0), (3, 8.0)], interpolate=True)
    assert points.get_default_story_points(2) == 4.0
    points.levels[1].story_points = 32.0
    points.validate(NO)
    assert points.get_default_story_points(2) == 8.0


def test_missing_level_kept() -> None:
    """A level the guess says nothing about is not worked out twice."""
    points = read([(1, 2.0), (3, 8.0)])
    assert points.get_default_story_points(2) is None
    # pylint: disable-next=protected-access
    assert points._points_for_level[2] is None


def test_cache_rebuilt() -> None:
    """A level added afterwards is used once the guess is validated."""
    points = DefaultStoryPoints(stderr_file=NO)
    level = DefaultStoryPointLevel(stderr_file=NO)
    level.level = 2
    level.story_points = 5.0
    points.levels.append(level)
    assert points.get_default_story_points(2) is None
    points.validate(NO)
    assert points.get_default_story_points(2) == 5.0


@pytest.mark.parametrize('levels,interpolate,extrapolate', [
    ([(1, 2.0), (1, 3.0)], False, False),
    ([(1, 2.0)], True, False),
    ([(1, 2.0)], False, True),
    ([], True, False),
    ([(1, 0.0), (2, 0.0)], True, False),
    ([(1, 0.04), (2, 0.04)], True, False),
    ([(1, 0.04), (2, 2.0)], False, True)])
def test_refused_guess(levels: list[tuple[int, float]], interpolate: bool,
                       extrapolate: bool) -> None:
    """A repeated level, and filling in without two levels, are refused."""
    with pytest.raises(ValueError):
        read(levels, interpolate, extrapolate)


@pytest.mark.parametrize('member,value', [
    ('story_points', -1.0),
    ('story_points', True),
    ('story_points', '2'),
    ('level', 500),
    ('level', -500),
    ('level', 1.5),
    ('level', True)])
def test_refused_level(member: str, value: object) -> None:
    """A level or a story points value outside its rules is refused."""
    data: dict[str, object] = {'level': 1, 'story_points': 2.0}
    data[member] = value
    text = json.dumps({'levels': [data], 'interpolate': False,
                       'extrapolate': False})
    with pytest.raises((TypeError, ValueError)):
        DefaultStoryPoints(from_json_data_text=text, stderr_file=NO)


@pytest.mark.parametrize('member', ['interpolate', 'extrapolate'])
def test_refused_flag(member: str) -> None:
    """A setting that is not yes or no is refused."""
    data: dict[str, object] = {'levels': [], 'interpolate': False,
                               'extrapolate': False}
    data[member] = 'yes'
    with pytest.raises((TypeError, ValueError)):
        DefaultStoryPoints(from_json_data_text=json.dumps(data),
                           stderr_file=NO)
