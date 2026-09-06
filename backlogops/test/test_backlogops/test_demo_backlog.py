#! /usr/local/bin/python3
"""Tests for the demonstration backlog and releases."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from collections import Counter
from datetime import date
from backlogops import BacklogItem, get_demo_backlog
from backlogops.backlog import DEPENDENCY_FIELDS
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()


def _estimated() -> list[BacklogItem]:
    """Return the demo items that carry story points of their own."""
    return [item for item in get_demo_backlog().backlog
            if item.story_points is not None]


def _unestimated() -> list[BacklogItem]:
    """Return the demo items that nobody has estimated yet."""
    return [item for item in get_demo_backlog().backlog
            if item.story_points is None]


def test_level_counts() -> None:
    """Test the demo has 6 level-2, 26 level-1 and 7 level-0 items."""
    demo = get_demo_backlog()
    counts = Counter(item.level for item in demo.backlog)
    assert counts == Counter({1: 26, 2: 6, 0: 7})


def test_estimated_levels() -> None:
    """Test the estimated part is 3 epics, 20 stories and 2 tasks."""
    counts = Counter(item.level for item in _estimated())
    assert counts == Counter({1: 20, 2: 3, 0: 2})


def test_task_parents() -> None:
    """Test both estimated level-0 tasks share the same level-1 parent."""
    tasks = [item for item in _estimated() if item.level == 0]
    assert len(tasks) == 2
    assert {task.parent_key for task in tasks} == {'S1'}


def test_parented_stories() -> None:
    """Test exactly fifteen estimated level-1 stories have a parent."""
    stories = [item for item in _estimated() if item.level == 1]
    parented = [story for story in stories if story.parent_key is not None]
    assert len(parented) == 15


def test_points_are_decimal() -> None:
    """Test every story point of the demo is a decimal, half included."""
    points = {item.story_points for item in _estimated()}
    assert all(isinstance(value, float) for value in points)
    assert 0.5 in points


def test_unestimated_levels() -> None:
    """Test the unestimated part is 3 epics, 6 stories and 5 tasks."""
    counts = Counter(item.level for item in _unestimated())
    assert counts == Counter({2: 3, 1: 6, 0: 5})


def test_unestimated_epics() -> None:
    """Test two of the three unestimated epics have two children each.

    The third is a bigger item that nobody has broken down at all, which
    is what the guess for its level is there for.
    """
    children = Counter(item.parent_key for item in _unestimated()
                       if item.level == 1)
    epics = [item.key for item in _unestimated() if item.level == 2]
    assert len(epics) == 3
    assert sorted(children[key] for key in epics) == [0, 2, 2]


def test_unestimated_stories() -> None:
    """Test one story under an epic and one on its own have children.

    Of the four unestimated stories under an epic exactly one has two
    level-0 children, and of the two without a parent exactly one has.
    """
    stories = [item for item in _unestimated() if item.level == 1]
    children = Counter(item.parent_key for item in _unestimated()
                       if item.level == 0)
    under = [item.key for item in stories if item.parent_key is not None]
    alone = [item.key for item in stories if item.parent_key is None]
    assert sorted(children[key] for key in under) == [0, 0, 0, 2]
    assert sorted(children[key] for key in alone) == [0, 2]


def test_lone_unestimated() -> None:
    """Test one unestimated level-0 item stands on its own."""
    tasks = [item for item in _unestimated() if item.level == 0]
    assert [task.key for task in tasks if task.parent_key is None] == ['UT5']


def test_unestimated_alone() -> None:
    """Test no unestimated item is in a release or in a dependency."""
    keys = {item.key for item in _unestimated()}
    assert all(item.release is None for item in _unestimated())
    for item in get_demo_backlog().backlog:
        for field_name in DEPENDENCY_FIELDS:
            assert not keys.intersection(getattr(item, field_name))


def test_demo_releases() -> None:
    """Test the two releases and how many items reference each."""
    demo = get_demo_backlog()
    by_name = {release.name: release for release in demo.releases}
    assert set(by_name) == {'Next', 'Later'}
    assert by_name['Next'].planned_date is not None
    assert by_name['Next'].planned_date > date.today()
    assert by_name['Later'].planned_date is None
    releases = [item.release for item in demo.backlog]
    assert releases.count('Next') == 5
    assert releases.count('Later') == 5


def test_consistency() -> None:
    """Test the demo backlog passes all consistency checks."""
    get_demo_backlog().check_consistency(NO_OUTPUT)


def test_not_dep_ordered() -> None:
    """Test the backlog is not pre-sorted by dependencies."""
    keys = [item.key for item in get_demo_backlog().backlog]
    assert keys.index('S2') < keys.index('S3')
