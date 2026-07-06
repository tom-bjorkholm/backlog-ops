#! /usr/local/bin/python3
"""Move issues to the front or end of a Jira backlog by rank.

The ranker offers a handler that asks for a preset, the keys to move and
which end to move them to, then ranks them in Jira on a worker thread and
hands the result back to the GUI thread. It is available only when a
configuration with Jira presets is loaded. The backlog and the current
ranking come from Jira through the preset, not from the shown backlog, so
the handler does not need the shown data.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable, Optional
from backlogops import RankedInJira, jira_rank_move_keys
from backlogops_gui.jira_base import JiraAction
from backlogops_gui.jira_dialogs import JiraRankOptions, ask_jira_rank


# pylint: disable-next=too-few-public-methods
class JiraRanker(JiraAction):
    """Moves issues to the front or end of a Jira backlog by rank."""

    def rank_action(self) -> Optional[Callable[
            [Callable[[RankedInJira], None]], None]]:
        """Return the rank handler, or None when it is unavailable."""
        return self._rank if self._available() else None

    def _rank(self, on_done: Callable[[RankedInJira], None]) -> None:
        """Ask for a preset, filter, keys and end, then rank in Jira."""
        options = ask_jira_rank(self._app.root, self._preset_filters(),
                                self._app.log)
        if options is None:
            return
        self._start(options.preset_name, 'Ranking items in Jira',
                    lambda: self._rank_worker(options, on_done))

    def _rank_worker(self, options: JiraRankOptions,
                     on_done: Callable[[RankedInJira], None]) -> None:
        """Rank the items on a worker and schedule the GUI update."""
        config = self._config()
        name = options.preset_name
        levels = config.get_levels()
        status = config.get_status_input_map()

        def call() -> RankedInJira:
            """Move the keys to the chosen end of the Jira backlog."""
            return jira_rank_move_keys(self._connections(), name, options.keys,
                                       filter_override=options.issue_filter,
                                       move_to_end=options.move_to_end,
                                       levels=levels, status_map=status,
                                       stderr_file=self._app.log)

        def done(result: RankedInJira) -> None:
            """Hand the result to the window and log the finished ranking."""
            summary = (f'Ranked {len(result.keys_ranked_ok)} items in Jira; '
                       f'{len(result.keys_not_in_jira)} not in Jira, '
                       f'{len(result.keys_not_in_filter)} not in filter '
                       f"(preset '{name}').\n")
            self._finish(on_done, result, summary)
        self._dispatch('Could not rank in Jira', name, call, done)
