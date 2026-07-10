#! /usr/local/bin/python3
"""Order releases in Jira, changing the order of a project's versions.

A release is a Jira version, and a project keeps its versions in an ordered
list. :func:`order_releases_in_jira` moves the versions named by a list of
names to the front of that list in the given order, and
:func:`order_jira_rel_by_date` orders every version by its release date,
earliest first. In both cases the versions that are not moved keep their
existing relative order and trail the ordered ones.

The wanted order is imposed by moving each wanted version to the first
position, working from the last wanted version to the first, so the first
wanted version ends up on top and the block ends up leading the list. Only the
absolute ``First`` position is used, so the order does not depend on the
direction of a relative move. When the versions are already in the wanted
order nothing is written to Jira. A name that is not a version is reported
rather than moved.

Ordering by date reads each version's own ``releaseDate`` and sorts earliest
first; a version without a valid release date is placed at the end, and
versions that share a date, or are all undated, keep their existing relative
order.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from datetime import date
from typing import NamedTuple, Optional, Sequence, TextIO
from jira import JIRA
from jira.resources import Resource
from backlogops.jira_connect import JiraConnections
from backlogops.jira_write_format import _key_section
from backlogops.jira_write_releases import _by_name, _release_context


class OrderedReleasesInJira(NamedTuple):
    """The result of ordering releases in Jira.

    Fields:
        ordered: The version names placed into the wanted order, in that
            order.
        not_in_jira: The requested names that are not the name of any Jira
            version, so they could not be ordered.
    """

    ordered: list[str]
    not_in_jira: list[str]


def _names_in_order(versions: Sequence[Resource]) -> list[str]:
    """Return the version names in their current Jira order."""
    return [name for name in (getattr(v, 'name', None) for v in versions)
            if isinstance(name, str)]


def _apply_order(client: JIRA, versions: Sequence[Resource],
                 wanted: Sequence[str]) -> None:
    """Move the wanted versions to the front, keeping the others trailing.

    Nothing is written when the versions already lead with the wanted order.
    Otherwise each wanted version is moved to the first position from the last
    wanted name to the first, so the first wanted name ends up on top.
    """
    if not wanted:
        return
    current = _names_in_order(versions)
    chosen = set(wanted)
    trailing = [name for name in current if name not in chosen]
    if list(wanted) + trailing == current:
        return
    by_name = _by_name(versions)
    for name in reversed(wanted):
        client.move_version(str(getattr(by_name[name], 'id')),
                            position='First')


def _split_present(names: Sequence[str], by_name: dict[str, Resource]
                   ) -> tuple[list[str], list[str]]:
    """Split names into present version names and names not in Jira.

    Duplicate names are collapsed, keeping the first occurrence, so each name
    appears once across the two returned lists.
    """
    present: list[str] = []
    absent: list[str] = []
    seen: set[str] = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        (present if name in by_name else absent).append(name)
    return present, absent


def order_releases_in_jira(connections: JiraConnections, preset_name: str,
                           names: Sequence[str], *,
                           stderr_file: TextIO = sys.stderr
                           ) -> OrderedReleasesInJira:
    """Order releases in Jira to match a list of names.

    The project's versions are read once. The versions named by ``names``
    that exist are moved to the front of the version list in the listed
    order; every other version keeps its existing relative order and trails
    them. A name that is not a version is reported and not ordered. Nothing is
    written when the versions are already in the wanted order.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset and its default project.
        preset_name: The name of the Jira preset to use.
        names: The version names in the wanted order. Duplicates are ignored
            after their first occurrence.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The names placed into the wanted order and the names not in Jira.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        JIRAError: If a Jira move call fails.
    """
    _ = stderr_file
    ctx = _release_context(connections, preset_name)
    versions = ctx.client.project_versions(ctx.project)
    present, absent = _split_present(names, _by_name(versions))
    _apply_order(ctx.client, versions, present)
    return OrderedReleasesInJira(present, absent)


def _release_date(version: Resource) -> Optional[date]:
    """Return a version's release date, or None when it has no valid one."""
    raw = getattr(version, 'releaseDate', None)
    if isinstance(raw, str):
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None
    return None


def _date_key(version: Resource) -> tuple[bool, date]:
    """Return a sort key ordering by release date, undated versions last."""
    released = _release_date(version)
    return released is None, released if released is not None else date.min


def _by_date_order(versions: Sequence[Resource]) -> list[str]:
    """Return the version names ordered by release date, earliest first."""
    named = [version for version in versions
             if isinstance(getattr(version, 'name', None), str)]
    return [getattr(version, 'name')
            for version in sorted(named, key=_date_key)]


def order_jira_rel_by_date(connections: JiraConnections, preset_name: str, *,
                           stderr_file: TextIO = sys.stderr
                           ) -> OrderedReleasesInJira:
    """Order releases in Jira by their release date, earliest first.

    The project's versions are read once and ordered by their own
    ``releaseDate``, earliest first, with an undated version placed at the
    end. Versions that share a date, or are all undated, keep their existing
    relative order. Nothing is written when the versions are already in that
    order.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset and its default project.
        preset_name: The name of the Jira preset to use.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The version names in the resulting date order and an empty
        not-in-Jira list, since every version is ordered.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        JIRAError: If a Jira move call fails.
    """
    _ = stderr_file
    ctx = _release_context(connections, preset_name)
    versions = ctx.client.project_versions(ctx.project)
    ordered = _by_date_order(versions)
    _apply_order(ctx.client, versions, ordered)
    return OrderedReleasesInJira(ordered, [])


def format_order_result(result: OrderedReleasesInJira) -> str:
    """Return a listing of the ordered names and the names not in Jira.

    Each section has a heading with its count, then one indented name per
    line, or a ``(none)`` line when it is empty. The CLI prints this text and
    the GUI shows it in a copy-pasteable pop-up.
    """
    lines = _key_section('Ordered in Jira', result.ordered)
    lines.append('')
    lines.extend(_key_section('Not in Jira', result.not_in_jira))
    return '\n'.join(lines)
