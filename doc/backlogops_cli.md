# Table of Contents

* [backlogops\_cli.list](#backlogops_cli.list)
  * [command\_modules](#backlogops_cli.list.command_modules)
  * [format\_listing](#backlogops_cli.list.format_listing)
  * [main](#backlogops_cli.list.main)
* [backlogops\_cli.demo\_backlog](#backlogops_cli.demo_backlog)
  * [build\_parser](#backlogops_cli.demo_backlog.build_parser)
  * [main](#backlogops_cli.demo_backlog.main)
* [backlogops\_cli.teams\_wizard](#backlogops_cli.teams_wizard)
  * [build\_parser](#backlogops_cli.teams_wizard.build_parser)
  * [main](#backlogops_cli.teams_wizard.main)
* [backlogops\_cli.convert](#backlogops_cli.convert)
  * [build\_parser](#backlogops_cli.convert.build_parser)
  * [main](#backlogops_cli.convert.main)
* [backlogops\_cli.extract\_keys](#backlogops_cli.extract_keys)
  * [build\_parser](#backlogops_cli.extract_keys.build_parser)
  * [main](#backlogops_cli.extract_keys.main)
* [backlogops\_cli.order\_by\_keys](#backlogops_cli.order_by_keys)
  * [build\_parser](#backlogops_cli.order_by_keys.build_parser)
  * [main](#backlogops_cli.order_by_keys.main)

<a id="backlogops_cli.list"></a>

# backlogops\_cli.list

List the commands available in backlogops_cli.

<a id="backlogops_cli.list.command_modules"></a>

#### command\_modules

```python
def command_modules() -> list[tuple[str, ModuleType]]
```

Return sorted (name, module) pairs for all command modules.

<a id="backlogops_cli.list.format_listing"></a>

#### format\_listing

```python
def format_listing(commands: list[tuple[str, ModuleType]]) -> str
```

Format the command listing for printing to the user.

<a id="backlogops_cli.list.main"></a>

#### main

```python
def main() -> None
```

Print the list of available backlogops_cli commands.

<a id="backlogops_cli.demo_backlog"></a>

# backlogops\_cli.demo\_backlog

Write a demonstration backlog and releases to a file.

The data comes from :func:`backlogops.get_demo_backlog`. The output
format is inferred from the output file name extension, but can be
overridden by a configuration file or by a named preset stored in the
teams configuration file.

<a id="backlogops_cli.demo_backlog.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the demo backlog command.

<a id="backlogops_cli.demo_backlog.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Write the demonstration backlog and releases to the output file.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be written.

<a id="backlogops_cli.teams_wizard"></a>

# backlogops\_cli.teams\_wizard

Run the available-teams wizard and store the result to a file.

<a id="backlogops_cli.teams_wizard.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the teams wizard command.

<a id="backlogops_cli.teams_wizard.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Run the interactive wizard and write the workforce configuration.

The output filename receives the ``.cfg`` extension when it is not
already present.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the entered workforce is rejected or
  cannot be written.

<a id="backlogops_cli.convert"></a>

# backlogops\_cli.convert

Read a backlog and releases from one file and write them to another.

The command reads a backlog, releases, or both from an input file and
writes them to an output file, possibly in another format and with other
column names. The input and output formats are inferred from the file
name extensions, but can be overridden by a configuration file or by a
named preset stored in the teams configuration file.

<a id="backlogops_cli.convert.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the convert command.

<a id="backlogops_cli.convert.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Convert a backlog and releases from the input to the output file.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be read, validated
  or written.

<a id="backlogops_cli.extract_keys"></a>

# backlogops\_cli.extract\_keys

Extract the keys of a backlog at the given levels.

The command reads a backlog from an input file and extracts the keys of
the items at the levels named on the command line, in backlog order, as
documented for :func:`backlogops.get_keys_in_order`. A level is given by
name, alias or number. The keys are written to the key list file given by
``-o``, or to standard output when ``-o`` is omitted.

<a id="backlogops_cli.extract_keys.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the extract-keys command.

<a id="backlogops_cli.extract_keys.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Extract the backlog keys at the given levels and emit them.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the backlog cannot be read or the
  keys cannot be written.

<a id="backlogops_cli.order_by_keys"></a>

# backlogops\_cli.order\_by\_keys

Reorder a backlog from a key list and write the result.

The command reads a backlog and its releases from an input file, reads a
key list from another file, and reorders the backlog so that the items
named by the key list come first, as documented for
:func:`backlogops.move_keys_first`. The reordered backlog and the
releases are written to the output file. The input and output formats are
inferred from the file name extensions, but can be overridden by a
configuration file or by a named preset.

<a id="backlogops_cli.order_by_keys.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the order_by_keys command.

<a id="backlogops_cli.order_by_keys.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Reorder the backlog from the key list and write the output file.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be read, reordered
  or written.

