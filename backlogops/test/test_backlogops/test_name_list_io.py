#! /usr/local/bin/python3
"""Tests for reading a release name list from a file.

A text file uses one release name per line, so a name may contain spaces,
and a table file uses a single column. The tests check both shapes, that a
blank line is skipped and surrounding whitespace trimmed, that a name keeps
its spaces, that a table with more than one column is rejected, and that the
package re-exports the reader.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
import backlogops
from backlogops.no_text_io import NoTextIO
from backlogops.name_list_io import read_name_list

NO = NoTextIO()


def test_read_text(tmp_path: Path) -> None:
    """Test a plain text file reads one release name per line."""
    source = tmp_path / 'names.txt'
    source.write_text('R1\nR2\n', encoding='utf-8')
    assert read_name_list(source, stderr_file=NO) == ['R1', 'R2']


def test_text_spaces(tmp_path: Path) -> None:
    """Test a release name keeps its spaces because a line is one name."""
    source = tmp_path / 'names.txt'
    source.write_text('Release 1.0\nBig Bang 2.0\n', encoding='utf-8')
    assert read_name_list(source, stderr_file=NO) == [
        'Release 1.0', 'Big Bang 2.0']


def test_text_blank_lines(tmp_path: Path) -> None:
    """Test blank and whitespace-only lines are skipped."""
    source = tmp_path / 'names.txt'
    source.write_text('R1\n\n   \nR2\n', encoding='utf-8')
    assert read_name_list(source, stderr_file=NO) == ['R1', 'R2']


def test_text_trims(tmp_path: Path) -> None:
    """Test leading and trailing whitespace around a name is removed."""
    source = tmp_path / 'names.txt'
    source.write_text('  Release 1.0  \n\tR2\t\n', encoding='utf-8')
    assert read_name_list(source, stderr_file=NO) == ['Release 1.0', 'R2']


def test_dat_extension(tmp_path: Path) -> None:
    """Test a .dat file is read as text, like a .txt file."""
    source = tmp_path / 'names.dat'
    source.write_text('First one\nSecond one\n', encoding='utf-8')
    assert read_name_list(source, stderr_file=NO) == [
        'First one', 'Second one']


def test_empty_text(tmp_path: Path) -> None:
    """Test an empty text file reads back as an empty list."""
    source = tmp_path / 'names.txt'
    source.write_text('', encoding='utf-8')
    assert not read_name_list(source, stderr_file=NO)


def test_read_table(tmp_path: Path) -> None:
    """Test a single column table file reads as release names."""
    source = tmp_path / 'names.csv'
    source.write_text('R1\nR2\n', encoding='utf-8')
    assert read_name_list(source, stderr_file=NO) == ['R1', 'R2']


def test_table_spaces(tmp_path: Path) -> None:
    """Test a table cell keeps its spaces, as a space is not a separator."""
    source = tmp_path / 'names.csv'
    source.write_text('Release 1.0\nBig Bang 2.0\n', encoding='utf-8')
    assert read_name_list(source, stderr_file=NO) == [
        'Release 1.0', 'Big Bang 2.0']


def test_table_two_columns(tmp_path: Path) -> None:
    """Test a table with more than one column is rejected with ValueError."""
    source = tmp_path / 'names.csv'
    source.write_text('R1,X\nR2,Y\n', encoding='utf-8')
    with pytest.raises(ValueError):
        read_name_list(source, stderr_file=NO)


def test_empty_table(tmp_path: Path) -> None:
    """Test an empty table file reads back as an empty list."""
    source = tmp_path / 'names.csv'
    source.write_text('', encoding='utf-8')
    assert not read_name_list(source, stderr_file=NO)


def test_missing_file(tmp_path: Path) -> None:
    """Test a missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_name_list(tmp_path / 'absent.txt', stderr_file=NO)


def test_reexport() -> None:
    """Test the package re-exports read_name_list."""
    assert backlogops.read_name_list is read_name_list
    assert 'read_name_list' in backlogops.__all__
