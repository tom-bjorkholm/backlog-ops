#! /usr/local/bin/python3
"""Backlog and and its related releases."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, TextIO, Sequence
import sys
from backlogops.backlog import Backlog, check_backlog_consistency
from backlogops.backlog_helpers import report_unknown_reference
from backlogops.releases import Release, Releases, check_releases
from backlogops.move_keys_first import move_keys_first
from backlogops.order_by_dependencies import order_by_dependencies, \
    DependencyMode
from backlogops.estimate_ready_date import estimate_ready_date, \
    set_plan_from_estimate
from backlogops.available_teams import AvailableTeams
from backlogops.release_backlog_updates import estimate_release_dates, \
    release_plan_on_estimate, adjust_release_content, ReleaseChanges, \
    ReleaseDateChanges


@dataclass
class BacklogReleases:
    """A backlog and its related releases.

    The releases list describes the releases that the backlog items are
    delivered in. A backlog item refers to its release by name through
    its ``release`` field. The releases list may hold releases that no
    backlog item refers to yet, but every release named by a backlog
    item is expected to be present in the releases list.

    Fields:
        backlog: The backlog of items.
        releases: The releases the backlog items are delivered in.
    """

    backlog: Backlog
    releases: Releases

    @staticmethod
    def add_to_releases(backlog: Backlog, releases: Releases) -> Releases:
        """Add all releases mentioned in the backlog to the releases list.

        For each backlog item that names a release, a release with that
        name is added to the releases list when no release of that name
        is present yet. A release added this way has no planned or
        estimated date, because a backlog item only carries the release
        name. The order of the existing releases is kept and any new
        releases are appended in the order they are first met in the
        backlog.

        Args:
            backlog: The backlog to take the release names from.
            releases: The releases to add the missing releases to.
                      The argument is not modified.

        Returns:
            The releases list with the added releases. If all releases
            named by the backlog are already present, the argument
            object is returned unchanged. If any new releases are added,
            a new list is returned.
        """
        known = {release.name for release in releases}
        added: Releases = []
        for item in backlog:
            if item.release is not None and item.release not in known:
                known.add(item.release)
                added.append(Release(name=item.release))
        return releases + added if added else releases

    @staticmethod
    def check_in_releases(backlog: Backlog, releases: Releases,
                          stderr_file: TextIO = sys.stderr) -> None:
        """Check that all releases in the backlog are in the releases list.

        For each backlog item that names a release, the release is
        checked to be present by name in the releases list.

        Args:
            backlog: The backlog to check.
            releases: The releases to check the backlog against.
            stderr_file: The file to report errors to.

        Raises:
            KeyError: If a release named by the backlog is not present in
                the releases list.
        """
        known = {release.name for release in releases}
        for item in backlog:
            if item.release is not None and item.release not in known:
                report_unknown_reference('release', item.key, item.release,
                                         stderr_file)

    def update_releases(self) -> None:
        """Update the releases list to include all releases in the backlog.

        For each backlog item that names a release, the release is added
        to the releases list when it is not already present, as
        documented for :meth:`add_to_releases`.
        """
        self.releases = self.add_to_releases(self.backlog, self.releases)

    def check_release_xref(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check that all releases in the backlog are in the releases list.

        This is the cross reference check documented for
        :meth:`check_in_releases`, applied to the member backlog and
        releases.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            KeyError: If a release named by the backlog is not present in
                the releases list.
        """
        self.check_in_releases(self.backlog, self.releases, stderr_file)

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the internal consistency of the backlog and releases.

        The backlog is checked for full consistency as documented for
        :func:`check_backlog_consistency`, the releases are checked for
        internal consistency and unique names as documented for
        :func:`check_releases`, and every release named by the backlog
        is checked to be present in the releases list.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If a field value violates a constraint, or if
                release names are not unique.
            KeyError: If a key reference is invalid, or if a release
                named by the backlog is not in the releases list.
        """
        check_backlog_consistency(self.backlog, stderr_file)
        check_releases(self.releases, stderr_file)
        self.check_in_releases(self.backlog, self.releases, stderr_file)

    def move_keys_first(self, keys: Sequence[str],
                        stderr_file: TextIO = sys.stderr) -> None:
        """Move the items named by ``keys`` to the front of the backlog.

        The named items lead the backlog in the order of ``keys``. Each
        named item is preceded by its descendants in post order: a child
        comes right before its own parent, and that parent right before
        the grandparent, up to the named item. Siblings keep their
        original backlog order. A named descendant is placed by its own
        key instead, so it may end up after its named parent. A descendant
        is pulled to the front only when it appears after its named
        ancestor in the backlog, so that no item is moved to a later
        position because of an ancestor's key. The remaining items keep
        their original order after the front block. The behavior is the
        one documented for :func:`backlogops.move_keys_first`.

        Args:
            keys: The keys to move to the front, in the wanted order. The
                keys must be unique and must exist in the backlog.
            stderr_file: The file to report errors to.

        Raises:
            KeyError: If a key is not found in the backlog.
            ValueError: If a key is not unique.
        """
        self.backlog = move_keys_first(self.backlog, keys, stderr_file)

    def order_by_dependencies(self, *, later: bool = False,
                              mode: DependencyMode = DependencyMode.KEEP,
                              space_around: Optional[str | Sequence[str]]
                              = None,
                              stderr_file: TextIO = sys.stderr) -> None:
        """Order the member backlog by dependencies.

        The member backlog is replaced by a backlog ordered so that a
        team can start the items in backlog order without starting an
        item before the items it depends on. The behavior is the one
        documented for :func:`backlogops.order_by_dependencies`.

        Args:
            later: How a dependency that is not yet satisfied is resolved.
                If False (the default) the prerequisite item is pulled to
                a position just before the dependent item. If True the
                dependent item is pushed to a position just after its
                prerequisites.
            mode: How items that take part in a dependency are placed in
                relation to items that take part in no dependency, as
                documented for :class:`DependencyMode`. The default is
                KEEP.
            space_around: Key or keys of items that should have as many
                other items as possible placed between them and the items
                they depend on, and between them and the items that
                depend on them. It only works well for one or very few
                items. None means no item is treated this way.
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If space_around is neither None, a string, nor a
                sequence of strings.
            KeyError: If a space_around key is not found in the backlog.
            RuntimeError: If space_around names more keys than allowed:
                more than five, or more than ten percent of a backlog of
                fewer than fifty items.
        """
        self.backlog = order_by_dependencies(self.backlog, later=later,
                                             mode=mode,
                                             space_around=space_around,
                                             stderr_file=stderr_file)

    def estimate_ready_date(self, available_teams: AvailableTeams,
                            start_date: Optional[date] = None,
                            stderr_file: TextIO = sys.stderr) \
            -> ReleaseDateChanges:
        """Estimate the ready date of the member backlog items.

        The member backlog is replaced by a backlog whose items carry the
        estimated ready date. The teams start working on the start date,
        which defaults to today when None is given. The behavior is the
        one documented for :func:`backlogops.estimate_ready_date`.

        Args:
            available_teams: The available teams used to estimate the
                         ready date, including absence, velocity and work
                         hours.
            start_date: The day the teams start working, or None for today.
            stderr_file: The file to report warnings to.
        """
        self.backlog = estimate_ready_date(self.backlog, available_teams,
                                           start_date, stderr_file)
        self.releases, changes = estimate_release_dates(self.releases,
                                                        self.backlog)
        return changes

    def set_plan_from_estimate(self, stderr_file: TextIO = sys.stderr) -> None:
        """Set the planned ready dates from the estimated ready dates.

        The member backlog is replaced by a backlog whose items carry the
        planned ready date taken from the estimated ready date, as
        documented for :func:`backlogops.set_plan_from_estimate`.

        Args:
            stderr_file: The file to report errors to.
        """
        self.backlog = set_plan_from_estimate(self.backlog, stderr_file)

    def adjust_release_content(self, buffer: timedelta,
                               stderr_file: TextIO = sys.stderr) \
            -> ReleaseChanges:
        """Adjust the release content to fit the planned release dates.

        The member backlog is replaced by a backlog whose items carry the
        adjusted release content. The behavior is the one documented for
        :func:`backlogops.adjust_release_content`.

        Args:
            buffer: The buffer or slack to add to the estimated ready dates
                    to get the planned release dates.
            stderr_file: The file to report errors to.

        Returns:
            A record of how the release content was changed.
        """
        _ = stderr_file
        self.backlog, changes = adjust_release_content(self.releases,
                                                       self.backlog, buffer)
        return changes

    def release_plan_on_estimate(self, buffer: timedelta,
                                 stderr_file: TextIO = sys.stderr) \
            -> ReleaseDateChanges:
        """Set the planned release dates from the estimated release dates.

        The member releases is replaced by releases whose items carry the
        planned release dates taken from the estimated release dates, as
        documented for :func:`backlogops.release_plan_on_estimate`.

        Args:
            buffer: The buffer or slack to add to the estimated release dates
                    to get the planned release dates.
            stderr_file: The file to report errors to.

        Returns:
            A record of how the release dates were changed.
        """
        _ = stderr_file
        self.releases, changes = release_plan_on_estimate(self.releases,
                                                          buffer)
        return changes
