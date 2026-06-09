# Table of Contents

* [backlogops.no\_text\_io](#backlogops.no_text_io)
  * [NoTextIO](#backlogops.no_text_io.NoTextIO)
    * [write](#backlogops.no_text_io.NoTextIO.write)
    * [writelines](#backlogops.no_text_io.NoTextIO.writelines)
    * [flush](#backlogops.no_text_io.NoTextIO.flush)
    * [close](#backlogops.no_text_io.NoTextIO.close)
    * [seek](#backlogops.no_text_io.NoTextIO.seek)
    * [tell](#backlogops.no_text_io.NoTextIO.tell)
    * [truncate](#backlogops.no_text_io.NoTextIO.truncate)
    * [\_\_enter\_\_](#backlogops.no_text_io.NoTextIO.__enter__)
    * [\_\_exit\_\_](#backlogops.no_text_io.NoTextIO.__exit__)
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

<a id="backlogops.no_text_io"></a>

# backlogops.no\_text\_io

NoTextIO can be used as a TextIO object that does nothing.

<a id="backlogops.no_text_io.NoTextIO"></a>

## NoTextIO Objects

```python
class NoTextIO(io.StringIO)
```

NoTextIO can be used as a TextIO object that does nothing.

When a function expects a TextIO object for output, you can pass in
a NoTextIO object and no output will be produced.
The differrence compared to using StringIO to suppress output is that
the NoTextIO does not store any data, so no matter how much is
written to it, you do not risk running out of memory.

<a id="backlogops.no_text_io.NoTextIO.write"></a>

#### write

```python
@override
def write(s: str) -> int
```

Write a string to the NoTextIO object.

This method does nothing and returns 0.

<a id="backlogops.no_text_io.NoTextIO.writelines"></a>

#### writelines

```python
@override
def writelines(lines: Iterable[str]) -> None
```

Write a list of strings to the NoTextIO object.

This method does nothing and returns None.

<a id="backlogops.no_text_io.NoTextIO.flush"></a>

#### flush

```python
@override
def flush() -> None
```

Flush the NoTextIO object.

This method does nothing and returns None.

<a id="backlogops.no_text_io.NoTextIO.close"></a>

#### close

```python
@override
def close() -> None
```

Close the NoTextIO object.

This method does nothing and returns None.

<a id="backlogops.no_text_io.NoTextIO.seek"></a>

#### seek

```python
@override
def seek(offset: int, whence: int = io.SEEK_SET) -> int
```

Seek to a position in the NoTextIO object.

This method does nothing and returns 0.

<a id="backlogops.no_text_io.NoTextIO.tell"></a>

#### tell

```python
@override
def tell() -> int
```

Get the current position in the NoTextIO object.

This method does nothing and returns 0.

<a id="backlogops.no_text_io.NoTextIO.truncate"></a>

#### truncate

```python
@override
def truncate(size: int | None = None) -> int
```

Truncate the NoTextIO object.

This method does nothing and returns 0.

<a id="backlogops.no_text_io.NoTextIO.__enter__"></a>

#### \_\_enter\_\_

```python
@override
def __enter__() -> 'NoTextIO'
```

Enter the NoTextIO object.

This method does nothing and returns the NoTextIO object.

<a id="backlogops.no_text_io.NoTextIO.__exit__"></a>

#### \_\_exit\_\_

```python
@override
def __exit__(exc_type: type[BaseException] | None,
             exc_value: BaseException | None,
             traceback: TracebackType | None) -> None
```

Exit the NoTextIO object.

This method does nothing.

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

