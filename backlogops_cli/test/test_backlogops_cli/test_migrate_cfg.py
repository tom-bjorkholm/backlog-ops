#! /usr/local/bin/python3
"""Tests for the backlogops_cli migrate_cfg command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
import json
from pathlib import Path
import pytest
from config_as_json import MigrateCfgWarnHook
from backlogops import (
    AvailableTeams, BacklogOpsConfig, InputFormatConfig, OutputFormatConfig,
    read_backlog_ops_config)
from backlogops.no_text_io import NoTextIO
from backlogops_cli import convert, migrate_cfg
from backlogops_cli.list import command_modules
from backlogops_cli._migrate_warn import CliMigrateWarnHook

NO_OUTPUT = NoTextIO()


def _write_old_config(path: Path) -> None:
    """Write an old top-level-workforce file that needs ROCF on read."""
    config = BacklogOpsConfig(
        available_teams=AvailableTeams(persons={}, teams=[]),
        stderr_file=NO_OUTPUT)
    data = json.loads(config.as_json_string(NO_OUTPUT))
    path.write_text(json.dumps(data['available_teams']), encoding='UTF-8')


def test_in_command_list() -> None:
    """Test the migrate_cfg command is discovered by the list command."""
    assert 'migrate_cfg' in [name for name, _ in command_modules()]


@pytest.mark.parametrize('args', [[], ['-i', 'a.cfg'], ['-o', 'b.cfg']])
def test_requires_args(args: list[str]) -> None:
    """Test the command requires both the input and the output file."""
    with pytest.raises(SystemExit):
        migrate_cfg.build_parser().parse_args(args)


def test_bad_kind() -> None:
    """Test an unknown --kind value is rejected by the parser."""
    with pytest.raises(SystemExit):
        migrate_cfg.build_parser().parse_args(['-i', 'a', '-o', 'b',
                                               '-k', 'bogus'])


def test_migrate_config(tmp_path: Path,
                        capsys: pytest.CaptureFixture[str]) -> None:
    """Test migrating an old config file writes a current-format file."""
    old = tmp_path / 'old.cfg'
    new = tmp_path / 'new.cfg'
    _write_old_config(old)
    assert migrate_cfg.main(['-i', str(old), '-o', str(new)]) == 0
    captured = capsys.readouterr()
    assert f'Wrote {new}' in captured.out
    assert 'Backward compatibility' not in captured.err
    out = io.StringIO()
    read_backlog_ops_config(new, out, auto_ch_hook=MigrateCfgWarnHook())
    assert out.getvalue() == ''


def test_migrate_input(tmp_path: Path) -> None:
    """Test migrating an old input preset file splits the single map."""
    old = tmp_path / 'in_old.cfg'
    new = tmp_path / 'in_new.cfg'
    old.write_text('{"tableio": {"format_name": "CSV"}, '
                   '"to_internal": {"Type": "level", "Rel": "name"}}',
                   encoding='UTF-8')
    assert migrate_cfg.main(['-i', str(old), '-o', str(new),
                            '-k', 'input']) == 0
    out = io.StringIO()
    loaded = InputFormatConfig(from_json_filename=new,
                               auto_ch_hook=MigrateCfgWarnHook(),
                               stderr_file=out)
    assert loaded.backlog_to_internal == {'Type': 'level', 'Rel': 'name'}
    assert loaded.release_to_internal == {'Rel': 'name'}
    assert out.getvalue() == ''


def test_migrate_output(tmp_path: Path) -> None:
    """Test migrating an old output preset file keeps the split map."""
    old = tmp_path / 'out_old.cfg'
    new = tmp_path / 'out_new.cfg'
    old.write_text('{"tableio": {"format_name": "CSV"}, '
                   '"to_external": {"level": "Type"}}', encoding='UTF-8')
    assert migrate_cfg.main(['-i', str(old), '-o', str(new),
                            '-k', 'output']) == 0
    out = io.StringIO()
    loaded = OutputFormatConfig(from_json_filename=new,
                                auto_ch_hook=MigrateCfgWarnHook(),
                                stderr_file=out)
    assert loaded.backlog_to_external == {'level': 'Type'}
    assert out.getvalue() == ''


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing input file makes the command return 1."""
    assert migrate_cfg.main(['-i', str(tmp_path / 'no.cfg'),
                            '-o', str(tmp_path / 'new.cfg')]) == 1


def test_existing_output(tmp_path: Path) -> None:
    """Test refusing to overwrite an existing output file returns 1."""
    old = tmp_path / 'old.cfg'
    new = tmp_path / 'new.cfg'
    _write_old_config(old)
    new.write_text('{}', encoding='UTF-8')
    assert migrate_cfg.main(['-i', str(old), '-o', str(new)]) == 1


def test_warn_hook_text() -> None:
    """Test the CLI warning hook points the user at migrate_cfg."""
    message = CliMigrateWarnHook.migrate_warn_msg()
    assert 'Backward compatibility' in message
    assert 'migrate_cfg' in message


def test_old_config_warns(tmp_path: Path,
                          capsys: pytest.CaptureFixture[str]) -> None:
    """Test a command reading an old -c config warns about migration."""
    teams = tmp_path / 'teams.cfg'
    _write_old_config(teams)
    source = tmp_path / 'in.csv'
    target = tmp_path / 'out.csv'
    source.write_text('key,level,title,story_points,status\n'
                      'A1,1,First,5,TODO\n', encoding='utf-8')
    assert convert.main(['-i', str(source), '-o', str(target),
                        '-c', str(teams)]) == 0
    assert 'migrate_cfg' in capsys.readouterr().err


def test_default_config_warns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                              capsys: pytest.CaptureFixture[str]) -> None:
    """Test a command auto-discovers an old default config and warns once.

    With no ``-c`` the command falls back to the backlog-ops configuration
    found via ``$BACKLOGOPS_CFG``, just like the GUI. The warning is shown
    exactly once even though the configuration is consulted several times
    while writing.
    """
    teams = tmp_path / 'teams.cfg'
    _write_old_config(teams)
    monkeypatch.setenv('BACKLOGOPS_CFG', str(teams))
    source = tmp_path / 'in.csv'
    target = tmp_path / 'out.csv'
    source.write_text('key,level,title,story_points,status\n'
                      'A1,1,First,5,TODO\n', encoding='utf-8')
    assert convert.main(['-i', str(source), '-o', str(target)]) == 0
    assert capsys.readouterr().err.count('Backward compatibility') == 1
