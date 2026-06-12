# Table of Contents

* [backlogops.backlog\_helpers](#backlogops.backlog_helpers)
  * [FORBIDDEN\_KEY\_CHARS](#backlogops.backlog_helpers.FORBIDDEN_KEY_CHARS)
  * [field\_type\_hints](#backlogops.backlog_helpers.field_type_hints)
  * [is\_mandatory\_field](#backlogops.backlog_helpers.is_mandatory_field)
  * [enum\_class\_of](#backlogops.backlog_helpers.enum_class_of)
  * [is\_union\_type](#backlogops.backlog_helpers.is_union_type)
  * [non\_optional\_type](#backlogops.backlog_helpers.non_optional_type)
  * [accepts\_none](#backlogops.backlog_helpers.accepts_none)
  * [value\_matches\_type](#backlogops.backlog_helpers.value_matches_type)
  * [report\_missing\_field](#backlogops.backlog_helpers.report_missing_field)
  * [report\_wrong\_type](#backlogops.backlog_helpers.report_wrong_type)
  * [report\_bad\_value](#backlogops.backlog_helpers.report_bad_value)
  * [report\_unknown\_reference](#backlogops.backlog_helpers.report_unknown_reference)
  * [convert\_to\_enum](#backlogops.backlog_helpers.convert_to_enum)
  * [convert\_to\_date](#backlogops.backlog_helpers.convert_to_date)
  * [convert\_field\_value](#backlogops.backlog_helpers.convert_field_value)
  * [is\_extra\_field\_map](#backlogops.backlog_helpers.is_extra_field_map)
  * [extra\_field\_name](#backlogops.backlog_helpers.extra_field_name)
  * [collect\_extra\_values](#backlogops.backlog_helpers.collect_extra_values)
  * [build\_item\_kwargs](#backlogops.backlog_helpers.build_item_kwargs)
  * [construct](#backlogops.backlog_helpers.construct)
  * [check\_key\_syntax](#backlogops.backlog_helpers.check_key_syntax)
  * [find\_cycle](#backlogops.backlog_helpers.find_cycle)
* [backlogops.no\_text\_io](#backlogops.no_text_io)
  * [NoTextIO](#backlogops.no_text_io.NoTextIO)
    * [write](#backlogops.no_text_io.NoTextIO.write)
    * [writelines](#backlogops.no_text_io.NoTextIO.writelines)
    * [flush](#backlogops.no_text_io.NoTextIO.flush)
    * [close](#backlogops.no_text_io.NoTextIO.close)
    * [seek](#backlogops.no_text_io.NoTextIO.seek)
    * [tell](#backlogops.no_text_io.NoTextIO.tell)
    * [truncate](#backlogops.no_text_io.NoTextIO.truncate)
* [backlogops.backlog](#backlogops.backlog)
  * [DEPENDENCY\_FIELDS](#backlogops.backlog.DEPENDENCY_FIELDS)
  * [Status](#backlogops.backlog.Status)
  * [BacklogItem](#backlogops.backlog.BacklogItem)
    * [to\_dict](#backlogops.backlog.BacklogItem.to_dict)
    * [check\_consistency](#backlogops.backlog.BacklogItem.check_consistency)
  * [prepare\_item\_data](#backlogops.backlog.prepare_item_data)
  * [get\_backlog\_item](#backlogops.backlog.get_backlog_item)
  * [get\_backlog](#backlogops.backlog.get_backlog)
  * [check\_unique\_keys](#backlogops.backlog.check_unique_keys)
  * [check\_key\_references](#backlogops.backlog.check_key_references)
  * [event\_start](#backlogops.backlog.event_start)
  * [event\_finish](#backlogops.backlog.event_finish)
  * [item\_dependency\_edges](#backlogops.backlog.item_dependency_edges)
  * [build\_dependency\_graph](#backlogops.backlog.build_dependency_graph)
  * [check\_no\_cycles](#backlogops.backlog.check_no_cycles)
  * [check\_parent\_levels](#backlogops.backlog.check_parent_levels)
  * [check\_backlog\_consistency](#backlogops.backlog.check_backlog_consistency)
* [backlogops.levels](#backlogops.levels)
  * [Level](#backlogops.levels.Level)
    * [check\_consistency](#backlogops.levels.Level.check_consistency)
  * [DEFAULT\_LEVELS](#backlogops.levels.DEFAULT_LEVELS)
  * [report\_duplicate\_label](#backlogops.levels.report_duplicate_label)
  * [check\_levels\_consistency](#backlogops.levels.check_levels_consistency)
  * [level\_number\_from\_name](#backlogops.levels.level_number_from_name)

<a id="backlogops.backlog_helpers"></a>

# backlogops.backlog\_helpers

Helpers for converting and validating backlog item data.

These helpers turn plain dictionaries into validated backlog field
values and report problems in a uniform way. They are deliberately
generic: they operate on values and type hints, not on the backlog item
class, so that the backlog module can use them without a circular
import.

<a id="backlogops.backlog_helpers.FORBIDDEN_KEY_CHARS"></a>

#### FORBIDDEN\_KEY\_CHARS

Characters that must never appear in a key, release or dependency.

<a id="backlogops.backlog_helpers.field_type_hints"></a>

#### field\_type\_hints

```python
def field_type_hints(cls: type) -> dict[str, object]
```

Return the resolved type hints for the fields of a class.

Postponed annotations and forward references are resolved, so that
callers receive concrete type objects (for example ``date`` and
``Status``) instead of their string annotations.

**Arguments**:

- `cls` - The class whose annotations should be resolved.
  

**Returns**:

  A mapping from field name to its resolved type hint.

<a id="backlogops.backlog_helpers.is_mandatory_field"></a>

#### is\_mandatory\_field

```python
def is_mandatory_field(item_field: Field[object]) -> bool
```

Return True when a field must be supplied by the input data.

A field is mandatory when it takes part in ``__init__`` and has
neither a default value nor a default factory.

**Arguments**:

- `item_field` - The dataclass field to inspect.
  

**Returns**:

  True if the field has no default and must be supplied.

<a id="backlogops.backlog_helpers.enum_class_of"></a>

#### enum\_class\_of

```python
def enum_class_of(data_type: object) -> Optional[type[Enum]]
```

Return the enum class of a type hint, or None.

**Arguments**:

- `data_type` - The type hint to inspect.
  

**Returns**:

  The enum class when ``data_type`` is an Enum subclass, else None.

<a id="backlogops.backlog_helpers.is_union_type"></a>

#### is\_union\_type

```python
def is_union_type(data_type: object) -> bool
```

Return True if a type hint is a ``Union`` or an ``X | Y`` union.

**Arguments**:

- `data_type` - The type hint to inspect.
  

**Returns**:

  True if the type hint is any kind of union.

<a id="backlogops.backlog_helpers.non_optional_type"></a>

#### non\_optional\_type

```python
def non_optional_type(data_type: object) -> object
```

Return the inner type of an ``Optional`` hint.

For ``Optional[X]`` (that is ``Union[X, None]``) the wrapped type
``X`` is returned. For a union with several non-None members, or for
a type hint that is not a union, the original hint is returned.

**Arguments**:

- `data_type` - The type hint to unwrap.
  

**Returns**:

  The single non-None union member, or the original type hint.

<a id="backlogops.backlog_helpers.accepts_none"></a>

#### accepts\_none

```python
def accepts_none(data_type: object) -> bool
```

Return True if ``None`` is a valid value for a type hint.

**Arguments**:

- `data_type` - The type hint to inspect.
  

**Returns**:

  True if the type hint is an optional or ``None`` accepting union.

<a id="backlogops.backlog_helpers.value_matches_type"></a>

#### value\_matches\_type

```python
def value_matches_type(value: object, data_type: object) -> bool
```

Return True if a value matches a supported type hint.

Supported hints are ``object``, optional and union types, enums, and
the ``str``, ``int``, ``date``, ``list[...]`` and ``dict[..., ...]``
forms used by backlog items.

**Arguments**:

- `value` - The runtime value to check.
- `data_type` - The type hint to check the value against.
  

**Returns**:

  True if the value is acceptable for the given type hint.

<a id="backlogops.backlog_helpers.report_missing_field"></a>

#### report\_missing\_field

```python
def report_missing_field(field_name: str,
                         stderr_file: TextIO = sys.stderr) -> NoReturn
```

Report a missing mandatory field and raise ``KeyError``.

**Arguments**:

- `field_name` - The name of the missing field.
- `stderr_file` - The file to report the error to.
  

**Raises**:

- `KeyError` - Always, after reporting the message.

<a id="backlogops.backlog_helpers.report_wrong_type"></a>

#### report\_wrong\_type

```python
def report_wrong_type(field_name: str,
                      value: object,
                      data_type: object,
                      stderr_file: TextIO = sys.stderr) -> NoReturn
```

Report a value of the wrong type and raise ``TypeError``.

**Arguments**:

- `field_name` - The name of the offending field.
- `value` - The value that has the wrong type.
- `data_type` - The type hint the value was expected to match.
- `stderr_file` - The file to report the error to.
  

**Raises**:

- `TypeError` - Always, after reporting the message.

<a id="backlogops.backlog_helpers.report_bad_value"></a>

#### report\_bad\_value

```python
def report_bad_value(field_name: str,
                     value: object,
                     reason: str,
                     stderr_file: TextIO = sys.stderr) -> NoReturn
```

Report a value that violates a constraint and raise ``ValueError``.

**Arguments**:

- `field_name` - The name of the offending field.
- `value` - The value that violates the constraint.
- `reason` - A human readable explanation of the constraint.
- `stderr_file` - The file to report the error to.
  

**Raises**:

- `ValueError` - Always, after reporting the message.

<a id="backlogops.backlog_helpers.report_unknown_reference"></a>

#### report\_unknown\_reference

```python
def report_unknown_reference(field_name: str,
                             owner_key: str,
                             referenced_key: str,
                             stderr_file: TextIO = sys.stderr) -> NoReturn
```

Report a reference to a missing key and raise ``KeyError``.

**Arguments**:

- `field_name` - The field that holds the reference.
- `owner_key` - The key of the item that owns the reference.
- `referenced_key` - The key that does not exist in the backlog.
- `stderr_file` - The file to report the error to.
  

**Raises**:

- `KeyError` - Always, after reporting the message.

<a id="backlogops.backlog_helpers.convert_to_enum"></a>

#### convert\_to\_enum

```python
def convert_to_enum(field_name: str,
                    value: object,
                    enum_class: type[Enum],
                    stderr_file: TextIO = sys.stderr) -> Enum
```

Convert a value to a member of an enum class.

A value that is already a member of ``enum_class`` is returned
unchanged. A string is matched against the member names using
``string_to_enum_best_match`` (which allows case and unique prefix
matches). An integer is looked up as a raw enum value. Booleans are
rejected, even though a boolean is technically an integer.

**Arguments**:

- `field_name` - The name of the field being converted.
- `value` - The member, name or raw value to convert.
- `enum_class` - The enum class to convert to.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The matching enum member.
  

**Raises**:

- `TypeError` - If no enum member matches the value.

<a id="backlogops.backlog_helpers.convert_to_date"></a>

#### convert\_to\_date

```python
def convert_to_date(field_name: str,
                    value: object,
                    stderr_file: TextIO = sys.stderr) -> date
```

Convert a value to a ``datetime.date``.

A value that is already a ``date`` is returned unchanged. A string
is parsed as an ISO 8601 date such as ``'2026-06-12'``.

**Arguments**:

- `field_name` - The name of the field being converted.
- `value` - The date or ISO 8601 string to convert.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The converted date.
  

**Raises**:

- `TypeError` - If the value is neither a date nor a valid ISO string.

<a id="backlogops.backlog_helpers.convert_field_value"></a>

#### convert\_field\_value

```python
def convert_field_value(field_name: str,
                        value: object,
                        data_type: object,
                        stderr_file: TextIO = sys.stderr) -> object
```

Convert and validate a single field value against its type hint.

``None`` is accepted for optional fields. Enum fields are converted
with :func:`convert_to_enum`, date fields with :func:`convert_to_date`,
and all other fields are checked with :func:`value_matches_type`.

**Arguments**:

- `field_name` - The name of the field being converted.
- `value` - The raw input value.
- `data_type` - The resolved type hint of the field.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The converted value, ready to be stored on the backlog item.
  

**Raises**:

- `TypeError` - If the value cannot be converted to the field type.

<a id="backlogops.backlog_helpers.is_extra_field_map"></a>

#### is\_extra\_field\_map

```python
def is_extra_field_map(item_field: Field[object],
                       field_types: dict[str, object]) -> bool
```

Return True if a field is the ``dict[str, object]`` extras map.

The extras map stores input keys that do not correspond to a named
field. It is recognised by being a default-factory ``dict`` field
whose value type is ``object``.

**Arguments**:

- `item_field` - The dataclass field to inspect.
- `field_types` - The resolved type hints of the dataclass.
  

**Returns**:

  True if the field is the extras mapping field.

<a id="backlogops.backlog_helpers.extra_field_name"></a>

#### extra\_field\_name

```python
def extra_field_name(item_fields: Sequence[Field[object]],
                     field_types: dict[str, object]) -> Optional[str]
```

Return the name of the extras map field, if any.

**Arguments**:

- `item_fields` - The dataclass fields to search.
- `field_types` - The resolved type hints of the dataclass.
  

**Returns**:

  The name of the extras mapping field, or None.

<a id="backlogops.backlog_helpers.collect_extra_values"></a>

#### collect\_extra\_values

```python
def collect_extra_values(
        data: dict[str, object],
        known_names: set[str],
        extra_name: str,
        data_type: object,
        stderr_file: TextIO = sys.stderr) -> dict[str, object]
```

Collect the values for the extras mapping field.

The result merges an explicit ``extra_name`` mapping found in the
input with every input key that does not match a named field.

**Arguments**:

- `data` - The raw input data for one backlog item.
- `known_names` - The names of the named dataclass fields.
- `extra_name` - The name of the extras mapping field.
- `data_type` - The resolved type hint of the extras field.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The mapping of extra field names to their values.
  

**Raises**:

- `TypeError` - If an explicit extras mapping has the wrong type.

<a id="backlogops.backlog_helpers.build_item_kwargs"></a>

#### build\_item\_kwargs

```python
def build_item_kwargs(item_fields: Sequence[Field[object]],
                      field_types: dict[str, object],
                      data: dict[str, object],
                      stderr_file: TextIO = sys.stderr) -> dict[str, object]
```

Build the constructor keyword arguments for a backlog item.

Each named field present in ``data`` is converted to its declared
type. Missing mandatory fields are reported and rejected. Any input
keys that do not match a named field are gathered into the extras
mapping field.

**Arguments**:

- `item_fields` - The dataclass fields of the backlog item.
- `field_types` - The resolved type hints of the dataclass.
- `data` - The raw input data for one backlog item.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The keyword arguments to construct one backlog item.
  

**Raises**:

- `KeyError` - If a mandatory field is missing.
- `TypeError` - If a field value has a type that cannot be converted.

<a id="backlogops.backlog_helpers.construct"></a>

#### construct

```python
def construct(item_cls: Callable[..., T], item_kwargs: dict[str, object]) -> T
```

Construct an instance from validated keyword arguments.

**Arguments**:

- `item_cls` - The class (or callable) to instantiate.
- `item_kwargs` - The keyword arguments to pass to ``item_cls``.
  

**Returns**:

  The constructed instance.

<a id="backlogops.backlog_helpers.check_key_syntax"></a>

#### check\_key\_syntax

```python
def check_key_syntax(field_name: str,
                     value: object,
                     stderr_file: TextIO = sys.stderr) -> None
```

Check that a value is a well formed backlog key.

A backlog key (used by ``key`` and ``release`` and by the entries of
the dependency lists) must be a non-empty string that contains no
whitespace and none of the separator or bracket characters
``, . ; : ( ) [ ] { }``. All other characters, including letters,
digits, ``-``, ``_`` and signs such as ``#`` or ``$``, are allowed.

**Arguments**:

- `field_name` - The name of the field being checked.
- `value` - The value that should be a valid key.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If the value is not a string.
- `ValueError` - If the string is empty or contains a forbidden
  character.

<a id="backlogops.backlog_helpers.find_cycle"></a>

#### find\_cycle

```python
def find_cycle(graph: dict[str, list[str]]) -> Optional[list[str]]
```

Return a cycle in a directed graph, or None if it is acyclic.

The graph maps each node to the list of nodes it points to. A
returned cycle starts and ends with the same node, so a self
reference is reported as ``[node, node]``.

**Arguments**:

- `graph` - A mapping from each node to its successor nodes.
  

**Returns**:

  The nodes that form a cycle (with the start node repeated at the
  end), or None when the graph has no cycle.

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

<a id="backlogops.backlog"></a>

# backlogops.backlog

Internal representation of a backlog.

<a id="backlogops.backlog.DEPENDENCY_FIELDS"></a>

#### DEPENDENCY\_FIELDS

Names of the fields that hold dependency keys of a backlog item.

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

The backlog item has a number of defined fields that are used
by the backlog operations. In addition, it has a number of extra
fields that store useful information (like descriptions) that are
not used by the backlog operations.

Fields:
    key: The key of the backlog item. Required. Must be unique.
         Must not be empty, must not contain whitespace and must
         not contain any of the characters , . ; : ( ) [ ] { }.
    level: The level of the backlog item. Required. Must be an integer.
    title: The title of the backlog item. Required.
    story_points: The story points of the backlog item.
    status: The status of the backlog item.
    parent_key: The key of the parent backlog item. Optional.
                Must exist as a key in the backlog.
                Parent keys are used to build the hierarchy of the backlog.
                The parent key must be at a higher level than the current
                item. Parent keys introduce implicit dependencies between
                items: the current item cannot start before the parent
                item starts, and the parent item cannot finish before
                all its children have finished.
    release: The release of the backlog item. Optional.
             Follows the same character rules as the key.
             Must not be empty string.
    depends_on_f2s: The list of keys of the backlog items that must
                    have been finished before the current item can
                    start. May be empty.
    depends_on_f2f: The list of keys of the backlog items that must
                    have been finished before the current item can
                    finish. May be empty.
    depends_on_s2s: The list of keys of the backlog items that must
                    have been started before the current item can
                    start. May be empty.
    planned_ready_date: The planned ready date of the backlog item.
                        The date that is communicated to the
                        customer. Optional.
    estimated_ready_date: The estimated ready date of the backlog
                          item. Optional.
    extra_fields: Additional input fields not used by the backlog
                  operations, stored by name.

<a id="backlogops.backlog.BacklogItem.to_dict"></a>

#### to\_dict

```python
def to_dict() -> dict[str, object]
```

Return a dictionary representation of the backlog item.

<a id="backlogops.backlog.BacklogItem.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the internal consistency of the backlog item.

The documented constraints are checked on all member variables.
Field types are verified, and the key, release and dependency
keys are checked for valid syntax. References between items are
not checked here; that is done by :func:`check_backlog_consistency`.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a field value violates a constraint.

<a id="backlogops.backlog.prepare_item_data"></a>

#### prepare\_item\_data

```python
def prepare_item_data(data: dict[str, object],
                      levels: Levels,
                      stderr_file: TextIO = sys.stderr) -> dict[str, object]
```

Return item data with a string level resolved to its number.

A ``level`` given as a string is matched against the level names and
aliases in ``levels`` and replaced by the level number. Integer
levels and absent levels are returned unchanged, so that type and
missing-field checks happen as usual when the data is converted.

**Arguments**:

- `data` - The raw input data for one backlog item.
- `levels` - The levels used to resolve a string level.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The input data, with a string level replaced by its number.
  

**Raises**:

- `ValueError` - If a string level matches no level name or alias.

<a id="backlogops.backlog.get_backlog_item"></a>

#### get\_backlog\_item

```python
def get_backlog_item(data: dict[str, object],
                     levels: Optional[Levels] = None,
                     stderr_file: TextIO = sys.stderr) -> BacklogItem
```

Get a backlog item from a dictionary.

The dictionary is expected to hold the mandatory fields of the
BacklogItem dataclass and any number of extra fields. Field values
are converted to their declared types (for example ISO date strings
to ``date`` and status names to ``Status``) and checked. A ``level``
given as a string is resolved to its level number using ``levels``.
When ``levels`` is None the default levels are used. Errors are
reported to the given file object.

**Arguments**:

- `data` - The dictionary to get the backlog item from.
- `levels` - The levels used to resolve a string level, or None to
  use :data:`DEFAULT_LEVELS`.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a mandatory field is missing.
- `TypeError` - If a field has a type that cannot be converted.
- `ValueError` - If a string level matches no level name or alias.
  

**Returns**:

  The backlog item.

<a id="backlogops.backlog.get_backlog"></a>

#### get\_backlog

```python
def get_backlog(datalist: list[dict[str, object]],
                levels: Optional[Levels] = None,
                stderr_file: TextIO = sys.stderr) -> Backlog
```

Get a backlog from a list of dictionaries.

Each dictionary is converted to a backlog item as documented for
:func:`get_backlog_item`.

**Arguments**:

- `datalist` - The list of dictionaries to get the backlog from.
- `levels` - The levels used to convert level names to level numbers,
  or None to use :data:`DEFAULT_LEVELS`.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a mandatory field is missing.
- `TypeError` - If a field has a type that cannot be converted.
- `ValueError` - If a string level matches no level name or alias.
  

**Returns**:

  The backlog.

<a id="backlogops.backlog.check_unique_keys"></a>

#### check\_unique\_keys

```python
def check_unique_keys(backlog: Backlog,
                      stderr_file: TextIO = sys.stderr) -> set[str]
```

Check that all backlog item keys are unique.

**Arguments**:

- `backlog` - The backlog to check.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The set of all keys, for reuse by later checks.
  

**Raises**:

- `ValueError` - If two items share the same key.

<a id="backlogops.backlog.check_key_references"></a>

#### check\_key\_references

```python
def check_key_references(backlog: Backlog,
                         known_keys: set[str],
                         stderr_file: TextIO = sys.stderr) -> None
```

Check that parent and dependency keys reference existing items.

**Arguments**:

- `backlog` - The backlog to check.
- `known_keys` - The set of keys that exist in the backlog.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a parent_key or dependency key is unknown.

<a id="backlogops.backlog.event_start"></a>

#### event\_start

```python
def event_start(key: str) -> str
```

Return the start-event node name for a backlog item key.

<a id="backlogops.backlog.event_finish"></a>

#### event\_finish

```python
def event_finish(key: str) -> str
```

Return the finish-event node name for a backlog item key.

<a id="backlogops.backlog.item_dependency_edges"></a>

#### item\_dependency\_edges

```python
def item_dependency_edges(item: BacklogItem) -> list[tuple[str, str]]
```

Return the directed scheduling edges implied by one item.

Each item has a start event and a finish event. An edge ``a -> b``
means that event ``a`` cannot happen before event ``b`` (``a``
depends on ``b``). An item finish depends on its own start. The
dependency lists add finish-to-start, finish-to-finish and
start-to-start edges. A parent relation adds two implicit edges: the
child cannot start before the parent starts, and the parent cannot
finish before the child finishes.

**Arguments**:

- `item` - The backlog item to take the edges from.
  

**Returns**:

  The directed (source, target) event edges of the item.

<a id="backlogops.backlog.build_dependency_graph"></a>

#### build\_dependency\_graph

```python
def build_dependency_graph(backlog: Backlog) -> dict[str, list[str]]
```

Return the scheduling-event dependency graph of a backlog.

The nodes are the start and finish events of the items, named
``'<key>:start'`` and ``'<key>:finish'`` (``:`` cannot appear in a
key). The edges combine the explicit dependency lists with the
implicit parent relations, as described in
:func:`item_dependency_edges`. A cycle in this graph is an
unsatisfiable set of scheduling constraints.

**Arguments**:

- `backlog` - The backlog to build the graph from.
  

**Returns**:

  A mapping from each event node to the events it depends on.

<a id="backlogops.backlog.check_no_cycles"></a>

#### check\_no\_cycles

```python
def check_no_cycles(backlog: Backlog,
                    stderr_file: TextIO = sys.stderr) -> None
```

Check that the scheduling-event graph of a backlog has no cycles.

The graph combines the explicit dependencies with the implicit
parent relations. A self dependency is treated as a cycle of length
one. A valid parent and child nesting is not a cycle, because the
parent and child start and finish events stay distinct.

**Arguments**:

- `backlog` - The backlog to check.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `ValueError` - If a dependency cycle is found.

<a id="backlogops.backlog.check_parent_levels"></a>

#### check\_parent\_levels

```python
def check_parent_levels(backlog: Backlog,
                        items_by_key: dict[str, BacklogItem],
                        stderr_file: TextIO = sys.stderr) -> None
```

Check that each parent is at a higher level than its child.

A parent is a bigger backlog item than its children, so its level
number must be strictly higher than the item that references it. The
parent references are assumed to exist, as already checked by
:func:`check_key_references`.

**Arguments**:

- `backlog` - The backlog to check.
- `items_by_key` - A mapping from each key to its backlog item.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `ValueError` - If a parent is not at a higher level than its child.

<a id="backlogops.backlog.check_backlog_consistency"></a>

#### check\_backlog\_consistency

```python
def check_backlog_consistency(backlog: Backlog,
                              stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of a backlog.

Every item is checked for internal consistency, all keys are checked
for uniqueness, parent and dependency keys are checked to reference
existing items, each parent is checked to be at a higher level than
its child, and the scheduling-event graph is checked to be free of
cycles.

**Arguments**:

- `backlog` - The backlog to check.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a key reference is invalid.
- `TypeError` - If a field has the wrong type.
- `ValueError` - If a field value violates a constraint, if keys are
  not unique, if a parent is not at a higher level than its
  child, or if there is a dependency cycle.

<a id="backlogops.levels"></a>

# backlogops.levels

Levels of a backlog item.

<a id="backlogops.levels.Level"></a>

## Level Objects

```python
@dataclass
class Level()
```

A level of a backlog item.

Fields:
    level: The level of the backlog item. Required. Must be an integer.
           Usually a positive integer, but can be negative for special
           cases. A higher level means a bigger backlog item.
           A lower level means a smaller, more detailed backlog item.
    name: The name of the level. Required. Must be a string.
          Must not be empty, must not contain whitespace and must
          not contain any of the characters , . ; : ( ) [ ] { }.
          Must be unique within the Levels.
    aliases: The aliases of the level. Optional. Must be a list of strings.
             For instance if level 1 is called "Story", it may have the
             aliases "Task" and "Bug".
             The aliases are used if a backlog item is converted from a
             tool that have different names for the same level.
             Each alias must not be empty, must not contain whitespace and
             must not contain any of the characters , . ; : ( ) [ ] { }.
             Must be unique within the Levels and must not be the same
             as any name used in the Levels.

<a id="backlogops.levels.Level.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of the level.

The documented constraints are checked on all member variables.
The name and aliases follow the same character rules as a backlog
item key. Uniqueness across levels is checked by
:func:`check_levels_consistency`, not here.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a field value violates a constraint.

<a id="backlogops.levels.DEFAULT_LEVELS"></a>

#### DEFAULT\_LEVELS

The default levels for backlog items.

<a id="backlogops.levels.report_duplicate_label"></a>

#### report\_duplicate\_label

```python
def report_duplicate_label(label: str,
                           existing: str,
                           stderr_file: TextIO = sys.stderr) -> NoReturn
```

Report a duplicate level name or alias and raise ``KeyError``.

**Arguments**:

- `label` - The label that duplicates an earlier one.
- `existing` - The earlier label it collides with.
- `stderr_file` - The file to report the error to.
  

**Raises**:

- `KeyError` - Always, after reporting the message.

<a id="backlogops.levels.check_levels_consistency"></a>

#### check\_levels\_consistency

```python
def check_levels_consistency(levels: Levels,
                             stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of the levels.

The documented constraints are checked on all levels. Each dict key
must match the ``level`` field of its value. Names and aliases are
checked for uniqueness across all levels using case-insensitive
comparison, so that a name and an alias may not differ only in case.

**Arguments**:

- `levels` - The levels to check.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a field value violates a constraint, or a dict key
  does not match its level number.
- `KeyError` - If a name or alias is not unique (case-insensitive).

<a id="backlogops.levels.level_number_from_name"></a>

#### level\_number\_from\_name

```python
def level_number_from_name(name: str,
                           levels: Levels,
                           stderr_file: TextIO = sys.stderr) -> int
```

Return the level number whose name or alias matches ``name``.

Matching is case-insensitive but otherwise exact (no prefix or
fuzzy matching). The level name and all of its aliases are
considered. The levels are assumed to be consistent, as checked by
:func:`check_levels_consistency`.

**Arguments**:

- `name` - The level name or alias to look up.
- `levels` - The levels to search.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The level number of the matching level.
  

**Raises**:

- `ValueError` - If no level name or alias matches ``name``.

