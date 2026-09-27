#! /usr/local/bin/python3
"""Tests for reading and writing a remaining time as text."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import timedelta
import pytest
from backlogops import format_duration, parse_duration


@pytest.mark.parametrize('text, expected', [
    ('1:30:00', timedelta(hours=1, minutes=30)),
    ('01:30:00', timedelta(hours=1, minutes=30)),
    ('0:00:00', timedelta(0)),
    ('102:30:00', timedelta(hours=102, minutes=30)),
    ('00:00:01.5', timedelta(seconds=1.5)),
    ('1d 00:00:00', timedelta(hours=24)),
    ('1d 1:30:45', timedelta(hours=25, minutes=30, seconds=45)),
    ('1w 1d 2:30:00', timedelta(hours=194, minutes=30)),
    ('1 w 1 d 02:30:00', timedelta(hours=194, minutes=30)),
    ('1 week 2 days 00:00:00', timedelta(days=9)),
    ('  1d 0:00:01  ', timedelta(days=1, seconds=1)),
    ('1 day, 1:30:00', timedelta(hours=25, minutes=30)),
    ('2 days, 0:00:00', timedelta(days=2))])
def test_parse_duration(text: str, expected: timedelta) -> None:
    """Test TableIO duration texts with weeks and days of 24 hours."""
    assert parse_duration(text) == expected


@pytest.mark.parametrize('text', [
    '', '   ', '1:30', '1h', '1:60:00', '1:00:60', '1d', '1w', '1d 1w',
    '1:00:00 1d', '1x', 'd', '-1:00:00', '-1 day, 23:00:00'])
def test_parse_refused(text: str) -> None:
    """Test a text that is not a non-negative duration says none."""
    assert parse_duration(text) is None


@pytest.mark.parametrize('text', ['90', '1.5', ' 90 ', '-5', '1e3', 'nan'])
def test_parse_bare_number(text: str) -> None:
    """Test a bare number is refused, as it names no unit."""
    assert parse_duration(text) is None


def test_parse_too_large() -> None:
    """Test a time too large for a timedelta says no remaining time."""
    assert parse_duration('999999999999:00:00') is None


@pytest.mark.parametrize('duration, text', [
    (timedelta(0), '00:00:00'),
    (timedelta(seconds=5), '00:00:05'),
    (timedelta(hours=1, minutes=30), '01:30:00'),
    (timedelta(days=1, hours=1, minutes=30, seconds=45), '25:30:45'),
    (timedelta(weeks=1, days=1, hours=2, minutes=30), '194:30:00'),
    (timedelta(seconds=1.5), '00:00:01.5')])
def test_format_duration(duration: timedelta, text: str) -> None:
    """Test a remaining time is written as hours, never as days."""
    assert format_duration(duration) == text


@pytest.mark.parametrize('text', [
    '1w 1d 2:30:00', '0:00:00', '3d 00:00:00', '00:00:01.25'])
def test_round_trip(text: str) -> None:
    """Test a written remaining time reads back as the same time."""
    duration = parse_duration(text)
    assert duration is not None
    assert parse_duration(format_duration(duration)) == duration
