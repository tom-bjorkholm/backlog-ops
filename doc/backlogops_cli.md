# Table of Contents

* [backlogops\_cli.jira\_fields](#backlogops_cli.jira_fields)
  * [build\_parser](#backlogops_cli.jira_fields.build_parser)
  * [main](#backlogops_cli.jira_fields.main)
* [backlogops\_cli.update\_backlog\_in\_jira](#backlogops_cli.update_backlog_in_jira)
  * [build\_parser](#backlogops_cli.update_backlog_in_jira.build_parser)
  * [main](#backlogops_cli.update_backlog_in_jira.main)
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
* [backlogops\_cli.migrate\_cfg](#backlogops_cli.migrate_cfg)
  * [KIND\_CLASSES](#backlogops_cli.migrate_cfg.KIND_CLASSES)
  * [MIGRATE\_ERRORS](#backlogops_cli.migrate_cfg.MIGRATE_ERRORS)
  * [build\_parser](#backlogops_cli.migrate_cfg.build_parser)
  * [main](#backlogops_cli.migrate_cfg.main)
* [backlogops\_cli.config\_wizard](#backlogops_cli.config_wizard)
  * [build\_parser](#backlogops_cli.config_wizard.build_parser)
  * [main](#backlogops_cli.config_wizard.main)
* [backlogops\_cli.add\_to\_jira](#backlogops_cli.add_to_jira)
  * [build\_parser](#backlogops_cli.add_to_jira.build_parser)
  * [main](#backlogops_cli.add_to_jira.main)
* [backlogops\_cli.convert](#backlogops_cli.convert)
  * [build\_parser](#backlogops_cli.convert.build_parser)
  * [main](#backlogops_cli.convert.main)
* [backlogops\_cli.add\_releases\_to\_jira](#backlogops_cli.add_releases_to_jira)
  * [build\_parser](#backlogops_cli.add_releases_to_jira.build_parser)
  * [main](#backlogops_cli.add_releases_to_jira.main)
* [backlogops\_cli.extract\_keys](#backlogops_cli.extract_keys)
  * [build\_parser](#backlogops_cli.extract_keys.build_parser)
  * [main](#backlogops_cli.extract_keys.main)
* [backlogops\_cli.rank\_in\_jira](#backlogops_cli.rank_in_jira)
  * [build\_parser](#backlogops_cli.rank_in_jira.build_parser)
  * [main](#backlogops_cli.rank_in_jira.main)
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
* [backlogops\_cli.preset\_wizard](#backlogops_cli.preset_wizard)
  * [build\_parser](#backlogops_cli.preset_wizard.build_parser)
  * [main](#backlogops_cli.preset_wizard.main)
* [backlogops\_cli.order\_releases\_in\_jira](#backlogops_cli.order_releases_in_jira)
  * [build\_parser](#backlogops_cli.order_releases_in_jira.build_parser)
  * [main](#backlogops_cli.order_releases_in_jira.main)
* [backlogops\_cli.order\_by\_keys](#backlogops_cli.order_by_keys)
  * [build\_parser](#backlogops_cli.order_by_keys.build_parser)
  * [main](#backlogops_cli.order_by_keys.main)
* [backlogops\_cli.read\_jira](#backlogops_cli.read_jira)
  * [build\_parser](#backlogops_cli.read_jira.build_parser)
  * [main](#backlogops_cli.read_jira.main)
* [backlogops\_cli.update\_releases\_in\_jira](#backlogops_cli.update_releases_in_jira)
  * [build\_parser](#backlogops_cli.update_releases_in_jira.build_parser)
  * [main](#backlogops_cli.update_releases_in_jira.main)
* [backlogops\_cli.rename\_releases\_in\_jira](#backlogops_cli.rename_releases_in_jira)
  * [build\_parser](#backlogops_cli.rename_releases_in_jira.build_parser)
  * [main](#backlogops_cli.rename_releases_in_jira.main)
* [backlogops\_cli.estimate\_ready\_date](#backlogops_cli.estimate_ready_date)
  * [build\_parser](#backlogops_cli.estimate_ready_date.build_parser)
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

<a id="backlogops_cli.update_backlog_in_jira"></a>

# backlogops\_cli.update\_backlog\_in\_jira

Update a backlog in Jira from an input file, matching issues by key.

The command reads a backlog (or a backlog and its releases) from the input
file, then updates the matching Jira issues using a named preset of the
backlog-ops configuration, changing only a chosen subset of the mapped
fields. The subset is chosen with exactly one of two flags: ``-s``/``--store``
lists the columns to update (or the single word ``all`` for every mapped
writable column), while ``-e``/``--exclude`` updates every mapped writable
column except the listed ones.

``--on-missing`` chooses what to do with an item whose key is not present in
Jira: ``raise`` (the default) stops with an error, ``ignore`` leaves it
alone, and ``add`` creates it with all of its fields. ``--links`` chooses how
the parent and dependency links are updated: ``reconcile`` (the default) makes
the Jira links match the backlog exactly, removing a Jira link the backlog no
longer has and clearing a dropped parent, while ``add`` only adds the missing
links and never removes one. ``--links`` governs only the links; the other
selected fields are updated the same way under either value. With ``--rank``
the items are also ranked in Jira to match the backlog order, at the chosen
anchor.

The updated, already-correct, ignored, added and failed items are printed
to stdout as labelled lists, unless ``-q``/``--quiet`` is given. An
encrypted Jira token is unlocked by a pass phrase asked on the terminal
only when it is needed.

<a id="backlogops_cli.update_backlog_in_jira.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the update-backlog command.

<a id="backlogops_cli.update_backlog_in_jira.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Update a backlog in Jira and report the outcome per item.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the backlog cannot be updated or a key
  is not present in Jira with the raise policy.

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

<a id="backlogops_cli.add_to_jira"></a>

# backlogops\_cli.add\_to\_jira

Add a backlog to Jira from an input file, creating one issue per item.

The command reads a backlog (or a backlog and its releases) from the input
file, then adds the backlog items to Jira using a named preset of the
backlog-ops configuration. By default it stops with an error when an
item's key already exists in Jira; ``--skip-existing`` skips those items
instead. With ``--rank`` the items are also ranked in Jira to match the
supplied backlog order, at the chosen anchor.

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

<a id="backlogops_cli.rank_in_jira"></a>

# backlogops\_cli.rank\_in\_jira

Move key-list items to a chosen anchor of a Jira backlog by rank.

The command reads a key list from a file and moves the named issues to a
chosen anchor of the backlog read by a named preset of the backlog-ops
configuration. ``--anchor`` places them at the top (the default) or the
bottom end of the backlog, or relative to the first or last key of the list.
The backlog is the issues the preset filter reads in their Jira rank order;
``--filter`` overrides that filter for one run and may only order by rank.

By default only the named issues are ranked, in the listed order. With
``--honor-relations`` the named issues, their descendants and their
dependencies are moved as one block, ordered so that a parent is ranked
before its child and a prerequisite before its dependent. Every other issue
keeps its Jira rank order. The re-ranked keys and the named keys that are
not part of the backlog are printed to stdout unless ``-q``/``--quiet`` is
given. An encrypted Jira token is unlocked by a pass phrase asked on the
terminal only when it is needed.

<a id="backlogops_cli.rank_in_jira.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the rank-in-Jira command.

<a id="backlogops_cli.rank_in_jira.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Move key-list items in the Jira rank order and report the outcome.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the items cannot be ranked.

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

<a id="backlogops_cli.order_releases_in_jira"></a>

# backlogops\_cli.order\_releases\_in\_jira

Order releases in Jira, changing the order of a project's versions.

The command reorders the Jira versions of a named preset of the backlog-ops
configuration. Exactly one order source must be given, and the three are
mutually exclusive: ``--by-date`` orders the versions by their own release
date, earliest first, with undated versions at the end; ``--name-list`` names
a file whose lines give the wanted order, one release name per line; and
``-i``/``--input`` names a backlog-and-releases input file whose release order
is used. argparse enforces that exactly one of the three is given.

With ``--by-date`` every version is ordered. With a name source, the named
versions are moved to the front in the listed order and every other version
keeps its existing relative order and trails them; a name that is not a
version is reported. The ordered names and the names not in Jira are printed
to stdout unless ``-q``/``--quiet`` is given. An encrypted Jira token is
unlocked by a pass phrase asked on the terminal only when it is needed.

<a id="backlogops_cli.order_releases_in_jira.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the order-releases command.

The three order sources form a required, mutually exclusive group, so
argparse checks that exactly one of them is given. Giving the input file
with ``-i``/``--input`` is itself the third source; ``-I`` only names its
format.

<a id="backlogops_cli.order_releases_in_jira.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Order releases in Jira and report the ordered and skipped names.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the order cannot be resolved or applied.

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

<a id="backlogops_cli.update_releases_in_jira"></a>

# backlogops\_cli.update\_releases\_in\_jira

Update releases in Jira from an input file, matching versions by name.

The command reads a backlog and its releases from the input file, then
updates the matching Jira versions using a named preset of the backlog-ops
configuration, changing each version's mapped fields (most importantly the
release date) to match the internal release. ``--on-missing`` chooses what
to do with a release whose name is not present in Jira: ``raise`` (the
default) stops with an error, ``ignore`` leaves it alone, and ``add``
creates it. ``--release`` names releases and may be given several times;
``--only-listed`` limits the update to just those named releases, while
without it every input release is updated.

The updated, already-correct, ignored, added and failed releases are
printed to stdout as labelled lists, unless ``-q``/``--quiet`` is given. An
encrypted Jira token is unlocked by a pass phrase asked on the terminal
only when it is needed.

<a id="backlogops_cli.update_releases_in_jira.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the update-releases command.

<a id="backlogops_cli.update_releases_in_jira.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Update releases in Jira and report the outcome per release.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the releases cannot be updated or a
  name is not present in Jira with the raise policy.

<a id="backlogops_cli.rename_releases_in_jira"></a>

# backlogops\_cli.rename\_releases\_in\_jira

Rename releases in Jira, changing Jira version names.

The command renames Jira versions of a named preset of the backlog-ops
configuration. A single rename is given with ``--rename OLD NEW``; a batch of
renames is read from a two column file named with ``--rename-file``, whose
first column holds the old names and second column the new names. The two
ways are mutually exclusive and one is required, which argparse enforces.

Each version is matched by its old name. An old name that is not a version, a
new name that equals the old name, and a new name that is already a version
name are reported rather than applied, and a rename Jira refuses is reported
with its reason; the other renames are still applied. The renamed, unchanged,
missing, colliding and failed renames are printed to stdout unless
``-q``/``--quiet`` is given. An encrypted Jira token is unlocked by a pass
phrase asked on the terminal only when it is needed.

<a id="backlogops_cli.rename_releases_in_jira.build_parser"></a>

#### build\_parser

```python
def build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the rename-releases command.

The single rename and the batch file form a required, mutually exclusive
group, so argparse checks that exactly one way is given. ``--rename``
takes both names at once, so its old and new name always travel together.

<a id="backlogops_cli.rename_releases_in_jira.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> int
```

Rename releases in Jira and report the outcome per rename.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.
  

**Returns**:

  ``0`` on success, ``1`` when the renames cannot be read or applied.

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

