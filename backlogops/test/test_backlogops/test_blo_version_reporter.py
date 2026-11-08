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
                'wizard-ui-bridge', 'config-as-json', 'mformat',
                'edit-cfg-json']
    names = BloVersionReporter().package_names()
    assert names[:len(expected)] == expected
    for base in ('versionreporter', 'packaging', 'pypi-simple'):
        assert base in names


def test_main_package() -> None:
    """Test backlogops is treated as the main package."""
    assert BloVersionReporter().get_main_package_name() == 'backlogops'


def test_recommended() -> None:
    """Test the recommended Python version is the newest supported one."""
    assert BloVersionReporter().recommended_python() == Version('3.15')


def test_support_expires() -> None:
    """Test the configured Python support cutoffs."""
    expires = BloVersionReporter().get_app_support_expires()
    assert expires == {date(2026, 1, 1): '3.11', date(2027, 3, 1): '3.12',
                       date(2027, 11, 1): '3.13', date(2028, 11, 1): '3.14'}


@pytest.mark.parametrize('pyver,today', [
    ('3.11', date(2026, 1, 1)), ('3.12', date(2027, 3, 1)),
    ('3.13', date(2027, 11, 1)), ('3.14', date(2028, 11, 1))])
def test_warns_old(monkeypatch: pytest.MonkeyPatch, pyver: str,
                   today: date) -> None:
    """Test a Python version is reported from the day its support ends."""
    text = _support_check(_old_reporter(monkeypatch, pyver, today))
    assert 'old version of Python' in text
    assert 'install --upgrade backlogops' in text


@pytest.mark.parametrize('pyver,today', [
    ('3.11', date(2025, 12, 31)), ('3.12', date(2027, 2, 28)),
    ('3.13', date(2027, 10, 31)), ('3.14', date(2028, 10, 31)),
    ('3.15', date(2035, 1, 1))])
def test_silent_ok(monkeypatch: pytest.MonkeyPatch, pyver: str,
                   today: date) -> None:
    """Test no message for a Python whose support has not ended."""
    assert _support_check(_old_reporter(monkeypatch, pyver, today)) == ''
