#! /usr/local/bin/python3
"""Tests for the backlogops_cli jira_fields diagnostic command.

A stand-in Jira client returns canned field descriptors and edit-screen
metadata, so the command can be tested without a server: the tests check
it prints the custom field id-to-name map, prints an issue's editable
fields when asked, prints the raw JSON of the ``--field`` paths of that
issue, refuses ``--field`` without ``--issue``, and is discovered by the
list command.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from types import SimpleNamespace
import pytest
from test_backlogops.jira_write_helpers import jira_conn_preset
from backlogops import (
    AvailableTeams, BacklogOpsConfig, write_backlog_ops_config)
from backlogops.no_text_io import NoTextIO
import backlogops.jira_connect as jc
from backlogops_cli.list import command_modules
from backlogops_cli import jira_fields
from backlogops_cli.jira_fields import _print_pairs

NO = NoTextIO()


class _FieldClient:
    """A stand-in Jira client returning canned field information."""

    def myself(self) -> dict[str, str]:
        """Report a live session for the connection liveness check."""
        return {'name': 'tester'}

    def fields(self) -> list[dict[str, str]]:
        """Return the canned field descriptors."""
        return [{'id': 'customfield_10016', 'name': 'Story point estimate'},
                {'id': 'summary', 'name': 'Summary'}]

    def editmeta(self, issue: str) -> dict[str, object]:
        """Return the canned edit-screen field metadata."""
        _ = issue
        return {'fields': {'customfield_10016': {'name': 'Story point est'},
                           'summary': {'name': 'Summary'},
                           'timetracking': {'operations': ['set', 'edit']}}}

    def issue(self, key: str) -> SimpleNamespace:
        """Return the issue carrying canned raw fields."""
        return SimpleNamespace(raw={'key': key, 'fields': {
            'timetracking': {'remainingEstimateSeconds': 22020},
            'timeestimate': 22020}})

    def close(self) -> None:
        """Close the stand-in client (nothing to release)."""


def _connect_fake(connection: object, passphrase: object) -> _FieldClient:
    """Return a stand-in client, ignoring the connection details."""
    _ = (connection, passphrase)
    return _FieldClient()


def _config_file(path: Path) -> None:
    """Write a configuration with one Jira connection and preset."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]), stderr_file=NO)
    conn, preset = jira_conn_preset()
    preset.def_project = 'SCRUM'
    config.jira.connections = {'c': conn}
    config.jira.backlog_column_maps = {'bk': {}}
    config.jira.release_column_maps = {'rel': {}}
    config.jira.presets = {'a': preset}
    write_backlog_ops_config(config, path, NO)


def test_print_none(capsys: pytest.CaptureFixture[str]) -> None:
    """Test an empty field list prints a (none) placeholder."""
    _print_pairs('Heading', [])
    out = capsys.readouterr().out
    assert 'Heading' in out and '(none)' in out


def test_bad_preset(tmp_path: Path,
                    capsys: pytest.CaptureFixture[str]) -> None:
    """Test an unknown preset reports an error and returns 1."""
    _config_file(tmp_path / 'ops.cfg')
    code = jira_fields.main(['-p', 'nope', '-c', str(tmp_path / 'ops.cfg')])
    assert code == 1
    assert 'Could not read Jira fields' in capsys.readouterr().err


def test_in_command_list() -> None:
    """Test the jira_fields command is discovered by the list command."""
    assert 'jira_fields' in [name for name, _ in command_modules()]


def test_requires_preset() -> None:
    """Test the command requires the preset argument."""
    with pytest.raises(SystemExit):
        jira_fields.build_parser().parse_args([])


def test_prints_custom_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                              capsys: pytest.CaptureFixture[str]) -> None:
    """Test the command prints the custom field id-to-name map."""
    _config_file(tmp_path / 'ops.cfg')
    monkeypatch.setattr(jc, '_connect', _connect_fake)
    code = jira_fields.main(['-p', 'a', '-c', str(tmp_path / 'ops.cfg')])
    assert code == 0
    assert 'customfield_10016  Story point estimate' in capsys.readouterr().out


def test_prints_editable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                         capsys: pytest.CaptureFixture[str]) -> None:
    """Test the command prints an issue's editable fields when asked."""
    _config_file(tmp_path / 'ops.cfg')
    monkeypatch.setattr(jc, '_connect', _connect_fake)
    code = jira_fields.main(['-p', 'a', '-c', str(tmp_path / 'ops.cfg'),
                             '--issue', 'SCRUM-1'])
    assert code == 0
    out = capsys.readouterr().out
    assert 'edit screen of SCRUM-1' in out
    assert 'customfield_10016' in out


def _field_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
               *fields: str) -> int:
    """Run the command for issue SCRUM-1 with a --field per name."""
    _config_file(tmp_path / 'ops.cfg')
    monkeypatch.setattr(jc, '_connect', _connect_fake)
    args = ['-p', 'a', '-c', str(tmp_path / 'ops.cfg'), '--issue', 'SCRUM-1']
    for name in fields:
        args += ['--field', name]
    return jira_fields.main(args)


def test_prints_field_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                           capsys: pytest.CaptureFixture[str]) -> None:
    """Test --field prints the JSON value and the edit screen entry."""
    code = _field_run(tmp_path, monkeypatch, 'timetracking')
    assert code == 0
    out = capsys.readouterr().out
    assert "Field 'timetracking' of SCRUM-1 (Jira field timetracking):" in out
    assert '"remainingEstimateSeconds": 22020' in out
    assert '"edit"' in out


def test_prints_field_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                           capsys: pytest.CaptureFixture[str]) -> None:
    """Test a dotted path, a read-only field and a missing path print."""
    code = _field_run(tmp_path, monkeypatch,
                      'timetracking.remainingEstimateSeconds', 'timeestimate',
                      'timetracking.raw')
    assert code == 0
    out = capsys.readouterr().out
    assert 'value:\n    22020' in out
    assert 'edit screen: (not offered, so not writable by an edit)' in out
    assert "Field 'timetracking.raw'" in out
    assert 'value: (no such path in the issue)' in out


def test_field_needs_issue(tmp_path: Path,
                           capsys: pytest.CaptureFixture[str]) -> None:
    """Test --field without --issue is a usage error."""
    with pytest.raises(SystemExit) as raised:
        jira_fields.main(['-p', 'a', '-c', str(tmp_path / 'ops.cfg'),
                          '--field', 'timetracking'])
    assert raised.value.code == 2
    assert '--field needs --issue' in capsys.readouterr().err
