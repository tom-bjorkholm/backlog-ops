#! /usr/local/bin/python3
"""Workforce builders shared by the ready date estimate tests."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from typing import Optional
from backlogops import (
    AvailableTeams, CompanyWorkHours, ExceptionWorkHours, Membership, Person,
    Team)

MON = date(2026, 6, 15)
"""A Monday used as the start date in the tests."""


def person(name: str,
           exceptions: Optional[list[ExceptionWorkHours]] = None) -> Person:
    """Build a person, optionally with work-hours exceptions."""
    return Person(name=name, exceptions=exceptions or [])


def member(name: str, fte: float = 1.0) -> Membership:
    """Build a full-membership for a person by name."""
    return Membership(person_name=name, fte=fte)


def workforce(team_list: list[Team], persons: list[Person],
              company: Optional[CompanyWorkHours] = None) -> AvailableTeams:
    """Build the available workforce from teams and persons."""
    registry = {p.name.lower(): p for p in persons}
    if company is None:
        return AvailableTeams(persons=registry, teams=team_list)
    return AvailableTeams(persons=registry, teams=team_list,
                          company_work_hours=company)
