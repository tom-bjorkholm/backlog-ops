#! /usr/local/bin/python3
"""Backlog and and its related releases."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass
from typing import TextIO
import sys
from backlogops.backlog import Backlog
from backlogops.releases import Releases


@dataclass
class BacklogReleases:
    """A backlog and its related releases."""

    backlog: Backlog
    releases: Releases

    @staticmethod
    def add_to_releases(backlog: Backlog, releases: Releases) -> Releases:
        """Add all releases mentioned in the backlog to the releases list.

        For each BacklogItem with in the backlog that has a release,
        add the release to the releases list if it is not already there.

        Args:
            backlog: The backlog to add the releases to.
            releases: The releases to add the releases to.
                      The argument is not modified.

        Returns:
            The releases list with the added releases.
            If all releases are already in the list, the argument
            object is returned unchanged.
            If any new releases are added, a new list is returned.
        """
        # to be implemented
        return releases

    @staticmethod
    def check_in_releases(backlog: Backlog, releases: Releases,
                          stderr_file: TextIO = sys.stderr) -> None:
        """Check that all releases in the backlog are in the releases list.

        For each BacklogItem with in the backlog that has a release,
        check that the release is in the releases list.

        Args:
            backlog: The backlog to check.
            releases: The releases to check.
            stderr_file: The file to report errors to.

        Raises:
            KeyError: If a release mentioned in the backlog is not in
                      the releases list.
        """
        # to be implemented

    def update_releases(self) -> None:
        """Update the releases list to include all releases in the backlog.

        For each BacklogItem with in the backlog that has a release,
        add the release to the releases list if it is not already there.
        """
        self.releases = self.add_to_releases(self.backlog, self.releases)

    def check_release_xref(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check that all releases in the backlog are in the releases list.

        For each BacklogItem with in the backlog that has a release,
        check that the release is in the releases list.
        """
        self.check_in_releases(self.backlog, self.releases, stderr_file)

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the internal consistency of the backlog and releases.

        The documented constraints are checked on all member variables.
        Field types are verified. The releases are checked to be unique
        by name. The backlog is checked to have all releases mentioned
        in the backlog in the releases list.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If a field value violates a constraint.
            KeyError: If a release mentioned in the backlog is not in
                      the releases list.
        """
        # to be implemented
