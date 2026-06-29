#! /usr/local/bin/python3
"""Tests for reading a backlog and its releases from Jira.

The pure mapping functions are tested with stand-in Jira objects built
from SimpleNamespace, the filter resolution is tested directly, and the
connection and orchestration are tested by replacing the client factory.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from types import SimpleNamespace
from typing import Optional
import pytest
import backlogops
from backlogops.available_teams import AvailableTeams
from backlogops.backlog import Status
from backlogops.backlog_ops_config import BacklogOpsConfig
from backlogops.backlog_releases import BacklogReleases
from backlogops.jira_io_config import (
    DEF_BACKLOG_COLUMN_MAP, DEF_RELEASE_COLUMN_MAP, JiraAttrPath, JiraAttrType,
    JiraConnectConfig, JiraIOConfig, JiraPreset, JiraType, TokenStorage,
    default_jira_filter)
from backlogops.no_text_io import NoTextIO
import backlogops.jira_read as jr
from backlogops.jira_read import (
    build_backlog_releases, read_backlog_from_jira, read_jira_from_config,
    resolve_jql, _connect, _coerce, _custom_ids, _resolve)

NO = NoTextIO()

FIELDS: list[dict[str, str]] = [
    {'id': 'customfield_10016', 'name': 'Story point estimate'},
    {'id': 'customfield_10001', 'name': 'Team'},
    {'id': 'summary', 'name': 'Summary'}]
"""Field descriptors with two custom fields and one system field."""


def _issue(status: str = 'DONE', issuetype: str = 'Story') -> SimpleNamespace:
    """Return a stand-in Jira issue with the default-mapped attributes."""
    fields = SimpleNamespace(summary='Build it',
                             status=SimpleNamespace(name=status),
                             issuetype=SimpleNamespace(name=issuetype),
                             fixVersions=[SimpleNamespace(name='R1')],
                             customfield_10016=5.0, customfield_10001='Alpha')
    return SimpleNamespace(key='S-1', fields=fields)


def _version() -> SimpleNamespace:
    """Return a stand-in Jira version with a name and a release date."""
    return SimpleNamespace(name='R1', releaseDate='2026-06-01')


def _build(issue: SimpleNamespace, version: SimpleNamespace,
           status_map: Optional[dict[str, Status]] = None) -> BacklogReleases:
    """Build a BacklogReleases from one stand-in issue and version."""
    return build_backlog_releases([issue], [version], FIELDS,
                                  backlog_map=DEF_BACKLOG_COLUMN_MAP,
                                  release_map=DEF_RELEASE_COLUMN_MAP,
                                  status_map=status_map, stderr_file=NO)


@pytest.mark.parametrize('value, expected', [
    (None, None), ('x', 'x'), (5, 5), (5.0, 5.0),
    ([SimpleNamespace(name='V1'), SimpleNamespace(name='V2')], 'V1'),
    ([], None), (SimpleNamespace(name='S'), 'S'),
    (date(2026, 1, 2), '2026-01-02')])
def test_coerce(value: object, expected: object) -> None:
    """Test a Jira value is coerced to a plain cell value."""
    assert _coerce(value) == expected


def test_custom_ids() -> None:
    """Test the custom field display names map to their field ids."""
    assert _custom_ids(FIELDS) == {
        'Story point estimate': 'customfield_10016',
        'Team': 'customfield_10001'}


def test_resolve_attr() -> None:
    """Test an ATTRIBUTE path reads a direct attribute of the issue."""
    issue = _issue()
    attr = JiraAttrPath(JiraAttrType.ATTRIBUTE, ('key',))
    assert _resolve(issue, issue.fields, attr, {}) == 'S-1'


def test_resolve_field() -> None:
    """Test a FIELD path reads a value under issue.fields."""
    issue = _issue()
    attr = JiraAttrPath(JiraAttrType.FIELD, ('status', 'name'))
    assert _resolve(issue, issue.fields, attr, {}) == 'DONE'


def test_resolve_custom() -> None:
    """Test a CUSTOM_FIELD display name resolves through the id map."""
    issue = _issue()
    attr = JiraAttrPath(JiraAttrType.CUSTOM_FIELD, ('Story point estimate',))
    ids = {'Story point estimate': 'customfield_10016'}
    assert _resolve(issue, issue.fields, attr, ids) == 5.0


def test_resolve_custom_id() -> None:
    """Test a CUSTOM_FIELD given as a field id resolves without the map."""
    issue = _issue()
    attr = JiraAttrPath(JiraAttrType.CUSTOM_FIELD, ('customfield_10001',))
    assert _resolve(issue, issue.fields, attr, {}) == 'Alpha'


def test_build() -> None:
    """Test an issue and a version map to a backlog item and a release."""
    data = _build(_issue(), _version())
    item = data.backlog[0]
    assert item.key == 'S-1'
    assert item.level == 1
    assert item.title == 'Build it'
    assert item.status is Status.DONE
    assert item.release == 'R1'
    assert item.team == 'Alpha'
    assert item.story_points == 5
    release = data.releases[0]
    assert release.name == 'R1'
    assert release.planned_date == date(2026, 6, 1)
    data.check_consistency(NO)


def test_build_status_map() -> None:
    """Test a non-standard status name maps through the status map."""
    data = _build(_issue(status='To Do'), _version(),
                  status_map={'To Do': Status.TODO})
    assert data.backlog[0].status is Status.TODO


def _preset(def_filter: str = '', def_project: str = 'PROJ') -> JiraPreset:
    """Return a preset with the given default filter and project."""
    preset = JiraPreset(stderr_file=NO)
    preset.connection_name = 'c'
    preset.column_map_name = 'bk'
    preset.release_column_map_name = 'rel'
    preset.def_project = def_project
    preset.def_filter = def_filter
    return preset


def test_resolve_jql() -> None:
    """Test the override wins, then the preset filter, then the default."""
    assert resolve_jql(_preset('F1'), None) == 'F1'
    assert resolve_jql(_preset('F1'), 'OV') == 'OV'
    assert resolve_jql(_preset(''), None) == default_jira_filter('PROJ')
    assert resolve_jql(_preset('F1'), '') == default_jira_filter('PROJ')


def test_jql_no_project() -> None:
    """Test an empty filter and no project is rejected."""
    with pytest.raises(ValueError):
        resolve_jql(_preset('', ''), None)


def _connection() -> JiraConnectConfig:
    """Return a connection with a clear internal token."""
    conn = JiraConnectConfig(stderr_file=NO)
    conn.base_url = 'https://x'
    conn.login_email = 'me@x'
    conn.token_storage = TokenStorage.CLEAR_INTERNAL
    conn.stored_token = 'TOK'
    return conn


def test_connect_cloud(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cloud connection uses basic authentication."""
    captured: dict[str, object] = {}
    monkeypatch.setattr(jr, 'JIRA', lambda **kwargs: captured.update(kwargs))
    _connect(_connection(), None)
    assert captured == {'server': 'https://x', 'basic_auth': ('me@x', 'TOK')}


