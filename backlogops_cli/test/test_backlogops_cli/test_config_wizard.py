#! /usr/local/bin/python3
"""Tests for the backlogops_cli config_wizard command."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
import os
from pathlib import Path
from typing import Optional
import pytest
from backlogops import (
    AvailableTeams, BacklogOpsConfig, Membership, NoTextIO, Person, Team,
    read_backlog_ops_config, write_backlog_ops_config)
from backlogops_cli.list import command_modules
from backlogops_cli import config_wizard


def _make_cfg(person: str) -> BacklogOpsConfig:
    """Return a minimal valid configuration with one named person."""
    teams = AvailableTeams(persons={person.lower(): Person(name=person)},
                           teams=[])
    return BacklogOpsConfig(available_teams=teams)


def _write_cfg(path: Path, person: str) -> None:
    """Write a minimal readable configuration with one named person."""
    write_backlog_ops_config(_make_cfg(person), path, NoTextIO())


def _persons(path: Path) -> list[str]:
    """Return the person names of the configuration stored at path."""
    loaded = read_backlog_ops_config(path, NoTextIO())
    return list(loaded.available_teams.persons)


def _echo_wizard(_bridge: object, *,
                 default: Optional[BacklogOpsConfig] = None,
                 backward: bool = False) -> Optional[BacklogOpsConfig]:
    """Return the pre-fill default unchanged (a no-op wizard for tests)."""
    _ = backward
    return default


def _new_wizard(_bridge: object, *, default: Optional[BacklogOpsConfig] = None,
                backward: bool = False) -> BacklogOpsConfig:
    """Return a fresh configuration that differs from any pre-fill."""
    _ = (default, backward)
    return _make_cfg('New')


def test_in_command_list() -> None:
    """Test config_wizard is discovered and the old name is gone."""
    names = [name for name, _ in command_modules()]
    assert 'config_wizard' in names
    assert 'teams_wizard' not in names


def test_requires_output() -> None:
    """Test the command requires the output file argument."""
    with pytest.raises(SystemExit):
        config_wizard.build_parser().parse_args([])


def test_no_textual_flag() -> None:
    """Test the --no-textual switch is parsed as a boolean flag."""
    parser = config_wizard.build_parser()
    assert parser.parse_args(['-o', 'x']).no_textual is False
    assert parser.parse_args(['-o', 'x', '--no-textual']).no_textual is True


def test_input_flag() -> None:
    """Test the optional -i/--input pre-fill file argument is parsed."""
    parser = config_wizard.build_parser()
    assert parser.parse_args(['-o', 'x']).input is None
    assert parser.parse_args(['-o', 'x', '-i', 'y']).input == 'y'
    assert parser.parse_args(['-o', 'x', '--input', 'y']).input == 'y'


def test_no_textual_writes(tmp_path: Path,
                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the forced console interface writes a configuration file."""
    answers = [''] * 21
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'.join(answers) + '\n'))
    assert config_wizard.main(
        ['-o', str(tmp_path / 'teams'), '--no-textual']) == 0
    assert (tmp_path / 'teams.cfg').exists()


