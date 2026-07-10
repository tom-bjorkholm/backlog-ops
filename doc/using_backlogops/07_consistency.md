# 7. Checking backlog consistency

← Previous: [Reporting a release forecast to the customer](06_customer_forecast.md) | [Contents](README.md)

---

A backlog is only useful if its structure holds together: keys are unique,
parents exist and sit above their children, releases referenced by items
actually exist, and dependencies do not form a cycle. backlogops checks all
of this for you, and — importantly — it does so **automatically**, so you
mostly do not have to think about it.

## What is checked

When a backlog and its releases are validated, these must all hold:

- **Item internal consistency** — every required field is present and every
  field has a valid type and value (for example, a `key` with no whitespace
  and none of the forbidden characters).
- **Unique keys** — no two items share a key.
- **Valid references** — every `parent_key` and every dependency key refers
  to an item that exists.
- **Level hierarchy** — each parent is at a *higher* level than its child.
- **No dependency cycles** — the scheduling graph (explicit dependencies plus
  the implicit parent/child ones) has no cycle.
- **Unique release names** — no two releases share a name.
- **Release cross-reference** — every release named by an item exists in the
  releases list.

The library functions are
[`check_backlog_consistency`](../backlogops_api.md#backlogops.backlog.check_backlog_consistency)
for the backlog alone, and
[`BacklogReleases.check_consistency`](../backlogops_api.md#backlogops.backlog_releases.BacklogReleases.check_consistency)
for a backlog together with its releases (which also runs the
release-name-uniqueness and cross-reference checks).

## You get it for free

Every command that reads a backlog validates it immediately after reading.
The CLI reader calls the consistency check as part of loading the input, so:

- if the input file is inconsistent, the command **stops and reports the
  problem** on standard error, rather than producing a subtly wrong result;
- the demo backlog and the outputs of the operations are all consistent by
  construction, so a clean round trip stays clean.

There is therefore no separate "check" command to run in the normal case —
loading the file *is* the check. In the GUI the same validation runs when you
read a backlog (from a file or from Jira) or create the demo; a problem is
shown in an error dialog and the backlog window is not opened with bad data.

## Reading the error, and fixing it

The reports name the offending key, field or release, so the message points
straight at the row to fix. Typical causes and fixes:

| Message is about | Likely cause | Fix |
| --- | --- | --- |
| A duplicate key | Two rows with the same `key` | Make each key unique. |
| A missing reference | A `parent_key`, dependency or `release` that does not exist | Add the referenced item/release, or correct the name. |
| A level violation | A parent at the same or a lower level than its child | Raise the parent's level or lower the child's. |
| A dependency cycle | Items that (directly or via parents) depend on each other | Break the cycle by removing one dependency. |
| A bad key/value | Whitespace or a forbidden character in a key, an unknown status | Clean the value; map custom statuses in the configuration (chapter 1). |

Because validation happens on read, the safe way to repair a bad export is:
open it in the tool it came from (a spreadsheet, or Jira), fix the flagged
rows, and read it again. Once it loads without complaint, every later
operation in this manual can be trusted to keep it consistent.

---

← Previous: [Reporting a release forecast to the customer](06_customer_forecast.md) | [Contents](README.md)
