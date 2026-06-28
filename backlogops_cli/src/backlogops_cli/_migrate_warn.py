#! /usr/local/bin/python3
"""Backward-compatibility warning hook for the command line interface.

When a command reads a configuration file that needed backward-compatible
normalization (Reading an Old Configuration File), this hook prints the
standard migration warning followed by command-specific instructions that
point the user at the ``migrate_cfg`` command. The leading underscore in
the module name keeps it out of the command listing.
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
