#! /usr/local/bin/python3
"""Shared helpers for backlog GUI tests."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from contextlib import contextmanager
from typing import Callable, Iterator, Optional
import pytest


def root_or_skip() -> tk.Tk:
    """Return a withdrawn Tk root, or skip when no display is available."""
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip('no display available')
    root.withdraw()
    return root


@contextmanager
def gui_root() -> Iterator[tk.Tk]:
    """Yield a withdrawn Tk root and destroy it afterwards.

    This factors out the create-try-finally-destroy boilerplate the widget
    tests share; the test body runs inside the ``with`` block. The test is
    skipped when no display is available.
    """
    root = root_or_skip()
    try:
        yield root
    finally:
        root.destroy()


def press_close(win: tk.Toplevel) -> None:
    """Send a Cmd-W key press to a window so its close binding fires.

    The window is realized with ``update`` first, and the event is
    delivered synchronously with ``when='now'`` so the bound handler runs
    before this call returns. This delivers to a normal top-level window;
    a transient window would need forced focus, which is avoided here as
    it can crash Tk during automated runs, so transient windows verify
    the binding through :class:`CloseSpy` instead.
    """
    win.update()
    win.event_generate('<Command-w>', when='now')


# pylint: disable-next=too-few-public-methods
class CloseSpy:
    """Record the windows and actions passed to a patched ``bind_close``.

    A transient window cannot receive a synthetic key press without forced
    focus, so its test replaces ``bind_close`` with this spy and checks
    that the window wires the intended close action.
    """

    def __init__(self) -> None:
        """Start with no recorded close bindings."""
        self.calls: list[tuple[tk.Misc, Optional[Callable[[], None]]]] = []

    def __call__(self, win: tk.Misc,
                 on_close: Optional[Callable[[], None]] = None) -> None:
        """Record one ``bind_close`` call and its close action."""
        self.calls.append((win, on_close))


class MsgRecorder:
    """Record Tk message-box calls made through it."""

    def __init__(self) -> None:
        """Start with an empty record of calls."""
        self.calls: list[tuple[str, str]] = []

    def showerror(self, title: str, message: str, parent: object) -> None:
        """Record a shown error message."""
        assert parent is not None
        self.calls.append((title, message))

    def showinfo(self, title: str, message: str, parent: object) -> None:
        """Record a shown informational message."""
        assert parent is not None
        self.calls.append((title, message))
