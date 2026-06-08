#! /usr/local/bin/python3
"""Tests for the Tkinter placeholder application."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from collections.abc import Callable
from typing import Any, Literal, Optional

from backlogops_gui import application
from backlogops_gui.application import TkWindow


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
        self.tk: object = FakeTcl(version_text)
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

    def pack(self, *args: Any, **pack_options: Any) -> None:
        """Record requested pack options."""
        assert not args
        self.pack_options = pack_options


class WidgetFactory:
    """Factory collecting fake widgets created by the application."""

    def __init__(self) -> None:
        """Create an empty widget collection."""
        self.widgets: list[FakeWidget] = []

    def label(self, master: TkWindow, text: str, wraplength: int,
              justify: Literal['center', 'left']) -> FakeWidget:
        """Create and record a fake label."""
        assert master.tk is not None
        assert wraplength == application.WARN_WRAP_LENGTH
        assert justify in ('center', 'left')
        widget = FakeWidget('label', text)
        self.widgets.append(widget)
        return widget

    def button(self, master: TkWindow, text: str,
               command: Callable[[], None]) -> FakeWidget:
        """Create and record a fake button."""
        assert master.tk is not None
        widget = FakeWidget('button', text, command)
        self.widgets.append(widget)
        return widget


def _widget_texts(factory: WidgetFactory) -> list[str]:
    """Return the widget texts recorded by the fake factory."""
    return [widget.text for widget in factory.widgets]


def test_window_no_warning() -> None:
    """Test the placeholder window without a Tcl/Tk warning."""
    root = FakeRoot('9.0.2')
    factory = WidgetFactory()
    application.build_main_window(root, factory.label, factory.button)
    assert root.title_text == application.APP_TITLE
    assert _widget_texts(factory) == [application.APP_TEXT, 'Quit']


def test_window_with_warning() -> None:
    """Test the placeholder window includes old Tcl/Tk warnings."""
    root = FakeRoot('8.6.13')
    factory = WidgetFactory()
    application.build_main_window(root, factory.label, factory.button)
    assert _widget_texts(factory) == [
        application.APP_TEXT,
        'This application was developed for Tcl/Tk version 9.0.2 or newer, '
        'but you are running version 8.6.13. This may affect the '
        'functionality.',
        'Quit'
    ]


def test_button_quits() -> None:
    """Test the quit button command calls the root quit method."""
    root = FakeRoot('9.0.2')
    factory = WidgetFactory()
    application.build_main_window(root, factory.label, factory.button)
    button = factory.widgets[-1]
    assert button.command is not None
    button.command()
    assert root.quit_count == 1


def test_main_runs_loop() -> None:
    """Test main builds the window and starts the Tkinter loop."""
    root = FakeRoot('9.0.2')
    factory = WidgetFactory()
    application.main(lambda: root, factory.label, factory.button)
    assert root.mainloop_count == 1
    assert _widget_texts(factory) == [application.APP_TEXT, 'Quit']
