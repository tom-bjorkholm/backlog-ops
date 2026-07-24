#! /usr/local/bin/python3
"""Test data shared between the backlogops and backlogops_cli tests.

The CLI tests reuse a couple of fixtures first written for the library
tests: an over-allocated workforce and the input and output preset
writers. Keeping them here lets both test packages share one copy instead
of duplicating them across the package boundary.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from backlogops import (
    AvailableTeams, InputFormatConfig, LevelDisplay, Membership,
    OutputFormatConfig, Person, Team)
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
