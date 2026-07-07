#! /usr/local/bin/python3
"""Rank a backlog in Jira into its given order at a chosen anchor.

:func:`jira_rank_backlog` ranks the items of a backlog in Jira so that they
end up in the order they appear in the backlog, relative to each other. It
is a convenience wrapper over
:func:`backlogops.jira_rank_by_keys.jira_rank_by_keys_raw` that takes a
backlog and a :class:`JiraRankAnchor` instead of a key list and a
``move_before`` flag.

The anchor chooses where the ordered block lands. ``FIRST_KEY`` keeps the
first item's Jira rank fixed and ranks the rest after it, and ``LAST_KEY``
keeps the last item's rank fixed and ranks the rest before it; neither reads
the rest of the backlog. ``BACKLOG_TOP`` and ``BACKLOG_BOTTOM`` place the
block at the top or the bottom of the backlog the preset filter reads, so
the current filter result is read to find that end while every other issue
keeps its rank.

This module also holds the shared :class:`JiraRankAnchor` enum, the
:class:`BadJiraRankFilter` error and the filter and placement helpers used
by :func:`backlogops.jira_rank_move_keys.jira_rank_move_keys`.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Sequence, TextIO
from jira import JIRAError
from backlogops.backlog import Backlog, Status
from backlogops.jira_connect import JiraConnections
from backlogops.jira_rank_by_keys import (
    jira_rank_by_keys_raw, JiraKeyError, JiraTooManyLoops)
from backlogops.jira_read import read_backlog_from_jira, resolve_jql
from backlogops.levels import Levels


class JiraRankAnchor(Enum):
    """The fixed reference point a ranking is arranged around.

    ``BACKLOG_TOP`` and ``BACKLOG_BOTTOM`` place the ranked items at the top
    or bottom of the whole backlog the filter reads. ``FIRST_KEY`` keeps the
    first listed key fixed and ranks the rest after it, and ``LAST_KEY``
    keeps the last listed key fixed and ranks the rest before it.
    """

    BACKLOG_TOP = auto()
    BACKLOG_BOTTOM = auto()
    FIRST_KEY = auto()
    LAST_KEY = auto()


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


_RANK_ERRORS = (JIRAError, JiraKeyError, JiraTooManyLoops, BadJiraRankFilter)
"""Errors from a ranking that :func:`rank_backlog_or_warn` reports."""


@dataclass(frozen=True)
class RankEnv:
    """The connection, preset and options for a post-write ranking.

    Bundles the arguments the add and update operations share when they
    also rank, so :func:`rank_backlog_or_warn` stays a short call. An
    ``anchor`` of None ranks nothing.
    """

    connections: JiraConnections
    preset_name: str
    anchor: Optional[JiraRankAnchor]
    levels: Optional[Levels] = None
    status_map: Optional[dict[str, Status]] = None
    stderr_file: TextIO = sys.stderr


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


def _anchor_plan(ordered: Sequence[str], anchor: JiraRankAnchor,
                 rest: Sequence[str]) -> tuple[list[str], bool]:
    """Return the key list and move-before flag for the raw ranking call.

    The keys in ``ordered`` keep their given order and are anchored per
    ``anchor``. ``FIRST_KEY`` keeps the first key fixed (rest ranked after)
    and ``LAST_KEY`` keeps the last key fixed (rest ranked before), so the
    rest of the backlog is not needed. ``BACKLOG_TOP`` ranks the block just
    before the first remaining key and ``BACKLOG_BOTTOM`` just after the
    last remaining key, so the block lands at that end while every remaining
    key keeps its rank. With no remaining keys both ends keep the first key
    fixed.
    """
    keys = list(ordered)
    if anchor is JiraRankAnchor.FIRST_KEY:
        return keys, False
    if anchor is JiraRankAnchor.LAST_KEY:
        return keys, True
    if not rest:
        return keys, False
    if anchor is JiraRankAnchor.BACKLOG_TOP:
        return keys + [rest[0]], True
    return [rest[-1]] + keys, False


def _rank_keys(connections: JiraConnections, connection_name: str,
               ordered: Sequence[str], anchor: JiraRankAnchor,
               rest: Sequence[str]) -> None:
    """Place the ordered keys per anchor and rank them in Jira.

    A plan of fewer than two keys leaves nothing to rank relative to
    another key, so the ranking call is skipped.
    """
    raw_keys, move_before = _anchor_plan(ordered, anchor, rest)
    if len(raw_keys) < 2:
        return
    jira_rank_by_keys_raw(connections, connection_name, raw_keys,
                          move_before=move_before)


# pylint: disable-next=too-many-arguments
def _rank_key_list(connections: JiraConnections, preset_name: str,
                   keys: Sequence[str], *, anchor: JiraRankAnchor,
                   filter_override: Optional[str] = None,
                   levels: Optional[Levels] = None,
                   status_map: Optional[dict[str, Status]] = None,
                   stderr_file: TextIO = sys.stderr) -> None:
    """Rank the given keys in Jira in their order at the chosen anchor.

    For an end anchor the preset filter (or ``filter_override``) is read to
    find the backlog end and the remaining keys, so the block lands at that
    end while every other issue keeps its rank. Key-relative anchors need no
    read. The keys must be unique and present in Jira.
    """
    preset = connections.jira_config.get_preset(preset_name)
    rest: list[str] = []
    if anchor in (JiraRankAnchor.BACKLOG_TOP, JiraRankAnchor.BACKLOG_BOTTOM):
        jql = _ensure_rank_order(resolve_jql(preset, filter_override))
        fetched = read_backlog_from_jira(connections, preset_name,
                                         filter_override=jql, levels=levels,
                                         status_map=status_map,
                                         stderr_file=stderr_file).backlog
        block = set(keys)
        rest = [item.key for item in fetched if item.key not in block]
    _rank_keys(connections, preset.connection_name, keys, anchor, rest)


# pylint: disable-next=too-many-arguments
def jira_rank_backlog(connections: JiraConnections, preset_name: str,
                      backlog: Backlog, *, anchor: JiraRankAnchor,
                      filter_override: Optional[str] = None,
                      levels: Optional[Levels] = None,
                      status_map: Optional[dict[str, Status]] = None,
                      stderr_file: TextIO = sys.stderr) -> None:
    """Rank the backlog items in Jira into the order they appear in.

    The items are ranked in Jira so that they end up in the backlog's order
    relative to each other. Every item must already exist in Jira. The
    ``anchor`` chooses where the ordered block lands, as described on
    :class:`JiraRankAnchor`. For ``BACKLOG_TOP`` and ``BACKLOG_BOTTOM`` the
    preset filter (or ``filter_override``) is read to find the backlog end;
    it may only order by rank ascending. A backlog of fewer than two items
    with a key-relative anchor needs no ranking and returns at once.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset.
        preset_name: The name of the Jira preset to use.
        backlog: The items to rank, in the wanted order. Keys must be
            unique and present in Jira. Not modified.
        anchor: Where the ordered block lands in the Jira rank order.
        filter_override: A Jira filter used instead of the preset's when an
            end anchor reads the backlog; it may only order by rank.
        levels: The levels used to resolve a string level while reading, or
            None for the default levels.
        status_map: Extra Jira status names mapped to Status members, or
            None. Needed when the Jira statuses are not the built-in names.
        stderr_file: Stream used for user-facing diagnostics.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        BadJiraRankFilter: If an end anchor reads a filter that orders by
            anything but rank.
        JiraKeyError: If an item key is not present in Jira.
        JiraTooManyLoops: If the ranking does not converge within the loop
            limit.
        JIRAError: If a Jira ranking call fails.
    """
    _rank_key_list(connections, preset_name, [item.key for item in backlog],
                   anchor=anchor, filter_override=filter_override,
                   levels=levels, status_map=status_map,
                   stderr_file=stderr_file)


def rank_backlog_or_warn(env: RankEnv, present: Backlog,
                         key_map: dict[str, str]) -> None:
    """Rank the present items in Jira in order, reporting a refusal.

    This is used after adding or updating a backlog to also set its Jira
    rank order. Each present item's key is remapped through ``key_map``, so
    an item added in the same run is ranked by its assigned Jira key, and
    the items are ranked in their given order at the environment's anchor
    using the preset filter. An anchor of None ranks nothing. A ranking
    Jira refuses is reported as a warning and does not undo the completed
    add or update.
    """
    if env.anchor is None:
        return
    keys = [key_map.get(item.key, item.key) for item in present]
    try:
        _rank_key_list(env.connections, env.preset_name, keys,
                       anchor=env.anchor, levels=env.levels,
                       status_map=env.status_map, stderr_file=env.stderr_file)
    except _RANK_ERRORS as error:
        print(f'WARNING: could not rank the items in Jira: {error}',
              file=env.stderr_file)
