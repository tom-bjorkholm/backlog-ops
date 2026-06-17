#! /usr/local/bin/python3
"""Tests for the NoTextIO do-nothing text stream."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from backlogops.no_text_io import NoTextIO


def test_write_discards() -> None:
    """Test write accepts text, stores nothing and reports zero."""
    sink = NoTextIO()
    assert sink.write('hello') == 0
    assert sink.getvalue() == ''


def test_writelines_discards() -> None:
    """Test writelines accepts lines and stores nothing."""
    sink = NoTextIO()
    assert sink.writelines(['a', 'b']) is None
    assert sink.getvalue() == ''


def test_flush_and_close() -> None:
    """Test flush and close do nothing and keep the stream usable."""
    sink = NoTextIO()
    assert sink.flush() is None
    assert sink.close() is None
    assert sink.write('after close') == 0


def test_seek_and_tell() -> None:
    """Test seek and tell always report position zero."""
    sink = NoTextIO()
    sink.write('content')
    assert sink.seek(5) == 0
    assert sink.seek(2, io.SEEK_CUR) == 0
    assert sink.tell() == 0


def test_truncate() -> None:
    """Test truncate reports zero whether or not a size is given."""
    sink = NoTextIO()
    assert sink.truncate() == 0
    assert sink.truncate(10) == 0


def test_context_manager() -> None:
    """Test the stream works as a context manager returning itself."""
    with NoTextIO() as sink:
        assert isinstance(sink, NoTextIO)
        assert sink.write('inside') == 0
