# Table of Contents

* [backlogops.backlog](#backlogops.backlog)
  * [Status](#backlogops.backlog.Status)
  * [BacklogItem](#backlogops.backlog.BacklogItem)
    * [to\_dict](#backlogops.backlog.BacklogItem.to_dict)
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

<a id="backlogops.backlog.BacklogItem.to_dict"></a>

#### to\_dict

```python
def to_dict() -> dict[str, object]
```

Return a dictionary representation of the backlog item.

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

