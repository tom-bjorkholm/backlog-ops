#! /usr/local/bin/python3
"""Interaction between releases and backlogs."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass, replace
from datetime import date, timedelta
from typing import NamedTuple, Optional
from backlogops.backlog import Backlog, BacklogItem
from backlogops.releases import Releases


@dataclass
class ReleaseChange:
    """A change of the release a backlog item is delivered in.

    Both releases are optional, because a backlog item may carry no
    release before the change and may end up with no release after it.
    """

    backlog_key: str
    old_release: Optional[str]
    new_release: Optional[str]


type ReleaseChanges = list[ReleaseChange]
"""Changes of releases for a backlog items."""


class BacklogReleaseChange(NamedTuple):
    """A change of a backlog with changes to releases."""

    backlog: Backlog
    release_changes: ReleaseChanges


@dataclass
class ReleaseDateChange:
    """A change of a release date.

    Both dates are optional, because a release may have had no date
    before the change and may have no date after it.
    """

    release: str
    old_date: Optional[date]
    new_date: Optional[date]


type ReleaseDateChanges = list[ReleaseDateChange]
"""Changes of release dates for a release."""


class ReleasesAndDateChanges(NamedTuple):
    """Releases and their date changes."""

    releases: Releases
    date_changes: ReleaseDateChanges


def _check_buffer(buffer: timedelta) -> None:
    """Raise ``ValueError`` when the buffer is negative.

    A buffer is a slack added to a date, so a negative buffer would mean
    negative slack and is rejected.
    """
    if buffer < timedelta(0):
        raise ValueError('buffer must not be negative')


def _latest_per_release(backlog: Backlog) -> dict[str, date]:
    """Return the latest estimated ready date assigned to each release.

    A backlog item adds to the result only when it names a release and
    carries an estimated ready date. A release named by no such item is
    absent from the result.
    """
    latest: dict[str, date] = {}
    for item in backlog:
        ready = item.estimated_ready_date
        if item.release is None or ready is None:
            continue
        current = latest.get(item.release)
        if current is None or ready > current:
            latest[item.release] = ready
    return latest


def estimate_release_dates(releases: Releases, backlog: Backlog) \
        -> ReleasesAndDateChanges:
    """Find estimated release dates from backlog item estimates.

    For each release, the estimated date is set to the latest estimated
    ready date of the backlog items assigned to the release. A release
    with no assigned item that carries an estimated ready date gets no
    estimated date (``None``). A change is recorded only for a release
    whose estimated date actually changes.

    Args:
        releases: The releases to find the estimated dates for.
                  The argument is not modified.
        backlog: The already estimated backlog to find the estimated dates
                 from. The argument is not modified.

    Returns:
        The releases with updated estimated dates and a record of how
        the estimated release dates were changed.
    """
    latest = _latest_per_release(backlog)
    new_releases: Releases = []
    changes: ReleaseDateChanges = []
    for release in releases:
        new_date = latest.get(release.name)
        if new_date != release.estimated_date:
            changes.append(ReleaseDateChange(release.name,
                                             release.estimated_date, new_date))
        new_releases.append(replace(release, estimated_date=new_date))
    return ReleasesAndDateChanges(new_releases, changes)


def release_plan_on_estimate(releases: Releases, buffer: timedelta) \
        -> ReleasesAndDateChanges:
    """Set the planned release dates from the estimated release dates.

    For each release the planned date is set to the estimated date plus
    the buffer. A release with no estimated date gets no planned date
    (``None``), as there is nothing to base the plan on. A change is
    recorded only for a release whose planned date actually changes.

    Args:
        releases: The releases to set the planned release dates for.
                  The argument is not modified.
        buffer: The buffer or slack to add to the estimated release dates
                to get the planned release dates. Must not be negative.

    Returns:
        The releases with updated planned release dates and a record of
        how the planned release dates were changed.

    Raises:
        ValueError: If the buffer is negative.
    """
    _check_buffer(buffer)
    new_releases: Releases = []
    changes: ReleaseDateChanges = []
    for release in releases:
        estimated = release.estimated_date
        new_date = None if estimated is None else estimated + buffer
        if new_date != release.planned_date:
            changes.append(ReleaseDateChange(release.name,
                                             release.planned_date, new_date))
        new_releases.append(replace(release, planned_date=new_date))
    return ReleasesAndDateChanges(new_releases, changes)


def _dated_releases(releases: Releases) -> list[tuple[date, int, str]]:
    """Return the planned releases as ``(date, order, name)``, sorted.

    Only releases that carry a planned date take part, because a release
    with no planned date offers no deadline to fit an item into. The
    order index keeps the sort stable for releases that share a date.
    """
    dated = [(release.planned_date, index, release.name)
             for index, release in enumerate(releases)
             if release.planned_date is not None]
    return sorted(dated)


def _fitting_release(dated: list[tuple[date, int, str]],
                     fit_date: date) -> Optional[str]:
    """Return the earliest planned release that the fit date reaches.

    The earliest release whose planned date is on or after ``fit_date``
    is returned, or ``None`` when no planned release is late enough.
    """
    for planned, _order, name in dated:
        if planned >= fit_date:
            return name
    return None


def _new_release_for(item: BacklogItem, dated: list[tuple[date, int, str]],
                     buffer: timedelta) -> Optional[str]:
    """Return the release the item belongs in for its current estimate.

    An item with no estimated ready date keeps its current release, as
    there is no basis to place it. Otherwise the item is placed in the
    earliest planned release that its estimated ready date plus the buffer
    reaches, regardless of its current release, so an item with no release
    yet is assigned to the release it is ready in time for. The item is
    placed in no release when no planned release is late enough.
    """
    if item.estimated_ready_date is None:
        return item.release
    return _fitting_release(dated, item.estimated_ready_date + buffer)


def adjust_release_content(releases: Releases, backlog: Backlog,
                           buffer: timedelta) -> BacklogReleaseChange:
    """Adjust the release content to fit the planned release dates.

    Each backlog item that carries an estimated ready date is placed in
    the earliest release whose planned date is on or after the item's
    estimated ready date plus the buffer. This pushes an item to a later
    release when it no longer fits its current one, pulls it to an earlier
    release when it now fits sooner, and assigns an item that has no
    release yet to the release it is ready in time for. An item that no
    planned release is late enough for is left out of every release (its
    release becomes ``None``). An item with no estimated ready date keeps
    its current release, as there is no basis to place it. A change is
    recorded only for an item whose release actually changes.

    Args:
        releases: The releases to fit the items into. The argument is not
                  modified.
        backlog: The already estimated backlog to adjust. The argument is
                 not modified.
        buffer: The buffer or slack added to the estimated ready dates to
                gain confidence that an item fits a release. Must not be
                negative.

    Returns:
        The backlog with updated release content and a record of how the
        release content was changed.

    Raises:
        ValueError: If the buffer is negative.
    """
    _check_buffer(buffer)
    dated = _dated_releases(releases)
    new_backlog: Backlog = []
    changes: ReleaseChanges = []
    for item in backlog:
        new_release = _new_release_for(item, dated, buffer)
        if new_release != item.release:
            changes.append(ReleaseChange(item.key, item.release, new_release))
        new_backlog.append(replace(item, release=new_release))
    return BacklogReleaseChange(new_backlog, changes)
