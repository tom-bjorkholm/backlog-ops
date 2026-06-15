#! /usr/local/bin/python3
"""Backlog and and its related releases."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass
from typing import Optional, TextIO, Sequence
import sys
from backlogops.backlog import Backlog, check_backlog_consistency
from backlogops.backlog_helpers import report_unknown_reference
from backlogops.releases import Release, Releases, check_releases
from backlogops.move_keys_first import move_keys_first
from backlogops.order_by_dependencies import order_by_dependencies, \
    DependencyMode


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
                              = None, stderr_file: TextIO = sys.stderr) \
            -> Backlog:
        """Order a backlog by dependencies.

        The backlog is ordered so that the team(s) can work on the items in the
        backlog order without violating dependencies. This is achieved by
        moving items with dependencies to a position after/later than the item
        it depends on, or to a position before/earlier than the item it
        depends on.
        Items without dependencies are not normally moved, but can be moved
        between items that depend on each other, if one of the items is named
        by space_around or mode is EVEN.

        Args:
            backlog: The backlog to order. The argument is not modified.
            later: If True an item that depends on another item is moved
                   after/later than the item it depends on.
                   If False an item that depends on another item is moved
                   before/earlier than the item it depends on.
            mode: Mode to determine backlog position of items with
                  dependencies, in relation to items without dependencies.
                  The default is KEEP.
            space_around: Key(s) of items in the backlog that should have as
                    much space between them and the items they depend on or
                    items that depend on them as possible.
                    This means that as many other backlog items as possible
                    are placed between them and the items they depend on,
                    and between them and items that depend on them.
                    This is useful when there is a big risk of delays in
                    a chain of dependencies.
                    Notice that this only works for one or very few items.
                    If None, no items receive this extra care.
            stderr_file: The file to report errors to.

        Raises:
            KeyError:   If a key in space_around is not found in the backlog.
            RuntimeError: If the number of items in space_around is more than
                          5 (more than 10% of the total number of items in the
                          backlog if there are less than 50 items in the
                          backlog).
            TypeError: If the space_around is not a string or a sequence of
                       strings.

        """
        self.backlog = order_by_dependencies(self.backlog, later=later,
                                             mode=mode,
                                             space_around=space_around,
                                             stderr_file=stderr_file)
