#! /usr/local/bin/python3
"""Functions to sort backlog items in release order."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import TextIO
import sys
import heapq
from backlogops.backlog import Backlog, BacklogItem
from backlogops.releases import Releases


def _report_unknown_release(item: BacklogItem, stderr_file: TextIO) -> None:
    """Report a backlog item that names a release not in the list.

    The message is written to ``stderr_file`` and no exception is raised,
    so the item is still ordered (after the last release).
    """
    print(f"Backlog item {item.key!r} field 'release' references "
          f'unknown release {item.release!r}', file=stderr_file)


def _release_rank(backlog: Backlog, releases: Releases,
                  stderr_file: TextIO) -> dict[str, int]:
    """Return each backlog item key mapped to its release rank.

    The rank of an item is the position (zero based) of its release in
    the ``releases`` list. An item with no release, or with a release
    that is not present in the ``releases`` list, gets the rank
    ``len(releases)``, which places it after every listed release. An
    unknown release is reported to ``stderr_file`` but is not an error.
    """
    position = {release.name: index
                for index, release in enumerate(releases)}
    after_last = len(releases)
    rank: dict[str, int] = {}
    for item in backlog:
        if item.release is None:
            rank[item.key] = after_last
        elif item.release in position:
            rank[item.key] = position[item.release]
        else:
            _report_unknown_release(item, stderr_file)
            rank[item.key] = after_last
    return rank


def _finish_prereqs(backlog: Backlog) -> dict[str, set[str]]:
    """Return each key mapped to the keys that must be delivered first.

    A key ``X`` must be delivered (finished) before a key ``Y`` when
    ``Y`` names ``X`` in ``depends_on_f2s`` or ``depends_on_f2f``, or
    when ``X`` is a child of ``Y`` (a parent is delivered only once all
    its children are delivered). A ``depends_on_s2s`` reference only
    constrains the start of an item, not its delivery, and so does not
    order the items here. A reference to a key that is not present in the
    backlog is ignored, so a partly broken backlog still gets ordered.
    """
    present = {item.key for item in backlog}
    prereqs: dict[str, set[str]] = {item.key: set() for item in backlog}
    for item in backlog:
        for dep in item.depends_on_f2s + item.depends_on_f2f:
            if dep in present:
                prereqs[item.key].add(dep)
        if item.parent_key is not None and item.parent_key in present:
            prereqs[item.parent_key].add(item.key)
    return prereqs


def _with_leftovers(order: list[str], backlog: Backlog, rank: dict[str, int],
                    position: dict[str, int]) -> list[str]:
    """Append any keys a dependency cycle left out, in release order.

    A consistent backlog has no dependency cycle, so every key is already
    in ``order`` and nothing is appended. A cyclic backlog would leave
    some keys without a satisfiable order; those keys are added at the end
    in release order so that no backlog item is ever lost.
    """
    emitted = set(order)
    rest = [item.key for item in backlog if item.key not in emitted]
    rest.sort(key=lambda key: (rank[key], position[key]))
    return order + rest


def _ordered_keys(backlog: Backlog, rank: dict[str, int]) -> list[str]:
    """Return all keys in release order honoring the finish prerequisites.

    The keys are emitted in release order (the release rank, then the
    original backlog position), but a key is never emitted before the
    keys that must be delivered before it, as given by
    :func:`_finish_prereqs`. A prerequisite is therefore pulled in as
    early as the release order allows once it becomes the next deliverable
    item, which may place it earlier, or its dependents later, than the
    release order alone would.
    """
    prereqs = _finish_prereqs(backlog)
    position = {item.key: index for index, item in enumerate(backlog)}
    dependents: dict[str, list[str]] = {}
    for key, deps in prereqs.items():
        for dep in deps:
            dependents.setdefault(dep, []).append(key)
    pending = {key: len(deps) for key, deps in prereqs.items()}

    def entry(key: str) -> tuple[int, int, str]:
        """Return the heap entry that ranks one ready key."""
        return (rank[key], position[key], key)
    ready = [entry(key) for key in pending if pending[key] == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        key = heapq.heappop(ready)[2]
        order.append(key)
        for dependent in dependents.get(key, []):
            pending[dependent] -= 1
            if pending[dependent] == 0:
                heapq.heappush(ready, entry(dependent))
    return _with_leftovers(order, backlog, rank, position)


def backlog_in_release_order(backlog: Backlog, releases: Releases,
                             honor_dependencies: bool = False,
                             stderr_file: TextIO = sys.stderr) -> Backlog:
    """Return the backlog items ordered to follow the release order.

    A new backlog is returned and the ``backlog`` argument is never
    modified, not even when it is already in release order.

    The release order is taken as is from the ``releases`` list: items
    are grouped by release in the order the releases appear in that list.
    This function does not sort the releases by date; order the releases
    first (for example with
    :func:`backlogops.releases.order_releases_by_date`) when a date order
    is wanted. Items that share a release keep their original relative
    order from ``backlog``. An item with no release, or with a release
    that is not in the ``releases`` list, is placed after the items of the
    last listed release, again keeping its original relative order. A
    release named by an item but missing from ``releases`` is reported to
    ``stderr_file`` but does not raise.

    When ``honor_dependencies`` is False (the default) this grouping by
    release is the whole result.

    When ``honor_dependencies`` is True the result is still led by the
    release order, but no item is placed before an item that must be
    delivered before it. An item ``X`` must be delivered before an item
    ``Y`` when ``Y`` names ``X`` in ``depends_on_f2s`` or
    ``depends_on_f2f``, or when ``X`` is a child of ``Y`` (so a child is
    always placed before its parent). A ``depends_on_s2s`` reference does
    not affect the order, because it constrains only the start of an item,
    not its delivery. Where a dependency and the release order disagree
    the dependency wins, so a prerequisite may end up earlier, or a
    dependent later, than the release order alone would place it. The
    result is always a valid delivery order. References to keys that are
    not in the backlog are ignored.

    Calling :func:`check_backlog_consistency` before calling this function
    is recommended.

    Args:
        backlog: The backlog to order. This argument is not modified.
        releases: The releases to use for ordering. Their order in this
            list defines the release order; the list is not modified.
        honor_dependencies: If True, never place an item before an item
            that must be delivered before it, as described above. Default
            is False.
        stderr_file: The file to report a missing release reference to.

    Returns:
        A new backlog with the items ordered as described above.
    """
    rank = _release_rank(backlog, releases, stderr_file)
    if not honor_dependencies:
        return sorted(backlog, key=lambda item: rank[item.key])
    by_key = {item.key: item for item in backlog}
    return [by_key[key] for key in _ordered_keys(backlog, rank)]
