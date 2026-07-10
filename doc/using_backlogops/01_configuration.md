# 1. Configuration files

[Contents](README.md) | Next: [The backlog and a demo](02_backlog_basics.md) →

---

Configuration is what turns backlogops from a set of file converters into a
tool that knows *your* teams, *your* column names and *your* Jira. This
chapter explains every kind of configuration, shows a complete example, and
walks through the single most confusing part for new Jira users: **finding
the correct field mapping**.

## The three ways a command gets its settings

1. **No configuration at all.** Commands that only move a backlog between
   files (`convert`, `order_by_deps`, and so on) work with built-in
   defaults: the file format is guessed from the file-name extension and no
   column renaming happens. This is enough for quick jobs.
2. **A backlog-ops configuration file** (usually named `backlogops.cfg`).
   This is the main configuration object. It holds the workforce, the named
   file presets, the levels, the status mapping and the whole Jira setup.
   Any command reaches it with `-c file.cfg`, or by discovery (see below).
3. **Stand-alone preset files.** A single input or output preset saved in
   its own file, handed to a command wherever an input or output format is
   expected (`-I file` / `-O file`). Useful when you want one reusable
   format description without a full configuration.

### How the configuration file is discovered

When you do not pass `-c` (CLI) or a start-up file (GUI `-c`), the file is
searched for in this order — identical for CLI and GUI:

1. `$BACKLOGOPS_CFG` — a full path to the file;
2. `backlogops.cfg` inside `$BACKLOGOPS_DIR`;
3. `.backlogops.cfg` in your home directory.

