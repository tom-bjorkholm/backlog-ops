#! /usr/local/bin/python3
"""Tests for the backlogops version reporter."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from datetime import date
import pytest
from packaging.version import Version
from backlogops.blo_version_reporter import BloVersionReporter


def _old_reporter(monkeypatch: pytest.MonkeyPatch, pyver: str,
                  today: date) -> BloVersionReporter:
    """Return a reporter seeing a fixed Python version and date."""
    reporter = BloVersionReporter()
    versions = {'backlogops': Version('0.1.1'), 'Python': Version(pyver)}
    monkeypatch.setattr(reporter, '_get', lambda: versions)
    monkeypatch.setattr(reporter, '_today', lambda: today)
    return reporter


def _support_check(reporter: BloVersionReporter) -> str:
    """Return what the support check writes for the reporter."""
    buffer = io.StringIO()
    reporter.check_if_unsupported_python(out_file=buffer)
    return buffer.getvalue()


def test_package_names() -> None:
    """Test the reported packages lead with the application packages."""
    expected = ['backlogops', 'tableio', 'tableio-cfg-json',
                'config-as-json', 'mformat']
    names = BloVersionReporter().package_names()
    assert names[:len(expected)] == expected
    for base in ('versionreporter', 'packaging', 'pypi-simple'):
        assert base in names


def test_main_package() -> None:
    """Test backlogops is treated as the main package."""
    assert BloVersionReporter().get_main_package_name() == 'backlogops'


def test_recommended() -> None:
    """Test the recommended Python version is 3.14."""
    assert BloVersionReporter().recommended_python() == Version('3.14')


def test_support_expires() -> None:
    """Test the configured Python support cutoffs."""
    expires = BloVersionReporter().get_app_support_expires()
    assert expires == {date(2026, 1, 1): '3.11', date(2027, 10, 1): '3.12'}


@pytest.mark.parametrize('pyver', ['3.11', '3.12'])
def test_warns_old(monkeypatch: pytest.MonkeyPatch, pyver: str) -> None:
    """Test an expired Python version is reported with upgrade help."""
    text = _support_check(_old_reporter(monkeypatch, pyver, date(2027, 10, 1)))
    assert 'old version of Python' in text
    assert 'install --upgrade backlogops' in text


@pytest.mark.parametrize('pyver,today', [
    ('3.14', date(2027, 10, 1)), ('3.11', date(2025, 1, 1))])
def test_silent_ok(monkeypatch: pytest.MonkeyPatch, pyver: str,
                   today: date) -> None:
    """Test no message for a current Python or before any cutoff."""
    assert _support_check(_old_reporter(monkeypatch, pyver, today)) == ''
