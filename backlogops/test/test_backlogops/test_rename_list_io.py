#! /usr/local/bin/python3
"""Tests for reading a release rename list from a file.

A text file uses one tab-separated old and new name per line, and a table
file uses a two column layout. The tests check both shapes, that a blank
line or empty row is skipped, that a name may contain spaces, and that a
line or row without both names, or a table with the wrong column count, is
rejected.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
import backlogops
from backlogops.jira_rename_releases import ReleaseRename
from backlogops.no_text_io import NoTextIO
from backlogops.rename_list_io import read_renames

NO = NoTextIO()


def test_read_text(tmp_path: Path) -> None:
    """Test a tab-separated text file reads as old-to-new renames."""
    source = tmp_path / 'renames.txt'
    source.write_text('R1\tR9\nR2\tR8\n', encoding='utf-8')
    assert read_renames(source, stderr_file=NO) == [
        ReleaseRename('R1', 'R9'), ReleaseRename('R2', 'R8')]


def test_text_blank_lines(tmp_path: Path) -> None:
    """Test a blank line in a text file is skipped."""
    source = tmp_path / 'renames.txt'
    source.write_text('R1\tR9\n\nR2\tR8\n', encoding='utf-8')
    assert read_renames(source, stderr_file=NO) == [
        ReleaseRename('R1', 'R9'), ReleaseRename('R2', 'R8')]


def test_text_spaces(tmp_path: Path) -> None:
    """Test a name with spaces is kept whole because a tab separates them."""
    source = tmp_path / 'renames.txt'
    source.write_text('Rel 1\tRel one\n', encoding='utf-8')
    assert read_renames(source, stderr_file=NO) == [
        ReleaseRename('Rel 1', 'Rel one')]


def test_text_no_tab(tmp_path: Path) -> None:
    """Test a text line without a tab is rejected with ValueError."""
    source = tmp_path / 'renames.txt'
    source.write_text('R1 R9\n', encoding='utf-8')
    with pytest.raises(ValueError):
        read_renames(source, stderr_file=NO)


def test_text_one_name(tmp_path: Path) -> None:
    """Test a text line missing the new name is rejected with ValueError."""
    source = tmp_path / 'renames.txt'
    source.write_text('R1\t\n', encoding='utf-8')
    with pytest.raises(ValueError):
        read_renames(source, stderr_file=NO)


def test_read_table(tmp_path: Path) -> None:
    """Test a two column table file reads as old-to-new renames."""
    source = tmp_path / 'renames.csv'
    source.write_text('R1,R9\nR2,R8\n', encoding='utf-8')
    assert read_renames(source, stderr_file=NO) == [
        ReleaseRename('R1', 'R9'), ReleaseRename('R2', 'R8')]


def test_table_three_columns(tmp_path: Path) -> None:
    """Test a table with three columns is rejected with ValueError."""
    source = tmp_path / 'renames.csv'
    source.write_text('R1,R9,X\nR2,R8,Y\n', encoding='utf-8')
    with pytest.raises(ValueError):
        read_renames(source, stderr_file=NO)


def test_table_one_cell(tmp_path: Path) -> None:
    """Test a table row missing the new name is rejected with ValueError."""
    source = tmp_path / 'renames.csv'
    source.write_text('R1,\n', encoding='utf-8')
    with pytest.raises(ValueError):
        read_renames(source, stderr_file=NO)


def test_empty_table(tmp_path: Path) -> None:
    """Test an empty table file reads back as an empty list."""
    source = tmp_path / 'renames.csv'
    source.write_text('', encoding='utf-8')
    assert not read_renames(source, stderr_file=NO)


def test_table_empty_row(tmp_path: Path) -> None:
    """Test an empty table row between renames is skipped, not read."""
    source = tmp_path / 'renames.csv'
    source.write_text('R1,R9\n,\nR2,R8\n', encoding='utf-8')
    assert read_renames(source, stderr_file=NO) == [
        ReleaseRename('R1', 'R9'), ReleaseRename('R2', 'R8')]


def test_reexport() -> None:
    """Test the package re-exports read_renames."""
    assert backlogops.read_renames is read_renames
    assert 'read_renames' in backlogops.__all__
