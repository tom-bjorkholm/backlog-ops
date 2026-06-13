#! /usr/local/bin/python3
"""Define available teams to do work."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass
from typing import TextIO
import sys
from backlogops.team import Team
from backlogops.work_hours import CompanyWorkHours, DEFAULT_WORK_HOURS


@dataclass
class AvailableTeam:
    """Define an available team."""

    teams: list[Team]
    """The list of teams that are available to do work."""

    company_work_hours: CompanyWorkHours = DEFAULT_WORK_HOURS
    """The company work hours."""

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the consistency of the available teams."""
        # to be implemented
