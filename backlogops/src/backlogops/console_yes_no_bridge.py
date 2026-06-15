#! /usr/local/bin/python3
"""Console wizard bridge that adds yes/no questions.

The workforce wizard asks yes/no questions through a
:class:`YesNoUiBridge`. This module provides the console implementation of
that bridge, built on the text-based ``WizardUiBridgeConsole`` of
``tableio_cfg_json``, so a command-line program can drive the wizard. A yes
or no answer is read as free text such as ``y`` or ``no``, and an empty
answer chooses the default.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional
from tableio_cfg_json import WizardUiBridgeConsole
from backlogops.available_teams_wizard import YesNoUiBridge


class ConsoleYesNoUiBridge(WizardUiBridgeConsole, YesNoUiBridge):
    """Console wizard bridge that asks yes/no questions as free text."""

    def ask_yes_no(self, question: str, default: bool) -> bool:
        """Ask a yes/no question, returning ``default`` for an empty answer.

        Args:
            question: The yes/no question to ask.
            default: The value to use when the user gives an empty answer.

        Returns:
            The user's choice as a boolean.
        """
        hint = 'Y/n' if default else 'y/N'
        re_ask: Optional[str] = None
        while True:
            answer = self.ask(f'{question} ({hint})', re_ask)
            text = answer if isinstance(answer, str) else str(answer)
            if text == '':
                return default
            lowered = text.strip().lower()
            if lowered in ('y', 'yes'):
                return True
            if lowered in ('n', 'no'):
                return False
            re_ask = "Please answer 'yes' or 'no'."
