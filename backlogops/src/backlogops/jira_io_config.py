#! /usr/local/bin/python3
"""Jira input and output configuration stored as config-as-json.

A :class:`JiraIOConfig` is the ``jira`` member of the top-level
:class:`backlogops.backlog_ops_config.BacklogOpsConfig`. It groups three
named, reusable parts:

* ``connections`` are named :class:`JiraConnectConfig` objects, each
  describing one Jira server and how its API token is stored;
* ``column_maps`` are named :data:`JiraColumnMap` maps from an internal
  field name to the :class:`JiraAttrPath` that reaches the value on a
  Jira issue or version;
* ``from_jira_presets`` are named :class:`JiraPreset` objects that tie a
  connection, a backlog column map and a release column map together with
  a default project and a default issue filter for reading from Jira.

Keeping the connections and column maps in their own dictionaries lets
several presets share one connection or one map. A preset refers to them
by name, and :meth:`JiraIOConfig.check_consistency` rejects a preset that
refers to a name that is not defined.

The API token is never written into the configuration file in clear text
unless the user explicitly chooses a clear storage mode (meant for demo
data). The token itself is materialized only at use time by
:meth:`JiraConnectConfig.get_token`, into a private attribute that
config-as-json does not serialize.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Callable, Optional, TextIO, override
from config_as_json import CallingWholeConfigValidator, Config, \
    ConfigAutoChangeHook, ConfigNesting, ConfigNestingKind, ConfigPath, \
    JsonType, MemberValidationStep, MemberValidator, NestedConfigs, \
    ParseConverter, PathOrStr, ReadOldConfiguration, SerializeConverter, \
    SerializeConverters, ValidationPlan, ValueTypeValidator, \
    WholeConfigValidationStep
from backlogops.backlog_helpers import convert_to_enum, report_bad_value, \
    report_wrong_type
from backlogops.jira_token import decrypt_token, encrypt_token


class JiraType(Enum):
    """Jira deployment type, cloud or server."""

    CLOUD = auto()
    SERVER = auto()


class TokenStorage(Enum):
    """How the Jira API token is stored.

    A ``CLEAR`` mode stores the token unprotected and is meant for demo
    data only. An ``ENCRYPTED`` mode stores the token encrypted with a
    pass phrase the user supplies when the token is stored and when it is
    used. A ``FILE`` mode keeps the token in a separate file named by
    ``token_file_path``; an ``INTERNAL`` mode keeps it in the
    configuration itself.
    """

    CLEAR_FILE = auto()
    ENCRYPTED_FILE = auto()
    CLEAR_INTERNAL = auto()
    ENCRYPTED_INTERNAL = auto()


_CLEAR_MODES = (TokenStorage.CLEAR_FILE, TokenStorage.CLEAR_INTERNAL)
"""Storage modes that keep the token in clear text."""

_FILE_MODES = (TokenStorage.CLEAR_FILE, TokenStorage.ENCRYPTED_FILE)
"""Storage modes that keep the token in a separate file."""

_ENCRYPTED_MODES = (TokenStorage.ENCRYPTED_FILE,
                    TokenStorage.ENCRYPTED_INTERNAL)
"""Storage modes that keep the token encrypted with a pass phrase."""

CLEAR_TOKEN_WARNING = (
    'WARNING: storing a Jira API token in clear text is insecure. Use it '
    'for demonstration data only, never for production credentials.')
"""Warning shown when a token is stored with a clear storage mode."""


class JiraAttrType(Enum):
    """Where the value of a mapped column is found on a Jira object.

    ATTRIBUTE is a direct attribute of the issue or version object, such
    as ``issue.key`` or ``version.releaseDate``. FIELD is reached under
    ``issue.fields`` by the remaining path steps, such as
    ``issue.fields.status.name``. CUSTOM_FIELD is a custom field named by
    its id (``customfield_10016``) or by its display name (``Story point
    estimate``); the display name is resolved against the live custom
    field mapping when reading.
    """

    ATTRIBUTE = auto()
    FIELD = auto()
    CUSTOM_FIELD = auto()


@dataclass(frozen=True)
class JiraAttrPath:
    """A path to the value of one column on a Jira issue or version.

    Fields:
        kind: How the path is interpreted, as documented for
            :class:`JiraAttrType`.
        path: The path steps. ATTRIBUTE and CUSTOM_FIELD use exactly one
            step; FIELD uses one or more steps reached under
            ``issue.fields``.
    """

    kind: JiraAttrType
    path: tuple[str, ...]


type JiraColumnMap = dict[str, JiraAttrPath]
"""Map from an internal field name to the Jira attribute path for it.

