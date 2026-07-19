# backlogops-gui

There are 3 related packages for backlog operations:

- **[backlogops](https://pypi.org/project/backlogops/)** a collection of library
  functions to manipulate backlogs

- **[backlogops-cli](https://pypi.org/project/backlogops-cli/)** command line
  interface to use the functions in the library. This is just a thin wrapper
  around the library functions. It serves a dual purpose as both an example of
  how to use the library and as a tool for the user to use the library.

- **[backlogops-gui](https://pypi.org/project/backlogops-gui/)** graphical user
  interface to use the functions in the library. It is based on TkInter. The
  ambition is to keep it as a thin wrapper around the library.

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

- Reorder the backlog in release order, optionally taking dependencies into
  account.

- Set planned release dates from the estimated release dates.

- Calculate the release dates from the backlog items estimated ready dates, with
  a configurable buffer time.

- Validate the backlog and releases for consistency.

- Convert a backlog and releases between table file formats.

- Order the releases by their planned or estimated date.

- Rename columns when reading a file and when writing a file.

- Map custom status names in input files to backlog item statuses.

- Choose how backlog item levels are written: by number, by name, or both, and
  configure custom level names.

- Create stand-alone input or output preset configuration files.

- Migrate an older configuration or preset file to the current file format.

- A wizard to create a backlog-ops configuration file with the workforce, named
  input and output presets, level names, and status name mapping.

- Read a backlog and releases from Jira into a backlog and release table.

- Write a backlog to Jira, creating a new Jira issue for each backlog item.

- Update a backlog that is already in Jira, changing only the chosen columns.

- Add the releases to Jira as Jira versions.

- Update the releases in Jira, setting their dates to the planned release dates.

- Order the releases in Jira by date, by a name list, or by the input order.

- Rename releases in Jira, changing the Jira version names.

- Move backlog items to a chosen anchor in the Jira rank order, following a key
  list.

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

- `key` The key of the backlog item. Required. Must be unique. Must not be
  empty, must not contain whitespace and must not contain any of the characters
  , . ; : ( ) \[ \] \{ \}.

- `level` The level of the backlog item. Required. Must be an integer.

- `title` The title of the backlog item. Required.

- `story_points` The story points of the backlog item. Required.

- `status` The status of the backlog item. Required.

- `parent_key` The key of the parent backlog item. Optional. Must exist as a key
  in the backlog. Parent keys are used to build the hierarchy of the backlog.
  The parent key must be at a higher level than the current item. Parent keys
  introduce implicit dependencies between items: the current item cannot start
  before the parent item starts, and the parent item cannot finish before all
  its children have finished.

- `release` The release of the backlog item. Optional. Must not be empty string,
  must not start or end with whitespace, and must not contain tabs, newlines or
  control characters.

- `team` The team responsible for the backlog item. Optional. Must not be empty
  string. Must be a valid team name. If None the item can be done by any team.
  If not None. the item can only be done by the specified team.

- `depends_on_f2s` The list of keys of the backlog items that must have been
  finished before the current item can start. May be empty.

- `depends_on_f2f` The list of keys of the backlog items that must have been
  finished before the current item can finish. May be empty.

- `depends_on_s2s` The list of keys of the backlog items that must have been
  started before the current item can start. May be empty.

- `planned_ready_date` The planned ready date of the backlog item. The date that
  is communicated to the customer. Optional.

- `estimated_ready_date` The estimated ready date of the backlog item. Optional.

Additionally each backlog item can have any number of other fields.

## Installing backlogops-gui

### On macOS and Linux

To install backlogops-gui on macOS and Linux, run the following command:

````sh
pip3 install --upgrade backlogops-gui
````

### On Microsoft Windows

To install backlogops-gui on Microsoft Windows, run the following command:

````sh
pip install --upgrade backlogops-gui
````

## Using backlogops documentation

For a better understanding of how to use the library, CLI or GUI, see the user
documentation:
[Using backlogops](https://github.com/tom-bjorkholm/backlog-ops/blob/master/doc//using_backlogops/README.md)

## API documentation

For more detailed code documentation, see the API documentation:

- [Library public API](https://github.com/tom-bjorkholm/backlog-ops/blob/master/doc/backlogops_api.md)

- [Library protected API](https://github.com/tom-bjorkholm/backlog-ops/blob/master/doc/backlogops_protected_api.md)

- [Public CLI code documentation](https://github.com/tom-bjorkholm/backlog-ops/blob/master/doc/backlogops_cli.md)

- [Protected CLI code documentation](https://github.com/tom-bjorkholm/backlog-ops/blob/master/doc/backlogops_protected_cli.md)

- [Public GUI code documentation](https://github.com/tom-bjorkholm/backlog-ops/blob/master/doc/backlogops_gui.md)

- [Protected GUI code documentation](https://github.com/tom-bjorkholm/backlog-ops/blob/master/doc/backlogops_protected_gui.md)

## Graphical user interface for backlog manipulation

Most of the functionality in the backlogops backlog operations library
is made available for GUI users in this GUI application.

### Tkinter

The Graphical user interface is based on
[Tkinter](https://docs.python.org/3/library/tkinter.html). Tkinter
is based on [Tcl/Tk](https://en.wikipedia.org/wiki/Tk_(software)).

For full functionality you need Tk version 9.0.2 or newer.

## First startup

Start the application on Linux or mac with command
````sh
python3 -m backlogops_gui
python3 -m backlogops_gui -c config_file.cfg
````
or on Microsoft Windows with command
````sh
python -m backlogops_gui
python -m backlogops_gui -c config_file.cfg
````

At first startup you do not have any configuration file yet,
so when you start the application it will start the configuration
wizard.

## Main window

The main window has some informative text, but the functionality
is in the menus.

- File

    - Read backlog from file...: Read in a file with a backlog and list
      of releases. A new backlog window will be opened with the read in
      backlog.

    - Read backlog from Jira...: Read a backlog and list of releases from
      Jira. A new backlog window will be opened with the read in backlog.

    - New demo backlog: Create a demo backlog with some backlog items and
      releases. A new backlog window will be opened with the demo backlog.

    - Exit: Close the application.

- Configuration

    - Load configuration file...: Load a configuration file, replacing the
      configuration currently active in the application.

    - Run configuration wizard...: this lets you configure the teams that work on
      the backlog and also other aspects like the dates the company is
      closed for vacation, and preset configuration for the inputs or
      outputs you want to use.

    - Create IO preset file...: Create a stand-alone input or output preset
      configuration file via a wizard.

    - Migrate IO preset file...: Migrate an older input or output preset
      file to the current file format.

    - Write configuration...: This lets you write the configuration you
      have in application to a file.

- Help

    - Report version information: Show version information for the
      application and its dependencies.

## Backlog window

The backlog window shows 2 read-only tables: one with the backlog and
one with the list of releases. You will want to use the menus.

- Backlog

    - Order by keys...

    - Order by dependencies...

    - Order by release order...

    - Estimate ready date...

    - Set planned date from estimated

    - Adjust release content...

    - Adjust planned release dates...

    - Order releases by date...

    - Extract keys...

    - Save to file...

    - Close

- Jira

    - Add backlog to Jira...

    - Update backlog in Jira...

    - Add releases to Jira...

    - Update releases in Jira...

    - Order releases in Jira...

    - Rename releases in Jira...

    - Rank items in Jira...

## Test summary

- Test result: 2528 passed, 7 deselected in 48s
- No flake8 warnings.
- No mypy errors found.
- No python layout warnings.
- Built version(s): 0.3.1
- Build and test using Python 3.14.6
