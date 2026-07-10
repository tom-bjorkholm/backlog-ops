#! /usr/local/bin/python3
"""Update releases in Jira from internal releases.

:func:`update_releases_in_jira` changes each Jira version whose name
matches an internal release so that its mapped fields match the release,
most importantly the release date. The fields written are the inverse of
the preset's release column map, exactly as when adding a release, but the
version name is the identity used to find the version and is never
changed. A mapped value that is empty (such as a release with no planned
date) is left unset, so an empty internal value never clears a Jira field.
Only the fields whose value differs from the version's current value are
written; a release whose mapped fields already match Jira is reported as
already correct and its version is not touched.

A release whose name is not present in Jira is handled by the chosen
:class:`OnMissingKey` policy: ``RAISE`` raises :class:`ItemNotInJiraError`
before anything is changed, ``IGNORE`` leaves the missing release alone,
and ``ADD`` creates it exactly as :func:`add_releases_to_jira` would. A
release whose update or creation Jira refuses is collected in the result's
``failed`` list with a concise reason, and the remaining releases are
still processed. The argument releases are never modified.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from dataclasses import dataclass
from typing import NamedTuple, Optional, TextIO
from jira.resources import Resource
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import JiraColumnMap
from backlogops.jira_write import ItemNotInJiraError, OnMissingKey
from backlogops.jira_write_format import _key_section, _outcome_prefix
from backlogops.jira_write_releases import (
    FailedRelease, _ReleaseCtx, _by_name, _failed_section, _release_context,
    _report_skipped, _run_version_write, _try_create_version, _version_kwargs)
from backlogops.releases import Release, Releases


class UpdatedReleasesInJira(NamedTuple):
    """The result of updating releases in Jira.

    Fields:
        updated: Names of the releases whose matching Jira version had at
            least one mapped field changed.
        already_correct: Names of the releases whose matching Jira version
            already held the mapped values, so no change was made. A
            release with nothing to write (an empty mapped value) is
            counted here too, since its version is left untouched.
        ignored: Names of the releases not present in Jira and left
            untouched under the ``IGNORE`` policy.
        added: Names of the releases not present in Jira and created under
            the ``ADD`` policy.
        failed: Releases whose update or creation Jira refused, each with a
            concise reason; the argument releases are not changed by a
            failure.
    """

    updated: list[str]
    already_correct: list[str]
    ignored: list[str]
    added: list[str]
    failed: list[FailedRelease]


@dataclass
class _UpdatedRel:
    """Mutable accumulator of the update-releases results being built."""

    updated: list[str]
    already_correct: list[str]
    ignored: list[str]
    added: list[str]
    failed: list[FailedRelease]


@dataclass(frozen=True)
class _UpdateCtx:
    """The resolved target, the existing versions and the missing mode."""

    base: _ReleaseCtx
    existing: dict[str, Resource]
    mode: OnMissingKey
    stderr_file: TextIO


def _versions_by_name(ctx: _ReleaseCtx) -> dict[str, Resource]:
    """Return the project's versions indexed by their name."""
    return _by_name(ctx.client.project_versions(ctx.project))


def _raise_missing(names: list[str], stderr_file: TextIO) -> None:
    """Report and raise for release names not present in Jira."""
    error = ItemNotInJiraError(names, 'Release names')
    print(str(error), file=stderr_file)
    raise error


def _changed_fields(release: Release, column_map: JiraColumnMap,
                    version: Resource) -> tuple[dict[str, object], list[str]]:
    """Return the mapped fields that differ from the version, and skipped.

    The intended payload is the inverted release map without the version
    name, which is the identity and never changes. A field is kept only
    when its value differs from the version's current value, so an empty
    result means the version already holds the mapped values.
    """
    kwargs, skipped = _version_kwargs(release, column_map)
    del kwargs['name']
    changed = {target: value for target, value in kwargs.items()
               if getattr(version, target, None) != value}
    return changed, skipped


def _record(acc: _UpdatedRel, done: list[str], name: str,
            failed: Optional[FailedRelease]) -> None:
    """Add a refusal to ``failed``, else the name to the ``done`` list."""
    if failed is not None:
        acc.failed.append(failed)
    else:
        done.append(name)


