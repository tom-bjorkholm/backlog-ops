#! /usr/local/bin/python3
"""Look up the raw Jira JSON of an issue's fields, to help map columns.

A backlog column map names a Jira attribute path such as
``timetracking.remainingEstimateSeconds``. :func:`jira_field_json` shows
what Jira really holds at such a path of one issue, as the JSON Jira
returned, together with the field's entry on the issue's edit screen,
which lists the operations Jira allows for writing it. A name is a field
id, optionally followed by dotted path steps into the field's JSON; a
step into a list is its index, as in ``fixVersions.0.name``. The first
step may also be a custom field display name, such as ``Story point
estimate``, which is resolved to its field id the way a column map's
custom field is; a whole name that is a display name is not split at its
dots.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import NamedTuple, Optional
from backlogops.jira_connect import JiraConnections
from backlogops.jira_read import _custom_ids


class JiraFieldJson(NamedTuple):
    """The raw Jira JSON found for one requested field path of an issue.

    Fields:
        name: The field or dotted path as requested, such as
            ``timetracking.remainingEstimateSeconds``.
        field_id: The Jira field id the first step resolved to, such as
            ``customfield_10016`` for ``Story point estimate``.
        present: Whether the issue holds a value at the path; False when a
            step names no key of an object or no index of a list.
        value: The JSON value at the path; None when it is not present, or
            when Jira holds null there.
        edit_entry: The field's entry on the issue's edit screen, with the
            operations Jira allows, or None when the edit screen does not
            offer the field, which then cannot be written by an edit.
    """

    name: str
    field_id: str
    present: bool
    value: object
    edit_entry: Optional[dict[str, object]]


def _split_name(name: str, custom_ids: dict[str, str]
                ) -> tuple[str, list[str]]:
    """Return the field id and the remaining path steps of a dotted name.

    A whole name that is a custom field display name is not split, so a
    display name containing a dot still resolves.
    """
    if name in custom_ids:
        return custom_ids[name], []
    first, *rest = name.split('.')
    return custom_ids.get(first, first), rest


def _walk_json(value: object, steps: list[str]) -> tuple[bool, object]:
    """Return whether the path steps exist in the JSON and the value there.

    A step into an object is its key and a step into a list is its index.
    """
    for step in steps:
        if isinstance(value, dict) and step in value:
            value = value[step]
        elif isinstance(value, list) and step.isdigit() and \
                int(step) < len(value):
            value = value[int(step)]
        else:
            return False, None
    return True, value


def _lookup(name: str, fields: dict[str, object], custom_ids: dict[str, str],
            editable: dict[str, object]) -> JiraFieldJson:
    """Return the JSON at one requested path and its edit screen entry."""
    field_id, steps = _split_name(name, custom_ids)
    present, value = _walk_json(fields, [field_id, *steps])
    entry = editable.get(field_id)
    return JiraFieldJson(name, field_id, present, value,
                         entry if isinstance(entry, dict) else None)


def jira_field_json(connections: JiraConnections, preset_name: str,
                    issue_key: str, names: list[str]) -> list[JiraFieldJson]:
    """Return the raw Jira JSON of the named field paths of one issue.

    The issue's fields are read once as the JSON Jira returns, so every
    field is present, including read-only ones that a column map may read
    from but never write to. Each name is looked up as described in the
    module docstring. No names need no Jira calls.

    Args:
        connections: The pool holding the configuration with the preset.
        preset_name: The name of the Jira preset whose connection to use.
        issue_key: The key of the issue to read, such as ``SCRUM-15``.
        names: The field ids or dotted paths to look up, in output order.

    Returns:
        One result per name, in the order of ``names``.

    Raises:
        KeyError: If the preset or its connection is missing.
        JIRAError: If Jira refuses to return the issue or its edit screen.
    """
    if not names:
        return []
    preset = connections.jira_config.get_preset(preset_name)
    client = connections.client(preset.connection_name)
    fields = client.issue(issue_key).raw.get('fields', {})
    custom_ids = _custom_ids(client.fields())
    editable = client.editmeta(issue_key).get('fields', {})
    return [_lookup(name, fields, custom_ids, editable) for name in names]
