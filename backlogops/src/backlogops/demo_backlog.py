#! /usr/local/bin/python3
"""A demonstration backlog and releases for manual tests and examples.

The estimated part of the demo data has three level-2 items (epics),
twenty level-1 items (stories) and two level-0 items (tasks). The two
tasks share the same story as parent, and fifteen of the stories have an
epic as parent. A few dependencies are added between items. Two releases
exist: ``Next`` with a planned date one month ahead, and ``Later`` with no
planned date. Five items are assigned to ``Next`` and five to ``Later``;
the rest have no release.

Beside those, fourteen items carry no story points at all, because nobody
has estimated them yet: three level-2 items, of which two have two
level-1 children each and one of those children has two level-0 children;
two more level-1 items without a parent, one of them with two level-0
children; and one level-0 item standing on its own. They show what the
configured default story points are for, and they are what makes the demo
useful for trying an estimate of a backlog that is not fully broken down.

The items are returned in a deliberately mixed order, so the backlog is
neither dependency-ordered nor release-ordered, while still passing all
consistency checks.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from calendar import monthrange
from datetime import date
from typing import Optional
from backlogops.backlog import BacklogItem, Status
from backlogops.backlog_releases import BacklogReleases
from backlogops.releases import Release

_POINTS = (0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0)
"""Story point values cycled over the estimated demo items."""

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


_UNESTIMATED = (
    ('UE1', 2, 'Unestimated epic 1', None),
    ('UE2', 2, 'Unestimated epic 2', None),
    ('UE3', 2, 'Unestimated epic 3', None),
    ('US1', 1, 'Unestimated story 1', 'UE1'),
    ('US2', 1, 'Unestimated story 2', 'UE1'),
    ('US3', 1, 'Unestimated story 3', 'UE2'),
    ('US4', 1, 'Unestimated story 4', 'UE2'),
    ('US5', 1, 'Unestimated story 5', None),
    ('US6', 1, 'Unestimated story 6', None),
    ('UT1', 0, 'Unestimated task 1', 'US1'),
    ('UT2', 0, 'Unestimated task 2', 'US1'),
    ('UT3', 0, 'Unestimated task 3', 'US5'),
    ('UT4', 0, 'Unestimated task 4', 'US5'),
    ('UT5', 0, 'Unestimated task 5', None))
"""The items nobody has estimated, as (key, level, title, parent key).

``UE3`` is a bigger item that is not broken down at all, ``UE1`` and
``UE2`` are broken down into children that are not estimated either, and
``US6``, ``UT5`` stand on their own at their level.
"""


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


def _unestimated() -> list[BacklogItem]:
    """Return the fourteen items that carry no story points at all.

    None of them is in a release or in a dependency, so they change
    neither the release counts nor the dependency graph of the demo.
    """
    return [BacklogItem(key=key, level=level, title=title, story_points=None,
                        status=Status.TODO, parent_key=parent)
            for key, level, title, parent in _UNESTIMATED]


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
                 tasks: list[BacklogItem],
                 unestimated: list[BacklogItem]) -> list[BacklogItem]:
    """Interleave the items so they are neither level nor release sorted.

    The unestimated items are spread over the result rather than kept
    together, so that a demo table shows them among the estimated ones.
    A position past the end of the list appends, which is what the last
    of them do.
    """
    items = list(stories)
    items.insert(3, epics[0])
    items.insert(9, tasks[0])
    items.insert(14, epics[1])
    items.insert(20, tasks[1])
    items.insert(23, epics[2])
    for offset, item in enumerate(unestimated):
        items.insert(offset * 3 + 2, item)
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
        A backlog with epics, stories and tasks, estimated and
        unestimated, and the ``Next`` and ``Later`` releases.
    """
    epics, stories, tasks = _epics(), _stories(), _tasks()
    by_key = {item.key: item for item in epics + stories + tasks}
    _apply_releases(by_key)
    _apply_dependencies(by_key)
    backlog = _mixed_order(epics, stories, tasks, _unestimated())
    releases = [Release(name='Next', planned_date=_one_month_ahead()),
                Release(name='Later')]
    return BacklogReleases(backlog=backlog, releases=releases)
