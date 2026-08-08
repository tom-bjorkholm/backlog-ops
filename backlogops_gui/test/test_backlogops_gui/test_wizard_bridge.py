#! /usr/local/bin/python3
"""Smoke test of a backlogops wizard over the packaged Tk bridge.

The graphical wizard is the wizard-tk-bridge package, which has its own
test suite, so this file only checks that the two fit together here: a
real WizardUiBridgeTk built the way the application builds it shows a
real backlogops wizard question in real Tk widgets, and the abort button
of that window reaches the wizard as the abandoned-wizard EOFError.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Optional
import pytest
from wizard_tk_bridge import WizardUiBridgeTk
from backlogops import NoTextIO, available_teams_wizard
from .gui_test_helpers import gui_root

ABORT_TEXT = 'Abort'
RETRY_MS = 50


def _abort_button(widget: tk.Misc) -> Optional[tk.Button]:
    """Return the abort button of the wizard window, if it is built yet."""
    if isinstance(widget, tk.Button) and widget.cget('text') == ABORT_TEXT:
        return widget
    for child in widget.winfo_children():
        found = _abort_button(child)
        if found is not None:
            return found
    return None


def _press_abort(root: tk.Tk) -> None:
    """Press the abort button, retrying until the question is on screen."""
    button = _abort_button(root)
    if button is None:
        root.after(RETRY_MS, lambda: _press_abort(root))
    else:
        button.invoke()


def test_wizard_abort() -> None:
    """Test aborting a wizard question asked through a real Tk bridge."""
    with gui_root() as root:
        bridge = WizardUiBridgeTk(root, log=NoTextIO())
        try:
            root.after(0, lambda: _press_abort(root))
            with pytest.raises(EOFError):
                available_teams_wizard(bridge)
        finally:
            bridge.close()