def _update_matched(ctx: _UpdateCtx, release: Release, version: Resource,
                    acc: _UpdatedRel) -> None:
    """Record a matched version as already correct, updated or failed.

    Only the mapped fields whose value differs from the version are
    written; when none differ the version is left untouched and the release
    is already correct. A skipped mapped target is reported in either case.
    """
    changed, skipped = _changed_fields(release, ctx.base.column_map, version)
    if not changed:
        if skipped:
            _report_skipped(release.name, skipped, ctx.stderr_file)
        acc.already_correct.append(release.name)
        return

    def write() -> None:
        """Write only the mapped fields whose value differs in Jira."""
        version.update(fields=changed)
    _record(acc, acc.updated, release.name,
            _run_version_write(release, skipped, ctx.stderr_file, write))


def _apply_one(ctx: _UpdateCtx, release: Release, acc: _UpdatedRel) -> None:
    """Update, add or ignore one release per the missing-key mode.

    A release matched by name is updated. A missing release is created
    under ``ADD`` and left alone under ``IGNORE``; the ``RAISE`` mode has
    already raised before the loop, so a missing release is not seen here.
    """
    version = ctx.existing.get(release.name)
    if version is not None:
        _update_matched(ctx, release, version, acc)
    elif ctx.mode is OnMissingKey.ADD:
        _record(acc, acc.added, release.name,
                _try_create_version(ctx.base, release, ctx.stderr_file))
    elif ctx.mode is OnMissingKey.IGNORE:
        acc.ignored.append(release.name)


def update_releases_in_jira(connections: JiraConnections, preset_name: str,
                            releases: Releases, *,
                            on_missing_key: OnMissingKey,
                            stderr_file: TextIO = sys.stderr
                            ) -> UpdatedReleasesInJira:
    """Update the releases in Jira, matching a Jira version by its name.

    The project's versions are read once and indexed by name. In ``RAISE``
    mode, if any release name is not present the function raises before
    changing anything. Each matched version is updated from the preset's
    release column map, so its mapped fields (most importantly the release
    date) match the internal release; an empty internal value is left
    unset. A release whose name is not present is added in ``ADD`` mode and
    left alone in ``IGNORE`` mode. A release whose update or creation Jira
    refuses is collected in ``failed`` with a concise reason, and the other
    releases are still processed. The argument releases are never modified.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset, connection and release column map.
        preset_name: The name of the Jira preset to use.
        releases: The releases to update. Not modified.
        on_missing_key: Whether to raise, ignore or add when a release name
            is not present in Jira.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The names of the updated, already-correct, ignored and added
        releases, and the releases whose update or creation failed with a
        reason.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        ItemNotInJiraError: In ``RAISE`` mode, if any release name is not
            present in Jira.
    """
    ctx = _release_context(connections, preset_name)
    existing = _versions_by_name(ctx)
    missing = sorted({release.name for release in releases} - set(existing))
    if on_missing_key is OnMissingKey.RAISE and missing:
        _raise_missing(missing, stderr_file)
    update_ctx = _UpdateCtx(ctx, existing, on_missing_key, stderr_file)
    acc = _UpdatedRel([], [], [], [], [])
    for release in releases:
        _apply_one(update_ctx, release, acc)
    return UpdatedReleasesInJira(acc.updated, acc.already_correct, acc.ignored,
                                 acc.added, acc.failed)


def format_release_updates(result: UpdatedReleasesInJira) -> str:
    """Return a listing of the update outcome per release.

    The sections are the updated, already-correct, ignored, added and
    failed releases. Each section has a heading with its count, then one
    line per release name, or a ``(none)`` line when the section is empty.
    The CLI prints this text and the GUI shows it in a copy-pasteable
    pop-up.
    """
    lines = _outcome_prefix(result.updated, result.already_correct,
                            result.ignored)
    lines.append('')
    lines.extend(_key_section('Added to Jira', result.added))
    lines.append('')
    lines.extend(_failed_section('Failed to update', result.failed))
    return '\n'.join(lines)