The library function behind reading and locating it is
[`get_backlog_ops_config`](../backlogops_api.md#backlogops.backlog_ops_config.get_backlog_ops_config);
reading a named file is
[`read_backlog_ops_config`](../backlogops_api.md#backlogops.backlog_ops_config.read_backlog_ops_config)
and writing one is
[`write_backlog_ops_config`](../backlogops_api.md#backlogops.backlog_ops_config.write_backlog_ops_config).

## What is inside the backlog-ops configuration file

The file is JSON. You will normally create it with the wizard rather than by
hand, but knowing the shape helps you read and tweak it. The top-level keys
are:

| Key | Purpose |
| --- | --- |
| `available_teams` | The workforce: persons, teams, and the company calendar. Used by date estimation. |
| `levels` | Your backlog levels and their names/aliases (optional; defaults apply when omitted). |
| `status_input_map` | Maps the status words in *your* files/Jira to the four internal statuses. |
| `input_configs` | Named input presets (file format + column renaming when reading). |
| `output_configs` | Named output presets (file format + column renaming when writing). |
| `gui_display` | How columns and levels are shown on screen in the GUI. |
| `jira` | Jira connections, column maps and presets (see [Jira](#jira-configuration)). |

### The workforce (`available_teams`)

This is what date estimation needs. A team has a **velocity** measured
against a reference workforce size (`sum_fte_at_velocity`) and a
`sprint_length`; each member is a person with a full-time-equivalent (`fte`).
Persons and members can carry **exceptions** — vacations, parental leave, a
month at half time — and the company calendar carries holidays.

```json
"available_teams": {
    "company_work_hours": {
        "work_hours": {"MONDAY": 8.0, "TUESDAY": 8.0, "WEDNESDAY": 8.0,
                       "THURSDAY": 8.0, "FRIDAY": 8.0,
                       "SATURDAY": 0.0, "SUNDAY": 0.0},
        "exceptions": [
            {"start_date": "2026-12-24", "end_date": "2026-12-26",
             "hours_per_day": 0.0, "new_work_days": false}
        ]
    },
    "persons": {
        "ada": {"name": "Ada",
                "exceptions": [
                    {"start_date": "2026-07-01", "end_date": "2026-07-20",
                     "hours_per_day": 0.0, "new_work_days": false}]},
        "bo": {"name": "Bo", "exceptions": []}
    },
    "teams": [
        {"name": "Phoenix", "velocity": 30.0, "sum_fte_at_velocity": 2.0,
         "sprint_length": 14, "aliases": [],
         "members": [
             {"person_name": "Ada", "fte": 1.0, "start_date": "2026-01-01",
              "fte_exceptions": [
                  {"start_date": "2026-02-01", "end_date": "2026-02-28",
                   "fte": 0.5}]},
             {"person_name": "Bo", "fte": 0.5, "fte_exceptions": []}]}
    ]
}
```

Read this as: *Team Phoenix delivers 30 story points per 14-day sprint when
it has 2 full-time people. Ada is full time from January (but half time in
February for training) and takes July 1–20 off; Bo is half time.* From this
plus the backlog, estimation can compute when each item will be ready.

### Levels

Backlog items live at integer **levels** (higher number = broader). If you
omit `levels`, the built-in defaults apply. Configure them to give levels
your own names and aliases (an alias lets an input file say `Bug` where you
mean level 1):

```json
"levels": [
    {"level": 0, "name": "Task", "aliases": []},
    {"level": 1, "name": "Story", "aliases": ["Bug"]},
    {"level": 2, "name": "Epic", "aliases": []}
]
```

### Status mapping

Internally there are four statuses: `TODO`, `IN_PROGRESS`, `DONE`,
`REJECTED`. Your files and Jira use many more words. `status_input_map` maps
each incoming word to one of the four. A sensible default map is created for
you (`Backlog`, `To Do` → `TODO`; `In Progress`, `In Review`, `Testing`,
`Blocked`, `On Hold` → `IN_PROGRESS`; `Closed` → `DONE`; `Rejected` →
`REJECTED`), and you extend it with whatever words your workflow uses.

### Input and output presets

A **preset** is a named bundle of "how to read this kind of file" or "how to
write this kind of file". It records the file format and the **column-name
map**. Column maps follow one simple rule in every direction:

- a column **not** in the map is read/written/shown **unchanged**;
- a column mapped to another name is **renamed**;
- a column mapped to `null` is **dropped** (an input drops the file column;
  an output does not write it).

An **input** preset maps external file column names to internal field names;
an **output** preset maps internal field names to the external column names
to write.

```json
"input_configs": {
    "from-excel": {
        "tableio": {"format_name": "Excel"},
        "backlog_to_internal": {"Issue key": "key", "Summary": "title",
                                "Points": "story_points"},
        "release_to_internal": {"Version": "name"},
        "status_input_map": {}
    }
},
"output_configs": {
    "customer-report": {
        "tableio": {"format_name": "Excel"},
        "level_display": "BOTH",
        "backlog_to_external": {"key": "Issue key", "title": "Summary",
                                "estimated_ready_date": "Forecast"},
        "release_to_external": {"name": "Release",
                                "planned_date": "Committed date"}
    }
}
```

`level_display` controls how the level is written: `NUMERIC` (number only),
`NAME` (name only), or `BOTH` (number and name in separate columns). You use
these preset names on the command line, for example
`-I from-excel` when reading or `-O customer-report` when writing.

## Jira configuration

The `jira` section is the largest, because talking to Jira needs three
things kept separately so they can be mixed and matched:

- **connections** — one per Jira server, with its URL, your login e-mail and
  how the API token is stored;
- **column maps** — `backlog_column_maps` and `release_column_maps`, each
  mapping an internal field to the path(s) that reach its value on a Jira
  issue or version. Backlog maps and release maps are kept apart so they can
  never be confused;
- **presets** — a named tie-together of one connection, one backlog map and
  one release map, plus a default project and a default filter. **One preset
  drives both reading and writing**, so you use the same preset name in both
  directions.

```json
"jira": {
    "connections": {
        "cloud": {
            "jira_type": "CLOUD",
            "base_url": "https://your-org.atlassian.net",
            "login_email": "you@example.com",
            "token_storage": "ENCRYPTED_FILE",
            "token_file_path": ".backlogops_jira_token"
        }
    },
    "backlog_column_maps": {"default-backlog": { "...": "see below" }},
    "release_column_maps": {"default-release": {
        "name": ["ATTRIBUTE", "name"],
        "planned_date": ["ATTRIBUTE", "releaseDate"]}},
    "presets": {
        "scrum": {
            "connection_name": "cloud",
            "backlog_column_map_name": "default-backlog",
            "release_column_map_name": "default-release",
            "backlog_write_map_name": "",
            "issue_type_map_name": "",
            "def_project": "SCRUM",
            "def_filter": "project = SCRUM ORDER BY rank"}
    }
}
```

### Connection type and token storage

A **cloud** connection authenticates with your login e-mail plus an API
token; a **server** connection uses the token as a personal access token.
The token is never written to the file in clear text unless you explicitly
choose a clear mode. The `token_storage` modes are:

| Mode | Meaning |
| --- | --- |
| `ENCRYPTED_FILE` | Token encrypted with a pass phrase, in a separate file. Recommended. |
| `ENCRYPTED_INTERNAL` | Token encrypted with a pass phrase, inside the config file. |
| `CLEAR_FILE` | Token in clear text in a separate file. Demo use only. |
| `CLEAR_INTERNAL` | Token in clear text inside the config file. Demo use only. |

With an encrypted mode you are asked for the pass phrase on the terminal
(CLI) or in a dialog (GUI) only when a command actually needs to reach Jira.
The clear modes print a warning, because anyone who reads the file reads your
token.

### Column maps: how a field reaches a Jira value

Each internal field maps to one or more **attribute paths**. A path starts
with a *kind* and then the steps to follow. The kinds are:

| Kind | Where it looks |
| --- | --- |
| `ATTRIBUTE` | A plain attribute of the issue/version object (e.g. `key`, `name`). |
| `FIELD` | A field inside the issue's `fields` (e.g. `summary`, `status.name`). |
| `CUSTOM_FIELD` | A custom field, looked up **by display name** (e.g. `Story point estimate`). |
| `FILTERED_FIELD` | A list field filtered by a sub-value (e.g. issue links of type `Blocks`). |

When more than one path is listed for a field, the first one that yields a
value wins. This is why the default `parent_key` maps to both the modern
`parent` object **and** the old `Epic Link` custom field. The usable default
backlog map looks like this:

```json
"default-backlog": {
    "key":            ["ATTRIBUTE", "key"],
    "level":          ["FIELD", "issuetype", "name"],
    "title":          ["FIELD", "summary"],
    "status":         ["FIELD", "status", "name"],
    "parent_key":     [["FIELD", "parent", "key"],
                       ["CUSTOM_FIELD", "Epic Link"]],
    "release":        ["FIELD", "fixVersions"],
    "team":           ["CUSTOM_FIELD", "Team"],
    "story_points":   ["CUSTOM_FIELD", "Story point estimate"],
    "depends_on_f2s": ["FILTERED_FIELD", "issuelinks", "type.name",
                       "Blocks", "inwardIssue.key"],
    "description":    ["FIELD", "description"]
}
```

Note that `level` maps to the Jira **issue type name** (`Story`, `Epic`, …),
which is resolved to a level number through your `levels`. So your level
names/aliases should match your Jira issue type names.

### Finding the correct field mapping in your Jira

The custom-field names above (`Story point estimate`, `Team`, `Epic Link`)
are Jira defaults, but **every Jira instance is different** — story points in
particular hide behind different custom fields in different sites. The
`jira_fields` command exists precisely to remove the guesswork. It prints the
custom fields your reader can see, and — with `--issue` — the fields an
individual issue's edit screen will actually accept.

```sh
# List the custom-field ids and their display names for a preset.
python3 -m backlogops_cli.jira_fields -c my.cfg -p scrum

# Also show which fields SCRUM-15's edit screen allows to be set.
python3 -m backlogops_cli.jira_fields -c my.cfg -p scrum --issue SCRUM-15
```

Use it two ways:

- **To pick the right name.** Find the row whose display name is the field
  you want (say `Story point estimate` → `customfield_10016`) and use that
  display name in a `CUSTOM_FIELD` path. The reader matches custom fields by
  display name, so you write the name, not the id.
- **To explain why a write is refused.** If updating a field silently does
  nothing, run with `--issue`: a field that is missing from that issue type's
  edit screen simply cannot be set through the Jira edit endpoint, no matter
  how it is mapped. The output tells you which is which.

Behind these two listings are
[`jira_custom_fields`](../backlogops_api.md#backlogops.jira_write.jira_custom_fields)
and
[`jira_editable_fields`](../backlogops_api.md#backlogops.jira_write.jira_editable_fields).

## Creating and maintaining configuration

You rarely write these files by hand. Three tools build and maintain them.

### The configuration wizard

Builds a complete backlog-ops file interactively: the workforce, the company
calendar, named presets, levels and the status map.

- **CLI:** `python3 -m backlogops_cli.config_wizard`
- **GUI:** *Configuration → Run configuration wizard…* On the very first
  start-up, when no configuration file exists yet, the GUI launches this
  wizard automatically.
- **Library:**
  [`backlog_ops_wizard`](../backlogops_api.md#backlogops.backlog_ops_wizard.backlog_ops_wizard).

To save the configuration you have loaded in the GUI, use *Configuration →
Write configuration…*
([`write_backlog_ops_config`](../backlogops_api.md#backlogops.backlog_ops_config.write_backlog_ops_config)).

### The preset wizard

Builds one stand-alone input or output preset file (format plus column maps,
and level display for an output preset). Use its file name wherever an input
(`-I`) or output (`-O`) format is expected.

- **CLI:** `python3 -m backlogops_cli.preset_wizard`
- **GUI:** *Configuration → Create IO preset file…*
- **Library:**
  [`preset_wizard`](../backlogops_api.md#backlogops.io_preset_wizard.preset_wizard).

### Migrating an older file

When the file format evolves, older files still load, and this rewrites one
in the current format to a new file (it refuses to overwrite an existing
one). `--kind` selects what the input is: `config` (the backlog-ops file),
`input` or `output` (a stand-alone preset).

- **CLI:** `python3 -m backlogops_cli.migrate_cfg -i old.cfg -o new.cfg -k config`
- **GUI:** *Configuration → Migrate IO preset file…* (for preset files)

---

[Contents](README.md) | Next: [The backlog and a demo](02_backlog_basics.md) →
