#! /usr/local/bin/python3
"""Shared stand-in Jira client for the ranking tests.

The raw ranking tests and the high-level move tests both drive a Jira
client that holds a global rank order, moves an issue with ``rank`` and
reads the order back with ``search_issues``. This one stand-in lives here
so both test modules share it rather than duplicating it. Its ``rank`` can
silently drop the first few moves, to mimic the Jira ranking forgetting an
early constraint, so a test can exercise the read-verify loop.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import NamedTuple, Optional, Sequence
from jira import JIRAError


class RankIssue(NamedTuple):
    """A stand-in issue carrying only the key the ranking reads."""

    key: str


def _keys_in_jql(jql: str) -> set[str]:
    """Return the keys named in an ``issueKey in (...)`` filter."""
    inside = jql[jql.index('(') + 1:jql.index(')')]
    return {part.strip() for part in inside.split(',')}


class FakeRankClient:
    """A stand-in Jira client holding and reordering a global rank order.

    The client keeps the keys in their current rank order and moves one key
    before or after another on ``rank``. ``search_issues`` reads back the
    order of the keys named in the filter. The first ``drop_ranks`` moves
    are silently ignored, to mimic the Jira ranking losing an early write,
    so a test can drive the read-verify loop over more than one pass.
    """

    def __init__(self, order: Sequence[str], *,
                 exist: Optional[Sequence[str]] = None,
                 drop_ranks: int = 0) -> None:
        """Start with the rank order, the existing keys and the drop count."""
        self.order = list(order)
        self._exist = set(order if exist is None else exist)
        self._drop = drop_ranks
        self.rank_calls: list[tuple[str, Optional[str], Optional[str]]] = []

    def myself(self) -> dict[str, str]:
        """Return a truthy value so the connection counts as alive."""
        return {}

    def issue(self, key: str) -> RankIssue:
        """Return the issue, or raise as Jira does for an unknown key."""
        if key not in self._exist:
            raise JIRAError(status_code=404, text=f'no issue {key}')
        return RankIssue(key)

    def search_issues(self, jql: str, **kwargs: object) -> list[RankIssue]:
        """Return the named keys in rank order, raising for an unknown key."""
        _ = kwargs
        wanted = _keys_in_jql(jql)
        missing = [key for key in wanted if key not in self._exist]
        if missing:
            raise JIRAError(status_code=400, text=f'no issue {missing[0]}')
        return [RankIssue(key) for key in self.order if key in wanted]

    def rank(self, issue: str, next_issue: Optional[str] = None,
             prev_issue: Optional[str] = None) -> None:
        """Move the issue before next_issue or after prev_issue in order."""
        self.rank_calls.append((issue, next_issue, prev_issue))
        if self._drop > 0:
            self._drop -= 1
            return
        self.order.remove(issue)
        if next_issue is not None:
            self.order.insert(self.order.index(next_issue), issue)
        else:
            assert prev_issue is not None
            self.order.insert(self.order.index(prev_issue) + 1, issue)