def test_main_writes_file(tmp_path: Path,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the command adds the .cfg extension and writes a readable file."""
    answers = [''] * 21
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'.join(answers) + '\n'))
    assert config_wizard.main(['-o', str(tmp_path / 'teams')]) == 0
    written = tmp_path / 'teams.cfg'
    assert written.exists()
    loaded = read_backlog_ops_config(written, NoTextIO())
    assert not loaded.available_teams.teams


def test_overwrite_declined(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test declining the overwrite keeps the config and skips the wizard."""
    target = tmp_path / 'teams.cfg'
    target.write_text('OLD', encoding='utf-8')
    monkeypatch.setattr('sys.stdin', io.StringIO('n\n'))
    assert config_wizard.main(['-o', str(tmp_path / 'teams'),
                               '--no-textual']) == 1
    assert target.read_text(encoding='utf-8') == 'OLD'


def test_overwrite_force(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the force flag overwrites the existing config without asking."""
    target = tmp_path / 'teams.cfg'
    target.write_text('OLD', encoding='utf-8')
    answers = [''] * 21
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'.join(answers) + '\n'))
    assert config_wizard.main(['-o', str(tmp_path / 'teams'),
                               '--no-textual', '-f']) == 0
    loaded = read_backlog_ops_config(target, NoTextIO())
    assert not loaded.available_teams.teams


def test_prefill(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test -i reads a config and passes it as the wizard pre-fill.

    The no-op wizard returns the pre-fill unchanged, so the output file is
    written from the values read from the input file.
    """
    source = tmp_path / 'source.cfg'
    _write_cfg(source, 'Ada')
    monkeypatch.setattr(config_wizard, 'backlog_ops_wizard', _echo_wizard)
    out = tmp_path / 'out.cfg'
    assert config_wizard.main(
        ['-i', str(source), '-o', str(out), '--no-textual']) == 0
    assert _persons(out) == ['ada']


def test_edit_in_place(tmp_path: Path,
                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Test -i and -o naming the same file edits it after confirming."""
    target = tmp_path / 'teams.cfg'
    _write_cfg(target, 'Ada')
    monkeypatch.setattr(config_wizard, 'backlog_ops_wizard', _echo_wizard)
    monkeypatch.setattr('sys.stdin', io.StringIO('y\n'))
    assert config_wizard.main(
        ['-i', str(target), '-o', str(target), '--no-textual']) == 0
    assert _persons(target) == ['ada']
    assert not (tmp_path / 'teams.cfg.in_progress').exists()


def test_missing_input(tmp_path: Path) -> None:
    """Test a missing pre-fill file makes the command fail cleanly."""
    out = tmp_path / 'out.cfg'
    assert config_wizard.main(
        ['-i', str(tmp_path / 'nope.cfg'), '-o', str(out),
         '--no-textual']) == 1
    assert not out.exists()


def test_crash_keeps_old(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a crash before the atomic rename loses no information.

    The rename is made to fail to simulate a kill at the worst moment. The
    old output file must then still hold its original contents and the new
    contents must be fully present in the .in_progress file.
    """
    target = tmp_path / 'teams.cfg'
    _write_cfg(target, 'Ada')
    monkeypatch.setattr(config_wizard, 'backlog_ops_wizard', _new_wizard)
    monkeypatch.setattr('sys.stdin', io.StringIO('y\n'))

    def _boom(_src: object, _dst: object) -> None:
        """Fail the atomic rename to simulate a crash before it completes."""
        raise OSError('simulated crash before rename')
    monkeypatch.setattr(os, 'replace', _boom)
    assert config_wizard.main(
        ['-i', str(target), '-o', str(target), '--no-textual']) == 1
    in_progress = tmp_path / 'teams.cfg.in_progress'
    assert _persons(target) == ['ada']
    assert _persons(in_progress) == ['new']


def test_main_reports_failure(tmp_path: Path,
                              monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an inconsistent workforce makes the command return 1."""
    def _bad_wizard(_bridge: object, *, default: object = None,
                    backward: bool = False) -> BacklogOpsConfig:
        """Return an over-allocated workforce that fails validation."""
        _ = (default, backward)
        persons = {'ada': Person(name='Ada')}
        first = Team(name='A', velocity=1.0, sum_fte_at_velocity=1.0,
                     sprint_length=10, members=[Membership(person_name='Ada')])
        second = Team(name='B', velocity=1.0, sum_fte_at_velocity=1.0,
                      sprint_length=10,
                      members=[Membership(person_name='Ada', fte=0.5)])
        bad = AvailableTeams(persons=persons, teams=[first, second])
        return BacklogOpsConfig(available_teams=bad)
    monkeypatch.setattr(config_wizard, 'backlog_ops_wizard', _bad_wizard)
    assert config_wizard.main(['-o', str(tmp_path / 'teams')]) == 1
    assert not (tmp_path / 'teams.cfg').exists()
    assert not (tmp_path / 'teams.cfg.in_progress').exists()
