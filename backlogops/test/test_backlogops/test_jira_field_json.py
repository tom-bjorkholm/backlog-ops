#! /usr/local/bin/python3
"""Tests for looking up the raw Jira JSON of an issue's fields.

A stand-in Jira client returns one issue's raw fields, the field list and
the edit screen, so a field id, a dotted path, a list index, a custom
field display name and a missing path are resolved without a server.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from types import SimpleNamespace
from typing import Optional
import pytest
import backlogops
from backlogops.jira_field_json import JiraFieldJson, jira_field_json
from .jira_write_helpers import connections_for

RAW: dict[str, object] = {
    'timetracking': {'remainingEstimate': '6h 7m',
                     'remainingEstimateSeconds': 22020},
    'timeestimate': 22020,
    'fixVersions': [{'name': 'R1'}, {'name': 'R2'}],
    'customfield_10016': 5.0,
    'customfield_10020': 'dotted'}
"""The raw fields of the stand-in issue, as Jira returns them."""

EDIT_TT: dict[str, object] = {'name': 'Time tracking',
                              'operations': ['set', 'edit']}
"""The stand-in edit screen entry of the time tracking field."""


class _JsonClient:
    """A stand-in Jira client returning one issue's raw JSON."""

    def __init__(self) -> None:
        """Start with no issue fetched yet."""
        self.fetched: list[str] = []

    def myself(self) -> dict[str, str]:
        """Report a live session for the connection pool."""
        return {'name': 'tester'}

    def fields(self) -> list[dict[str, str]]:
        """Return the field list resolving the custom field names."""
        return [{'id': 'customfield_10016', 'name': 'Story point estimate'},
                {'id': 'customfield_10020', 'name': 'Odd.name'}]

    def issue(self, key: str) -> SimpleNamespace:
        """Return the issue carrying its raw fields."""
        self.fetched.append(key)
        return SimpleNamespace(raw={'key': key, 'fields': RAW})

    def editmeta(self, key: str) -> dict[str, object]:
        """Return the edit screen, offering only the time tracking."""
        _ = key
        return {'fields': {'timetracking': EDIT_TT}}

    def close(self) -> None:
        """Ignore a close of the stand-in client."""


def _lookup(monkeypatch: pytest.MonkeyPatch, names: list[str],
            client: Optional[_JsonClient] = None) -> list[JiraFieldJson]:
    """Look the names up in the stand-in issue ``K-1``."""
    chosen = _JsonClient() if client is None else client
    return jira_field_json(connections_for(monkeypatch, chosen), 'w', 'K-1',
                           names)


@pytest.mark.parametrize('name, field_id, value', [
    ('timetracking.remainingEstimateSeconds', 'timetracking', 22020),
    ('timetracking', 'timetracking', RAW['timetracking']),
    ('timeestimate', 'timeestimate', 22020),
    ('fixVersions.1.name', 'fixVersions', 'R2'),
    ('Story point estimate', 'customfield_10016', 5.0),
    ('Odd.name', 'customfield_10020', 'dotted'),
    ('customfield_10016', 'customfield_10016', 5.0)])
def test_found(monkeypatch: pytest.MonkeyPatch, name: str, field_id: str,
               value: object) -> None:
    """Test a field id, dotted path, index and display name resolve."""
    found = _lookup(monkeypatch, [name])[0]
    assert (found.name, found.field_id, found.present, found.value) == \
        (name, field_id, True, value)


@pytest.mark.parametrize('name', [
    'timetracking.raw', 'fixVersions.2.name', 'fixVersions.x',
    'timeestimate.seconds', 'nosuchfield'])
def test_missing(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    """Test a path step naming no key or index is reported not present."""
    found = _lookup(monkeypatch, [name])[0]
    assert not found.present and found.value is None


def test_edit_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the root field's edit entry is given, or None if not offered."""
    found = _lookup(monkeypatch, ['timetracking.remainingEstimate',
                                  'timeestimate'])
    assert found[0].edit_entry == EDIT_TT
    assert found[1].edit_entry is None


def test_order_one_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test results follow the names and the issue is fetched once."""
    client = _JsonClient()
    found = _lookup(monkeypatch, ['timeestimate', 'fixVersions'], client)
    assert [item.name for item in found] == ['timeestimate', 'fixVersions']
    assert client.fetched == ['K-1']


def test_no_names(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test no names give no results and fetch nothing from Jira."""
    client = _JsonClient()
    assert not _lookup(monkeypatch, [], client)
    assert not client.fetched


def test_exported() -> None:
    """Test the lookup and its result are exported by the package."""
    assert backlogops.jira_field_json is jira_field_json
    assert backlogops.JiraFieldJson is JiraFieldJson
