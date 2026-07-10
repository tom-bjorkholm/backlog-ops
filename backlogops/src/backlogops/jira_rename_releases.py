#! /usr/local/bin/python3
"""Rename releases in Jira, changing a Jira version's name.

A release is a Jira version, and a version is matched by its name.
:func:`rename_releases_in_jira` renames each version named by an old name to
its new name, and :func:`rename_release_in_jira` renames a single one. The
project's versions are read once and each rename is validated against them
before anything is changed, so a rename whose old name is not a version, or
whose new name is already taken, is reported rather than attempted. A rename
Jira still refuses is collected with a concise reason and the other renames
are still applied. The argument renames are never modified.

A version is renamed through ``version.update(name=new_name)``, which is
exactly what the Jira client's ``rename_version`` does once it has looked the
version up; renaming the already-read version avoids a second lookup and lets
the collision and missing-name checks report a clear outcome. A new name that
is already a version name (including one claimed earlier in the same batch) is
a collision and the rename is not attempted, so no two versions ever share a
name. Renames are applied in the given order.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from dataclasses import dataclass
from typing import NamedTuple, Sequence, TextIO
from jira import JIRAError
from jira.resources import Resource
from backlogops.jira_connect import JiraConnections
from backlogops.jira_write import _jira_reason
from backlogops.jira_write_format import _key_section, _labeled_lines
from backlogops.jira_write_releases import _by_name, _release_context


class ReleaseRename(NamedTuple):
    """A request to rename a Jira release from one name to another."""

    old_name: str
    new_name: str


class FailedRename(NamedTuple):
    """A rename that could not be applied, with the failure reason."""

    rename: ReleaseRename
    reason: str


class RenamedReleasesInJira(NamedTuple):
    """The result of renaming releases in Jira.

    Fields:
        renamed: The renames whose version was successfully renamed.
        unchanged: Old names whose new name equals the old name, so the
            version was left untouched.
        missing: Old names that are not the name of any Jira version.
        collisions: Renames whose new name is already a version name, so
            the rename was not attempted to keep names unique.
        failed: Renames Jira refused, each with a concise reason; the
            argument renames are not changed by a failure.
    """

    renamed: list[ReleaseRename]
    unchanged: list[str]
    missing: list[str]
    collisions: list[ReleaseRename]
    failed: list[FailedRename]


@dataclass
class _RenameAcc:
    """Mutable accumulator of the rename results being built."""

    renamed: list[ReleaseRename]
    unchanged: list[str]
    missing: list[str]
    collisions: list[ReleaseRename]
    failed: list[FailedRename]


def _do_rename(version: Resource, rename: ReleaseRename, acc: _RenameAcc,
               taken: set[str]) -> None:
    """Rename one version, recording the outcome and updating taken names.

    On success the old name is freed and the new name is claimed, so a later
    rename in the same batch sees the current set of version names.
    """
    try:
        version.update(name=rename.new_name)
    except JIRAError as error:
        acc.failed.append(FailedRename(rename, _jira_reason(error)))
        return
    acc.renamed.append(rename)
    taken.discard(rename.old_name)
    taken.add(rename.new_name)


def _apply_rename(by_name: dict[str, Resource], taken: set[str],
                  rename: ReleaseRename, acc: _RenameAcc) -> None:
    """Validate and apply one rename, recording it in the accumulator.

    An unchanged name, a missing old name and a new name that is already
    taken are each recorded without touching Jira; otherwise the version is
    renamed.
    """
    if rename.old_name == rename.new_name:
        acc.unchanged.append(rename.old_name)
    elif rename.old_name not in by_name:
        acc.missing.append(rename.old_name)
    elif rename.new_name in taken:
        acc.collisions.append(rename)
    else:
        _do_rename(by_name[rename.old_name], rename, acc, taken)


def rename_releases_in_jira(connections: JiraConnections, preset_name: str,
                            renames: Sequence[ReleaseRename], *,
                            stderr_file: TextIO = sys.stderr
                            ) -> RenamedReleasesInJira:
    """Rename releases in Jira, matching each old name to a Jira version.

    The project's versions are read once and indexed by name. Each rename is
    validated against them and the names claimed by earlier renames of the
    batch: a new name equal to the old name is unchanged, an old name that is
    not a version is missing, and a new name that is already a version name is
    a collision. A valid rename changes the version's name; a rename Jira
    refuses is collected in ``failed`` with a concise reason, and the other
    renames are still applied. The argument renames are never modified.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset and its default project.
        preset_name: The name of the Jira preset to use.
        renames: The old-name-to-new-name renames to apply, in order. Not
            modified.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The applied, unchanged, missing, colliding and failed renames.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        JIRAError: If a Jira call other than a single rename fails.
    """
    _ = stderr_file
    ctx = _release_context(connections, preset_name)
    by_name = _by_name(ctx.client.project_versions(ctx.project))
    taken = set(by_name)
    acc = _RenameAcc([], [], [], [], [])
    for rename in renames:
        _apply_rename(by_name, taken, rename, acc)
    return RenamedReleasesInJira(acc.renamed, acc.unchanged, acc.missing,
                                 acc.collisions, acc.failed)


def rename_release_in_jira(connections: JiraConnections, preset_name: str,
                           old_name: str, new_name: str, *,
                           stderr_file: TextIO = sys.stderr
                           ) -> RenamedReleasesInJira:
    """Rename a single release in Jira from an old name to a new name.

    This is the single-rename form of :func:`rename_releases_in_jira` and
    returns the same result with exactly one rename classified.

    Args:
        connections: The pool of live Jira clients and the configuration.
        preset_name: The name of the Jira preset to use.
        old_name: The current name of the version to rename.
        new_name: The name to give the version.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The result classifying the single rename.
    """
    return rename_releases_in_jira(connections, preset_name,
                                   [ReleaseRename(old_name, new_name)],
                                   stderr_file=stderr_file)


def _rename_section(heading: str,
                    renames: Sequence[ReleaseRename]) -> list[str]:
    """Return the heading and one ``old -> new`` line per rename."""
    body = [f'  {rename.old_name} -> {rename.new_name}' for rename in renames]
    return _labeled_lines(heading, len(renames), body)


def _failed_rename_section(heading: str,
                           failed: Sequence[FailedRename]) -> list[str]:
    """Return the heading and the names and reason of each failed rename."""
    body = [f'  {entry.rename.old_name} -> {entry.rename.new_name}'
            f'  - {entry.reason}' for entry in failed]
    return _labeled_lines(heading, len(failed), body)


def format_rename_result(result: RenamedReleasesInJira) -> str:
    """Return a listing of the renamed, unchanged, missing and failed renames.

    Each section has a heading with its count, then one line per entry, or a
    ``(none)`` line when the section is empty. The CLI prints this text and
    the GUI shows it in a copy-pasteable pop-up.
    """
    lines = _rename_section('Renamed in Jira', result.renamed)
    lines.append('')
    lines.extend(_key_section('Unchanged (new name equals old)',
                              result.unchanged))
    lines.append('')
    lines.extend(_key_section('Old name not in Jira', result.missing))
    lines.append('')
    lines.extend(_rename_section('New name already in use', result.collisions))
    lines.append('')
    lines.extend(_failed_rename_section('Failed to rename', result.failed))
    return '\n'.join(lines)
