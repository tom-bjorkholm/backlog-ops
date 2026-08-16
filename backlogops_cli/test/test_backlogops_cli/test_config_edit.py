#! /usr/local/bin/python3
"""Tests for the backlogops_cli config_edit command.

The editor itself needs a terminal and runs until the user closes it, so
these tests put a stand-in backend in its place. The session around that
backend is the real one, so the command is tested against an edit model
that read the file and writes it; each stand-in does what a user could do
in one session — save, or close without saving.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Callable, Optional
import pytest
from test_backlogops.shared_test_data import write_full_config, \
    write_input_preset
from config_as_json import Config, PathOrStr
from edit_cfg_json import Descriptions, EditModel, Settings, edit
from backlogops import (
    CONFIG_DESCRIPTIONS, InputFormatConfig, NoTextIO, read_backlog_ops_config)
from backlogops.config_descriptions import EVERY
from backlogops_cli.list import command_modules
from backlogops_cli import config_edit

VELOCITY = ('available_teams', 'teams', '0', 'velocity')
"""Path of the velocity of the one team of the full test configuration."""

SAID = CONFIG_DESCRIPTIONS[('available_teams', 'teams', EVERY, 'velocity')]
"""What the library says about the velocity of a team."""


def _session(act: Callable[[EditModel], None]
             ) -> Callable[..., Optional[Config]]:
    """Return a stand-in for the editing session the command runs.

    It is the real session of the library with a backend that scripts what
    the user does, so everything the command relies on — reading the file,
    the descriptions, the settings and the save — is the real thing.
    """
    # pylint: disable-next=too-few-public-methods
    class StandIn:
        """Stand-in for the Textual editor, running one scripted session."""

        def run_editor(self, model: EditModel) -> None:
            """Do to the model what the scripted session does."""
            act(model)

    def scripted(config: Config, *, descriptions: Optional[Descriptions],
                 in_file: PathOrStr, out_file: PathOrStr,
                 settings: Settings) -> Optional[Config]:
        """Edit the configuration with the scripted backend."""
        return edit(config, StandIn(), descriptions=descriptions,
                    in_file=in_file, out_file=out_file, settings=settings)
    return scripted


def _saving(text: str) -> Callable[[EditModel], None]:
    """Return a session that sets the team velocity and saves."""
    def act(model: EditModel) -> None:
        """Edit one value and write the output file."""
        model.set_text(VELOCITY, text)
        model.save()
    return act


def _closing(model: EditModel) -> None:
    """Close the editor without saving anything."""
    _ = model


def _run(monkeypatch: pytest.MonkeyPatch, args: list[str],
         act: Callable[[EditModel], None]) -> int:
    """Run the command with a stand-in editor running ``act``."""
    monkeypatch.setattr(config_edit, 'edit', _session(act))
    return config_edit.main(args)


def _velocity(path: Path) -> Optional[float]:
    """Return the velocity of the team of the configuration at ``path``."""
    stored = read_backlog_ops_config(path, NoTextIO())
    return stored.available_teams.teams[0].velocity


def test_in_command_list() -> None:
    """Test config_edit is discovered as a command of the package."""
    assert 'config_edit' in [name for name, _ in command_modules()]


def test_requires_input() -> None:
    """Test the command refuses to run without the file to edit."""
    with pytest.raises(SystemExit):
        config_edit.build_parser().parse_args([])


def test_parsed_options() -> None:
    """Test the output file is optional and the kind defaults to config."""
    parsed = config_edit.build_parser().parse_args(['-i', 'x'])
    assert parsed.input == 'x'
    assert parsed.output is None
    assert parsed.kind == 'config'


@pytest.mark.parametrize('kind', ['config', 'input', 'output'])
def test_kind_choices(kind: str) -> None:
    """Test every kind of configuration file can be named."""
    parsed = config_edit.build_parser().parse_args(['-i', 'x', '-k', kind])
    assert parsed.kind == kind


def test_unknown_kind() -> None:
    """Test a kind of file the command does not know is refused."""
    with pytest.raises(SystemExit):
        config_edit.build_parser().parse_args(['-i', 'x', '-k', 'other'])


def test_missing_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                       capsys: pytest.CaptureFixture[str]) -> None:
    """Test a file that is not there is reported instead of edited."""
    assert _run(monkeypatch, ['-i', str(tmp_path / 'nope')], _closing) == 1
    assert 'not found' in capsys.readouterr().err


def test_edits_in_place(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                        capsys: pytest.CaptureFixture[str]) -> None:
    """Test the edited file is the file that is written without -o."""
    target = tmp_path / 'full.cfg'
    write_full_config(target)
    assert _run(monkeypatch, ['-i', str(target)], _saving('42.0')) == 0
    assert _velocity(target) == 42.0
    assert f'Saved to {target}' in capsys.readouterr().out
    assert (tmp_path / 'full.cfg.bak').is_file()


def test_extension_assumed(tmp_path: Path,
                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the .cfg extension is assumed for a name that is not a file."""
    write_full_config(tmp_path / 'full.cfg')
    assert _run(monkeypatch, ['-i', str(tmp_path / 'full')],
                _saving('7.0')) == 0
    assert _velocity(tmp_path / 'full.cfg') == 7.0


