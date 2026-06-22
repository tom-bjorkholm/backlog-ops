#! /usr/local/bin/python3
"""Tkinter application for backlog operations.

The application opens a main window whose menu reads a backlog from a file,
runs the teams configuration wizard, writes the running configuration to a
file, and creates a demonstration backlog. Each backlog opens in its own
window. On macOS the menu bar sits at the top of the display rather than in
the window, so the main window body shows a short description, the current
configuration status, and a log of the most recent diagnostic messages, to
make clear that the application is running. The teams configuration is
taken from the file given with ``-c`` or from the configured locations;
when no configuration is found a startup dialog offers to run the wizard,
load a configuration file, or exit. Cancelling the wizard or a dialog
returns to that choice, so the application ends only when the user exits.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional, TextIO
import argcomplete
from config_as_json.file_extension import fix_file_extension
from backlogops import (
    AvailableTeams, AvailableTeamsConfig, BacklogReleases, InputFormatConfig,
    NoTextIO, OutputFormatConfig, get_demo_backlog, get_available_teams,
    teams_config_wizard)
from backlogops_gui.backlog_io import read_backlog
from backlogops_gui.backlog_window import BacklogWindow
from backlogops_gui.blog_version_reporter import BloGuiVersionReporter
from backlogops_gui.gui_wizard import TkWizardBridge
from backlogops_gui.io_dialogs import (
    ConfigChoice, ask_no_config_choice, ask_read_options, choose_config_file,
    choose_existing_config, choose_input_file)
from backlogops_gui.log_buffer import LogBuffer
from backlogops_gui.python_version import check_python_version
from backlogops_gui.tcltk_version import check_tcltk_version

APP_TITLE = 'Backlog operations GUI'
CONFIG_EXTENSION = '.cfg'
WRAP_LENGTH = 520
LOG_REFRESH_MS = 800
HEADING_FONT = ('TkDefaultFont', 14, 'bold')
INSTRUCTIONS = (
    'Use the menus to read a backlog file, run the teams wizard, write the '
    'current configuration to a file, or create a demonstration backlog. '
    'Each backlog opens in its own window. On macOS the menu bar is at the '
    'top of the display.')
DESCRIPTION = 'Graphical user interface for backlog operations'
CONFIG_ERRORS = (FileNotFoundError, NotADirectoryError, RuntimeError,
                 ValueError, TypeError, KeyError, OSError)
IO_ERRORS = (ValueError, TypeError, KeyError, OSError)
VERSION_ERRORS = (OSError, RuntimeError, ValueError)


def initial_config(config_arg: Optional[str], sink: Optional[TextIO] = None
                   ) -> tuple[Optional[AvailableTeamsConfig], Optional[str]]:
    """Return the startup configuration and an optional error message.

    The configuration is looked up as documented for
    :func:`backlogops.get_available_teams`. A failure is mapped to a None
    configuration and the error text, so the caller can decide whether to
    show the error and whether to run the wizard.

    Args:
        config_arg: The file from ``-c``, or None to search the defaults.
        sink: Stream for diagnostics, or None to discard them.

    Returns:
        The loaded configuration and None, or None and the error text.
    """
    out = NoTextIO() if sink is None else sink
    try:
        return get_available_teams(config_arg, out), None
    except CONFIG_ERRORS as error:
        return None, str(error)


class BacklogApp:
    """The backlog operations application and its menu actions."""

    def __init__(self, root: tk.Tk,
                 config: Optional[AvailableTeamsConfig] = None) -> None:
        """Store the main window, configuration, and a log buffer."""
        self.root = root
        self.config = config
        self.log = LogBuffer()
        self.config_source: Optional[str] = None
        self.log_view: Optional[tk.Text] = None
        self._status: Optional[tk.StringVar] = None

    def in_presets(self) -> Optional[dict[str, InputFormatConfig]]:
        """Return the input presets of the current configuration."""
        return self.config.input_configs if self.config else None

    def out_presets(self) -> Optional[dict[str, OutputFormatConfig]]:
        """Return the output presets of the current configuration."""
        return self.config.output_configs if self.config else None

    def available_teams(self) -> Optional[AvailableTeams]:
        """Return the loaded teams configuration, or None when absent."""
        return self.config

    def show_error(self, title: str, message: str) -> None:
        """Show an error message to the user."""
        messagebox.showerror(title, message, parent=self.root)

    def show_info(self, title: str, message: str) -> None:
        """Show an informational message to the user."""
        messagebox.showinfo(title, message, parent=self.root)

    def start(self, config_arg: Optional[str]) -> bool:
        """Load the startup configuration, offering choices if needed.

        A configuration named with ``-c`` that cannot be read is reported
        before the no-configuration dialog is shown. When no configuration
        is loaded the user may run the wizard, load a file, or exit, and
        the application is ready only once a configuration is in place.

        Args:
            config_arg: The file from ``-c``, or None to search defaults.

        Returns:
            Whether the application is ready to enter its main loop.
        """
        config, error = initial_config(config_arg, self.log)
        if config is not None:
            self.config = config
            self.config_source = (config_arg if config_arg is not None
                                  else 'the default location')
            return True
        if config_arg is not None and error is not None:
            self.show_error('Configuration error', error)
        return self._resolve_missing_config()

    def _resolve_missing_config(self) -> bool:
        """Offer to create, load, or exit until a configuration is ready.

        The no-configuration dialog is shown repeatedly: running the
        wizard or loading a file makes the application ready, while
        cancelling either one returns to the dialog. Only the exit choice,
        or closing the dialog, ends the application.
        """
        while True:
            choice = ask_no_config_choice(self.root)
            if choice is ConfigChoice.WIZARD and self._adopt_startup_wizard():
                return True
            if choice is ConfigChoice.LOAD and self._adopt_loaded_config():
                return True
            if choice is ConfigChoice.EXIT:
                return False

    def _adopt_startup_wizard(self) -> bool:
        """Run the startup wizard, adopting a configuration it produces."""
        config = self.run_wizard()
        if config is None:
            return False
        self.config = config
        self.config_source = 'the wizard'
        return True

    def _adopt_loaded_config(self) -> bool:
        """Load a chosen configuration file, adopting it on success."""
        path = choose_existing_config(self.root)
        if path is None:
            return False
        config, error = initial_config(path, self.log)
        if config is None:
            self.show_error('Configuration error',
                            error or 'Could not load the configuration.')
            return False
        self.config = config
        self.config_source = path
        return True

    def run_wizard(self) -> Optional[AvailableTeamsConfig]:
        """Run the teams wizard and return its configuration, or None."""
        bridge = TkWizardBridge(self.root, self.log)
        try:
            return teams_config_wizard(bridge)
        except EOFError:
            return None
        except IO_ERRORS as error:
            self.show_error('Wizard error', str(error))
            return None
        finally:
            bridge.close()

    def run_teams_wizard(self) -> None:
        """Run the wizard and make a new configuration active on success."""
        config = self.run_wizard()
        if config is not None:
            self.config = config
            self.config_source = 'the wizard'
            self._update_status()
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
            self.config.write(to_json_filename=path, stderr_file=self.log)
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
            data = read_backlog(path, options.config_value, presets, self.log)
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
                      self.available_teams, self.log)

    def report_versions(self) -> None:
        """Report version information into the log on a worker thread.

        The report queries PyPI for newer releases, which can take several
        seconds, so it runs on a daemon thread that only writes to the log
        buffer. The periodic refresh then shows the result in the window.
        """
        self.log.write('Collecting version information…\n')
        thread = threading.Thread(target=self._write_version_report,
                                  daemon=True)
        thread.start()

    def _write_version_report(self) -> None:
        """Write the version report to the log buffer.

        This runs on a worker thread and must not touch any widgets. A
        failure, such as missing network access, is written to the log
        rather than raised on the worker thread where it would be lost.
        """
        try:
            BloGuiVersionReporter().print(out_file=self.log)
        except VERSION_ERRORS as error:
            self.log.write(f'Could not report versions: {error}\n')

    def build_menu(self) -> None:
        """Build the menu bar of the main window."""
        menubar = tk.Menu(self.root)
        self._add_file_menu(menubar)
        self._add_config_menu(menubar)
        self._add_help_menu(menubar)
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

    def _add_help_menu(self, menubar: tk.Menu) -> None:
        """Add the help menu with the version report action."""
        menu = tk.Menu(menubar, tearoff=False)
        menu.add_command(label='Report version information',
                         command=self.report_versions)
        menubar.add_cascade(label='Help', menu=menu)

    def build_body(self) -> None:
        """Build the main window body and start the log refresh."""
        tk.Label(self.root, text=APP_TITLE,
                 font=HEADING_FONT).pack(anchor='w', padx=12, pady=(12, 4))
        tk.Label(self.root, text=INSTRUCTIONS, wraplength=WRAP_LENGTH,
                 justify='left').pack(anchor='w', padx=12)
        self._add_warning(check_tcltk_version(self.root))
        self._add_warning(check_python_version())
        self._status = tk.StringVar(self.root, self._status_text())
        tk.Label(self.root, textvariable=self._status).pack(anchor='w',
                                                            padx=12, pady=4)
        self._build_log_view()
        self._schedule_refresh()

    def _add_warning(self, warning: Optional[str]) -> None:
        """Show a red warning label in the main window, when present."""
        if warning is None:
            return
        tk.Label(self.root, text=warning, fg='red', justify='left',
                 wraplength=WRAP_LENGTH).pack(anchor='w', padx=12, pady=4)

    def _build_log_view(self) -> None:
        """Build the read-only log view in the main window."""
        frame = tk.LabelFrame(self.root, text='Log (most recent messages)')
        frame.pack(fill='both', expand=True, padx=12, pady=8)
        text = tk.Text(frame, height=12, wrap='word', state='disabled')
        scroll = ttk.Scrollbar(frame, orient='vertical', command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        text.pack(side='left', fill='both', expand=True)
        self.log_view = text

    def _status_text(self) -> str:
        """Return the configuration status line for the main window."""
        if self.config is None:
            return 'No configuration loaded.'
        return f'Configuration loaded from {self.config_source}.'

    def _update_status(self) -> None:
        """Refresh the configuration status line, when it is shown."""
        if self._status is not None:
            self._status.set(self._status_text())

    def _refresh_log(self) -> None:
        """Copy the latest log lines into the read-only log view."""
        if self.log_view is None:
            return
        self.log_view.configure(state='normal')
        self.log_view.delete('1.0', 'end')
        self.log_view.insert('end', self.log.text())
        self.log_view.see('end')
        self.log_view.configure(state='disabled')

    def _schedule_refresh(self) -> None:
        """Refresh the log view and schedule the next refresh."""
        try:
            self._refresh_log()
            self.root.after(LOG_REFRESH_MS, self._schedule_refresh)
        except tk.TclError:
            pass


def _build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the GUI launcher."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-c', '--config', dest='config',
                        help='Teams configuration file to start with. '
                        'Without -c the file is found from $BACKLOGOPS_CFG, '
                        'else backlogops.cfg in $BACKLOGOPS_DIR, else '
                        '$HOME/.backlogops.cfg.')
    return parser


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
    app.build_body()
    root.mainloop()
