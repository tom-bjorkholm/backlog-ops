#! /usr/local/bin/python3
"""Order a backlog by dependencies."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
import heapq
from enum import Enum, auto
from typing import Optional, TextIO
from collections.abc import Sequence
from backlogops.backlog import Backlog, BacklogItem, DEPENDENCY_FIELDS
from backlogops.backlog import build_dependency_graph, event_start


class DependencyMode(Enum):
    """Mode to determine backlog position of items with dependencies.

    EARLY: All items that take part in a dependency are placed as early
           as possible, before the items that take part in no
           dependency. This packs the dependency chains at the front and
           leaves a buffer of independent items after the last dependent
           item, to reduce the risk of delays in a chain of dependencies.
    EVEN:  Items that take part in a dependency are spread out so that
           the dependency chains are as evenly distributed as possible
           over the complete backlog. The independent items fill the gaps
           between them. This may create a small time buffer between each
           item in a dependency chain.
    KEEP:  Items that take part in no dependency keep their original
           relative order, and only the items that take part in a
           dependency are moved, and only as far as a dependency forces
           them to move. The idea is that someone has already put work
           into the order of the backlog, and we should not change it
           without a good reason. This is the default behavior.
    """

    EARLY = auto()
    EVEN = auto()
    KEEP = auto()


def _normalize_space_around(space_around: Optional[str | Sequence[str]],
                            stderr_file: TextIO) -> list[str]:
    """Return the space_around argument as a list of key strings.

    A single key is wrapped in a one element list and a sequence of keys
    is copied into a new list. ``None`` becomes an empty list.

    Raises:
        TypeError: If the argument is neither None, a string, nor a
            sequence of strings.
    """
    if space_around is None:
        return []
    if isinstance(space_around, str):
        return [space_around]
    if isinstance(space_around, Sequence) and \
            all(isinstance(key, str) for key in space_around):
        return list(space_around)
    message = 'space_around must be a string or a sequence of strings'
    print(message, file=stderr_file)
    raise TypeError(message)


def _space_around_limit(item_count: int) -> int:
    """Return the largest allowed number of space_around items.

    The limit is five items for a backlog of at least fifty items, and
    ten percent of the backlog (but at least one) for a smaller backlog.
    """
    if item_count >= 50:
        return 5
    return max(1, item_count // 10)


def _check_space_around(keys: Sequence[str], backlog: Backlog,
                        stderr_file: TextIO) -> None:
    """Check that the space_around keys exist and are not too many.

    Raises:
        KeyError: If a key is not the key of a backlog item.
        RuntimeError: If there are more keys than the allowed limit.
    """
    present = {item.key for item in backlog}
    for key in keys:
        if key not in present:
            message = f'space_around key not found in backlog: {key!r}'
            print(message, file=stderr_file)
            raise KeyError(message)
    limit = _space_around_limit(len(backlog))
    if len(keys) > limit:
        message = (f'space_around has {len(keys)} keys, more than the '
                   f'allowed {limit}')
        print(message, file=stderr_file)
        raise RuntimeError(message)


def _item_dependencies(item: BacklogItem) -> list[str]:
    """Return the keys that one item depends on (explicit and parent)."""
    keys: list[str] = []
    for dep_field in DEPENDENCY_FIELDS:
        keys.extend(getattr(item, dep_field))
    if item.parent_key is not None:
        keys.append(item.parent_key)
    return keys


def _has_dependencies(backlog: Backlog) -> bool:
    """Tell whether any backlog item takes part in a dependency."""
    return any(_item_dependencies(item) for item in backlog)


def _linked_items(backlog: Backlog) -> set[str]:
    """Return the keys of items that take part in any dependency.

    An item is linked when it depends on another item or is depended on
    by another item, counting both the explicit dependency lists and the
    parent relations.
    """
    linked: set[str] = set()
    for item in backlog:
        dependencies = _item_dependencies(item)
        if dependencies:
            linked.add(item.key)
            linked.update(dependencies)
    return linked


def _seed_events(backlog: Backlog) -> list[str]:
    """Return all start and finish events in original backlog order."""
    events: list[str] = []
    for item in backlog:
        events.append(event_start(item.key))
        events.append(f'{item.key}:finish')
    return events


def _forward_events(graph: dict[str, list[str]],
                    seed: Sequence[str]) -> list[str]:
    """Order events with each prerequisite emitted just before its user.

    A depth first search visits the events in original order and emits
    every event after all the events it depends on. This pulls a
    prerequisite to a position just before the dependent item, while the
    dependent item keeps its original position as much as possible.
    """
    visited: set[str] = set()
    order: list[str] = []

    def visit(event: str) -> None:
        if event in visited:
            return
        visited.add(event)
        for dependency in graph.get(event, []):
            visit(dependency)
        order.append(event)
    for event in seed:
        visit(event)
    return order


def _back_events(graph: dict[str, list[str]],
                 seed: Sequence[str]) -> list[str]:
    """Order events delaying each dependent event as long as possible.

    A stable topological sort always emits the ready event with the
    smallest original position. This keeps the independent events early
    and pushes a dependent event as late as its prerequisites allow.
    """
    rank = {event: index for index, event in enumerate(seed)}
    pending = {event: set(graph.get(event, [])) for event in seed}
    dependents: dict[str, list[str]] = {}
    for event, dependencies in pending.items():
        for dependency in dependencies:
            dependents.setdefault(dependency, []).append(event)
    ready = [(rank[event], event)
             for event, deps in pending.items() if not deps]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        _, event = heapq.heappop(ready)
        order.append(event)
        for dependent in dependents.get(event, []):
            pending[dependent].discard(event)
            if not pending[dependent]:
                heapq.heappush(ready, (rank[dependent], dependent))
    return order


def _topo_item_order(backlog: Backlog, later: bool) -> list[str]:
    """Return the item keys in dependency order, projected from events.

    The events of the backlog are topologically sorted, honoring the
    direction given by ``later``, and the item order is read off from the
    order of the start events. The backlog position of an item is the
    order in which a team starts to work on it.
    """
    graph = build_dependency_graph(backlog)
    seed = _seed_events(backlog)
    events = _back_events(graph, seed) if later \
        else _forward_events(graph, seed)
    start_to_key = {event_start(item.key): item.key for item in backlog}
    return [start_to_key[event] for event in events if event in start_to_key]


def _merge_even(linked: Sequence[str], unlinked: Sequence[str]) -> list[str]:
    """Merge linked and unlinked keys, spreading linked keys evenly.

    The linked keys keep their given order and the unlinked keys keep
    their given order. The linked keys are placed at evenly spaced
    positions over the whole result, and the unlinked keys fill the gaps.
    """
    total = len(linked) + len(unlinked)
    if not linked:
        return list(unlinked)
    targets = [(index + 0.5) * total / len(linked)
               for index in range(len(linked))]
    result: list[str] = []
    next_linked = 0
    next_unlinked = 0
    for position in range(total):
        due = next_linked < len(linked) and \
            targets[next_linked] <= position + 0.5
        if (due or next_unlinked >= len(unlinked)) and \
                next_linked < len(linked):
            result.append(linked[next_linked])
            next_linked += 1
        else:
            result.append(unlinked[next_unlinked])
            next_unlinked += 1
    return result


def _arrange_by_mode(topo: Sequence[str], backlog: Backlog,
                     mode: DependencyMode) -> list[str]:
    """Place the dependency-ordered keys according to the chosen mode."""
    if mode is DependencyMode.KEEP:
        return list(topo)
    linked = _linked_items(backlog)
    linked_order = [key for key in topo if key in linked]
    unlinked_order = [item.key for item in backlog
                      if item.key not in linked]
    if mode is DependencyMode.EARLY:
        return linked_order + unlinked_order
    return _merge_even(linked_order, unlinked_order)


def _start_reachable(graph: dict[str, list[str]], item: BacklogItem,
                     backlog: Backlog) -> set[str]:
    """Return the keys of items that must start before the given item.

    The search follows the dependency edges from the start event of the
    item. Reaching either the start or the finish event of another item
    means that other item must start before this item.
    """
    start_to_key = {event_start(other.key): other.key for other in backlog}
    finish_to_key = {f'{other.key}:finish': other.key for other in backlog}
    seen: set[str] = set()
    stack = [event_start(item.key)]
    while stack:
        event = stack.pop()
        for dependency in graph.get(event, []):
            if dependency not in seen:
                seen.add(dependency)
                stack.append(dependency)
    keys: set[str] = set()
    for event in seen:
        key = start_to_key.get(event) or finish_to_key.get(event)
        if key is not None and key != item.key:
            keys.add(key)
    return keys


def _precedence(backlog: Backlog) -> tuple[dict[str, set[str]],
                                           dict[str, set[str]]]:
    """Return the must-start-before and must-start-after item relations."""
    graph = build_dependency_graph(backlog)
    before = {item.key: _start_reachable(graph, item, backlog)
              for item in backlog}
    after: dict[str, set[str]] = {item.key: set() for item in backlog}
    for key, prerequisites in before.items():
        for prerequisite in prerequisites:
            after[prerequisite].add(key)
    return before, after


def precedence_relations(backlog: Backlog) -> tuple[dict[str, set[str]],
                                                    dict[str, set[str]]]:
    """Return the must-start-before and must-start-after key relations.

    The first mapping gives, for each item key, the keys of the items that
    must start before that item can start, that is its transitive
    prerequisites. The second mapping gives, for each item key, the keys of
    the items that can only start after that item has started, that is its
    transitive dependents. Both combine the explicit dependency lists with
    the implicit parent relations, as documented for
    :func:`backlogops.backlog.build_dependency_graph`. A parent is a start
    prerequisite of its child, so a child is a start dependent of its
    parent.

    Args:
        backlog: The backlog to take the relations from.

    Returns:
        The must-start-before and must-start-after relations, each as a
        mapping from an item key to the set of related item keys.
    """
    return _precedence(backlog)


def _space_one(order: Sequence[str], key: str, prereqs: set[str],
               dependents: set[str]) -> list[str]:
    """Reposition one key to maximize the space to its dependencies.

    The prerequisites of the key are moved as early as possible and the
    items that depend on the key are moved as late as possible, keeping
    their relative order. The key is then placed among the remaining
    items: at the front when it has no prerequisite, at the back when it
    has no dependent, and in the middle otherwise. This places as many
    other items as possible between the key and its dependencies.
    """
    front = [item for item in order if item in prereqs]
    back = [item for item in order if item in dependents]
    middle = [item for item in order if item != key
              and item not in prereqs and item not in dependents]
    if not prereqs:
        insert = 0
    elif not dependents:
        insert = len(middle)
    else:
        insert = len(middle) // 2
    return front + middle[:insert] + [key] + middle[insert:] + back


def _apply_space_around(order: list[str], keys: Sequence[str],
                        backlog: Backlog) -> list[str]:
    """Reposition each space_around key to the middle of its slack."""
    before, after = _precedence(backlog)
    for key in keys:
        order = _space_one(order, key, before[key], after[key])
    return order


def order_by_dependencies(backlog: Backlog, *, later: bool = False,
                          mode: DependencyMode = DependencyMode.KEEP,
                          space_around: Optional[str | Sequence[str]] = None,
                          stderr_file: TextIO = sys.stderr) -> Backlog:
    """Order a backlog by dependencies.

    A new backlog is returned; the argument is not modified. If no item
    takes part in any dependency the argument backlog is returned
    unchanged (the same object). The backlog is ordered so that a team
    can start the items in backlog order without starting an item before
    the items it depends on. The dependencies are taken from the start
    and finish event graph of the backlog, which combines the explicit
    dependency lists with the implicit parent relations. The backlog
    position of an item is the order in which the team starts it, so only
    a dependency that constrains the start of an item moves that item;
    a finish-to-finish dependency, which only constrains completion, does
    not move an item by itself.

    Args:
        backlog: The backlog to order. The argument is not modified.
        later: How a dependency that is not yet satisfied is resolved.
            If False (the default) the prerequisite item is pulled to a
            position just before the dependent item, and the dependent
            item keeps its position. If True the dependent item is pushed
            to a position just after its prerequisites, and the
            prerequisite items keep their position.
        mode: How items that take part in a dependency are placed in
            relation to items that take part in no dependency, as
            documented for :class:`DependencyMode`. The default is KEEP.
        space_around: Key or keys of items that should have as many other
            items as possible placed between them and the items they
            depend on, and between them and the items that depend on them.
            For each named item the prerequisites are pulled as early as
            possible and the items that depend on it are pushed as late as
            possible, and the named item is centered among the remaining
            items. This is useful when there is a big risk of delays in a
            chain of dependencies. It only works well for one or very few
            items. None means no item is treated this way.
        stderr_file: The file to report errors to.

    Returns:
        A new backlog with the items ordered by dependencies, or the
        argument backlog unchanged when no item takes part in a
        dependency.

    Raises:
        TypeError: If space_around is neither None, a string, nor a
            sequence of strings.
        KeyError: If a space_around key is not the key of a backlog item.
        RuntimeError: If space_around names more keys than allowed: more
            than five, or more than ten percent of a backlog of fewer
            than fifty items.
    """
    space_keys = _normalize_space_around(space_around, stderr_file)
    _check_space_around(space_keys, backlog, stderr_file)
    if not _has_dependencies(backlog):
        return backlog
    topo = _topo_item_order(backlog, later)
    order = _arrange_by_mode(topo, backlog, mode)
    order = _apply_space_around(order, space_keys, backlog)
    by_key = {item.key: item for item in backlog}
    return [by_key[key] for key in order]
