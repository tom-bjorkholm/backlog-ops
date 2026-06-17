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

    - Read backlog...: Read in a file with a backlog and list of releases.
      A new backlog window will be opened with the read in backlog.

    - New demo backlog: Create a demo backlog with some backlog items and
      releases. A new backlog window will be opened with the demo backlog.

- Configuration

    - Run teams wizard...: this lets you configure the teams that work on
      the backlog and also other aspects like the dates the company is
      closed for vacation, and preset configuration for the inputs or
      outputs you want to use.

    - Write configuration...: This lets you write the configuration you
      have in application to a file.

## Backlog window

The backlog window shows 2 read-only tables: one with the backlog and
one with the list of releases. You will want to use the menus.

- Backlog

    - Order by keys...

    - Order by dependencies...

    - Estimate ready date...

    - Set planned date from estimated

    - Adjust release content

    - Adjust planned release dates...

    - Extract keys...

    - Save to file...

    - Close
