#! /usr/local/bin/python3
"""Move named issues to the front or the end of a Jira backlog by rank.

A backlog in Jira is the set of issues a filter reads in their Jira rank
order. :func:`jira_rank_move_keys` moves the named issues, together with
the issues they pull along, to the front or the end of that backlog, and
leaves every other issue in its existing Jira rank order.

The moved block is the named issues, all their descendants (the items below
them in the parent and child hierarchy) and their dependencies. For a move
to the front the dependencies pulled along are the prerequisites of the
block, so everything the named issues need is ranked before them. For a
move to the end they are the dependents of the block, so everything that
needs the named issues is ranked after them. The block is ordered by
:func:`backlogops.order_by_dependencies.order_by_dependencies`, so a parent
is ranked before its child and a prerequisite before its dependent. The new
order is written to Jira through
:func:`backlogops.jira_rank_by_keys.jira_rank_by_keys_raw`.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from enum import Enum, auto
from typing import NamedTuple, Optional, Sequence, TextIO
from jira import JIRA
from backlogops.backlog import Backlog, Status
from backlogops.jira_connect import JiraConnections
from backlogops.jira_rank_by_keys import jira_rank_by_keys_raw
from backlogops.jira_read import read_backlog_from_jira, resolve_jql
from backlogops.jira_write import _issue_exists, _key_section
from backlogops.levels import Levels
from backlogops.order_by_dependencies import (
    order_by_dependencies, precedence_relations)


class JiraMoveToEnd(Enum):
    """Which end of the Jira backlog the named issues are moved to."""

    FIRST = auto()
    LAST = auto()


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


class BadJiraRankFilter(ValueError):
    """Raised when a filter cannot be used for ranking in Jira.

    A filter used for ranking must read the backlog in its Jira rank
    order, so it may only order by rank ascending. This is raised when the
    filter orders by anything else.
    """

    def __init__(self, *, jql_text: str, message: str) -> None:
        """Store the filter and the reason and build the message."""
        self.jql_text = jql_text
        self.reason_message = message
        super().__init__(f"Filter '{jql_text}' is not usable for ranking "
                         f'in Jira: {message}')


def _ensure_rank_order(jql: str) -> str:
    """Return the filter with an ``ORDER BY Rank ASC`` clause enforced.

    A filter with no ORDER BY clause has one appended. A filter that
    already orders by rank ascending is returned unchanged. Any other
    ORDER BY clause is rejected, because it would not read the backlog in
    its Jira rank order.

    Raises:
        BadJiraRankFilter: If the filter orders by anything but rank.
    """
    marker = 'order by'
    index = jql.lower().rfind(marker)
    if index == -1:
        return f'{jql} ORDER BY Rank ASC'
    clause = ' '.join(jql[index + len(marker):].lower().split())
    if clause in ('rank', 'rank asc'):
        return jql
    raise BadJiraRankFilter(jql_text=jql,
                            message="the only allowed ORDER BY clause is"
                                    " 'Rank ASC'")


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
            move_to_end: JiraMoveToEnd) -> set[str]:
    """Return the keys to move: the named keys, descendants and their deps.

    The named keys and all their descendants are always included. For a
    move to the front the transitive prerequisites of that set are added,
    so everything the named issues need is ranked before them. For a move
    to the end the transitive dependents are added, so everything that
    needs the named issues is ranked after them.
    """
    base = set(named) | _descendants(backlog, named)
    before, after = precedence_relations(backlog)
    related = before if move_to_end is JiraMoveToEnd.FIRST else after
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


def _rank_plan(backlog: Backlog, named: Sequence[str],
               move_to_end: JiraMoveToEnd,
               stderr_file: TextIO) -> tuple[list[str], bool]:
    """Return the key list and move_before flag for the raw ranking call.

    The moved block (the named keys with their descendants and pulled
    dependencies) is ordered by dependencies. For a move to the front the
    ordered block is followed by the first remaining key and ranked before
    it; for a move to the end the last remaining key is followed by the
    ordered block and ranked after it. This keeps every remaining item in
    its existing Jira rank order and moves only the block.
    """
    block = _family(backlog, named, move_to_end)
    order = _block_order(backlog, block, stderr_file)
    rest = [item.key for item in backlog if item.key not in block]
    if not rest:
        return order, False
    if move_to_end is JiraMoveToEnd.FIRST:
        return order + [rest[0]], True
    return [rest[-1]] + order, False


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
              requested: Sequence[str],
              backlog: Backlog) -> tuple[RankedInJira, list[str]]:
    """Classify requested keys against the backlog and existing Jira issues.

    Returns the full result and the list of found keys, so the caller can
    rank the found keys and still return the complete classification.
    """
    client = connections.client(connection_name)
    found, absent = _present_and_absent(requested, backlog)
    not_in_jira, not_in_filter = _split_absent(client, absent)
    return RankedInJira(found, not_in_jira, not_in_filter), found


# pylint: disable-next=too-many-arguments
def jira_rank_move_keys(connections: JiraConnections, preset_name: str,
                        issue_keys: Sequence[str], *,
                        filter_override: Optional[str] = None,
                        move_to_end: JiraMoveToEnd = JiraMoveToEnd.FIRST,
                        levels: Optional[Levels] = None,
                        status_map: Optional[dict[str, Status]] = None,
                        stderr_file: TextIO = sys.stderr) -> RankedInJira:
    """Move named issues to the front or the end of a Jira backlog by rank.

    The preset names the connection and the column maps, and its filter
    (or ``filter_override`` when given) reads the backlog in its Jira rank
    order. The named issues, their descendants and their dependencies are
    moved as one block to the front (``FIRST``) or the end (``LAST``) of
    that backlog, ordered so that a parent is ranked before its child and a
    prerequisite before its dependent. Every other issue keeps its existing
    Jira rank order. A named key that is not part of the backlog is not
    ranked but reported, either as not existing in Jira or as excluded by
    the filter.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset.
        preset_name: The name of the preset to use.
        issue_keys: The keys of the issues to move, in no required order.
        filter_override: A Jira filter to use instead of the preset's. It
            may only order by rank ascending; a missing ORDER BY clause is
            added.
        move_to_end: Whether to move the named issues to the front
            (``FIRST``, the default) or the end (``LAST``) of the backlog.
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
    result, found = _classify(connections, preset.connection_name, issue_keys,
                              backlog)
    if not found:
        return result
    raw_keys, move_before = _rank_plan(backlog, found, move_to_end,
                                       stderr_file)
    jira_rank_by_keys_raw(connections, preset.connection_name, raw_keys,
                          move_before=move_before)
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
