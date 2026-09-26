#! /usr/local/bin/python3
"""Read and write a remaining time as text.

A remaining time is ideal focused person work time, which is easy to
confuse with calendar time. What is written is therefore always hours,
minutes and seconds, such as ``102:30:00``, so that nobody has to guess
what a day or a week means. What is read may also start with whole weeks
and days, such as ``1w 1d 2:30:00``, where a day is 24 hours and a week
is 7 days, so that a large value is quick to type.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import re
from datetime import timedelta
from typing import Optional

_DURATION_RE = re.compile(r'(?:(\d+)w)?\s*(?:(\d+)d)?\s*'
                          r'(?:(\d+):([0-5]\d):([0-5]\d))?')
"""Weeks, days and hours:minutes:seconds, each part optional, in order."""


def parse_duration(text: str) -> Optional[timedelta]:
    """Return the remaining time a text says, or None when it says none.

    The text is whole weeks (``1w``), whole days (``1d``) and hours,
    minutes and seconds (``2:30:00``), in that order and each of them
    optional, but at least one of them given. A day is 24 hours and a
    week is 7 days. Space around and between the parts is allowed.

    Args:
        text: The text to read.

    Returns:
        The remaining time, or None when the text is empty, not in the
        format above, or too large for a ``timedelta``.
    """
    match = _DURATION_RE.fullmatch(text.strip())
    if match is None or not any(match.groups()):
        return None
    weeks, days, hours, minutes, seconds = (int(part) if part else 0
                                            for part in match.groups())
    try:
        return timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes,
                         seconds=seconds)
    except OverflowError:
        return None


def format_duration(duration: timedelta) -> str:
    """Return a remaining time as hours, minutes and seconds.

    The hours are not split into days, so 1 day and 1.5 hours is written
    as ``25:30:00``. A fraction of a second is dropped.

    Args:
        duration: The remaining time to write, not negative.

    Returns:
        The text ``H:MM:SS``, with as many hour digits as needed.
    """
    minutes, seconds = divmod(int(duration.total_seconds()), 60)
    hours, minutes = divmod(minutes, 60)
    return f'{hours}:{minutes:02}:{seconds:02}'
