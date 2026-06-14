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
  python3 -m backlogops_cli.list
     List all commands available in backlogops_cli
  python3 -m backlogops_cli.teams_wizard
     Create an AvailableTeams configuration file via a wizard
````

## Test summary

- Test result: 479 passed in 7s
- No flake8 warnings.
- No mypy errors found.
- No python layout warnings.
- Built version(s): 0.0.1
- Build and test using Python 3.14.5
