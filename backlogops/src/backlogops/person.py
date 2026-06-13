#! /usr/local/bin/python3
"""Define a person including any exceptions in work hours."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass, field
from backlogops.work_hours import ExceptionWorkHours


@dataclass
class Person:
    """Define a person including any exceptions in work hours."""

    name: str
    """The name of the person."""

    exceptions: list[ExceptionWorkHours] = field(default_factory=list)
    """Any exceptions in work hours for the person.

    These exceptions are used to mark personal vacation days,
    and other planned days off. They can also mark any period
    of time the person has other work hours, for instance periods
    of part-time work or ordered over-time work.
    """