def test_connect_server(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a server connection uses token authentication."""
    captured: dict[str, object] = {}
    monkeypatch.setattr(jr, 'JIRA', lambda **kwargs: captured.update(kwargs))
    conn = _connection()
    conn.jira_type = JiraType.SERVER
    _connect(conn, None)
    assert captured == {'server': 'https://x', 'token_auth': 'TOK'}


class _FakeClient:
    """A stand-in Jira client returning canned issues and versions."""

    def __init__(self, issues: list[object], versions: list[object]) -> None:
        """Store the canned issues and versions and the queried filter."""
        self.issues = issues
        self.versions = versions
        self.jql = ''
        self.project = ''

    def search_issues(self, jql: str, **kwargs: object) -> list[object]:
        """Record the filter and return the canned issues."""
        _ = kwargs
        self.jql = jql
        return self.issues

    def project_versions(self, project: str) -> list[object]:
        """Record the project and return the canned versions."""
        self.project = project
        return self.versions

    def fields(self) -> list[dict[str, str]]:
        """Return the canned field descriptors."""
        return FIELDS


def _io_config() -> JiraIOConfig:
    """Return a Jira configuration with one connection, maps and preset."""
    config = JiraIOConfig(stderr_file=NO)
    config.connections = {'c': _connection()}
    config.column_maps = {'bk': DEF_BACKLOG_COLUMN_MAP,
                          'rel': DEF_RELEASE_COLUMN_MAP}
    config.from_jira_presets = {'p': _preset()}
    return config


def test_read_orchestration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the reader wires the default filter and maps the data."""
    client = _FakeClient([_issue()], [_version()])
    monkeypatch.setattr(jr, '_connect', lambda connection, passphrase: client)
    data = read_backlog_from_jira(_io_config(), 'p')
    assert client.jql == default_jira_filter('PROJ')
    assert client.project == 'PROJ'
    assert data.backlog[0].key == 'S-1'
    assert data.releases[0].name == 'R1'


def test_read_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a filter override replaces the preset filter."""
    client = _FakeClient([_issue()], [_version()])
    monkeypatch.setattr(jr, '_connect', lambda connection, passphrase: client)
    read_backlog_from_jira(_io_config(), 'p',
                           filter_override='project = OTHER')
    assert client.jql == 'project = OTHER'
    assert client.project == 'PROJ'


def test_read_from_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the config convenience reads with the config's levels."""
    client = _FakeClient([_issue()], [_version()])
    monkeypatch.setattr(jr, '_connect', lambda connection, passphrase: client)
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]), stderr_file=NO)
    config.jira = _io_config()
    data = read_jira_from_config(config, 'p')
    assert data.backlog[0].level == 1
    assert data.releases[0].name == 'R1'


def test_reexport() -> None:
    """Test the package re-exports the Jira reader functions."""
    assert backlogops.read_backlog_from_jira is read_backlog_from_jira
    assert 'read_backlog_from_jira' in backlogops.__all__
    assert 'read_jira_from_config' in backlogops.__all__
