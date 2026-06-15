#! /usr/local/bin/python3
"""A bounded text sink that keeps the most recent log lines.

The graphical application routes the diagnostics that the library would
write to ``stderr`` into a log buffer instead of discarding them, so the
most recent lines can be shown in the main window. The buffer keeps only a
bounded number of the latest lines, so a long-running session cannot
exhaust memory.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from collections import deque
from typing import override

DEFAULT_MAX_LINES = 100


class LogBuffer(io.StringIO):
    """A text sink keeping only the most recent written lines."""

    def __init__(self, max_lines: int = DEFAULT_MAX_LINES) -> None:
        """Create an empty buffer keeping at most ``max_lines`` lines."""
        super().__init__()
        self._lines: deque[str] = deque(maxlen=max_lines)
        self._partial = ''

    @override
    def write(self, s: str) -> int:
        """Append text, keeping only the most recent completed lines.

        The text is split on newlines; completed lines join the bounded
        store and any text after the last newline is kept as the pending
        last line. Nothing is stored in the underlying string buffer, so
        memory stays bounded regardless of how much is written.
        """
        combined = self._partial + s
        parts = combined.split('\n')
        self._partial = parts.pop()
        self._lines.extend(parts)
        return len(s)

    def text(self) -> str:
        """Return the kept lines, including any unfinished last line."""
        lines = list(self._lines)
        if self._partial:
            lines.append(self._partial)
        return '\n'.join(lines)
