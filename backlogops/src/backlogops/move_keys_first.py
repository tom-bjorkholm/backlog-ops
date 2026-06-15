#! /usr/bin/env python3
"""Reorder a backlog from a key list and extract keys by level."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional, TextIO
from collections.abc import Sequence
import sys
from backlogops.backlog import Backlog, BacklogItem
from backlogops.backlog_helpers import report_bad_value
from backlogops.levels import DEFAULT_LEVELS, Levels, level_number_from_name


def _by_key(backlog: Backlog) -> dict[str, BacklogItem]:
    """Return a mapping from each key to its backlog item."""
    return {item.key: item for item in backlog}


def _validate_keys(keys: Sequence[str], by_key: dict[str, BacklogItem],
                   stderr_file: TextIO) -> None:
    """Check that the keys are unique and present in the backlog."""
    seen: set[str] = set()
    for key in keys:
        if key in seen:
            report_bad_value('keys', key, 'duplicate key', stderr_file)
        seen.add(key)
        if key not in by_key:
            message = f'Key not found in backlog: {key!r}'
            print(message, file=stderr_file)
            raise KeyError(message)


def _children_map(backlog: Backlog) -> dict[str, list[BacklogItem]]:
    """Return the children of each key, in original backlog order."""
    children: dict[str, list[BacklogItem]] = {}
    for item in backlog:
        if item.parent_key is not None:
            children.setdefault(item.parent_key, []).append(item)
    return children


def _front_order(backlog: Backlog, keys: Sequence[str]) -> list[str]:
    """Return the leading keys: each named key after its descendant subtree.

    Each named key is preceded by its descendants in post order, so that a
    child comes right before its own parent and a parent right before the
    grandparent. Siblings keep their original backlog order. A named
    descendant is not pulled in, as it is placed by its own key. A
    descendant is pulled in only when it appears after its named ancestor
    in the backlog, so that no item is moved to a later position because
    of an ancestor's key.
    """
    named = set(keys)
    index = {item.key: position for position, item in enumerate(backlog)}
    children = _children_map(backlog)
    visited: set[str] = set()
    front: list[str] = []

    def emit_descendants(node_key: str, root_index: int) -> None:
        visited.add(node_key)
        for child in children.get(node_key, []):
            if child.key in named or child.key in visited:
                continue
            emit_descendants(child.key, root_index)
            if index[child.key] > root_index:
                front.append(child.key)

    for key in keys:
        emit_descendants(key, index[key])
        front.append(key)
    return front


def move_keys_first(backlog: Backlog, keys: Sequence[str],
                    stderr_file: TextIO = sys.stderr) -> Backlog:
    """Move the items named by ``keys`` to the front of the backlog.

    A new backlog is returned; the argument is not modified. The named
    items lead the backlog in the order of ``keys``. Each named item is
    preceded by its descendants in post order: a child comes right before
    its own parent, and that parent right before the grandparent, all the
    way up to the named item. For example, if ``E`` is a parent of ``S1``
    and ``S2`` and ``S2`` is a parent of ``T``, moving ``E`` first yields
    ``S1, T, S2, E``. Siblings keep their original backlog order. A named
    descendant is not pulled in this way; it is placed by its own key, so
    it may end up after its named parent. A descendant is pulled to the
    front only when it appears after its named ancestor in the backlog, so
    that no item is moved to a later position because of an ancestor's
    key. All items that are neither named nor pulled to the front keep
    their original order after the front block.

    Args:
        backlog: The backlog to reorder. The argument is not modified.
        keys: The keys to move to the front, in the wanted order. The keys
            must be unique and must exist in the backlog.
        stderr_file: The stream to report errors to.

    Returns:
        A new backlog with the named items moved to the front.

    Raises:
        KeyError: If a key is not found in the backlog.
        ValueError: If a key is not unique.
    """
    by_key = _by_key(backlog)
    _validate_keys(keys, by_key, stderr_file)
    front = _front_order(backlog, keys)
    front_set = set(front)
    moved = [by_key[key] for key in front]
    rest = [item for item in backlog if item.key not in front_set]
    return moved + rest


def _level_sequence(only_levels: int | str | Sequence[int | str]
                    ) -> Sequence[int | str]:
    """Return the requested levels as a sequence of single level values."""
    if isinstance(only_levels, (int, str)):
        return [only_levels]
    if isinstance(only_levels, Sequence):
        return only_levels
    raise TypeError('only_levels must be an int, a str, or a sequence of '
                    'ints or strs')


def _level_number(value: int | str, levels: Levels) -> int:
    """Return the level number for one int or str level value."""
    if isinstance(value, bool):
        raise TypeError('a level must be an int or a str, not a bool')
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return level_number_from_name(value, levels)
    raise TypeError('a level must be an int or a str')


def get_keys_in_order(backlog: Backlog,
                      only_levels: int | str | Sequence[int | str],
                      levels: Optional[Levels] = None) -> list[str]:
    """Return the keys of the backlog items at the given levels, in order.

    The keys are returned in the order they appear in the backlog, keeping
    only the items whose level is among ``only_levels``. A level may be
    given as a level number or as a level name or alias. A name or alias
    is resolved through ``levels`` (the default levels when ``levels`` is
    None). A level number is used as is and need not be one of ``levels``.

    Args:
        backlog: The backlog to take the keys from.
        only_levels: The levels to keep, as a single int or str or as a
            sequence of ints and strs.
        levels: The levels used to resolve a level name or alias, or None
            to use :data:`DEFAULT_LEVELS`.

    Returns:
        The keys of the matching items, in backlog order.

    Raises:
        TypeError: If ``only_levels`` is not an int, a str, or a sequence
            of ints and strs.
        ValueError: If a level name or alias matches no level.
    """
    chosen = DEFAULT_LEVELS if levels is None else levels
    numbers = {_level_number(value, chosen)
               for value in _level_sequence(only_levels)}
    return [item.key for item in backlog if item.level in numbers]
