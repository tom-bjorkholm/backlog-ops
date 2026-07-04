#! /usr/local/bin/python3
"""Tests for updating releases in Jira.

A stand-in Jira client answers the project-version query with fake version
resources that carry their current field values and record or refuse field
updates, so the matching by name, the diff-based update payload, the
already-correct detection, the empty-value no-op, the missing-name policies
(raise, ignore, add) and the never-mutated argument are checked without a
real server.
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
from backlogops.jira_write import ItemNotInJiraError, OnMissingKey
from backlogops.jira_update_releases import (
    UpdatedReleasesInJira, format_release_updates, update_releases_in_jira)
from backlogops.jira_write_releases import FailedRelease
from backlogops.releases import Release
from .jira_write_helpers import (
    FakeJiraClient as _UpdClient, attr_path as _attr,
    connections_for as _connections, jira_write_config as _config, NO)

_TWO_FIELD_MAP: JiraColumnMap = {'name': _attr('name'),
                                 'planned_date': _attr('releaseDate'),
                                 'estimated_date': _attr('startDate')}


def _upd(connections: JiraConnections, releases: list[Release],
         mode: OnMissingKey = OnMissingKey.RAISE,
         stderr: Optional[io.StringIO] = None) -> UpdatedReleasesInJira:
    """Update the releases with the given mode and diagnostics stream."""
    sink = NO if stderr is None else stderr
    return update_releases_in_jira(connections, 'w', releases,
                                   on_missing_key=mode, stderr_file=sink)


def test_update_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a matched version gets its release date from the planned date."""
    client = _UpdClient(existing=['R1'])
    connections = _connections(monkeypatch, client)
    result = _upd(connections, [Release('R1', date(2026, 6, 12))])
    assert result.updated == ['R1']
    assert not result.already_correct and not result.ignored
    assert not result.added and not result.failed
    assert client.versions['R1'].updated == {'releaseDate': '2026-06-12'}


def test_update_map_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test every mapped field except the name is written on update."""
    client = _UpdClient(existing=['R1'])
    connections = _connections(monkeypatch, client,
                               _config('P', _TWO_FIELD_MAP))
    _upd(connections, [Release('R1', date(2026, 6, 12), date(2026, 3, 4))])
    assert client.versions['R1'].updated == {'releaseDate': '2026-06-12',
                                             'startDate': '2026-03-04'}


def test_already_correct(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a version already holding the planned date is left unchanged."""
    client = _UpdClient(existing=['R1'],
                        current={'R1': {'releaseDate': '2026-06-12'}})
    connections = _connections(monkeypatch, client)
    result = _upd(connections, [Release('R1', date(2026, 6, 12))])
    assert result.already_correct == ['R1']
    assert not result.updated
    assert client.versions['R1'].updated == {}