def test_writes_output_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                            capsys: pytest.CaptureFixture[str]) -> None:
    """Test -o is written, completed with the extension, and -i is left."""
    source = tmp_path / 'full.cfg'
    write_full_config(source)
    before = source.read_text(encoding='utf-8')
    assert _run(monkeypatch, ['-i', str(source), '-o', str(tmp_path / 'copy')],
                _saving('3.0')) == 0
    assert _velocity(tmp_path / 'copy.cfg') == 3.0
    assert source.read_text(encoding='utf-8') == before
    assert f'Saved to {tmp_path / "copy.cfg"}' in capsys.readouterr().out


def test_output_ext_kept(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a destination that has an extension keeps the one it has."""
    source = tmp_path / 'full.cfg'
    write_full_config(source)
    other = str(tmp_path / 'c.txt')
    assert _run(monkeypatch, ['-i', str(source), '-o', other],
                _saving('4.0')) == 0
    assert _velocity(tmp_path / 'c.txt') == 4.0


def test_closed_unsaved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                        capsys: pytest.CaptureFixture[str]) -> None:
    """Test closing the editor without saving succeeds and says so."""
    target = tmp_path / 'full.cfg'
    write_full_config(target)
    before = target.read_text(encoding='utf-8')
    assert _run(monkeypatch, ['-i', str(target)], _closing) == 0
    assert 'Closed without saving' in capsys.readouterr().out
    assert target.read_text(encoding='utf-8') == before


def test_describes_members(tmp_path: Path,
                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the session is given what the library says about its members."""
    target = tmp_path / 'full.cfg'
    write_full_config(target)
    seen: list[Optional[str]] = []

    def act(model: EditModel) -> None:
        """Record what is said about the velocity of the team."""
        rows = {row.path: row for row in model.rows}
        seen.append(rows[VELOCITY].description)
    assert _run(monkeypatch, ['-i', str(target)], act) == 0
    assert seen[0] is not None and SAID in seen[0]


def test_edits_input_preset(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a stand-alone input preset file is edited as its own kind."""
    target = tmp_path / 'in.cfg'
    write_input_preset(target)

    def act(model: EditModel) -> None:
        """Rename the mapped column and save the preset."""
        model.set_text(('backlog_to_internal', 'Type'), 'title')
        model.save()
    assert _run(monkeypatch, ['-i', str(target), '-k', 'input'], act) == 0
    written = InputFormatConfig(from_json_filename=target,
                                stderr_file=NoTextIO())
    assert written.backlog_to_internal == {'Type': 'title'}
