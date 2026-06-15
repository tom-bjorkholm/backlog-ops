#! /usr/bin/env python3
"""Move keys to the beginning of the backlog item."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import TextIO, Optional
from collections.abc import Sequence
import sys
from backlogops.backlog import Backlog
from backlogops.levels import Levels


def move_keys_first(backlog: Backlog, keys: Sequence[str],
                    stderr_file: TextIO = sys.stderr) -> Backlog:
    """Move keys to the beginning of the backlog.

    Conceptually, the function works as if copied the backlog and
    then moved the BacklogItems identified by the keys to the
    beginning of the copied backlog.
    The BacklogItem identified by the first key is moved first.
    For each subsequent key, the BacklogItem is inserted right after
    the BacklogItem identified by the previous key.
    However, if a BacklogItem identified by a key is the (direct or
    indirect) parent of other BacklogItems that are further down
    in the backlog, they are moved to a position right before their
    parent.
    As keys identifies BacklogItems at different levels, a BackogItem
    may be moved to a later position in the backlog when its own
    key is processed.
    A BacklogItem is never moved to a later position in the backlog
    due to a key of its (direct or indirect) parent.

    Args:
        backlog: The backlog to move keys in.
                 The argument object is not modified.
        keys: The keys to move to the beginning of the backlog item.
              The keys must be unique and must exist in the backlog.
        stderr_file: The file to report errors to.


    Raises:
        KeyError: If a key is not found in the backlog.
        ValueError: If a key is not unique.

    Returns:
        The backlog with the BacklogItems identified by the keys moved
        to the beginning of the backlog.
    """
    # implement this
    return backlog


def get_keys_in_order(backlog: Backlog,
                      only_levels: int | str | Sequence[int | str],
                      levels: Optional[Levels] = None) -> list[str]:
    """Get the keys from the backlog in order for the given levels.

    Get the keys from the backlog in the order they appear in the backlog,
    but only keys for BacklogItems at the given levels are included.

    Args:
        backlog: The backlog to get the keys from.
        only_levels: The levels to include the keys for.
        levels: The levels to use use for translating str values in
                only_levels to numbers. If None, the default levels
                are used.

    Raises:
        KeyError: If a value in only_levels is not a valid level.
        TypeError: If only_levels is not a single int, str, or sequence of
                   ints or strs.
                   If levels is not a Levels object.

    Returns:
        The keys of the BacklogItems in the order they appear in the backlog.
    """
    # implement this
    return []
