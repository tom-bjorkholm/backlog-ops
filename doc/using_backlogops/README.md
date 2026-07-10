# Using backlogops

This manual explains how to *use* backlogops to get real work done. The
[API documentation](../backlogops_api.md) is excellent for programmers
calling the library, but it does not explain the concepts, or when to reach
for which command. This manual fills that gap for people using the
**command line interface (CLI)** and the **graphical user interface (GUI)**,
while pointing at the library function behind each action for those who want
to script it.

## The three packages

backlogops ships as three packages that you install with `pip`:

| Package | What it is |
| --- | --- |
| [`backlogops`](https://pypi.org/project/backlogops/) | The library. All the real work lives here. |
| [`backlogops-cli`](https://pypi.org/project/backlogops-cli/) | A thin command line wrapper around the library. |
| [`backlogops-gui`](https://pypi.org/project/backlogops-gui/) | A Tkinter graphical wrapper around the library. |

The CLI and the GUI do the same things; they are two front ends over the
same library functions. Every task in this manual is therefore shown **both
ways**, and each names the top-level library function that actually performs
it, with a link into the [API documentation](../backlogops_api.md).

## Installing

On macOS and Linux:

```sh
pip3 install --upgrade backlogops backlogops-cli backlogops-gui
```

On Microsoft Windows:

```sh
pip install --upgrade backlogops backlogops-cli backlogops-gui
```

The GUI needs Tk 9.0.2 or newer for full functionality.

## Running the tools

**CLI.** Every command is a Python module run with `-m`. On macOS and Linux
use `python3`; on Windows use `python`. This manual writes `python3` in the
examples.

```sh
python3 -m backlogops_cli                     # list every available command
python3 -m backlogops_cli.demo_backlog -o demo.xlsx
python3 -m backlogops_cli.order_by_deps -i demo.xlsx -o ordered.xlsx
```

Add `--help` to any command to see its flags.

**GUI.** Start the application with:

```sh
python3 -m backlogops_gui                     # macOS / Linux
python3 -m backlogops_gui -c my_config.cfg    # start with a chosen config file
```

The GUI opens a small main window whose real functionality is in the menus.
Reading a backlog (from a file or from Jira, or creating a demo backlog)
opens a **backlog window** with a `Backlog` menu and a `Jira` menu.

## Where the configuration comes from

Almost every task can use a **backlog-ops configuration file** that holds the
workforce, named file presets, the levels, the status mapping and the Jira
connections. When you do not pass one explicitly, both the CLI (`-c`) and the
GUI look for it in the same order:

1. the file named by the `$BACKLOGOPS_CFG` environment variable;
2. `backlogops.cfg` inside the directory named by `$BACKLOGOPS_DIR`;
3. `.backlogops.cfg` in your home directory.

Chapter 1 is all about this file. Commands that only move data between files
work without any configuration, falling back to built-in defaults.

## The operating model in one paragraph

backlogops is built for teams that work off **one backlog, in backlog order**.
Items are ordered by priority and dependencies so a team can simply take the
next item. Each backlog item and each release can carry a **planned ready
date** (what you have promised the customer) and an **estimated ready date**
(what the current backlog, the team velocity, and the team's availability
imply). Most operations exist to keep those two in a sensible relationship.

## Chapters

1. [Configuration files](01_configuration.md) — what the configuration is
   for, the backlog-ops file and stand-alone presets, the Jira connection,
   and how to discover the correct Jira field mapping.
2. [The backlog and a demo to experiment with](02_backlog_basics.md) — the
   data model (items, levels, releases, dependencies), file formats, and a
   throw-away demo backlog to try everything on.
3. [Moving a backlog between files, formats and Jira](03_files_and_jira.md) —
   read and write files, convert formats, pull a backlog out of Jira, and
   push a file backlog into Jira.
4. [Ordering the backlog](04_ordering.md) — order by dependencies, by a key
   list, or in release order, and persist the order back to Jira by rank.
5. [Estimating ready dates and planning releases](05_estimating.md) —
   estimate ready dates, set planned dates, and keep release dates and
   release content consistent, in files and in Jira.
6. [Reporting a release forecast to the customer](06_customer_forecast.md) —
   keep the backlog in Jira, but produce a clean Excel/ODS forecast for the
   customer.
7. [Checking backlog consistency](07_consistency.md) — what is validated,
   how problems are reported, and where checks fit in a workflow.

## Full code documentation

- [Library public API](../backlogops_api.md)
- [Library protected API](../backlogops_protected_api.md)
- [CLI code](../backlogops_cli.md) and [GUI code](../backlogops_gui.md)
