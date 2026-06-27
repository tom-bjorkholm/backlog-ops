#! /usr/local/bin/python3
"""Tests for the backlogops_cli list command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import os
import pkgutil
import importlib
from types import ModuleType, SimpleNamespace
from typing import Callable
import pytest
import backlogops_cli
from backlogops_cli.list import command_modules
from backlogops_cli.list import format_listing
from backlogops_cli.list import main
from backlogops_cli.list import _is_command
from backlogops_cli.list import _python_prefix
from backlogops_cli.bloc_version_reporter import BloCliVersionReporter


def _fake_module(name: str, description: object) -> ModuleType:
    """Return a fake module carrying main and the given description."""
    module = ModuleType(name)
    setattr(module, 'main', lambda: None)
    if description is not None:
        setattr(module, 'DESCRIPTION', description)
    return module


def test_list_is_listed() -> None:
    """Test the list command discovers and includes itself."""
    names = [name for name, _ in command_modules()]
    assert 'list' in names
    assert names == sorted(names)


def test_format_listing() -> None:
    """Test the listing shows each command and its description."""
    commands = [('list', _fake_module('list', 'List things'))]
    text = format_listing(commands)
    prefix = _python_prefix()
    assert f'  {prefix} backlogops_cli.list' in text
    assert '     List things' in text


def test_format_multiline() -> None:
    """Test a multi-line description is indented line by line."""
    module = _fake_module('cmd', 'First line\nSecond line')
    text = format_listing([('cmd', module)])
    assert '     First line' in text
    assert '     Second line' in text


def test_format_empty() -> None:
    """Test formatting an empty command list yields no text."""
    assert format_listing([]) == ''


@pytest.mark.parametrize('os_name,expected', [
    ('nt', 'python -m'), ('posix', 'python3 -m')])
def test_python_prefix(monkeypatch: pytest.MonkeyPatch, os_name: str,
                       expected: str) -> None:
    """Test the prefix matches the running operating system."""
    monkeypatch.setattr(os, 'name', os_name)
    assert _python_prefix() == expected


@pytest.mark.parametrize('description,expected', [
    ('a text', True), (None, False), (123, False)])
def test_is_command(description: object, expected: bool) -> None:
    """Test command detection needs main and a string description."""
    module = _fake_module('fake', description)
    assert _is_command(module) is expected


def test_main_without_main() -> None:
    """Test a module without a main is not treated as a command."""
    module = ModuleType('no_main')
    setattr(module, 'DESCRIPTION', 'has description only')
    assert _is_command(module) is False


def test_main_prints(capsys: pytest.CaptureFixture[str]) -> None:
    """Test main prints the formatted listing of commands."""
    main()
    out = capsys.readouterr().out
    assert 'backlogops_cli.list' in out


def test_skips_non_command(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a discovered module without main is skipped from the list."""
    info = SimpleNamespace(name='fake', ispkg=False)
    monkeypatch.setattr('backlogops_cli.list.pkgutil.iter_modules',
                        lambda path: [info])
    monkeypatch.setattr('backlogops_cli.list.importlib.import_module',
                        lambda name: ModuleType('fake'))
    assert not command_modules()


def test_modules_have_desc() -> None:
    """Test every command module exposing main defines DESCRIPTION."""
    for info in pkgutil.iter_modules(backlogops_cli.__path__):
        if info.ispkg or info.name.startswith('_'):
            continue
        module = importlib.import_module(f'backlogops_cli.{info.name}')
        if callable(getattr(module, 'main', None)):
            description = getattr(module, 'DESCRIPTION', None)
            assert isinstance(description, str), info.name


def _recorder(calls: list[bool]) -> Callable[..., None]:
    """Return a support-check stub recording that it ran."""
    def record(_self: object, _out: object = None) -> None:
        """Record the support check call instead of running it."""
        calls.append(True)
    return record


def test_main_checks_python(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the list command runs the unsupported-Python check."""
    calls: list[bool] = []
    monkeypatch.setattr(BloCliVersionReporter, 'check_if_unsupported_python',
                        _recorder(calls))
    main()
    assert calls == [True]
