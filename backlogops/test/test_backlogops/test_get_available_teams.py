#! /usr/local/bin/python3
"""Tests for the get_available_teams convenience loader."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from backlogops import get_available_teams, write_available_teams
from backlogops.available_teams import AvailableTeams
from backlogops import available_teams_config
from backlogops.no_text_io import NoTextIO

NO_OUTPUT = NoTextIO()


@pytest.fixture(autouse=True)
def _clean_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset the stored workforce and point HOME at an empty directory."""
    # pylint: disable-next=protected-access
    monkeypatch.setattr(available_teams_config._TeamsStore, 'current', None)
    monkeypatch.delenv('BACKLOGOPS_CFG', raising=False)
    monkeypatch.delenv('BACKLOGOPS_DIR', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('USERPROFILE', str(tmp_path))


def _write_teams(path: Path) -> None:
    """Write an empty but valid workforce to the given path."""
    write_available_teams(AvailableTeams(persons={}, teams=[]), path,
                          NO_OUTPUT)


def test_filename_stored(tmp_path: Path) -> None:
    """Test a named file is read and reused on a later call."""
    config_file = tmp_path / 'teams.json'
    _write_teams(config_file)
    first = get_available_teams(config_file, NO_OUTPUT)
    second = get_available_teams(None, NO_OUTPUT)
    assert second is first


def test_env_cfg_file_used(tmp_path: Path,
                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Test $BACKLOGOPS_CFG names the file to load."""
    config_file = tmp_path / 'env.json'
    _write_teams(config_file)
    monkeypatch.setenv('BACKLOGOPS_CFG', str(config_file))
    assert get_available_teams(None, NO_OUTPUT) is not None


def test_env_cfg_missing_file(tmp_path: Path,
                              monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing $BACKLOGOPS_CFG file raises FileNotFoundError."""
    monkeypatch.setenv('BACKLOGOPS_CFG', str(tmp_path / 'no.json'))
    with pytest.raises(FileNotFoundError):
        get_available_teams(None, NO_OUTPUT)


def test_env_dir_missing(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing $BACKLOGOPS_DIR raises NotADirectoryError."""
    monkeypatch.setenv('BACKLOGOPS_DIR', str(tmp_path / 'no_dir'))
    with pytest.raises(NotADirectoryError):
        get_available_teams(None, NO_OUTPUT)


def test_env_dir_holds_config(tmp_path: Path,
                              monkeypatch: pytest.MonkeyPatch) -> None:
    """Test backlogops.cfg in $BACKLOGOPS_DIR is loaded."""
    _write_teams(tmp_path / 'backlogops.cfg')
    monkeypatch.setenv('BACKLOGOPS_DIR', str(tmp_path))
    assert get_available_teams(None, NO_OUTPUT) is not None


def test_home_config_used(tmp_path: Path) -> None:
    """Test $HOME/.backlogops.cfg is used as the last resort."""
    _write_teams(tmp_path / '.backlogops.cfg')
    assert get_available_teams(None, NO_OUTPUT) is not None


def test_no_config_found() -> None:
    """Test a RuntimeError is raised when no configuration is found."""
    with pytest.raises(RuntimeError):
        get_available_teams(None, NO_OUTPUT)


def test_not_found_lists() -> None:
    """Test the not-found error names the locations that were searched."""
    with pytest.raises(RuntimeError) as info:
        get_available_teams(None, NO_OUTPUT)
    message = str(info.value)
    assert 'BACKLOGOPS_CFG' in message
    assert 'BACKLOGOPS_DIR' in message
    assert '.backlogops.cfg' in message
