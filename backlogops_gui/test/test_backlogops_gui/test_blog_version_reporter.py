#! /usr/local/bin/python3
"""Tests for the backlogops_gui version reporter."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from backlogops_gui.blog_version_reporter import BloGuiVersionReporter


def test_package_names() -> None:
    """Test the GUI package leads the inherited reported packages."""
    names = BloGuiVersionReporter().package_names()
    assert names[0] == 'backlogops-gui'
    for expected in ('backlogops', 'versionreporter', 'tableio'):
        assert expected in names


def test_main_package_name() -> None:
    """Test the GUI package is the main reported package."""
    reporter = BloGuiVersionReporter()
    assert reporter.get_main_package_name() == 'backlogops-gui'
