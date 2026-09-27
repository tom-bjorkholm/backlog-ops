#! /usr/local/bin/python3
"""Read and write a remaining time as text.

A remaining time is ideal focused person work time, which is easy to
confuse with calendar time. What is written is therefore always hours,
minutes and seconds, such as ``102:30:00``, so that nobody has to guess
what a day or a week means. What is read may also start with whole weeks
and days, such as ``1w 1d 02:30:00``, where a day is 24 hours and a week
is 7 days, so that a large value is quick to type.

Both directions use the duration text of TableIO (``parse_timedelta`` and
``format_timedelta`` with ``HMS_STRING``), so a remaining time looks the
same in a configuration file, in the GUI and in a CSV file written with
TableIO's default duration fallback.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from datetime import timedelta
from typing import Optional
from tableio import TimeDeltaFallback, format_timedelta, parse_timedelta


def _is_number(text: str) -> bool:
    """Return whether a text is a bare number, such as ``90`` or ``1.5``."""
    try:
        float(text)
    except ValueError:
        return False
    return True


def parse_duration(text: str) -> Optional[timedelta]:
    """Return the remaining time a text says, or None when it says none.

    The text is read by TableIO's ``parse_timedelta``: hours, minutes and
    seconds (``2:30:00``, ``25:30:00``, ``00:00:01.5``), optionally after
    whole weeks and days (``1w 1d 2:30:00``, ``1 week 2 days 00:00:00``),
    or the ``str(timedelta)`` form (``1 day, 1:30:00``). A day is 24 hours
    and a week is 7 days. A bare number is refused, because it does not
    say whether it counts seconds, hours or days, and so is a negative
    remaining time.

    Args:
        text: The text to read.

    Returns:
        The remaining time, or None when the text is empty, a bare
        number, not a duration TableIO can read, too large for a
        ``timedelta``, or negative.
    """
    if _is_number(text):
        return None
    try:
        duration = parse_timedelta(text)
    except ValueError:
        return None
    return None if duration < timedelta(0) else duration


def format_duration(duration: timedelta) -> str:
    """Return a remaining time as hours, minutes and seconds.

    The hours are not split into days, so 1 day and 1.5 hours is written
    as ``25:30:00``. The hours have at least two digits, and a fraction of
    a second is kept (``00:00:01.5``), as TableIO's ``HMS_STRING`` writes
    it.

    Args:
        duration: The remaining time to write. A negative one, which a
            valid remaining time never is, gets a leading ``-``.

    Returns:
        The text ``HH:MM:SS``, with as many hour digits as needed.
    """
    text = format_timedelta(duration, TimeDeltaFallback.HMS_STRING)
    assert isinstance(text, str)
    return text
