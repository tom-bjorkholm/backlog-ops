#! /usr/local/bin/python3
"""Shared fixtures for the Jira collaborator tests.

The Jira operations run their network call on a worker thread and hand the
result back through the main window's ``after``. These helpers replace the
thread with one that runs at once and the ``after`` with one that runs its
callback at once, so a test drives a whole operation synchronously. They
also build a minimal configuration with one Jira preset.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable, Optional, cast
from backlogops import (
    BacklogOpsConfig, JiraConnectConfig, JiraIOConfig, JiraPreset,
    TokenStorage)
from backlogops.jira_token import encrypt_token
from backlogops_gui.application import BacklogApp


def record_calls(store: list[tuple[str, str]]) -> Callable[[str, str], None]:
    """Return a callback recording its title and message."""
    def recorder(title: str, message: str) -> None:
        store.append((title, message))
    return recorder


# pylint: disable-next=too-few-public-methods
class AfterRoot:
    """Minimal root that runs scheduled callbacks immediately."""

    def after(self, delay: int, callback: Callable[[], None]) -> None:
        """Record a zero-delay GUI handoff by running it now."""
        assert delay == 0
        callback()


# pylint: disable-next=too-few-public-methods
class ImmediateThread:
    """Small thread stand-in that runs its work when started."""

    def __init__(self, target: Callable[[], None], daemon: bool) -> None:
        """Store the worker callable and daemon flag."""
        self._target = target
        self.daemon = daemon
        self.started = False

    def start(self) -> None:
        """Mark the worker started and call its target immediately."""
        self.started = True
        self._target()


def make_immediate(target: Callable[[], None],
                   daemon: bool) -> ImmediateThread:
    """Return an immediate thread stand-in."""
    return ImmediateThread(target, daemon)


def jira_config(encrypted: bool = False) -> JiraIOConfig:
    """Return a minimal Jira configuration with one preset."""
    conn = JiraConnectConfig()
    conn.token_storage = (TokenStorage.ENCRYPTED_INTERNAL if encrypted
                          else TokenStorage.CLEAR_INTERNAL)
    conn.stored_token = encrypt_token('TOK', 'secret') if encrypted else 'TOK'
    preset = JiraPreset()
    preset.connection_name = 'main'
    preset.def_filter = 'project = SCRUM'
    cfg = JiraIOConfig()
    cfg.connections = {'main': conn}
    cfg.presets = {'scrum': preset}
    return cfg


def config(encrypted: bool = False) -> BacklogOpsConfig:
    """Return a top-level config with one Jira preset."""
    top = BacklogOpsConfig()
    top.jira = jira_config(encrypted)
    return top


def make_app(top: Optional[BacklogOpsConfig]) -> BacklogApp:
    """Return an application with immediate ``after`` callbacks."""
    return BacklogApp(cast(tk.Tk, AfterRoot()), top)
