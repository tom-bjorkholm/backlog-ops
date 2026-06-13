#! /usr/local/bin/python3
"""Helpers for validating inclusive date ranges."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from datetime import date
from typing import TextIO
from backlogops.backlog_helpers import report_bad_value


def check_date_range(field_name: str, start: date, end: date,
                     stderr_file: TextIO = sys.stderr,
                     subject: str = 'Backlog item') -> None:
    """Check that an inclusive date range is not empty.

    The range covers every day from ``start`` to ``end`` inclusive, so
    ``start`` must not be after ``end``.

    Args:
        field_name: The name of the field that holds the range.
        start: The first day of the range.
        end: The last day of the range.
        stderr_file: The file to report errors to.
        subject: What owns the field, used to start error messages.

    Raises:
        ValueError: If ``start`` is after ``end``.
    """
    if start > end:
        report_bad_value(field_name, (start, end),
                         'start_date is after end_date', stderr_file, subject)


def check_no_overlap(field_name: str, ranges: list[tuple[date, date]],
                     stderr_file: TextIO = sys.stderr,
                     subject: str = 'Backlog item') -> None:
    """Check that inclusive date ranges do not share a day.

    Each range must already be valid (start not after end). The ranges
    are sorted by start day and each is compared with the next, so an
    overlap is found in a single pass.

    Args:
        field_name: The name of the field that holds the ranges.
        ranges: The inclusive ``(start, end)`` ranges to check.
        stderr_file: The file to report errors to.
        subject: What owns the field, used to start error messages.

    Raises:
        ValueError: If two ranges share a day.
    """
    ordered = sorted(ranges)
    for earlier, later in zip(ordered, ordered[1:]):
        if later[0] <= earlier[1]:
            report_bad_value(field_name, later,
                             'overlaps an earlier date range', stderr_file,
                             subject)
