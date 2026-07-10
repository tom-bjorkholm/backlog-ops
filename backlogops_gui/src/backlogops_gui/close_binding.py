#! /usr/local/bin/python3
"""Bind the close-window key to a secondary window's close action.

On macOS the Tk toolkit does not close a window when the user presses
Cmd-W, so every secondary window binds that key here. Cmd-W is bound on
every platform, where it is harmless without a Command key, and Ctrl-W is
added on Windows, its customary close-window shortcut. The bound action
defaults to destroying the window but may be the window's own cancel or
abort handler, so the key behaves exactly like the window close button.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
import tkinter as tk
from typing import Callable, Optional

CLOSE_ACCELERATOR = 'Command-W'


def _close_events() -> list[str]:
    """Return the key patterns that close a window on this platform."""
    if sys.platform.startswith('win'):
        return ['<Command-w>', '<Control-w>']
    return ['<Command-w>']


def _perform_close(win: tk.Toplevel,
                   on_close: Optional[Callable[[], None]]) -> str:
    """Run the window's close action and stop further event handling."""
    (win.destroy if on_close is None else on_close)()
    return 'break'


def bind_close(win: tk.Toplevel,
               on_close: Optional[Callable[[], None]] = None) -> None:
    """Bind the close-window key to run the window's close action.

    Args:
        win: The secondary window to close on the key press.
        on_close: The close action, defaulting to destroying the window.
            A window that cancels or aborts on close passes its own
            handler, so the key matches its window close button.
    """
    for event in _close_events():
        win.bind(event, lambda _event: _perform_close(win, on_close))
