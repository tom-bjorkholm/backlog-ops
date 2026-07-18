# 3. Moving a backlog between files, formats and Jira

← Previous: [The backlog and a demo](02_backlog_basics.md) | [Contents](README.md) | Next: [Ordering the backlog](04_ordering.md) →

---

Every other task starts by getting a backlog **in** and ends by writing it
**out**. This chapter covers those endpoints on their own: reading and
writing files, converting between formats, pulling a backlog out of Jira, and
pushing a file backlog into Jira. Later chapters reuse these steps and refer
back here.

Two things are worth stating once, because they shape every workflow:

- **The CLI is file-to-file.** Each command reads a file and writes a file.
  To transform a Jira backlog from the CLI you therefore do it in steps:
  read Jira into a file, transform the file, write the file back to Jira.
- **The GUI is in-memory.** You read a backlog into a window (from a file or
  from Jira), apply operations to the data in that window, then write it out.
  No intermediate files are needed.

Each backlog window shows, at the top, where its data came from and when it
was read — the file name for a file, the Jira filter for Jira — so several
open windows stay easy to tell apart. A **modified** mark appears once you
change the backlog in that window. A **Read again** button re-reads the same
source (the same file, or the same Jira preset and filter), replaces the
window's contents in place, and updates the shown read time, so you can
refresh a window instead of opening a new one. If the window has unsaved
changes, Read again asks for confirmation first. Saving back to the same file
the window was read from clears the modified mark.

## Convert between file formats

The simplest job: read one file, write another, possibly in a different
format and with different column names.

**CLI**

```sh
# Excel to CSV, format inferred from the extensions:
python3 -m backlogops_cli.convert -i demo.xlsx -o demo.csv

# Apply a named input preset when reading and an output preset when writing:
python3 -m backlogops_cli.convert -i export.xlsx -I from-excel \
    -o clean.ods -O customer-report
```

Common flags shared by all file commands:

| Flag | Meaning |
| --- | --- |
| `-i` / `--input` | Input data file. |
| `-I` / `--input-config` | Input format: a preset name or a config-file path. |
| `-o` / `--output` | Output data file. |
| `-O` / `--output-config` | Output format: a preset name or a config-file path. |
| `-c` / `--config` | The backlog-ops configuration file (holds the named presets). |
| `--releases-first` | Write the releases table before the backlog table. |
| `-f` / `--force` | Overwrite an existing output file without asking. |

**GUI** — *File → Read backlog from file…* opens a backlog window; then
*Backlog → Save to file…* writes it, letting you choose the format. Reading
uses the input side of your configuration; saving uses the output side.

**Library** —
[`read_backlog_releases`](../backlogops_api.md#backlogops.backlog_releases_io.read_backlog_releases)
and
[`write_backlog_releases`](../backlogops_api.md#backlogops.backlog_releases_io.write_backlog_releases).

Reading always **validates** the data (chapter 7); a broken file is reported
rather than silently loaded.

## Pull a backlog out of Jira

Reads the backlog items and releases from Jira through a preset and writes
them to a file, exactly like the other commands write their output.

**CLI**

```sh
# Read with the preset's own default filter:
python3 -m backlogops_cli.read_jira -c my.cfg -p scrum -o from_jira.xlsx

# Override the filter for this one run:
python3 -m backlogops_cli.read_jira -c my.cfg -p scrum \
    --filter "project = SCRUM AND labels = q3 ORDER BY rank" \
    -o q3.xlsx
```

| Flag | Meaning |
| --- | --- |
| `-p` / `--preset` | The Jira preset to read through. |
| `--filter` | A JQL filter to use instead of the preset's default. |
| `-o` / `-O` | Output file and (optional) output format, as above. |

An encrypted token is unlocked by a pass-phrase prompt only when the read
actually reaches Jira. For the recommended `ENCRYPTED_FILE` storage mode you
first create that encrypted token file once — see [Creating the encrypted
token file](01_configuration.md#creating-the-encrypted-token-file).

**GUI** — *File → Read backlog from Jira…* Pick the preset (and optionally a
filter); a backlog window opens on the Jira data, ready for any operation. The
window's **Read again** button re-reads the same preset and filter in place.

**Library** —
[`read_jira_from_config`](../backlogops_api.md#backlogops.jira_read.read_jira_from_config).

## Push a file backlog into Jira

There are two ways to send a backlog to Jira, depending on whether the items
already exist there.

### Add new items

Creates one Jira issue per backlog item.

**CLI**

```sh
python3 -m backlogops_cli.add_to_jira -c my.cfg -p scrum -i demo.xlsx

# Skip items whose key already exists, and record what was created:
python3 -m backlogops_cli.add_to_jira -c my.cfg -p scrum -i demo.xlsx \
    --skip-existing --added-file created.xlsx
```

By default it **stops** if an item's key already exists in Jira;
`--skip-existing` skips those instead. `--rank` additionally ranks the new
issues to match your file's order (see [chapter 4](04_ordering.md)). The
added items (with their new Jira keys) and the pre-existing items are printed
as two lists, unless `-q`; `--added-file` / `--existing-file` also save them.

**GUI** — *Jira → Add backlog to Jira…*

**Library** —
[`add_backlog_to_jira`](../backlogops_api.md#backlogops.jira_write.add_backlog_to_jira).

### Update existing items

Matches Jira issues to file items **by key** and changes only the columns you
choose — nothing else on the issue is touched.

**CLI**

```sh
# Update only the story-point and title columns:
python3 -m backlogops_cli.update_backlog_in_jira -c my.cfg -p scrum \
    -i edited.xlsx -s story_points title

# Update everything mapped and writable except the description:
python3 -m backlogops_cli.update_backlog_in_jira -c my.cfg -p scrum \
    -i edited.xlsx -e description
```

You must give exactly one of:

| Flag | Meaning |
| --- | --- |
| `-s` / `--store` | Columns to update, or the single word `all`. |
| `-e` / `--exclude` | Update every mapped, writable column **except** these. |

Two more choices matter:

- `--on-missing` — what to do with a key not present in Jira: `raise`
  (default, stop), `ignore` (skip it), or `add` (create it with all fields).
- `--links` — how parent and dependency links are updated: `reconcile`
  (default; make Jira match the file exactly, removing links the file no
  longer has) or `add` (only add missing links, never remove).

`--rank` can again re-rank to match the file order.

**GUI** — *Jira → Update backlog in Jira…*

**Library** —
[`update_backlog_in_jira`](../backlogops_api.md#backlogops.jira_update_backlog.update_backlog_in_jira).

## Putting it together

These endpoints compose into round trips. A CLI Jira round trip is
read → transform-a-file → update:

```sh
python3 -m backlogops_cli.read_jira -c my.cfg -p scrum -o work.xlsx
python3 -m backlogops_cli.order_by_deps -i work.xlsx -o work.xlsx -f
python3 -m backlogops_cli.update_backlog_in_jira -c my.cfg -p scrum \
    -i work.xlsx -s parent_key --rank backlog-top
```

The equivalent in the GUI is: *Read backlog from Jira → Backlog → Order by
dependencies… → Jira → Rank items in Jira…* — all on the one window, no
files. The next chapters describe those middle steps.

---

← Previous: [The backlog and a demo](02_backlog_basics.md) | [Contents](README.md) | Next: [Ordering the backlog](04_ordering.md) →
