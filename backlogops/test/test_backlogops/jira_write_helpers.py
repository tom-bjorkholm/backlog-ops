#! /usr/local/bin/python3
"""Shared config and connection-pool helpers for the Jira-write tests.

The backlog-write tests and the release-write tests both need a Jira
configuration with one connection, the default backlog and release column
maps and one preset named ``'w'``, and a connection pool whose clients are
all a stand-in. The release add and update tests also share one stand-in
Jira client that records created and updated versions, and a small builder
for a version attribute path. Those live here so the test modules share
one copy rather than duplicating them.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass, field
from typing import Callable, Optional
import pytest
from jira import JIRAError
from backlogops import JiraRankAnchor
from backlogops.backlog import BacklogItem
from backlogops.jira_rank_backlog import RankEnv
import backlogops.jira_connect as jc
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import (
    DEF_BACKLOG_COLUMN_MAP, DEF_RELEASE_COLUMN_MAP, JiraAttrPath,
    JiraAttrType, JiraColumnMap, JiraConnectConfig, JiraIOConfig, JiraPreset,
    TokenStorage)
from backlogops.no_text_io import NoTextIO

NO = NoTextIO()


@dataclass
class RankCall:
    """Records the arguments a captured rank_backlog_or_warn was given.

    The add and update tests both replace ``rank_backlog_or_warn`` with a
    stand-in, so this shared record and its capturing stand-in live here.
    """

    called: bool = False
    present: list[BacklogItem] = field(default_factory=list)
    key_map: dict[str, str] = field(default_factory=dict)
    anchor: Optional[JiraRankAnchor] = None


def capture_rank(record: RankCall) -> Callable[..., None]:
    """Return a rank_backlog_or_warn stand-in recording its arguments."""
    def stub(env: RankEnv, present: list[BacklogItem],
             key_map: dict[str, str]) -> None:
        """Record the ranking call instead of talking to Jira."""
        record.called = True
        record.present = list(present)
        record.key_map = dict(key_map)
        record.anchor = env.anchor
    return stub


def jira_write_config(project: str = 'PROJ',
                      release_map: Optional[JiraColumnMap] = None
                      ) -> JiraIOConfig:
    """Return a Jira config with one connection, maps and a preset ``'w'``.

    The connection ``'c'`` stores a clear internal token, the preset names
    the backlog map ``'bk'`` and the release map ``'rel'`` and the given
    default project. A caller may pass a custom release map; the backlog
    map is always the default one.
    """
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = TokenStorage.CLEAR_INTERNAL
    conn.stored_token = 'TOK'
    preset = JiraPreset(stderr_file=NO)
    preset.connection_name = 'c'
    preset.backlog_column_map_name = 'bk'
    preset.release_column_map_name = 'rel'
    preset.def_project = project
    config = JiraIOConfig(stderr_file=NO)
    config.connections = {'c': conn}
    config.backlog_column_maps = {'bk': DEF_BACKLOG_COLUMN_MAP}
    rel = DEF_RELEASE_COLUMN_MAP if release_map is None else release_map
    config.release_column_maps = {'rel': rel}
    config.presets = {'w': preset}
    return config


def connections_for(monkeypatch: pytest.MonkeyPatch, client: object,
                    config: Optional[JiraIOConfig] = None) -> JiraConnections:
    """Return a pool whose connections all yield the given stand-in client."""
    monkeypatch.setattr(jc, '_connect', lambda connection, passphrase: client)
    chosen = jira_write_config() if config is None else config
    return JiraConnections(chosen, None)


def attr_path(step: str) -> tuple[JiraAttrPath, ...]:
    """Return a one-step attribute path targeting a version attribute."""
    return (JiraAttrPath(JiraAttrType.ATTRIBUTE, (step,)),)


# pylint: disable-next=too-few-public-methods
class FakeVersion:
    """A stand-in Jira version that records or refuses field updates.

    Any ``fields`` are set as attributes to mimic a version's current
    values, so the update code can read them (such as ``releaseDate``) and
    tell an already-correct version from one that needs a change.
    """

    def __init__(self, name: str, fail: bool = False,
                 fields: Optional[dict[str, object]] = None) -> None:
        """Start with the name, the failing flag and the current fields.

        The version id defaults to the name and its self link to
        ``version/<name>``, so the order tests can move a version by id; a
        ``fields`` entry may override either.
        """
        self.name = name
        self.fail = fail
        self.id = name
        setattr(self, 'self', f'version/{name}')
        self.updated: dict[str, object] = {}
        for field_name, value in (fields or {}).items():
            setattr(self, field_name, value)

    def update(self, **kwargs: object) -> None:
        """Merge the fields as the real version does, or raise when failing.

        The production code updates through ``fields=``; this mirrors the
        real ``Version`` by merging that dict and any bare keyword args, so
        a test can read the effective payload sent to Jira.
        """
        if self.fail:
            raise JIRAError(status_code=400, text='bad update')
        fields = kwargs.pop('fields', {})
        assert isinstance(fields, dict)
        self.updated.update(fields)
        self.updated.update(kwargs)


class FakeJiraClient:
    """A stand-in Jira client recording created and updated versions.

    The project's existing versions are held as :class:`FakeVersion`
    objects keyed by name, so a release name matches a version and its
    update is recorded. A name in ``fail_update`` refuses its update and a
    name in ``fail_create`` refuses its creation, so both failure paths can
    be exercised. Created versions are recorded as payload dictionaries.
    """

    def __init__(self, existing: Optional[list[str]] = None,
                 fail_create: Optional[set[str]] = None,
                 fail_update: Optional[set[str]] = None,
                 current: Optional[dict[str, dict[str, object]]] = None
                 ) -> None:
        """Start with the present versions, their fields and the fail sets.

        ``current`` maps a present version name to the field values it
        already holds in Jira, so an update that would set the same values
        is recognised as already correct.
        """
        fails = set() if fail_update is None else fail_update
        fields = {} if current is None else current
        self.versions = {name: FakeVersion(name, name in fails,
                                           fields.get(name))
                         for name in (existing or [])}
        self.fail_create = set() if fail_create is None else set(fail_create)
        self.created: list[dict[str, object]] = []
        self.moves: list[tuple[str, Optional[str]]] = []

    def project_versions(self, project: str) -> list[FakeVersion]:
        """Return the project's versions as fake version resources."""
        _ = project
        return list(self.versions.values())

    def move_version(self, version_id: str, after: Optional[str] = None,
                     position: Optional[str] = None) -> FakeVersion:
        """Move a version to the first or last position, recording the move.

        The version is found by its id and reinserted at the front, or at
        the back for the ``Last`` position, so the recorded version order
        reflects the moves the order code makes.
        """
        _ = after
        name = next(cur for cur, version in self.versions.items()
                    if getattr(version, 'id') == version_id)
        version = self.versions.pop(name)
        if position == 'Last':
            self.versions[name] = version
        else:
            self.versions = {name: version, **self.versions}
        self.moves.append((version_id, position))
        return version

    def create_version(self, name: str, project: str,
                       **kwargs: object) -> FakeVersion:
        """Record the create payload, or raise for a failing name."""
        if name in self.fail_create:
            raise JIRAError(status_code=400, text='bad version')
        record: dict[str, object] = {'name': name, 'project': project}
        record.update(kwargs)
        self.created.append(record)
        return FakeVersion(name)
