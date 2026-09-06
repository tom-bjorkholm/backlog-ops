#! /usr/local/bin/python3
"""Resolve and validate the Jira issue type of a backlog item.

A backlog item carries an internal level while Jira needs an issue type
name. :func:`_issue_type` resolves one from the other through the preset's
level-to-issue-type map, falling back to the level's own name, so a Jira
that renamed a type (such as a Swedish ``Deluppgift`` sub-task) still gets
a valid issue type. :func:`_issue_type_meta` reads the project's creatable
issue types and whether Jira marks each one a sub-task, trying both create
metadata endpoints because different Jira versions expose only one of
them, and :func:`_subtask_types` reduces that to the sub-task type names.
:func:`_validate_issue_types` checks a whole backlog against the project
before anything is created, raising :class:`UnknownIssueTypeError`.

The write modules import these helpers; nothing here writes to Jira, so
the modules that create and update issues can share them without
depending on each other in a cycle.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass
from typing import Optional
from jira import JIRA, JIRAError
from backlogops.backlog import Backlog
from backlogops.jira_io_config import JiraIssueTypeMap
from backlogops.levels import Levels, level_name


class UnknownIssueTypeError(ValueError):
    """Raised when a backlog item's issue type is not valid in the project.

    It carries the invalid issue type names mapped to the item keys that
    use them, and the sorted valid type names, so a caller can report
    them. It derives from :class:`ValueError`.
    """

    def __init__(self, bad: dict[str, list[str]], valid: list[str]) -> None:
        """Store the bad and valid type names and build the message."""
        self.bad = bad
        self.valid = valid
        parts = '; '.join(f'{name!r} (for {", ".join(keys)})'
                          for name, keys in sorted(bad.items()))
        super().__init__(f'Invalid Jira issue type(s): {parts}. Valid '
                         f'types: {", ".join(valid)}.')


@dataclass(frozen=True)
class _TypeInfo:
    """The level and issue-type resolution used when creating issues.

    ``subtask_types`` holds the Jira issue type names that are sub-tasks,
    or None when the create metadata did not reveal them, in which case a
    sub-task is detected by the lowest configured level instead.
    """

    levels: Levels
    issue_type_map: JiraIssueTypeMap
    subtask_types: Optional[frozenset[str]]


def _issue_type(level: int, issue_type_map: JiraIssueTypeMap,
                levels: Levels) -> Optional[str]:
    """Return the Jira issue type to write for one internal level.

    The preset's level-to-issue-type map wins when it names the level;
    otherwise the level's own name is used, as before.
    """
    mapped = issue_type_map.get(level)
    if mapped is not None:
        return mapped
    return level_name(level, levels)


def _types_from_dicts(items: object) -> dict[str, bool]:
    """Return each issue type ``name`` mapped to its ``subtask`` flag."""
    result: dict[str, bool] = {}
    if isinstance(items, list):
        for item in items:
            name = item.get('name') if isinstance(item, dict) else None
            if isinstance(name, str):
                result[name] = bool(item.get('subtask'))
    return result


def _types_from_issuetypes(client: JIRA, project: str) -> dict[str, bool]:
    """Return issue type name to subtask flag via the issuetypes API."""
    meta = client.createmeta_issuetypes(project)
    values = meta.get('values', []) if isinstance(meta, dict) else []
    return _types_from_dicts(values)


def _types_from_createmeta(client: JIRA, project: str) -> dict[str, bool]:
    """Return issue type name to subtask flag via the older createmeta API."""
    meta = client.createmeta(projectKeys=project, expand='projects.issuetypes')
    projects = meta.get('projects', []) if isinstance(meta, dict) else []
    result: dict[str, bool] = {}
    for proj in projects:
        if isinstance(proj, dict):
            result.update(_types_from_dicts(proj.get('issuetypes', [])))
    return result


def _issue_type_meta(client: JIRA, project: str) -> dict[str, bool]:
    """Return the project's creatable issue types with subtask flags.

    Each creatable issue type name is mapped to whether Jira marks it a
    sub-task. Different Jira versions expose the create metadata through
    different endpoints and reject the other, so both are tried; when
    neither works the result is empty, issue-type validation is skipped
    and sub-task detection falls back to the lowest configured level.
    """
    for reader in (_types_from_issuetypes, _types_from_createmeta):
        try:
            types = reader(client, project)
        except JIRAError:
            continue
        if types:
            return types
    return {}


def _subtask_types(type_meta: dict[str, bool]) -> Optional[frozenset[str]]:
    """Return the sub-task issue type names, or None when unknown.

    None means the create metadata was unavailable, so the caller detects
    a sub-task by the lowest configured level instead.
    """
    if not type_meta:
        return None
    return frozenset(name for name, subtask in type_meta.items() if subtask)


def _validate_issue_types(valid: set[str], backlog: Backlog, levels: Levels,
                          issue_type_map: JiraIssueTypeMap) -> None:
    """Raise when an item's issue type is not valid in the project.

    The issue type written for each item is resolved through the preset's
    level-to-issue-type map, falling back to the level name. The valid
    type names come from the project's create metadata. When that is
    empty (an unexpected response), the check is skipped and each issue
    type is left to fail at create time instead.
    """
    if not valid:
        return
    bad: dict[str, list[str]] = {}
    for item in backlog:
        name = _issue_type(item.level, issue_type_map, levels) \
            or f'level {item.level}'
        if name not in valid:
            bad.setdefault(name, []).append(item.key)
    if bad:
        raise UnknownIssueTypeError(bad, sorted(valid))
