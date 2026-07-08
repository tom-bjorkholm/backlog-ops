#! /usr/bin/env python3
"""Pytest configuration for backlogops_gui tests."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom pytest markers for backlogops_gui tests."""
    config.addinivalue_line(
        'markers',
        'focus_sensitive: test requires a focused window and unlocked '
        'display; run manually under controlled conditions')
