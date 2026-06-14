#! /usr/local/bin/python3
"""Tests for the demonstration backlog and releases."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from collections import Counter
from datetime import date
from backlogops import get_demo_backlog
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()


def test_level_counts() -> None:
    """Test the demo has 3 level-2, 20 level-1 and 2 level-0 items."""
    demo = get_demo_backlog()
    counts = Counter(item.level for item in demo.backlog)
    assert counts == Counter({1: 20, 2: 3, 0: 2})


def test_task_parents() -> None:
    """Test both level-0 tasks share the same level-1 parent."""
    demo = get_demo_backlog()
    tasks = [item for item in demo.backlog if item.level == 0]
    assert len(tasks) == 2
    assert {task.parent_key for task in tasks} == {'S1'}


def test_parented_stories() -> None:
    """Test exactly fifteen level-1 stories have a parent."""
    stories = [item for item in get_demo_backlog().backlog if item.level == 1]
    parented = [story for story in stories if story.parent_key is not None]
    assert len(parented) == 15


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
