#! /usr/local/bin/python3
"""The story points to work a backlog item with.

A backlog item carries the story points somebody estimated it at, or
carries none because nobody has estimated it yet. What the work on the
item is counted as is another matter, and it is what
:func:`use_story_points` answers: an item that is finished is no work
left, an item that is only a container for its children is no work of its
own, and an item nobody has estimated is what the configured
:class:`backlogops.DefaultStoryPoints` guesses for its level.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import Optional
from backlogops.backlog import Backlog, BacklogItem, Status
from backlogops.default_story_points import DefaultStoryPoints


def find_keys_with_children(backlog: Backlog) -> set[str]:
    """Return the keys of the backlog items that have children.

    Working this out once and handing it to :func:`use_story_points` is
    what keeps pricing a whole backlog a matter of one pass over it.

    Args:
        backlog: The backlog to take the parent references from.

    Returns:
        The key of every item that another item names as its parent.
    """
    return {item.parent_key for item in backlog
            if item.parent_key is not None}


def use_story_points(backlog: Backlog, backlog_item: BacklogItem,
                     default_story_points: DefaultStoryPoints,
                     keys_with_children: Optional[set[str]] = None) -> float:
    """Return the story points to work one backlog item with.

    A done or rejected item is no work left to do. An item that has story
    points of its own is worked with those, whether or not it has
    children, because those points are the work on the item itself beside
    the work in its children. An item without story points that has
    children is a container for them and is no work of its own. An item
    without story points and without children is a bigger item that
    nobody has broken down or estimated yet, and is worked with what the
    default story points guess for its level, or with none when they
    guess nothing for it.

    Args:
        backlog: The backlog the item belongs to, used to find out
            whether the item has children.
        backlog_item: The backlog item to find the story points of.
        default_story_points: What the configuration guesses for an item
            nobody has estimated.
        keys_with_children: The keys of the items that have children, as
            :func:`find_keys_with_children` returns them, or None to work
            them out from the backlog. Pass them when pricing more than
            one item, so that the backlog is walked once instead of once
            per item.

    Returns:
        The story points to work the item with, which is never negative.
    """
    if backlog_item.status in (Status.DONE, Status.REJECTED):
        return 0.0
    if backlog_item.story_points is not None:
        return backlog_item.story_points
    if keys_with_children is None:
        keys_with_children = find_keys_with_children(backlog)
    if backlog_item.key in keys_with_children:
        return 0.0
    guess = default_story_points.get_default_story_points(backlog_item.level)
    return guess if guess is not None else 0.0
