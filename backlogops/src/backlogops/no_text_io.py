#! /usr/local/bin/python3
"""NoTextIO can be used as a TextIO object that does nothing."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import override
from collections.abc import Iterable
from types import TracebackType
import io


class NoTextIO(io.StringIO):
    """NoTextIO can be used as a TextIO object that does nothing.

    When a function expects a TextIO object for output, you can pass in
    a NoTextIO object and no output will be produced.
    The differrence compared to using StringIO to suppress output is that
    the NoTextIO does not store any data, so no matter how much is
    written to it, you do not risk running out of memory.
    """

    @override
    def write(self, s: str) -> int:
        """Write a string to the NoTextIO object.

        This method does nothing and returns 0.
        """
        _ = s
        return 0

    @override
    def writelines(self,  # type: ignore[override]
                   lines: Iterable[str]) -> None:
        """Write a list of strings to the NoTextIO object.

        This method does nothing and returns None.
        """
        _ = lines

    @override
    def flush(self) -> None:
        """Flush the NoTextIO object.

        This method does nothing and returns None.
        """

    @override
    def close(self) -> None:
        """Close the NoTextIO object.

        This method does nothing and returns None.
        """

    @override
    def seek(self, offset: int, whence: int = io.SEEK_SET, /) -> int:
        """Seek to a position in the NoTextIO object.

        This method does nothing and returns 0.
        """
        _ = offset
        _ = whence
        return 0

    @override
    def tell(self) -> int:
        """Get the current position in the NoTextIO object.

        This method does nothing and returns 0.
        """
        return 0

    @override
    def truncate(self, size: int | None = None, /) -> int:
        """Truncate the NoTextIO object.

        This method does nothing and returns 0.
        """
        _ = size
        return 0

    @override
    def __enter__(self) -> 'NoTextIO':
        """Enter the NoTextIO object.

        This method does nothing and returns the NoTextIO object.
        """
        return self

    @override
    def __exit__(self, exc_type: type[BaseException] | None,
                 exc_value: BaseException | None,
                 traceback: TracebackType | None) -> None:
        """Exit the NoTextIO object.

        This method does nothing.
        """
        _ = exc_type
        _ = exc_value
        _ = traceback
