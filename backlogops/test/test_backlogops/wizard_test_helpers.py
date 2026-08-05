#! /usr/local/bin/python3
"""Shared helpers and scripted-answer constants for the wizard tests.

The wizard tests drive the console bridge with a scripted list of answers.
These helpers build such a bridge and run the workforce and full-config
wizards, and the constants name the common blocks of blank answers that
keep the pre-filled defaults of the company work-hours form and the level,
status and rename tables. :class:`TableScript` is a bridge that returns
queued raw tables so the whole-table re-ask paths can be exercised.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from typing import Optional, Sequence, TextIO
from wizard_ui_bridge import TableCell, TableColumn, WizardUiBridge, \
    WizardUiBridgeConsole
from backlogops.available_teams import AvailableTeams
from backlogops.backlog_ops_config import BacklogOpsConfig
from backlogops.backlog_ops_wizard import (
    available_teams_wizard, backlog_ops_wizard, _WORKFORCE_HEAD,
    _INPUT_PRESETS_HEAD, _OUTPUT_PRESETS_HEAD, _LEVELS_HEAD, _STATUS_MAP_HEAD,
    _GUI_DISPLAY_HEAD, _JIRA_HEAD)

GUI_KEEP = ['']
"""A blank answer that keeps the default GUI level display (both)."""

MAPS_KEEP = ['', '']
"""Blank answers that accept a pre-filled backlog and releases map."""

GUI_MAPS_KEEP = MAPS_KEEP + GUI_KEEP
"""Accept both GUI rename tables, then keep the GUI level display."""

JIRA_SKIP = ['0', '0', '0', '0']
"""Zero Jira connections, backlog and release column maps and issue-type
maps, which skips the presets too."""

LEVELS_KEEP = ['']
"""A blank answer that accepts the pre-filled default levels table."""

STATUS_KEEP = ['']
"""A blank answer that accepts the pre-filled default status map."""

SCHED = [''] * 7
"""Blank answers that keep the seven default daily work-hours fields."""

COMPANY = SCHED + ['']
"""The schedule kept, then a blank that leaves no company-holiday periods."""

CSV_OPTS = [''] * 7
"""Blank answers for the CSV format encoding and six option cells."""

CONFIG_HEADS = [
    _WORKFORCE_HEAD, _INPUT_PRESETS_HEAD, _OUTPUT_PRESETS_HEAD,
    _LEVELS_HEAD, _STATUS_MAP_HEAD, _GUI_DISPLAY_HEAD, _JIRA_HEAD]
"""The full-config wizard stage headings, in collection order."""


def bridge(answers: list[str]) -> WizardUiBridgeConsole:
    """Return a console bridge scripted with the given answers."""
    stdin = io.StringIO('\n'.join(answers) + '\n')
    return WizardUiBridgeConsole(io.StringIO(), stdin, io.StringIO())


def run_workforce(answers: list[str]) -> AvailableTeams:
    """Run the workforce wizard with scripted answers and return it."""
    return available_teams_wizard(bridge(answers))


def run_config(answers: list[str]) -> tuple[BacklogOpsConfig, str]:
    """Run the config wizard, returning the config and the stderr text."""
    stderr = io.StringIO()
    stdin = io.StringIO('\n'.join(answers) + '\n')
    scripted = WizardUiBridgeConsole(io.StringIO(), stdin, stderr)
    return backlog_ops_wizard(scripted), stderr.getvalue()


def config_stdout(answers: list[str]) -> str:
    """Run the config wizard and return what was shown on stdout."""
    stdout = io.StringIO()
    stdin = io.StringIO('\n'.join(answers) + '\n')
    backlog_ops_wizard(WizardUiBridgeConsole(stdout, stdin, io.StringIO()))
    return stdout.getvalue()


def teams_stdout(answers: list[str]) -> str:
    """Run the workforce wizard and return what was shown on stdout."""
    stdout = io.StringIO()
    stdin = io.StringIO('\n'.join(answers) + '\n')
    available_teams_wizard(WizardUiBridgeConsole(stdout, stdin, io.StringIO()))
    return stdout.getvalue()


class TableScript(WizardUiBridge):
    """A bridge that returns queued raw tables for each ask_table call.

    It hands the wizard an invalid table first and a valid one next,
    which the real console bridge's per-cell checks never produce, so the
    whole-table re-ask path of the read helpers can be exercised.
    """

    def __init__(self, tables: list[list[list[Optional[str]]]]) -> None:
        """Store the tables to return in order and a diagnostics sink."""
        self._tables = tables
        self._index = 0
        self._errors = io.StringIO()
        self.seen: list[list[list[TableCell]]] = []

    def ask_table(self, columns: Sequence[TableColumn],
                  cells: list[list[TableCell]], question: str,
                  **kwargs: object) -> list[list[Optional[str]]]:
        """Return the next queued table, ignoring the prompt details."""
        _ = (columns, question, kwargs)
        self.seen.append(cells)
        table = self._tables[self._index]
        self._index += 1
        return table

    def error_file(self) -> TextIO:
        """Return the diagnostics stream used for level validation."""
        return self._errors

    def show(self, message: str) -> None:
        """Ignore any message shown while a table is being re-asked."""
        _ = message

    def ask_choice(self, question: str, *, choices: Sequence[str],
                   default: Optional[str] = None,
                   re_ask_reason: Optional[str] = None) -> str:
        """Abstract in base class, but not used in these tests."""
        _ = (question, choices, default, re_ask_reason)
        assert False, "ask_choice not used in these tests"
        return ''  # pylint: disable=unreachable

    # pylint: disable-next=too-many-arguments
    def ask_multi(self, question: str, *, choices: Sequence[str],
                  default: Optional[Sequence[str]] = None, min_select: int = 0,
                  max_select: Optional[int] = None,
                  re_ask_reason: Optional[str] = None) -> list[str]:
        """Abstract in base class, but not used in these tests."""
        _ = (question, choices, default, min_select, max_select, re_ask_reason)
        assert False, "ask_multi not used in these tests"
        return []  # pylint: disable=unreachable

    def ask_text(self, question: str, re_ask_reason: Optional[str] = None,
                 nullable: bool = False, *, default: Optional[str] = None,
                 sensitive: bool = False) -> Optional[str]:
        """Abstract in base class, but not used in these tests."""
        _ = (question, re_ask_reason, nullable, default, sensitive)
        assert False, "ask_text not used in these tests"
        return ''  # pylint: disable=unreachable

    def ask_yes_no(self, question: str, default: bool,
                   re_ask_reason: Optional[str] = None) -> bool:
        """Abstract in base class, but not used in these tests."""
        _ = (question, default, re_ask_reason)
        assert False, "ask_yes_no not used in these tests"
        return False  # pylint: disable=unreachable
