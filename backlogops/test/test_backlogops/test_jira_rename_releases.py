#! /usr/local/bin/python3
"""Tests for renaming releases in Jira.

A stand-in Jira client answers the project-version query with fake version
resources that record or refuse a name update, so matching by the old name,
the collision and missing checks, the unchanged no-op, the reuse of a freed
name within a batch, a refused rename, the single-rename wrapper and the
never-mutated argument are all checked without a real server.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Sequence
import pytest
import backlogops
from backlogops.jira_connect import JiraConnections
from backlogops.jira_rename_releases import (
    FailedRename, ReleaseRename, RenamedReleasesInJira, format_rename_result,
    rename_release_in_jira, rename_releases_in_jira)
from .jira_write_helpers import (
    FakeJiraClient as _Client, connections_for as _connections, NO)


def _rename(connections: JiraConnections,
            renames: Sequence[ReleaseRename]) -> RenamedReleasesInJira:
    """Rename the releases through the preset ``'w'`` without diagnostics."""
    return rename_releases_in_jira(connections, 'w', renames, stderr_file=NO)


def test_rename_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a matched version has its name updated to the new name."""
    client = _Client(existing=['R1', 'R2'])
    connections = _connections(monkeypatch, client)
    result = _rename(connections, [ReleaseRename('R1', 'R9')])
    assert result.renamed == [ReleaseRename('R1', 'R9')]
    assert not result.missing and not result.collisions
    assert client.versions['R1'].updated == {'name': 'R9'}


def test_rename_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an old name that is not a version is reported as missing."""
    client = _Client(existing=['R1'])
    connections = _connections(monkeypatch, client)
    result = _rename(connections, [ReleaseRename('RX', 'R9')])
    assert result.missing == ['RX']
    assert not result.renamed
    assert client.versions['R1'].updated == {}


def test_rename_collision(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a new name that is already a version is a collision."""
    client = _Client(existing=['R1', 'R2'])
    connections = _connections(monkeypatch, client)
    result = _rename(connections, [ReleaseRename('R1', 'R2')])
    assert result.collisions == [ReleaseRename('R1', 'R2')]
    assert not result.renamed
    assert client.versions['R1'].updated == {}


def test_rename_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a new name equal to the old name is an unchanged no-op."""
    client = _Client(existing=['R1'])
    connections = _connections(monkeypatch, client)
    result = _rename(connections, [ReleaseRename('R1', 'R1')])
    assert result.unchanged == ['R1']
    assert not result.renamed
    assert client.versions['R1'].updated == {}


def test_batch_dup_target(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test two renames to the same new name make the second a collision."""
    client = _Client(existing=['R1', 'R2'])
    connections = _connections(monkeypatch, client)
    result = _rename(connections, [ReleaseRename('R1', 'X'),
                                   ReleaseRename('R2', 'X')])
    assert result.renamed == [ReleaseRename('R1', 'X')]
    assert result.collisions == [ReleaseRename('R2', 'X')]


def test_reuse_freed_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a rename may take a name freed by an earlier rename."""
    client = _Client(existing=['R1', 'R2'])
    connections = _connections(monkeypatch, client)
    result = _rename(connections, [ReleaseRename('R1', 'R1new'),
                                   ReleaseRename('R2', 'R1')])
    assert result.renamed == [ReleaseRename('R1', 'R1new'),
                              ReleaseRename('R2', 'R1')]
    assert not result.collisions


def test_rename_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused rename is reported and the others still applied."""
    client = _Client(existing=['R1', 'R2'], fail_update={'R1'})
    connections = _connections(monkeypatch, client)
    result = _rename(connections, [ReleaseRename('R1', 'R9'),
                                   ReleaseRename('R2', 'R8')])
    assert result.renamed == [ReleaseRename('R2', 'R8')]
    assert [entry.rename for entry in result.failed] == \
        [ReleaseRename('R1', 'R9')]
    assert 'HTTP 400' in result.failed[0].reason


def test_single_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the single-rename function classifies one rename."""
    client = _Client(existing=['R1'])
    connections = _connections(monkeypatch, client)
    result = rename_release_in_jira(connections, 'w', 'R1', 'R9',
                                    stderr_file=NO)
    assert result.renamed == [ReleaseRename('R1', 'R9')]
    assert client.versions['R1'].updated == {'name': 'R9'}


def test_input_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the argument renames sequence is not modified."""
    client = _Client(existing=['R1'])
    connections = _connections(monkeypatch, client)
    renames = [ReleaseRename('R1', 'R9')]
    _rename(connections, renames)
    assert renames == [ReleaseRename('R1', 'R9')]


def test_format_rename() -> None:
    """Test the listing shows the five sections with their entries."""
    result = RenamedReleasesInJira(
        renamed=[ReleaseRename('R1', 'R9')], unchanged=['R5'], missing=['RX'],
        collisions=[ReleaseRename('R2', 'R3')],
        failed=[FailedRename(ReleaseRename('R4', 'R7'), 'HTTP 400: nope')])
    text = format_rename_result(result)
    assert 'Renamed in Jira (1):' in text and '  R1 -> R9' in text
    assert 'Unchanged (new name equals old) (1):' in text and '  R5' in text
    assert 'Old name not in Jira (1):' in text and '  RX' in text
    assert 'New name already in use (1):' in text and '  R2 -> R3' in text
    assert 'Failed to rename (1):' in text
    assert '  R4 -> R7  - HTTP 400: nope' in text


def test_format_empty() -> None:
    """Test an empty section is shown as a count of zero and (none)."""
    text = format_rename_result(RenamedReleasesInJira([], [], [], [], []))
    assert 'Renamed in Jira (0):' in text
    assert 'Failed to rename (0):' in text
    assert '(none)' in text


def test_reexport() -> None:
    """Test the package re-exports the rename-releases-in-Jira names."""
    assert backlogops.rename_releases_in_jira is rename_releases_in_jira
    assert backlogops.rename_release_in_jira is rename_release_in_jira
    assert backlogops.ReleaseRename is ReleaseRename
    assert backlogops.RenamedReleasesInJira is RenamedReleasesInJira
    assert backlogops.format_rename_result is format_rename_result
    assert 'rename_releases_in_jira' in backlogops.__all__
    assert 'ReleaseRename' in backlogops.__all__
