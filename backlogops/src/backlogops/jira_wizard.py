#! /usr/local/bin/python3
"""Interactively collect the Jira input and output configuration.

The :func:`_build_jira_config` helper drives any ``WizardUiBridge`` to ask
for the named Jira connections, the named column maps, and the named
from-Jira read presets, returning a :class:`JiraIOConfig`. It is used by
the full configuration wizard in :mod:`backlogops.backlog_ops_wizard`.

The API token is captured in the wizard only for an internal storage mode,
where the token must live in the configuration; for a file storage mode
only the token file path is asked and the user places the file. An
encrypted internal token is encrypted with a pass phrase entered in the
wizard. Wizard input is not masked, so the token and pass phrase are
visible while typed.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from enum import Enum
from typing import TypeVar
from backlogops.jira_io_config import DEF_BACKLOG_COLUMN_MAP, \
    DEF_RELEASE_COLUMN_MAP, JiraColumnMap, JiraConnectConfig, JiraIOConfig, \
    JiraPreset, JiraType, TokenStorage
from backlogops.table_rows import BACKLOG_FIELDS, RELEASE_FIELDS
from backlogops.wizard_helpers import _Navigator

_E = TypeVar('_E', bound=Enum)


def _ask_enum(nav: _Navigator, question: str, enum_cls: type[_E],
              default: _E) -> _E:
    """Ask the user to pick one member of an enum by its lower-case name."""
    choices = [member.name.lower() for member in enum_cls]
    answer = nav.ask_choice(question, choices, default=default.name.lower())
    return enum_cls[answer.upper()]


def _build_jira_config(nav: _Navigator) -> JiraIOConfig:
    """Ask for the Jira connections, column maps and read presets."""
    jira = JiraIOConfig(stderr_file=nav.error_file())
    jira.connections = nav.level(lambda: _build_connections(nav))
    jira.column_maps = nav.level(lambda: _build_column_maps(nav))
    if jira.connections and jira.column_maps:
        jira.from_jira_presets = nav.level(
            lambda: _build_jira_presets(nav, jira.connections,
                                        jira.column_maps))
    elif jira.connections or jira.column_maps:
        nav.show('A Jira read preset needs at least one connection and one '
                 'column map; skipping presets.')
    return jira


def _build_connections(nav: _Navigator) -> dict[str, JiraConnectConfig]:
    """Ask for a counted list of named Jira connections."""
    count = nav.ask_count('Number of Jira connections')
    used: set[str] = set()
    result: dict[str, JiraConnectConfig] = {}
    for _ in range(count):
        name, connection = nav.level(lambda: _ask_connection(nav, used))
        used.add(name)
        result[name] = connection
    return result


def _ask_connection(nav: _Navigator,
                    used: set[str]) -> tuple[str, JiraConnectConfig]:
    """Ask one Jira connection: name, type, URL, email and token storage."""
    name = nav.ask_preset_name('Connection name (letters and digits)', used)
    connection = JiraConnectConfig(stderr_file=nav.error_file())
    connection.jira_type = _ask_enum(nav, 'Jira deployment type', JiraType,
                                     JiraType.CLOUD)
    connection.base_url = nav.ask_text('Jira base URL')
    connection.login_email = nav.ask_text('Login email')
    connection.token_storage = _ask_enum(nav, 'API token storage',
                                         TokenStorage, TokenStorage.CLEAR_FILE)
    _set_token(nav, connection)
    return name, connection


def _set_token(nav: _Navigator, connection: JiraConnectConfig) -> None:
    """Ask the token file path, or the token itself for an internal mode."""
    if connection.uses_token_file():
        connection.token_file_path = nav.ask_text('Token file path')
        return
    token = nav.ask_text('API token (visible while typed)')
    if connection.uses_encryption():
        phrase = nav.ask_text('Pass phrase to encrypt the token')
        connection.set_token(token, lambda: phrase, nav.error_file())
    else:
        connection.set_token(token, None, nav.error_file())


def _build_column_maps(nav: _Navigator) -> dict[str, JiraColumnMap]:
    """Ask for a counted list of named Jira column maps."""
    count = nav.ask_count('Number of Jira column maps')
    used: set[str] = set()
    result: dict[str, JiraColumnMap] = {}
    for _ in range(count):
        name, column_map = nav.level(lambda: _ask_column_map(nav, used))
        used.add(name)
        result[name] = column_map
    return result


def _ask_column_map(nav: _Navigator,
                    used: set[str]) -> tuple[str, JiraColumnMap]:
    """Ask one named column map, seeded from the backlog or release default."""
    name = nav.ask_preset_name('Column map name (letters and digits)', used)
    kind = nav.ask_choice('Map for the backlog or the releases',
                          ['backlog', 'release'], default='backlog')
    if kind == 'release':
        column_map = nav.ask_jira_map(list(RELEASE_FIELDS),
                                      DEF_RELEASE_COLUMN_MAP)
    else:
        column_map = nav.ask_jira_map(list(BACKLOG_FIELDS),
                                      DEF_BACKLOG_COLUMN_MAP)
    return name, column_map


def _build_jira_presets(nav: _Navigator,
                        connections: dict[str, JiraConnectConfig],
                        column_maps: dict[str, JiraColumnMap]
                        ) -> dict[str, JiraPreset]:
    """Ask for a counted list of named from-Jira read presets."""
    count = nav.ask_count('Number of Jira read presets')
    used: set[str] = set()
    conn_names = sorted(connections)
    map_names = sorted(column_maps)
    result: dict[str, JiraPreset] = {}
    for _ in range(count):
        name, preset = nav.level(
            lambda: _ask_jira_preset(nav, used, conn_names, map_names))
        used.add(name)
        result[name] = preset
    return result


def _ask_jira_preset(nav: _Navigator, used: set[str], conn_names: list[str],
                     map_names: list[str]) -> tuple[str, JiraPreset]:
    """Ask one read preset: name, connection, column maps and defaults."""
    name = nav.ask_preset_name('Preset name (letters and digits)', used)
    preset = JiraPreset(stderr_file=nav.error_file())
    preset.connection_name = nav.ask_choice('Connection to use', conn_names,
                                            default=conn_names[0])
    preset.column_map_name = nav.ask_choice('Backlog column map', map_names,
                                            default=map_names[0])
    release = nav.ask_choice('Release column map', map_names,
                             default=map_names[0])
    preset.release_column_map_name = release
    preset.def_project = nav.ask_text('Default Jira project key')
    preset.def_filter = nav.ask_text('Default issue filter (JQL)',
                                     allow_empty=True)
    return name, preset
