#! /usr/local/bin/python3
"""The Jira read, write and update collaborators of the application.

The Jira menu actions of a backlog window are split across three
collaborators so each stays focused as the Jira support grows.
:class:`JiraActions` groups them behind one attribute of the application,
so the application talks to ``self.jira.reader``, ``self.jira.writer`` and
``self.jira.updater``.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import TYPE_CHECKING
from backlogops_gui.jira_read import JiraReader
from backlogops_gui.jira_write import JiraWriter
from backlogops_gui.jira_update import JiraUpdater

if TYPE_CHECKING:
    from backlogops_gui.application import BacklogApp


# pylint: disable-next=too-few-public-methods
class JiraActions:
    """Groups the Jira read, write and update collaborators."""

    def __init__(self, app: 'BacklogApp') -> None:
        """Create the reader, writer and updater for the application."""
        self.reader = JiraReader(app)
        self.writer = JiraWriter(app)
        self.updater = JiraUpdater(app)
