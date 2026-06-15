#! /usr/local/bin/python3
"""Order a backlog by dependencies."""

# Copyright (c) 2026, Tom Björkholm
# MIT License


from typing import Optional, TextIO, Sequence
from enum import Enum, auto
import sys
from backlogops.backlog import Backlog


class DependencyMode(Enum):
    """Mode to determine backlog position of items with dependencies.

    EARLY: All items with dependencies are placed as early as possible.
           This may create a time buffer after the last item with
           dependencies, to reduce the risk of delays in a chain of
           dependencies.
    EVEN:  Items with dependencies are spread out so that each
           dependency chain is as evenly distributed as possible
           over the complete backlog. This may create a small
           time buffer between each item in a dependency chain.
    KEEP:  Items without dependencies are kept in their original position.
           The idea is that someone has already put work into the
           order of the backlog, and we should not change it without
           a good reason.
           This is the default behavior.
    """

    EARLY = auto()
    EVEN = auto()
    KEEP = auto()


def order_by_dependencies(backlog: Backlog, *, later: bool = False,
                          mode: DependencyMode = DependencyMode.KEEP,
                          space_around: Optional[str | Sequence[str]] = None,
                          stderr_file: TextIO = sys.stderr) -> Backlog:
    """Order a backlog by dependencies.

    A new backlog is returned; the argument is not modified.
    If no dependencies are found, the argument backlog is returned unchanged.
    The backlog is ordered so that the team(s) can work on the items in the
    backlog order without violating dependencies. This is achieved by moving
    items with dependencies to a position after/later than the item
    it depends on, or to a position before/earlier than the item it depends on.
    Items without dependencies are not normally moved, but can be moved
    between items that depend on each other, if one of the items is named by
    space_around or mode is EVEN.

    Args:
        backlog: The backlog to order. The argument is not modified.
        later: If True an item that depends on another item is moved
               after/later than the item it depends on.
               If False an item that depends on another item is moved
               before/earlier than the item it depends on.
        mode: Mode to determine backlog position of items with dependencies,
              in relation to items without dependencies. The default is KEEP.
        space_around: Key(s) of items in the backlog that should have as much
                      space between them and the items they depend on or items
                      that depend on them as possible.
                      This means that as many other backlog items as possible
                      are placed between them and the items they depend on,
                      and between them and items that depend on them.
                      This is useful when there is a big risk of delays in
                      a chain of dependencies.
                      Notice that this only works for one or very few items.
                      If None, no items receive this extra care.
        stderr_file: The file to report errors to.

    Returns:
        A new backlog with the items ordered by dependencies.
        If no dependencies are found, the argument backlog is returned
        unchanged.
    Raises:
        ValueError: If the space_around is not a string or a sequence of
                    strings.
        KeyError:   If a key in space_around is not found in the backlog.
        RuntimeError: If the number of items in space_around is more than
                      5 (or more than 10% of the total number of items in the
                      backlog if there are less than 50 items in the backlog).
        TypeError: If the space_around is not a string or a sequence of
                   strings.
    """
    # implement this
    return backlog
