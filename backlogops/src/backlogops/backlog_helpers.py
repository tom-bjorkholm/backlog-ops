#! /usr/local/bin/python3
"""Helpers for converting and validating backlog item data.

These helpers turn plain dictionaries into validated backlog field
values and report problems in a uniform way. They are deliberately
generic: they operate on values and type hints, not on the backlog item
class, so that the backlog module can use them without a circular
import.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from collections.abc import Callable, Sequence
from dataclasses import MISSING, Field
from datetime import date
from enum import Enum
from types import NoneType, UnionType
from typing import NoReturn, Optional, TextIO, TypeVar, Union
from typing import get_args, get_origin, get_type_hints
from config_as_json import string_to_enum_best_match

T = TypeVar('T')

FORBIDDEN_KEY_CHARS = frozenset(',.;:()[]{}')
"""Characters that must never appear in a key, release or dependency."""


def field_type_hints(cls: type) -> dict[str, object]:
    """Return the resolved type hints for the fields of a class.

    Postponed annotations and forward references are resolved, so that
    callers receive concrete type objects (for example ``date`` and
    ``Status``) instead of their string annotations.

    Args:
        cls: The class whose annotations should be resolved.

    Returns:
        A mapping from field name to its resolved type hint.
    """
    return dict(get_type_hints(cls))


def is_mandatory_field(item_field: Field[object]) -> bool:
    """Return True when a field must be supplied by the input data.

    A field is mandatory when it takes part in ``__init__`` and has
    neither a default value nor a default factory.

    Args:
        item_field: The dataclass field to inspect.

    Returns:
        True if the field has no default and must be supplied.
    """
    return (item_field.init and item_field.default is MISSING and
            item_field.default_factory is MISSING)


def enum_class_of(data_type: object) -> Optional[type[Enum]]:
    """Return the enum class of a type hint, or None.

    Args:
        data_type: The type hint to inspect.

    Returns:
        The enum class when ``data_type`` is an Enum subclass, else None.
    """
    if isinstance(data_type, type) and issubclass(data_type, Enum):
        return data_type
    return None


def is_union_type(data_type: object) -> bool:
    """Return True if a type hint is a ``Union`` or an ``X | Y`` union.

    Args:
        data_type: The type hint to inspect.

    Returns:
        True if the type hint is any kind of union.
    """
    return get_origin(data_type) in (Union, UnionType)


def non_optional_type(data_type: object) -> object:
    """Return the inner type of an ``Optional`` hint.

    For ``Optional[X]`` (that is ``Union[X, None]``) the wrapped type
    ``X`` is returned. For a union with several non-None members, or for
    a type hint that is not a union, the original hint is returned.

    Args:
        data_type: The type hint to unwrap.

    Returns:
        The single non-None union member, or the original type hint.
    """
    if not is_union_type(data_type):
        return data_type
    members = [arg for arg in get_args(data_type) if arg is not NoneType]
    return members[0] if len(members) == 1 else data_type


def accepts_none(data_type: object) -> bool:
    """Return True if ``None`` is a valid value for a type hint.

    Args:
        data_type: The type hint to inspect.

    Returns:
        True if the type hint is an optional or ``None`` accepting union.
    """
    return is_union_type(data_type) and NoneType in get_args(data_type)


def _matches_class(value: object, data_type: type) -> bool:
    """Return True if a value matches a plain (unparameterized) class.

    A boolean is rejected where an integer is expected, because a
    boolean is rarely a meaningful story point or numeric value here.
    """
    if data_type is int:
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, data_type)


def _matches_list(value: object, args: tuple[object, ...]) -> bool:
    """Return True if a value is a list whose items match the hint."""
    if not isinstance(value, list):
        return False
    return all(value_matches_type(item, args[0]) for item in value) \
        if args else True


def _matches_dict(value: object, args: tuple[object, ...]) -> bool:
    """Return True if a value is a dict matching the key/value hints."""
    if not isinstance(value, dict):
        return False
    if len(args) != 2:
        return True
    return all(value_matches_type(key, args[0]) and
               value_matches_type(item, args[1])
               for key, item in value.items())


def _matches_concrete(value: object, data_type: object) -> bool:
    """Return True if a non-None value matches a concrete type hint."""
    enum_class = enum_class_of(data_type)
    if enum_class is not None:
        return isinstance(value, enum_class)
    origin = get_origin(data_type)
    if origin is list:
        return _matches_list(value, get_args(data_type))
    if origin is dict:
        return _matches_dict(value, get_args(data_type))
    if isinstance(data_type, type):
        return _matches_class(value, data_type)
    return True


def value_matches_type(value: object, data_type: object) -> bool:
    """Return True if a value matches a supported type hint.

    Supported hints are ``object``, optional and union types, enums, and
    the ``str``, ``int``, ``date``, ``list[...]`` and ``dict[..., ...]``
    forms used by backlog items.

    Args:
        value: The runtime value to check.
        data_type: The type hint to check the value against.

    Returns:
        True if the value is acceptable for the given type hint.
    """
    if data_type is object:
        return True
    if is_union_type(data_type):
        return any(value_matches_type(value, arg)
                   for arg in get_args(data_type))
    if value is None:
        return data_type is NoneType
    return _matches_concrete(value, data_type)


def _type_name(data_type: object) -> str:
    """Return a readable name for a type hint, used in messages."""
    if data_type is object:
        return 'object'
    if isinstance(data_type, type):
        return data_type.__name__
    return str(data_type).replace('typing.', '')


def report_missing_field(field_name: str,
                         stderr_file: TextIO = sys.stderr) -> NoReturn:
    """Report a missing mandatory field and raise ``KeyError``.

    Args:
        field_name: The name of the missing field.
        stderr_file: The file to report the error to.

    Raises:
        KeyError: Always, after reporting the message.
    """
    message = f'Missing mandatory backlog item field: {field_name}'
    print(message, file=stderr_file)
    raise KeyError(message)


def report_wrong_type(field_name: str, value: object, data_type: object,
                      stderr_file: TextIO = sys.stderr,
                      subject: str = 'Backlog item') -> NoReturn:
    """Report a value of the wrong type and raise ``TypeError``.

    Args:
        field_name: The name of the offending field.
        value: The value that has the wrong type.
        data_type: The type hint the value was expected to match.
        stderr_file: The file to report the error to.
        subject: What owns the field, used to start the message (for
            example ``'Backlog item'``, ``'Person'`` or ``'Team'``).

    Raises:
        TypeError: Always, after reporting the message.
    """
    message = (f'{subject} field {field_name!r} expected '
               f'{_type_name(data_type)}, got {type(value).__name__}: '
               f'{value!r}')
    print(message, file=stderr_file)
    raise TypeError(message)


def report_bad_value(field_name: str, value: object, reason: str,
                     stderr_file: TextIO = sys.stderr,
                     subject: str = 'Backlog item') -> NoReturn:
    """Report a value that violates a constraint and raise ``ValueError``.

    Args:
        field_name: The name of the offending field.
        value: The value that violates the constraint.
        reason: A human readable explanation of the constraint.
        stderr_file: The file to report the error to.
        subject: What owns the field, used to start the message (for
            example ``'Backlog item'``, ``'Person'`` or ``'Team'``).

    Raises:
        ValueError: Always, after reporting the message.
    """
    message = (f'{subject} field {field_name!r} has invalid value '
               f'{value!r}: {reason}')
    print(message, file=stderr_file)
    raise ValueError(message)


def report_unknown_reference(field_name: str, owner_key: str,
                             referenced_key: str,
                             stderr_file: TextIO = sys.stderr,
                             subject: str = 'Backlog item') -> NoReturn:
    """Report a reference to a missing key and raise ``KeyError``.

    Args:
        field_name: The field that holds the reference.
        owner_key: The key of the item that owns the reference.
        referenced_key: The key that does not exist.
        stderr_file: The file to report the error to.
        subject: What owns the field, used to start the message (for
            example ``'Backlog item'`` or ``'Team'``).

    Raises:
        KeyError: Always, after reporting the message.
    """
    message = (f'{subject} {owner_key!r} field {field_name!r} '
               f'references unknown key {referenced_key!r}')
    print(message, file=stderr_file)
    raise KeyError(message)


def check_field_types(instance: object, stderr_file: TextIO = sys.stderr,
                      subject: str = 'Backlog item') -> None:
    """Check that every field of a dataclass holds its declared type.

    The instance must be a dataclass instance. Each field value is
    compared with its resolved type hint using
    :func:`value_matches_type`, and the first mismatch is reported with
    :func:`report_wrong_type`.

    Args:
        instance: The dataclass instance to check.
        stderr_file: The file to report errors to.
        subject: What owns the fields, used to start error messages.

    Raises:
        TypeError: If a field holds a value of the wrong type.
    """
    field_types = field_type_hints(type(instance))
    for field_name, data_type in field_types.items():
        value = getattr(instance, field_name)
        if not value_matches_type(value, data_type):
            report_wrong_type(field_name, value, data_type, stderr_file,
                              subject)


def convert_to_enum(field_name: str, value: object, enum_class: type[Enum],
                    stderr_file: TextIO = sys.stderr) -> Enum:
    """Convert a value to a member of an enum class.

    A value that is already a member of ``enum_class`` is returned
    unchanged. A string is matched against the member names using
    ``string_to_enum_best_match`` (which allows case and unique prefix
    matches). An integer is looked up as a raw enum value. Booleans are
    rejected, even though a boolean is technically an integer.

    Args:
        field_name: The name of the field being converted.
        value: The member, name or raw value to convert.
        enum_class: The enum class to convert to.
        stderr_file: The file to report errors to.

    Returns:
        The matching enum member.

    Raises:
        TypeError: If no enum member matches the value.
    """
    if isinstance(value, enum_class):
        return value
    if isinstance(value, bool):
        report_wrong_type(field_name, value, enum_class, stderr_file)
    if isinstance(value, str):
        try:
            return string_to_enum_best_match(value, enum_class)
        except KeyError:
            report_wrong_type(field_name, value, enum_class, stderr_file)
    if isinstance(value, int):
        try:
            return enum_class(value)
        except ValueError:
            report_wrong_type(field_name, value, enum_class, stderr_file)
    report_wrong_type(field_name, value, enum_class, stderr_file)


def convert_to_date(field_name: str, value: object,
                    stderr_file: TextIO = sys.stderr) -> date:
    """Convert a value to a ``datetime.date``.

    A value that is already a ``date`` is returned unchanged. A string
    is parsed as an ISO 8601 date such as ``'2026-06-12'``.

    Args:
        field_name: The name of the field being converted.
        value: The date or ISO 8601 string to convert.
        stderr_file: The file to report errors to.

    Returns:
        The converted date.

    Raises:
        TypeError: If the value is neither a date nor a valid ISO string.
    """
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            report_wrong_type(field_name, value, date, stderr_file)
    report_wrong_type(field_name, value, date, stderr_file)


def convert_field_value(field_name: str, value: object, data_type: object,
                        stderr_file: TextIO = sys.stderr) -> object:
    """Convert and validate a single field value against its type hint.

    ``None`` is accepted for optional fields. Enum fields are converted
    with :func:`convert_to_enum`, date fields with :func:`convert_to_date`,
    and all other fields are checked with :func:`value_matches_type`.

    Args:
        field_name: The name of the field being converted.
        value: The raw input value.
        data_type: The resolved type hint of the field.
        stderr_file: The file to report errors to.

    Returns:
        The converted value, ready to be stored on the backlog item.

    Raises:
        TypeError: If the value cannot be converted to the field type.
    """
    if value is None and accepts_none(data_type):
        return None
    inner_type = non_optional_type(data_type)
    enum_class = enum_class_of(inner_type)
    if enum_class is not None:
        return convert_to_enum(field_name, value, enum_class, stderr_file)
    if inner_type is date:
        return convert_to_date(field_name, value, stderr_file)
    if not value_matches_type(value, data_type):
        report_wrong_type(field_name, value, data_type, stderr_file)
    return value


def is_extra_field_map(item_field: Field[object],
                       field_types: dict[str, object]) -> bool:
    """Return True if a field is the ``dict[str, object]`` extras map.

    The extras map stores input keys that do not correspond to a named
    field. It is recognised by being a default-factory ``dict`` field
    whose value type is ``object``.

    Args:
        item_field: The dataclass field to inspect.
        field_types: The resolved type hints of the dataclass.

    Returns:
        True if the field is the extras mapping field.
    """
    data_type = field_types.get(item_field.name)
    args = get_args(data_type)
    return (item_field.default_factory is not MISSING and
            get_origin(data_type) is dict and len(args) == 2 and
            args[0] is str and args[1] is object)


def extra_field_name(item_fields: Sequence[Field[object]],
                     field_types: dict[str, object]) -> Optional[str]:
    """Return the name of the extras map field, if any.

    Args:
        item_fields: The dataclass fields to search.
        field_types: The resolved type hints of the dataclass.

    Returns:
        The name of the extras mapping field, or None.
    """
    for item_field in item_fields:
        if is_extra_field_map(item_field, field_types):
            return item_field.name
    return None


def collect_extra_values(data: dict[str, object], known_names: set[str],
                         extra_name: str, data_type: object,
                         stderr_file: TextIO = sys.stderr
                         ) -> dict[str, object]:
    """Collect the values for the extras mapping field.

    The result merges an explicit ``extra_name`` mapping found in the
    input with every input key that does not match a named field.

    Args:
        data: The raw input data for one backlog item.
        known_names: The names of the named dataclass fields.
        extra_name: The name of the extras mapping field.
        data_type: The resolved type hint of the extras field.
        stderr_file: The file to report errors to.

    Returns:
        The mapping of extra field names to their values.

    Raises:
        TypeError: If an explicit extras mapping has the wrong type.
    """
    result: dict[str, object] = {}
    if extra_name in data:
        value = convert_field_value(extra_name, data[extra_name], data_type,
                                    stderr_file)
        assert isinstance(value, dict)
        for key, item in value.items():
            assert isinstance(key, str)
            result[key] = item
    for field_name, item in data.items():
        if field_name not in known_names:
            result[field_name] = item
    return result


def build_item_kwargs(item_fields: Sequence[Field[object]],
                      field_types: dict[str, object], data: dict[str, object],
                      stderr_file: TextIO = sys.stderr) -> dict[str, object]:
    """Build the constructor keyword arguments for a backlog item.

    Each named field present in ``data`` is converted to its declared
    type. Missing mandatory fields are reported and rejected. Any input
    keys that do not match a named field are gathered into the extras
    mapping field.

    Args:
        item_fields: The dataclass fields of the backlog item.
        field_types: The resolved type hints of the dataclass.
        data: The raw input data for one backlog item.
        stderr_file: The file to report errors to.

    Returns:
        The keyword arguments to construct one backlog item.

    Raises:
        KeyError: If a mandatory field is missing.
        TypeError: If a field value has a type that cannot be converted.
    """
    known_names = {item_field.name for item_field in item_fields}
    extra_name = extra_field_name(item_fields, field_types)
    result: dict[str, object] = {}
    for item_field in item_fields:
        if not item_field.init or item_field.name == extra_name:
            continue
        data_type = field_types.get(item_field.name, item_field.type)
        if item_field.name in data:
            result[item_field.name] = convert_field_value(
                item_field.name, data[item_field.name], data_type, stderr_file)
        elif is_mandatory_field(item_field):
            report_missing_field(item_field.name, stderr_file)
    if extra_name is not None:
        extra_type = field_types.get(extra_name, dict[str, object])
        result[extra_name] = collect_extra_values(data, known_names,
                                                  extra_name, extra_type,
                                                  stderr_file)
    return result


def construct(item_cls: Callable[..., T], item_kwargs: dict[str, object]) -> T:
    """Construct an instance from validated keyword arguments.

    Args:
        item_cls: The class (or callable) to instantiate.
        item_kwargs: The keyword arguments to pass to ``item_cls``.

    Returns:
        The constructed instance.
    """
    return item_cls(**item_kwargs)


def check_key_syntax(field_name: str, value: object,
                     stderr_file: TextIO = sys.stderr,
                     subject: str = 'Backlog item') -> None:
    """Check that a value is a well formed backlog key.

    A backlog key (used by ``key`` and ``release`` and by the entries of
    the dependency lists) must be a non-empty string that contains no
    whitespace and none of the separator or bracket characters
    ``, . ; : ( ) [ ] { }``. All other characters, including letters,
    digits, ``-``, ``_`` and signs such as ``#`` or ``$``, are allowed.

    Args:
        field_name: The name of the field being checked.
        value: The value that should be a valid key.
        stderr_file: The file to report errors to.
        subject: What owns the field, used to start error messages.

    Raises:
        TypeError: If the value is not a string.
        ValueError: If the string is empty or contains a forbidden
            character.
    """
    if not isinstance(value, str):
        report_wrong_type(field_name, value, str, stderr_file, subject)
    if value == '':
        report_bad_value(field_name, value, 'must not be empty', stderr_file,
                         subject)
    if any(char.isspace() for char in value):
        report_bad_value(field_name, value, 'must not contain whitespace',
                         stderr_file, subject)
    forbidden = sorted(set(value) & FORBIDDEN_KEY_CHARS)
    if forbidden:
        report_bad_value(field_name, value,
                         'must not contain any of ' + ''.join(forbidden),
                         stderr_file, subject)


def find_cycle(graph: dict[str, list[str]]) -> Optional[list[str]]:
    """Return a cycle in a directed graph, or None if it is acyclic.

    The graph maps each node to the list of nodes it points to. A
    returned cycle starts and ends with the same node, so a self
    reference is reported as ``[node, node]``.

    Args:
        graph: A mapping from each node to its successor nodes.

    Returns:
        The nodes that form a cycle (with the start node repeated at the
        end), or None when the graph has no cycle.
    """
    visiting: set[str] = set()
    visited: set[str] = set()
    path: list[str] = []

    def visit(node: str) -> Optional[list[str]]:
        """Depth-first search for a cycle reachable from ``node``."""
        if node in visited:
            return None
        if node in visiting:
            return path[path.index(node):] + [node]
        visiting.add(node)
        path.append(node)
        for successor in graph.get(node, []):
            cycle = visit(successor)
            if cycle is not None:
                return cycle
        path.pop()
        visiting.discard(node)
        visited.add(node)
        return None
    for start in graph:
        cycle = visit(start)
        if cycle is not None:
            return cycle
    return None
