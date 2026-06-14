#! /usr/local/bin/python3
"""Releases related to a backlog."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass, fields
from datetime import date
from typing import NoReturn, Optional, TextIO
import sys
from backlogops.backlog_helpers import build_item_kwargs, check_field_types
from backlogops.backlog_helpers import check_key_syntax, construct
from backlogops.backlog_helpers import field_type_hints, report_bad_value


@dataclass
class Release:
    """A release of some BacklogItems.

    A release groups backlog items that are delivered together. A
    backlog item refers to its release by name through its ``release``
    field, so the release name must follow the same syntax rules as a
    backlog item key.

    Fields:
        name: The name of the release. Required. Must be unique among
              the releases. Must not be empty, must not contain
              whitespace and must not contain any of the characters
              , . ; : ( ) [ ] { }.
        planned_date: The planned date of the release. Optional.
                      The date that is communicated to the customer.
        estimated_date: The estimated date of the release. Optional.
                        The date that the content of the release is
                        estimated to be ready. The estimated date and
                        the planned date are independent of each other;
                        no ordering between them is required.
    """

    name: str
    planned_date: Optional[date] = None
    estimated_date: Optional[date] = None

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the internal consistency of the release.

        The field types are verified and the name is checked to be a
        well formed key (a non-empty string with no whitespace and none
        of the forbidden separator characters). Uniqueness of the name
        among several releases is not checked here; that is done by
        :func:`check_releases`.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If the name violates the key syntax constraint.
        """
        check_field_types(self, stderr_file, subject='Release')
        check_key_syntax('name', self.name, stderr_file, subject='Release')


type Releases = list[Release]
"""A list of releases related to a Backlog."""


def report_unknown_keys(unknown: set[str],
                        stderr_file: TextIO = sys.stderr) -> NoReturn:
    """Report unknown release input keys and raise ``KeyError``.

    Args:
        unknown: The input keys that match no field of :class:`Release`.
        stderr_file: The file to report the error to.

    Raises:
        KeyError: Always, after reporting the message.
    """
    names = ', '.join(sorted(unknown))
    message = f'Release has unknown field(s): {names}'
    print(message, file=stderr_file)
    raise KeyError(message)


def get_release(data: dict[str, object], stderr_file: TextIO = sys.stderr,
                strict: bool = True) -> Release:
    """Get a release from a dictionary.

    The dictionary is expected to hold the mandatory ``name`` field and
    may hold the optional ``planned_date`` and ``estimated_date``
    fields. Date fields given as ISO 8601 strings (such as
    ``'2026-06-12'``) are converted to ``date`` objects.

    Args:
        data: The dictionary to get the release from.
        stderr_file: The file to report errors to.
        strict: When True (the default), any input key that matches no
                field of :class:`Release` is an error. When False such
                keys are silently ignored.

    Returns:
        The release.

    Raises:
        KeyError: If the mandatory ``name`` field is missing, or if
            ``strict`` is True and the data has a key that is not a
            release field.
        TypeError: If a field has a type that cannot be converted.
    """
    field_types = field_type_hints(Release)
    if strict:
        unknown = set(data) - set(field_types)
        if unknown:
            report_unknown_keys(unknown, stderr_file)
    item_kwargs = build_item_kwargs(fields(Release), field_types, data,
                                    stderr_file)
    return construct(Release, item_kwargs)


def get_releases(datalist: list[dict[str, object]],
                 stderr_file: TextIO = sys.stderr,
                 strict: bool = True) -> Releases:
    """Get a list of releases from a list of dictionaries.

    Each dictionary is converted to a release as documented for
    :func:`get_release`, with the same ``strict`` handling of keys that
    do not match a release field.

    Args:
        datalist: The list of dictionaries to get the releases from.
        stderr_file: The file to report errors to.
        strict: Passed to :func:`get_release` for each dictionary. When
                True (the default), unknown keys are an error; when
                False they are ignored.

    Returns:
        The list of releases.

    Raises:
        KeyError: If a mandatory ``name`` field is missing, or if
            ``strict`` is True and a dictionary has a key that is not a
            release field.
        TypeError: If a field has a type that cannot be converted.
    """
    return [get_release(data, stderr_file, strict) for data in datalist]


def check_releases(releases: Releases,
                   stderr_file: TextIO = sys.stderr) -> None:
    """Check the internal consistency of a list of releases.

    Every release is checked for internal consistency as documented for
    :meth:`Release.check_consistency`, and the release names are checked
    to be unique.

    Args:
        releases: The list of releases to check.
        stderr_file: The file to report errors to.

    Raises:
        TypeError: If a field has the wrong type.
        ValueError: If a name violates the key syntax constraint, or if
            two releases share the same name.
    """
    seen: set[str] = set()
    for release in releases:
        release.check_consistency(stderr_file)
        if release.name in seen:
            report_bad_value('name', release.name, 'duplicate release name',
                             stderr_file, subject='Release')
        seen.add(release.name)
