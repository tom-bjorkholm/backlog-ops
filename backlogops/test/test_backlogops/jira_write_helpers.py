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
from types import SimpleNamespace
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
from backlogops.jira_write import _transition_target
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


WRITE_FIELDS: list[dict[str, str]] = [
    {'id': 'customfield_10016', 'name': 'Story point estimate'},
    {'id': 'customfield_10001', 'name': 'Team'}]
"""Field descriptors resolving the two custom fields used on create."""

EDITABLE_DEFAULT: dict[str, str] = {
    'description': 'Description',
    'customfield_10016': 'Story point estimate',
    'customfield_10001': 'Team', 'fixVersions': 'Fix versions'}
"""Fields the fake add issue's edit screen offers by default."""

ISSUE_TYPES_DEFAULT: dict[str, bool] = {
    'Story': False, 'Epic': False, 'Subtask': True}
"""Creatable issue types of the fake Jira, mapped to their subtask flag.

An empty issue-type map instead models a Jira whose create metadata is
unavailable, so that sub-task detection falls back to the lowest level.
"""


@dataclass
class WriteBehavior:
    """How the fake Jira answers create, edit and transition calls.

    ``transition_fault`` selects a transition failure: ``'apply'`` makes
    applying a transition raise and ``'list'`` makes listing the available
    transitions raise; the empty default lets both succeed.
    """

    editable: dict[str, str]
    issue_types: dict[str, bool]
    fail_types: set[str]
    init_status: str = 'TODO'
    transitions: list[dict[str, object]] = field(default_factory=list)
    transition_fault: str = ''
    transitioned: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class WriteLinkLog:
    """Recorded update and link calls, and the link failure knobs.

    ``updates`` records each ``update`` call as (key, fields), ``links``
    records each created issue link as (type, inward, outward),
    ``fail_parent`` makes a parent update fail, and ``fail_link_to`` names
    the endpoint keys whose link creation should fail.
    """

    updates: list[tuple[str, dict[str, object]]] = field(default_factory=list)
    links: list[tuple[str, str, str]] = field(default_factory=list)
    fail_parent: bool = False
    fail_link_to: set[str] = field(default_factory=set)


