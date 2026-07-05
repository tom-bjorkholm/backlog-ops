#! /usr/local/bin/python3
"""Update the shown releases and backlog in Jira.

The updater offers a handler for updating the shown releases and a handler
for updating the shown backlog, each available only when a configuration
with Jira presets is loaded. A handler asks for a preset and the update
options, then updates on a worker thread and hands the result back to the
GUI thread. The backlog-update dialog offers the columns each preset can
update, taken from the library.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable, Optional
from backlogops import (
    BacklogReleases, LinkUpdate, UpdatedBacklogInJira, UpdatedReleasesInJira,
    updatable_backlog_fields, update_backlog_in_jira, update_releases_in_jira)
from backlogops_gui.jira_base import JiraAction
from backlogops_gui.jira_dialogs import (
    JiraBacklogUpdateOptions, JiraReleaseUpdateOptions, ask_backlog_update,
    ask_release_update)


class JiraUpdater(JiraAction):
    """Updates the shown releases and backlog in Jira."""

    def releases_action(self) -> Optional[Callable[
            [BacklogReleases, Callable[[UpdatedReleasesInJira], None]],
            None]]:
        """Return the update-releases handler, or None when unavailable."""
        return self._update_releases if self._available() else None

    def backlog_action(self) -> Optional[Callable[
            [BacklogReleases, Callable[[UpdatedBacklogInJira], None]],
            None]]:
        """Return the update-backlog handler, or None when unavailable."""
        return self._update_backlog if self._available() else None

    def _update_releases(
            self, data: BacklogReleases,
            on_done: Callable[[UpdatedReleasesInJira], None]) -> None:
        """Ask for a preset, mode and releases, then update them in Jira."""
        names = [release.name for release in data.releases]
        options = ask_release_update(self._app.root, self._presets(), names)
        if options is None:
            return
        self._start(options.preset_name, 'Updating releases in Jira',
                    lambda: self._releases_worker(options, data, on_done))

    def _releases_worker(
            self, options: JiraReleaseUpdateOptions, data: BacklogReleases,
            on_done: Callable[[UpdatedReleasesInJira], None]) -> None:
        """Update the releases on a worker and schedule the GUI update."""
        name = options.preset_name
        chosen = set(options.selected)
        selected = [release for release in data.releases
                    if release.name in chosen]

        def call() -> UpdatedReleasesInJira:
            """Update the selected releases in Jira."""
            return update_releases_in_jira(self._connections(), name, selected,
                                           on_missing_key=options.on_missing,
                                           stderr_file=self._app.log)

        def done(result: UpdatedReleasesInJira) -> None:
            """Hand the result to the window and log the completed update."""
            summary = (
                f"Updated {len(result.updated)} releases in Jira; "
                f"{len(result.already_correct)} already correct; "
                f"{len(result.ignored)} ignored; {len(result.added)} "
                f"added (preset '{name}').\n")
            self._finish(on_done, result, summary)
        self._dispatch('Could not update releases in Jira', name, call, done)

    def _preset_fields(self) -> dict[str, list[str]]:
        """Return each preset name mapped to its updatable backlog fields."""
        connections = self._connections()
        return {name: updatable_backlog_fields(connections, name)
                for name in self._config().get_jira_config().presets}

    def _update_backlog(
            self, data: BacklogReleases,
            on_done: Callable[[UpdatedBacklogInJira], None]) -> None:
        """Ask for a preset, fields and mode, then update the backlog."""
        options = ask_backlog_update(self._app.root, self._preset_fields())
        if options is None:
            return
        self._start(options.preset_name, 'Updating backlog in Jira',
                    lambda: self._backlog_worker(options, data, on_done))

    def _backlog_worker(
            self, options: JiraBacklogUpdateOptions, data: BacklogReleases,
            on_done: Callable[[UpdatedBacklogInJira], None]) -> None:
        """Update the backlog on a worker and schedule the GUI update."""
        config = self._config()
        name = options.preset_name
        link_update = (LinkUpdate.RECONCILE if options.reconcile_links
                       else LinkUpdate.ADD_MISSING)

        def call() -> UpdatedBacklogInJira:
            """Update the backlog in Jira with the chosen options."""
            return update_backlog_in_jira(
                self._connections(), name, data.backlog,
                on_missing_key=options.on_missing,
                fields_to_update=options.fields, link_update=link_update,
                levels=config.get_levels(),
                status_map=config.get_status_input_map(),
                stderr_file=self._app.log)

        def done(result: UpdatedBacklogInJira) -> None:
            """Hand the result to the window and log the completed update."""
            summary = (
                f"Updated {len(result.updated)} backlog items in Jira; "
                f"{len(result.already_correct)} already correct; "
                f"{len(result.ignored)} ignored; "
                f"{len(result.added.stored)} added "
                f"(preset '{name}').\n")
            self._finish(on_done, result, summary)
        self._dispatch('Could not update backlog in Jira', name, call, done)