The key is the internal backlog or release field name. The value is the
:class:`JiraAttrPath` that reaches the matching value on a Jira issue or
version. Internal fields that are not mapped are not read.
"""


DEF_BACKLOG_COLUMN_MAP: JiraColumnMap = {
    'key': JiraAttrPath(JiraAttrType.ATTRIBUTE, ('key',)),
    'title': JiraAttrPath(JiraAttrType.FIELD, ('summary',)),
    'status': JiraAttrPath(JiraAttrType.FIELD, ('status', 'name')),
    'story_points': JiraAttrPath(JiraAttrType.CUSTOM_FIELD,
                                 ('Story point estimate',))}
"""A usable default backlog column map for a fresh Jira preset."""


DEF_RELEASE_COLUMN_MAP: JiraColumnMap = {
    'name': JiraAttrPath(JiraAttrType.ATTRIBUTE, ('name',)),
    'planned_date': JiraAttrPath(JiraAttrType.ATTRIBUTE, ('releaseDate',))}
"""A usable default release column map for a fresh Jira preset."""


def _as_step(name: str, value: object, stderr_file: TextIO) -> str:
    """Return one Jira attribute path step, rejecting a non-string."""
    if not isinstance(value, str):
        report_wrong_type(name, value, str, stderr_file, 'Jira column map')
    return value


def _check_arity(name: str, kind: JiraAttrType, steps: tuple[str, ...],
                 stderr_file: TextIO) -> None:
    """Check the number of path steps matches the attribute kind."""
    if kind is not JiraAttrType.FIELD and len(steps) != 1:
        report_bad_value(name, list(steps),
                         f'{kind.name} needs exactly one path step',
                         stderr_file, 'Jira column map')


def _attr_path_from_obj(name: str, value: object,
                        stderr_file: TextIO) -> JiraAttrPath:
    """Return a JiraAttrPath from a parsed JSON list, or pass one through."""
    if isinstance(value, JiraAttrPath):
        return value
    if not isinstance(value, (list, tuple)) or len(value) < 2:
        report_bad_value(name, value, 'a Jira attribute path must list a '
                         'kind and at least one path step', stderr_file,
                         'Jira column map')
    kind = convert_to_enum(name, value[0], JiraAttrType, stderr_file)
    assert isinstance(kind, JiraAttrType)
    steps = tuple(_as_step(f'{name}[{index}]', step, stderr_file)
                  for index, step in enumerate(value[1:], start=1))
    _check_arity(name, kind, steps, stderr_file)
    return JiraAttrPath(kind=kind, path=steps)


# pylint: disable-next=too-few-public-methods
class _ColumnMapsValidator(MemberValidator):
    """Validate and convert the named column maps member.

    The member maps each map name to a map from an internal field name to
    a Jira attribute path written as a list of a kind and one or more
    path steps. The lists are converted to :class:`JiraAttrPath` objects;
    a value that is already a :class:`JiraAttrPath` is kept, so the
    validator is safe to run again before writing.
    """

    @override
    def validate_member(self, config: Config, member_name: str,
                        member_value: object,
                        stderr_file: TextIO = sys.stderr) -> object:
        """Return the column maps with each path as a JiraAttrPath."""
        _ = config
        if not isinstance(member_value, dict):
            report_wrong_type(member_name, member_value, dict, stderr_file,
                              'Jira column maps')
        result: dict[str, JiraColumnMap] = {}
        for map_name, mapping in member_value.items():
            sub = f'{member_name}[{map_name}]'
            result[map_name] = self._one_map(sub, mapping, stderr_file)
        return result

    @staticmethod
    def _one_map(name: str, mapping: object,
                 stderr_file: TextIO) -> JiraColumnMap:
        """Return one column map with each path as a JiraAttrPath."""
        if not isinstance(mapping, dict):
            report_wrong_type(name, mapping, dict, stderr_file,
                              'Jira column map')
        return {column: _attr_path_from_obj(f'{name}[{column}]', path,
                                            stderr_file)
                for column, path in mapping.items()}


def _column_maps_to_json(value: object, *, path_text: str, stderr_file: TextIO,
                         **_extra: object) -> JsonType:
    """Convert the column maps of JiraAttrPath values to JSON lists."""
    _ = path_text, stderr_file
    assert isinstance(value, dict)
    maps: dict[str, JsonType] = {}
    for map_name, mapping in value.items():
        assert isinstance(mapping, dict)
        columns: dict[str, JsonType] = {}
        for column, attr in mapping.items():
            assert isinstance(attr, JiraAttrPath)
            columns[column] = [attr.kind.name, *attr.path]
        maps[map_name] = columns
    return maps


class JiraConnectConfig(Config):
    """Connection to one Jira server and how its API token is stored.

    The connection holds the deployment type, the base URL and the login
    email, plus the chosen :class:`TokenStorage`. For a file storage mode
    the token lives in the file named by ``token_file_path``; for an
    internal storage mode it lives in ``stored_token`` (clear text for a
    clear mode, an encrypted blob for an encrypted mode). The clear text
    token is materialized on demand by :meth:`get_token` into a private
    attribute that is never serialized.
    """

    jira_type: JiraType
    base_url: str
    login_email: str
    token_storage: TokenStorage
    token_file_path: Optional[str]
    stored_token: Optional[str]

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create connection defaults, then read them from JSON."""
        self.jira_type = JiraType.CLOUD
        self.base_url = ''
        self.login_email = ''
        self.token_storage = TokenStorage.CLEAR_FILE
        self.token_file_path = None
        self.stored_token = None
        self._cached_token: Optional[str] = None
        Config.__init__(self, from_json_data_text=from_json_data_text,
                        from_json_filename=from_json_filename,
                        auto_ch_hook=auto_ch_hook, stderr_file=stderr_file)

    @override
    def _omit_none_from_json(self) -> list[str]:
        """Omit the unused token reference members while they are None."""
        return ['token_file_path', 'stored_token']

    @override
    def parse_converters(self) -> dict[str, ParseConverter]:
        """Parse the enum members from their member names."""
        return {'jira_type': self.get_converter_dict(JiraType),
                'token_storage': self.get_converter_dict(TokenStorage)}

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check the base URL and the login email are strings."""
        _ = stderr_file
        return [MemberValidationStep(
            member_names=['base_url', 'login_email'],
            validator=ValueTypeValidator(value_type=str))]

    def get_token(self, passphrase: Optional[Callable[[], str]] = None,
                  stderr_file: TextIO = sys.stderr) -> str:
        """Return the clear text API token, materializing it once.

        The token is read from its file or internal storage and decrypted
        when an encrypted mode is used; the result is cached so a later
        call returns it without asking for the pass phrase again.

        Args:
            passphrase: Called to obtain the pass phrase for an encrypted
                mode. Not called for a clear mode.
            stderr_file: Stream used for user-facing diagnostics.

        Returns:
            The clear text API token.

        Raises:
            ValueError: If a needed token, file path or pass phrase is
                missing, or decryption fails.
        """
        _ = stderr_file
        if self._cached_token is None:
            self._cached_token = self._materialize_token(passphrase)
        return self._cached_token

    def set_token(self, token: str,
                  passphrase: Optional[Callable[[], str]] = None,
                  stderr_file: TextIO = sys.stderr) -> None:
        """Store a clear text API token according to the storage mode.

        For an encrypted mode the token is encrypted with the pass phrase;
        for a clear mode a strong warning is printed. The token is also
        cached so a following :meth:`get_token` returns it directly.

        Args:
            token: The clear text API token to store.
            passphrase: Called to obtain the pass phrase for an encrypted
                mode. Not called for a clear mode.
            stderr_file: Stream the clear-text warning is printed to.

        Raises:
            ValueError: If a needed file path or pass phrase is missing.
        """
        if self.token_storage in _CLEAR_MODES:
            print(CLEAR_TOKEN_WARNING, file=stderr_file)
        if self.token_storage in _FILE_MODES:
            self._write_token_file(self._for_storage(token, passphrase))
            self.stored_token = None
        else:
            self.stored_token = self._for_storage(token, passphrase)
            self.token_file_path = None
        self._cached_token = token

    def _materialize_token(self,
                           passphrase: Optional[Callable[[], str]]) -> str:
        """Return the clear text token from its storage, decrypting it."""
        stored = (self._read_token_file()
                  if self.token_storage in _FILE_MODES
                  else self._stored_token_value())
        if self.token_storage in _ENCRYPTED_MODES:
            return decrypt_token(stored, self._passphrase(passphrase))
        return stored

    def _for_storage(self, token: str,
                     passphrase: Optional[Callable[[], str]]) -> str:
        """Return the token as it should be stored for the storage mode."""
        if self.token_storage in _ENCRYPTED_MODES:
            return encrypt_token(token, self._passphrase(passphrase))
        return token

    def _stored_token_value(self) -> str:
        """Return the internally stored token, or raise when it is missing."""
        if self.stored_token is None:
            raise ValueError('No Jira token is stored in the configuration.')
        return self.stored_token

    def _token_file(self) -> Path:
        """Return the token file path, or raise when it is missing."""
        if self.token_file_path is None:
            raise ValueError('No Jira token file path is configured.')
        return Path(self.token_file_path).expanduser()

    def _read_token_file(self) -> str:
        """Return the stripped contents of the configured token file."""
        with open(self._token_file(), 'r', encoding='utf-8') as file:
            return file.read().strip()

    def _write_token_file(self, text: str) -> None:
        """Write the stored token text to the configured token file."""
        with open(self._token_file(), 'w', encoding='utf-8') as file:
            file.write(text)

    @staticmethod
    def _passphrase(passphrase: Optional[Callable[[], str]]) -> str:
        """Return the pass phrase from the provider, or raise when absent."""
        if passphrase is None:
            raise ValueError('A pass phrase is required for this Jira token.')
        return passphrase()


class JiraPreset(Config):
    """A named preset for reading a backlog and releases from Jira.

    The preset names the connection to use, the backlog and release
    column maps to use, the default project key, and the default issue
    filter (Jira Query Language). The names refer to entries in the
    enclosing :class:`JiraIOConfig`. The default project is used to read
    the releases (versions) even when the caller overrides the issue
    filter.
    """

    connection_name: str
    column_map_name: str
    release_column_map_name: str
    def_project: str
    def_filter: str

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create preset defaults, then read them from JSON."""
        self.connection_name = ''
        self.column_map_name = ''
        self.release_column_map_name = ''
        self.def_project = ''
        self.def_filter = ''
        Config.__init__(self, from_json_data_text=from_json_data_text,
                        from_json_filename=from_json_filename,
                        auto_ch_hook=auto_ch_hook, stderr_file=stderr_file)

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check every preset member is a string."""
        _ = stderr_file
        return [MemberValidationStep(
            member_names=['connection_name', 'column_map_name',
                          'release_column_map_name', 'def_project',
                          'def_filter'],
            validator=ValueTypeValidator(value_type=str))]


class _JiraReadOldConfig(ReadOldConfiguration):
    """Default the jira sub-sections when an old file omits them."""

    def get_missing_path_values(self) -> dict[ConfigPath, object]:
        """Supply empty connection, column-map and preset maps."""
        return {('connections',): {}, ('column_maps',): {},
                ('from_jira_presets',): {}}


def _check_ref(preset_name: str, kind: str, ref: str,
               available: Mapping[str, object], stderr_file: TextIO) -> None:
    """Check a preset reference names a defined entry, or raise."""
    if ref not in available:
        known = ', '.join(sorted(available)) if available else 'none'
        message = (f'Jira preset {preset_name!r} refers to unknown {kind} '
                   f'{ref!r}. Defined: {known}.')
        print(message, file=stderr_file)
        raise KeyError(message)


class JiraIOConfig(Config):
    """Jira input and output configuration as the top-level jira member.

    Holds the named connections, the named column maps, and the named
    presets for reading from Jira, each indexed by name so that several
    presets can share one connection or one column map. The column maps
    are validated and converted to :class:`JiraAttrPath` values on read
    and written back as lists on write; an old file that omits any
    sub-section loads with that sub-section empty.
    """

    connections: dict[str, JiraConnectConfig]
    column_maps: dict[str, JiraColumnMap]
    from_jira_presets: dict[str, JiraPreset]

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create empty defaults, then read the jira configuration."""
        self.connections = {}
        self.column_maps = {}
        self.from_jira_presets = {}
        self._unchecked_dicts = ['column_maps']
        Config.__init__(self, from_json_data_text=from_json_data_text,
                        from_json_filename=from_json_filename,
                        auto_ch_hook=auto_ch_hook, stderr_file=stderr_file)

    @override
    def _get_read_old_config(self) -> ReadOldConfiguration:
        """Return the processor that defaults omitted sub-sections."""
        return _JiraReadOldConfig()

    @override
    def nested_configs(self) -> NestedConfigs:
        """Declare the connections and presets as nested configurations."""
        conn = ConfigNesting(kind=ConfigNestingKind.DICT_VALUE,
                             config_type=JiraConnectConfig)
        preset = ConfigNesting(kind=ConfigNestingKind.DICT_VALUE,
                               config_type=JiraPreset)
        return {'connections': conn, 'from_jira_presets': preset}

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Convert the column maps, then check the preset references."""
        _ = stderr_file
        consistency = CallingWholeConfigValidator('check_consistency')
        return [MemberValidationStep(member_names=['column_maps'],
                                     validator=_ColumnMapsValidator()),
                WholeConfigValidationStep(validator=consistency)]

    @override
    def serialize_converters(self) -> SerializeConverters:
        """Write the column maps as lists of a kind and path steps."""
        return {'column_maps': SerializeConverter(value_type=dict,
                                                  func=_column_maps_to_json,
                                                  args={})}

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check every preset refers to a defined connection and maps.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            KeyError: If a preset refers to a connection or column map
                name that is not defined.
        """
        for name, preset in self.from_jira_presets.items():
            _check_ref(name, 'connection', preset.connection_name,
                       self.connections, stderr_file)
            _check_ref(name, 'column map', preset.column_map_name,
                       self.column_maps, stderr_file)
            _check_ref(name, 'release column map',
                       preset.release_column_map_name, self.column_maps,
                       stderr_file)

    def get_preset(self, name: str) -> JiraPreset:
        """Return the named from-Jira preset.

        Args:
            name: The preset name.

        Returns:
            The named preset.

        Raises:
            KeyError: If no preset of that name is configured.
        """
        return self.from_jira_presets[name]
