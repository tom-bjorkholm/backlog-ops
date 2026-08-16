#! /usr/local/bin/python3
"""Tests for the configuration editor support and its descriptions.

The descriptions are checked against the tree the editor really builds, so
a selector that names no member is found here rather than showing up as a
member without a description in a window. The editing support is checked by
reading, changing and saving a configuration through the model, without any
user interface.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Optional, TextIO, override
import pytest
from config_as_json import Config, ValidationPlan
from edit_cfg_json import ConfigLoadError, EditModel, default_config, \
    editor_model, row_description
from tableio import FileAccess, access_capabilities
from tableio_cfg_json import tio_json_config_default
from backlogops import (
    BacklogOpsConfig, CONFIG_DESCRIPTIONS, EDIT_SETTINGS, GUI_DESCRIPTIONS,
    INPUT_DESCRIPTIONS, JIRA_DESCRIPTIONS, InputFormatConfig, NoTextIO,
    OUTPUT_DESCRIPTIONS, OutputFormatConfig, Team, WORKFORCE_DESCRIPTIONS,
    descriptions_for, read_backlog_ops_config)
from backlogops.config_descriptions import EVERY, prefixed
from .shared_test_data import write_full_config, write_input_preset, \
    full_config


class UndescribedConfig(Config):
    """A configuration class the editing support says nothing about."""

    def __init__(self, stderr_file: TextIO) -> None:
        """Declare one member and read no JSON."""
        self.value = 1
        Config.__init__(self, from_json_data_text=None,
                        from_json_filename=None, stderr_file=stderr_file)

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Check nothing, because there is nothing here worth checking."""
        _ = stderr_file
        return []


def _model(config: Config, in_file: Optional[str] = None,
           out_file: Optional[str] = None) -> EditModel:
    """Return the edit model of one configuration, discarding diagnostics.

    This is what each user interface hands to the editor: the two answers
    this library gives about a session, and the files of that session.
    """
    return editor_model(config, descriptions=descriptions_for(config),
                        in_file=in_file, out_file=out_file,
                        settings=EDIT_SETTINGS, stderr_file=NoTextIO())


def _from_file(path: Path, out_file: Optional[str] = None) -> EditModel:
    """Return the model editing one backlog-ops configuration file."""
    return _model(default_config(BacklogOpsConfig), in_file=str(path),
                  out_file=out_file)


def _all_options_preset() -> InputFormatConfig:
    """Return an input preset whose endpoint holds every TableIO option."""
    access = FileAccess.READ
    preset = InputFormatConfig(stderr_file=NoTextIO())
    preset.tableio = tio_json_config_default(
        access_capabilities(access, error_file=NoTextIO()), access,
        include_all_options=True, stderr_file=NoTextIO())
    return preset


def _own_text(path: tuple[str, ...]) -> bool:
    """Whether this library writes the description of that member itself.

    A path that goes on below a ``tableio`` member names a member of the
    TableIO endpoint, whose text ``tableio_cfg_json`` supplies. Those are
    checked against an endpoint holding every option, because a preset
    file holds only the settings that were chosen.
    """
    return 'tableio' not in path[:-1]


def _explained(model: EditModel) -> str:
    """Return everything the model says below its nodes, as one text."""
    return '\n'.join(row_description(model, row) for row in model.rows)


def _teams(path: Path) -> list[Team]:
    """Return the teams of the configuration stored at ``path``."""
    stored = read_backlog_ops_config(path, NoTextIO())
    return list(stored.available_teams.teams)


def test_descriptions_used() -> None:
    """Test every description reaches a member of a full configuration.

    A selector that addresses no member is never shown and is never an
    error, so a misspelled one would silently do nothing.
    """
    shown = _explained(_model(full_config()))
    unused = [path for path, text in CONFIG_DESCRIPTIONS.items()
              if _own_text(path) and text not in shown]
    assert not unused


def test_tableio_described() -> None:
    """Test the TableIO endpoint is described by the library owning it.

    The text is asked of ``tableio_cfg_json`` rather than written here, so
    what is checked is that every member of an endpoint is reached by it.
    """
    shown = _explained(_model(_all_options_preset()))
    unused = [path for path, text in INPUT_DESCRIPTIONS.items()
              if not _own_text(path) and text not in shown]
    assert not unused


def test_only_when_explained() -> None:
    """Test nothing is said below a node while the explanations are hidden."""
    model = _model(full_config())
    model.toggle_explanations()
    assert _explained(model).strip() == ''


@pytest.mark.parametrize('path', [
    ('available_teams', 'persons', EVERY, 'name'),
    ('available_teams', 'teams', EVERY, 'sprint_length'),
    ('available_teams', 'company_work_hours', 'work_hours'),
    ('input_configs', EVERY, 'status_input_map', EVERY),
    ('output_configs', EVERY, 'level_display'),
    ('gui_display', 'backlog_to_external'),
    ('jira', 'connections', EVERY, 'token_storage'),
    ('jira', 'presets', EVERY, 'def_filter'),
    ('levels', EVERY, 'aliases'),
    ('status_input_map', EVERY)])
def test_described_member(path: tuple[str, ...]) -> None:
    """Test a member deep inside the tree is described where it is."""
    assert CONFIG_DESCRIPTIONS[path]


@pytest.mark.parametrize('prefix,members', [
    (('available_teams',), WORKFORCE_DESCRIPTIONS),
    (('input_configs', EVERY), INPUT_DESCRIPTIONS),
    (('output_configs', EVERY), OUTPUT_DESCRIPTIONS),
    (('gui_display',), GUI_DESCRIPTIONS),
    (('jira',), JIRA_DESCRIPTIONS)])
