#! /usr/local/bin/python3
"""Test data shared between the backlogops and backlogops_cli tests.

The CLI tests reuse a few fixtures first written for the library tests: an
over-allocated workforce, the input and output preset writers, and a
configuration with every member populated, which is what the tests of the
configuration editor and of its descriptions need. Keeping them here lets
both test packages share one copy instead of duplicating them across the
package boundary.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from pathlib import Path
from backlogops import (
    AvailableTeams, BacklogOpsConfig, ExceptionWorkHours, FteException,
    InputFormatConfig, JiraAttrPath, JiraAttrType, JiraConnectConfig,
    JiraPreset, Level, LevelDisplay, Membership, OutputFormatConfig, Person,
    Status, Team, write_backlog_ops_config)
from backlogops.no_text_io import NoTextIO


def overallocated_teams() -> AvailableTeams:
    """Return a workforce where Ada is booked on two teams beyond capacity."""
    persons = {'ada': Person(name='Ada')}
    first = Team(name='A', velocity=1.0, sum_fte_at_velocity=1.0,
                 sprint_length=10, members=[Membership(person_name='Ada')])
    second = Team(name='B', velocity=1.0, sum_fte_at_velocity=1.0,
                  sprint_length=10,
                  members=[Membership(person_name='Ada', fte=0.5)])
    return AvailableTeams(persons=persons, teams=[first, second])


def write_input_preset(path: Path) -> None:
    """Write an input preset whose backlog map renames one column."""
    config = InputFormatConfig(stderr_file=NoTextIO())
    config.backlog_to_internal = {'Type': 'level'}
    config.write(to_json_filename=path, stderr_file=NoTextIO())


def write_output_preset(path: Path) -> None:
    """Write an output preset with the numeric level display."""
    config = OutputFormatConfig(stderr_file=NoTextIO())
    config.level_display = LevelDisplay.NUMERIC
    config.write(to_json_filename=path, stderr_file=NoTextIO())


def full_workforce() -> AvailableTeams:
    """Return a workforce where every member of every part is populated."""
    closed = ExceptionWorkHours(start_date=date(2026, 1, 1),
                                end_date=date(2026, 1, 2), hours_per_day=0.0)
    person = Person(name='Ada', exceptions=[closed])
    learning = FteException(start_date=date(2026, 2, 1),
                            end_date=date(2026, 2, 28), fte=0.5)
    member = Membership(person_name='Ada', fte_exceptions=[learning],
                        start_date=date(2026, 1, 1),
                        end_date=date(2026, 12, 31))
    team = Team(name='Blue', velocity=10.0, sum_fte_at_velocity=1.0,
                sprint_length=10, aliases=['Bla'], members=[member])
    teams = AvailableTeams(persons={'ada': person}, teams=[team])
    teams.company_work_hours.exceptions = [closed]
    return teams


def _full_input() -> InputFormatConfig:
    """Return an input preset with every map populated."""
    config = InputFormatConfig(stderr_file=NoTextIO())
    config.backlog_to_internal = {'Key': 'key'}
    config.release_to_internal = {'Name': 'name'}
    config.status_input_map = {'Klar': Status.DONE}
    return config


def _full_output() -> OutputFormatConfig:
    """Return an output preset with every map populated."""
    config = OutputFormatConfig(stderr_file=NoTextIO())
    config.backlog_to_external = {'key': 'Key'}
    config.release_to_external = {'name': 'Name'}
    return config


def _full_jira(config: BacklogOpsConfig) -> None:
    """Populate every part of the Jira configuration of ``config``."""
    jira = config.jira
    connection = JiraConnectConfig(stderr_file=NoTextIO())
    connection.base_url = 'https://example.atlassian.net'
    connection.login_email = 'ada@example.com'
    connection.token_file_path = 'token.txt'
    connection.stored_token = 'stored'
    jira.connections = {'cloud': connection}
    path = JiraAttrPath(JiraAttrType.ATTRIBUTE, ('key',))
    jira.backlog_column_maps = {'std': {'key': (path,)}}
    jira.release_column_maps = {'std': {'name': (path,)}}
    jira.issue_type_maps = {'swedish': {0: 'Deluppgift'}}
    preset = JiraPreset(stderr_file=NoTextIO())
    preset.connection_name = 'cloud'
    preset.backlog_column_map_name = 'std'
    preset.release_column_map_name = 'std'
    preset.def_project = 'ABC'
    preset.def_filter = 'project = "ABC" ORDER BY rank ASC'
    jira.presets = {'main': preset}


def full_config() -> BacklogOpsConfig:
    """Return a configuration where every declared member holds a value.

    The editor shows no row for a member a file leaves out, so a test of
    what the editor shows needs a configuration that leaves nothing out.
    """
    config = BacklogOpsConfig(available_teams=full_workforce(),
                              stderr_file=NoTextIO())
    config.levels = [Level(level=1, name='Story', aliases=['Task'])]
    config.input_configs = {'excel': _full_input()}
    config.output_configs = {'excel': _full_output()}
    config.gui_display.backlog_to_external = {'key': 'Key'}
    config.gui_display.release_to_external = {'name': 'Name'}
    _full_jira(config)
    return config


def write_full_config(path: Path) -> None:
    """Write a configuration where every declared member holds a value."""
    write_backlog_ops_config(full_config(), path, NoTextIO())
