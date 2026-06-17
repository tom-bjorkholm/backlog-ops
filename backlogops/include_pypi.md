## Library main entry points

All names an application programmer is most likely to need are
re-exported from the top-level `backlogops` package, so they can be
imported directly, for example:

````python
from backlogops import (
    read_backlog_releases, order_by_dependencies, estimate_ready_date,
    get_demo_backlog)
````

### Core data model

- `Backlog`, `BacklogItem`, `Status`: the backlog and its items.

- `Releases`, `Release`: the planned releases.

- `BacklogReleases`: a backlog together with its releases.

- `AvailableTeams`, `Team`, `Person`, `Membership`: the workforce that
  the date estimation uses.

### Reading and writing

- `read_backlog_releases`, `write_backlog_releases`: read and write a
  backlog and its releases from and to a table file.

- `read_available_teams`, `write_available_teams`: read and write the
  available-teams configuration.

- `read_key_list`, `write_key_list`: read and write a list of keys.

- `get_demo_backlog`: create a demonstration backlog and releases.

### Operations

- `order_by_dependencies`: reorder the backlog so that dependencies are
  satisfied.

- `move_keys_first`: reorder so that listed keys (and their parents)
  come first.

- `estimate_ready_date`, `set_plan_from_estimate`: estimate ready dates
  and set planned dates from the estimate.

- `estimate_release_dates`, `release_plan_on_estimate`,
  `adjust_release_content`: estimate and plan release dates, and adjust
  release content to fit the planned dates.

- `check_backlog_consistency`: validate the backlog and releases for
  consistency.

For the full set of public names see the API documentation linked above.
