# 6. Reporting a release forecast to the customer

← Previous: [Estimating ready dates and planning releases](05_estimating.md) | [Contents](README.md) | Next: [Checking backlog consistency](07_consistency.md) →

---

A very common situation: **the backlog lives in Jira** and stays there, but
the customer wants a readable release forecast — an Excel or ODS sheet, with
friendly column names, that says when each release is expected. This chapter
threads the earlier pieces into that one goal. The backlog is never modified
in Jira; the output is a file for the customer.

The shape of the workflow is: **read from Jira → estimate → write a clean
file**, using an *output preset* (chapter 1) to make the file
customer-friendly.

## Prepare a customer output preset

The `customer-report` output preset from [chapter 1](01_configuration.md)
does the presentation work. It renames internal fields to words a customer
understands and drops the columns they should not see. Recall its column
maps:

```json
"customer-report": {
    "tableio": {"format_name": "Excel"},
    "level_display": "NAME",
    "backlog_to_external": {"key": "Issue key", "title": "Summary",
                            "estimated_ready_date": "Forecast",
                            "story_points": null},
    "release_to_external": {"name": "Release",
                            "planned_date": "Committed date",
                            "estimated_date": "Forecast date"}
}
```

Mapping a field to `null` (here `story_points`) drops it from the sheet;
everything unmapped is written under its own name. Set `level_display` to
`NAME` so the customer sees `Epic`/`Story`, not numbers.

## Do it from the CLI

Because the CLI is file-to-file, the forecast is a short pipeline:

```sh
# 1. Read the current backlog and releases out of Jira.
python3 -m backlogops_cli.read_jira -c my.cfg -p scrum -o snapshot.xlsx

# 2. (Optional) order by dependencies so the estimate is realistic.
python3 -m backlogops_cli.order_by_deps -i snapshot.xlsx -o snapshot.xlsx -f

# 3. Estimate ready dates (fills in the estimated release dates too).
python3 -m backlogops_cli.estimate_ready_date -c my.cfg \
    -i snapshot.xlsx -o snapshot.xlsx -f

# 4. Write the customer forecast through the output preset.
python3 -m backlogops_cli.convert -c my.cfg \
    -i snapshot.xlsx -o forecast_for_customer.xlsx -O customer-report
```

Steps 2–4 read and write the same working file; step 4 re-formats it for the
customer. Nothing is written back to Jira, so the customer report can never
disturb the real backlog.

## Do it from the GUI

1. *File → Read backlog from Jira…* — pick the `scrum` preset. A backlog
   window opens on the Jira data.
2. *Backlog → Order by dependencies…* (optional).
3. *Backlog → Estimate ready date…* — the estimated dates now appear in the
   window.
4. *Backlog → Save to file…* — choose the `customer-report` output preset (or
   a stand-alone preset file) and save as `.xlsx` or `.ods`.

Everything happens in the one window; no intermediate files.

## Keeping Jira and the report in agreement (optional)

If you also want Jira's version dates to match the forecast you just sent,
push the planned dates back — this is the only step that writes to Jira:

```sh
python3 -m backlogops_cli.plan_release_dates -c my.cfg \
    -i snapshot.xlsx -o snapshot.xlsx -f
python3 -m backlogops_cli.update_releases_in_jira -c my.cfg -p scrum \
    -i snapshot.xlsx
```

Or, in the GUI, *Backlog → Adjust planned release dates…* followed by
*Jira → Update releases in Jira…*. Leave these out when the report is meant
to be a forecast only.

## Why this uses only pieces you have already seen

| Step | Command / menu | Library function |
| --- | --- | --- |
| Read from Jira | `read_jira` / *Read backlog from Jira* | [`read_jira_from_config`](../backlogops_api.md#backlogops.jira_read.read_jira_from_config) |
| Order | `order_by_deps` / *Order by dependencies* | [`order_by_dependencies`](../backlogops_api.md#backlogops.order_by_dependencies.order_by_dependencies) |
| Estimate | `estimate_ready_date` / *Estimate ready date* | [`estimate_ready_date`](../backlogops_api.md#backlogops.estimate_ready_date.estimate_ready_date) |
| Write the report | `convert` / *Save to file* | [`write_backlog_releases`](../backlogops_api.md#backlogops.backlog_releases_io.write_backlog_releases) |
| (Optional) push dates | `update_releases_in_jira` / *Update releases in Jira* | [`update_releases_in_jira`](../backlogops_api.md#backlogops.jira_update_releases.update_releases_in_jira) |

The customer-facing polish comes entirely from the **output preset**, which
is why setting it up once (chapter 1) pays off every reporting cycle.

---

← Previous: [Estimating ready dates and planning releases](05_estimating.md) | [Contents](README.md) | Next: [Checking backlog consistency](07_consistency.md) →