def test_one_text_per_member(prefix: tuple[str, ...],
                             members: dict[tuple[str, ...], str]) -> None:
    """Test a class says the same thing wherever it is used.

    The mapping of the whole configuration is built from the mapping of each
    class, so a member cannot come to say one thing nested in the
    configuration and another in a stand-alone preset file.
    """
    for path, text in prefixed(prefix, members).items():
        assert CONFIG_DESCRIPTIONS[path] == text


def test_prefixed_paths() -> None:
    """Test the prefix helper puts each path under the given prefix."""
    assert prefixed(('a', EVERY), {('b',): 'x'}) == {('a', EVERY, 'b'): 'x'}


@pytest.mark.parametrize('config_type,expected', [
    (BacklogOpsConfig, CONFIG_DESCRIPTIONS),
    (InputFormatConfig, INPUT_DESCRIPTIONS),
    (OutputFormatConfig, OUTPUT_DESCRIPTIONS)])
def test_descriptions_for(config_type: type[Config],
                          expected: dict[tuple[str, ...], str]) -> None:
    """Test each editable class is given the descriptions of its members."""
    assert descriptions_for(default_config(config_type)) == expected


def test_no_descriptions() -> None:
    """Test a class this library says nothing about gets no descriptions."""
    assert descriptions_for(UndescribedConfig(NoTextIO())) is None


def test_edit_settings() -> None:
    """Test the editor keeps one backup and confirms an overwrite."""
    assert EDIT_SETTINGS.file_extension == '.cfg'
    assert EDIT_SETTINGS.extension_enforced is False
    assert EDIT_SETTINGS.backup_suffix == '.bak'
    assert EDIT_SETTINGS.backup_count == 1
    assert EDIT_SETTINGS.confirm_overwrite is True


def test_editor_builds_config() -> None:
    """Test the editor constructs the top-level class on its own.

    It needs no loader for it, because the class takes only the arguments
    ``config_as_json`` documents, and what it builds is the declared
    defaults that a session with no input file starts from.
    """
    config = default_config(BacklogOpsConfig)
    assert isinstance(config, BacklogOpsConfig)
    assert not config.available_teams.teams


def test_reads_input_file(tmp_path: Path) -> None:
    """Test the model holds the values of the file it was given."""
    source = tmp_path / 'full.cfg'
    write_full_config(source)
    model = _from_file(source)
    paths = [row.path for row in model.rows]
    assert ('available_teams', 'persons', 'ada', 'name') in paths
    assert model.out_file == str(source)


def test_out_file_completed(tmp_path: Path) -> None:
    """Test a chosen destination is completed and the input file is not.

    The output file was chosen for this session, so it gets the extension
    the application uses; the input file names a file that already exists
    and completing it would open another one.
    """
    source = tmp_path / 'full.cfg'
    write_full_config(source)
    model = _from_file(source, out_file=str(tmp_path / 'copy'))
    assert model.out_file == str(tmp_path / 'copy.cfg')


def test_missing_input_file(tmp_path: Path) -> None:
    """Test a file that cannot be opened is refused with its diagnostics."""
    with pytest.raises(ConfigLoadError, match='nope.cfg'):
        _from_file(tmp_path / 'nope.cfg')


def test_saves_edited_value(tmp_path: Path) -> None:
    """Test an edited value is validated and written to the output file."""
    source = tmp_path / 'full.cfg'
    write_full_config(source)
    out = tmp_path / 'out.cfg'
    model = _from_file(source, out_file=str(out))
    model.set_text(('available_teams', 'teams', '0', 'velocity'), '20.0')
    assert model.save().saved
    assert isinstance(model.saved_config, BacklogOpsConfig)
    assert model.saved_config.available_teams.teams[0].velocity == 20.0
    assert _teams(out)[0] == model.saved_config.available_teams.teams[0]


def test_keeps_old_file(tmp_path: Path) -> None:
    """Test the configuration a save writes over is kept as a .bak file."""
    source = tmp_path / 'full.cfg'
    write_full_config(source)
    before = source.read_text(encoding='utf-8')
    model = _from_file(source)
    model.set_text(('available_teams', 'teams', '0', 'sprint_length'), '5')
    assert model.save().saved
    assert (tmp_path / 'full.cfg.bak').read_text(encoding='utf-8') == before
    assert _teams(source)[0].sprint_length == 5


def test_refuses_bad_value(tmp_path: Path) -> None:
    """Test a value the configuration class refuses is not written.

    The status map holds the name of a status, so a name that is no status
    is refused by the library's own validation and the file on disk is left
    exactly as it was.
    """
    source = tmp_path / 'full.cfg'
    write_full_config(source)
    before = source.read_text(encoding='utf-8')
    model = _from_file(source)
    model.set_text(('status_input_map', 'Closed'), 'NO_SUCH_STATUS')
    assert not model.validate().valid
    assert not model.save().saved
    assert source.read_text(encoding='utf-8') == before


def test_edits_input_preset(tmp_path: Path) -> None:
    """Test a stand-alone preset file is edited with its own descriptions."""
    source = tmp_path / 'in.cfg'
    write_input_preset(source)
    model = _model(default_config(InputFormatConfig), in_file=str(source))
    assert INPUT_DESCRIPTIONS[('backlog_to_internal',)] in _explained(model)
    model.set_text(('backlog_to_internal', 'Type'), 'title')
    assert model.save().saved
    written = InputFormatConfig(from_json_filename=source,
                                stderr_file=NoTextIO())
    assert written.backlog_to_internal == {'Type': 'title'}
