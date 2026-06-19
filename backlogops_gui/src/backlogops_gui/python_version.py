#! /usr/local/bin/python3
"""Python version support check for the backlog operations GUI."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from typing import Optional
from backlogops.blo_version_reporter import BloVersionReporter
from backlogops_gui.blog_version_reporter import BloGuiVersionReporter


def check_python_version(
        reporter: Optional[BloVersionReporter] = None) -> Optional[str]:
    """Return a warning when the running Python version is unsupported.

    The version reporter writes an explanation and upgrade instructions
    only when the running Python version is no longer supported by the
    application, and writes nothing otherwise. Its output is captured so
    it can be shown in the main window instead of on standard output.

    Args:
        reporter: The reporter to query, or None to use the GUI reporter.

    Returns:
        The captured warning text, or None when Python is still supported.
    """
    used = BloGuiVersionReporter() if reporter is None else reporter
    buffer = io.StringIO()
    used.check_if_unsupported_python(out_file=buffer)
    text = buffer.getvalue().strip()
    return text if text else None
