#! /usr/local/bin/python3
"""Tests for the backlogops_cli version reporter."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
import pytest
from packaging.version import Version
from backlogops_cli.bloc_version_reporter import BloCliVersionReporter


def test_package_names() -> None:
    """Test the CLI package leads the inherited reported packages."""
    names = BloCliVersionReporter().package_names()
    assert names[0] == 'backlogops-cli'
    for inherited in ('backlogops', 'tableio', 'versionreporter'):
        assert inherited in names


def test_main_package() -> None:
    """Test the CLI package is treated as the main package."""
    reporter = BloCliVersionReporter()
    assert reporter.get_main_package_name() == 'backlogops-cli'


def test_inherits_cutoffs() -> None:
    """Test the CLI reporter inherits the support cutoffs and Python."""
    reporter = BloCliVersionReporter()
    assert reporter.recommended_python() == Version('3.14')
    expires = reporter.get_app_support_expires()
    assert expires == {date(2026, 1, 1): '3.11', date(2027, 10, 1): '3.12'}


def test_warns_names_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the upgrade help names the CLI package as the application."""
    reporter = BloCliVersionReporter()
    versions = {'backlogops-cli': Version('0.1.1'),
                'Python': Version('3.11')}
    monkeypatch.setattr(reporter, '_get', lambda: versions)
    monkeypatch.setattr(reporter, '_today', lambda: date(2027, 10, 1))
    buffer = io.StringIO()
    reporter.check_if_unsupported_python(out_file=buffer)
    assert 'install --upgrade backlogops-cli' in buffer.getvalue()
