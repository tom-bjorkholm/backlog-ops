#! /usr/local/bin/python3
"""Match the Jira status of a written issue to the internal status.

Jira does not let a status be set as an ordinary field: it is reached by
a workflow transition. :func:`_status_from_name` maps a Jira status name
to an internal :class:`~backlogops.backlog.Status`, preferring a
configured status map and falling back to the built-in name matching, and
:func:`_jira_status_name` reads the name an issue currently has through
the column map. :func:`_try_transitions` then applies the first workflow
transition whose target maps to the wanted status, and
:class:`StatusMismatch` records an issue that no transition could move.

Nothing here writes fields or links, so both the module that adds issues
and the module that updates them can share these helpers without
depending on each other in a cycle. The write context is not used; the
caller passes the client, the column map and the status map it holds.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import NamedTuple, Optional, TextIO
from config_as_json import string_to_enum_best_match
from jira import JIRA, JIRAError
from backlogops.backlog import BacklogItem, Status
from backlogops.jira_io_config import JiraColumnMap
from backlogops.jira_read import _coerce, _resolve


class StatusMismatch(NamedTuple):
    """A created issue whose Jira status could not be matched.

    Fields:
        item: The stored copy of the item, carrying its new Jira key.
        expected: The internal status the item carries.
        actual: The Jira status name the created issue ended up in, or
            None when the status could not be read.
    """

    item: BacklogItem
    expected: Status
    actual: Optional[str]


def _status_from_name(name: str, status_map: Optional[dict[str, Status]]
                      ) -> Optional[Status]:
    """Return the internal status a Jira status name maps to, or None.

    A configured ``status_map`` is matched case-insensitively first, as
    when reading; otherwise the built-in status-name matching is used. A
    name that matches neither returns None.
    """
    if status_map:
        lookup = {key.lower(): value for key, value in status_map.items()}
        mapped = lookup.get(name.lower())
        if mapped is not None:
            return mapped
    try:
        result = string_to_enum_best_match(name, Status)
    except KeyError:
        return None
    assert isinstance(result, Status)
    return result


def _maps_to(name: Optional[str], target: Status,
             status_map: Optional[dict[str, Status]]) -> bool:
    """Return whether a Jira status name maps to the target status."""
    return name is not None and _status_from_name(name, status_map) is target


def _jira_status_name(column_map: JiraColumnMap, custom_ids: dict[str, str],
                      issue: object) -> Optional[str]:
    """Return the issue's Jira status name via the column map."""
    field_root = getattr(issue, 'fields', None)
    for attr in column_map.get('status', ()):
        value = _coerce(_resolve(issue, field_root, attr, custom_ids))
        if isinstance(value, str) and value:
            return value
    return None


def _transition_target(trans: dict[str, object]) -> Optional[str]:
    """Return the target status name of a workflow transition, or None."""
    to_field = trans.get('to')
    if isinstance(to_field, dict):
        name = to_field.get('name')
        if isinstance(name, str):
            return name
    return None


def _available_transitions(client: JIRA,
                           issue: object) -> list[dict[str, object]]:
    """Return the issue's available workflow transitions, or empty."""
    try:
        transitions = client.transitions(issue)
    except JIRAError:
        return []
    return transitions if isinstance(transitions, list) else []


def _matching_transitions(client: JIRA, target: Status, issue: object,
                          status_map: Optional[dict[str, Status]]
                          ) -> list[str]:
    """Return ids of transitions whose target maps to the target status."""
    result: list[str] = []
    for trans in _available_transitions(client, issue):
        trans_id = trans.get('id')
        if isinstance(trans_id, str) and _maps_to(_transition_target(trans),
                                                  target, status_map):
            result.append(trans_id)
    return result


def _try_transitions(client: JIRA, target: Status, issue: object,
                     status_map: Optional[dict[str, Status]]) -> bool:
    """Transition the issue to a matching status; True on the first success.

    A direct transition to the target status is assumed to reach it, so
    the first transition that Jira accepts is treated as a success.
    """
    for trans_id in _matching_transitions(client, target, issue, status_map):
        try:
            client.transition_issue(issue, trans_id)
            return True
        except JIRAError:
            continue
    return False


def _report_status_mismatch(bad: StatusMismatch, stderr_file: TextIO) -> None:
    """Warn that a written issue's status could not be matched."""
    print(f'WARNING: {bad.item.key} ({bad.item.title}) is {bad.actual!r} in '
          f'Jira, not a status matching {bad.expected.name}; transition it '
          'manually.', file=stderr_file)
