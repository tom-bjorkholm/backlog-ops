#! /usr/local/bin/python3
"""Rank issues in Jira into the relative order of a key list.

This is the low-level primitive under
:func:`backlogops.jira_rank_move_keys.jira_rank_move_keys`. Given the keys
in the wanted relative order, it drives the Jira ranking so that those
issues end up in that order relative to each other, using the Jira client's
``rank`` call. A ``rank`` call places one issue immediately before or after
another, so the order is built by ranking each key next to its neighbour.

The Jira ranking is eventually consistent and can, after moving several
issues, forget an ordering constraint set earlier. So the wanted order is
enforced in a read-verify loop: a deterministic chaining pass is applied,
the current order is read back from Jira, and the pass is repeated until the
read order matches the wanted order. The loop is bounded, and a run that
does not converge raises :class:`JiraTooManyLoops` rather than looping
forever.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional, Sequence
from jira import JIRA, JIRAError
from backlogops.jira_connect import JiraConnections


class JiraKeyError(KeyError):
    """Exception raised when an issue key is not found in Jira."""

    def __init__(self, key_name: str, *, connection_name: Optional[str] = None,
                 message: Optional[str] = None) -> None:
        """Store the key and connection and build the error message."""
        self.key_name = key_name
        self.connection_name = connection_name
        text = f'{message}. ' if message is not None else ''
        text += f'Jira key "{key_name}" not found'
        text += (f' in connection "{connection_name}".'
                 if connection_name is not None else '.')
        super().__init__(text)


class JiraTooManyLoops(RuntimeError):
    """Exception raised when a Jira ranking does not converge in time.

    The wanted order is enforced in a bounded read-verify loop. When the
    order read back from Jira still does not match the wanted order after
    the last allowed loop, this exception is raised instead of looping
    forever.
    """

    def __init__(self, max_loops: int, *,
                 connection_name: Optional[str] = None,
                 message: Optional[str] = None) -> None:
        """Store the loop count and connection and build the message."""
        self.max_loops = max_loops
        self.connection_name = connection_name
        text = f'{message}. ' if message is not None else ''
        text += f'Too many loops ({max_loops}) performed'
        text += (f' in connection "{connection_name}".'
                 if connection_name is not None else '.')
        super().__init__(text)


def _raise_for_missing(client: JIRA, keys: Sequence[str],
                       connection_name: str) -> None:
    """Raise JiraKeyError for the first key that is absent from Jira."""
    for key in keys:
        try:
            client.issue(key)
        except JIRAError:
            raise JiraKeyError(key, connection_name=connection_name) from None


def _order_in_jira(client: JIRA, keys: Sequence[str],
                   connection_name: str) -> list[str]:
    """Return the current rank order of the given keys, read from Jira.

    The keys are searched with an ``ORDER BY Rank ASC`` filter, so the
    result lists exactly those keys in their current rank order.

    Raises:
        JiraKeyError: If a key is not present in Jira.
    """
    jql = 'issueKey in (' + ', '.join(keys) + ') ORDER BY Rank ASC'
    try:
        issues = client.search_issues(jql, maxResults=False, fields='key')
    except JIRAError:
        _raise_for_missing(client, keys, connection_name)
        raise
    wanted = set(keys)
    order = [issue.key for issue in issues if issue.key in wanted]
    if len(order) != len(wanted):
        missing = next(key for key in keys if key not in set(order))
        raise JiraKeyError(missing, connection_name=connection_name)
    return order


def _chain_pass(client: JIRA, keys: Sequence[str], move_before: bool) -> None:
    """Rank each key next to its neighbour to build the wanted order.

    When ``move_before`` is True each key is ranked before the next key,
    working from the second last key to the first, so the last key stays
    put and the block ends up just before it. When it is False each key is
    ranked after the previous key, working from the second key to the last,
    so the first key stays put and the block ends up just after it.
    """
    if move_before:
        for index in range(len(keys) - 2, -1, -1):
            client.rank(keys[index], next_issue=keys[index + 1])
    else:
        for index in range(1, len(keys)):
            client.rank(keys[index], prev_issue=keys[index - 1])


def jira_rank_by_keys_raw(connections: JiraConnections, connection_name: str,
                          issue_keys: Sequence[str], *,
                          move_before: bool = True) -> None:
    """Rank issues in Jira into the relative order of a key list.

    The issues named by ``issue_keys`` are ranked in Jira so that they end
    up in the given order relative to each other. Only these issues are
    moved; issues not in the list are moved only as a side effect of an
    insertion. Parent and child relations and dependencies are not
    considered here; the caller supplies the final wanted order.

    ``move_before`` selects which key of the list stays put and thereby
    where the block lands relative to issues that are not in the list. When
    True each key is ranked before the next one, so the last key stays put
    and the block ends up just before it. When False each key is ranked
    after the previous one, so the first key stays put and the block ends
    up just after it.

    The order is enforced in a bounded read-verify loop, because the Jira
    ranking can forget an earlier constraint after later moves: a chaining
    pass is applied, the order is read back, and the pass is repeated until
    the read order matches or the loop limit is reached. A list of fewer
    than two keys needs no ranking and returns at once.

    Args:
        connections: The pool of live Jira clients.
        connection_name: The name of the connection to rank in.
        issue_keys: The issue keys in the wanted relative order. The keys
            must be unique.
        move_before: Whether to rank each key before the next one (True) or
            after the previous one (False), as described above.

    Raises:
        KeyError: If the configuration has no such connection.
        JiraKeyError: If an issue key is not present in Jira.
        JiraTooManyLoops: If the ranking does not converge within the loop
            limit.
        JIRAError: If a Jira ranking call fails.
    """
    keys = list(issue_keys)
    if len(keys) < 2:
        return
    client = connections.client(connection_name)
    max_loops = 2 * len(keys)
    for attempt in range(max_loops + 1):
        if _order_in_jira(client, keys, connection_name) == keys:
            return
        if attempt == max_loops:
            raise JiraTooManyLoops(max_loops, connection_name=connection_name)
        _chain_pass(client, keys, move_before)
