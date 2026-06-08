#! /usr/local/bin/python3
"""Tkinter placeholder application for backlog operations."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from collections.abc import Callable
import tkinter as tk
from typing import Any, Literal, Optional, Protocol

from backlogops_gui.tcltk_version import TclTkRoot, check_tcltk_version


APP_TEXT = 'Backlog operations GUI - no functionality yet'
APP_TITLE = 'Backlog operations GUI'
WARN_WRAP_LENGTH = 520


class PackedWidget(Protocol):  # pylint: disable=too-few-public-methods
    """Widget that can be placed in the Tkinter layout."""

    def pack(self, *args: Any, **pack_options: Any) -> None:
        """Place the widget in its parent container."""
        raise NotImplementedError


class TkWindow(TclTkRoot, Protocol):
    """Small part of the Tk root window API used by the app."""

    def title(self, text: str) -> None:
        """Set the title of the window."""
        raise NotImplementedError

    def quit(self) -> None:
        """Request that the Tkinter main loop exits."""
        raise NotImplementedError

    def mainloop(self) -> None:
        """Run the Tkinter event loop."""
        raise NotImplementedError


class RootMaker(Protocol):  # pylint: disable=too-few-public-methods
    """Callable that creates the main window root."""

    def __call__(self) -> TkWindow:
        """Return the main window root."""
        raise NotImplementedError


class LabelMaker(Protocol):  # pylint: disable=too-few-public-methods
    """Callable that creates a label widget."""

    def __call__(self, master: TkWindow, text: str, wraplength: int,
                 justify: Literal['center', 'left']) -> PackedWidget:
        """Return a label widget."""
        raise NotImplementedError


class ButtonMaker(Protocol):  # pylint: disable=too-few-public-methods
    """Callable that creates a button widget."""

    def __call__(self, master: TkWindow, text: str,
                 command: Callable[[], None]) -> PackedWidget:
        """Return a button widget."""
        raise NotImplementedError


def _make_root() -> TkWindow:
    """Create the Tkinter root window."""
    return tk.Tk()


def _make_label(master: TkWindow, text: str, wraplength: int,
                justify: Literal['center', 'left']) -> PackedWidget:
    """Create a Tkinter label widget."""
    assert isinstance(master, tk.Misc)
    return tk.Label(master, text=text, wraplength=wraplength, justify=justify)


def _make_button(master: TkWindow, text: str,
                 command: Callable[[], None]) -> PackedWidget:
    """Create a Tkinter button widget."""
    assert isinstance(master, tk.Misc)
    return tk.Button(master, text=text, command=command)


def _add_label(root: TkWindow, text: str, label_maker: LabelMaker,
               justify: Literal['center', 'left']) -> None:
    """Add one text label to the main window."""
    label = label_maker(root, text, WARN_WRAP_LENGTH, justify)
    label.pack(padx=16, pady=8)


def _add_quit_button(root: TkWindow, button_maker: ButtonMaker) -> None:
    """Add the quit button to the main window."""
    button = button_maker(root, 'Quit', root.quit)
    button.pack(padx=16, pady=12)


def build_main_window(root: TkWindow, label_maker: Optional[LabelMaker] = None,
                      button_maker: Optional[ButtonMaker] = None) -> None:
    """Build the placeholder widgets in the main window."""
    resolved_label = label_maker or _make_label
    resolved_button = button_maker or _make_button
    root.title(APP_TITLE)
    _add_label(root, APP_TEXT, resolved_label, 'center')
    warning_text = check_tcltk_version(root)
    if warning_text is not None:
        _add_label(root, warning_text, resolved_label, 'left')
    _add_quit_button(root, resolved_button)


def main(root_maker: Optional[RootMaker] = None,
         label_maker: Optional[LabelMaker] = None,
         button_maker: Optional[ButtonMaker] = None) -> None:
    """Start the backlog operations GUI."""
    resolved_root = root_maker or _make_root
    root = resolved_root()
    build_main_window(root, label_maker, button_maker)
    root.mainloop()
