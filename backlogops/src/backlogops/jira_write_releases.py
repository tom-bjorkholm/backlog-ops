#! /usr/local/bin/python3
"""Add releases to Jira from internal releases.

:func:`add_releases_to_jira` creates one Jira version per internal
release whose name is not already present in the preset's default
project. Before creating anything it reads the project's version names
once; in ``RAISE`` mode it raises when any release name already exists,
and in ``SKIP`` mode it leaves the already-present releases alone. A
release whose creation Jira still refuses is collected in the result's
``failed`` list with a concise reason, and the remaining releases are
still added.

The create payload for each new version is built by inverting the
preset's release column map: the version keeps the release's own name
(the identity the presence check uses), and every other mapped internal
field is written to the Jira version create field its path names, such as
the planned date to ``releaseDate``. A date is written as ISO text. A
mapped field whose target is not a Jira version create field (name,
description, releaseDate, startDate, archived, released) is skipped and
reported. The internal ``estimated_date`` has no Jira analogue and is not
in the default release map, so it is not written unless a map targets a
version create field with it.

Each added release is copied into the result, so a caller can build a
consistent backlog-and-releases view; a version name never changes, so no
remapping is needed. The argument releases are never modified.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import copy
import sys
from dataclasses import dataclass
from datetime import date
from typing import Callable, NamedTuple, Optional, TextIO
from jira import JIRA, JIRAError
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import JiraColumnMap
from backlogops.jira_write import OnExistingKey, _jira_reason
from backlogops.jira_write_format import _labeled_lines
from backlogops.releases import Release, Releases

_VERSION_CREATE_FIELDS = frozenset({
    'name', 'description', 'releaseDate', 'startDate', 'archived', 'released'})
"""Jira version create fields a release column map may target.

