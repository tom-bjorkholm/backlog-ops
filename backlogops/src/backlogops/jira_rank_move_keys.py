#! /usr/local/bin/python3
"""Move named issues to a chosen anchor of a Jira backlog by rank.

A backlog in Jira is the set of issues a filter reads in their Jira rank
order. :func:`jira_rank_move_keys` moves the named issues to a chosen
:class:`~backlogops.jira_rank_backlog.JiraRankAnchor` of that backlog and
leaves every other issue in its existing Jira rank order.

By default only the named issues are moved, in the order they are listed.
When relations are honoured the moved block is instead the named issues,
all their descendants (the items below them in the parent and child
hierarchy) and their dependencies: for a top or first-key anchor the
prerequisites of the block are pulled along, so everything the named issues
need is ranked before them, and for a bottom or last-key anchor the
dependents are pulled along, so everything that needs the named issues is
ranked after them. That block is ordered by
:func:`backlogops.order_by_dependencies.order_by_dependencies`, so a parent
is ranked before its child and a prerequisite before its dependent. The new
order is written to Jira through
:func:`backlogops.jira_rank_by_keys.jira_rank_by_keys_raw`.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from typing import NamedTuple, Optional, Sequence, TextIO
from jira import JIRA
from backlogops.backlog import Backlog, Status
from backlogops.jira_connect import JiraConnections
from backlogops.jira_rank_backlog import (
    JiraRankAnchor, _ensure_rank_order, _rank_keys)
from backlogops.jira_read import read_backlog_from_jira, resolve_jql
from backlogops.jira_write import _issue_exists
from backlogops.jira_write_format import _key_section
from backlogops.levels import Levels
from backlogops.order_by_dependencies import (
    order_by_dependencies, precedence_relations)


class RankedInJira(NamedTuple):
    """The result of moving named issues in the Jira rank order.

    Fields:
        keys_ranked_ok: The named issue keys that were found in the backlog
                        and re-ranked in Jira.
        keys_not_in_jira: The named issue keys that do not exist in Jira.
        keys_not_in_filter: The named issue keys that exist in Jira but
                            were not read by the filter, so they are not
                            part of the backlog.
    """

    keys_ranked_ok: list[str]
    keys_not_in_jira: list[str]
    keys_not_in_filter: list[str]


def _children(backlog: Backlog) -> dict[str, list[str]]:
    """Return the child keys of each parent key, in backlog order."""
    children: dict[str, list[str]] = {}
    for item in backlog:
        if item.parent_key is not None:
            children.setdefault(item.parent_key, []).append(item.key)
    return children


def _descendants(backlog: Backlog, roots: Sequence[str]) -> set[str]:
    """Return the transitive descendant keys of the given root keys."""
    children = _children(backlog)
    found: set[str] = set()
    stack = list(roots)
    while stack:
        for child in children.get(stack.pop(), []):
            if child not in found:
                found.add(child)
                stack.append(child)
    return found


def _family(backlog: Backlog, named: Sequence[str],
            anchor: JiraRankAnchor) -> set[str]:
    """Return the keys to move: the named keys, descendants and their deps.

    The named keys and all their descendants are always included. For a top
    or first-key anchor the transitive prerequisites of that set are added,
    so everything the named issues need is ranked before them. For a bottom
    or last-key anchor the transitive dependents are added, so everything
    that needs the named issues is ranked after them.
    """
    base = set(named) | _descendants(backlog, named)
    before, after = precedence_relations(backlog)
    toward_top = anchor in (JiraRankAnchor.BACKLOG_TOP,
                            JiraRankAnchor.FIRST_KEY)
    related = before if toward_top else after
    block = set(base)
    for key in base:
        block |= related.get(key, set())
    return block


def _block_order(backlog: Backlog, block: set[str],
                 stderr_file: TextIO) -> list[str]:
    """Return the block keys ordered by dependencies, parent before child.

    The block items are taken in their current backlog rank order and
    reordered by :func:`order_by_dependencies`, so a parent is ranked
    before its child and a prerequisite before its dependent.
    """
    items = [item for item in backlog if item.key in block]
    ordered = order_by_dependencies(items, stderr_file=stderr_file)
    return [item.key for item in ordered]


def _ordered_block(backlog: Backlog, found: Sequence[str],
                   anchor: JiraRankAnchor, honor_relations: bool,
                   stderr_file: TextIO) -> list[str]:
    """Return the found keys as the ordered block to rank.

    Without honouring relations the found keys are ranked in the listed
    order. Honouring relations expands them into their family and orders the
    whole block by dependencies, parent before child.
    """
    if not honor_relations:
        return list(found)
    block = _family(backlog, found, anchor)
    return _block_order(backlog, block, stderr_file)


def _rank_plan(backlog: Backlog, found: Sequence[str], anchor: JiraRankAnchor,
               honor_relations: bool,
               stderr_file: TextIO) -> tuple[list[str], list[str]]:
    """Return the ordered block keys and the remaining backlog keys.

    The ordered block is the keys to move in their wanted order. The rest
    are every other backlog key in their existing Jira rank order, used to
    find the backlog end for a top or bottom anchor.
    """
    ordered = _ordered_block(backlog, found, anchor, honor_relations,
                             stderr_file)
    block = set(ordered)
    rest = [item.key for item in backlog if item.key not in block]
    return ordered, rest


def _present_and_absent(requested: Sequence[str], backlog: Backlog
                        ) -> tuple[list[str], list[str]]:
    """Split requested keys into those in the backlog and those not in it.

    Duplicate requests are collapsed, keeping the first occurrence, so the
    two returned lists together hold each requested key once.
    """
    present = {item.key for item in backlog}
    found: list[str] = []
    absent: list[str] = []
    seen: set[str] = set()
    for key in requested:
        if key in seen:
            continue
        seen.add(key)
        (found if key in present else absent).append(key)
    return found, absent


def _split_absent(client: JIRA,
                  absent: Sequence[str]) -> tuple[list[str], list[str]]:
    """Split absent keys into not-in-Jira and excluded-by-filter keys."""
    not_in_jira: list[str] = []
    not_in_filter: list[str] = []
    for key in absent:
        target = not_in_filter if _issue_exists(client, key) \
            else not_in_jira
        target.append(key)
    return not_in_jira, not_in_filter


def _classify(connections: JiraConnections, connection_name: str,
              requested: Sequence[str], backlog: Backlog) -> RankedInJira:
    """Classify requested keys against the backlog and existing Jira issues.

    The found keys are the ``keys_ranked_ok`` of the result, so the caller
    ranks those and returns the same complete classification.
    """
    client = connections.client(connection_name)
    found, absent = _present_and_absent(requested, backlog)
    not_in_jira, not_in_filter = _split_absent(client, absent)
    return RankedInJira(found, not_in_jira, not_in_filter)


# pylint: disable-next=too-many-arguments
def jira_rank_move_keys(connections: JiraConnections, preset_name: str,
                        issue_keys: Sequence[str], *,
                        filter_override: Optional[str] = None,
                        anchor: JiraRankAnchor = JiraRankAnchor.BACKLOG_TOP,
                        honor_relations: bool = False,
                        levels: Optional[Levels] = None,
                        status_map: Optional[dict[str, Status]] = None,
                        stderr_file: TextIO = sys.stderr) -> RankedInJira:
    """Move named issues to a chosen anchor of a Jira backlog by rank.

    The preset names the connection and the column maps, and its filter
    (or ``filter_override`` when given) reads the backlog in its Jira rank
    order. By default only the named issues are moved, in the order they are
    listed. When ``honor_relations`` is set the named issues, their
    descendants and their dependencies are moved as one block, ordered so
    that a parent is ranked before its child and a prerequisite before its
    dependent. The ``anchor`` chooses where the moved keys land, as
    described on :class:`~backlogops.jira_rank_backlog.JiraRankAnchor`.
    Every other issue keeps its existing Jira rank order. A named key that
    is not part of the backlog is not ranked but reported, either as not
    existing in Jira or as excluded by the filter.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset.
        preset_name: The name of the preset to use.
        issue_keys: The keys of the issues to move. Without honouring
            relations they are ranked in this order.
        filter_override: A Jira filter to use instead of the preset's. It
            may only order by rank ascending; a missing ORDER BY clause is
            added.
        anchor: Where the moved keys land in the Jira rank order.
        honor_relations: Whether to also move the descendants and
            dependencies of the named issues and order the block parent
            before child (True), or to rank only the listed keys in the
            listed order (False, the default).
        levels: The levels used to resolve a string level, or None for the
            default levels.
        status_map: Extra Jira status names mapped to Status members, or
            None. Needed when the Jira statuses are not the built-in names.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The keys that were re-ranked and the named keys that were not part
        of the backlog.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        BadJiraRankFilter: If the filter orders by anything but rank.
        JiraTooManyLoops: If the ranking does not converge within the loop
            limit.
        JIRAError: If a Jira call fails.
    """
    preset = connections.jira_config.get_preset(preset_name)
    jql = _ensure_rank_order(resolve_jql(preset, filter_override))
    backlog = read_backlog_from_jira(connections, preset_name,
                                     filter_override=jql, levels=levels,
                                     status_map=status_map,
                                     stderr_file=stderr_file).backlog
    result = _classify(connections, preset.connection_name, issue_keys,
                       backlog)
    if not result.keys_ranked_ok:
        return result
    ordered, rest = _rank_plan(backlog, result.keys_ranked_ok, anchor,
                               honor_relations, stderr_file)
    _rank_keys(connections, preset.connection_name, ordered, anchor, rest)
    return result


def format_rank_result(result: RankedInJira) -> str:
    """Return a listing of the ranked, not-in-Jira and not-in-filter keys.

    Each section has a heading with its count, then one indented key per
    line, or a ``(none)`` line when it is empty. The CLI prints this text
    and the GUI shows it in a copy-pasteable pop-up.
    """
    lines = _key_section('Ranked in Jira', result.keys_ranked_ok)
    lines.append('')
    lines.extend(_key_section('Not in Jira', result.keys_not_in_jira))
    lines.append('')
    lines.extend(_key_section('Excluded by the filter',
                              result.keys_not_in_filter))
    return '\n'.join(lines)