def test_all_correct_multi(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a version holding every mapped value is already correct."""
    client = _UpdClient(existing=['R1'],
                        current={'R1': {'releaseDate': '2026-06-12',
                                        'startDate': '2026-03-04'}})
    connections = _connections(monkeypatch, client,
                               _config('P', _TWO_FIELD_MAP))
    result = _upd(connections,
                  [Release('R1', date(2026, 6, 12), date(2026, 3, 4))])
    assert result.already_correct == ['R1']
    assert not result.updated
    assert client.versions['R1'].updated == {}


def test_diff_only_written(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test only the differing mapped field is written on an update."""
    client = _UpdClient(existing=['R1'],
                        current={'R1': {'startDate': '2026-03-04'}})
    connections = _connections(monkeypatch, client,
                               _config('P', _TWO_FIELD_MAP))
    result = _upd(connections,
                  [Release('R1', date(2026, 6, 12), date(2026, 3, 4))])
    assert result.updated == ['R1']
    assert client.versions['R1'].updated == {'releaseDate': '2026-06-12'}


def test_empty_date_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a release with no planned date is already correct, not updated."""
    client = _UpdClient(existing=['R1'])
    connections = _connections(monkeypatch, client)
    result = _upd(connections, [Release('R1')])
    assert result.already_correct == ['R1']
    assert not result.updated
    assert client.versions['R1'].updated == {}


def test_missing_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing name raises before anything is changed."""
    client = _UpdClient(existing=['R1'])
    connections = _connections(monkeypatch, client)
    with pytest.raises(ItemNotInJiraError) as caught:
        _upd(connections, [Release('R1', date(2026, 1, 1)), Release('R2')])
    assert caught.value.names == ['R2']
    assert client.versions['R1'].updated == {}


def test_missing_ignore(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing name is ignored and no version is created."""
    client = _UpdClient(existing=['R1'])
    connections = _connections(monkeypatch, client)
    releases = [Release('R1', date(2026, 1, 1)), Release('R2')]
    result = _upd(connections, releases, OnMissingKey.IGNORE)
    assert result.updated == ['R1']
    assert result.ignored == ['R2']
    assert not client.created


def test_missing_add(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing name is created under the add policy."""
    client = _UpdClient(existing=['R1'])
    connections = _connections(monkeypatch, client)
    releases = [Release('R1', date(2026, 1, 1)),
                Release('R2', date(2026, 2, 2))]
    result = _upd(connections, releases, OnMissingKey.ADD)
    assert result.updated == ['R1']
    assert result.added == ['R2']
    assert client.created == [{'name': 'R2', 'project': 'PROJ',
                               'releaseDate': '2026-02-02'}]


def test_mixed_outcomes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test one release each of updated, already correct and added."""
    client = _UpdClient(existing=['R1', 'R2'],
                        current={'R2': {'releaseDate': '2026-02-02'}})
    connections = _connections(monkeypatch, client)
    releases = [Release('R1', date(2026, 1, 1)),
                Release('R2', date(2026, 2, 2)),
                Release('R3', date(2026, 3, 3))]
    result = _upd(connections, releases, OnMissingKey.ADD)
    assert result.updated == ['R1']
    assert result.already_correct == ['R2']
    assert result.added == ['R3']
    assert not result.ignored and not result.failed


def test_update_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused update is reported and the others still updated."""
    client = _UpdClient(existing=['R1', 'R2'], fail_update={'R1'})
    connections = _connections(monkeypatch, client)
    result = _upd(connections, [Release('R1', date(2026, 1, 1)),
                                Release('R2', date(2026, 2, 2))])
    assert result.updated == ['R2']
    assert [entry.release.name for entry in result.failed] == ['R1']
    assert 'HTTP 400' in result.failed[0].reason


def test_add_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused create under the add policy is reported."""
    client = _UpdClient(fail_create={'R1'})
    connections = _connections(monkeypatch, client)
    result = _upd(connections, [Release('R1', date(2026, 1, 1))],
                  OnMissingKey.ADD)
    assert not result.added
    assert [entry.release.name for entry in result.failed] == ['R1']


def test_skipped_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a target that is not a version field is skipped and reported.

    Nothing else is mapped, so the version is already correct, yet the
    misconfigured target is still warned about.
    """
    release_map: JiraColumnMap = {'name': _attr('name'),
                                  'planned_date': _attr('userReleaseDate')}
    client = _UpdClient(existing=['R1'])
    connections = _connections(monkeypatch, client, _config('P', release_map))
    errors = io.StringIO()
    result = _upd(connections, [Release('R1', date(2026, 1, 1))],
                  stderr=errors)
    assert result.already_correct == ['R1']
    assert not result.updated
    assert client.versions['R1'].updated == {}
    assert 'userReleaseDate' in errors.getvalue()


def test_input_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the argument releases are not modified by an update."""
    client = _UpdClient(existing=['R1'])
    connections = _connections(monkeypatch, client)
    release = Release('R1', date(2026, 1, 1))
    _upd(connections, [release])
    assert release.name == 'R1'
    assert release.planned_date == date(2026, 1, 1)


def test_format_updates() -> None:
    """Test the listing shows the five sections with their entries."""
    result = UpdatedReleasesInJira(
        updated=['R1'], already_correct=['R5'], ignored=['R2'], added=['R3'],
        failed=[FailedRelease(Release('R4'), 'HTTP 400: nope')])
    text = format_release_updates(result)
    assert 'Updated in Jira (1):' in text and '  R1' in text
    assert 'Already correct in Jira (1):' in text and '  R5' in text
    assert 'Not in Jira (ignored) (1):' in text and '  R2' in text
    assert 'Added to Jira (1):' in text and '  R3' in text
    assert 'Failed to update (1):' in text
    assert '  R4  - HTTP 400: nope' in text


def test_format_empty() -> None:
    """Test an empty section is shown as a count of zero and (none)."""
    text = format_release_updates(UpdatedReleasesInJira([], [], [], [], []))
    assert 'Updated in Jira (0):' in text
    assert 'Already correct in Jira (0):' in text
    assert 'Not in Jira (ignored) (0):' in text
    assert 'Added to Jira (0):' in text
    assert 'Failed to update (0):' in text
    assert '(none)' in text


def test_reexport() -> None:
    """Test the package re-exports the update-releases-in-Jira names."""
    assert backlogops.update_releases_in_jira is update_releases_in_jira
    assert backlogops.UpdatedReleasesInJira is UpdatedReleasesInJira
    assert backlogops.format_release_updates is format_release_updates
    assert backlogops.ItemNotInJiraError is ItemNotInJiraError
    assert backlogops.OnMissingKey is OnMissingKey
    assert 'update_releases_in_jira' in backlogops.__all__
    assert 'ItemNotInJiraError' in backlogops.__all__
