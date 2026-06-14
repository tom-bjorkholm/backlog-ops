# Table of Contents

* [backlogops\_cli.list](#backlogops_cli.list)
  * [\_python\_prefix](#backlogops_cli.list._python_prefix)
  * [\_is\_command](#backlogops_cli.list._is_command)
  * [command\_modules](#backlogops_cli.list.command_modules)
  * [\_description\_lines](#backlogops_cli.list._description_lines)
  * [format\_listing](#backlogops_cli.list.format_listing)
  * [main](#backlogops_cli.list.main)
* [backlogops\_cli.teams\_wizard](#backlogops_cli.teams_wizard)
  * [build\_parser](#backlogops_cli.teams_wizard.build_parser)
  * [main](#backlogops_cli.teams_wizard.main)
* [backlogops\_cli.convert](#backlogops_cli.convert)
  * [build\_parser](#backlogops_cli.convert.build_parser)
  * [\_input\_presets](#backlogops_cli.convert._input_presets)
  * [\_output\_presets](#backlogops_cli.convert._output_presets)
  * [\_convert](#backlogops_cli.convert._convert)
  * [main](#backlogops_cli.convert.main)

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

<a id="backlogops_cli.convert._input_presets"></a>

#### \_input\_presets

```python
def _input_presets(
        io_config: Optional[str]) -> Optional[dict[str, InputFormatConfig]]
```

Return the named input presets from a presets file, if given.

<a id="backlogops_cli.convert._output_presets"></a>

#### \_output\_presets

```python
def _output_presets(
        io_config: Optional[str]) -> Optional[dict[str, OutputFormatConfig]]
```

Return the named output presets from a presets file, if given.

<a id="backlogops_cli.convert._convert"></a>

#### \_convert

```python
def _convert(parsed: argparse.Namespace) -> None
```

Read the input file and write the output file.

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

