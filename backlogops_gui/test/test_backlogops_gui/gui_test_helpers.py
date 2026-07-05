#! /usr/local/bin/python3
"""Shared helpers for backlog GUI tests."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from contextlib import contextmanager
from typing import Iterator
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
