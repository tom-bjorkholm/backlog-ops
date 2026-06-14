#! /usr/local/bin/python3
"""Releases related to a backlog."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass
from datetime import date
from typing import Optional, TextIO
import sys


@dataclass
class Release:
    """A release of some BacklogItems.

    Fields:
        name: The name of the release. Required. Must be unique.
              Must not be empty, must not contain whitespace and must
              not contain any of the characters , . ; : ( ) [ ] { }.
        planned_date: The planned date of the release. Optional.
                      The date that is communicated to the customer.
        estimated_date: The estimated date of the release. Optional.
                        The date that the content of the release is
                        estimated to be ready.
    """

    name: str
    planned_date: Optional[date] = None
    estimated_date: Optional[date] = None

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the internal consistency of the release.

        The documented constraints are checked on all member variables.
        Field types are verified.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If a field value violates a constraint.
        """
        # to be implemented


type Releases = list[Release]
"""A list of releases related to a Backlog."""


def check_releases(releases: Releases,
                   stderr_file: TextIO = sys.stderr) -> None:
    """Check the internal consistency of a list of releases.

    The documented constraints are checked on all releases.
    Field types are verified.
    The releases are checked to be unique by name.

    Args:
        releases: The list of releases to check.
        stderr_file: The file to report errors to.
    """
    for release in releases:
        release.check_consistency(stderr_file)
    # rest to be implemented
