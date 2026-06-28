#! /usr/local/bin/python3
"""Adjust release content to fit the planned release dates.

The command reads an already estimated backlog and its releases, then
moves each backlog item to the earliest release whose planned date is on
or after the item's estimated ready date plus a slack buffer, as
documented for :func:`backlogops.adjust_release_content`. The adjusted
backlog and the releases are written to the output file, and the list of
content changes is printed to stdout, or also saved to a file when
``--changes-file`` is given.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from datetime import timedelta
from typing import Callable, Optional
from backlogops import BacklogReleases
from backlogops_cli._command_io import (
    build_change_parser, content_report, overwrite_callback, parsed_args,
    run_change_command)

DESCRIPTION = 'Adjust release content to fit the planned release dates'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the adjust-content command."""
    return build_change_parser(DESCRIPTION)


def _adjust(parsed: argparse.Namespace, data: BacklogReleases
            ) -> tuple[str, Optional[Callable[[str], None]]]:
    """Adjust the release content and return the change report."""
    changes = data.adjust_release_content(timedelta(days=parsed.buffer_days))
    return content_report(changes, overwrite_callback(parsed.force))


def main(args: Optional[list[str]] = None) -> int:
    """Adjust the release content and write the output file.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the data cannot be read, adjusted or
        written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_change_command(parsed, lambda _, data: _adjust(parsed, data))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
