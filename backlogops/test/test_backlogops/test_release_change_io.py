#! /usr/local/bin/python3
"""Tests for printing and writing release-change records."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from pathlib import Path
import pytest
from tableio import FileAccess, Value, access_capabilities, tio_config_create
from backlogops import (
    ReleaseChange, ReleaseDateChange, format_content_changes,
    format_date_changes, resolve_input_config, write_content_changes,
    write_date_changes)
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()


def _read_rows(path: Path) -> list[list[Value]]:
    """Return the rows of a one table file read with list reading."""
    config = resolve_input_config(None, data_file=path,
                                  stderr_file=NO_OUTPUT).tableio
    capabilities = access_capabilities(FileAccess.READ, error_file=NO_OUTPUT)
    with tio_config_create(config=config, file_name=path,
                           file_access=FileAccess.READ,
                           capabilities=capabilities) as tableio:
        rows = tableio.read_table_listdata().data
    return rows


def test_fmt_content() -> None:
    """Test the content listing names the item and both releases."""
    changes = [ReleaseChange('a', 'R1', 'R2'), ReleaseChange('b', 'R3', None)]
    text = format_content_changes(changes)
    assert 'Release content changes:' in text
    assert 'a: R1 -> R2' in text
    assert 'b: R3 -> (none)' in text


def test_fmt_date() -> None:
    """Test the date listing names the release and both dates."""
    changes = [ReleaseDateChange('R1', None, date(2026, 1, 15))]
    text = format_date_changes(changes)
    assert 'Release date changes:' in text
    assert 'R1: (none) -> 2026-01-15' in text


def test_format_empty() -> None:
    """Test an empty change list yields the no-changes message."""
    assert format_content_changes([]) == 'No release content changes.'
    assert format_date_changes([]) == 'No release date changes.'


def test_write_content(tmp_path: Path) -> None:
    """Test content changes are written with a header and an empty cell."""
    target = tmp_path / 'changes.csv'
    write_content_changes([ReleaseChange('a', 'R1', None)], target, NO_OUTPUT)
    rows = _read_rows(target)
    assert rows[0] == ['backlog_key', 'old_release', 'new_release']
    assert rows[1][0] == 'a'
    assert rows[1][1] == 'R1'
    assert rows[1][2] in (None, '')


def test_write_date(tmp_path: Path) -> None:
    """Test date changes are written as ISO strings with a header."""
    target = tmp_path / 'changes.csv'
    write_date_changes([ReleaseDateChange('R1', None, date(2026, 1, 15))],
                       target, NO_OUTPUT)
    rows = _read_rows(target)
    assert rows[0] == ['release', 'old_date', 'new_date']
    assert rows[1][0] == 'R1'
    assert rows[1][1] in (None, '')
    assert rows[1][2] == '2026-01-15'


def test_write_existing_file(tmp_path: Path) -> None:
    """Test writing over an existing changes file raises an error."""
    target = tmp_path / 'changes.csv'
    target.write_text('x', encoding='utf-8')
    with pytest.raises(FileExistsError):
        write_date_changes([ReleaseDateChange('R1', None, date(2026, 1, 1))],
                           target, NO_OUTPUT)
