#! /usr/local/bin/python3
"""Tests for applying format rules to backlog and release rows."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from typing import Optional
import pytest
from tableio import Color, Fmt, ValueFmt
from backlogops import (
    BacklogItem, FormatRules, Release, Status, format_backlog,
    format_releases)


def _make_item(est: Optional[date], plan: Optional[date],
               status: Status = Status.TODO) -> BacklogItem:
    """Return a one-field backlog item with the given dates and status."""
    return BacklogItem(key='A1', level=1, title='T', story_points=1,
                       status=status, estimated_ready_date=est,
                       planned_ready_date=plan)


@pytest.mark.parametrize('est,plan,attr', [
    (date(2026, 7, 2), date(2026, 7, 1), 'estimate_late'),
    (date(2026, 6, 30), date(2026, 7, 1), 'estimate_early'),
    (date(2026, 7, 1), date(2026, 7, 1), 'estimate_eq_planned'),
    (None, date(2026, 7, 1), None),
    (date(2026, 7, 1), None, None)])
def test_estimate(est: Optional[date], plan: Optional[date],
                  attr: Optional[str]) -> None:
    """Test the estimate cell uses the format for its planned relation."""
    rules = FormatRules(estimate_late=Fmt(bold=True),
                        estimate_early=Fmt(italic=True),
                        estimate_eq_planned=Fmt(highlight=Color.YELLOW))
    row = format_backlog([_make_item(est, plan)], rules)[0]
    expected = getattr(rules, attr) if attr is not None else Fmt()
    assert row['estimated_ready_date'].fmt == expected


def test_status_fmt() -> None:
    """Test the status cell is formatted by its status and keeps its value."""
    rules = FormatRules()
    row = format_backlog([_make_item(None, None, Status.DONE)], rules)[0]
    assert row['status'].fmt == rules.get_status_format(Status.DONE)
    assert row['status'].value == 'DONE'


def test_other_plain() -> None:
    """Test cells other than status and estimate are left unformatted."""
    row = format_backlog([_make_item(None, None, Status.DONE)],
                         FormatRules())[0]
    assert row['title'] == ValueFmt(value='T', fmt=Fmt())


def test_extra_plain() -> None:
    """Test an extra field becomes a plain formatted cell."""
    item = _make_item(None, None)
    item.extra_fields['note'] = 'hi'
    row = format_backlog([item], FormatRules())[0]
    assert row['note'] == ValueFmt(value='hi', fmt=Fmt())


def test_plain_when_off() -> None:
    """Test every cell is plain once cell formatting is turned off."""
    rules = FormatRules()
    rules.turn_off_cell_format()
    item = _make_item(date(2026, 7, 2), date(2026, 7, 1), Status.DONE)
    row = format_backlog([item], rules)[0]
    assert all(cell.fmt == Fmt() for cell in row.values())


def test_release_fmt() -> None:
    """Test a release estimate is formatted while other cells stay plain."""
    rules = FormatRules(estimate_late=Fmt(bold=True))
    rel = Release(name='R1', planned_date=date(2026, 7, 1),
                  estimated_date=date(2026, 7, 2))
    row = format_releases([rel], rules)[0]
    assert row['estimated_date'].fmt == Fmt(bold=True)
    assert row['name'] == ValueFmt(value='R1', fmt=Fmt())
    assert row['planned_date'].value == '2026-07-01'
