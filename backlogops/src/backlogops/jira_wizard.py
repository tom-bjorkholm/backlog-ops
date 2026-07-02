#! /usr/local/bin/python3
"""Interactively collect the Jira input and output configuration.

The :func:`_build_jira_config` helper drives any ``WizardUiBridge`` to ask
for the named Jira connections, the named backlog and release column maps,
and the named from-Jira read presets and to-Jira write presets, returning
a :class:`JiraIOConfig`. It is used by the full configuration wizard in
:mod:`backlogops.backlog_ops_wizard`.

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
from typing import Callable, TypeVar
from backlogops.jira_io_config import DEF_BACKLOG_COLUMN_MAP, \
    DEF_RELEASE_COLUMN_MAP, JiraColumnMap, JiraConnectConfig, JiraIOConfig, \
    JiraPreset, JiraType, JiraWritePreset, TokenStorage, _JiraPresetBase, \
    default_jira_filter
from backlogops.table_rows import BACKLOG_FIELDS, RELEASE_FIELDS
from backlogops.wizard_helpers import _Navigator

_E = TypeVar('_E', bound=Enum)
_T = TypeVar('_T')


def _ask_enum(nav: _Navigator, question: str, enum_cls: type[_E],
              default: _E) -> _E:
    """Ask the user to pick one member of an enum by its lower-case name."""
    choices = [member.name.lower() for member in enum_cls]
    answer = nav.ask_choice(question, choices, default=default.name.lower())
    return enum_cls[answer.upper()]


def _counted_named(nav: _Navigator, what: str,
                   ask_one: Callable[[set[str]], tuple[str, _T]]
                   ) -> dict[str, _T]:
    """Ask a counted list of uniquely named items through ``ask_one``.

    The count question opens the section and each item is asked inside its
    own sub-level, so cancelling an item returns to the count question.
    Every accepted name is added to the set passed to ``ask_one`` so the
    next name must differ.
    """
    count = nav.ask_count(f'Number of Jira {what}')
    used: set[str] = set()
    result: dict[str, _T] = {}
    for _ in range(count):
        name, item = nav.level(lambda: ask_one(used))
        used.add(name)
        result[name] = item
    return result


def _build_jira_config(nav: _Navigator) -> JiraIOConfig:
    """Ask for the Jira connections, column maps and read/write presets."""
    jira = JiraIOConfig(stderr_file=nav.error_file())
    jira.connections = nav.level(lambda: _build_connections(nav))
    jira.backlog_column_maps = nav.level(lambda: _build_backlog_maps(nav))
    jira.release_column_maps = nav.level(lambda: _build_release_maps(nav))
    _build_presets(nav, jira)
    return jira


def _build_presets(nav: _Navigator, jira: JiraIOConfig) -> None:
    """Ask the read and write presets when the prerequisites exist.

    A preset needs a connection, a backlog column map and a release column
    map. When some but not all of these exist the presets are skipped with
    a note; when none exist the Jira section stays empty.
    """
    conn = sorted(jira.connections)
    backlog = sorted(jira.backlog_column_maps)
    release = sorted(jira.release_column_maps)
    if not (conn and backlog and release):
        if conn or backlog or release:
            nav.show('A Jira preset needs a connection, a backlog column '
                     'map and a release column map; skipping presets.')
        return
    jira.from_jira_presets = nav.level(
        lambda: _build_from_presets(nav, conn, backlog, release))
    jira.to_jira_presets = nav.level(
        lambda: _build_to_presets(nav, conn, backlog, release))


def _build_connections(nav: _Navigator) -> dict[str, JiraConnectConfig]:
    """Ask for a counted list of named Jira connections."""
    return _counted_named(nav, 'connections',
                          lambda used: _ask_connection(nav, used))


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


def _build_backlog_maps(nav: _Navigator) -> dict[str, JiraColumnMap]:
    """Ask for a counted list of named Jira backlog column maps."""
    return _counted_named(nav, 'backlog column maps',
                          lambda used: _ask_backlog_map(nav, used))


def _build_release_maps(nav: _Navigator) -> dict[str, JiraColumnMap]:
    """Ask for a counted list of named Jira release column maps."""
    return _counted_named(nav, 'release column maps',
                          lambda used: _ask_release_map(nav, used))


def _ask_backlog_map(nav: _Navigator,
                     used: set[str]) -> tuple[str, JiraColumnMap]:
    """Ask one named backlog column map, seeded from the backlog default."""
    return _ask_map(nav, used, 'Backlog', list(BACKLOG_FIELDS),
                    DEF_BACKLOG_COLUMN_MAP)


def _ask_release_map(nav: _Navigator,
                     used: set[str]) -> tuple[str, JiraColumnMap]:
    """Ask one named release column map, seeded from the release default."""
    return _ask_map(nav, used, 'Release', list(RELEASE_FIELDS),
                    DEF_RELEASE_COLUMN_MAP)


def _ask_map(nav: _Navigator, used: set[str], label: str, fields: list[str],
             default: JiraColumnMap) -> tuple[str, JiraColumnMap]:
    """Ask one named Jira column map, seeded from ``default``."""
    name = nav.ask_preset_name(f'{label} column map name (letters and '
                               'digits)', used)
    return name, nav.ask_jira_map(fields, default)


def _build_from_presets(nav: _Navigator, conn: list[str], backlog: list[str],
                        release: list[str]) -> dict[str, JiraPreset]:
    """Ask for a counted list of named from-Jira read presets."""
    return _counted_named(
        nav, 'read presets',
        lambda used: _ask_from_preset(nav, used, conn, backlog, release))


def _build_to_presets(nav: _Navigator, conn: list[str], backlog: list[str],
                      release: list[str]) -> dict[str, JiraWritePreset]:
    """Ask for a counted list of named to-Jira write presets."""
    return _counted_named(
        nav, 'write presets',
        lambda used: _ask_to_preset(nav, used, conn, backlog, release))


def _ask_from_preset(nav: _Navigator, used: set[str], conn: list[str],
                     backlog: list[str],
                     release: list[str]) -> tuple[str, JiraPreset]:
    """Ask one read preset: name, connection, maps, project and filter."""
    name = nav.ask_preset_name('Read preset name (letters and digits)', used)
    preset = JiraPreset(stderr_file=nav.error_file())
    _fill_base_preset(nav, preset, conn, backlog, release)
    preset.def_filter = _ask_filter(nav, preset.def_project)
    return name, preset


def _ask_to_preset(nav: _Navigator, used: set[str], conn: list[str],
                   backlog: list[str],
                   release: list[str]) -> tuple[str, JiraWritePreset]:
    """Ask one write preset: name, connection, maps and project."""
    name = nav.ask_preset_name('Write preset name (letters and digits)', used)
    preset = JiraWritePreset(stderr_file=nav.error_file())
    _fill_base_preset(nav, preset, conn, backlog, release)
    return name, preset


def _fill_base_preset(nav: _Navigator, preset: _JiraPresetBase,
                      conn: list[str], backlog: list[str],
                      release: list[str]) -> None:
    """Fill the shared preset fields: connection, maps and project."""
    preset.connection_name = _choice(nav, 'Connection to use', conn)
    preset.backlog_column_map_name = _choice(nav, 'Backlog column map',
                                             backlog)
    preset.release_column_map_name = _choice(nav, 'Release column map',
                                             release)
    preset.def_project = nav.ask_text('Default Jira project key')


def _choice(nav: _Navigator, question: str, choices: list[str]) -> str:
    """Ask a choice among ``choices``, defaulting to the first option."""
    return nav.ask_choice(question, choices, default=choices[0])


def _ask_filter(nav: _Navigator, project: str) -> str:
    """Ask the default issue filter, suggesting the project filter."""
    if project:
        return nav.ask_text('Default issue filter (JQL)',
                            default=default_jira_filter(project))
    return nav.ask_text('Default issue filter (JQL)', allow_empty=True)
