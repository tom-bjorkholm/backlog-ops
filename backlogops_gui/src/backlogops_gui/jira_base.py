#! /usr/local/bin/python3
"""Shared behavior for the Jira operations of the application.

The Jira read, write and update operations all resolve a Jira connection
and materialize an encrypted API token before starting, run their network
call on a worker thread, and hand success or failure back to the GUI
thread. :class:`JiraAction` holds a reference to the running
:class:`~backlogops_gui.application.BacklogApp` and provides those shared
steps, so each concrete Jira collaborator only implements the call, the
success reporting and, where needed, the dialog that gathers its options.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import threading
import tkinter as tk
from typing import Callable, TypeVar, TYPE_CHECKING
from jira.exceptions import JIRAError
from backlogops import BacklogOpsConfig, JiraConnectConfig, JiraConnections
from backlogops_gui.jira_dialogs import ask_jira_passphrase

if TYPE_CHECKING:
    from backlogops_gui.application import BacklogApp

JIRA_ERRORS = (ValueError, TypeError, KeyError, RuntimeError, OSError,
               JIRAError)

_R = TypeVar('_R')


# pylint: disable-next=too-few-public-methods
class JiraAction:
    """Base for the Jira menu actions, sharing the app and worker steps."""

    def __init__(self, app: 'BacklogApp') -> None:
        """Store the application whose window, log and config are used."""
        self._app = app

    def _config(self) -> BacklogOpsConfig:
        """Return the active configuration, which the caller ensured is set."""
        config = self._app.config
        assert config is not None
        return config

    def _available(self) -> bool:
        """Return whether a configuration with Jira presets is loaded."""
        config = self._app.config
        return config is not None and bool(config.get_jira_config().presets)

    def _presets(self) -> list[str]:
        """Return the Jira preset names of the configuration, sorted."""
        return sorted(self._config().get_jira_config().presets)

    def _connections(self) -> JiraConnections:
        """Return the Jira connections of the configuration."""
        return JiraConnections(self._config().get_jira_config())

    def _jira_connection(self, preset_name: str) -> JiraConnectConfig:
        """Return the Jira connection used by the named preset."""
        jira_config = self._config().get_jira_config()
        preset = jira_config.get_preset(preset_name)
        return jira_config.connections[preset.connection_name]

    def _prepare_jira_token(self, preset_name: str) -> bool:
        """Materialize an encrypted Jira token before the worker starts."""
        connection = self._jira_connection(preset_name)
        if not connection.uses_encryption() or connection.has_cached_token():
            return True
        passphrase = ask_jira_passphrase(self._app.root)
        if passphrase is None:
            return False
        try:
            connection.get_token(lambda: passphrase, self._app.log)
        except JIRA_ERRORS as error:
            self._fail('Could not read Jira token', preset_name, str(error))
            return False
        return True

    def _start(self, preset_name: str, verb: str,
               worker: Callable[[], None]) -> None:
        """Prepare the token, log the start, and run the worker on a thread.

        ``verb`` is spliced into the "<verb> using preset '<name>'..." start
        message logged before the worker thread runs. Nothing runs when the
        token could not be materialized.
        """
        if not self._prepare_jira_token(preset_name):
            return
        self._app.log.write(f"{verb} using preset '{preset_name}'...\n")
        self._app.refresh_log()
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _dispatch(self, title: str, preset_name: str, call: Callable[[], _R],
                  done: Callable[[_R], None]) -> None:
        """Run the Jira call and hand its result to the GUI thread.

        A call raising one of the known Jira errors is reported under
        ``title`` for ``preset_name``; otherwise the result is passed to
        ``done``. Both run on the GUI thread if the main window still exists.
        """
        try:
            result = call()
        except JIRA_ERRORS as error:
            message = str(error)
            self._after(lambda: self._fail(title, preset_name, message))
            return
        self._after(lambda: done(result))

    def _after(self, callback: Callable[[], None]) -> None:
        """Schedule a GUI-thread callback if the main window still exists."""
        try:
            self._app.root.after(0, callback)
        except tk.TclError:
            pass

    def _fail(self, title: str, preset_name: str, message: str) -> None:
        """Log and report a failed Jira operation for one preset."""
        self._app.log.write(f"{title} preset '{preset_name}': {message}\n")
        self._app.show_error(title, message)

    def _finish(self, on_done: Callable[[_R], None], result: _R,
                summary: str) -> None:
        """Hand the result to the window and log a completion summary."""
        on_done(result)
        self._app.log.write(summary)
