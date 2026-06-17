#! /usr/local/bin/python3
"""Tests for reading and writing key lists."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from backlogops import read_key_list, write_key_list
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()
KEYS = ['A1', 'B2', 'C3']


@pytest.mark.parametrize('extension', ['.txt', '.dat', '.csv', '.ods'])
def test_round_trip(tmp_path: Path, extension: str) -> None:
    """Test keys written to a file are read back unchanged and in order."""
    target = tmp_path / f'keys{extension}'
    write_key_list(KEYS, target, stderr_file=NO_OUTPUT)
    assert read_key_list(target, stderr_file=NO_OUTPUT) == KEYS


def test_text_with_header(tmp_path: Path) -> None:
    """Test a text column with a heading round trips with the heading set."""
    target = tmp_path / 'keys.txt'
    write_key_list(KEYS, target, add_column_name=True, stderr_file=NO_OUTPUT)
    assert target.read_text(encoding='utf-8').splitlines()[0] == 'Keys'
    read = read_key_list(target, skip_column_names=True, stderr_file=NO_OUTPUT)
    assert read == KEYS


@pytest.mark.parametrize('extension', ['.csv', '.ods'])
def test_table_with_header(tmp_path: Path, extension: str) -> None:
    """Test a table with a column name round trips when the name is set."""
    target = tmp_path / f'keys{extension}'
    write_key_list(KEYS, target, add_column_name=True, stderr_file=NO_OUTPUT)
    read = read_key_list(target, skip_column_names=True, stderr_file=NO_OUTPUT)
    assert read == KEYS


def test_text_word_list(tmp_path: Path) -> None:
    """Test a free text file yields every word in order, across lines."""
    source = tmp_path / 'keys.txt'
    source.write_text('A1 B2\nC3\n', encoding='utf-8')
    assert read_key_list(source, stderr_file=NO_OUTPUT) == KEYS


def test_skip_blank_lines(tmp_path: Path) -> None:
    """Test blank lines under a heading are skipped, not treated as keys."""
    source = tmp_path / 'keys.txt'
    source.write_text('Keys\nA1\n\nB2\n', encoding='utf-8')
    read = read_key_list(source, skip_column_names=True, stderr_file=NO_OUTPUT)
    assert read == ['A1', 'B2']


def test_column_two_words(tmp_path: Path) -> None:
    """Test a column line with two words is rejected with ValueError."""
    source = tmp_path / 'keys.txt'
    source.write_text('Keys\nA1 extra\n', encoding='utf-8')
    with pytest.raises(ValueError):
        read_key_list(source, skip_column_names=True, stderr_file=NO_OUTPUT)


def test_empty_round_trip(tmp_path: Path) -> None:
    """Test an empty key list is written and read back as an empty list."""
    target = tmp_path / 'keys.txt'
    write_key_list([], target, stderr_file=NO_OUTPUT)
    assert read_key_list(target, stderr_file=NO_OUTPUT) == []


def test_empty_table_list(tmp_path: Path) -> None:
    """Test an empty one-column table reads back as an empty list."""
    target = tmp_path / 'keys.csv'
    target.write_text('', encoding='utf-8')
    assert read_key_list(target, stderr_file=NO_OUTPUT) == []


def test_empty_table_dict(tmp_path: Path) -> None:
    """Test a table holding only a column name reads as an empty list."""
    target = tmp_path / 'keys.csv'
    target.write_text('Keys\n', encoding='utf-8')
    assert read_key_list(target, skip_column_names=True,
                         stderr_file=NO_OUTPUT) == []


def test_numeric_keys(tmp_path: Path) -> None:
    """Test numeric-looking table cells are returned as string keys."""
    target = tmp_path / 'keys.csv'
    write_key_list(['1', '2', '3'], target, stderr_file=NO_OUTPUT)
    assert read_key_list(target, stderr_file=NO_OUTPUT) == ['1', '2', '3']


def test_table_two_columns(tmp_path: Path) -> None:
    """Test a table with more than one column is rejected with ValueError."""
    source = tmp_path / 'keys.csv'
    source.write_text('Col1,Col2\nA1,X\n', encoding='utf-8')
    with pytest.raises(ValueError):
        read_key_list(source, stderr_file=NO_OUTPUT)


def test_existing_file(tmp_path: Path) -> None:
    """Test writing over an existing file raises FileExistsError."""
    target = tmp_path / 'keys.txt'
    target.write_text('', encoding='utf-8')
    with pytest.raises(FileExistsError):
        write_key_list(KEYS, target, stderr_file=NO_OUTPUT)


def test_missing_file(tmp_path: Path) -> None:
    """Test reading a missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_key_list(tmp_path / 'nope.txt', stderr_file=NO_OUTPUT)
