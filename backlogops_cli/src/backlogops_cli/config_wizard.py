#! /usr/local/bin/python3
"""Run the backlog-ops configuration wizard and store the result."""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from typing import Optional
from backlogops import BacklogOpsConfig, backlog_ops_wizard, \
    read_backlog_ops_config
from backlogops_cli._command_io import parsed_args
from backlogops_cli._migrate_warn import CliMigrateWarnHook
from backlogops_cli._wizard_io import build_wizard_parser, run_wizard_to_file

DESCRIPTION = 'Create a backlog-ops configuration file via a wizard'


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the config wizard command."""
    return build_wizard_parser(DESCRIPTION)


def _read_config(filename: str) -> BacklogOpsConfig:
    """Read an existing backlog-ops configuration to pre-fill the wizard."""
    return read_backlog_ops_config(filename, sys.stderr,
                                   auto_ch_hook=CliMigrateWarnHook())


def main(args: Optional[list[str]] = None) -> int:
    """Run the interactive wizard and write the backlog-ops configuration.

    With ``-i`` an existing configuration file is read first and used to
    pre-fill the wizard, so the user edits those values; pointing ``-i`` at
    the same file as ``-o`` edits it in place after confirming the
    overwrite. The output filename receives the ``.cfg`` extension when it
    is not already present.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` on success, ``1`` when the entered configuration is rejected
        or cannot be read or written.
    """
    parsed = parsed_args(build_parser(), args)
    return run_wizard_to_file(parsed, backlog_ops_wizard, _read_config,
                              'Backlog-ops configuration')


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