class WriteClient:
    """A stand-in Jira client for the add-to-Jira tests.

    Shared by the add-to-Jira and connection-pool tests. ``fail_close`` is
    set as an attribute after construction when a dead session's close
    should raise.
    """

    def __init__(self, existing: Optional[set[str]] = None, alive: bool = True,
                 editable: Optional[dict[str, str]] = None,
                 issue_types: Optional[dict[str, bool]] = None,
                 fail_types: Optional[set[str]] = None) -> None:
        """Start with the present keys, screens, types and failing types.

        ``issue_types`` maps each creatable issue type name to whether it
        is a sub-task; an empty map models unavailable create metadata.
        The status and transition behaviour lives in ``behavior`` and a
        status test sets the fields it needs.
        """
        self.existing = set() if existing is None else set(existing)
        self.alive = alive
        self.fail_close = False
        self.behavior = WriteBehavior(
            editable=EDITABLE_DEFAULT if editable is None else editable,
            issue_types=(ISSUE_TYPES_DEFAULT if issue_types is None
                         else issue_types),
            fail_types=set() if fail_types is None else fail_types)
        self.created: list[dict[str, object]] = []
        self.link_log = WriteLinkLog()
        self.closed = 0

    def myself(self) -> dict[str, str]:
        """Report a live session, or raise when the client is dead."""
        if not self.alive:
            raise JIRAError(status_code=401, text='session closed')
        return {'name': 'tester'}

    def fields(self) -> list[dict[str, str]]:
        """Return the canned field descriptors."""
        return WRITE_FIELDS

    def issue(self, key: str) -> SimpleNamespace:
        """Return the issue for a present key, or raise for an absent one."""
        if key in self.existing:
            return SimpleNamespace(key=key)
        raise JIRAError(status_code=404, text='not found')

    def _issue_type_values(self) -> list[dict[str, object]]:
        """Return the issue types with their sub-task flags for metadata."""
        return [{'name': name, 'subtask': subtask}
                for name, subtask in sorted(self.behavior.issue_types.items())]

    def createmeta_issuetypes(self, project: str) -> dict[str, object]:
        """Return the project's creatable issue types as create metadata."""
        _ = project
        return {'values': self._issue_type_values()}

    def createmeta(self, **kwargs: object) -> dict[str, object]:
        """Return the creatable issue types via the older createmeta API."""
        _ = kwargs
        return {'projects': [{'issuetypes': self._issue_type_values()}]}

    def create_issue(self, fields: dict[str, object]) -> SimpleNamespace:
        """Record the create payload; the issue merges a later update.

        Raises for an issue type in ``fail_types``, and for a sub-task
        without a ``parent``, as Jira does when it refuses a create. The
        returned issue's ``update`` merges its fields into the same record,
        and it carries a ``fields.status`` set to the initial status, so
        the status reconciliation can read and transition it.
        """
        issuetype = fields.get('issuetype')
        name = issuetype.get('name') if isinstance(issuetype, dict) else None
        if name in self.behavior.fail_types:
            raise JIRAError(status_code=400, text='Specify a valid issue type')
        if name is not None and self.behavior.issue_types.get(name) \
                and 'parent' not in fields:
            raise JIRAError(status_code=400, text='Issue type is a sub-task '
                            'but parent issue key or id not specified.')
        record = dict(fields)
        self.created.append(record)
        key = f'JIRA-{len(self.created)}'
        status = SimpleNamespace(name=self.behavior.init_status)
        return SimpleNamespace(key=key, update=self._updater(key, record),
                               fields=SimpleNamespace(status=status))

    def _updater(self, key: str, record: dict[str, object]
                 ) -> Callable[..., None]:
        """Return an update callback that records and may refuse a parent."""
        def update(fields: dict[str, object]) -> None:
            """Record the update, refusing a parent link when set to fail."""
            if self.link_log.fail_parent and 'parent' in fields:
                raise JIRAError(status_code=400, text='parent rejected')
            record.update(fields)
            self.link_log.updates.append((key, dict(fields)))
        return update

    def create_issue_link(self, link_type: str, inward: str, outward: str,
                          comment: Optional[dict[str, object]] = None) -> None:
        """Record a created issue link, or refuse a failing endpoint."""
        _ = comment
        if inward in self.link_log.fail_link_to or \
                outward in self.link_log.fail_link_to:
            raise JIRAError(status_code=400, text='link rejected')
        self.link_log.links.append((link_type, inward, outward))

    def editmeta(self, issue: str) -> dict[str, object]:
        """Return the edit-screen field metadata for the issue."""
        _ = issue
        return {'fields': {fid: {'name': name}
                           for fid, name in self.behavior.editable.items()}}

    def transitions(self, issue: SimpleNamespace) -> list[dict[str, object]]:
        """Return the configured transitions, or raise when set to fail."""
        _ = issue
        if self.behavior.transition_fault == 'list':
            raise JIRAError(status_code=500, text='cannot list transitions')
        return list(self.behavior.transitions)

    def transition_issue(self, issue: SimpleNamespace,
                         transition: str) -> None:
        """Apply a transition, updating the status, or raise when set to."""
        if self.behavior.transition_fault == 'apply':
            raise JIRAError(status_code=400, text='transition rejected')
        target = self._target_of(transition)
        if target is not None:
            issue.fields.status.name = target
        self.behavior.transitioned.append((issue.key, transition))

    def _target_of(self, transition: str) -> Optional[str]:
        """Return the target status name of a transition id, or None."""
        for trans in self.behavior.transitions:
            if trans.get('id') == transition:
                return _transition_target(trans)
        return None

    def close(self) -> None:
        """Count a close, or raise as a dead session's close can."""
        self.closed += 1
        if self.fail_close:
            raise JIRAError(status_code=401, text='already closed')


def connect_each(clients: list[WriteClient]
                 ) -> Callable[[object, object], WriteClient]:
    """Return a stand-in ``_connect`` yielding each client in turn."""
    supply = iter(clients)
    return lambda connection, passphrase: next(supply)


def attr_parent_config() -> JiraIOConfig:
    """Return a write config whose parent_key maps to a bare attribute.

    The parent_key path is a non-writable ATTRIBUTE kind, so the add and
    update paths exercise their "no writable parent field" guards.
    """
    config = jira_write_config()
    backlog_map = dict(DEF_BACKLOG_COLUMN_MAP)
    attr = JiraAttrPath(JiraAttrType.ATTRIBUTE, ('parent',))
    backlog_map['parent_key'] = (attr,)
    config.backlog_column_maps = {'bk': backlog_map}
    return config
