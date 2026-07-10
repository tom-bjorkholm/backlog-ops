# 5. Estimating ready dates and planning releases

← Previous: [Ordering the backlog](04_ordering.md) | [Contents](README.md) | Next: [Reporting a release forecast to the customer](06_customer_forecast.md) →

---

This is where backlogops earns its keep: turning an ordered backlog and a
known workforce into **dates**, and keeping the plan you have promised the
customer consistent with those dates. The natural sequence is:

1. **estimate** ready dates for items (and, from them, for releases);
2. **set the plan** from the estimate (for items, for releases, or both);
3. **adjust release content** so each release can actually meet its planned
   date;
4. **order releases** by date.

All of these need the workforce, so a configuration file is required
(chapter 1). Order the backlog first (chapter 4) — the estimate assumes the
teams work in backlog order.

## Estimate ready dates

Computes an estimated ready date for every item from the available teams
(velocity, work hours, vacations, part-time periods) and the backlog order.
Estimating the items also fills in the **estimated release dates**.

**CLI**

```sh
# Estimate, starting today:
python3 -m backlogops_cli.estimate_ready_date -c my.cfg \
    -i ordered.xlsx -o estimated.xlsx

# Start from a specific date and also copy each estimate to the plan:
python3 -m backlogops_cli.estimate_ready_date -c my.cfg \
    -i ordered.xlsx -o estimated.xlsx -d 2026-08-01 --set-plan --changes-file rel_dates.xlsx
```

| Flag | Meaning |
| --- | --- |
| `-d` / `--start-date` | ISO date the teams start working (default: today). |
| `--set-plan` | Also copy each estimated item date to its planned date. |
| `--changes-file` | Also save the list of release-date changes to a file. |

The list of release-date changes is printed to stdout (and saved with
`--changes-file`).

**GUI** — *Backlog → Estimate ready date…*

**Library** —
[`estimate_ready_date`](../backlogops_api.md#backlogops.estimate_ready_date.estimate_ready_date).

## Set the planned dates from the estimate

If you did not pass `--set-plan` while estimating, you can copy the estimated
**item** dates to their planned dates as a separate step. In the GUI this is
*Backlog → Set planned date from estimated*
([`set_plan_from_estimate`](../backlogops_api.md#backlogops.estimate_ready_date.set_plan_from_estimate));
in the CLI it is the `--set-plan` flag of the estimate command shown above.

To set the planned **release** dates, use the release planner, which sets
each planned release date to the estimated release date plus a slack buffer:

**CLI**

```sh
python3 -m backlogops_cli.plan_release_dates -c my.cfg \
    -i estimated.xlsx -o planned.xlsx --buffer-days 5 --changes-file changes.xlsx
```

`--buffer-days` (default 5) is the calendar-day slack kept against the
estimate. The list of planned-date changes is printed, and saved when
`--changes-file` is given.

**GUI** — *Backlog → Adjust planned release dates…*

**Library** —
[`release_plan_on_estimate`](../backlogops_api.md#backlogops.release_backlog_updates.release_plan_on_estimate)
(built on
[`estimate_release_dates`](../backlogops_api.md#backlogops.release_backlog_updates.estimate_release_dates)).

## Adjust release content to fit the planned dates

The opposite direction: rather than moving the dates to fit the content, move
the **content** to fit the dates. Each item is moved to the earliest release
whose planned date is on or after the item's estimated ready date plus the
buffer. Use this when the customer-facing release dates are fixed and you
need to see what can realistically ship in each.

**CLI**

```sh
python3 -m backlogops_cli.adjust_release_content -c my.cfg \
    -i estimated.xlsx -o adjusted.xlsx --buffer-days 5 --changes-file moves.xlsx
```

**GUI** — *Backlog → Adjust release content…*

**Library** —
[`adjust_release_content`](../backlogops_api.md#backlogops.release_backlog_updates.adjust_release_content).

## Order the releases by date

Sorts the releases (the backlog is written back unchanged) by planned date,
or by estimated date with `-e`. A release with no date of the chosen kind
goes to the end; ties keep their original order. Do this before
*order by release order* (chapter 4) when you want the backlog grouped in
date order.

**CLI**

```sh
python3 -m backlogops_cli.order_releases -i planned.xlsx -o sorted.xlsx
python3 -m backlogops_cli.order_releases -i estimated.xlsx -o sorted.xlsx -e
```

**GUI** — *Backlog → Order releases by date…*

**Library** —
[`order_releases_by_date`](../backlogops_api.md#backlogops.backlog_releases.BacklogReleases.order_releases_by_date).

## Releases in Jira

Jira stores releases as **versions**. Four commands keep them in step with
your plan. All take `-p`/`--preset`, print result lists unless `-q`, and
prompt for the token pass phrase only when needed.

### Set the release dates in Jira

Matches Jira versions to your releases **by name** and writes the mapped
fields — most importantly the release date.

```sh
python3 -m backlogops_cli.update_releases_in_jira -c my.cfg -p scrum \
    -i planned.xlsx

# Only two named releases, and create them if missing:
python3 -m backlogops_cli.update_releases_in_jira -c my.cfg -p scrum \
    -i planned.xlsx --release Next --release Later --only-listed --on-missing add
```

`--on-missing` is `raise` / `ignore` / `add`; `--release` names a release
(repeatable); `--only-listed` restricts the update to those names.
**GUI:** *Jira → Update releases in Jira…*. **Library:**
[`update_releases_in_jira`](../backlogops_api.md#backlogops.jira_update_releases.update_releases_in_jira).

### Create versions in Jira

```sh
python3 -m backlogops_cli.add_releases_to_jira -c my.cfg -p scrum \
    -i planned.xlsx --skip-existing
```

Stops on a name that already exists, unless `--skip-existing`. **GUI:**
*Jira → Add releases to Jira…*. **Library:**
[`add_releases_to_jira`](../backlogops_api.md#backlogops.jira_write_releases.add_releases_to_jira).

### Order the versions in Jira

```sh
# By their own release date:
python3 -m backlogops_cli.order_releases_in_jira -c my.cfg -p scrum --by-date

# By the order in a file, or by an input backlog's release order:
python3 -m backlogops_cli.order_releases_in_jira -c my.cfg -p scrum \
    --name-list order.txt
python3 -m backlogops_cli.order_releases_in_jira -c my.cfg -p scrum \
    -i planned.xlsx
```

Exactly one of `--by-date`, `--name-list FILE`, `-i FILE` must be given.
**GUI:** *Jira → Order releases in Jira…*. **Library:**
[`order_releases_in_jira`](../backlogops_api.md#backlogops.jira_order_releases.order_releases_in_jira).

### Rename versions in Jira

```sh
python3 -m backlogops_cli.rename_releases_in_jira -c my.cfg -p scrum \
    --rename "Next" "2026 Q3"

python3 -m backlogops_cli.rename_releases_in_jira -c my.cfg -p scrum \
    --rename-file renames.csv
```

One rename with `--rename OLD NEW`, or a two-column file with
`--rename-file` (old names in column one, new in column two). **GUI:**
*Jira → Rename releases in Jira…*. **Library:**
[`rename_releases_in_jira`](../backlogops_api.md#backlogops.jira_rename_releases.rename_releases_in_jira).

---

← Previous: [Ordering the backlog](04_ordering.md) | [Contents](README.md) | Next: [Reporting a release forecast to the customer](06_customer_forecast.md) →
