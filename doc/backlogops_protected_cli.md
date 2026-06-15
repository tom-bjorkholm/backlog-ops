# Table of Contents

* [backlogops\_cli.list](#backlogops_cli.list)
  * [\_python\_prefix](#backlogops_cli.list._python_prefix)
  * [\_is\_command](#backlogops_cli.list._is_command)
  * [command\_modules](#backlogops_cli.list.command_modules)
  * [\_description\_lines](#backlogops_cli.list._description_lines)
  * [format\_listing](#backlogops_cli.list.format_listing)
  * [main](#backlogops_cli.list.main)
* [backlogops\_cli.demo\_backlog](#backlogops_cli.demo_backlog)
  * [build\_parser](#backlogops_cli.demo_backlog.build_parser)
  * [main](#backlogops_cli.demo_backlog.main)
* [backlogops\_cli.teams\_wizard](#backlogops_cli.teams_wizard)
  * [build\_parser](#backlogops_cli.teams_wizard.build_parser)
  * [main](#backlogops_cli.teams_wizard.main)
* [backlogops\_cli.\_command\_io](#backlogops_cli._command_io)
  * [parsed\_args](#backlogops_cli._command_io.parsed_args)
  * [add\_input\_args](#backlogops_cli._command_io.add_input_args)
  * [\_input\_presets](#backlogops_cli._command_io._input_presets)
  * [read\_input](#backlogops_cli._command_io.read_input)
  * [add\_output\_args](#backlogops_cli._command_io.add_output_args)
  * [\_output\_presets](#backlogops_cli._command_io._output_presets)
  * [run\_write](#backlogops_cli._command_io.run_write)
* [backlogops\_cli.convert](#backlogops_cli.convert)
  * [build\_parser](#backlogops_cli.convert.build_parser)
  * [main](#backlogops_cli.convert.main)
* [backlogops\_cli.extract\_keys](#backlogops_cli.extract_keys)
  * [build\_parser](#backlogops_cli.extract_keys.build_parser)
  * [\_level\_value](#backlogops_cli.extract_keys._level_value)
  * [\_emit](#backlogops_cli.extract_keys._emit)
  * [main](#backlogops_cli.extract_keys.main)
* [backlogops\_cli.order\_by\_deps](#backlogops_cli.order_by_deps)
  * [build\_parser](#backlogops_cli.order_by_deps.build_parser)
  * [\_ordered](#backlogops_cli.order_by_deps._ordered)
  * [main](#backlogops_cli.order_by_deps.main)
* [backlogops\_cli.order\_by\_keys](#backlogops_cli.order_by_keys)
  * [build\_parser](#backlogops_cli.order_by_keys.build_parser)
  * [\_reordered](#backlogops_cli.order_by_keys._reordered)
  * [main](#backlogops_cli.order_by_keys.main)

<a id="backlogops_cli.list"></a>

# backlogops\_cli.list

List the commands available in backlogops_cli.

<a id="backlogops_cli.list._python_prefix"></a>

#### \_python\_prefix

```python
def _python_prefix() -> str
```

Return the 'python -m' prefix matching the running OS.

<a id="backlogops_cli.list._is_command"></a>

#### \_is\_command

```python
def _is_command(module: ModuleType) -> bool
```

Tell whether a module is a usable backlogops_cli command.

<a id="backlogops_cli.list.command_modules"></a>

#### command\_modules

```python
def command_modules() -> list[tuple[str, ModuleType]]
```

Return sorted (name, module) pairs for all command modules.

<a id="backlogops_cli.list._description_lines"></a>

#### \_description\_lines

```python
def _description_lines(description: str) -> list[str]
```

Return the description as indented lines, one per text line.

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

<a id="backlogops_cli._command_io"></a>

# backlogops\_cli.\_command\_io

Shared command helpers for resolving output configs and writing.

The helpers here are used by more than one command (for example by the
``convert`` command and the ``demo_backlog`` command). The leading
underscore in the module name keeps it out of the command listing.

<a id="backlogops_cli._command_io.parsed_args"></a>

#### parsed\_args

```python
def parsed_args(parser: argparse.ArgumentParser,
                args: Optional[list[str]]) -> argparse.Namespace
```

Enable shell completion and parse the command line arguments.

<a id="backlogops_cli._command_io.add_input_args"></a>

#### add\_input\_args

```python
def add_input_args(parser: argparse.ArgumentParser) -> None
```

Add the input-file and input-config arguments.

<a id="backlogops_cli._command_io._input_presets"></a>

#### \_input\_presets

```python
def _input_presets(
        io_config: Optional[str]) -> Optional[dict[str, InputFormatConfig]]
```

Return the named input presets from a presets file, if given.

<a id="backlogops_cli._command_io.read_input"></a>

#### read\_input

```python
def read_input(parsed: argparse.Namespace) -> BacklogReleases
```

Read and validate the backlog and releases from the input file.

The input format is resolved from the ``--input-config`` value, which
may be empty (inferred from the file name), a preset name looked up in
the presets file given by ``--io-config``, or a config file path.

**Arguments**:

- `parsed` - Parsed command line arguments holding the input options
  added by :func:`add_input_args` and, optionally, the
  ``--io-config`` option added by :func:`add_output_args`.
  

**Returns**:

  The validated backlog and releases read from the input file.

<a id="backlogops_cli._command_io.add_output_args"></a>

#### add\_output\_args

```python
def add_output_args(parser: argparse.ArgumentParser) -> None
```

Add the output-file, output-config and ordering arguments.

<a id="backlogops_cli._command_io._output_presets"></a>

#### \_output\_presets

```python
def _output_presets(
        io_config: Optional[str]) -> Optional[dict[str, OutputFormatConfig]]
```

Return the named output presets from a presets file, if given.

<a id="backlogops_cli._command_io.run_write"></a>

#### run\_write

```python
def run_write(parsed: argparse.Namespace,
              data_source: Callable[[], BacklogReleases]) -> int
```

Build the data, write it to the output file, and report the result.

**Arguments**:

- `parsed` - Parsed command line arguments holding the output options
  added by :func:`add_output_args`.
- `data_source` - Callable that returns the backlog and releases to
  write. It is called inside the error handling so that reading
  failures are reported like writing failures.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be built or written.

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

<a id="backlogops_cli.extract_keys._level_value"></a>

#### \_level\_value

```python
def _level_value(text: str) -> int | str
```

Return a level token as an int when numeric, else as a name.

<a id="backlogops_cli.extract_keys._emit"></a>

#### \_emit

```python
def _emit(keys: list[str], output: Optional[str]) -> None
```

Write the keys to the output file, or to stdout when none is given.

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

<a id="backlogops_cli.order_by_deps"></a>

# backlogops\_cli.order\_by\_deps

Reorder a backlog by its dependencies and write the result.

The command reads a backlog and its releases from an input file and
reorders the backlog so that a team can start the items in backlog order
without starting an item before the items it depends on, as documented
for :func:`backlogops.order_by_dependencies`. The reordered backlog and
the releases are written to the output file. The input and output formats
are inferred from the file name extensions, but can be overridden by a
configuration file or by a named preset.

<a id="backlogops_cli.order_by_deps.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the order_by_deps command.

<a id="backlogops_cli.order_by_deps._ordered"></a>

#### \_ordered

```python
def _ordered(parsed: argparse.Namespace) -> BacklogReleases
```

Read the backlog and return it reordered by dependencies.

<a id="backlogops_cli.order_by_deps.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Reorder the backlog by dependencies and write the output file.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be read, reordered
  or written.

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

<a id="backlogops_cli.order_by_keys._reordered"></a>

#### \_reordered

```python
def _reordered(parsed: argparse.Namespace) -> BacklogReleases
```

Read the backlog and key list and return the reordered data.

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

