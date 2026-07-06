#! /usr/local/bin/python3
"""Read a backlog and its releases from Jira into a new window.

The reader asks for a Jira preset and an issue filter, then reads on a
worker thread and opens the result in a new backlog window on the GUI
thread. Jira data that is not fully consistent still opens, but with a
warning that disables the backlog operations, so the user can inspect and
save it without acting on inconsistent data.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional
from backlogops import BacklogReleases, read_jira_from_config
from backlogops_gui.jira_base import JiraAction
from backlogops_gui.jira_dialogs import JiraReadOptions, ask_jira_read_options

CONSISTENCY_ERRORS = (ValueError, TypeError, KeyError)
JIRA_WARNING = (
    'The data read from Jira is not fully consistent. Backlog operations '
    'are disabled except save to file. See the main log for details.')


# pylint: disable-next=too-few-public-methods
class JiraReader(JiraAction):
    """Reads a backlog from Jira into a new window."""

    def read_backlog(self) -> None:
        """Read a backlog from Jira into a new window."""
        if self._app.config is None:
            self._app.show_error('No configuration',
                                 'There is no configuration to read Jira '
                                 'from.')
            return
        filters = self._preset_filters()
        if not filters:
            self._app.show_error('No Jira presets',
                                 'There are no Jira presets in the '
                                 'configuration.')
            return
        options = ask_jira_read_options(self._app.root, filters)
        if options is None:
            return
        self._start(options.preset_name, 'Reading from Jira',
                    lambda: self._read_worker(options))

    def _read_worker(self, options: JiraReadOptions) -> None:
        """Read Jira data on a worker and schedule the GUI update."""
        name = options.preset_name

        def call() -> tuple[BacklogReleases, Optional[str]]:
            """Read the Jira data with any consistency warning."""
            data = read_jira_from_config(self._config(), name,
                                         filter_override=options.issue_filter,
                                         stderr_file=self._app.log)
            return data, self._consistency_warning(data)

        def done(result: tuple[BacklogReleases, Optional[str]]) -> None:
            """Open the Jira backlog and report the completed read."""
            data, warning = result
            self._app.open_backlog(data, f'Jira: {name}', warning)
            self._app.log.write(
                f"Read {len(data.backlog)} backlog items and "
                f"{len(data.releases)} releases from Jira preset "
                f"'{name}'.\n")
            self._app.show_info('Read from Jira',
                                f"Finished reading from Jira preset "
                                f"'{name}'.")
        self._dispatch('Could not read from Jira', name, call, done)

    def _consistency_warning(self, data: BacklogReleases) -> Optional[str]:
        """Return a warning if the Jira data is not fully consistent."""
        try:
            data.check_consistency(self._app.log)
        except CONSISTENCY_ERRORS:
            self._app.log.write(f'{JIRA_WARNING}\n')
            return JIRA_WARNING
        return None
