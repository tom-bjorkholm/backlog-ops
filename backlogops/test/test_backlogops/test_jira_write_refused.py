#! /usr/local/bin/python3
"""Tests for what Jira refuses while a backlog is added.

Creating an issue is the only step that may fail an item: once Jira has
created it, the assigned key must survive whatever Jira refuses next. A
stand-in Jira client that refuses named field values, or refuses to show
an edit screen, checks that the item is still stored under its new key,
that a refused update is retried one field at a time so the accepted
values are kept, and that the refusals are collected and reported. The
same client answers for the project's versions, so the warning for a
release the project does not have as a version is checked too.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
import pytest
from jira import JIRAError
from backlogops.backlog import BacklogItem, Status
from backlogops.jira_write import add_backlog_to_jira, OnExistingKey
from .jira_write_helpers import (
    connections_for as _connections, leveled_item as _leveled, NO,
    title_only_config as _title_only_config, WriteClient as _WriteClient)


def _released(key: str, release: str = 'R1') -> BacklogItem:
    """Return a story in a release, with story points and no extra fields."""
    return BacklogItem(key=key, level=1, title=f'T {key}', story_points=5,
                       status=Status.TODO, release=release)


def test_refused_field_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused field value does not cost the item its new issue.

    Jira has created the issue by the time it refuses the value, so the
    item is stored with the key Jira assigned and only the value is lost.
    """
    client = _WriteClient()
    client.behavior.fail_fields = {'fixVersions'}
    connections = _connections(monkeypatch, client)
    result = add_backlog_to_jira(connections, 'w', [_released('A')],
                                 on_existing_key=OnExistingKey.SKIP,
                                 stderr_file=NO)
    assert [item.key for item in result.stored] == ['JIRA-1']
    assert result.key_map == {'A': 'JIRA-1'}
    assert not result.failed
    assert [bad.field for bad in result.failed_fields] == ['fixVersions']
    assert 'HTTP 400' in result.failed_fields[0].reason


def test_refused_field_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the fields Jira accepts are still set after a refused update.

    Jira applies an update as a whole, so the refused update is retried
    one field at a time and only the refused value is lost.
    """
    client = _WriteClient()
    client.behavior.fail_fields = {'fixVersions'}
    connections = _connections(monkeypatch, client)
    result = add_backlog_to_jira(connections, 'w', [_released('A')],
                                 on_existing_key=OnExistingKey.SKIP,
                                 stderr_file=NO)
    assert client.created[0]['customfield_10016'] == 5
    assert 'fixVersions' not in client.created[0]
    assert len(client.link_log.refused) == 2
    assert [bad.field for bad in result.failed_fields] == ['fixVersions']


def test_refused_only_field(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a single refused field is not retried on its own again."""
    client = _WriteClient()
    client.behavior.fail_fields = {'fixVersions'}
    connections = _connections(monkeypatch, client)
    item = _released('A')
    item.story_points = None
    result = add_backlog_to_jira(connections, 'w', [item],
                                 on_existing_key=OnExistingKey.SKIP,
                                 stderr_file=NO)
    assert len(client.link_log.refused) == 1
    assert [bad.field for bad in result.failed_fields] == ['fixVersions']


def test_refused_field_warned(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a refused custom field is warned about by its display name."""
    client = _WriteClient()
    client.behavior.fail_fields = {'customfield_10016'}
    connections = _connections(monkeypatch, client)
    errors = io.StringIO()
    result = add_backlog_to_jira(connections, 'w', [_released('A')],
                                 on_existing_key=OnExistingKey.SKIP,
                                 stderr_file=errors)
    text = errors.getvalue()
    assert 'JIRA-1' in text and 'was not set' in text
    assert 'customfield_10016 (Story point estimate)' in text
    assert result.failed_fields[0].field == \
        'customfield_10016 (Story point estimate)'


def test_no_edit_screen(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an unreadable edit screen keeps the issue and refuses fields."""
    client = _WriteClient()
    client.behavior.fail_editmeta = True
    connections = _connections(monkeypatch, client)
    result = add_backlog_to_jira(connections, 'w', [_released('A')],
                                 on_existing_key=OnExistingKey.SKIP,
                                 stderr_file=NO)
    assert [item.key for item in result.stored] == ['JIRA-1']
    assert not result.failed
    assert sorted(bad.field for bad in result.failed_fields) == \
        ['customfield_10016 (Story point estimate)', 'fixVersions']


def test_refused_parent_link(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a child still links to a parent whose field value was refused.

    The parent keeps the key Jira assigned, so the child's parent link is
    written to that key instead of to the internal key.
    """
    client = _WriteClient()
    client.behavior.fail_fields = {'fixVersions'}
    connections = _connections(monkeypatch, client)
    parent = _released('P')
    parent.level = 2
    result = add_backlog_to_jira(connections, 'w',
                                 [_leveled('C', 1, 'P'), parent],
                                 on_existing_key=OnExistingKey.SKIP,
                                 stderr_file=NO)
    assert result.key_map == {'C': 'JIRA-1', 'P': 'JIRA-2'}
    assert ('JIRA-1', {'parent': {'key': 'JIRA-2'}}) in client.link_log.updates
    assert not result.failed_links


def test_unknown_release_warn(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a release that is no version of the project is reported."""
    client = _WriteClient()
    connections = _connections(monkeypatch, client)
    errors = io.StringIO()
    add_backlog_to_jira(connections, 'w', [_released('A', 'Next')],
                        on_existing_key=OnExistingKey.SKIP, stderr_file=errors)
    text = errors.getvalue()
    assert 'not a version of Jira project PROJ: Next' in text


def test_known_release_quiet(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a release the project has as a version is not reported."""
    client = _WriteClient()
    connections = _connections(monkeypatch, client)
    errors = io.StringIO()
    add_backlog_to_jira(connections, 'w', [_released('A')],
                        on_existing_key=OnExistingKey.SKIP, stderr_file=errors)
    assert 'not a version' not in errors.getvalue()


def test_versions_unreadable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test releases are not reported when the versions cannot be read."""
    client = _WriteClient()

    def refuse(project: str) -> list[object]:
        """Refuse to list the project's versions, as Jira may."""
        raise JIRAError(status_code=403, text=f'no versions of {project}')
    monkeypatch.setattr(client, 'project_versions', refuse)
    connections = _connections(monkeypatch, client)
    errors = io.StringIO()
    add_backlog_to_jira(connections, 'w', [_released('A', 'Next')],
                        on_existing_key=OnExistingKey.SKIP, stderr_file=errors)
    assert 'not a version' not in errors.getvalue()


def test_release_unmapped(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an unmapped release is not reported, as it is never written."""
    client = _WriteClient()
    connections = _connections(monkeypatch, client, _title_only_config())
    errors = io.StringIO()
    add_backlog_to_jira(connections, 'w', [_released('A', 'Next')],
                        on_existing_key=OnExistingKey.SKIP, stderr_file=errors)
    assert 'not a version' not in errors.getvalue()
