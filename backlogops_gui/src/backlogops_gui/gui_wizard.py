#! /usr/local/bin/python3
"""Graphical bridge that drives the synchronous config wizard.

The backlog-ops configuration wizard asks its questions through a
:class:`WizardUiBridge`. This module provides :class:`TkWizardBridge`, a
concrete bridge that overrides every typed ask method of that base class
with a real Tkinter control, including the GUI-recommended ones: ask_path()
opens a native file or directory picker, and ask_form() shows a whole form
on one screen so the user answers related fields together in any order. All
questions are answered in one reused
:class:`~backlogops_gui.wizard_window.WizardWindow`, so the whole wizard
session happens in a single pop-up that does not jump around the display.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional, Sequence, TextIO
from pathlib import Path
import tkinter as tk
from tableio_cfg_json import AnswerFields, AskFields, PartialCheck, \
    PartialFormValidator, PathAskOptions, TableCell, TableColumn, \
    WizardUiBridge
from backlogops import NoTextIO
from backlogops_gui.wizard_window import WizardWindow


class TkWizardBridge(WizardUiBridge):
    """Bridge that answers wizard prompts in one reused Tkinter window."""

    def __init__(self, parent: tk.Misc, log: Optional[TextIO] = None) -> None:
        """Store the parent window and the optional diagnostics log.

        Args:
            parent: The window the wizard window is shown over.
            log: Stream that receives low-level wizard diagnostics.
        """
        self._parent = parent
        self._log = log
        self._window: Optional[WizardWindow] = None

    def ask_text(self, question: str, re_ask_reason: Optional[str] = None,
                 nullable: bool = False, *, default: Optional[str] = None,
                 sensitive: bool = False) -> Optional[str]:
        """Ask for free text; see WizardUiBridge.ask_text."""
        if sensitive and default is not None:
            raise ValueError('default is not allowed for sensitive input')
        return self._window_obj().ask_text(question, re_ask_reason, nullable,
                                           default, sensitive)

    # pylint: disable-next=too-many-arguments
    def ask_int(self, question: str, re_ask_reason: Optional[str] = None, *,
                nullable: bool = False, min_value: Optional[int] = None,
                max_value: Optional[int] = None,
                default: Optional[int] = None) -> Optional[int]:
        """Ask for an integer within optional bounds; see ask_int."""
        return self._window_obj().ask_int(question, re_ask_reason, nullable,
                                          min_value, max_value, default)

    def ask_path(self, question: str, re_ask_reason: Optional[str] = None, *,
                 options: Optional[PathAskOptions] = None) -> Optional[Path]:
        """Ask for a path with a native file or directory picker."""
        path_options = PathAskOptions() if options is None else options
        return self._window_obj().ask_path(question, path_options,
                                           re_ask_reason)

    def ask_yes_no(self, question: str, default: bool,
                   re_ask_reason: Optional[str] = None) -> bool:
        """Ask a yes/no question with dedicated yes and no buttons."""
        return self._window_obj().ask_yes_no(question, default, re_ask_reason)

    def ask_choice(self, question: str, *, choices: Sequence[str],
                   default: Optional[str] = None,
                   re_ask_reason: Optional[str] = None) -> str:
        """Ask the user to pick one choice from a single-selection list."""
        return self._window_obj().ask_choice(question, choices, default,
                                             re_ask_reason)

    # pylint: disable-next=too-many-arguments
    def ask_multi(self, question: str, *, choices: Sequence[str],
                  default: Optional[Sequence[str]] = None, min_select: int = 0,
                  max_select: Optional[int] = None,
                  re_ask_reason: Optional[str] = None) -> list[str]:
        """Ask the user to pick several choices from a multi-selection list."""
        return self._window_obj().ask_multi(question, choices, default,
                                            min_select, max_select,
                                            re_ask_reason)

    # pylint: disable-next=too-many-arguments
    def ask_table(self, columns: Sequence[TableColumn],
                  cells: list[list[TableCell]], question: str, *,
                  re_ask_reason: Optional[str] = None,
                  partial_check: Optional[PartialCheck] = None,
                  min_rows: Optional[int] = None,
                  max_rows: Optional[int] = None) -> list[list[Optional[str]]]:
        """Ask the user to fill an editable table of the given rows.

        With both ``min_rows`` and ``max_rows`` given the table has a
        variable number of rows: add-row and remove-row buttons grow the
        table up to ``max_rows`` and shrink it down to ``min_rows``.
        Otherwise the rows given in ``cells`` are fixed and only filled.
        """
        return self._window_obj().ask_table(columns, cells, question,
                                            re_ask_reason, partial_check,
                                            min_rows, max_rows)

    def ask_form(self, long_question: str, ask_fields: AskFields, *,
                 re_ask_reason: Optional[str] = None,
                 partial_validator: Optional[PartialFormValidator] = None) \
            -> AnswerFields:
        """Ask a whole form on one screen; see WizardUiBridge.ask_form."""
        return self._window_obj().ask_form(long_question, ask_fields,
                                           re_ask_reason, partial_validator)

    def show(self, message: str) -> None:
        """Show an informational message to the user."""
        self._window_obj().show(message)

    def error_file(self) -> TextIO:
        """Return the stream used for low-level wizard diagnostics."""
        return self._log if self._log is not None else NoTextIO()

    def close(self) -> None:
        """Close the wizard window when one was opened."""
        if self._window is not None:
            self._window.close()
            self._window = None

    def _window_obj(self) -> WizardWindow:
        """Return the wizard window, creating it on first use."""
        if self._window is None:
            self._window = WizardWindow(self._parent)
        return self._window
