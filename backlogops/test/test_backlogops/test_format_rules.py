#! /usr/local/bin/python3
"""Tests for the FormatRules dataclass and its defaults."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from tableio import Color, Fmt
from backlogops import FormatRules, Status
from backlogops.format_rules import default_status_format


def test_defaults() -> None:
    """Test the default rules bold the header and color done and rejected."""
    rules = FormatRules()
    assert rules.backlog_first is True
    assert rules.filtered_data_range is True
    assert rules.first_row_format == Fmt(bold=True)
    assert rules.get_status_format(Status.DONE).highlight == Color.GREEN
    assert rules.get_status_format(Status.REJECTED).highlight == Color.RED
    assert rules.get_status_format(Status.TODO) == Fmt()


def test_status_default_map() -> None:
    """Test the default status map has an entry for every status value."""
    assert set(default_status_format()) == set(Status)


def test_get_unknown_status() -> None:
    """Test a status missing from the map gets the plain format."""
    rules = FormatRules(status_format={})
    assert rules.get_status_format(Status.DONE) == Fmt()


def test_independent_maps() -> None:
    """Test two rule objects do not share one status map."""
    first = FormatRules()
    second = FormatRules()
    first.status_format[Status.TODO] = Fmt(bold=True)
    assert second.status_format[Status.TODO] == Fmt()


def test_cell_format_used() -> None:
    """Test cell formatting is reported as used for the defaults."""
    assert FormatRules().cell_format_used() is True


def test_turn_off_format() -> None:
    """Test turning off cell formatting clears every cell format."""
    rules = FormatRules()
    rules.turn_off_cell_format()
    assert rules.cell_format_used() is False
    assert rules.first_row_format == Fmt()
    assert all(fmt == Fmt() for fmt in rules.status_format.values())


def test_off_keeps_layout() -> None:
    """Test turning off cell formatting keeps borders and filter range."""
    rules = FormatRules()
    border = rules.border_style
    rules.turn_off_cell_format()
    assert rules.border_style == border
    assert rules.filtered_data_range is True
