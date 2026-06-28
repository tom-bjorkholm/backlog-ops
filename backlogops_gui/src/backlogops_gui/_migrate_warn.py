#! /usr/local/bin/python3
"""Backward-compatibility warning hook for the graphical interface.

When the application reads a configuration file that needed
backward-compatible normalization (Reading an Old Configuration File),
this hook prints the standard migration warning followed by instructions
that point the user at the ``Write configuration…`` menu action. The
warning is written to the diagnostics stream, which the application shows
in its log view. The leading underscore in the module name marks it as an
internal helper.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from config_as_json import MigrateCfgWarnHook


class GuiMigrateWarnHook(MigrateCfgWarnHook):
    """Tell the user to migrate an old config file from the menu."""

    @classmethod
    def migrate_instructions(cls) -> str:
        """Return the graphical interface migration instructions.

        Returns:
            Text that points the user at the ``Write configuration…`` menu
            action to rewrite the configuration in the current format.
        """
        txt = 'Use "Write configuration…" in the Configuration menu to '
        txt += 'save the\nconfiguration in the current format.\n\n'
        return txt
