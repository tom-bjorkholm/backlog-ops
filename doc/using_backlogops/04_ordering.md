# 4. Ordering the backlog

← Previous: [Moving a backlog between files, formats and Jira](03_files_and_jira.md) | [Contents](README.md) | Next: [Estimating ready dates and planning releases](05_estimating.md) →

---

The whole point of a single ordered backlog is that a team can take the next
item and just do it. This chapter is about producing that order. There are
three ways to reorder, and — because Jira keeps its own order as a **rank** —
one way to persist an order back to Jira.

Each ordering command reads a file and writes a file, so the two round trips
are:

- **File → file:** run the command on your file.
- **Jira → Jira:** *(CLI)* read Jira to a file, order the file, then update
  Jira or set the Jira rank from the file; *(GUI)* read Jira into a window,
  order, then *Jira → Rank items in Jira…*

## Order by dependencies

Reorders the backlog so no item comes before something it depends on. A team
can then follow the order top to bottom without ever being blocked.

**CLI**

```sh
python3 -m backlogops_cli.order_by_deps -i demo.xlsx -o ordered.xlsx

# Keep two keys far apart from their dependencies, and prefer pushing
# dependents later rather than pulling prerequisites earlier:
python3 -m backlogops_cli.order_by_deps -i demo.xlsx -o ordered.xlsx \
    -s S5 -s S6 --later --mode SPREAD
```

| Flag | Meaning |
| --- | --- |
| `-m` / `--mode` | Placement of dependency items (default `KEEP`). |
| `-s` / `--space-around` | A key to keep far from its dependencies; repeatable. |
| `-L` / `--later` | Push dependents later instead of pulling prerequisites earlier. |

**GUI** — *Backlog → Order by dependencies…*

**Library** —
[`order_by_dependencies`](../backlogops_api.md#backlogops.order_by_dependencies.order_by_dependencies).

## Order by a key list (bring chosen items to the front)

Sometimes you simply want certain items first — a themed sprint, an urgent
customer request. You give a **key list**, and those items (and, recursively,
everything they are the parent of) move to the front.

You usually build the key list with **extract keys**, which pulls the keys at
chosen levels out of a backlog, in backlog order:

```sh
# 1. Extract every epic key to a key-list file (levels by name or number):
python3 -m backlogops_cli.extract_keys -i demo.xlsx -l Epic -o epics.txt

# 2. Edit epics.txt down to the ones you want first, then reorder:
python3 -m backlogops_cli.order_by_keys -i demo.xlsx -k epics.txt -o front.xlsx
```

`extract_keys` takes `-l` / `--levels` (one or more level names, aliases or
numbers) and writes to `-o`, or to standard output when `-o` is omitted.
`order_by_keys` takes the key-list file with `-k` / `--key-list`.

**GUI** — *Backlog → Extract keys…* and *Backlog → Order by keys…*

**Library** —
[`get_keys_in_order`](../backlogops_api.md#backlogops.move_keys_first.get_keys_in_order)
for extraction and
[`move_keys_first`](../backlogops_api.md#backlogops.move_keys_first.move_keys_first)
for the reorder. (Key lists are read and written with
[`read_key_list`](../backlogops_api.md#backlogops.key_list_io.read_key_list) /
[`write_key_list`](../backlogops_api.md#backlogops.key_list_io.write_key_list).)

## Order in release order

Groups the backlog items so they follow the order of the releases — all of
the first release's items, then the next release's, and so on.

**CLI**

```sh
# Group by release, keeping each release's items in their current order:
python3 -m backlogops_cli.order_by_release -i demo.xlsx -o by_release.xlsx

# Also respect dependencies while doing so:
python3 -m backlogops_cli.order_by_release -i demo.xlsx -o by_release.xlsx \
    --honor-deps
```

The releases are taken in their **current file order** and written back
unchanged, so order the releases first when you want them in date order (see
[chapter 5](05_estimating.md)). With `--honor-deps` (`-d`) no item is placed
before a prerequisite: a prerequisite planned for a later release is pulled
earlier, unless `--later` (`-L`) is given, which pushes the dependent to a
later release instead.

**GUI** — *Backlog → Order by release order…*

**Library** —
[`backlog_in_release_order`](../backlogops_api.md#backlogops.backlog_in_release_order.backlog_in_release_order).

## Persist an order back to Jira (rank)

Jira does not store "position N"; it stores a **rank**. To make a Jira
backlog reflect an order you have decided, you move items in the rank order.
Two commands do this:

- Any of the write commands (`add_to_jira`, `update_backlog_in_jira`) accept
  `--rank`, which sets the Jira rank to match the file order, placing the
  items at an anchor: `backlog-top`, `backlog-bottom`, `first-key` (keep the
  first item fixed) or `last-key` (keep the last item fixed).
- `rank_in_jira` moves the items named by a key list to a chosen anchor,
  **without** a file round trip — it reads and re-ranks directly in Jira.

**CLI**

```sh
# Move the issues listed in hot.txt to the top of the Jira backlog:
python3 -m backlogops_cli.rank_in_jira -c my.cfg -p scrum -k hot.txt \
    --anchor backlog-top

# Move them and their descendants + dependencies as one block:
python3 -m backlogops_cli.rank_in_jira -c my.cfg -p scrum -k hot.txt \
    --anchor first-key --honor-relations
```

| Flag | Meaning |
| --- | --- |
| `-k` / `--key-list` | Key-list file naming the issues to move. |
| `--anchor` | Where to place them: `backlog-top` (default), `backlog-bottom`, `first-key`, `last-key`. |
| `--honor-relations` | Also move descendants and dependencies, parents before children, prerequisites before dependents. |
| `--filter` | Override the preset filter for this run (must order by rank only). |

**GUI** — *Jira → Rank items in Jira…*

**Library** —
[`jira_rank_move_keys`](../backlogops_api.md#backlogops.jira_rank_move_keys.jira_rank_move_keys).

### A complete Jira reorder

```sh
python3 -m backlogops_cli.read_jira -c my.cfg -p scrum -o work.xlsx
python3 -m backlogops_cli.order_by_deps -i work.xlsx -o work.xlsx -f
python3 -m backlogops_cli.extract_keys -i work.xlsx -l Epic -l Story -o keys.txt
python3 -m backlogops_cli.rank_in_jira -c my.cfg -p scrum -k keys.txt \
    --anchor backlog-top --honor-relations
```

In the GUI the same is: *Read backlog from Jira → Backlog → Order by
dependencies… → Jira → Rank items in Jira…*

---

← Previous: [Moving a backlog between files, formats and Jira](03_files_and_jira.md) | [Contents](README.md) | Next: [Estimating ready dates and planning releases](05_estimating.md) →
