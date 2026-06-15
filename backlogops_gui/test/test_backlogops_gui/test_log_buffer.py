#! /usr/local/bin/python3
"""Tests for the bounded log buffer."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from backlogops_gui.log_buffer import LogBuffer


def test_keeps_written_lines() -> None:
    """Test completed lines are returned without the trailing newline."""
    buffer = LogBuffer()
    buffer.write('first\nsecond\n')
    assert buffer.text() == 'first\nsecond'


def test_partial_line() -> None:
    """Test text without a trailing newline is kept as the last line."""
    buffer = LogBuffer()
    buffer.write('partial')
    assert buffer.text() == 'partial'
    buffer.write(' end\n')
    assert buffer.text() == 'partial end'


def test_trims_to_max() -> None:
    """Test only the most recent lines are kept."""
    buffer = LogBuffer(max_lines=2)
    buffer.write('a\nb\nc\n')
    assert buffer.text() == 'b\nc'


def test_write_returns_length() -> None:
    """Test write returns the number of characters written."""
    assert LogBuffer().write('abc') == 3
