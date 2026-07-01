#! /usr/local/bin/python3
"""Shared helpers for backlog GUI tests."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
import pytest


def root_or_skip() -> tk.Tk:
    """Return a withdrawn Tk root, or skip when no display is available."""
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip('no display available')
    root.withdraw()
    return root


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
