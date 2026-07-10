#! /usr/local/bin/python3
"""The Jira read, write and update collaborators of the application.

The Jira menu actions of a backlog window are split across focused
collaborators so each stays focused as the Jira support grows.
:class:`JiraActions` groups them behind one attribute of the application,
so the application talks to ``self.jira.reader``, ``self.jira.writer``,
``self.jira.updater``, ``self.jira.ranker``, ``self.jira.renamer`` and
``self.jira.orderer``.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import TYPE_CHECKING
from backlogops_gui.jira_read import JiraReader
from backlogops_gui.jira_write import JiraWriter
from backlogops_gui.jira_update import JiraUpdater
from backlogops_gui.jira_rank import JiraRanker
from backlogops_gui.jira_rename import JiraRenamer
from backlogops_gui.jira_order import JiraOrderer

if TYPE_CHECKING:
    from backlogops_gui.application import BacklogApp


# pylint: disable-next=too-few-public-methods
class JiraActions:
    """Groups the Jira read, write, update, rank, rename and order actions."""

    def __init__(self, app: 'BacklogApp') -> None:
        """Create the Jira collaborators for the app."""
        self.reader = JiraReader(app)
        self.writer = JiraWriter(app)
        self.updater = JiraUpdater(app)
        self.ranker = JiraRanker(app)
        self.renamer = JiraRenamer(app)
        self.orderer = JiraOrderer(app)
