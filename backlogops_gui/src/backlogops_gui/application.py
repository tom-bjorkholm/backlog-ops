#! /usr/local/bin/python3
"""Tkinter application for backlog operations.

The application opens a main window whose menu reads a backlog from a file,
runs the teams configuration wizard, writes the running configuration to a
file, and creates a demonstration backlog. Each backlog opens in its own
window. The teams configuration is taken from the file given with ``-c`` or
from the configured locations; when no configuration is found the wizard
runs at startup, and cancelling it ends the application.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import tkinter as tk
from tkinter import messagebox
from typing import Optional
import argcomplete
from config_as_json.file_extension import fix_file_extension
from backlogops import (
    AvailableTeamsConfig, BacklogReleases, InputFormatConfig, NoTextIO,
    OutputFormatConfig, get_demo_backlog, get_available_teams,
    teams_config_wizard)
from backlogops_gui.backlog_io import read_backlog
from backlogops_gui.backlog_window import BacklogWindow
from backlogops_gui.gui_wizard import TkWizardBridge
from backlogops_gui.io_dialogs import (
    ask_read_options, choose_config_file, choose_input_file)
from backlogops_gui.tcltk_version import check_tcltk_version

APP_TITLE = 'Backlog operations GUI'
CONFIG_EXTENSION = '.cfg'
WARN_WRAP_LENGTH = 520
DESCRIPTION = 'Graphical user interface for backlog operations'
CONFIG_ERRORS = (FileNotFoundError, NotADirectoryError, RuntimeError,
                 ValueError, TypeError, KeyError, OSError)
IO_ERRORS = (ValueError, TypeError, KeyError, OSError)


def initial_config(config_arg: Optional[str]
                   ) -> tuple[Optional[AvailableTeamsConfig], Optional[str]]:
    """Return the startup configuration and an optional error message.

    The configuration is looked up as documented for
    :func:`backlogops.get_available_teams`. A failure is mapped to a None
    configuration and the error text, so the caller can decide whether to
    show the error and whether to run the wizard.

    Args:
        config_arg: The file from ``-c``, or None to search the defaults.

    Returns:
        The loaded configuration and None, or None and the error text.
    """
    try:
        return get_available_teams(config_arg, NoTextIO()), None
    except CONFIG_ERRORS as error:
        return None, str(error)


class BacklogApp:
    """The backlog operations application and its menu actions."""

    def __init__(self, root: tk.Tk,
                 config: Optional[AvailableTeamsConfig] = None) -> None:
        """Store the main window and the current configuration."""
        self.root = root
        self.config = config

    def in_presets(self) -> Optional[dict[str, InputFormatConfig]]:
        """Return the input presets of the current configuration."""
        return self.config.input_configs if self.config else None

    def out_presets(self) -> Optional[dict[str, OutputFormatConfig]]:
        """Return the output presets of the current configuration."""
        return self.config.output_configs if self.config else None

    def show_error(self, title: str, message: str) -> None:
        """Show an error message to the user."""
        messagebox.showerror(title, message, parent=self.root)

    def show_info(self, title: str, message: str) -> None:
        """Show an informational message to the user."""
        messagebox.showinfo(title, message, parent=self.root)

    def start(self, config_arg: Optional[str]) -> bool:
        """Load the startup configuration, running the wizard if needed.

        A configuration named with ``-c`` that cannot be read is reported
        before the wizard runs. When no configuration is loaded and the
        wizard is cancelled, the application is not ready to run.

        Args:
            config_arg: The file from ``-c``, or None to search defaults.

        Returns:
            Whether the application is ready to enter its main loop.
        """
        config, error = initial_config(config_arg)
        if config is None:
            if config_arg is not None and error is not None:
                self.show_error('Configuration error', error)
            config = self.run_wizard()
            if config is None:
                return False
        self.config = config
        return True

    def run_wizard(self) -> Optional[AvailableTeamsConfig]:
        """Run the teams wizard and return its configuration, or None."""
        bridge = TkWizardBridge(self.root)
        try:
            return teams_config_wizard(bridge)
        except EOFError:
            return None
        except IO_ERRORS as error:
            self.show_error('Wizard error', str(error))
            return None

    def run_teams_wizard(self) -> None:
        """Run the wizard and make a new configuration active on success."""
        config = self.run_wizard()
        if config is not None:
            self.config = config
            self.show_info('Wizard', 'The new configuration is now active.')

    def write_config(self) -> None:
        """Write the running configuration to a chosen file."""
        if self.config is None:
            self.show_error('No configuration',
                            'There is no configuration to write.')
            return
        path = choose_config_file(self.root)
        if path is None:
            return
        path = fix_file_extension(path, CONFIG_EXTENSION)
        try:
            self.config.write(to_json_filename=path, stderr_file=NoTextIO())
        except IO_ERRORS as error:
            self.show_error('Could not write configuration', str(error))
            return
        self.show_info('Wrote configuration', f'Wrote {path}')

    def read_backlog_file(self) -> None:
        """Read a backlog from a chosen file into a new window."""
        path = choose_input_file(self.root)
        if path is None:
            return
        presets = self.in_presets()
        options = ask_read_options(self.root,
                                   sorted(presets) if presets else None)
        if options is None:
            return
        try:
            data = read_backlog(path, options.config_value, presets)
        except IO_ERRORS as error:
            self.show_error('Could not read file', str(error))
            return
        self.open_backlog(data, path)

    def new_demo_backlog(self) -> None:
        """Open a demonstration backlog in a new window."""
        self.open_backlog(get_demo_backlog(), 'Demo backlog')

    def open_backlog(self, data: BacklogReleases, title: str) -> None:
        """Open one backlog and its releases in a new window."""
        BacklogWindow(self.root, data, title, self.out_presets,
                      self.show_error, self.show_info)

    def build_menu(self) -> None:
        """Build the menu bar of the main window."""
        menubar = tk.Menu(self.root)
        self._add_file_menu(menubar)
        self._add_config_menu(menubar)
        self.root.config(menu=menubar)

    def _add_file_menu(self, menubar: tk.Menu) -> None:
        """Add the file menu with the backlog and exit actions."""
        menu = tk.Menu(menubar, tearoff=False)
        menu.add_command(label='Read backlog…', command=self.read_backlog_file)
        menu.add_command(label='New demo backlog',
                         command=self.new_demo_backlog)
        menu.add_separator()
        menu.add_command(label='Exit', command=self.root.destroy)
        menubar.add_cascade(label='File', menu=menu)

    def _add_config_menu(self, menubar: tk.Menu) -> None:
        """Add the configuration menu with the wizard and write actions."""
        menu = tk.Menu(menubar, tearoff=False)
        menu.add_command(label='Run teams wizard…',
                         command=self.run_teams_wizard)
        menu.add_command(label='Write configuration…',
                         command=self.write_config)
        menubar.add_cascade(label='Configuration', menu=menu)


def _build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the GUI launcher."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-c', '--config', dest='config',
                        help='Teams configuration file to start with. '
                        'Without -c the file is found from $BACKLOGOPS_CFG, '
                        'else backlogops.cfg in $BACKLOGOPS_DIR, else '
                        '$HOME/.backlogops.cfg.')
    return parser


def _add_warning(root: tk.Tk) -> None:
    """Add a Tcl/Tk version warning label when one applies."""
    warning_text = check_tcltk_version(root)
    if warning_text is not None:
        tk.Label(root, text=warning_text, wraplength=WARN_WRAP_LENGTH,
                 justify='left').pack(padx=16, pady=8)


def main(args: Optional[list[str]] = None) -> None:
    """Start the backlog operations GUI.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.
    """
    parser = _build_parser()
    argcomplete.autocomplete(parser)
    parsed = parser.parse_args(args)
    root = tk.Tk()
    app = BacklogApp(root)
    if not app.start(parsed.config):
        root.destroy()
        return
    root.title(APP_TITLE)
    app.build_menu()
    _add_warning(root)
    root.mainloop()
