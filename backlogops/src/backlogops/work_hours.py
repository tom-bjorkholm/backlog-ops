#! /usr/local/bin/python3
"""Work hours schedule and exceptions."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from dataclasses import dataclass, field
from enum import IntEnum, auto
from datetime import date
from typing import TextIO
from backlogops.backlog_helpers import check_field_types, report_bad_value
from backlogops.date_ranges import check_date_range, check_no_overlap


class WeekDay(IntEnum):
    """Week day."""

    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()
    SATURDAY = auto()
    SUNDAY = auto()


type ScheduleWorkHours = dict[WeekDay, float]
"""Work hours schedule by week day."""

DEFAULT_WORK_WEEK: ScheduleWorkHours = {
    WeekDay.MONDAY: 8.0,
    WeekDay.TUESDAY: 8.0,
    WeekDay.WEDNESDAY: 8.0,
    WeekDay.THURSDAY: 8.0,
    WeekDay.FRIDAY: 8.0,
    WeekDay.SATURDAY: 0.0,
    WeekDay.SUNDAY: 0.0,
}
"""The default work week."""


@dataclass
class ExceptionWorkHours:
    """Exception work hours for a specific period.

    The exception work hours are used to override the default work hours
    for a specific period. This can be used to mark holidays or other days
    with different work hours. It can also be used to mark a period with
    ordered over-time work.
    When used for an individual employee, the company exceptions are seen
    as part of the schedule.

    Fields:
        start_date: The first day of the exception (inclusive).
        end_date: The last day of the exception (inclusive). Must not be
                  before start_date.
        hours_per_day: The work hours per day during the exception. Must
                       not be negative.
        new_work_days: If True, the exception adds new work days compared
                       to the schedule. That is the hours per day also
                       applies to days with no work hours in the schedule.
                       If False, the exception does not add new work days.
                       That is the hours per day only applies to days with
                       work hours in the schedule.
                       If an individual employee has an exception to work
                       during days the company is closed, the new_work_days
                       flag must be True.

    Exceptions in one list (a company or a person) must not overlap, so
    that the work hours of any day are defined by at most one exception.
    """

    start_date: date
    end_date: date
    hours_per_day: float
    new_work_days: bool = False

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the consistency of the exception work hours.

        Field types are verified, the date range must be non-empty, and
        the work hours per day must not be negative.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If the range is empty or the hours are negative.
        """
        check_field_types(self, stderr_file, 'Work hours exception')
        check_date_range('exception', self.start_date, self.end_date,
                         stderr_file, 'Work hours exception')
        if self.hours_per_day < 0.0:
            report_bad_value('hours_per_day', self.hours_per_day,
                             'must not be negative', stderr_file,
                             'Work hours exception')


@dataclass
class CompanyWorkHours:
    """Company work hours.

    The company work hours are used to define the work hours for a company.

    Fields:
        work_hours: The work hours schedule for the company. Every week
                    day must have non-negative work hours.
        exceptions: The list of exception work hours for the company.
                    This should list national holidays and other days with
                    different work hours. This should also include any days
                    the company is closed for any reason (such as company
                    wide vacations). The exceptions must not overlap.
    """

    work_hours: ScheduleWorkHours = field(
        default_factory=lambda: dict(DEFAULT_WORK_WEEK))
    exceptions: list[ExceptionWorkHours] = field(default_factory=list)

    def _check_schedule(self, stderr_file: TextIO) -> None:
        """Check every week day has non-negative work hours defined."""
        for week_day in WeekDay:
            if week_day not in self.work_hours:
                report_bad_value('work_hours', week_day,
                                 'missing work hours for week day',
                                 stderr_file, 'Company work hours')
            elif self.work_hours[week_day] < 0.0:
                report_bad_value('work_hours', self.work_hours[week_day],
                                 'must not be negative', stderr_file,
                                 'Company work hours')

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the consistency of the company work hours.

        Field types are verified, the schedule must define non-negative
        work hours for every week day, every exception must be consistent,
        and the exceptions must not overlap.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If the schedule or an exception is invalid, or if
                two exceptions overlap.
        """
        check_field_types(self, stderr_file, 'Company work hours')
        self._check_schedule(stderr_file)
        for exception in self.exceptions:
            exception.check_consistency(stderr_file)
        check_no_overlap('exceptions',
                         [(e.start_date, e.end_date)
                          for e in self.exceptions], stderr_file,
                         'Company work hours')
