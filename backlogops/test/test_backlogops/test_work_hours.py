#! /usr/local/bin/python3
"""Tests for work hours schedules and exceptions."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from io import StringIO

import pytest

from backlogops.work_hours import CompanyWorkHours, DEFAULT_WORK_WEEK
from backlogops.work_hours import ExceptionWorkHours, WeekDay
from backlogops.no_text_io import NoTextIO


def _exception(hours: float = 0.0) -> ExceptionWorkHours:
    """Return a one day exception with the given hours per day."""
    return ExceptionWorkHours(start_date=date(2026, 12, 24),
                              end_date=date(2026, 12, 24), hours_per_day=hours)


def test_exception_ok() -> None:
    """Test a valid exception passes its consistency check."""
    _exception(4.0).check_consistency(NoTextIO())


def test_exception_bad_range() -> None:
    """Test an exception with start after end is a ValueError."""
    exception = ExceptionWorkHours(start_date=date(2026, 12, 26),
                                   end_date=date(2026, 12, 24),
                                   hours_per_day=0.0)
    with pytest.raises(ValueError):
        exception.check_consistency(NoTextIO())


def test_exc_neg_hours() -> None:
    """Test a negative hours per day is a ValueError."""
    with pytest.raises(ValueError):
        _exception(-1.0).check_consistency(NoTextIO())


def test_exc_message() -> None:
    """Test a bad exception range names the work hours exception."""
    err = StringIO()
    exception = ExceptionWorkHours(start_date=date(2026, 12, 26),
                                   end_date=date(2026, 12, 24),
                                   hours_per_day=0.0)
    with pytest.raises(ValueError):
        exception.check_consistency(err)
    message = err.getvalue()
    assert message.startswith("Work hours exception field 'exception'")
    assert 'Backlog item' not in message
    assert 'start_date is after end_date' in message


def test_exception_bad_type() -> None:
    """Test a non-date start date is reported as a TypeError."""
    exception = _exception()
    exception.start_date = '2026-12-24'  # type: ignore[assignment]
    with pytest.raises(TypeError):
        exception.check_consistency(NoTextIO())


def test_company_default_ok() -> None:
    """Test the default company work hours are consistent."""
    CompanyWorkHours().check_consistency(NoTextIO())


def test_default_not_shared() -> None:
    """Test two default instances do not share the same mutable state."""
    first = CompanyWorkHours()
    second = CompanyWorkHours()
    first.exceptions.append(_exception())
    first.work_hours[WeekDay.MONDAY] = 1.0
    assert not second.exceptions
    assert second.work_hours[WeekDay.MONDAY] == DEFAULT_WORK_WEEK[
        WeekDay.MONDAY]


def test_missing_week_day() -> None:
    """Test a schedule missing a week day is a ValueError."""
    schedule = dict(DEFAULT_WORK_WEEK)
    del schedule[WeekDay.SUNDAY]
    with pytest.raises(ValueError):
        CompanyWorkHours(work_hours=schedule).check_consistency(NoTextIO())


def test_company_neg_hours() -> None:
    """Test a negative scheduled work hours is a ValueError."""
    schedule = dict(DEFAULT_WORK_WEEK)
    schedule[WeekDay.MONDAY] = -1.0
    with pytest.raises(ValueError):
        CompanyWorkHours(work_hours=schedule).check_consistency(NoTextIO())


def test_company_exc_overlap() -> None:
    """Test two overlapping company exceptions are a ValueError."""
    first = ExceptionWorkHours(start_date=date(2026, 12, 24),
                               end_date=date(2026, 12, 31), hours_per_day=0.0)
    second = ExceptionWorkHours(start_date=date(2026, 12, 31),
                                end_date=date(2027, 1, 1), hours_per_day=0.0)
    company = CompanyWorkHours(exceptions=[first, second])
    with pytest.raises(ValueError):
        company.check_consistency(NoTextIO())
