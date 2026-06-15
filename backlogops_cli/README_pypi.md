# backlogops-cli

There are 3 related packages for backlog operations:

- backlogops: a collection of library functions to manipulate backlogs

- backlogops-cli: command line interface to use the functions in the library

- backlogops-gui: graphical user interface to use the functions in the library

## Installing backlogops-cli

### On macOS and Linux

To install backlogops-cli on macOS and Linux, run the following command:

````sh
pip3 install --upgrade backlogops-cli
````

### On Microsoft Windows

To install backlogops-cli on Microsoft Windows, run the following command:

````sh
pip install --upgrade backlogops-cli
````

## Command line backlog operations

backlogops_cli serves 2 purposes:

- as a command line utility collection for manipulating backlogs

- as an example of how to write your own programs that use the backlogops library

### Currently available commands

````text
  python3 -m backlogops_cli.convert
     Convert a backlog and releases between table file formats
  python3 -m backlogops_cli.demo_backlog
     Write a demonstration backlog and releases to a file
  python3 -m backlogops_cli.estimate_ready_date
     Estimate ready dates for the backlog items
  python3 -m backlogops_cli.extract_keys
     Extract backlog keys at the given levels to a key list
  python3 -m backlogops_cli.list
     List all commands available in backlogops_cli
  python3 -m backlogops_cli.order_by_deps
     Reorder a backlog so that dependencies are fulfilled
  python3 -m backlogops_cli.order_by_keys
     Reorder a backlog so that key-list items come first
  python3 -m backlogops_cli.teams_wizard
     Create an AvailableTeams configuration file via a wizard
````

## Test summary

- Test result: 735 passed in 12s
- No flake8 warnings.
- No mypy errors found.
- No python layout warnings.
- Built version(s): 0.0.1
- Build and test using Python 3.14.6
