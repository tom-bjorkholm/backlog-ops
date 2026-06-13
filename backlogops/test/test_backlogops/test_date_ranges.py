#! /usr/local/bin/python3
"""Tests for inclusive date range helpers."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from io import StringIO

import pytest

from backlogops.date_ranges import check_date_range, check_no_overlap
from backlogops.no_text_io import NoTextIO


def test_range_ok() -> None:
    """Test a non-empty range with start before end passes."""
    check_date_range('r', date(2026, 1, 1), date(2026, 1, 31), NoTextIO())


def test_range_one_day() -> None:
    """Test a range that starts and ends on the same day passes."""
    check_date_range('r', date(2026, 1, 1), date(2026, 1, 1), NoTextIO())


def test_range_reversed() -> None:
    """Test a range with start after end is reported as a ValueError."""
    with pytest.raises(ValueError):
        check_date_range('r', date(2026, 2, 1), date(2026, 1, 1), NoTextIO())


def test_no_overlap_ok() -> None:
    """Test ranges that do not share a day pass the overlap check."""
    ranges = [(date(2026, 1, 1), date(2026, 1, 10)),
              (date(2026, 1, 11), date(2026, 1, 20))]
    check_no_overlap('r', ranges, NoTextIO())


def test_no_overlap_empty() -> None:
    """Test an empty list of ranges passes the overlap check."""
    check_no_overlap('r', [], NoTextIO())


def test_overlap_shared_day() -> None:
    """Test ranges sharing the boundary day are reported."""
    ranges = [(date(2026, 1, 1), date(2026, 1, 10)),
              (date(2026, 1, 10), date(2026, 1, 20))]
    with pytest.raises(ValueError):
        check_no_overlap('r', ranges, NoTextIO())


def test_range_subject() -> None:
    """Test the subject starts the range error message."""
    err = StringIO()
    with pytest.raises(ValueError):
        check_date_range('r', date(2026, 2, 1), date(2026, 1, 1), err, 'Team')
    message = err.getvalue()
    assert message.startswith("Team field 'r'")
    assert 'start_date is after end_date' in message


def test_overlap_unordered() -> None:
    """Test overlap is found regardless of the order of the ranges."""
    ranges = [(date(2026, 2, 1), date(2026, 2, 20)),
              (date(2026, 1, 1), date(2026, 2, 5))]
    with pytest.raises(ValueError):
        check_no_overlap('r', ranges, NoTextIO())
