# Table of Contents

* [backlogops.backlog](#backlogops.backlog)
  * [Status](#backlogops.backlog.Status)
  * [BacklogItem](#backlogops.backlog.BacklogItem)
    * [\_\_getitem\_\_](#backlogops.backlog.BacklogItem.__getitem__)
    * [\_\_setitem\_\_](#backlogops.backlog.BacklogItem.__setitem__)
    * [\_\_contains\_\_](#backlogops.backlog.BacklogItem.__contains__)
    * [to\_dict](#backlogops.backlog.BacklogItem.to_dict)
  * [\_field\_types](#backlogops.backlog._field_types)
  * [\_is\_mandatory](#backlogops.backlog._is_mandatory)
  * [\_enum\_type](#backlogops.backlog._enum_type)
  * [\_is\_extra\_map](#backlogops.backlog._is_extra_map)
  * [\_extra\_map\_name](#backlogops.backlog._extra_map_name)
  * [\_type\_name](#backlogops.backlog._type_name)
  * [\_missing\_field](#backlogops.backlog._missing_field)
  * [\_wrong\_type](#backlogops.backlog._wrong_type)
  * [\_is\_union\_type](#backlogops.backlog._is_union_type)
  * [\_matches\_class](#backlogops.backlog._matches_class)
  * [\_matches\_list](#backlogops.backlog._matches_list)
  * [\_matches\_dict](#backlogops.backlog._matches_dict)
  * [\_matches\_tuple](#backlogops.backlog._matches_tuple)
  * [\_matches\_origin](#backlogops.backlog._matches_origin)
  * [\_matches\_type](#backlogops.backlog._matches_type)
  * [\_convert\_enum](#backlogops.backlog._convert_enum)
  * [\_convert\_value](#backlogops.backlog._convert_value)
  * [\_extra\_values](#backlogops.backlog._extra_values)
  * [\_item\_kwargs](#backlogops.backlog._item_kwargs)
  * [\_create\_item](#backlogops.backlog._create_item)
  * [get\_backlog\_item](#backlogops.backlog.get_backlog_item)
  * [get\_backlog](#backlogops.backlog.get_backlog)

<a id="backlogops.backlog"></a>

# backlogops.backlog

Internal representation of a backlog.

<a id="backlogops.backlog.Status"></a>

## Status Objects

```python
class Status(IntEnum)
```

Status of a backlog item.

<a id="backlogops.backlog.BacklogItem"></a>

## BacklogItem Objects

```python
@dataclass
class BacklogItem()
```

Internal representation of a backlog item.

<a id="backlogops.backlog.BacklogItem.__getitem__"></a>

#### \_\_getitem\_\_

```python
def __getitem__(field_name: str) -> object
```

Return a mandatory or extra field by name.

<a id="backlogops.backlog.BacklogItem.__setitem__"></a>

#### \_\_setitem\_\_

```python
def __setitem__(field_name: str, value: object) -> None
```

Set a mandatory or extra field by name.

<a id="backlogops.backlog.BacklogItem.__contains__"></a>

#### \_\_contains\_\_

```python
def __contains__(field_name: str) -> bool
```

Check if a mandatory or extra field exists by name.

<a id="backlogops.backlog.BacklogItem.to_dict"></a>

#### to\_dict

```python
def to_dict() -> dict[str, object]
```

Return a dictionary representation of the backlog item.

<a id="backlogops.backlog._field_types"></a>

#### \_field\_types

```python
def _field_types() -> dict[str, object]
```

Return resolved type hints for backlog item fields.

<a id="backlogops.backlog._is_mandatory"></a>

#### \_is\_mandatory

```python
def _is_mandatory(item_field: Field[object]) -> bool
```

Return True if a dataclass field must be supplied by input data.

<a id="backlogops.backlog._enum_type"></a>

#### \_enum\_type

```python
def _enum_type(data_type: object) -> Optional[type[Enum]]
```

Return the enum class for an enum type hint, if any.

<a id="backlogops.backlog._is_extra_map"></a>

#### \_is\_extra\_map

```python
def _is_extra_map(item_field: Field[object],
                  field_types: dict[str, object]) -> bool
```

Return True if a field is the extra field mapping.

<a id="backlogops.backlog._extra_map_name"></a>

#### \_extra\_map\_name

```python
def _extra_map_name(field_types: dict[str, object]) -> Optional[str]
```

Return the name of the field used for unknown input keys.

<a id="backlogops.backlog._type_name"></a>

#### \_type\_name

```python
def _type_name(data_type: object) -> str
```

Return a readable name for a type hint.

<a id="backlogops.backlog._missing_field"></a>

#### \_missing\_field

```python
def _missing_field(field_name: str, stderr_file: TextIO) -> NoReturn
```

Report and raise an error for a missing mandatory field.

<a id="backlogops.backlog._wrong_type"></a>

#### \_wrong\_type

```python
def _wrong_type(field_name: str, value: object, data_type: object,
                stderr_file: TextIO) -> NoReturn
```

Report and raise an error for a field with an invalid value.

<a id="backlogops.backlog._is_union_type"></a>

#### \_is\_union\_type

```python
def _is_union_type(data_type: object) -> bool
```

Return True if a type hint is a union type.

<a id="backlogops.backlog._matches_class"></a>

#### \_matches\_class

```python
def _matches_class(value: object, data_type: type[object]) -> bool
```

Return True if a value matches a non-parameterized class.

<a id="backlogops.backlog._matches_list"></a>

#### \_matches\_list

```python
def _matches_list(value: object, type_args: tuple[object, ...]) -> bool
```

Return True if a value matches a list type hint.

<a id="backlogops.backlog._matches_dict"></a>

#### \_matches\_dict

```python
def _matches_dict(value: object, type_args: tuple[object, ...]) -> bool
```

Return True if a value matches a dict type hint.

<a id="backlogops.backlog._matches_tuple"></a>

#### \_matches\_tuple

```python
def _matches_tuple(value: object, type_args: tuple[object, ...]) -> bool
```

Return True if a value matches a tuple type hint.

<a id="backlogops.backlog._matches_origin"></a>

#### \_matches\_origin

```python
def _matches_origin(value: object, origin: object,
                    type_args: tuple[object, ...]) -> Optional[bool]
```

Return a match result for a parameterized type origin.

<a id="backlogops.backlog._matches_type"></a>

#### \_matches\_type

```python
def _matches_type(value: object, data_type: object) -> bool
```

Return True if a value matches a supported type hint.

<a id="backlogops.backlog._convert_enum"></a>

#### \_convert\_enum

```python
def _convert_enum(field_name: str, value: object, data_type: type[Enum],
                  stderr_file: TextIO) -> Enum
```

Return an enum value from an enum member, name or raw value.

<a id="backlogops.backlog._convert_value"></a>

#### \_convert\_value

```python
def _convert_value(field_name: str, value: object, data_type: object,
                   stderr_file: TextIO) -> object
```

Return a field value converted and checked against its type hint.

<a id="backlogops.backlog._extra_values"></a>

#### \_extra\_values

```python
def _extra_values(data: dict[str,
                             object], known_names: set[str], extra_name: str,
                  data_type: object, stderr_file: TextIO) -> dict[str, object]
```

Return values for the extra fields mapping.

<a id="backlogops.backlog._item_kwargs"></a>

#### \_item\_kwargs

```python
def _item_kwargs(data: dict[str, object],
                 stderr_file: TextIO) -> dict[str, object]
```

Return constructor keyword arguments for a backlog item.

<a id="backlogops.backlog._create_item"></a>

#### \_create\_item

```python
def _create_item(item_kwargs: dict[str, object]) -> BacklogItem
```

Return a backlog item from checked dynamic constructor arguments.

<a id="backlogops.backlog.get_backlog_item"></a>

#### get\_backlog\_item

```python
def get_backlog_item(data: dict[str, object],
                     stderr_file: TextIO = sys.stderr) -> BacklogItem
```

Get a backlog item from a dictionary.

The dictionary is expected to have the mandatory fields of the
BacklogItem dataclass and any extra fields. The mandatory fields
must have the correct type as specified in the BacklogItem class.
Runtime types are checked and errors are reported to the given file
object.

**Arguments**:

- `data` - The dictionary to get the backlog item from.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a mandatory field is missing.
- `TypeError` - If a mandatory field has the wrong type.
  

**Returns**:

  The backlog item.

<a id="backlogops.backlog.get_backlog"></a>

#### get\_backlog

```python
def get_backlog(datalist: list[dict[str, object]],
                stderr_file: TextIO = sys.stderr) -> Backlog
```

Get a backlog from a list of dictionaries.

The dictionaries are expected to have the mandatory fields of the
BacklogItem dataclass and any extra fields. The mandatory fields
must have the correct type as specified in the BacklogItem class.
Runtime types are checked and errors are reported to the given file
object.

**Arguments**:

- `datalist` - The list of dictionaries to get the backlog from.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a mandatory field is missing.
- `TypeError` - If a mandatory field has the wrong type.
  

**Returns**:

  The backlog.

