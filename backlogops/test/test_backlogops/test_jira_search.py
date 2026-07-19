#! /usr/local/bin/python3
"""Tests for paging a Jira issue search over large backlogs.

The paging is driven with stand-in clients cast to the Jira client type:
a Cloud client that hands out pages by next-page token and a server client
that hands out pages by offset. The tests check that every page is read,
that the paging state is threaded correctly and that progress is reported
only once a read spans more than one page.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from types import SimpleNamespace
from typing import Optional, cast
from jira import JIRA
from jira.client import ResultList
from jira.resources import Resource
from backlogops.jira_search import search_all_issues, _PAGE_SIZE


def _issues(count: int, start: int = 0) -> list[object]:
    """Return stand-in Jira issues with sequential keys."""
    return [SimpleNamespace(key=f'K-{index}')
            for index in range(start, start + count)]


def _keys(issues: list[object]) -> list[str]:
    """Return the keys of stand-in Jira issues."""
    return [str(getattr(issue, 'key')) for issue in issues]


# pylint: disable-next=too-few-public-methods
class _CloudClient:
    """A stand-in Cloud client handing out issue pages by page token."""

    def __init__(self, pages: list[list[object]]) -> None:
        """Store the pages to hand out and record the queries made."""
        self.pages = pages
        self.tokens: list[Optional[str]] = []
        self.fields_asked: list[object] = []

    def enhanced_search_issues(self, jql: str, *,
                               nextPageToken: Optional[str] = None,
                               fields: object = None,
                               **kwargs: object) -> ResultList[Resource]:
        """Return the page for the given token with the next token."""
        _ = jql, kwargs
        self.tokens.append(nextPageToken)
        self.fields_asked.append(fields)
        index = 0 if nextPageToken is None else int(nextPageToken)
        has_more = index + 1 < len(self.pages)
        token = str(index + 1) if has_more else None
        return ResultList[Resource](self.pages[index], _nextPageToken=token)


# pylint: disable-next=too-few-public-methods
class _ServerClient:
    """A stand-in server client handing out issue pages by offset."""

    def __init__(self, issues: list[object]) -> None:
        """Store all issues and record the offsets asked for."""
        self.issues = issues
        self.starts: list[int] = []

    def search_issues(self, jql: str, *, startAt: int = 0,
                      maxResults: int = 50,
                      **kwargs: object) -> ResultList[Resource]:
        """Return the offset page of issues as a result list."""
        _ = jql, kwargs
        self.starts.append(startAt)
        return ResultList[Resource](self.issues[startAt:startAt + maxResults])


def test_cloud_tokens() -> None:
    """Test token paging threads each next token into the next request."""
    pages = [_issues(2, 0), _issues(2, 2), _issues(1, 4)]
    fake = _CloudClient(pages)
    err = io.StringIO()
    result = search_all_issues(cast(JIRA, fake), True, 'jql', ['key'],
                               stderr_file=err)
    assert _keys(result) == [f'K-{index}' for index in range(5)]
    assert fake.tokens == [None, '1', '2']
    assert all(asked == ['key'] for asked in fake.fields_asked)


def test_no_progress_single() -> None:
    """Test a single-page read stays silent and returns the issues."""
    fake = _CloudClient([_issues(3, 0)])
    err = io.StringIO()
    result = search_all_issues(cast(JIRA, fake), True, 'jql', [],
                               stderr_file=err)
    assert len(result) == 3
    assert err.getvalue() == ''


def test_progress_multi_page() -> None:
    """Test a multi-page read reports the running count of each page."""
    pages = [_issues(2, 0), _issues(2, 2), _issues(2, 4)]
    err = io.StringIO()
    search_all_issues(cast(JIRA, _CloudClient(pages)), True, 'jql', [],
                      stderr_file=err)
    lines = err.getvalue().splitlines()
    assert len(lines) == 2
    assert '4 issues' in lines[0] and '6 issues' in lines[1]


def test_server_paging() -> None:
    """Test offset paging reads every page from a server backlog."""
    fake = _ServerClient(_issues(_PAGE_SIZE * 2 + 5))
    err = io.StringIO()
    result = search_all_issues(cast(JIRA, fake), False, 'jql', ['key'],
                               stderr_file=err)
    assert len(result) == _PAGE_SIZE * 2 + 5
    assert fake.starts == [0, _PAGE_SIZE, _PAGE_SIZE * 2]
    assert len(err.getvalue().splitlines()) == 2


def test_server_exact_page() -> None:
    """Test an exact multiple of the page size stops after an empty page."""
    fake = _ServerClient(_issues(_PAGE_SIZE))
    result = search_all_issues(cast(JIRA, fake), False, 'jql', ['key'],
                               stderr_file=io.StringIO())
    assert len(result) == _PAGE_SIZE
    assert fake.starts == [0, _PAGE_SIZE]
