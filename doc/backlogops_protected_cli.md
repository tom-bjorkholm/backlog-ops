# Table of Contents

* [backlogops\_cli.jira\_fields](#backlogops_cli.jira_fields)
  * [build\_parser](#backlogops_cli.jira_fields.build_parser)
  * [\_passphrase](#backlogops_cli.jira_fields._passphrase)
  * [\_print\_pairs](#backlogops_cli.jira_fields._print_pairs)
  * [\_run](#backlogops_cli.jira_fields._run)
  * [main](#backlogops_cli.jira_fields.main)
* [backlogops\_cli.adjust\_release\_content](#backlogops_cli.adjust_release_content)
  * [build\_parser](#backlogops_cli.adjust_release_content.build_parser)
  * [\_adjust](#backlogops_cli.adjust_release_content._adjust)
  * [main](#backlogops_cli.adjust_release_content.main)
* [backlogops\_cli.version](#backlogops_cli.version)
  * [main](#backlogops_cli.version.main)
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
* [backlogops\_cli.migrate\_cfg](#backlogops_cli.migrate_cfg)
  * [KIND\_CLASSES](#backlogops_cli.migrate_cfg.KIND_CLASSES)
  * [MIGRATE\_ERRORS](#backlogops_cli.migrate_cfg.MIGRATE_ERRORS)
  * [build\_parser](#backlogops_cli.migrate_cfg.build_parser)
  * [\_exit\_code](#backlogops_cli.migrate_cfg._exit_code)
  * [main](#backlogops_cli.migrate_cfg.main)
* [backlogops\_cli.config\_wizard](#backlogops_cli.config_wizard)
  * [build\_parser](#backlogops_cli.config_wizard.build_parser)
  * [main](#backlogops_cli.config_wizard.main)
* [backlogops\_cli.\_command\_io](#backlogops_cli._command_io)
  * [overwrite\_callback](#backlogops_cli._command_io.overwrite_callback)
  * [parsed\_args](#backlogops_cli._command_io.parsed_args)
  * [add\_input\_args](#backlogops_cli._command_io.add_input_args)
  * [add\_config\_arg](#backlogops_cli._command_io.add_config_arg)
  * [\_resolve\_config](#backlogops_cli._command_io._resolve_config)
  * [required\_config](#backlogops_cli._command_io.required_config)
  * [optional\_config](#backlogops_cli._command_io.optional_config)
  * [io\_levels](#backlogops_cli._command_io.io_levels)
  * [read\_input](#backlogops_cli._command_io.read_input)
  * [add\_force\_arg](#backlogops_cli._command_io.add_force_arg)
  * [add\_output\_args](#backlogops_cli._command_io.add_output_args)
  * [build\_io\_parser](#backlogops_cli._command_io.build_io_parser)
  * [\_write\_output](#backlogops_cli._command_io._write_output)
  * [run\_write](#backlogops_cli._command_io.run_write)
  * [DEFAULT\_BUFFER\_DAYS](#backlogops_cli._command_io.DEFAULT_BUFFER_DAYS)
  * [add\_buffer\_arg](#backlogops_cli._command_io.add_buffer_arg)
  * [add\_changes\_arg](#backlogops_cli._command_io.add_changes_arg)
  * [build\_change\_parser](#backlogops_cli._command_io.build_change_parser)
  * [date\_report](#backlogops_cli._command_io.date_report)
  * [content\_report](#backlogops_cli._command_io.content_report)
  * [run\_change\_command](#backlogops_cli._command_io.run_change_command)
  * [\_save\_changes](#backlogops_cli._command_io._save_changes)
* [backlogops\_cli.add\_to\_jira](#backlogops_cli.add_to_jira)
  * [build\_parser](#backlogops_cli.add_to_jira.build_parser)
  * [\_passphrase](#backlogops_cli.add_to_jira._passphrase)
  * [\_add](#backlogops_cli.add_to_jira._add)
  * [\_write\_backlog\_file](#backlogops_cli.add_to_jira._write_backlog_file)
  * [\_write\_result\_files](#backlogops_cli.add_to_jira._write_result_files)
  * [\_run](#backlogops_cli.add_to_jira._run)
  * [main](#backlogops_cli.add_to_jira.main)
* [backlogops\_cli.convert](#backlogops_cli.convert)
  * [build\_parser](#backlogops_cli.convert.build_parser)
  * [main](#backlogops_cli.convert.main)
* [backlogops\_cli.add\_releases\_to\_jira](#backlogops_cli.add_releases_to_jira)
  * [build\_parser](#backlogops_cli.add_releases_to_jira.build_parser)
  * [\_passphrase](#backlogops_cli.add_releases_to_jira._passphrase)
  * [\_add](#backlogops_cli.add_releases_to_jira._add)
  * [\_write\_file](#backlogops_cli.add_releases_to_jira._write_file)
  * [\_write\_result\_files](#backlogops_cli.add_releases_to_jira._write_result_files)
  * [\_run](#backlogops_cli.add_releases_to_jira._run)
  * [main](#backlogops_cli.add_releases_to_jira.main)
* [backlogops\_cli.extract\_keys](#backlogops_cli.extract_keys)
  * [build\_parser](#backlogops_cli.extract_keys.build_parser)
  * [\_level\_value](#backlogops_cli.extract_keys._level_value)
  * [\_emit](#backlogops_cli.extract_keys._emit)
  * [main](#backlogops_cli.extract_keys.main)
* [backlogops\_cli.\_wizard\_io](#backlogops_cli._wizard_io)
  * [build\_wizard\_parser](#backlogops_cli._wizard_io.build_wizard_parser)
  * [\_check\_overwrite](#backlogops_cli._wizard_io._check_overwrite)
  * [\_make\_bridge](#backlogops_cli._wizard_io._make_bridge)
  * [run\_wizard\_to\_file](#backlogops_cli._wizard_io.run_wizard_to_file)
* [backlogops\_cli.\_migrate\_warn](#backlogops_cli._migrate_warn)
  * [CliMigrateWarnHook](#backlogops_cli._migrate_warn.CliMigrateWarnHook)
    * [migrate\_instructions](#backlogops_cli._migrate_warn.CliMigrateWarnHook.migrate_instructions)
  * [CliPresetMigrateWarnHook](#backlogops_cli._migrate_warn.CliPresetMigrateWarnHook)
    * [migrate\_instructions](#backlogops_cli._migrate_warn.CliPresetMigrateWarnHook.migrate_instructions)
* [backlogops\_cli.bloc\_version\_reporter](#backlogops_cli.bloc_version_reporter)
  * [BloCliVersionReporter](#backlogops_cli.bloc_version_reporter.BloCliVersionReporter)
    * [package\_names](#backlogops_cli.bloc_version_reporter.BloCliVersionReporter.package_names)
    * [get\_main\_package\_name](#backlogops_cli.bloc_version_reporter.BloCliVersionReporter.get_main_package_name)
* [backlogops\_cli.plan\_release\_dates](#backlogops_cli.plan_release_dates)
  * [build\_parser](#backlogops_cli.plan_release_dates.build_parser)
  * [\_plan](#backlogops_cli.plan_release_dates._plan)
  * [main](#backlogops_cli.plan_release_dates.main)
* [backlogops\_cli.order\_releases](#backlogops_cli.order_releases)
  * [build\_parser](#backlogops_cli.order_releases.build_parser)
  * [\_ordered](#backlogops_cli.order_releases._ordered)
  * [main](#backlogops_cli.order_releases.main)
* [backlogops\_cli.order\_by\_deps](#backlogops_cli.order_by_deps)
  * [build\_parser](#backlogops_cli.order_by_deps.build_parser)
  * [\_ordered](#backlogops_cli.order_by_deps._ordered)
  * [main](#backlogops_cli.order_by_deps.main)
* [backlogops\_cli.order\_by\_release](#backlogops_cli.order_by_release)
  * [build\_parser](#backlogops_cli.order_by_release.build_parser)
  * [\_ordered](#backlogops_cli.order_by_release._ordered)
  * [main](#backlogops_cli.order_by_release.main)
* [backlogops\_cli.preset\_wizard](#backlogops_cli.preset_wizard)
  * [build\_parser](#backlogops_cli.preset_wizard.build_parser)
  * [main](#backlogops_cli.preset_wizard.main)
* [backlogops\_cli.order\_by\_keys](#backlogops_cli.order_by_keys)
  * [build\_parser](#backlogops_cli.order_by_keys.build_parser)
  * [\_reordered](#backlogops_cli.order_by_keys._reordered)
  * [main](#backlogops_cli.order_by_keys.main)
* [backlogops\_cli.read\_jira](#backlogops_cli.read_jira)
  * [build\_parser](#backlogops_cli.read_jira.build_parser)
  * [\_passphrase](#backlogops_cli.read_jira._passphrase)
  * [\_warn\_if\_inconsistent](#backlogops_cli.read_jira._warn_if_inconsistent)
  * [\_read\_jira](#backlogops_cli.read_jira._read_jira)
  * [main](#backlogops_cli.read_jira.main)
* [backlogops\_cli.estimate\_ready\_date](#backlogops_cli.estimate_ready_date)
  * [build\_parser](#backlogops_cli.estimate_ready_date.build_parser)
  * [\_start\_date](#backlogops_cli.estimate_ready_date._start_date)
  * [\_estimate](#backlogops_cli.estimate_ready_date._estimate)
  * [main](#backlogops_cli.estimate_ready_date.main)

<a id="backlogops_cli.jira_fields"></a>

# backlogops\_cli.jira\_fields

Print Jira field information for a preset, to diagnose write mappings.

The command prints the custom field id to display name map that the reader
fetches from Jira, so a column-map name such as 'Story point estimate' can
be matched to its field id. With ``--issue`` it also prints the fields the
given issue's edit screen offers, which explains why a mapped field cannot
be set on that issue's type: a field missing from the edit screen cannot be
set through the issue edit REST endpoint.

An encrypted Jira token is unlocked by a pass phrase asked on the terminal
only when it is needed.

<a id="backlogops_cli.jira_fields.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the field diagnostic command.

<a id="backlogops_cli.jira_fields._passphrase"></a>

#### \_passphrase

```python
def _passphrase() -> str
```

Ask for the Jira token pass phrase on the terminal.

<a id="backlogops_cli.jira_fields._print_pairs"></a>

#### \_print\_pairs

```python
def _print_pairs(heading: str, pairs: list[tuple[str, str]]) -> None
```

Print a heading and each field id and display name pair.

<a id="backlogops_cli.jira_fields._run"></a>

#### \_run

```python
def _run(parsed: argparse.Namespace) -> int
```

Print the custom field map and, optionally, editable fields.

<a id="backlogops_cli.jira_fields.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Print Jira field information for a preset.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the fields cannot be read.

<a id="backlogops_cli.adjust_release_content"></a>

# backlogops\_cli.adjust\_release\_content

Adjust release content to fit the planned release dates.

The command reads an already estimated backlog and its releases, then
moves each backlog item to the earliest release whose planned date is on
or after the item's estimated ready date plus a slack buffer, as
documented for :func:`backlogops.adjust_release_content`. The adjusted
backlog and the releases are written to the output file, and the list of
content changes is printed to stdout, or also saved to a file when
``--changes-file`` is given.

<a id="backlogops_cli.adjust_release_content.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the adjust-content command.

<a id="backlogops_cli.adjust_release_content._adjust"></a>

#### \_adjust

```python
def _adjust(
        parsed: argparse.Namespace,
        data: BacklogReleases) -> tuple[str, Optional[Callable[[str], None]]]
```

Adjust the release content and return the change report.

<a id="backlogops_cli.adjust_release_content.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Adjust the release content and write the output file.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be read, adjusted or
  written.

<a id="backlogops_cli.version"></a>

# backlogops\_cli.version

Print version information for the backlogops_cli package.

<a id="backlogops_cli.version.main"></a>

#### main

```python
def main() -> None
```

Print version information for the backlogops_cli package.

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
backlog-ops configuration file.

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

<a id="backlogops_cli.migrate_cfg"></a>

# backlogops\_cli.migrate\_cfg

Migrate a configuration file to the current file format.

The command reads an existing configuration file through the normal
backward-compatibility (Reading an Old Configuration File) rules and
writes the same configuration back in the current format to a new file.
The ``--kind`` option selects what the input file is: the backlog-ops
configuration file, a stand-alone input format preset file, or a
stand-alone output format preset file. The library refuses to overwrite an
existing output file, so the destination must not exist.

<a id="backlogops_cli.migrate_cfg.KIND_CLASSES"></a>

#### KIND\_CLASSES

Map a ``--kind`` value to the configuration class used to migrate it.

<a id="backlogops_cli.migrate_cfg.MIGRATE_ERRORS"></a>

#### MIGRATE\_ERRORS

Errors raised when an input file cannot be read or written.

<a id="backlogops_cli.migrate_cfg.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the migrate_cfg command.

<a id="backlogops_cli.migrate_cfg._exit_code"></a>

#### \_exit\_code

```python
def _exit_code(error: SystemExit) -> int
```

Return the integer exit code carried by a SystemExit.

<a id="backlogops_cli.migrate_cfg.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Migrate a configuration file to the current format.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the input cannot be read, the output
  already exists, or the data cannot be written.

<a id="backlogops_cli.config_wizard"></a>

# backlogops\_cli.config\_wizard

Run the backlog-ops configuration wizard and store the result.

<a id="backlogops_cli.config_wizard.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the config wizard command.

<a id="backlogops_cli.config_wizard.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Run the interactive wizard and write the backlog-ops configuration.

The output filename receives the ``.cfg`` extension when it is not
already present.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the entered configuration is rejected
  or cannot be written.

<a id="backlogops_cli._command_io"></a>

# backlogops\_cli.\_command\_io

Shared command helpers for resolving output configs and writing.

The helpers here are used by more than one command (for example by the
``convert`` command and the ``demo_backlog`` command). The leading
underscore in the module name keeps it out of the command listing.

<a id="backlogops_cli._command_io.overwrite_callback"></a>

#### overwrite\_callback

```python
def overwrite_callback(force: bool,
                       in_stream: Optional[TextIO] = None,
                       out_stream: Optional[TextIO] = None) -> FileExistsCb
```

Return a file-exists callback for writing CLI output files.

A writer calls the returned callback only when the target file
already exists. With ``force`` the overwrite is allowed silently.
Otherwise the user is asked on ``out_stream``/``in_stream`` and the
overwrite is allowed only on an explicit yes; any other answer, an
empty answer, or end of input refuses it with ``FileExistsError``.

**Arguments**:

- `force` - Allow the overwrite without asking when True.
- `in_stream` - Stream the answer is read from, or None for stdin.
- `out_stream` - Stream the prompt is written to, or None for stdout.
  

**Returns**:

  A callback suitable as ``file_exists_callback`` for the writers.

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

<a id="backlogops_cli._command_io.add_config_arg"></a>

#### add\_config\_arg

```python
def add_config_arg(parser: argparse.ArgumentParser) -> None
```

Add the ``-c``/``--config`` backlog-ops configuration argument.

The configuration file holds the workforce, the named input and output
presets, the levels and the global status map. Without ``-c`` the file
is discovered the same way as the GUI.

<a id="backlogops_cli._command_io._resolve_config"></a>

#### \_resolve\_config

```python
def _resolve_config(parsed: argparse.Namespace) -> BacklogOpsConfig
```

Return the backlog-ops configuration from ``-c`` or by discovery.

With ``-c`` the named file is read; an old file triggers a migration
warning. Without ``-c`` the file is discovered the same way as the GUI
(``$BACKLOGOPS_CFG``, then ``backlogops.cfg`` in ``$BACKLOGOPS_DIR``,
then ``$HOME/.backlogops.cfg``).

**Raises**:

- `ValueError` - If ``-c`` names a file that does not exist.
- `RuntimeError` - If no ``-c`` is given and no file is discovered.

<a id="backlogops_cli._command_io.required_config"></a>

#### required\_config

```python
def required_config(parsed: argparse.Namespace) -> BacklogOpsConfig
```

Return the configuration, reporting a missing one as a ValueError.

Used by commands that cannot work without a configuration, such as the
estimate command, which needs the workforce.

<a id="backlogops_cli._command_io.optional_config"></a>

#### optional\_config

```python
def optional_config(parsed: argparse.Namespace) -> Optional[BacklogOpsConfig]
```

Return the configuration, or None with a note when none is found.

Used by commands that fall back to the built-in defaults (formats
inferred from the file name, no presets) when no configuration file is
available.

<a id="backlogops_cli._command_io.io_levels"></a>

#### io\_levels

```python
def io_levels(config: Optional[BacklogOpsConfig]) -> Optional[Levels]
```

Return the configured levels from ``config``, or None.

**Arguments**:

- `config` - The resolved backlog-ops configuration, or None to use the
  default levels.
  

**Returns**:

  The levels configured in ``config``, or None when no configuration
  is given.

<a id="backlogops_cli._command_io.read_input"></a>

#### read\_input

```python
def read_input(parsed: argparse.Namespace,
               config: Optional[BacklogOpsConfig]) -> BacklogReleases
```

Read and validate the backlog and releases from the input file.

The input format is resolved from the ``--input-config`` value, which
may be empty (inferred from the file name), a preset name looked up in
``config``, or a config file path. When ``config`` is given its levels
and its library-wide status input map are honoured while reading the
items; the input configuration's own status map overrides the global
one per name.

**Arguments**:

- `parsed` - Parsed command line arguments holding the input options
  added by :func:`add_input_args`.
- `config` - The resolved backlog-ops configuration, or None to use the
  built-in defaults.
  

**Returns**:

  The validated backlog and releases read from the input file.

<a id="backlogops_cli._command_io.add_force_arg"></a>

#### add\_force\_arg

```python
def add_force_arg(parser: argparse.ArgumentParser) -> None
```

Add the force flag that overwrites output files without asking.

<a id="backlogops_cli._command_io.add_output_args"></a>

#### add\_output\_args

```python
def add_output_args(parser: argparse.ArgumentParser) -> None
```

Add the output-file, output-config and ordering arguments.

<a id="backlogops_cli._command_io.build_io_parser"></a>

#### build\_io\_parser

```python
def build_io_parser(description: str,
                    *,
                    with_input: bool = True,
                    with_config: bool = True,
                    with_output: bool = True) -> argparse.ArgumentParser
```

Create a parser with the common input, config and output options.

Most data commands read a file, take the backlog-ops configuration,
and write a file, so this builds the parser with those option groups
already added. A command adds only its own extra options to the
returned parser. A group is left out when its flag is False, for a
command that does not read (or does not write) a backlog file.

**Arguments**:

- `description` - The command description shown in the help text.
- `with_input` - Add the input-file and input-config options.
- `with_config` - Add the ``-c`` backlog-ops configuration option.
- `with_output` - Add the output-file, output-config, ordering and
  force options.
  

**Returns**:

  The parser with the requested common options added.

<a id="backlogops_cli._command_io._write_output"></a>

#### \_write\_output

```python
def _write_output(parsed: argparse.Namespace,
                  config: Optional[BacklogOpsConfig],
                  data: BacklogReleases) -> None
```

Write the backlog and releases to the configured output file.

<a id="backlogops_cli._command_io.run_write"></a>

#### run\_write

```python
def run_write(parsed: argparse.Namespace,
              data_source: Callable[[Optional[BacklogOpsConfig]],
                                    BacklogReleases],
              require_config: bool = False) -> int
```

Build the data, write it to the output file, and report the result.

The configuration is resolved once from ``-c`` or by discovery. It
falls back to the built-in defaults when none is found, unless
``require_config`` is True, in which case a missing configuration is
reported as an error.

**Arguments**:

- `parsed` - Parsed command line arguments holding the output options
  added by :func:`add_output_args` and the ``-c`` option added by
  :func:`add_config_arg`.
- `data_source` - Callable that receives the resolved configuration (or
  None) and returns the backlog and releases to write. It is
  called inside the error handling so that reading failures are
  reported like writing failures.
- `require_config` - When True a missing configuration is reported as an
  error instead of falling back to the built-in defaults.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be built or written.

<a id="backlogops_cli._command_io.DEFAULT_BUFFER_DAYS"></a>

#### DEFAULT\_BUFFER\_DAYS

Default slack in calendar days added when fitting dates.

<a id="backlogops_cli._command_io.add_buffer_arg"></a>

#### add\_buffer\_arg

```python
def add_buffer_arg(parser: argparse.ArgumentParser) -> None
```

Add the buffer-days argument with the default slack.

<a id="backlogops_cli._command_io.add_changes_arg"></a>

#### add\_changes\_arg

```python
def add_changes_arg(parser: argparse.ArgumentParser) -> None
```

Add the optional file to also save the list of changes to.

<a id="backlogops_cli._command_io.build_change_parser"></a>

#### build\_change\_parser

```python
def build_change_parser(description: str) -> argparse.ArgumentParser
```

Build a parser with input, config, output, buffer and changes.

<a id="backlogops_cli._command_io.date_report"></a>

#### date\_report

```python
def date_report(
    changes: ReleaseDateChanges, file_exists_cb: FileExistsCb
) -> tuple[str, Optional[Callable[[str], None]]]
```

Return the date change listing and a writer, None when empty.

The writer overwrites an existing changes file as decided by
``file_exists_cb``.

<a id="backlogops_cli._command_io.content_report"></a>

#### content\_report

```python
def content_report(
    changes: ReleaseChanges, file_exists_cb: FileExistsCb
) -> tuple[str, Optional[Callable[[str], None]]]
```

Return the content change listing and a writer, None when empty.

The writer overwrites an existing changes file as decided by
``file_exists_cb``.

<a id="backlogops_cli._command_io.run_change_command"></a>

#### run\_change\_command

```python
def run_change_command(parsed: argparse.Namespace,
                       produce: Callable[
                           [Optional[BacklogOpsConfig], BacklogReleases],
                           tuple[str, Optional[Callable[[str], None]]]],
                       require_config: bool = False) -> int
```

Read, change, write the data, and emit the list of changes.

The configuration is resolved once, the input is read and validated,
``produce`` changes it in place and returns the change listing as text
together with a callback that writes the same changes to a file. The
changed data is written to the output file, the listing is printed to
stdout, and, when ``--changes-file`` is given, the changes are also
written to that file.

**Arguments**:

- `parsed` - Parsed command line arguments holding the input, output,
  ``-c`` and ``--changes-file`` options.
- `produce` - Callable that receives the resolved configuration (or
  None) and the data, changes the data, and returns the change
  listing text and a writer for the change file.
- `require_config` - When True a missing configuration is reported as an
  error instead of falling back to the built-in defaults.
  

**Returns**:

  ``0`` on success, ``1`` when any step fails.

<a id="backlogops_cli._command_io._save_changes"></a>

#### \_save\_changes

```python
def _save_changes(parsed: argparse.Namespace,
                  write_changes: Optional[Callable[[str], None]]) -> None
```

Save the changes to ``--changes-file`` when one is requested.

A ``write_changes`` of None means there were no changes, so nothing is
written and a short note is printed instead.

<a id="backlogops_cli.add_to_jira"></a>

# backlogops\_cli.add\_to\_jira

Add a backlog to Jira from an input file, creating one issue per item.

The command reads a backlog (or a backlog and its releases) from the input
file, then adds the backlog items to Jira using a named preset of the
backlog-ops configuration. By default it stops with an error when an
item's key already exists in Jira; ``--skip-existing`` skips those items
instead.

The added items (carrying their new Jira keys) and the items already in
Jira are printed to stdout as two labelled lists, unless ``-q``/``--quiet``
is given. Each list is also written to a file when ``--added-file`` or
``--existing-file`` names one; without a file name the list is not written.
An encrypted Jira token is unlocked by a pass phrase asked on the terminal
only when it is needed.

<a id="backlogops_cli.add_to_jira.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the add-to-Jira command.

<a id="backlogops_cli.add_to_jira._passphrase"></a>

#### \_passphrase

```python
def _passphrase() -> str
```

Ask for the Jira token pass phrase on the terminal.

<a id="backlogops_cli.add_to_jira._add"></a>

#### \_add

```python
def _add(parsed: argparse.Namespace, config: BacklogOpsConfig,
         data: BacklogReleases) -> AddedToJira
```

Add the input backlog to Jira using the named write preset.

<a id="backlogops_cli.add_to_jira._write_backlog_file"></a>

#### \_write\_backlog\_file

```python
def _write_backlog_file(config: BacklogOpsConfig, path: str,
                        data: BacklogReleases, force: bool) -> None
```

Write one returned backlog and the input releases to a file.

<a id="backlogops_cli.add_to_jira._write_result_files"></a>

#### \_write\_result\_files

```python
def _write_result_files(parsed: argparse.Namespace, config: BacklogOpsConfig,
                        data: BacklogReleases, result: AddedToJira) -> None
```

Write the added and already-present backlogs to any named files.

<a id="backlogops_cli.add_to_jira._run"></a>

#### \_run

```python
def _run(parsed: argparse.Namespace) -> int
```

Read the input, add it to Jira, write files and print the lists.

<a id="backlogops_cli.add_to_jira.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Add a backlog to Jira and report the added and present items.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the backlog cannot be added or a key
  already exists in Jira without ``--skip-existing``.

<a id="backlogops_cli.convert"></a>

# backlogops\_cli.convert

Read a backlog and releases from one file and write them to another.

The command reads a backlog, releases, or both from an input file and
writes them to an output file, possibly in another format and with other
column names. The input and output formats are inferred from the file
name extensions, but can be overridden by a configuration file or by a
named preset stored in the backlog-ops configuration file.

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

<a id="backlogops_cli.add_releases_to_jira"></a>

# backlogops\_cli.add\_releases\_to\_jira

Add releases to Jira from an input file, creating one version per name.

The command reads a backlog and its releases from the input file, then
adds the releases to Jira using a named preset of the backlog-ops
configuration. By default it stops with an error when a release name
already exists in Jira; ``--skip-existing`` skips those releases instead.

The added releases and the releases already in Jira are printed to stdout
as two labelled lists, unless ``-q``/``--quiet`` is given. Each list is
also written, together with the unchanged input backlog, to a file when
``--added-file`` or ``--existing-file`` names one; without a file name the
list is not written. An encrypted Jira token is unlocked by a pass phrase
asked on the terminal only when it is needed.

<a id="backlogops_cli.add_releases_to_jira.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the add-releases command.

<a id="backlogops_cli.add_releases_to_jira._passphrase"></a>

#### \_passphrase

```python
def _passphrase() -> str
```

Ask for the Jira token pass phrase on the terminal.

<a id="backlogops_cli.add_releases_to_jira._add"></a>

#### \_add

```python
def _add(parsed: argparse.Namespace, config: BacklogOpsConfig,
         data: BacklogReleases) -> AddedReleasesToJira
```

Add the input releases to Jira using the named preset.

<a id="backlogops_cli.add_releases_to_jira._write_file"></a>

#### \_write\_file

```python
def _write_file(config: BacklogOpsConfig, path: str, data: BacklogReleases,
                force: bool) -> None
```

Write one backlog-and-releases result to a file.

<a id="backlogops_cli.add_releases_to_jira._write_result_files"></a>

#### \_write\_result\_files

```python
def _write_result_files(parsed: argparse.Namespace, config: BacklogOpsConfig,
                        data: BacklogReleases,
                        result: AddedReleasesToJira) -> None
```

Write the added and already-present releases to any named files.

<a id="backlogops_cli.add_releases_to_jira._run"></a>

#### \_run

```python
def _run(parsed: argparse.Namespace) -> int
```

Read the input, add the releases, write files and print the lists.

<a id="backlogops_cli.add_releases_to_jira.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Add releases to Jira and report the added and present releases.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the releases cannot be added or a name
  already exists in Jira without ``--skip-existing``.

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
def _emit(keys: list[str], output: Optional[str], force: bool) -> None
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

<a id="backlogops_cli._wizard_io"></a>

# backlogops\_cli.\_wizard\_io

Shared helpers for the configuration and preset wizard commands.

Both wizard commands write a JSON configuration file built interactively
through a ``WizardUiBridge``. They share the same command line shape (an
output file, a switch forcing the plain console interface, and a force
flag), the same overwrite check, and the same run-write-report flow. That
shared logic lives here; the leading underscore in the module name keeps
it out of the command listing.

<a id="backlogops_cli._wizard_io.build_wizard_parser"></a>

#### build\_wizard\_parser

```python
def build_wizard_parser(description: str) -> argparse.ArgumentParser
```

Build a wizard parser with output, no-textual and force options.

<a id="backlogops_cli._wizard_io._check_overwrite"></a>

#### \_check\_overwrite

```python
def _check_overwrite(output: str, force: bool) -> None
```

Ask before overwriting an existing configuration file.

The check runs before the wizard, so the user is not asked to confirm
an overwrite only after entering the whole configuration.

<a id="backlogops_cli._wizard_io._make_bridge"></a>

#### \_make\_bridge

```python
def _make_bridge(no_textual: bool) -> WizardUiBridge
```

Return the console bridge when forced, else the best text bridge.

Without ``--no-textual`` the factory returns a Textual full-screen
bridge in a real terminal and a console bridge otherwise, such as when
input is redirected or under tests.

<a id="backlogops_cli._wizard_io.run_wizard_to_file"></a>

#### run\_wizard\_to\_file

```python
def run_wizard_to_file(parsed: argparse.Namespace,
                       wizard: Callable[[WizardUiBridge],
                                        Config], label: str) -> int
```

Run a wizard, write its configuration to the output file, report.

The output filename receives the ``.cfg`` extension when it is not
already present.

**Arguments**:

- `parsed` - Parsed arguments holding ``output``, ``force`` and
  ``no_textual``.
- `wizard` - Wizard called with the chosen UI bridge; it returns a
  configuration object that knows how to write itself.
- `label` - Human-readable name of what was written, for the message.
  

**Returns**:

  ``0`` on success, ``1`` when the wizard is abandoned or the
  configuration is rejected or cannot be written.

<a id="backlogops_cli._migrate_warn"></a>

# backlogops\_cli.\_migrate\_warn

Backward-compatibility warning hooks for the command line interface.

When a command reads a file that needed backward-compatible normalization
(Reading an Old Configuration File), one of these hooks prints the
standard migration warning followed by command-specific instructions.
``CliMigrateWarnHook`` is used when the old file is the backlog-ops
configuration file and shows the ``migrate_cfg`` command for the default
config kind. ``CliPresetMigrateWarnHook`` is used when the old file is a
stand-alone input or output preset file and shows the ``migrate_cfg``
command with the ``--kind`` option, because that option selects how a
preset file is migrated. The leading underscore in the module name keeps
it out of the command listing.

<a id="backlogops_cli._migrate_warn.CliMigrateWarnHook"></a>

## CliMigrateWarnHook Objects

```python
class CliMigrateWarnHook(MigrateCfgWarnHook)
```

Tell the user to migrate an old config file with ``migrate_cfg``.

<a id="backlogops_cli._migrate_warn.CliMigrateWarnHook.migrate_instructions"></a>

#### migrate\_instructions

```python
@classmethod
def migrate_instructions(cls) -> str
```

Return the command line migration instructions.

**Returns**:

  Text that points the user at the ``migrate_cfg`` command to
  rewrite the configuration file in the current format.

<a id="backlogops_cli._migrate_warn.CliPresetMigrateWarnHook"></a>

## CliPresetMigrateWarnHook Objects

```python
class CliPresetMigrateWarnHook(MigrateCfgWarnHook)
```

Tell the user to migrate an old preset file with ``migrate_cfg``.

<a id="backlogops_cli._migrate_warn.CliPresetMigrateWarnHook.migrate_instructions"></a>

#### migrate\_instructions

```python
@classmethod
def migrate_instructions(cls) -> str
```

Return the command line preset migration instructions.

**Returns**:

  Text that points the user at the ``migrate_cfg`` command with
  the ``--kind`` option for input or output preset files.

<a id="backlogops_cli.bloc_version_reporter"></a>

# backlogops\_cli.bloc\_version\_reporter

Version reporter for the backlogops_cli package.

<a id="backlogops_cli.bloc_version_reporter.BloCliVersionReporter"></a>

## BloCliVersionReporter Objects

```python
class BloCliVersionReporter(BloVersionReporter)
```

Version reporter for the backlogops_cli package.

<a id="backlogops_cli.bloc_version_reporter.BloCliVersionReporter.package_names"></a>

#### package\_names

```python
@override
def package_names() -> list[str]
```

Return the package names that this package reports.

<a id="backlogops_cli.bloc_version_reporter.BloCliVersionReporter.get_main_package_name"></a>

#### get\_main\_package\_name

```python
@override
@classmethod
def get_main_package_name(cls) -> str
```

Return the name of the main package.

<a id="backlogops_cli.plan_release_dates"></a>

# backlogops\_cli.plan\_release\_dates

Set planned release dates from the estimated release dates.

The command reads a backlog and its releases whose estimated release
dates are already filled in, then sets each planned release date to the
estimated release date plus a slack buffer, as documented for
:func:`backlogops.release_plan_on_estimate`. The backlog and the releases
with the new planned dates are written to the output file, and the list of
planned date changes is printed to stdout, or also saved to a file when
``--changes-file`` is given.

<a id="backlogops_cli.plan_release_dates.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the plan-dates command.

<a id="backlogops_cli.plan_release_dates._plan"></a>

#### \_plan

```python
def _plan(
        parsed: argparse.Namespace,
        data: BacklogReleases) -> tuple[str, Optional[Callable[[str], None]]]
```

Set the planned release dates and return the change report.

<a id="backlogops_cli.plan_release_dates.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Set the planned release dates and write the output file.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be read, planned or
  written.

<a id="backlogops_cli.order_releases"></a>

# backlogops\_cli.order\_releases

Order the releases by date and write the result.

The command reads a backlog and its releases from an input file and orders
the releases by their planned date, or by their estimated date when
``--by-estimated`` is given. A release with no date of the chosen kind is
placed at the end, and releases that share a date keep their original
order. The backlog is written back unchanged together with the ordered
releases. The input and output formats are inferred from the file name
extensions, but can be overridden by a configuration file or by a named
preset.

<a id="backlogops_cli.order_releases.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the order_releases command.

<a id="backlogops_cli.order_releases._ordered"></a>

#### \_ordered

```python
def _ordered(parsed: argparse.Namespace,
             config: Optional[BacklogOpsConfig]) -> BacklogReleases
```

Read the data and return it with the releases ordered by date.

<a id="backlogops_cli.order_releases.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Order the releases by date and write the output file.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be read, ordered or
  written.

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
def _ordered(parsed: argparse.Namespace,
             config: Optional[BacklogOpsConfig]) -> BacklogReleases
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

<a id="backlogops_cli.order_by_release"></a>

# backlogops\_cli.order\_by\_release

Order the backlog to follow the release order and write the result.

The command reads a backlog and its releases from an input file and orders
the backlog items so that they follow the order of the releases. The
releases are taken in their current file order and are written back
unchanged; order the releases first (for example with the order_releases
command) when a date order is wanted. By default the items are only grouped
by release, keeping their original relative order within a release. With
``--honor-deps`` no item is placed before an item that must be delivered
before it; a prerequisite that is planned for a later release is then
pulled to an earlier release, unless ``--later`` is given, in which case
the dependent is pushed to a later release instead. The input and output
formats are inferred from the file name extensions, but can be overridden
by a configuration file or by a named preset.

<a id="backlogops_cli.order_by_release.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the order_by_release command.

<a id="backlogops_cli.order_by_release._ordered"></a>

#### \_ordered

```python
def _ordered(parsed: argparse.Namespace,
             config: Optional[BacklogOpsConfig]) -> BacklogReleases
```

Read the data and order the backlog by the release order.

<a id="backlogops_cli.order_by_release.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Order the backlog by release order and write the output file.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be read, ordered or
  written.

<a id="backlogops_cli.preset_wizard"></a>

# backlogops\_cli.preset\_wizard

Run the IO preset wizard and store the created preset file.

The created file holds a single input or output TableIO preset (a format
configuration with its column-name maps, and a level display for an output
preset). Such a stand-alone file is used wherever an input or output
configuration is taken, by giving its file name.

<a id="backlogops_cli.preset_wizard.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the preset wizard command.

<a id="backlogops_cli.preset_wizard.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Run the interactive IO preset wizard and write the preset file.

The wizard asks whether to build an input or an output preset and then
the settings for it. The output filename receives the ``.cfg``
extension when it is not already present.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the wizard is abandoned or the preset
  cannot be written.

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
def _reordered(parsed: argparse.Namespace,
               config: Optional[BacklogOpsConfig]) -> BacklogReleases
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

<a id="backlogops_cli.read_jira"></a>

# backlogops\_cli.read\_jira

Read a backlog and its releases from Jira and store them to a file.

The command reads the backlog items and the releases from Jira using a
named from-Jira preset of the backlog-ops configuration, then writes them
to an output file like the other commands (the output format is inferred
from the file name or taken from an output preset or config file).

The ``--preset`` flag names the Jira preset to use; the optional
``--filter`` flag supplies a Jira Query Language filter to use instead of
the preset's default. An encrypted Jira token is unlocked by a pass
phrase asked on the terminal only when it is needed.

<a id="backlogops_cli.read_jira.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the read-from-Jira command.

<a id="backlogops_cli.read_jira._passphrase"></a>

#### \_passphrase

```python
def _passphrase() -> str
```

Ask for the Jira token pass phrase on the terminal.

<a id="backlogops_cli.read_jira._warn_if_inconsistent"></a>

#### \_warn\_if\_inconsistent

```python
def _warn_if_inconsistent(data: BacklogReleases) -> None
```

Warn when the data read from Jira is not fully consistent.

A filtered read can leave a cross reference dangling, for example a
parent or release that the filter excluded. The problem is reported
but the file is still written, so a partial read still produces output.

<a id="backlogops_cli.read_jira._read_jira"></a>

#### \_read\_jira

```python
def _read_jira(parsed: argparse.Namespace,
               config: Optional[BacklogOpsConfig]) -> BacklogReleases
```

Read the backlog and releases from Jira for the named preset.

<a id="backlogops_cli.read_jira.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Read a backlog and releases from Jira and write them to a file.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be read or written.

<a id="backlogops_cli.estimate_ready_date"></a>

# backlogops\_cli.estimate\_ready\_date

Estimate ready dates for a backlog and write the result.

The command reads a backlog and its releases from an input file and
estimates the ready date of each backlog item from the available teams,
as documented for :func:`backlogops.estimate_ready_date`. The teams
configuration (velocity, work hours, vacations and so on) is taken from
the file given by ``--config`` or, when that is absent, from the
configured backlog-ops file. The backlog with the estimated dates and the
releases are written to the output file. The input and output formats are
inferred from the file name extensions, but can be overridden by a
configuration file or by a named preset.

<a id="backlogops_cli.estimate_ready_date.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the estimate command.

<a id="backlogops_cli.estimate_ready_date._start_date"></a>

#### \_start\_date

```python
def _start_date(parsed: argparse.Namespace) -> Optional[date]
```

Return the start date from the command line, or None for today.

<a id="backlogops_cli.estimate_ready_date._estimate"></a>

#### \_estimate

```python
def _estimate(
        parsed: argparse.Namespace, config: Optional[BacklogOpsConfig],
        data: BacklogReleases) -> tuple[str, Optional[Callable[[str], None]]]
```

Estimate the dates and return the release date change report.

The configuration is required for this command, so ``config`` is never
None here; the assertion makes that explicit for the type checker.

<a id="backlogops_cli.estimate_ready_date.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Estimate the ready dates and write the output file.

The backlog with the estimated dates and the releases are written to
the output file. The estimated release dates are updated as well, and
the list of release date changes is printed to stdout, or also saved
to a file when ``--changes-file`` is given.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the data cannot be read, estimated
  or written.

