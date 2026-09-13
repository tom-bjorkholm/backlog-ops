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

At first startup you do not have any configuration file yet, so the
application shows a *No configuration* dialog offering to run the
configuration wizard, load an existing configuration file, or exit.
Cancelling the wizard or the file chooser returns to that dialog, so
the application starts only once a configuration is in place.

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

    - Edit configuration...: Show the whole configuration in a folding,
      searchable editor, so you can change one value without stepping
      through the wizard. It asks whether to edit the configuration the
      application is using or one in a file you pick. A preset, a Jira
      connection, a person, a team, a level and an entry of any of the maps
      can be added beside the ones that are there, taken out again, and
      moved within a list. Saving validates the configuration first, keeps
      what it writes over as a `.bak` file, and makes what it wrote the
      configuration in use.

    - Create IO preset file...: Create a stand-alone input or output preset
      configuration file via a wizard.

    - Edit IO preset file...: Show a stand-alone input or output preset file
      in the same folding editor. Whether the file is an input or an output
      preset is detected from the file itself.

    - Migrate IO preset file...: Migrate an older input or output preset
      file to the current file format.

    - Write configuration...: This lets you write the configuration you
      have in application to a file.

    - Encrypt Jira API token file...: Encrypt a Jira API token to a
      pass-phrase-protected file, for use with the ENCRYPTED_FILE token
      storage mode.

- Help

    - Report version information: Show version information for the
      application and its dependencies.

## Backlog window

The backlog window shows 2 read-only tables: one with the backlog and
one with the list of releases. You will want to use the menus.

At the top of the window an information region records where the data
came from and when it was read, marks the window once you change the
backlog, and offers a **Read again** button that re-reads the same
source (the same file, or the same Jira preset and filter) in place. A
re-read with unsaved changes asks for confirmation first.

Each Jira action answers in a copy-pasteable pop-up that leads with what
did not happen: what Jira refused, then what was skipped, and last what
succeeded. When something was refused the pop-up title is marked
*NOT ALL SUCCEEDED*, so it is visible even behind another window.

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
