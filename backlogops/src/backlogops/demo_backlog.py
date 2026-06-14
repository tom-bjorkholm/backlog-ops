#! /usr/local/bin/python3
"""A demonstration backlog and releases for manual tests and examples.

The demo data has three level-2 items (epics), twenty level-1 items
(stories) and two level-0 items (tasks). The two tasks share the same
story as parent, and fifteen of the stories have an epic as parent. A few
dependencies are added between items. Two releases exist: ``Next`` with a
planned date one month ahead, and ``Later`` with no planned date. Five
items are assigned to ``Next`` and five to ``Later``; the rest have no
release. The items are returned in a deliberately mixed order, so the
backlog is neither dependency-ordered nor release-ordered, while still
passing all consistency checks.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from calendar import monthrange
from datetime import date
from typing import Optional
from backlogops.backlog import BacklogItem, Status
from backlogops.backlog_releases import BacklogReleases
from backlogops.releases import Release

_POINTS = (1, 2, 3, 5, 8, 13)
"""Story point values cycled over the demo items."""

_STATUSES = (Status.TODO, Status.IN_PROGRESS)
"""Statuses cycled over the demo items."""

_NEXT_KEYS = ('E1', 'S2', 'S7', 'S16', 'T1')
"""Demo items delivered in the ``Next`` release."""

_LATER_KEYS = ('E2', 'S3', 'S9', 'S18', 'T2')
"""Demo items delivered in the ``Later`` release."""

_DEPENDENCIES = (
    ('S2', 'depends_on_f2s', 'S3'),
    ('S5', 'depends_on_s2s', 'S6'),
    ('S10', 'depends_on_f2f', 'S11'),
    ('T1', 'depends_on_f2s', 'T2'),
    ('E3', 'depends_on_f2f', 'E1'))
"""A few demo dependencies as (item key, dependency field, target key)."""


def _make_item(key: str, level: int, title: str, index: int,
               parent_key: Optional[str] = None) -> BacklogItem:
    """Build one demo backlog item with cycled points and status."""
    return BacklogItem(key=key, level=level, title=title,
                       story_points=_POINTS[index % len(_POINTS)],
                       status=_STATUSES[index % len(_STATUSES)],
                       parent_key=parent_key)


def _epics() -> list[BacklogItem]:
    """Return the three level-2 epics."""
    return [_make_item(f'E{i + 1}', 2, f'Epic {i + 1}', i) for i in range(3)]


def _story_parent(index: int) -> Optional[str]:
    """Return the epic parent for a story, or None for the last five."""
    return f'E{index % 3 + 1}' if index < 15 else None


def _stories() -> list[BacklogItem]:
    """Return the twenty level-1 stories, fifteen with an epic parent."""
    return [_make_item(f'S{i + 1}', 1, f'Story {i + 1}', i, _story_parent(i))
            for i in range(20)]


def _tasks() -> list[BacklogItem]:
    """Return the two level-0 tasks, both children of story ``S1``."""
    return [_make_item(f'T{i + 1}', 0, f'Task {i + 1}', i, 'S1')
            for i in range(2)]


def _apply_releases(by_key: dict[str, BacklogItem]) -> None:
    """Assign the ``Next`` and ``Later`` releases to five items each."""
    for key in _NEXT_KEYS:
        by_key[key].release = 'Next'
    for key in _LATER_KEYS:
        by_key[key].release = 'Later'


def _apply_dependencies(by_key: dict[str, BacklogItem]) -> None:
    """Add the demo dependencies between items."""
    for key, field_name, target in _DEPENDENCIES:
        getattr(by_key[key], field_name).append(target)


def _mixed_order(epics: list[BacklogItem], stories: list[BacklogItem],
                 tasks: list[BacklogItem]) -> list[BacklogItem]:
    """Interleave the items so they are neither level nor release sorted."""
    items = list(stories)
    items.insert(3, epics[0])
    items.insert(9, tasks[0])
    items.insert(14, epics[1])
    items.insert(20, tasks[1])
    items.insert(23, epics[2])
    return items


def _one_month_ahead() -> date:
    """Return the date one calendar month after today."""
    today = date.today()
    month = today.month % 12 + 1
    year = today.year + (1 if today.month == 12 else 0)
    return date(year, month, min(today.day, monthrange(year, month)[1]))


def get_demo_backlog() -> BacklogReleases:
    """Return a demonstration backlog and its releases.

    The returned data passes :meth:`BacklogReleases.check_consistency`.
    It is useful for manual tests and for developers building
    applications on top of this library.

    Returns:
        A backlog with epics, stories and tasks, and the ``Next`` and
        ``Later`` releases.
    """
    epics, stories, tasks = _epics(), _stories(), _tasks()
    by_key = {item.key: item for item in epics + stories + tasks}
    _apply_releases(by_key)
    _apply_dependencies(by_key)
    backlog = _mixed_order(epics, stories, tasks)
    releases = [Release(name='Next', planned_date=_one_month_ahead()),
                Release(name='Later')]
    return BacklogReleases(backlog=backlog, releases=releases)
