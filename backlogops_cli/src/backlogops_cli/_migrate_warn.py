#! /usr/local/bin/python3
"""Backward-compatibility warning hooks for the command line interface.

When a command reads a file that needed backward-compatible normalization
(Reading an Old Configuration File), one of these hooks prints the
standard migration warning followed by command-specific instructions.
``CliMigrateWarnHook`` is used when the old file is the backlog-ops
configuration file and shows the ``migrate_cfg`` command for the default
config kind. ``CliPresetMigrateWarnHook`` is used when the old file is a
stand-alone input or output preset file and shows the ``migrate_cfg``
command with the ``--kind`` option, because that option selects how a
preset file is migrated. The leading underscore in the module name keeps
it out of the command listing.
"""
# PYTHON_ARGCOMPLETE_OK

# Copyright (c) 2026, Tom Björkholm
# MIT License

from config_as_json import MigrateCfgWarnHook


class CliMigrateWarnHook(MigrateCfgWarnHook):
    """Tell the user to migrate an old config file with ``migrate_cfg``."""

    @classmethod
    def migrate_instructions(cls) -> str:
        """Return the command line migration instructions.

        Returns:
            Text that points the user at the ``migrate_cfg`` command to
            rewrite the configuration file in the current format.
        """
        txt = 'Run the migrate_cfg command to write the configuration file '
        txt += 'in the\ncurrent format, for example:\n'
        txt += '  python3 -m backlogops_cli.migrate_cfg -i OLD.cfg '
        txt += '-o NEW.cfg\n\n'
        return txt


class CliPresetMigrateWarnHook(MigrateCfgWarnHook):
    """Tell the user to migrate an old preset file with ``migrate_cfg``."""

    @classmethod
    def migrate_instructions(cls) -> str:
        """Return the command line preset migration instructions.

        Returns:
            Text that points the user at the ``migrate_cfg`` command with
            the ``--kind`` option for input or output preset files.
        """
        txt = 'Run the migrate_cfg command with -k input or -k output to '
        txt += 'write the\npreset file in the current format, for example:\n'
        txt += '  python3 -m backlogops_cli.migrate_cfg -k input '
        txt += '-i OLD.cfg -o NEW.cfg\n\n'
        return txt
