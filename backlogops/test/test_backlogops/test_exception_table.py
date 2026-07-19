#! /usr/local/bin/python3
"""Tests for the company work-hour exception table helpers.

The focused tests check the yes/no cell parser, the per-cell early
feedback and the whole-table parser of the variable-row exception table
used for the company holiday, closure and special-work periods.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from typing import Optional
import pytest
from backlogops.wizard_helpers import _exc_check, _parse_exceptions, \
    _parse_yes_no


@pytest.mark.parametrize('text, expected', [
    (None, False), ('', False), ('no', False), (' N ', False),
    ('false', False), ('0', False), ('yes', True), ('Y', True),
    ('true', True), ('1', True), ('maybe', None)])
def test_parse_yes_no(text: Optional[str], expected: Optional[bool]) -> None:
    """Test yes/no cells parse to a boolean, blank as no, else None."""
    assert _parse_yes_no(text) is expected


@pytest.mark.parametrize('table, pos, ok', [
    ([['2026-01-01', '', '', 'no']], (0, 0), True),
    ([['bad', '', '', 'no']], (0, 0), False),
    ([['', '', '', 'no']], (0, 1), True),
    ([['', '', '5', 'no']], (0, 2), True),
    ([['', '', 'x', 'no']], (0, 2), False),
    ([['', '', '', 'yes']], (0, 3), True),
    ([['', '', '', 'maybe']], (0, 3), False)])
def test_exc_check(table: list[list[Optional[str]]], pos: tuple[int, int],
                   ok: bool) -> None:
    """Test a work-hour exception cell is flagged only when it is bad."""
    assert _exc_check(table, pos)[0] is ok


def test_parse_exc_ok() -> None:
    """Test a full exception row parses, with blank hours meaning zero."""
    table: list[list[Optional[str]]] = [['2026-01-01', '2026-01-05', '',
                                         'yes']]
    result = _parse_exceptions(table)
    assert result is not None
    assert result[0].start_date == date(2026, 1, 1)
    assert result[0].hours_per_day == 0.0
    assert result[0].new_work_days is True


def test_parse_exc_skip() -> None:
    """Test a row with both dates blank is treated as unused and skipped."""
    assert _parse_exceptions([[None, None, '3', 'no']]) == []


@pytest.mark.parametrize('table', [
    [['2026-01-06', '2026-01-05', '', 'no']],
    [['bad', '2026-01-05', '', 'no']],
    [['2026-01-01', '2026-01-05', 'x', 'no']],
    [['2026-01-01', '2026-01-05', '', 'maybe']],
    [['2026-01-01', '', '', 'no']]])
def test_parse_exc_bad(table: list[list[Optional[str]]]) -> None:
    """Test a bad order, date, hours, flag or missing end rejects the table."""
    assert _parse_exceptions(table) is None
