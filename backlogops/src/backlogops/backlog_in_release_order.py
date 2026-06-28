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


def _dependents_map(prereqs: dict[str, set[str]]) -> dict[str, set[str]]:
    """Return each key mapped to the keys that depend on it.

    This inverts the prerequisite relation from :func:`_finish_prereqs`:
    a key ``P`` maps to every key that names ``P`` as a prerequisite.
    Every key is present, mapped to an empty set when nothing depends on
    it.
    """
    dependents: dict[str, set[str]] = {key: set() for key in prereqs}
    for key, deps in prereqs.items():
        for dep in deps:
            dependents[dep].add(key)
    return dependents


def _adjusted_rank(rank: dict[str, int], prereqs: dict[str, set[str]],
                   dependents: dict[str, set[str]],
                   later: bool) -> dict[str, int]:
    """Return the release rank adjusted for the chosen direction.

    When ``later`` is True the rank of a dependent is raised to the
    latest rank among its prerequisites, so a dependent is never ordered
    before a prerequisite's release; the dependent moves later. When
    ``later`` is False the rank of a prerequisite is lowered to the
    earliest rank among its dependents, so a prerequisite is ready in
    time for its earliest dependent; the prerequisite moves earlier. The
    adjustment flows along the dependency edges, so it reaches a whole
    chain. Keys left out by a dependency cycle keep their own rank.
    """
    upstream = prereqs if later else dependents
    downstream = dependents if later else prereqs
    combine = max if later else min
    adjusted = dict(rank)
    waiting = {key: len(upstream[key]) for key in rank}
    ready = [key for key, count in waiting.items() if count == 0]
    while ready:
        key = ready.pop()
        for following in downstream[key]:
            adjusted[following] = combine(adjusted[following], adjusted[key])
            waiting[following] -= 1
            if waiting[following] == 0:
                ready.append(following)
    return adjusted


def _ordered_keys(backlog: Backlog, rank: dict[str, int],
                  later: bool) -> list[str]:
    """Return all keys in release order honoring the finish prerequisites.

    Each key is first given an effective release rank by
    :func:`_adjusted_rank`, which moves either a prerequisite earlier or
    a dependent later depending on ``later``. The keys are then emitted
    in that effective release order (the effective rank, then the
    original backlog position), but a key is never emitted before the
    keys that must be delivered before it, as given by
    :func:`_finish_prereqs`. The effective rank makes the two directions
    fall out of the same emission loop.
    """
    prereqs = _finish_prereqs(backlog)
    dependents = _dependents_map(prereqs)
    eff = _adjusted_rank(rank, prereqs, dependents, later)
    position = {item.key: index for index, item in enumerate(backlog)}
    pending = {key: len(deps) for key, deps in prereqs.items()}

    def entry(key: str) -> tuple[int, int, str]:
        """Return the heap entry that ranks one ready key."""
        return (eff[key], position[key], key)
    ready = [entry(key) for key in pending if pending[key] == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        key = heapq.heappop(ready)[2]
        order.append(key)
        for dependent in dependents[key]:
            pending[dependent] -= 1
            if pending[dependent] == 0:
                heapq.heappush(ready, entry(dependent))
    return _with_leftovers(order, backlog, eff, position)


def backlog_in_release_order(backlog: Backlog, releases: Releases, *,
                             honor_dependencies: bool = False,
                             later: bool = False,
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
    release is the whole result, and ``later`` has no effect.

    When ``honor_dependencies`` is True the result is still led by the
    release order, but no item is placed before an item that must be
    delivered before it. An item ``X`` must be delivered before an item
    ``Y`` when ``Y`` names ``X`` in ``depends_on_f2s`` or
    ``depends_on_f2f``, or when ``X`` is a child of ``Y`` (so a child is
    always placed before its parent). A ``depends_on_s2s`` reference does
    not affect the order, because it constrains only the start of an item,
    not its delivery. The result is always a valid delivery order, and
    references to keys that are not in the backlog are ignored.

    A dependency can disagree with the release order: a prerequisite may
    be planned for a *later* release than the item that depends on it.
    The ``later`` argument chooses how to resolve such a conflict, and it
    matters only when ``honor_dependencies`` is True:

    - ``later`` False (the default) moves the *prerequisite earlier*. The
      item that depends on it keeps its release, and the prerequisite is
      delivered ahead of its own release so that it is ready in time. The
      dependent's release wins and pulls its prerequisites forward. This
      is useful when the planned release of the dependent must hold.

    - ``later`` True moves the *dependent later*. The prerequisite keeps
      its release, and the item that depends on it is delivered after the
      prerequisite, behind its own release. The prerequisite's release
      wins and pushes its dependents back. This is useful when the
      planned release of the prerequisite must hold.

    Worked example. Item ``builder`` is planned for the first release but
    depends on item ``engine`` planned for the second release, so
    ``engine`` must be delivered before ``builder``. With ``later`` False
    the result keeps ``builder`` in the first release and pulls ``engine``
    in ahead of it, delivering ``engine`` early. With ``later`` True the
    result keeps ``engine`` in the second release and pushes ``builder``
    out to be delivered after it. Either way ``engine`` ends up before
    ``builder`` and the order stays a valid delivery order.

    The ``later`` argument has the same meaning here as in
    :func:`backlogops.order_by_dependencies`.

    Calling :func:`check_backlog_consistency` before calling this function
    is recommended.

    Args:
        backlog: The backlog to order. This argument is not modified.
        releases: The releases to use for ordering. Their order in this
            list defines the release order; the list is not modified.
        honor_dependencies: If True, never place an item before an item
            that must be delivered before it, as described above. Default
            is False.
        later: Chooses how a dependency that disagrees with the release
            order is resolved when ``honor_dependencies`` is True. If
            False (the default) the prerequisite is pulled to an earlier
            release and the dependent keeps its release. If True the
            dependent is pushed to a later release and the prerequisite
            keeps its release. Has no effect when ``honor_dependencies``
            is False. Default is False.
        stderr_file: The file to report a missing release reference to.

    Returns:
        A new backlog with the items ordered as described above.
    """
    rank = _release_rank(backlog, releases, stderr_file)
    if not honor_dependencies:
        return sorted(backlog, key=lambda item: rank[item.key])
    by_key = {item.key: item for item in backlog}
    return [by_key[key] for key in _ordered_keys(backlog, rank, later)]
