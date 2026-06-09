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
* [backlogops.backlog](#backlogops.backlog)
  * [Status](#backlogops.backlog.Status)
  * [BacklogItem](#backlogops.backlog.BacklogItem)
    * [to\_dict](#backlogops.backlog.BacklogItem.to_dict)
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

