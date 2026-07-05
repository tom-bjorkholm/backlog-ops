#! /usr/local/bin/python3
"""Add a shown backlog and its releases to Jira.

The writer offers a handler for adding the shown backlog and a handler for
adding the shown releases, each available only when a configuration with
Jira presets is loaded. A handler asks for a write preset and whether to
skip items whose key already exists, then adds on a worker thread and
hands the result back to the GUI thread.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable, Optional
from backlogops import (
    AddedReleasesToJira, AddedToJira, BacklogReleases, OnExistingKey,
    add_backlog_to_jira, add_releases_to_jira)
from backlogops_gui.jira_base import JiraAction
from backlogops_gui.jira_dialogs import (
    JiraWriteOptions, ask_jira_write_options)


class JiraWriter(JiraAction):
    """Adds a shown backlog and its releases to Jira."""

    def backlog_action(self) -> Optional[Callable[
            [BacklogReleases, Callable[[AddedToJira], None]], None]]:
        """Return the add-backlog handler, or None when it is unavailable."""
        return self._add_backlog if self._available() else None

    def releases_action(self) -> Optional[Callable[
            [BacklogReleases, Callable[[AddedReleasesToJira], None]], None]]:
        """Return the add-releases handler, or None when unavailable."""
        return self._add_releases if self._available() else None

    def _ask(self) -> Optional[JiraWriteOptions]:
        """Ask for the write preset and skip-existing choice."""
        return ask_jira_write_options(self._app.root, self._presets())

    def _add_backlog(self, data: BacklogReleases,
                     on_done: Callable[[AddedToJira], None]) -> None:
        """Ask for a preset and add the shown backlog to Jira."""
        options = self._ask()
        if options is None:
            return
        self._start(options.preset_name, 'Adding backlog to Jira',
                    lambda: self._backlog_worker(options, data, on_done))

    def _backlog_worker(self, options: JiraWriteOptions, data: BacklogReleases,
                        on_done: Callable[[AddedToJira], None]) -> None:
        """Add the backlog on a worker and schedule the GUI update."""
        config = self._config()
        name = options.preset_name
        mode = (OnExistingKey.SKIP if options.skip_existing
                else OnExistingKey.RAISE)

        def call() -> AddedToJira:
            """Add the backlog to Jira with the chosen skip policy."""
            return add_backlog_to_jira(
                self._connections(), name, data.backlog, on_existing_key=mode,
                levels=config.get_levels(),
                status_map=config.get_status_input_map(),
                stderr_file=self._app.log)

        def done(result: AddedToJira) -> None:
            """Hand the result to the window and log the completed write."""
            summary = (f"Added {len(result.stored)} backlog items to Jira; "
                       f"{len(result.already_present)} already present "
                       f"(preset '{name}').\n")
            self._finish(on_done, result, summary)
        self._dispatch('Could not add to Jira', name, call, done)

    def _add_releases(self, data: BacklogReleases,
                      on_done: Callable[[AddedReleasesToJira], None]) -> None:
        """Ask for a preset and add the shown releases to Jira."""
        options = self._ask()
        if options is None:
            return
        self._start(options.preset_name, 'Adding releases to Jira',
                    lambda: self._releases_worker(options, data, on_done))

    def _releases_worker(
            self, options: JiraWriteOptions, data: BacklogReleases,
            on_done: Callable[[AddedReleasesToJira], None]) -> None:
        """Add the releases on a worker and schedule the GUI update."""
        name = options.preset_name
        mode = (OnExistingKey.SKIP if options.skip_existing
                else OnExistingKey.RAISE)

        def call() -> AddedReleasesToJira:
            """Add the releases to Jira with the chosen skip policy."""
            return add_releases_to_jira(self._connections(), name,
                                        data.releases, on_existing_key=mode,
                                        stderr_file=self._app.log)

        def done(result: AddedReleasesToJira) -> None:
            """Hand the result to the window and log the completed write."""
            summary = (f"Added {len(result.stored)} releases to Jira; "
                       f"{len(result.already_present)} already present "
                       f"(preset '{name}').\n")
            self._finish(on_done, result, summary)
        self._dispatch('Could not add releases to Jira', name, call, done)
