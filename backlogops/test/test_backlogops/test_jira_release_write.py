#! /usr/local/bin/python3
"""Tests for adding releases to Jira.

A stand-in Jira client records the created version payloads and answers
the project-version query from a set of already-present names, so the
orchestration, the raise-before-write rule, the inverted release map, the
date conversion and the never-mutated argument are checked without a real
server.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
from typing import Optional
import pytest
import backlogops
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import JiraColumnMap
from backlogops.jira_write import OnExistingKey
from backlogops.jira_write_releases import (
    add_releases_to_jira, AddedReleasesToJira, FailedRelease,
    ReleaseExistsError, format_release_result)
from backlogops.releases import Release
from .jira_write_helpers import (
    FakeJiraClient as _RelClient, attr_path as _attr,
    connections_for as _connections, jira_write_config as _config, NO)


def _add(connections: JiraConnections, releases: list[Release],
         mode: OnExistingKey = OnExistingKey.SKIP,
         stderr: Optional[io.StringIO] = None) -> AddedReleasesToJira:
    """Add the releases with the given mode and diagnostics stream."""
    return add_releases_to_jira(connections, 'w', releases,
                                on_existing_key=mode,
                                stderr_file=NO if stderr is None else stderr)


def test_add_all_new(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test every release is created and copied when none are present."""
    client = _RelClient()
    connections = _connections(monkeypatch, client)
    releases = [Release('R1', date(2026, 1, 1)), Release('R2')]
    result = _add(connections, releases, OnExistingKey.RAISE)
    assert [rel.name for rel in result.stored] == ['R1', 'R2']
    assert not result.already_present
    assert not result.failed
    assert [rec['name'] for rec in client.created] == ['R1', 'R2']


def test_skip_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test present names are skipped and the rest are created."""
    client = _RelClient(existing=['R2'])
    connections = _connections(monkeypatch, client)
    releases = [Release('R1'), Release('R2'), Release('R3')]
    result = _add(connections, releases, OnExistingKey.SKIP)
    assert [rel.name for rel in result.stored] == ['R1', 'R3']
    assert [rel.name for rel in result.already_present] == ['R2']
    assert [rec['name'] for rec in client.created] == ['R1', 'R3']


def test_raise_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a present name raises before anything is created."""
    client = _RelClient(existing=['R2'])
    connections = _connections(monkeypatch, client)
    with pytest.raises(ReleaseExistsError) as caught:
        _add(connections, [Release('R1'), Release('R2')], OnExistingKey.RAISE)
    assert caught.value.names == ['R2']
    assert not client.created


def test_create_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the inverted release map builds the create-version payload."""
    client = _RelClient()
    connections = _connections(monkeypatch, client)
    _add(connections, [Release('R1', date(2026, 6, 12))])
    record = client.created[0]
    assert record == {'name': 'R1', 'project': 'PROJ',
                      'releaseDate': '2026-06-12'}


def test_no_planned_date(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a release without a planned date writes no release date."""
    client = _RelClient()
    connections = _connections(monkeypatch, client)
    _add(connections, [Release('R1')])
    assert client.created[0] == {'name': 'R1', 'project': 'PROJ'}


def test_estimated_via_map(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a map targeting startDate writes the estimated date as ISO."""
    release_map: JiraColumnMap = {'name': _attr('name'),
                                  'estimated_date': _attr('startDate')}
    client = _RelClient()
    connections = _connections(monkeypatch, client, _config('P', release_map))
    _add(connections, [Release('R1', estimated_date=date(2026, 3, 4))])
    assert client.created[0] == {'name': 'R1', 'project': 'P',
                                 'startDate': '2026-03-04'}


def test_skipped_field(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a target that is not a create field is skipped and reported."""
    release_map: JiraColumnMap = {'name': _attr('name'),
                                  'planned_date': _attr('userReleaseDate')}
    client = _RelClient()
    connections = _connections(monkeypatch, client, _config('P', release_map))
    errors = io.StringIO()
    _add(connections, [Release('R1', date(2026, 1, 1))], stderr=errors)
    assert client.created[0] == {'name': 'R1', 'project': 'P'}
    assert 'userReleaseDate' in errors.getvalue()


def test_input_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the stored copy is distinct and the argument is untouched."""
    client = _RelClient()
    connections = _connections(monkeypatch, client)
    release = Release('R1', date(2026, 1, 1))
    result = _add(connections, [release])
    stored = result.stored[0]
    stored.name = 'CHANGED'
    stored.planned_date = date(2030, 1, 1)
    assert release.name == 'R1'
    assert release.planned_date == date(2026, 1, 1)


def test_failed_continue(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused create is reported and the others still added."""
    client = _RelClient(fail_create={'R1'})
    connections = _connections(monkeypatch, client)
    result = _add(connections, [Release('R1'), Release('R2')])
    assert [rel.name for rel in result.stored] == ['R2']
    assert [entry.release.name for entry in result.failed] == ['R1']
    assert 'HTTP 400' in result.failed[0].reason


def test_empty_releases(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an empty release list adds nothing and creates no version."""
    client = _RelClient()
    connections = _connections(monkeypatch, client)
    result = _add(connections, [], OnExistingKey.RAISE)
    assert result == AddedReleasesToJira([], [], [])
    assert not client.created


def test_format_result() -> None:
    """Test the listing shows the added, present and failed sections."""
    result = AddedReleasesToJira(
        stored=[Release('R1', date(2026, 1, 1))],
        already_present=[Release('R2')],
        failed=[FailedRelease(Release('R3'), 'HTTP 400: nope')])
    text = format_release_result(result)
    assert 'Added to Jira (1):' in text
    assert '  R1  2026-01-01' in text
    assert 'Already in Jira (1):' in text
    assert '  R2' in text
    assert 'Failed to add (1):' in text
    assert '  R3  - HTTP 400: nope' in text


def test_format_empty() -> None:
    """Test an empty section is shown as a count of zero and (none)."""
    text = format_release_result(AddedReleasesToJira([], [], []))
    assert 'Added to Jira (0):' in text
    assert 'Already in Jira (0):' in text
    assert 'Failed to add (0):' in text
    assert '(none)' in text


def test_reexport() -> None:
    """Test the package re-exports the add-releases-to-Jira names."""
    assert backlogops.add_releases_to_jira is add_releases_to_jira
    assert backlogops.AddedReleasesToJira is AddedReleasesToJira
    assert backlogops.ReleaseExistsError is ReleaseExistsError
    assert backlogops.FailedRelease is FailedRelease
    assert 'add_releases_to_jira' in backlogops.__all__
    assert 'AddedReleasesToJira' in backlogops.__all__
