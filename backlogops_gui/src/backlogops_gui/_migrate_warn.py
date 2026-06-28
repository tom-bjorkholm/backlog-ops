#! /usr/local/bin/python3
"""Backward-compatibility warning hooks for the graphical interface.

When the application reads a file that needed backward-compatible
normalization (Reading an Old Configuration File), one of these hooks
prints the standard migration warning followed by menu-specific
instructions. ``GuiMigrateWarnHook`` is used when the old file is the
running backlog-ops configuration and points at the ``Write
configuration…`` menu action. ``GuiPresetMigrateWarnHook`` is used when
the old file is a stand-alone input or output preset file and points at
the ``Migrate IO preset file…`` menu action, because rewriting the
running configuration would not update that preset file. The warning is
written to the diagnostics stream, which the application shows in its log
view. The leading underscore in the module name marks it as an internal
helper.
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


class GuiPresetMigrateWarnHook(MigrateCfgWarnHook):
    """Tell the user to migrate an old preset file from the menu."""

    @classmethod
    def migrate_instructions(cls) -> str:
        """Return the graphical interface preset migration instructions.

        Returns:
            Text that points the user at the ``Migrate IO preset file…``
            menu action to rewrite the preset file in the current format.
        """
        txt = 'Use "Migrate IO preset file…" in the Configuration menu to '
        txt += 'write\nthe preset file in the current format.\n\n'
        return txt
