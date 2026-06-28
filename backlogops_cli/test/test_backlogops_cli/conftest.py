#! /usr/local/bin/python3
"""Shared fixtures isolating CLI tests from the real configuration."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from backlogops import backlog_ops_config


@pytest.fixture(autouse=True)
def _isolate_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset the stored configuration and point HOME at an empty directory.

    The data commands look up the default teams configuration the same way
    as the GUI when no ``--io-config`` is given. Without this isolation the
    tests would pick up the developer's ``$HOME/.backlogops.cfg`` and the
    process-wide configuration cache would leak between tests.
    """
    # pylint: disable-next=protected-access
    monkeypatch.setattr(backlog_ops_config._ConfigStore, 'current', None)
    monkeypatch.delenv('BACKLOGOPS_CFG', raising=False)
    monkeypatch.delenv('BACKLOGOPS_DIR', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('USERPROFILE', str(tmp_path))
