#! /usr/local/bin/python3
"""Read a backlog and its releases from Jira into BacklogReleases.

A configured :class:`JiraPreset` names the connection, the backlog and
release column maps, the default project and the default issue filter.
:func:`read_backlog_from_jira` connects to Jira, runs the issue
filter (Jira Query Language) to read the backlog items, reads the project
versions to read the releases, and maps each Jira attribute to an
internal field through the preset's column maps. Custom field display
names in a column map (such as 'Story point estimate') are resolved to
their field ids through the live custom field list of the Jira instance.

The caller may override the preset's filter for one read. When no filter
is configured at all, the default filter selects every issue in the
default project, ordered by rank, while the releases always come from the
default project's versions.

A cloud connection authenticates with the login email and the token; a
server connection uses the token as a personal access token. The token
is materialized through :meth:`JiraConnectConfig.get_token`, asking the
supplied pass phrase provider only when an encrypted storage mode needs
it.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from collections.abc import Iterable, Mapping
from datetime import date
from typing import Callable, Optional, TextIO
from jira import JIRA
from backlogops.backlog import BacklogItem, Status
from backlogops.backlog_ops_config import BacklogOpsConfig
from backlogops.backlog_releases import BacklogReleases
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType, \
    JiraColumnMap, JiraConnectConfig, JiraIOConfig, JiraPreset, JiraType, \
    default_jira_filter
from backlogops.levels import Levels
from backlogops.releases import Release
from backlogops.table_rows import row_to_item, row_to_release


def _connect(connection: JiraConnectConfig,
             passphrase: Optional[Callable[[], str]]) -> JIRA:
    """Return a Jira client connected with the connection's token."""
    token = connection.get_token(passphrase)
    if connection.jira_type is JiraType.SERVER:
        return JIRA(server=connection.base_url, token_auth=token)
    return JIRA(server=connection.base_url,
                basic_auth=(connection.login_email, token))


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


def _field_id(name: str, custom_ids: dict[str, str]) -> Optional[str]:
    """Return the field id for a custom field given as id or display name."""
    if name.startswith('customfield_'):
        return name
    return custom_ids.get(name)


def _resolve(attr_root: object, field_root: object, attr: JiraAttrPath,
             custom_ids: dict[str, str]) -> object:
    """Return the value an attribute path reaches on a Jira object."""
    if attr.kind is JiraAttrType.ATTRIBUTE:
        return _walk(attr_root, attr.path)
    if attr.kind is JiraAttrType.FIELD:
        return _walk(field_root, attr.path)
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


def _row(attr_root: object, field_root: object, column_map: JiraColumnMap,
         custom_ids: dict[str, str]) -> dict[str, object]:
    """Return one Jira object as a row keyed by internal field name."""
    return {name: _coerce(_resolve(attr_root, field_root, attr, custom_ids))
            for name, attr in column_map.items()}


def _backlog_row(attr_root: object, field_root: object,
                 column_map: JiraColumnMap,
                 custom_ids: dict[str, str]) -> dict[str, object]:
    """Return one Jira issue row with Jira-specific defaults applied."""
    row = _row(attr_root, field_root, column_map, custom_ids)
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
                                 backlog_map, custom_ids), levels, status_map,
                    stderr_file)
        for issue in issues]
    releases: list[Release] = [
        row_to_release(_row(version, version, release_map, {}), stderr_file)
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


# pylint: disable-next=too-many-arguments
def read_backlog_from_jira(
        jira_config: JiraIOConfig, preset_name: str, *,
        filter_override: Optional[str] = None,
        passphrase: Optional[Callable[[], str]] = None,
        levels: Optional[Levels] = None,
        status_map: Optional[dict[str, Status]] = None,
        stderr_file: TextIO = sys.stderr) -> BacklogReleases:
    """Read a backlog and its releases from Jira using a named preset.

    The preset names the connection and the backlog and release column
    maps, all looked up in ``jira_config``. The issues come from the
    resolved filter and the releases from the default project's versions.

    Args:
        jira_config: The Jira configuration holding the preset, connection
            and column maps.
        preset_name: The name of the from-Jira preset to use.
        filter_override: A Jira filter to use instead of the preset's.
        passphrase: Called to obtain the pass phrase for an encrypted
            token; not called for a clear token.
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
    preset = jira_config.get_preset(preset_name)
    connection = jira_config.connections[preset.connection_name]
    backlog_map = jira_config.column_maps[preset.column_map_name]
    release_map = jira_config.column_maps[preset.release_column_map_name]
    jql = resolve_jql(preset, filter_override)
    client = _connect(connection, passphrase)
    issues = client.search_issues(jql, maxResults=False)
    versions = client.project_versions(preset.def_project)
    return build_backlog_releases(issues, versions, client.fields(),
                                  backlog_map=backlog_map,
                                  release_map=release_map, levels=levels,
                                  status_map=status_map,
                                  stderr_file=stderr_file)


def read_jira_from_config(config: BacklogOpsConfig, preset_name: str, *,
                          filter_override: Optional[str] = None,
                          passphrase: Optional[Callable[[], str]] = None,
                          stderr_file: TextIO = sys.stderr) -> BacklogReleases:
    """Read from Jira using the config's Jira settings, levels and status map.

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
    return read_backlog_from_jira(config.get_jira_config(), preset_name,
                                  filter_override=filter_override,
                                  passphrase=passphrase,
                                  levels=config.get_levels(),
                                  status_map=config.get_status_input_map(),
                                  stderr_file=stderr_file)
