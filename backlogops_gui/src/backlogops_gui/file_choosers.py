#! /usr/local/bin/python3
"""Native file choosers for the backlog operations application.

Each helper opens a native open- or save-file dialog for one purpose and
returns the chosen path, or None when the user cancels. Keeping the
choosers in one module lets the tests drive them by patching a single
``filedialog`` reference.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import filedialog
from typing import Optional


def choose_input_file(parent: tk.Misc) -> Optional[str]:
    """Ask for an existing backlog file, or None when cancelled."""
    name = filedialog.askopenfilename(parent=parent, title='Read backlog')
    return name or None


def choose_output_file(parent: tk.Misc) -> Optional[str]:
    """Ask for a backlog file to create, or None when cancelled."""
    name = filedialog.asksaveasfilename(parent=parent, title='Save backlog')
    return name or None


def choose_config_file(parent: tk.Misc) -> Optional[str]:
    """Ask for a configuration file to create, or None when cancelled."""
    name = filedialog.asksaveasfilename(parent=parent,
                                        title='Write configuration')
    return name or None


def choose_existing_config(parent: tk.Misc) -> Optional[str]:
    """Ask for an existing configuration file, or None when cancelled."""
    name = filedialog.askopenfilename(parent=parent,
                                      title='Load configuration')
    return name or None


def choose_preset_to_migrate(parent: tk.Misc) -> Optional[str]:
    """Ask for an existing preset file to migrate, or None when cancelled."""
    name = filedialog.askopenfilename(parent=parent,
                                      title='Migrate preset file')
    return name or None


def choose_migrated_preset(parent: tk.Misc) -> Optional[str]:
    """Ask for a migrated preset file to create, or None when cancelled."""
    name = filedialog.asksaveasfilename(parent=parent,
                                        title='Save migrated preset')
    return name or None


def choose_key_list_output(parent: tk.Misc) -> Optional[str]:
    """Ask for a key list file to create, or None when cancelled."""
    name = filedialog.asksaveasfilename(parent=parent, title='Write keys')
    return name or None


def choose_changes_output(parent: tk.Misc) -> Optional[str]:
    """Ask for a changes file to create, or None when cancelled."""
    name = filedialog.asksaveasfilename(parent=parent, title='Save changes')
    return name or None
