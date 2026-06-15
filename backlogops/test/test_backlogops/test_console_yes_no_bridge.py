#! /usr/local/bin/python3
"""Tests for the console yes/no wizard bridge."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
import pytest
from backlogops.console_yes_no_bridge import ConsoleYesNoUiBridge


def _bridge(answer: str) -> ConsoleYesNoUiBridge:
    """Return a console bridge scripted with one answer stream."""
    return ConsoleYesNoUiBridge(io.StringIO(), io.StringIO(answer),
                                io.StringIO())


@pytest.mark.parametrize('answer,default,expected', [
    ('y\n', False, True),
    ('yes\n', False, True),
    ('n\n', True, False),
    ('no\n', True, False),
    ('\n', True, True),
    ('\n', False, False),
    ('maybe\ny\n', False, True)])
def test_ask_yes_no(answer: str, default: bool, expected: bool) -> None:
    """Test the answer text, defaults and re-asking yield the boolean."""
    assert _bridge(answer).ask_yes_no('Add?', default) is expected
