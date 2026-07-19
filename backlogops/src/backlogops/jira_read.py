#! /usr/local/bin/python3
"""Read a backlog and its releases from Jira into BacklogReleases.

A configured :class:`JiraPreset` names the connection, the backlog and
release column maps, the default project and the default issue filter.
:func:`read_backlog_from_jira` takes a live client from a
:class:`backlogops.jira_connect.JiraConnections` pool, runs the issue
filter (Jira Query Language) to read the backlog items, reads the project
versions to read the releases, and maps each Jira attribute to an
internal field through the preset's column maps. Custom field display
names in a column map (such as 'Story point estimate') are resolved to
their field ids through the live custom field list of the Jira instance.
Only the fields named by the column map are fetched, and the issues are
read page by page through :func:`backlogops.jira_search.search_all_issues`,
so a backlog of many thousands of items is read in full without fetching
every field of every issue.

The caller may override the preset's filter for one read. When no filter
is configured at all, the default filter selects every issue in the
default project, ordered by rank, while the releases always come from the
default project's versions.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from collections.abc import Iterable, Mapping
from datetime import date
from typing import Callable, Optional, TextIO
from backlogops.backlog import BacklogItem, DEPENDENCY_FIELDS, Status
from backlogops.backlog_ops_config import BacklogOpsConfig
from backlogops.backlog_releases import BacklogReleases
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType, \
    JiraColumnMap, JiraPreset, JiraType, default_jira_filter
from backlogops.jira_search import search_all_issues
from backlogops.levels import Levels
from backlogops.releases import Release
from backlogops.table_rows import BACKLOG_FIELDS, RELEASE_FIELDS
from backlogops.table_rows import row_to_item, row_to_release

_SINGLE_VALUE_FIELDS = frozenset(BACKLOG_FIELDS + RELEASE_FIELDS)
"""Internal fields that hold a single scalar value."""


def _custom_ids(fields_list: Iterable[Mapping[str, object]]) -> dict[str, str]:
    """Return a map from custom field display name to its field id."""
    result: dict[str, str] = {}
    for field in fields_list:
        field_id, name = field.get('id'), field.get('name')
        if (isinstance(field_id, str) and isinstance(name, str)
                and field_id.startswith('customfield_')):
            result[name] = field_id
    return result


def _walk(root: object, path: tuple[str, ...]) -> object:
    """Return the attribute reached from root by the path steps."""
    value = root
    for step in path:
        if value is None:
            return None
        value = getattr(value, step, None)
    return value


def _dotted(text: str) -> tuple[str, ...]:
    """Return dot-separated path text as path steps."""
    return tuple(part for part in text.split('.') if part)


def _filtered_values(field_root: object, attr: JiraAttrPath) -> list[object]:
    """Return values from list entries matching a filter path."""
    list_name, filter_path, expected, value_path = attr.path
    candidates = _walk(field_root, (list_name,))
    if not isinstance(candidates, (list, tuple)):
        return []
    values: list[object] = []
    for candidate in candidates:
        if _walk(candidate, _dotted(filter_path)) == expected:
            values.append(_walk(candidate, _dotted(value_path)))
    return values


def _field_id(name: str, custom_ids: dict[str, str]) -> Optional[str]:
    """Return the field id for a custom field given as id or display name."""
    if name.startswith('customfield_'):
        return name
    return custom_ids.get(name)


def _attr_field_id(attr: JiraAttrPath,
                   custom_ids: dict[str, str]) -> Optional[str]:
    """Return the Jira field an attribute path needs fetched, or None.

    An ATTRIBUTE path reads a direct issue attribute such as the key, which
    Jira always returns, so it needs no field fetched. A CUSTOM_FIELD path
    needs the field id its display name resolves to. A FIELD or
    FILTERED_FIELD path needs its first step, which names the field under
    ``fields``.
    """
    if attr.kind is JiraAttrType.ATTRIBUTE:
        return None
    if attr.kind is JiraAttrType.CUSTOM_FIELD:
        return _field_id(attr.path[0], custom_ids)
    return attr.path[0]


def _search_fields(column_map: JiraColumnMap,
                   custom_ids: dict[str, str]) -> list[str]:
    """Return the Jira fields to fetch for a backlog column map.

    Only the fields the map reads are requested, so a large backlog is not
    weighed down by every field of every issue. Fields are kept in the
    order first seen and never repeated.
    """
    fields: list[str] = []
    for attrs in column_map.values():
        for attr in attrs:
            field = _attr_field_id(attr, custom_ids)
            if field is not None and field not in fields:
                fields.append(field)
    return fields


def _resolve(attr_root: object, field_root: object, attr: JiraAttrPath,
             custom_ids: dict[str, str]) -> object:
    """Return the value an attribute path reaches on a Jira object."""
    if attr.kind is JiraAttrType.ATTRIBUTE:
        return _walk(attr_root, attr.path)
    if attr.kind is JiraAttrType.FIELD:
        return _walk(field_root, attr.path)
    if attr.kind is JiraAttrType.FILTERED_FIELD:
        return _filtered_values(field_root, attr)
    field_id = _field_id(attr.path[0], custom_ids)
    if field_id is None:
        return None
    return getattr(field_root, field_id, None)


def _coerce_first(values: Iterable[object]) -> object:
    """Return the first non-empty coerced element of a sequence, or None."""
    for element in values:
        cell = _coerce(element)
        if cell is not None:
            return cell
    return None


def _coerce_resource(value: object) -> object:
    """Return a Jira resource's name or value, else its text."""
    name = getattr(value, 'name', None)
    if isinstance(name, str):
        return name
    inner = getattr(value, 'value', None)
    if isinstance(inner, (bool, int, float, str)):
        return inner
    return str(value)