The version name always comes from the release name, so a map entry that
targets ``name`` is not written again; any other target outside this set
is skipped and reported, because Jira's create-version call does not
accept it.
"""


class ReleaseExistsError(ValueError):
    """Raised when a release name to add already exists in Jira.

    It carries the sorted names that already exist, so a caller can report
    them. It derives from :class:`ValueError`, so a handler that catches
    ``ValueError`` still catches it.
    """

    def __init__(self, names: list[str]) -> None:
        """Store the already-present names and build the message."""
        self.names = names
        super().__init__(
            'Release names already exist in Jira: ' + ', '.join(names) + '.')


class FailedRelease(NamedTuple):
    """A release that could not be added, with the failure reason."""

    release: Release
    reason: str


class AddedReleasesToJira(NamedTuple):
    """The result of adding releases to Jira.

    Fields:
        stored: Copies of the added releases; a version name never
            changes, so each copy carries its original name.
        already_present: Copies of the releases whose name already existed
            in Jira and were therefore not added.
        failed: Releases whose creation Jira refused, each with a concise
            reason; the argument releases are not changed by a failure.
    """

    stored: Releases
    already_present: Releases
    failed: list[FailedRelease]


@dataclass(frozen=True)
class _ReleaseCtx:
    """The resolved Jira target and release map for creating versions."""

    client: JIRA
    project: str
    column_map: JiraColumnMap


@dataclass
class _AddedRel:
    """Mutable accumulator of the add-releases results being built."""

    stored: Releases
    already: Releases
    failed: list[FailedRelease]


def _release_context(connections: JiraConnections,
                     preset_name: str) -> _ReleaseCtx:
    """Return the client, project and release map for a named preset."""
    jira_config = connections.jira_config
    preset = jira_config.get_preset(preset_name)
    client = connections.client(preset.connection_name)
    column_map = jira_config.release_column_maps[
        preset.release_column_map_name]
    return _ReleaseCtx(client, preset.def_project, column_map)


def _existing_names(client: JIRA, project: str) -> set[str]:
    """Return the names of the versions already in the project."""
    versions = client.project_versions(project)
    return {name for name in (getattr(v, 'name', None) for v in versions)
            if isinstance(name, str)}


def _iso(value: object) -> object:
    """Return a date as ISO text, or the value unchanged."""
    return value.isoformat() if isinstance(value, date) else value


def _version_kwargs(release: Release,
                    column_map: JiraColumnMap) -> tuple[dict[str, object],
                                                        list[str]]:
    """Return the create-version keyword args and the skipped targets.

    The version name is always the release name. Every other mapped
    internal field is written to the Jira version create field its path
    names, with a date written as ISO text and an empty value left unset.
    A target that is not a version create field is collected as skipped.
    """
    kwargs: dict[str, object] = {'name': release.name}
    skipped: list[str] = []
    for internal, attrs in column_map.items():
        if not attrs:
            continue
        target = attrs[0].path[0]
        if target == 'name':
            continue
        if target not in _VERSION_CREATE_FIELDS:
            skipped.append(target)
            continue
        value = _iso(getattr(release, internal, None))
        if value not in (None, ''):
            kwargs[target] = value
    return kwargs, sorted(set(skipped))


def _report_skipped(name: str, skipped: list[str],
                    stderr_file: TextIO) -> None:
    """Report mapped fields that are not Jira version create fields."""
    print(f'WARNING: release {name!r} maps {", ".join(skipped)} to a field '
          'that create-version does not accept; those values were not set.',
          file=stderr_file)


def _raise_existing(names: list[str], stderr_file: TextIO) -> None:
    """Report and raise for release names that already exist in Jira."""
    error = ReleaseExistsError(names)
    print(str(error), file=stderr_file)
    raise error


def _run_version_write(release: Release, skipped: list[str],
                       stderr_file: TextIO,
                       write: Callable[[], None]) -> Optional[FailedRelease]:
    """Run one version write, returning a FailedRelease when Jira refuses.

    ``write`` performs the create or update and raises ``JIRAError`` when
    Jira refuses it. On success any mapped field the write could not accept
    (``skipped``) is reported and None is returned; on a refusal a copy of
    the release and a concise reason are returned. This is shared by
    creating a version and by updating a version.
    """
    try:
        write()
    except JIRAError as error:
        return FailedRelease(copy.deepcopy(release), _jira_reason(error))
    if skipped:
        _report_skipped(release.name, skipped, stderr_file)
    return None


def _try_create_version(ctx: _ReleaseCtx, release: Release,
                        stderr_file: TextIO) -> Optional[FailedRelease]:
    """Create one version, returning a FailedRelease when Jira refuses.

    The create payload is the inverted release map. This create step is
    shared by adding releases and by adding a missing release on update.
    """
    kwargs, skipped = _version_kwargs(release, ctx.column_map)

    def write() -> None:
        """Create the version with the inverted release map payload."""
        ctx.client.create_version(project=ctx.project, **kwargs)
    return _run_version_write(release, skipped, stderr_file, write)


def _add_version(ctx: _ReleaseCtx, release: Release, existing: set[str],
                 acc: _AddedRel, stderr_file: TextIO) -> None:
    """Create one not-yet-present release and record it in the accumulator.

    An already-present release is copied into ``already``. A refused create
    is recorded in ``failed``. A created release is copied into ``stored``.
    """
    if release.name in existing:
        acc.already.append(copy.deepcopy(release))
        return
    failed = _try_create_version(ctx, release, stderr_file)
    if failed is not None:
        acc.failed.append(failed)
        return
    acc.stored.append(copy.deepcopy(release))


def _create_versions(ctx: _ReleaseCtx, releases: Releases, existing: set[str],
                     stderr_file: TextIO) -> AddedReleasesToJira:
    """Create the not-yet-present releases, reporting the ones that fail."""
    acc = _AddedRel([], [], [])
    for release in releases:
        _add_version(ctx, release, existing, acc, stderr_file)
    return AddedReleasesToJira(acc.stored, acc.already, acc.failed)


def add_releases_to_jira(connections: JiraConnections, preset_name: str,
                         releases: Releases, *, on_existing_key: OnExistingKey,
                         stderr_file: TextIO = sys.stderr
                         ) -> AddedReleasesToJira:
    """Add the releases to Jira, one created version per new release.

    Before creating anything the project's existing version names are read.
    In ``RAISE`` mode, if any release name already exists the function
    raises before creating anything. In ``SKIP`` mode the already-present
    releases are left untouched. Each added release is created from the
    preset's release column map and default project, and a copy of it is
    collected. A release whose creation Jira refuses is collected in
    ``failed`` with a concise reason, and the other releases are still
    added. The argument releases are never modified.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset, connection and release column map.
        preset_name: The name of the Jira preset to use.
        releases: The releases to add. Not modified.
        on_existing_key: Whether to raise or skip when a release name
            already exists in Jira.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The stored releases, the already-present releases, and the releases
        whose creation failed with a reason.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        ReleaseExistsError: In ``RAISE`` mode, if any release name already
            exists in Jira.
    """
    ctx = _release_context(connections, preset_name)
    existing = _existing_names(ctx.client, ctx.project)
    present = sorted({release.name for release in releases} & existing)
    if on_existing_key is OnExistingKey.RAISE and present:
        _raise_existing(present, stderr_file)
    return _create_versions(ctx, releases, existing, stderr_file)


def _release_line(release: Release) -> str:
    """Return the display line for one release, with its planned date."""
    if release.planned_date is not None:
        return f'  {release.name}  {release.planned_date.isoformat()}'
    return f'  {release.name}'


def _release_section(heading: str, releases: Releases) -> list[str]:
    """Return the heading and the name-and-date line for each release."""
    return _labeled_lines(heading, len(releases),
                          [_release_line(release) for release in releases])


def _failed_section(heading: str, failed: list[FailedRelease]) -> list[str]:
    """Return the heading and the name and reason of each failure."""
    body = [f'  {entry.release.name}  - {entry.reason}' for entry in failed]
    return _labeled_lines(heading, len(failed), body)


def format_release_result(result: AddedReleasesToJira) -> str:
    """Return a listing of the added, present and failed releases.

    Each section has a heading with its count, then one line per release,
    or a ``(none)`` line when the section is empty. The CLI prints this
    text and the GUI shows it in a copy-pasteable pop-up.
    """
    lines = _release_section('Added to Jira', result.stored)
    lines.append('')
    lines.extend(_release_section('Already in Jira', result.already_present))
    lines.append('')
    lines.extend(_failed_section('Failed to add', result.failed))
    return '\n'.join(lines)
