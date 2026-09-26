#! /usr/local/bin/python3
"""Tests for reading and writing a remaining time as text."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import timedelta
import pytest
from backlogops import format_duration, parse_duration


@pytest.mark.parametrize('text, expected', [
    ('1:30:00', timedelta(hours=1, minutes=30)),
    ('0:00:00', timedelta(0)),
    ('102:30:00', timedelta(hours=102, minutes=30)),
    ('1d', timedelta(hours=24)),
    ('1w', timedelta(days=7)),
    ('1d 1:30:45', timedelta(hours=25, minutes=30, seconds=45)),
    ('1w 1d 2:30:00', timedelta(hours=194, minutes=30)),
    ('2w 3d', timedelta(days=17)),
    ('1w1d', timedelta(days=8)),
    ('  1d   0:00:01  ', timedelta(days=1, seconds=1)),
    ('0d', timedelta(0))])
def test_parse_duration(text: str, expected: timedelta) -> None:
    """Test weeks, days of 24 hours and hours:minutes:seconds are read."""
    assert parse_duration(text) == expected


@pytest.mark.parametrize('text', [
    '', '   ', '1:30', '90', '1h', '1:60:00', '1:00:60', '1:0:00',
    '-1:00:00', '1d 1w', '1:00:00 1d', '1.5d', '1x', 'd', '1D',
    '1d, 1:00:00'])
def test_parse_refused(text: str) -> None:
    """Test a text that is not in the format says no remaining time."""
    assert parse_duration(text) is None


def test_parse_too_large() -> None:
    """Test a time too large for a timedelta says no remaining time."""
    assert parse_duration('9999999999w') is None


@pytest.mark.parametrize('duration, text', [
    (timedelta(0), '0:00:00'),
    (timedelta(seconds=5), '0:00:05'),
    (timedelta(hours=1, minutes=30), '1:30:00'),
    (timedelta(days=1, hours=1, minutes=30, seconds=45), '25:30:45'),
    (timedelta(weeks=1, days=1, hours=2, minutes=30), '194:30:00'),
    (timedelta(seconds=59, microseconds=999999), '0:00:59')])
def test_format_duration(duration: timedelta, text: str) -> None:
    """Test a remaining time is written as hours, never as days."""
    assert format_duration(duration) == text


@pytest.mark.parametrize('text', ['1w 1d 2:30:00', '0:00:00', '3d'])
def test_round_trip(text: str) -> None:
    """Test a written remaining time reads back as the same time."""
    duration = parse_duration(text)
    assert duration is not None
    assert parse_duration(format_duration(duration)) == duration
