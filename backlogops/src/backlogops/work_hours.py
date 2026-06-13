#! /usr/local/bin/python3
"""Work hours schedule and exceptions."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass, field
from enum import IntEnum, auto
from datetime import date


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
        start_date: The start date of the exception.
        end_date: The end date of the exception.
        hours_per_day: The work hours per day during the exception.
        new_work_days: If True, the exception adds new work days compared
                       to the schedule. That is the hours per day also
                       applies to days with no work hours in the schedule.
                       If False, the exception does not add new work days.
                       That is the hours per day only applies to days with
                       work hours in the schedule.
                       If an individual employee has an exception to work
                       during days the company is closed, the new_work_days
                       flag must be True.
    """

    start_date: date
    end_date: date
    hours_per_day: float
    new_work_days: bool = False


@dataclass
class CompanyWorkHours:
    """Company work hours.

    The company work hours are used to define the work hours for a company.

    Fields:
        work_hours: The work hours schedule for the company.
        exceptions: The list of exception work hours for the company.
                    This should list national holidays and other days with
                    different work hours. This should also include any
                    the company is closed for any reason (such as vacations).
    """

    work_hours: ScheduleWorkHours = DEFAULT_WORK_WEEK
    exceptions: list[ExceptionWorkHours] = field(default_factory=list)


CHRISTMAS_EXCEPTION: ExceptionWorkHours = \
    ExceptionWorkHours(start_date=date(date.today().year, month=12, day=24),
                       end_date=date(date.today().year+1, month=1, day=1),
                       hours_per_day=0.0, new_work_days=False)

DEFAULT_WORK_HOURS: CompanyWorkHours = \
    CompanyWorkHours(work_hours=DEFAULT_WORK_WEEK,
                     exceptions=[CHRISTMAS_EXCEPTION])
