#! /usr/local/bin/python3
"""Tests for the Tkinter placeholder application."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from collections.abc import Callable
import tkinter as tk
from typing import Optional

import pytest

from backlogops_gui import application


class FakeTcl:  # pylint: disable=too-few-public-methods
    """Fake Tcl interpreter returning a configured patch level."""

    def __init__(self, version_text: str) -> None:
        """Store the fake patch level."""
        self.version_text = version_text

    def call(self, *args: object) -> object:
        """Return the fake patch level."""
        assert args == ('info', 'patchlevel')
        return self.version_text


class FakeRoot:
    """Fake root window used by display-independent GUI tests."""

    def __init__(self, version_text: str) -> None:
        """Create the fake root with an associated fake Tcl interpreter."""
        self.tk = FakeTcl(version_text)
        self.title_text: Optional[str] = None
        self.quit_count = 0
        self.mainloop_count = 0

    def title(self, text: str) -> None:
        """Record the configured window title."""
        self.title_text = text

    def quit(self) -> None:
        """Record that quit was requested."""
        self.quit_count += 1

    def mainloop(self) -> None:
        """Record that the main loop was started."""
        self.mainloop_count += 1


class FakeWidget:  # pylint: disable=too-few-public-methods
    """Fake widget recording constructor and pack options."""

    def __init__(self, kind: str, text: str,
                 command: Optional[Callable[[], None]] = None) -> None:
        """Store fake widget metadata."""
        self.kind = kind
        self.text = text
        self.command = command
        self.pack_options: dict[str, object] = {}

    def pack(self, *args: object, **pack_options: object) -> None:
        """Record requested pack options."""
        assert not args
        self.pack_options = pack_options


class WidgetLog:
    """Factory collecting fake widgets created by patched Tkinter calls."""

    def __init__(self) -> None:
        """Create an empty widget collection."""
        self.widgets: list[FakeWidget] = []

    def label(self, master: object, **options: object) -> FakeWidget:
        """Create and record a fake label."""
        assert master is not None
        assert options['wraplength'] == application.WARN_WRAP_LENGTH
        assert options['justify'] in ('center', 'left')
        text = options['text']
        assert isinstance(text, str)
        widget = FakeWidget('label', text)
        self.widgets.append(widget)
        return widget

    def button(self, master: object, **options: object) -> FakeWidget:
        """Create and record a fake button."""
        assert master is not None
        assert options['text'] == 'Quit'
        command = options['command']
        assert callable(command)
        widget = FakeWidget('button', 'Quit', command)
        self.widgets.append(widget)
        return widget


def _patch_tk(monkeypatch: pytest.MonkeyPatch, root: FakeRoot,
              widget_log: WidgetLog) -> None:
    """Patch Tkinter constructors used by the application."""
    monkeypatch.setattr(tk, 'Tk', lambda: root)
    monkeypatch.setattr(tk, 'Label', widget_log.label)
    monkeypatch.setattr(tk, 'Button', widget_log.button)


def _widget_texts(widget_log: WidgetLog) -> list[str]:
    """Return the widget texts recorded by the fake factory."""
    return [widget.text for widget in widget_log.widgets]


def test_window_no_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the placeholder window without a Tcl/Tk warning."""
    root = FakeRoot('9.0.2')
    widget_log = WidgetLog()
    _patch_tk(monkeypatch, root, widget_log)
    application.main()
    assert root.title_text == application.APP_TITLE
    assert _widget_texts(widget_log) == [application.APP_TEXT, 'Quit']


def test_window_with_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the placeholder window includes old Tcl/Tk warnings."""
    root = FakeRoot('8.6.13')
    widget_log = WidgetLog()
    _patch_tk(monkeypatch, root, widget_log)
    application.main()
    assert _widget_texts(widget_log) == [
        application.APP_TEXT,
        'This application was developed for Tcl/Tk version 9.0.2 or newer, '
        'but you are running version 8.6.13. This may affect the '
        'functionality.',
        'Quit'
    ]


def test_button_quits(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the quit button command calls the root quit method."""
    root = FakeRoot('9.0.2')
    widget_log = WidgetLog()
    _patch_tk(monkeypatch, root, widget_log)
    application.main()
    button = widget_log.widgets[-1]
    assert button.command is not None
    button.command()
    assert root.quit_count == 1


def test_main_runs_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main builds the window and starts the Tkinter loop."""
    root = FakeRoot('9.0.2')
    widget_log = WidgetLog()
    _patch_tk(monkeypatch, root, widget_log)
    application.main()
    assert root.mainloop_count == 1
    assert _widget_texts(widget_log) == [application.APP_TEXT, 'Quit']
