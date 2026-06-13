# Table of Contents

* [backlogops\_cli.list](#backlogops_cli.list)
  * [\_python\_prefix](#backlogops_cli.list._python_prefix)
  * [\_is\_command](#backlogops_cli.list._is_command)
  * [command\_modules](#backlogops_cli.list.command_modules)
  * [\_description\_lines](#backlogops_cli.list._description_lines)
  * [format\_listing](#backlogops_cli.list.format_listing)
  * [main](#backlogops_cli.list.main)

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

