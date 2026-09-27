#! /usr/local/bin/python3
"""Write a remaining time estimate to Jira.

Jira reports an issue's remaining estimate as raw seconds, through
``timetracking.remainingEstimateSeconds`` and the plain ``timeestimate``
field, but both are read-only: Jira silently ignores a write of them. It
accepts a remaining estimate only as a duration text in the
``remainingEstimate`` of the ``timetracking`` field, and it keeps the
estimate in whole minutes. A remaining time mapped to such a time tracking
path is therefore rounded up to whole minutes, so an estimate is never
lowered, and written as ``'<minutes>m'``. It is written through an
``edit`` operation of the issue update rather than as a plain field value,
because an edit leaves the issue's original estimate as it is. Jira still
sets the original estimate from the first remaining estimate of an issue
that has none. A remaining time mapped to any other path, such as a
numeric custom field, is written as its whole number of seconds.

Because Jira acknowledges an ignored write as a success, the remaining
estimate is read back after it is written and a value Jira did not store
is reported as a refused field.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import math
from datetime import timedelta
from typing import Optional
from jira import JIRA, JIRAError
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType

TIME_TRACKING = 'timetracking'
"""The Jira field a remaining estimate is written to."""

_TIME_TRACKING_ROOTS = frozenset({TIME_TRACKING, 'timeestimate'})
"""First path steps that read the remaining estimate of time tracking."""

_EDIT_FIELDS = frozenset({TIME_TRACKING})
"""Jira fields set through an ``edit`` operation, not as a plain value."""

_REMAINING = 'remainingEstimate'
"""The time tracking key that takes the remaining estimate as text."""


def _is_time_tracking(attr: JiraAttrPath) -> bool:
    """Return whether a path reads the time tracking remaining estimate."""
    return attr.kind is JiraAttrType.FIELD and \
        attr.path[0] in _TIME_TRACKING_ROOTS


def _jira_value(attr: JiraAttrPath, value: object) -> object:
    """Return the value Jira stores when this value is written to a path.

    A remaining time becomes whole seconds, rounded up, and for a time
    tracking path rounded up to whole minutes, which is what Jira keeps.
    The result compares equal to the value read back from the same path,
    so an update can tell an estimate that is already correct. Any other
    value is returned unchanged.
    """
    if not isinstance(value, timedelta):
        return value
    seconds = math.ceil(value / timedelta(seconds=1))
    if _is_time_tracking(attr):
        return math.ceil(seconds / 60) * 60
    return seconds


def _time_payload(seconds: int) -> dict[str, object]:
    """Return the time tracking entry that sets a remaining estimate."""
    return {TIME_TRACKING: {_REMAINING: f'{seconds // 60}m'}}


def _split_edits(fields: dict[str, object]
                 ) -> tuple[dict[str, object], dict[str, object]]:
    """Split an update payload into plain fields and edit operations.

    A field of :data:`_EDIT_FIELDS` is sent as ``[{'edit': value}]`` in
    the update operations and every other field as a plain field value.
    """
    plain = {name: value for name, value in fields.items()
             if name not in _EDIT_FIELDS}
    edits: dict[str, object] = {name: [{'edit': value}]
                                for name, value in fields.items()
                                if name in _EDIT_FIELDS}
    return plain, edits


def _written_seconds(value: object) -> Optional[int]:
    """Return the seconds a time tracking entry writes, or None."""
    if not isinstance(value, dict):
        return None
    text = value.get(_REMAINING)
    if not isinstance(text, str) or not text.endswith('m'):
        return None
    return int(text[:-1]) * 60


def _stored_seconds(client: JIRA, key: str) -> object:
    """Return the remaining estimate seconds Jira holds for an issue."""
    issue = client.issue(key, fields=TIME_TRACKING)
    tracking = getattr(getattr(issue, 'fields', None), TIME_TRACKING, None)
    return getattr(tracking, 'remainingEstimateSeconds', None)


def _unstored_time(client: JIRA, key: str, written: dict[str, object],
                   refused: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Return the written remaining estimate Jira did not store, if any.

    Only a remaining estimate that was written and not already refused is
    read back. A read-back that differs, or that Jira refuses, is returned
    as the refused time tracking field with its reason.
    """
    expected = _written_seconds(written.get(TIME_TRACKING))
    if expected is None or TIME_TRACKING in {name for name, _ in refused}:
        return []
    try:
        stored = _stored_seconds(client, key)
    except JIRAError as error:
        return [(TIME_TRACKING, 'could not read the remaining estimate back: '
                 + str(error.text))]
    if stored == expected:
        return []
    return [(TIME_TRACKING, f'Jira did not store the remaining estimate '
             f'({expected} s written, {stored!r} s stored)')]
