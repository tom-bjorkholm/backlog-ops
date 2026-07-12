#! /usr/local/bin/python3
"""Interactively collect the Jira input and output configuration.

The :func:`_build_jira_config` helper drives any ``WizardUiBridge`` to ask
for the named Jira connections, the named backlog and release column maps,
the named level-to-issue-type write maps, and the named presets that tie
them together, returning a :class:`JiraIOConfig`. It is used by the full
configuration wizard in :mod:`backlogops.backlog_ops_wizard`, which passes
in the configured levels so the issue-type map can be seeded from them.

Each connection and each preset is asked as one :meth:`_Navigator.ask_form`
screen, so the related fields are answered together. The connection form's
rule shows the token file path only for a file storage mode, the API token
only for an internal mode, and the two masked pass phrases only for the
internal encrypted mode, requiring the two pass phrases to match. The API
token itself is captured in the wizard only for an internal storage mode,
where the token must live in the configuration; for a file storage mode
only the token file path is asked and the user places the file. The API
token is visible while typed; the pass phrases are masked.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass
from typing import Callable, Optional, TypeVar
from backlogops.jira_io_config import DEF_BACKLOG_COLUMN_MAP, \
    DEF_RELEASE_COLUMN_MAP, JiraColumnMap, JiraConnectConfig, JiraIOConfig, \
    JiraIssueTypeMap, JiraPreset, JiraType, TokenStorage, _FILE_MODES, \
    default_jira_filter
from backlogops.levels import Levels
from backlogops.table_rows import BACKLOG_FIELDS, RELEASE_FIELDS
from backlogops.wizard_forms import FormField, FormResult, choice_field, \
    name_field, opt_text_field, secret_field, text_field, yes_no_field
from backlogops.wizard_helpers import _Navigator

_T = TypeVar('_T')


@dataclass(frozen=True)
class _PresetChoices:
    """The named connections and maps a Jira preset may choose among."""

    connections: list[str]
    backlog_maps: list[str]
    release_maps: list[str]
    issue_type_maps: list[str]


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


def _build_jira_config(nav: _Navigator, levels: Levels) -> JiraIOConfig:
    """Ask for the Jira connections, maps, issue types and presets."""
    jira = JiraIOConfig(stderr_file=nav.error_file())
    jira.connections = nav.level(lambda: _build_connections(nav))
    jira.backlog_column_maps = nav.level(lambda: _build_backlog_maps(nav))
    jira.release_column_maps = nav.level(lambda: _build_release_maps(nav))
    jira.issue_type_maps = nav.level(
        lambda: _build_issue_type_maps(nav, levels))
    _build_presets(nav, jira)
    return jira


def _build_issue_type_maps(nav: _Navigator,
                           levels: Levels) -> dict[str, JiraIssueTypeMap]:
    """Ask for a counted list of named level-to-issue-type write maps."""
    return _counted_named(nav, 'issue type maps',
                          lambda used: _ask_issue_type_map(nav, used, levels))


def _ask_issue_type_map(nav: _Navigator, used: set[str],
                        levels: Levels) -> tuple[str, JiraIssueTypeMap]:
    """Ask one named level-to-issue-type write map, seeded from levels."""
    name = nav.ask_preset_name('Issue type map name (letters and digits)',
                               used)
    return name, nav.ask_issue_type_map(levels)


def _build_presets(nav: _Navigator, jira: JiraIOConfig) -> None:
    """Ask the Jira presets when the prerequisites exist.

    A preset needs a connection, a backlog column map and a release column
    map; a level-to-issue-type map is optional. When some but not all of
    the required parts exist the presets are skipped with a note; when none
    exist the Jira section stays empty.
    """
    choices = _PresetChoices(connections=sorted(jira.connections),
                             backlog_maps=sorted(jira.backlog_column_maps),
                             release_maps=sorted(jira.release_column_maps),
                             issue_type_maps=sorted(jira.issue_type_maps))
    if not (choices.connections and choices.backlog_maps
            and choices.release_maps):
        if (choices.connections or choices.backlog_maps
                or choices.release_maps):
            nav.show('A Jira preset needs a connection, a backlog column '
                     'map and a release column map; skipping presets.')
        return
    jira.presets = nav.level(lambda: _build_preset_list(nav, choices))


def _build_connections(nav: _Navigator) -> dict[str, JiraConnectConfig]:
    """Ask for a counted list of named Jira connections."""
    return _counted_named(nav, 'connections',
                          lambda used: _ask_connection(nav, used))


def _enum_choices(enum_cls: type[JiraType] | type[TokenStorage]) -> list[str]:
    """Return the lower-case names of an enum as choice-field options."""
    return [member.name.lower() for member in enum_cls]


def _connection_fields(used: set[str]) -> list[FormField]:
    """Return the fields of the one-screen Jira connection form.

    The token file path is only relevant for a file storage mode, the API
    token only for an internal mode, and the two masked pass phrases only
    for the internal encrypted mode; the connection rule disables the rows
    that the chosen storage mode makes irrelevant.
    """
    return [
        name_field('name', 'Connection name (letters and digits)', used),
        choice_field('jira_type', 'Jira deployment type',
                     _enum_choices(JiraType),
                     default=JiraType.CLOUD.name.lower()),
        text_field('base_url', 'Jira base URL'),
        text_field('login_email', 'Login email'),
        choice_field('token_storage', 'API token storage',
                     _enum_choices(TokenStorage),
                     default=TokenStorage.CLEAR_FILE.name.lower()),
        text_field('token_file_path', 'Token file path'),
        text_field('api_token', 'API token (visible while typed)'),
        secret_field('passphrase', 'Pass phrase to encrypt the token'),
        secret_field('confirm', 'Re-enter the pass phrase')
    ]


def _connection_rule(values: FormResult) -> tuple[Optional[str], set[str]]:
    """Disable the irrelevant token rows and check the two pass phrases."""
    storage = TokenStorage[values.text('token_storage').upper()]
    file_mode = storage in _FILE_MODES
    encrypted = storage is TokenStorage.ENCRYPTED_INTERNAL
    return (_phrase_error(values, encrypted),
            _connection_disabled(file_mode, encrypted))


def _connection_disabled(file_mode: bool, encrypted: bool) -> set[str]:
    """Return the connection rows irrelevant to the chosen storage mode."""
    disabled = {'api_token'} if file_mode else {'token_file_path'}
    if not encrypted:
        disabled.update({'passphrase', 'confirm'})
    return disabled


def _phrase_error(values: FormResult, encrypted: bool) -> Optional[str]:
    """Return a message when the two pass phrases differ, else None."""
    if not encrypted:
        return None
    first = values.opt_text('passphrase')
    second = values.opt_text('confirm')
    if first is not None and second is not None and first != second:
        return 'The two pass phrases must be identical.'
    return None


def _ask_connection(nav: _Navigator,
                    used: set[str]) -> tuple[str, JiraConnectConfig]:
    """Ask one Jira connection and its token storage on a single form."""
    values = nav.ask_form('Configure the Jira connection.',
                          _connection_fields(used), _connection_rule)
    connection = JiraConnectConfig(stderr_file=nav.error_file())
    connection.jira_type = JiraType[values.text('jira_type').upper()]
    connection.base_url = values.text('base_url')
    connection.login_email = values.text('login_email')
    connection.token_storage = TokenStorage[values.text('token_storage')
                                            .upper()]
    _store_token(nav, connection, values)
    return values.text('name'), connection


def _store_token(nav: _Navigator, connection: JiraConnectConfig,
                 values: FormResult) -> None:
    """Store the token from the form, by file path or internal storage."""
    if connection.uses_token_file():
        connection.token_file_path = values.text('token_file_path')
        return
    connection.set_token(values.text('api_token'),
                         _token_phrase(connection, values), nav.error_file())


def _token_phrase(connection: JiraConnectConfig,
                  values: FormResult) -> Optional[Callable[[], str]]:
    """Return a pass-phrase supplier for an encrypted token, else None."""
    if not connection.uses_encryption():
        return None
    phrase = values.text('passphrase')
    return lambda: phrase


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


def _build_preset_list(nav: _Navigator,
                       choices: _PresetChoices) -> dict[str, JiraPreset]:
    """Ask for a counted list of named Jira presets."""
    return _counted_named(nav, 'presets',
                          lambda used: _ask_preset(nav, used, choices))


_WRITE_MAP_Q = ('Use a separate backlog column map for writing (otherwise '
                'the read map is used)?')
"""Form question offering a separate backlog write map."""

_ISSUE_MAP_Q = ('Use a level-to-issue-type map when writing (otherwise the '
                'level name is the issue type)?')
"""Form question offering a level-to-issue-type write map."""

_FILTER_HELP = 'Leave blank to rank the default project by rank order.'
"""Help shown for the blank-defaulting issue filter field."""


def _issue_type_field(choices: _PresetChoices) -> FormField:
    """Return the choice field for the level-to-issue-type write map."""
    maps = choices.issue_type_maps
    return choice_field('issue_type_map', 'Level-to-issue-type map for '
                        'writing', maps, default=maps[0])


def _preset_fields(used: set[str], choices: _PresetChoices) -> list[FormField]:
    """Return the fields of the one-screen Jira preset form.

    The write-map choice is disabled unless a separate write map is asked
    for, and the level-to-issue-type rows appear and are enabled only when
    issue-type maps exist and the user opts to use one.
    """
    fields = [
        name_field('name', 'Preset name (letters and digits)', used),
        choice_field('connection', 'Connection to use', choices.connections,
                     default=choices.connections[0]),
        choice_field('backlog_map', 'Backlog column map (read)',
                     choices.backlog_maps, default=choices.backlog_maps[0]),
        yes_no_field('separate_write', _WRITE_MAP_Q, False),
        choice_field('write_map', 'Backlog column map for writing',
                     choices.backlog_maps, default=choices.backlog_maps[0]),
        choice_field('release_map', 'Release column map', choices.release_maps,
                     default=choices.release_maps[0])]
    if choices.issue_type_maps:
        fields.append(yes_no_field('use_issue_type', _ISSUE_MAP_Q, False))
        fields.append(_issue_type_field(choices))
    fields.append(text_field('def_project', 'Default Jira project key'))
    fields.append(opt_text_field('def_filter', 'Default issue filter (JQL)',
                                 help_text=_FILTER_HELP))
    return fields


def _preset_rule(has_issue_type: bool
                 ) -> Callable[[FormResult], tuple[Optional[str], set[str]]]:
    """Return a rule that disables the write and issue-type rows when off."""
    def rule(values: FormResult) -> tuple[Optional[str], set[str]]:
        """Disable the optional map rows the user has switched off."""
        disabled: set[str] = set()
        if not values.flag('separate_write'):
            disabled.add('write_map')
        if has_issue_type and not values.flag('use_issue_type'):
            disabled.add('issue_type_map')
        return None, disabled
    return rule


def _ask_preset(nav: _Navigator, used: set[str],
                choices: _PresetChoices) -> tuple[str, JiraPreset]:
    """Ask one preset on a single form: name, connection, maps and filter."""
    values = nav.ask_form('Configure the Jira preset.',
                          _preset_fields(used, choices),
                          _preset_rule(bool(choices.issue_type_maps)))
    return _preset_from(nav, values, choices)


def _preset_from(nav: _Navigator, values: FormResult,
                 choices: _PresetChoices) -> tuple[str, JiraPreset]:
    """Build a named preset from the answers of the preset form."""
    preset = JiraPreset(stderr_file=nav.error_file())
    preset.connection_name = values.text('connection')
    preset.backlog_column_map_name = values.text('backlog_map')
    preset.backlog_write_map_name = _write_map_name(values)
    preset.release_column_map_name = values.text('release_map')
    preset.issue_type_map_name = _issue_map_name(values, choices)
    preset.def_project = values.text('def_project')
    preset.def_filter = _preset_filter(values)
    return values.text('name'), preset


def _write_map_name(values: FormResult) -> str:
    """Return the chosen backlog write map, or empty to reuse the read map."""
    return values.text('write_map') if values.flag('separate_write') else ''


def _issue_map_name(values: FormResult, choices: _PresetChoices) -> str:
    """Return the chosen issue-type map, or empty when none is used."""
    if not choices.issue_type_maps or not values.flag('use_issue_type'):
        return ''
    return values.text('issue_type_map')


def _preset_filter(values: FormResult) -> str:
    """Return the entered filter, or the project rank filter when blank."""
    entered = values.opt_text('def_filter')
    if entered:
        return entered
    return default_jira_filter(values.text('def_project'))
