# 2. The backlog and a demo to experiment with

← Previous: [Configuration files](01_configuration.md) | [Contents](README.md) | Next: [Moving a backlog between files, formats and Jira](03_files_and_jira.md) →

---

Before doing anything useful you need to know what a *backlog item* is, what
a *release* is, and how the two relate. This chapter is the shared vocabulary
for the rest of the manual, and it ends by creating a throw-away **demo
backlog** so you can try every later chapter without touching real data.

## The operating model

backlogops assumes a single backlog that the teams work through **in order**.
Items near the top are done first. Two dates matter for every item and every
release:

- the **planned ready date** — the date you have communicated to the
  customer;
- the **estimated ready date** — the date the current backlog implies, given
  team velocity and availability.

Most operations exist to compute the estimate, or to keep the plan and the
estimate consistent with each other and with the order of the backlog.

## A backlog item

Each item has these fields (any extra columns you keep are carried along
untouched):

| Field | Required | Notes |
| --- | --- | --- |
| `key` | yes | Unique. No whitespace and none of `, . ; : ( ) [ ] { }`. |
| `level` | yes | Integer. Higher = broader (task → story → epic). |
| `title` | yes | Free text. |
| `story_points` | yes | The size estimate. |
| `status` | yes | One of `TODO`, `IN_PROGRESS`, `DONE`, `REJECTED`. |
| `parent_key` | no | Key of a higher-level parent. Implies dependencies (below). |
| `release` | no | Release name. Must not contain tabs, newlines or control characters. |
| `team` | no | If set, only that team can do the item; if empty, any team. |
| `depends_on_f2s` | no | Keys that must **finish** before this can **start**. |
| `depends_on_f2f` | no | Keys that must **finish** before this can **finish**. |
| `depends_on_s2s` | no | Keys that must **start** before this can **start**. |
| `planned_ready_date` | no | The date promised to the customer. |
| `estimated_ready_date` | no | The computed date. |

### Levels

Levels are integers; you give them names and aliases in the configuration
(chapter 1). A **parent must sit at a higher level than its child**. In the
default naming, level 0 is a sub-task, 1 a story, 2 an epic.

### Dependencies

There are two sources of dependency:

- **Explicit** — the three `depends_on_*` lists, using the standard
  finish-to-start, finish-to-finish and start-to-start relationships.
- **Implicit, from `parent_key`** — a child cannot start before its parent
  starts, and a parent cannot finish until all its children finish.

Dependencies must not form a cycle. Ordering and estimation both rely on
them, so getting them right matters (chapters 4 and 5).

## Releases

A **release** has a name and, optionally, a planned date and an estimated
date. Backlog items point at a release by name. A backlog and its releases
travel together as one unit through every read, operation and write.

## File formats

A backlog and its releases are stored in tabular files through TableIO.
Currently you can **read** CSV, Excel and ODS, and **write** those plus nine
more formats. The format is detected from the file-name extension (`.xlsx` →
Excel, `.csv` → CSV, `.ods` → ODS), and you can override it with an input or
output preset (chapter 1) or a config file. Both tables (backlog and
releases) live in one file.

## Create a demo backlog to experiment with

The quickest way to learn the tool is to generate a small, realistic backlog
and run commands against it. The demo has three epics (`E1`–`E3`), twenty
stories (`S1`–`S20`), two sub-tasks (`T1`, `T2`), a handful of dependencies,
and two releases: `Next` (planned one month out) and `Later` (no date). It is
deliberately **not** in dependency or release order, so the ordering commands
have something to do — yet it passes every consistency check.

**CLI** — write it to any supported format:

```sh
python3 -m backlogops_cli.demo_backlog -o demo.xlsx
python3 -m backlogops_cli.demo_backlog -o demo.csv          # CSV instead
python3 -m backlogops_cli.demo_backlog -o demo.ods -O customer-report
```

`-O` (or `-O <preset>`) is optional; without it the format comes from the
extension.

**GUI** — *File → New demo backlog*. A backlog window opens on the demo data,
ready for the `Backlog` and `Jira` menus. Nothing is written until you choose
*Backlog → Save to file…*.

**Library** —
[`get_demo_backlog`](../backlogops_api.md#backlogops.demo_backlog.get_demo_backlog)
returns the same `BacklogReleases` object.

Every example in the following chapters assumes you have a `demo.xlsx` like
this to work on.

---

← Previous: [Configuration files](01_configuration.md) | [Contents](README.md) | Next: [Moving a backlog between files, formats and Jira](03_files_and_jira.md) →
