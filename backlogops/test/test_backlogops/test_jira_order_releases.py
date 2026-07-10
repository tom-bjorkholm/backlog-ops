#! /usr/local/bin/python3
"""Tests for ordering releases in Jira.

A stand-in Jira client answers the project-version query with fake version
resources and records each move, so ordering to a name list, the trailing of
unlisted versions, the not-in-Jira reporting, the already-ordered no-op, the
duplicate-name collapse and ordering by release date (undated last, stable)
are all checked without a real server.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Sequence
import pytest
import backlogops
from backlogops.jira_connect import JiraConnections
from backlogops.jira_order_releases import (
    OrderedReleasesInJira, format_order_result, order_jira_rel_by_date,
    order_releases_in_jira)
from .jira_write_helpers import (
    FakeJiraClient as _Client, connections_for as _connections, NO)


def _order(connections: JiraConnections,
           names: Sequence[str]) -> OrderedReleasesInJira:
    """Order the releases to a name list through the preset ``'w'``."""
    return order_releases_in_jira(connections, 'w', names, stderr_file=NO)


def _current(client: _Client) -> list[str]:
    """Return the current version-name order of the fake client."""
    return [version.name for version in client.project_versions('P')]


def _dated(*pairs: tuple[str, str]) -> dict[str, dict[str, object]]:
    """Return a current-fields map giving each name a release date."""
    return {name: {'releaseDate': date} for name, date in pairs}


def test_order_by_names(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the named versions are moved to the front in the listed order."""
    client = _Client(existing=['R3', 'R1', 'R2'])
    connections = _connections(monkeypatch, client)
    result = _order(connections, ['R1', 'R2'])
    assert result.ordered == ['R1', 'R2'] and not result.not_in_jira
    assert _current(client) == ['R1', 'R2', 'R3']


def test_order_not_in_jira(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a name that is not a version is reported and not ordered."""
    client = _Client(existing=['R1', 'R2'])
    connections = _connections(monkeypatch, client)
    result = _order(connections, ['R1', 'RX'])
    assert result.ordered == ['R1'] and result.not_in_jira == ['RX']


def test_order_dedup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a repeated name is used only once, keeping the first place."""
    client = _Client(existing=['R1', 'R2'])
    connections = _connections(monkeypatch, client)
    result = _order(connections, ['R2', 'R2', 'R1'])
    assert result.ordered == ['R2', 'R1']
    assert _current(client) == ['R2', 'R1']


def test_already_ordered(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test nothing is moved when the versions already lead in order."""
    client = _Client(existing=['R1', 'R2', 'R3'])
    connections = _connections(monkeypatch, client)
    result = _order(connections, ['R1', 'R2'])
    assert result.ordered == ['R1', 'R2']
    assert not client.moves


def test_order_all_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test naming only absent versions orders nothing and reports them."""
    client = _Client(existing=['R1'])
    connections = _connections(monkeypatch, client)
    result = _order(connections, ['RX', 'RY'])
    assert result.ordered == [] and result.not_in_jira == ['RX', 'RY']
    assert not client.moves


def test_by_date_bad_date(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a version with an invalid release date is placed last."""
    client = _Client(existing=['R1', 'R2'],
                     current=_dated(('R1', 'not-a-date'),
                                    ('R2', '2026-01-01')))
    connections = _connections(monkeypatch, client)
    result = order_jira_rel_by_date(connections, 'w', stderr_file=NO)
    assert result.ordered == ['R2', 'R1']


def test_by_date(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test ordering by release date puts the earliest first, undated last."""
    client = _Client(existing=['R1', 'R2', 'R3'],
                     current=_dated(('R1', '2026-06-12'),
                                    ('R3', '2026-03-01')))
    connections = _connections(monkeypatch, client)
    result = order_jira_rel_by_date(connections, 'w', stderr_file=NO)
    assert result.ordered == ['R3', 'R1', 'R2'] and not result.not_in_jira
    assert _current(client) == ['R3', 'R1', 'R2']


def test_by_date_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test undated versions keep their relative order after the dated one."""
    client = _Client(existing=['A', 'B', 'C'],
                     current=_dated(('C', '2026-01-01')))
    connections = _connections(monkeypatch, client)
    result = order_jira_rel_by_date(connections, 'w', stderr_file=NO)
    assert result.ordered == ['C', 'A', 'B']
    assert _current(client) == ['C', 'A', 'B']


def test_by_date_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test already date-ordered versions are not moved."""
    client = _Client(existing=['R3', 'R1'],
                     current=_dated(('R3', '2026-03-01'),
                                    ('R1', '2026-06-12')))
    connections = _connections(monkeypatch, client)
    result = order_jira_rel_by_date(connections, 'w', stderr_file=NO)
    assert result.ordered == ['R3', 'R1']
    assert not client.moves


def test_format_order() -> None:
    """Test the listing shows the ordered and not-in-Jira sections."""
    result = OrderedReleasesInJira(ordered=['R1', 'R2'], not_in_jira=['RX'])
    text = format_order_result(result)
    assert 'Ordered in Jira (2):' in text and '  R1' in text and '  R2' in text
    assert 'Not in Jira (1):' in text and '  RX' in text


def test_format_empty() -> None:
    """Test an empty section is shown as a count of zero and (none)."""
    text = format_order_result(OrderedReleasesInJira([], []))
    assert 'Ordered in Jira (0):' in text
    assert 'Not in Jira (0):' in text
    assert '(none)' in text


def test_reexport() -> None:
    """Test the package re-exports the order-releases-in-Jira names."""
    assert backlogops.order_releases_in_jira is order_releases_in_jira
    assert backlogops.order_jira_rel_by_date is order_jira_rel_by_date
    assert backlogops.OrderedReleasesInJira is OrderedReleasesInJira
    assert backlogops.format_order_result is format_order_result
    assert 'order_releases_in_jira' in backlogops.__all__
    assert 'order_jira_rel_by_date' in backlogops.__all__
