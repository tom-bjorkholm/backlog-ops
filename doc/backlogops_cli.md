# Table of Contents

* [backlogops\_cli.adjust\_release\_content](#backlogops_cli.adjust_release_content)
  * [build\_parser](#backlogops_cli.adjust_release_content.build_parser)
  * [main](#backlogops_cli.adjust_release_content.main)
* [backlogops\_cli.version](#backlogops_cli.version)
  * [main](#backlogops_cli.version.main)
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
* [backlogops\_cli.bloc\_version\_reporter](#backlogops_cli.bloc_version_reporter)
  * [BloCliVersionReporter](#backlogops_cli.bloc_version_reporter.BloCliVersionReporter)
    * [package\_names](#backlogops_cli.bloc_version_reporter.BloCliVersionReporter.package_names)
    * [get\_main\_package\_name](#backlogops_cli.bloc_version_reporter.BloCliVersionReporter.get_main_package_name)
* [backlogops\_cli.plan\_release\_dates](#backlogops_cli.plan_release_dates)
  * [build\_parser](#backlogops_cli.plan_release_dates.build_parser)
  * [main](#backlogops_cli.plan_release_dates.main)
* [backlogops\_cli.order\_releases](#backlogops_cli.order_releases)
  * [build\_parser](#backlogops_cli.order_releases.build_parser)
  * [main](#backlogops_cli.order_releases.main)
* [backlogops\_cli.order\_by\_deps](#backlogops_cli.order_by_deps)
  * [build\_parser](#backlogops_cli.order_by_deps.build_parser)
  * [main](#backlogops_cli.order_by_deps.main)
* [backlogops\_cli.order\_by\_release](#backlogops_cli.order_by_release)
  * [build\_parser](#backlogops_cli.order_by_release.build_parser)
  * [main](#backlogops_cli.order_by_release.main)
* [backlogops\_cli.order\_by\_keys](#backlogops_cli.order_by_keys)
  * [build\_parser](#backlogops_cli.order_by_keys.build_parser)
  * [main](#backlogops_cli.order_by_keys.main)
* [backlogops\_cli.estimate\_ready\_date](#backlogops_cli.estimate_ready_date)
  * [build\_parser](#backlogops_cli.estimate_ready_date.build_parser)
  * [main](#backlogops_cli.estimate_ready_date.main)

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
before it. The input and output formats are inferred from the file name
extensions, but can be overridden by a configuration file or by a named
preset.

<a id="backlogops_cli.order_by_release.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the order_by_release command.

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

<a id="backlogops_cli.estimate_ready_date"></a>

# backlogops\_cli.estimate\_ready\_date

Estimate ready dates for a backlog and write the result.

The command reads a backlog and its releases from an input file and
estimates the ready date of each backlog item from the available teams,
as documented for :func:`backlogops.estimate_ready_date`. The teams
configuration (velocity, work hours, vacations and so on) is taken from
the file given by ``--config`` or, when that is absent, from the
configured teams file. The backlog with the estimated dates and the
releases are written to the output file. The input and output formats are
inferred from the file name extensions, but can be overridden by a
configuration file or by a named preset.

<a id="backlogops_cli.estimate_ready_date.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the estimate command.

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

