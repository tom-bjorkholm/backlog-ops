#! /usr/local/bin/python3
"""Order the releases in Jira.

The orderer offers a handler that asks for a preset and an order source, then
reorders the Jira versions on a worker thread and hands the result back to the
GUI thread. It is available only when a configuration with Jira presets is
loaded. The order source is the release date, the order of the releases shown
in the window, or a list of names entered in the dialog.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable, Optional
from backlogops import (
    BacklogReleases, OrderedReleasesInJira, order_jira_rel_by_date,
    order_releases_in_jira)
from backlogops_gui.jira_base import JiraAction
from backlogops_gui.jira_dialogs import JiraOrderOptions, ask_jira_order


# pylint: disable-next=too-few-public-methods
class JiraOrderer(JiraAction):
    """Orders the releases in Jira by date, window order or a name list."""

    def order_action(self) -> Optional[Callable[
            [BacklogReleases, Callable[[OrderedReleasesInJira], None]],
            None]]:
        """Return the order-releases handler, or None when unavailable."""
        return self._order if self._available() else None

    def _order(self, data: BacklogReleases,
               on_done: Callable[[OrderedReleasesInJira], None]) -> None:
        """Ask for a preset and order source, then order in Jira."""
        options = ask_jira_order(self._app.root, self._presets())
        if options is None:
            return
        self._start(options.preset_name, 'Ordering releases in Jira',
                    lambda: self._order_worker(options, data, on_done))

    def _wanted_names(self, options: JiraOrderOptions,
                      data: BacklogReleases) -> list[str]:
        """Return the wanted order of names for a by-name order source."""
        if options.mode == 'window':
            return [release.name for release in data.releases]
        return options.names

    def _order_worker(self, options: JiraOrderOptions, data: BacklogReleases,
                      on_done: Callable[[OrderedReleasesInJira], None]
                      ) -> None:
        """Order the releases on a worker and schedule the GUI update."""
        name = options.preset_name

        def call() -> OrderedReleasesInJira:
            """Order the releases in Jira using the chosen order source."""
            if options.mode == 'date':
                return order_jira_rel_by_date(self._connections(), name,
                                              stderr_file=self._app.log)
            return order_releases_in_jira(self._connections(), name,
                                          self._wanted_names(options, data),
                                          stderr_file=self._app.log)

        def done(result: OrderedReleasesInJira) -> None:
            """Hand the result to the window and log the completed order."""
            summary = (f'Ordered {len(result.ordered)} releases in Jira; '
                       f'{len(result.not_in_jira)} not in Jira '
                       f"(preset '{name}').\n")
            self._finish(on_done, result, summary)
        self._dispatch('Could not order releases in Jira', name, call, done)