def _coerce(value: object) -> object:
    """Return a Jira attribute value as a plain table cell value.

    A list (such as fix versions) yields the first non-empty element, a
    Jira resource yields its ``name`` or ``value``, and a date yields its
    ISO text, so a mapped value becomes a string, number or None.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return _coerce_first(value)
    if isinstance(value, date):
        return value.isoformat()
    return _coerce_resource(value)


def _coerce_all(values: Iterable[object]) -> list[object]:
    """Return all non-empty coerced elements from a sequence."""
    result: list[object] = []
    for element in values:
        cell = _coerce(element)
        if cell not in (None, ''):
            result.append(cell)
    return result


def _coerce_field(name: str, value: object) -> object:
    """Return a Jira value coerced for one internal field."""
    if name in DEPENDENCY_FIELDS and isinstance(value, (list, tuple)):
        return ' '.join(str(item) for item in _coerce_all(value))
    return _coerce(value)


def is_appendable_jira_field(name: str) -> bool:
    """Return whether duplicate Jira values should be appended."""
    return name not in _SINGLE_VALUE_FIELDS


def _unique(values: list[object]) -> list[object]:
    """Return values with duplicates removed while preserving order."""
    result: list[object] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _warn_many(name: str, values: list[object], stderr_file: TextIO) -> None:
    """Warn that several Jira paths had values for one field."""
    text = ', '.join(repr(value) for value in values)
    print(f'WARNING: several Jira paths had values for {name}: {text}.',
          file=stderr_file)


def _merge_values(name: str, values: list[object],
                  stderr_file: TextIO) -> object:
    """Return the value to store after merging duplicate sources."""
    unique = _unique(values)
    if not unique:
        return None
    if len(unique) == 1:
        return unique[0]
    _warn_many(name, unique, stderr_file)
    if is_appendable_jira_field(name):
        return '\n\n'.join(str(value) for value in unique)
    return unique[0]


def _field_values(name: str, attr_root: object, field_root: object,
                  attrs: tuple[JiraAttrPath, ...],
                  custom_ids: dict[str, str]) -> list[object]:
    """Return all non-empty values read from Jira paths."""
    values = []
    for attr in attrs:
        value = _coerce_field(name, _resolve(attr_root, field_root, attr,
                                             custom_ids))
        if value not in (None, ''):
            values.append(value)
    return values


def _row(attr_root: object, field_root: object, column_map: JiraColumnMap,
         custom_ids: dict[str, str],
         stderr_file: TextIO = sys.stderr) -> dict[str, object]:
    """Return one Jira object as a row keyed by internal field name."""
    return {name: _merge_values(name, _field_values(name, attr_root,
                                                    field_root, attrs,
                                                    custom_ids), stderr_file)
            for name, attrs in column_map.items()}


def _backlog_row(attr_root: object, field_root: object,
                 column_map: JiraColumnMap, custom_ids: dict[str, str],
                 stderr_file: TextIO) -> dict[str, object]:
    """Return one Jira issue row with Jira-specific defaults applied."""
    row = _row(attr_root, field_root, column_map, custom_ids, stderr_file)
    if 'story_points' in row and row['story_points'] in (None, ''):
        row['story_points'] = 0
    return row


# pylint: disable-next=too-many-arguments
def build_backlog_releases(
        issues: Iterable[object], versions: Iterable[object],
        fields_list: Iterable[Mapping[str, object]], *,
        backlog_map: JiraColumnMap, release_map: JiraColumnMap,
        levels: Optional[Levels] = None,
        status_map: Optional[dict[str, Status]] = None,
        stderr_file: TextIO = sys.stderr) -> BacklogReleases:
    """Build a BacklogReleases from fetched Jira issues and versions.

    Each issue is mapped through ``backlog_map`` into a backlog item, with
    a string level resolved through ``levels`` and a string status matched
    through ``status_map``; each version is mapped through ``release_map``
    into a release. The issue attributes are read relative to the issue
    itself and its ``fields``, while a version is read relative to itself.

    Args:
        issues: The Jira issues to map into backlog items.
        versions: The Jira versions to map into releases.
        fields_list: The Jira field descriptors, used to resolve custom
            field display names to their ids.
        backlog_map: The internal-field to Jira attribute path map for the
            backlog items.
        release_map: The internal-field to Jira attribute path map for the
            releases.
        levels: The levels used to resolve a string level, or None for the
            default levels.
        status_map: Extra status names mapped to Status members, or None.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The backlog and releases read from Jira.
    """
    custom_ids = _custom_ids(fields_list)
    backlog: list[BacklogItem] = [
        row_to_item(_backlog_row(issue, getattr(issue, 'fields', None),
                                 backlog_map, custom_ids, stderr_file),
                    levels, status_map, stderr_file)
        for issue in issues]
    releases: list[Release] = [
        row_to_release(_row(version, version, release_map, {}, stderr_file),
                       stderr_file)
        for version in versions]
    return BacklogReleases(backlog=backlog, releases=releases)


def resolve_jql(preset: JiraPreset, filter_override: Optional[str]) -> str:
    """Return the Jira Query Language filter to run for a preset.

    A non-empty override wins over the preset's default filter, and an
    empty filter falls back to the default project filter.

    Args:
        preset: The preset that carries the default filter and project.
        filter_override: A filter to use instead of the preset's, or None.

    Returns:
        The filter to run.

    Raises:
        ValueError: If no filter and no default project are configured.
    """
    chosen = preset.def_filter if filter_override is None else filter_override
    if chosen.strip():
        return chosen
    if not preset.def_project:
        raise ValueError('No Jira issue filter and no default project are '
                         'configured for this preset.')
    return default_jira_filter(preset.def_project)


# pylint: disable-next=too-many-arguments,too-many-locals
def read_backlog_from_jira(
        connections: JiraConnections, preset_name: str, *,
        filter_override: Optional[str] = None, levels: Optional[Levels] = None,
        status_map: Optional[dict[str, Status]] = None,
        stderr_file: TextIO = sys.stderr) -> BacklogReleases:
    """Read a backlog and its releases from Jira using a named preset.

    The preset names the connection and the backlog and release column
    maps, all looked up in the pool's configuration. The client is taken
    from ``connections``, so repeated reads and writes reuse it. The
    issues come from the resolved filter and the releases from the default
    project's versions.

    Args:
        connections: The pool of live Jira clients and the configuration
            holding the preset, connection and column maps.
        preset_name: The name of the from-Jira preset to use.
        filter_override: A Jira filter to use instead of the preset's.
        levels: The levels used to resolve a string level, or None for the
            default levels.
        status_map: Extra status names mapped to Status members, or None.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The backlog and releases read from Jira.

    Raises:
        KeyError: If the preset or a referenced connection or map is
            missing.
        ValueError: If no filter and no default project are configured.
    """
    jira_config = connections.jira_config
    preset = jira_config.get_preset(preset_name)
    client = connections.client(preset.connection_name)
    backlog_map = jira_config.backlog_column_maps[
        preset.backlog_column_map_name]
    release_map = jira_config.release_column_maps[
        preset.release_column_map_name]
    jql = resolve_jql(preset, filter_override)
    fields_list = client.fields()
    custom_ids = _custom_ids(fields_list)
    is_cloud = jira_config.connections[
        preset.connection_name].jira_type is JiraType.CLOUD
    issues = search_all_issues(client, is_cloud, jql,
                               _search_fields(backlog_map, custom_ids),
                               stderr_file=stderr_file)
    versions = client.project_versions(preset.def_project)
    return build_backlog_releases(issues, versions, fields_list,
                                  backlog_map=backlog_map,
                                  release_map=release_map, levels=levels,
                                  status_map=status_map,
                                  stderr_file=stderr_file)


def read_jira_from_config(config: BacklogOpsConfig, preset_name: str, *,
                          filter_override: Optional[str] = None,
                          passphrase: Optional[Callable[[], str]] = None,
                          stderr_file: TextIO = sys.stderr) -> BacklogReleases:
    """Read from Jira using the config's Jira settings, levels and status map.

    A fresh :class:`JiraConnections` pool is opened for the read. A caller
    that reads and writes several times should instead build one pool and
    pass it to :func:`read_backlog_from_jira` and
    :func:`backlogops.jira_write.add_backlog_to_jira` to reuse connections.

    Args:
        config: The backlog-ops configuration to take the Jira settings,
            levels and status map from.
        preset_name: The name of the from-Jira preset to use.
        filter_override: A Jira filter to use instead of the preset's.
        passphrase: Called to obtain the pass phrase for an encrypted
            token; not called for a clear token.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The backlog and releases read from Jira.
    """
    connections = JiraConnections(config.get_jira_config(), passphrase)
    return read_backlog_from_jira(connections, preset_name,
                                  filter_override=filter_override,
                                  levels=config.get_levels(),
                                  status_map=config.get_status_input_map(),
                                  stderr_file=stderr_file)
