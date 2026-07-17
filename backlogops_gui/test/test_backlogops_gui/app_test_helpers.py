#! /usr/local/bin/python3
"""Shared fakes and stubs for the backlog application logic tests.

These small helpers let the application's menu-action logic be tested
without a real Tk display or real configuration files, and are shared by
the application tests and the configuration-action tests. A stand-in
configuration records where it was written, a factory builds an
application over a dummy root, and a few stubs stand in for the message
recorders and configuration loaders the tests patch in.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable, Optional, TextIO, cast
from backlogops import BacklogOpsConfig, GuiDisplayConfig
from backlogops_gui.application import BacklogApp


# pylint: disable-next=too-few-public-methods
class FakeConfig:
    """Stand-in configuration recording where it was written."""

    def __init__(self) -> None:
        """Create non-empty presets and an unset written destination."""
        self.input_configs: dict[str, object] = {'in': object()}
        self.output_configs: dict[str, object] = {'out': object()}
        self.available_teams: object = object()
        self.gui_display: GuiDisplayConfig = GuiDisplayConfig()
        self.written: Optional[str] = None

    def get_levels(self) -> dict[int, object]:
        """Return an empty levels mapping, as the real config would."""
        return {}

    def get_status_input_map(self) -> dict[str, object]:
        """Return an empty status map, as the real config would."""
        return {}

    def write(self, to_json_filename: str, stderr_file: object) -> None:
        """Record the destination the configuration was written to."""
        assert stderr_file is not None
        self.written = to_json_filename


def make_app(config: Optional[FakeConfig] = None) -> BacklogApp:
    """Return an application over a dummy root for logic-only tests."""
    typed = cast(Optional[BacklogOpsConfig], config)
    return BacklogApp(cast(tk.Tk, object()), typed)


def record(store: list[tuple[str, str]]) -> Callable[[str, str], None]:
    """Return a callback that records its title and message."""
    def recorder(title: str, message: str) -> None:
        store.append((title, message))
    return recorder


def returns(value: object) -> Callable[..., object]:
    """Return a configuration-loader stub yielding a fixed value."""
    def get(_arg: object, _sink: object, **_kwargs: object) -> object:
        return value
    return get


def raise_exit(_arg: object, captured: TextIO,
               **_kwargs: object) -> BacklogOpsConfig:
    """Report a missing file and exit, as the config loader does."""
    captured.write('File aha does not exist. Cannot proceed.\n')
    raise SystemExit(1)


def pick_none(_parent: object) -> Optional[str]:
    """Return nothing as if the file chooser was cancelled."""
    return None
