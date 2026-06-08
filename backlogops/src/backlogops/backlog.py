#! /usr/local/bin/python3
"""Internal representation of a backlog."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from collections.abc import Callable
from dataclasses import MISSING, Field, dataclass, field, fields
from enum import Enum, IntEnum, auto
from types import UnionType
from typing import NoReturn, Optional, TextIO, Union, cast, get_args
from typing import get_origin, get_type_hints


class Status(IntEnum):
    """Status of a backlog item."""

    TODO = auto()
    IN_PROGRESS = auto()
    DONE = auto()
    REJECTED = auto()


@dataclass
class BacklogItem:
    """Internal representation of a backlog item."""

    key: str
    title: str
    story_points: int
    status: Status
    extra_fields: dict[str, object] = field(default_factory=dict)

    def __getitem__(self, field_name: str) -> object:
        """Return a mandatory or extra field by name."""
        # pylint: disable-next=no-member
        if field_name in self.__dataclass_fields__:
            return getattr(self, field_name)
        return self.extra_fields[field_name]

    def __setitem__(self, field_name: str, value: object) -> None:
        """Set a mandatory or extra field by name."""
        # pylint: disable-next=no-member
        if field_name in self.__dataclass_fields__:
            setattr(self, field_name, value)
        self.extra_fields[field_name] = value

    def __contains__(self, field_name: str) -> bool:
        """Check if a mandatory or extra field exists by name."""
        # pylint: disable-next=no-member
        return field_name in self.__dataclass_fields__ or \
            field_name in self.extra_fields

    def to_dict(self) -> dict[str, object]:
        """Return a dictionary representation of the backlog item."""
        result = {}
        # pylint: disable-next=no-member
        for field_name in self.__dataclass_fields__:
            result[field_name] = getattr(self, field_name)
        for field_name, value in self.extra_fields.items():
            result[field_name] = value
        return result


type Backlog = list[BacklogItem]
"""Internal representation of a backlog."""


def _field_types() -> dict[str, object]:
    """Return resolved type hints for backlog item fields."""
    return get_type_hints(BacklogItem)


def _is_mandatory(item_field: Field[object]) -> bool:
    """Return True if a dataclass field must be supplied by input data."""
    return (item_field.init and item_field.default is MISSING and
            item_field.default_factory is MISSING)


def _enum_type(data_type: object) -> Optional[type[Enum]]:
    """Return the enum class for an enum type hint, if any."""
    if isinstance(data_type, type) and issubclass(data_type, Enum):
        return data_type
    return None


def _is_extra_map(item_field: Field[object],
                  field_types: dict[str, object]) -> bool:
    """Return True if a field is the extra field mapping."""
    data_type = field_types.get(item_field.name)
    type_args = get_args(data_type)
    return (item_field.default_factory is not MISSING and
            get_origin(data_type) is dict and len(type_args) == 2 and
            type_args[0] is str and type_args[1] is object)


def _extra_map_name(field_types: dict[str, object]) -> Optional[str]:
    """Return the name of the field used for unknown input keys."""
    for item_field in fields(BacklogItem):
        if _is_extra_map(item_field, field_types):
            return item_field.name
    return None


def _type_name(data_type: object) -> str:
    """Return a readable name for a type hint."""
    if data_type is object:
        return 'object'
    if isinstance(data_type, type):
        return data_type.__name__
    return str(data_type).replace('typing.', '')


def _missing_field(field_name: str, stderr_file: TextIO) -> NoReturn:
    """Report and raise an error for a missing mandatory field."""
    message = f'Missing mandatory backlog item field: {field_name}'
    print(message, file=stderr_file)
    raise KeyError(message)


def _wrong_type(field_name: str, value: object, data_type: object,
                stderr_file: TextIO) -> NoReturn:
    """Report and raise an error for a field with an invalid value."""
    message = (
        f'Backlog item field {field_name!r} expected '
        f'{_type_name(data_type)}, got {type(value).__name__}: {value!r}'
    )
    print(message, file=stderr_file)
    raise TypeError(message)


def _is_union_type(data_type: object) -> bool:
    """Return True if a type hint is a union type."""
    return get_origin(data_type) in (Union, UnionType)


def _matches_class(value: object, data_type: type[object]) -> bool:
    """Return True if a value matches a non-parameterized class."""
    if data_type is int:
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, data_type)


def _matches_list(value: object, type_args: tuple[object, ...]) -> bool:
    """Return True if a value matches a list type hint."""
    if not isinstance(value, list):
        return False
    if not type_args:
        return True
    return all(_matches_type(item, type_args[0]) for item in value)


def _matches_dict(value: object, type_args: tuple[object, ...]) -> bool:
    """Return True if a value matches a dict type hint."""
    if not isinstance(value, dict):
        return False
    if len(type_args) != 2:
        return True
    key_type = type_args[0]
    value_type = type_args[1]
    return all(_matches_type(key, key_type) and
               _matches_type(item, value_type)
               for key, item in value.items())


def _matches_tuple(value: object, type_args: tuple[object, ...]) -> bool:
    """Return True if a value matches a tuple type hint."""
    if not isinstance(value, tuple):
        return False
    if not type_args:
        return True
    if len(type_args) == 2 and type_args[1] is Ellipsis:
        return all(_matches_type(item, type_args[0]) for item in value)
    if len(value) != len(type_args):
        return False
    return all(_matches_type(item, data_type)
               for item, data_type in zip(value, type_args))


def _matches_origin(value: object, origin: object,
                    type_args: tuple[object, ...]) -> Optional[bool]:
    """Return a match result for a parameterized type origin."""
    if origin is list:
        return _matches_list(value, type_args)
    if origin is dict:
        return _matches_dict(value, type_args)
    if origin is tuple:
        return _matches_tuple(value, type_args)
    if isinstance(origin, type):
        return isinstance(value, origin)
    return None


def _matches_type(value: object, data_type: object) -> bool:
    """Return True if a value matches a supported type hint."""
    if data_type is object:
        return True
    if _is_union_type(data_type):
        return any(_matches_type(value, item) for item in get_args(data_type))
    enum_type = _enum_type(data_type)
    if enum_type is not None:
        return isinstance(value, enum_type)
    origin_match = _matches_origin(value, get_origin(data_type),
                                   get_args(data_type))
    if origin_match is not None:
        return origin_match
    if isinstance(data_type, type):
        return _matches_class(value, data_type)
    return True


def _convert_enum(field_name: str, value: object, data_type: type[Enum],
                  stderr_file: TextIO) -> Enum:
    """Return an enum value from an enum member, name or raw value."""
    if isinstance(value, data_type):
        return value
    if isinstance(value, str):
        member = data_type.__members__.get(value)
        if member is not None:
            return member
    if isinstance(value, bool):
        _wrong_type(field_name, value, data_type, stderr_file)
    try:
        return data_type(value)
    except (TypeError, ValueError):
        _wrong_type(field_name, value, data_type, stderr_file)


def _convert_value(field_name: str, value: object, data_type: object,
                   stderr_file: TextIO) -> object:
    """Return a field value converted and checked against its type hint."""
    enum_type = _enum_type(data_type)
    if enum_type is not None:
        return _convert_enum(field_name, value, enum_type, stderr_file)
    if not _matches_type(value, data_type):
        _wrong_type(field_name, value, data_type, stderr_file)
    return value


def _extra_values(data: dict[str, object], known_names: set[str],
                  extra_name: str, data_type: object,
                  stderr_file: TextIO) -> dict[str, object]:
    """Return values for the extra fields mapping."""
    result: dict[str, object] = {}
    if extra_name in data:
        value = _convert_value(extra_name, data[extra_name], data_type,
                               stderr_file)
        assert isinstance(value, dict)
        for key, item in value.items():
            assert isinstance(key, str)
            result[key] = item
    for field_name, value in data.items():
        if field_name not in known_names:
            result[field_name] = value
    return result


def _item_kwargs(data: dict[str, object],
                 stderr_file: TextIO) -> dict[str, object]:
    """Return constructor keyword arguments for a backlog item."""
    field_types = _field_types()
    item_fields = fields(BacklogItem)
    known_names = {item_field.name for item_field in item_fields}
    extra_name = _extra_map_name(field_types)
    result: dict[str, object] = {}
    for item_field in item_fields:
        if not item_field.init or item_field.name == extra_name:
            continue
        data_type = field_types.get(item_field.name, item_field.type)
        if item_field.name in data:
            result[item_field.name] = _convert_value(item_field.name,
                                                     data[item_field.name],
                                                     data_type, stderr_file)
        elif _is_mandatory(item_field):
            _missing_field(item_field.name, stderr_file)
    if extra_name is not None:
        data_type = field_types.get(extra_name, dict[str, object])
        result[extra_name] = _extra_values(data, known_names, extra_name,
                                           data_type, stderr_file)
    return result


def _create_item(item_kwargs: dict[str, object]) -> BacklogItem:
    """Return a backlog item from checked dynamic constructor arguments."""
    item_factory = cast(Callable[..., BacklogItem], BacklogItem)
    return item_factory(**item_kwargs)


def get_backlog_item(data: dict[str, object],
                     stderr_file: TextIO = sys.stderr) -> BacklogItem:
    """Get a backlog item from a dictionary.

    The dictionary is expected to have the mandatory fields of the
    BacklogItem dataclass and any extra fields. The mandatory fields
    must have the correct type as specified in the BacklogItem class.
    Runtime types are checked and errors are reported to the given file
    object.

    Args:
        data: The dictionary to get the backlog item from.
        stderr_file: The file to report errors to.

    Raises:
        KeyError: If a mandatory field is missing.
        TypeError: If a mandatory field has the wrong type.

    Returns:
        The backlog item.
    """
    return _create_item(_item_kwargs(data, stderr_file))


def get_backlog(datalist: list[dict[str, object]],
                stderr_file: TextIO = sys.stderr) -> Backlog:
    """Get a backlog from a list of dictionaries.

    The dictionaries are expected to have the mandatory fields of the
    BacklogItem dataclass and any extra fields. The mandatory fields
    must have the correct type as specified in the BacklogItem class.
    Runtime types are checked and errors are reported to the given file
    object.

    Args:
        datalist: The list of dictionaries to get the backlog from.
        stderr_file: The file to report errors to.

    Raises:
        KeyError: If a mandatory field is missing.
        TypeError: If a mandatory field has the wrong type.

    Returns:
        The backlog.
    """
    return [get_backlog_item(data, stderr_file) for data in datalist]


if __name__ == '__main__':
    a = BacklogItem(key='123', title='Test', story_points=1,
                    status=Status.TODO)
    print(f'Key: {a["key"]}')
    a.extra_fields['description'] = 'Test description'
    print(f'Description: {a["description"]}')
    try:
        print(f'Non-existent field: {a["non_existent_field"]}')
    except KeyError as e:
        print(f'KeyError: {e} for field "non_existent_field"')
        print('KeyError expected for non-existent field')
    a['description'] = 'New description'
    a['title'] = 'New title'
    print(f'Title: {a["title"]}')
    print(f'Description: {a["description"]}')
    print(f'Story points: {a["story_points"]}')
    print(f'Contains key: {"key" in a}')
    print(f'Contains description: {"description" in a}')
    print(f'Contains non-existent field: {"non_existent_field" in a}')
    print(f'To dict: {a.to_dict()}')
