#! /usr/local/bin/python3
"""Tests for the format-value mapping and option dataclasses."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional
import pytest
from backlogops_gui.io_dialogs import (
    MODE_FILE, MODE_INFER, MODE_PRESET, ReadOptions, WriteOptions,
    format_value)


@pytest.mark.parametrize('mode,preset,path,expected', [
    (MODE_INFER, 'preset', 'file.csv', None),
    (MODE_PRESET, 'preset', '', 'preset'),
    (MODE_PRESET, '', '', None),
    (MODE_FILE, '', 'cfg.json', 'cfg.json'),
    (MODE_FILE, '', '', None)])
def test_format_value(mode: int, preset: str, path: str,
                      expected: Optional[str]) -> None:
    """Test the selected mode maps to the right resolver value."""
    assert format_value(mode, preset, path) == expected


def test_option_dataclasses() -> None:
    """Test the option dataclasses hold the entered selection."""
    assert ReadOptions(None).config_value is None
    write = WriteOptions('preset', True)
    assert write.config_value == 'preset'
    assert write.releases_first is True
