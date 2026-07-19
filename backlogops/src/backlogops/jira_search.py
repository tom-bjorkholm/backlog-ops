#! /usr/local/bin/python3
"""Read every issue of a Jira search, paging over large backlogs.

Jira returns the issues matching a Jira Query Language filter in pages, so
a backlog of many thousands of issues arrives over many requests.
:func:`search_all_issues` reads every page and returns all the issues. A
Cloud connection is paged with the token-based search endpoint and a
server connection with the offset-based one, chosen by the ``is_cloud``
flag the caller already knows from the Jira connection configuration.
Progress is reported once a read spans more than one page, so a small read
stays silent while a large read shows that it is making progress.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from collections.abc import Iterator, Sequence
from typing import Optional, TextIO
from jira import JIRA, Issue
from jira.client import ResultList

_PAGE_SIZE = 100
"""Number of issues fetched per Jira search request."""


def _report_progress(count: int, stderr_file: TextIO) -> None:
    """Report how many issues a multi-page read has fetched so far."""
    print(f'... read {count} issues from Jira so far.', file=stderr_file)


def _cloud_pages(client: JIRA, jql: str,
                 fields: Sequence[str]) -> Iterator[ResultList[Issue]]:
    """Yield issue pages from Cloud Jira using token-based paging.

    A fresh copy of the field list is passed on each request because the
    client translates the field names in place.
    """
    search = client.enhanced_search_issues
    token: Optional[str] = None
    while True:
        result = search(jql, nextPageToken=token, maxResults=_PAGE_SIZE,
                        fields=list(fields))
        assert isinstance(result, ResultList)
        yield result
        token = result.nextPageToken
        if not token or not result:
            return


def _server_pages(client: JIRA, jql: str,
                  fields: Sequence[str]) -> Iterator[ResultList[Issue]]:
    """Yield issue pages from a Jira server using offset-based paging."""
    start = 0
    while True:
        result = client.search_issues(jql, startAt=start,
                                      maxResults=_PAGE_SIZE,
                                      fields=list(fields))
        assert isinstance(result, ResultList)
        yield result
        start += len(result)
        if len(result) < _PAGE_SIZE:
            return


def search_all_issues(client: JIRA, is_cloud: bool, jql: str,
                      fields: Sequence[str], *,
                      stderr_file: TextIO = sys.stderr) -> list[object]:
    """Return every issue matching a filter, reading all pages.

    Args:
        client: The live Jira client to search with.
        is_cloud: Whether the connection is a Cloud connection, so the
            token-based search endpoint is used instead of the offset one.
        jql: The Jira Query Language filter to run.
        fields: The Jira field ids to fetch for each issue.
        stderr_file: Stream used for progress messages.

    Returns:
        The issues matching the filter, read from every page.
    """
    pages = _cloud_pages if is_cloud else _server_pages
    issues: list[object] = []
    for index, page in enumerate(pages(client, jql, fields)):
        issues.extend(page)
        if index and page:
            _report_progress(len(issues), stderr_file)
    return issues
