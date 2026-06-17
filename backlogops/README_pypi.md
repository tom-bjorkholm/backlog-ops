# backlogops

There are 3 related packages for backlog operations:

- backlogops: a collection of library functions to manipulate backlogs

- backlogops-cli: command line interface to use the functions in the library.
  This is just a thin wrapper around the library functions. It serves a dual
  purpose as both an example of how to use the library and as a tool for the
  user to use the library.

- backlogops-gui: graphical user interface to use the functions in the library.
  It is based on TkInter. The ambition is to keep it as a thin wrapper around
  the library.

## Available functionality

The following functionality is available in all 3 packages:

- Reading backlog and releases from file types that TableIO supports reading
  from (Currently CSV, Excel, and ODS).

- Writing backlog and releases to file types that TableIO supports writing to
  (Currently CSV, Excel, ODS and 9 other file formats).

- File format is detected from the file extension, but may be overridden.

- Adjust release content to fit the planned release dates.

- Create a demonstration backlog and releases (for exploring the features).

- Estimate ready date for the backlog items based on available teams, team
  velocity, vacation dates, periods with half time work, etc.

- Extract backlog keys at given backlog item levels.

- Reorder the backlog so that the dependencies are satisfied.

- Reorder the backlog so that items identified by keys in a list come first. If
  the key is at a higher level it will bring all items it is a parent of in
  front of it (recursively).

- Set planned release dates from the estimated release dates.

- Calculate the release dates from the backlog items estimated ready dates, with
  a configurable buffer time.

- Validate the backlog and releases for consistency.

- A wizard to create an available teams configuration.

## The operating model

The operating model that most of the functionality is designed for is that the
teams work off a single backlog in the order of the backlog. The backlog items
are ordered by priority and dependencies to allow the teams to work in the
backlog order. Each backlog item and each release may have a planned ready date,
that records what has been communicated to the customer. Each backlog item and
each release may have an estimated ready date, that is calculated from the
current backlog state, the team velocity, and what we know about the
availability of the team members.

## The backlog item fields

Each backlog item has the following fields that are used by the algorithms in
the library:

- key: The key of the backlog item. Required. Must be unique. Must not be empty,
  must not contain whitespace and must not contain any of the characters , . ; :
  ( ) \[ \] \{ \}.

- level: The level of the backlog item. Required. Must be an integer.

- title: The title of the backlog item. Required.

- story_points: The story points of the backlog item. Required.

- status: The status of the backlog item. Required.

- parent_key: The key of the parent backlog item. Optional. Must exist as a key
  in the backlog. Parent keys are used to build the hierarchy of the backlog.
  The parent key must be at a higher level than the current item. Parent keys
  introduce implicit dependencies between items: the current item cannot start
  before the parent item starts, and the parent item cannot finish before all
  its children have finished.

- release: The release of the backlog item. Optional. Follows the same character
  rules as the key. Must not be empty string.

- team: The team responsible for the backlog item. Optional. Must not be empty
  string. Must be a valid team name. If None the item can be done by any team.
  If not None. the item can only be done by the specified team.

- depends_on_f2s: The list of keys of the backlog items that must have been
  finished before the current item can start. May be empty.

- depends_on_f2f: The list of keys of the backlog items that must have been
  finished before the current item can finish. May be empty.

- depends_on_s2s: The list of keys of the backlog items that must have been
  started before the current item can start. May be empty.

- planned_ready_date: The planned ready date of the backlog item. The date that
  is communicated to the customer. Optional.

- estimated_ready_date: The estimated ready date of the backlog item. Optional.

Additionally each backlog item can have any number of other fields.

## Installing backlogops

### On macOS and Linux

To install backlogops on macOS and Linux, run the following command:

````sh
pip3 install --upgrade backlogops
````

### On Microsoft Windows

To install backlogops on Microsoft Windows, run the following command:

````sh
pip install --upgrade backlogops
````

## API documentation

For more detailed code documentation, see the API documentation:

- [Library public API](https://bitbucket.org/tom-bjorkholm/backlog-ops/src/master/doc/backlogops_api.md)

- [Library protected API](https://bitbucket.org/tom-bjorkholm/backlog-ops/src/master/doc/backlogops_protected_api.md)

- [Library public CLI](https://bitbucket.org/tom-bjorkholm/backlog-ops/src/master/doc/backlogops_cli.md)

- [Library protected CLI](https://bitbucket.org/tom-bjorkholm/backlog-ops/src/master/doc/backlogops_protected_cli.md)

- [Library public GUI](https://bitbucket.org/tom-bjorkholm/backlog-ops/src/master/doc/backlogops_gui.md)

- [Library protected GUI](https://bitbucket.org/tom-bjorkholm/backlog-ops/src/master/doc/backlogops_protected_gui.md)

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

- `move_keys_first`: reorder so that listed keys (and their children)
  come first.

- `estimate_ready_date`, `set_plan_from_estimate`: estimate ready dates
  and set planned dates from the estimate.

- `estimate_release_dates`, `release_plan_on_estimate`,
  `adjust_release_content`: estimate and plan release dates, and adjust
  release content to fit the planned dates.

- `check_backlog_consistency`: validate the backlog and releases for
  consistency.

For the full set of public names see the API documentation linked above.

## Test summary

- Test result: 1066 passed in 28s
- No flake8 warnings.
- No mypy errors found.
- No python layout warnings.
- Built version(s): 0.1
- Build and test using Python 3.13.7
