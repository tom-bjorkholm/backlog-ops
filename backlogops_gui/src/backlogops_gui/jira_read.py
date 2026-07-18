#! /usr/local/bin/python3
"""Read a backlog and its releases from Jira into a new window.

The reader asks for a Jira preset and an issue filter, then reads on a
worker thread and opens the result in a new backlog window on the GUI
thread. Jira data that is not fully consistent still opens, but with a
warning that disables the backlog operations, so the user can inspect and
save it without acting on inconsistent data. The window's "Read again"
button re-reads the same preset and filter and updates the window in place.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable, Optional
from backlogops import BacklogReleases, read_jira_from_config
from backlogops_gui.backlog_window import BacklogSource, current_time
from backlogops_gui.jira_base import JiraAction
from backlogops_gui.jira_dialogs import ask_jira_read_options

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
        self._read(options.preset_name, options.issue_filter, self._open_new)

    def _read(self, name: str, issue_filter: str, deliver: Callable[
            [str, str, BacklogReleases, Optional[str]], None]) -> None:
        """Read Jira on a worker and hand the result to ``deliver``.

        ``deliver`` runs on the GUI thread with the preset name, the filter
        used, the data and any consistency warning.
        """
        self._start(name, 'Reading from Jira',
                    lambda: self._worker(name, issue_filter, deliver))

    def _worker(self, name: str, issue_filter: str, deliver: Callable[
            [str, str, BacklogReleases, Optional[str]], None]) -> None:
        """Run the Jira read and schedule delivery on the GUI thread."""
        def call() -> tuple[BacklogReleases, Optional[str]]:
            """Read the Jira data with any consistency warning."""
            data = read_jira_from_config(self._config(), name,
                                         filter_override=issue_filter,
                                         stderr_file=self._app.log)
            return data, self._consistency_warning(data)

        def done(result: tuple[BacklogReleases, Optional[str]]) -> None:
            """Deliver the read data and warning."""
            data, warning = result
            deliver(name, issue_filter, data, warning)
        self._dispatch('Could not read from Jira', name, call, done)

    def _open_new(self, name: str, issue_filter: str, data: BacklogReleases,
                  warning: Optional[str]) -> None:
        """Open a new window on the Jira data and report the read."""
        source = BacklogSource(kind='jira', read_time=current_time(),
                               preset_name=name, issue_filter=issue_filter)
        self._app.open_backlog(data, f'Jira: {name}', warning, source=source,
                               reload=self._reload(name, issue_filter))
        self._app.log.write(
            f"Read {len(data.backlog)} backlog items and "
            f"{len(data.releases)} releases from Jira preset '{name}'.\n")
        self._app.show_info('Read from Jira',
                            f"Finished reading from Jira preset '{name}'.")

    def _reload(self, name: str, issue_filter: str) -> Callable[
            [Callable[[BacklogReleases, Optional[str]], None]], None]:
        """Return a reload that re-reads the same preset and filter."""
        def reload(apply: Callable[[BacklogReleases, Optional[str]], None]
                   ) -> None:
            """Re-read from Jira and apply the fresh data in place."""
            def deliver(_name: str, _filter: str, data: BacklogReleases,
                        warning: Optional[str]) -> None:
                """Apply the re-read data and warning to the window."""
                apply(data, warning)
            self._read(name, issue_filter, deliver)
        return reload

    def _consistency_warning(self, data: BacklogReleases) -> Optional[str]:
        """Return a warning if the Jira data is not fully consistent."""
        try:
            data.check_consistency(self._app.log)
        except CONSISTENCY_ERRORS:
            self._app.log.write(f'{JIRA_WARNING}\n')
            return JIRA_WARNING
        return None
