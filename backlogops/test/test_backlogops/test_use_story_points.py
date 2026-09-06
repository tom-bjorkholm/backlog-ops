#! /usr/local/bin/python3
"""Tests for the story points one backlog item is worked with."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional
import pytest
from backlogops import (
    Backlog, BacklogItem, Status, find_keys_with_children, use_story_points)
from .shared_test_data import def_points


def item(key: str, points: Optional[float] = None, level: int = 1,
         status: Status = Status.TODO,
         parent: Optional[str] = None) -> BacklogItem:
    """Build one backlog item with the fields these tests vary."""
    return BacklogItem(key=key, level=level, title=key, story_points=points,
                       status=status, parent_key=parent)


def test_own_points_used() -> None:
    """An item that is estimated is worked with its own story points."""
    backlog: Backlog = [item('a', 3.0)]
    assert use_story_points(backlog, backlog[0], def_points({1: 9.0})) == 3.0


def test_half_point_kept() -> None:
    """Half a story point is worked with as it stands."""
    backlog: Backlog = [item('a', 0.5)]
    assert use_story_points(backlog, backlog[0], def_points({})) == 0.5


@pytest.mark.parametrize('status', [Status.DONE, Status.REJECTED])
def test_finished_is_free(status: Status) -> None:
    """A done or rejected item is no work left, whatever it carries."""
    backlog: Backlog = [item('a', 3.0, status=status)]
    assert use_story_points(backlog, backlog[0], def_points({1: 9.0})) == 0.0


def test_unestimated_guessed() -> None:
    """An unestimated item without children is worked with the guess."""
    backlog: Backlog = [item('a', None, level=2)]
    assert use_story_points(backlog, backlog[0], def_points({2: 7.0})) == 7.0


def test_unguessed_level_free() -> None:
    """An unestimated item of an unguessed level is no work at all."""
    backlog: Backlog = [item('a', None, level=2)]
    assert use_story_points(backlog, backlog[0], def_points({1: 7.0})) == 0.0


def test_container_is_free() -> None:
    """An unestimated item with children is a container and no work."""
    backlog: Backlog = [item('p', None, level=2), item('c', 3.0, parent='p')]
    assert use_story_points(backlog, backlog[0], def_points({2: 7.0})) == 0.0


def test_parent_own_points() -> None:
    """A parent with story points is worked with them beside its children."""
    backlog: Backlog = [item('p', 2.0, level=2), item('c', 3.0, parent='p')]
    assert use_story_points(backlog, backlog[0], def_points({2: 7.0})) == 2.0


def test_keys_with_children() -> None:
    """The keys with children are the keys some item names as its parent."""
    backlog: Backlog = [item('p', None, level=2), item('c', 1.0, parent='p'),
                        item('o', 1.0)]
    assert find_keys_with_children(backlog) == {'p'}


def test_given_keys_used() -> None:
    """The given keys with children are used instead of the backlog.

    Passing them is what keeps pricing a whole backlog one pass over it,
    so what is passed decides, even when the backlog is not walked.
    """
    lonely = item('a', None, level=2)
    assert use_story_points([], lonely, def_points({2: 7.0}), set()) == 7.0
    assert use_story_points([], lonely, def_points({2: 7.0}), {'a'}) == 0.0
