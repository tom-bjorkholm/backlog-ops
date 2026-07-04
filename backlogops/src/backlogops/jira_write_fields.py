#! /usr/local/bin/python3
"""Invert a Jira column map into write payloads and issue-link specs.

Writing to Jira is the inverse of reading: a value read from a Jira
attribute path is written back to the same path. This module holds the
pure helpers that build one Jira field payload from a mapped path
(:func:`_place_value` and the parent update fields from
:func:`_parent_fields`) and that derive how a dependency field is written
as a Jira issue link (:func:`_link_specs`). It also defines
:class:`FailedLink`, the result of a link that Jira refused. The
orchestration that creates issues and writes the links lives in
:mod:`backlogops.jira_write`, which imports these helpers.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass
from typing import NamedTuple, Optional
from backlogops.backlog import BacklogItem, DEPENDENCY_FIELDS
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType, JiraColumnMap
from backlogops.jira_read import _field_id

_JIRA_LIST_FIELDS = frozenset({'fixVersions', 'versions', 'components'})
"""Jira issue fields whose create value is a list of named objects."""


class FailedLink(NamedTuple):
    """A link between two items that could not be written to Jira.

    Fields:
        item: The stored source item, carrying its Jira key.
        target: The Jira key the link points to, a parent or a dependency.
        relation: The link relation, ``'parent'`` or the Jira link type
            name such as ``'Blocks'``.
        reason: A concise reason the link could not be written.
    """

    item: BacklogItem
    target: str
    relation: str
    reason: str


def _nest(path: tuple[str, ...], value: object) -> dict[str, object]:
    """Return ``value`` wrapped in nested dicts named by the path steps."""
    result: object = value
    for step in reversed(path):
        result = {step: result}
    assert isinstance(result, dict)
    return result


def _field_payload(path: tuple[str, ...], value: object) -> dict[str, object]:
    """Return the create-fields entry for a plain or list issue field."""
    if path[0] in _JIRA_LIST_FIELDS:
        inner = _nest(path[1:], value) if len(path) > 1 else {'name': value}
        return {path[0]: [inner]}
    return _nest(path, value)


def _place_value(fields: dict[str, object], attr: JiraAttrPath, value: object,
                 custom_ids: dict[str, str]) -> None:
    """Place one field value into the Jira create-fields dict by kind."""
    if attr.kind is JiraAttrType.CUSTOM_FIELD:
        field_id = _field_id(attr.path[0], custom_ids)
        if field_id is not None:
            fields[field_id] = value
    elif attr.kind is JiraAttrType.FIELD:
        fields.update(_field_payload(attr.path, value))


def _parent_fields(column_map: JiraColumnMap, custom_ids: dict[str, str],
                   parent_key: str) -> dict[str, object]:
    """Build the update fields that set an item's parent link.

    The first mapped ``parent_key`` path is inverted, so the default map's
    ``parent`` field becomes ``{'parent': {'key': parent_key}}`` and an
    ``Epic Link`` custom field becomes its resolved field id. A
    ``parent_key`` that is not mapped, or whose custom field cannot be
    resolved, yields no fields.
    """
    attrs = column_map.get('parent_key', ())
    if not attrs:
        return {}
    fields: dict[str, object] = {}
    _place_value(fields, attrs[0], parent_key, custom_ids)
    return fields


@dataclass(frozen=True)
class _LinkSpec:
    """How to write one dependency field as a Jira issue link.

    ``field`` is the internal dependency field name, ``link_type`` is the
    Jira issue link type name to create (such as ``Blocks``), and
    ``dep_is_inward`` says the dependency is the inward issue on the
    current issue, so the link is created with the current issue as the
    inward side and the dependency as the outward side.
    """

    field: str
    link_type: str
    dep_is_inward: bool


def _link_attr(attrs: tuple[JiraAttrPath, ...]) -> Optional[JiraAttrPath]:
    """Return the first ``issuelinks`` FILTERED_FIELD path, or None.

    This is the path a dependency field is both read from and written as a
    Jira issue link, so it is shared by the link spec and by the update
    path that reads an issue's current links.
    """
    for attr in attrs:
        if attr.kind is JiraAttrType.FILTERED_FIELD and \
                len(attr.path) == 4 and attr.path[0] == 'issuelinks':
            return attr
    return None


def _link_spec_for(name: str, attrs: tuple[JiraAttrPath, ...]
                   ) -> Optional[_LinkSpec]:
    """Return the issue-link spec inverted from a dependency map entry.

    The first FILTERED_FIELD path over ``issuelinks`` is inverted: its
    expected filter value is the link type name and its value path names
    the side the dependency is read from, so ``inwardIssue.key`` means the
    dependency is the inward issue on the current issue. A field without
    such a path cannot be written as a link and yields None.
    """
    attr = _link_attr(attrs)
    if attr is None:
        return None
    return _LinkSpec(name, attr.path[2],
                     attr.path[3].startswith('inwardIssue'))


def _link_specs(column_map: JiraColumnMap) -> list[_LinkSpec]:
    """Return the writable issue-link specs for the dependency fields."""
    specs = []
    for name in DEPENDENCY_FIELDS:
        spec = _link_spec_for(name, column_map.get(name, ()))
        if spec is not None:
            specs.append(spec)
    return specs


def _dep_link_attrs(column_map: JiraColumnMap
                    ) -> list[tuple[_LinkSpec, JiraAttrPath]]:
    """Return each dependency field's link spec paired with its path.

    Only the dependency fields whose map has an ``issuelinks`` path are
    returned. The path lets the update path read the issue's current links
    for that field, so it can add the missing links and remove stale ones.
    """
    result: list[tuple[_LinkSpec, JiraAttrPath]] = []
    for name in DEPENDENCY_FIELDS:
        attrs = column_map.get(name, ())
        spec = _link_spec_for(name, attrs)
        attr = _link_attr(attrs)
        if spec is not None and attr is not None:
            result.append((spec, attr))
    return result
