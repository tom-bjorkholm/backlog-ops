#! /usr/local/bin/python3
"""Shared config and connection-pool helpers for the Jira-write tests.

The backlog-write tests and the release-write tests both need a Jira
configuration with one connection, the default backlog and release column
maps and one preset named ``'w'``, and a connection pool whose clients are
all a stand-in. Those builders live here so both test modules share one
copy rather than duplicating them.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional
import pytest
import backlogops.jira_connect as jc
from backlogops.jira_connect import JiraConnections
from backlogops.jira_io_config import (
    DEF_BACKLOG_COLUMN_MAP, DEF_RELEASE_COLUMN_MAP, JiraColumnMap,
    JiraConnectConfig, JiraIOConfig, JiraPreset, TokenStorage)
from backlogops.no_text_io import NoTextIO

NO = NoTextIO()


def jira_write_config(project: str = 'PROJ',
                      release_map: Optional[JiraColumnMap] = None
                      ) -> JiraIOConfig:
    """Return a Jira config with one connection, maps and a preset ``'w'``.

    The connection ``'c'`` stores a clear internal token, the preset names
    the backlog map ``'bk'`` and the release map ``'rel'`` and the given
    default project. A caller may pass a custom release map; the backlog
    map is always the default one.
    """
    conn = JiraConnectConfig(stderr_file=NO)
    conn.token_storage = TokenStorage.CLEAR_INTERNAL
    conn.stored_token = 'TOK'
    preset = JiraPreset(stderr_file=NO)
    preset.connection_name = 'c'
    preset.backlog_column_map_name = 'bk'
    preset.release_column_map_name = 'rel'
    preset.def_project = project
    config = JiraIOConfig(stderr_file=NO)
    config.connections = {'c': conn}
    config.backlog_column_maps = {'bk': DEF_BACKLOG_COLUMN_MAP}
    rel = DEF_RELEASE_COLUMN_MAP if release_map is None else release_map
    config.release_column_maps = {'rel': rel}
    config.presets = {'w': preset}
    return config


def connections_for(monkeypatch: pytest.MonkeyPatch, client: object,
                    config: Optional[JiraIOConfig] = None) -> JiraConnections:
    """Return a pool whose connections all yield the given stand-in client."""
    monkeypatch.setattr(jc, '_connect', lambda connection, passphrase: client)
    chosen = jira_write_config() if config is None else config
    return JiraConnections(chosen, None)
