#! /usr/local/bin/python3
"""Rename the shown releases in Jira.

The renamer offers a handler that asks for a preset and a new name per shown
release, then renames the matching Jira versions on a worker thread and hands
the result back to the GUI thread. It is available only when a configuration
with Jira presets is loaded. The shown release names are the old names; a
blank entry keeps a release unchanged.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable, Optional
from backlogops import (
    BacklogReleases, RenamedReleasesInJira, rename_releases_in_jira)
from backlogops_gui.jira_base import JiraAction
from backlogops_gui.jira_dialogs import JiraRenameOptions, ask_jira_rename


# pylint: disable-next=too-few-public-methods
class JiraRenamer(JiraAction):
    """Renames the shown releases in Jira."""

    def rename_action(self) -> Optional[Callable[
            [BacklogReleases, Callable[[RenamedReleasesInJira], None]],
            None]]:
        """Return the rename-releases handler, or None when unavailable."""
        return self._rename if self._available() else None

    def _rename(self, data: BacklogReleases,
                on_done: Callable[[RenamedReleasesInJira], None]) -> None:
        """Ask for a preset and new names, then rename in Jira."""
        names = [release.name for release in data.releases]
        options = ask_jira_rename(self._app.root, self._presets(), names)
        if options is None:
            return
        self._start(options.preset_name, 'Renaming releases in Jira',
                    lambda: self._rename_worker(options, on_done))

    def _rename_worker(self, options: JiraRenameOptions,
                       on_done: Callable[[RenamedReleasesInJira], None]
                       ) -> None:
        """Rename the releases on a worker and schedule the GUI update."""
        name = options.preset_name

        def call() -> RenamedReleasesInJira:
            """Rename the versions named by the old names in Jira."""
            return rename_releases_in_jira(self._connections(), name,
                                           options.renames,
                                           stderr_file=self._app.log)

        def done(result: RenamedReleasesInJira) -> None:
            """Hand the result to the window and log the completed rename."""
            summary = (f'Renamed {len(result.renamed)} releases in Jira; '
                       f'{len(result.missing)} not in Jira, '
                       f'{len(result.collisions)} name collisions '
                       f"(preset '{name}').\n")
            self._finish(on_done, result, summary)
        self._dispatch('Could not rename releases in Jira', name, call, done)
