#! /usr/local/bin/python3
"""Tests for native path picking and validation of the wizard bridge."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
import pytest
from tableio_cfg_json import PathAskOptions, WizardPathKind
from backlogops_gui.wizard_path import PathRow, pick_path, validate_path, \
    _start_location
from .gui_test_helpers import gui_root


def test_empty_required() -> None:
    """Test an empty answer with no default is re-asked."""
    done, path, reason = validate_path('', PathAskOptions())
    assert done is False and path is None and reason is not None


def test_empty_default() -> None:
    """Test an empty answer takes the option's default path."""
    default = Path('/somewhere/file')
    done, path, reason = validate_path('', PathAskOptions(default=default))
    assert (done, path, reason) == (True, default, None)


def test_empty_nullable() -> None:
    """Test an empty answer is None when the question is nullable."""
    result = validate_path('', PathAskOptions(nullable=True))
    assert result == (True, None, None)


def test_existing_file_ok(tmp_path: Path) -> None:
    """Test an existing file is accepted for EXISTING_FILE."""
    target = tmp_path / 'a.txt'
    target.write_text('x')
    options = PathAskOptions(kind=WizardPathKind.EXISTING_FILE)
    done, path, reason = validate_path(str(target), options)
    assert done is True and path == target and reason is None


def test_missing_file(tmp_path: Path) -> None:
    """Test a missing path is rejected for EXISTING_FILE."""
    options = PathAskOptions(kind=WizardPathKind.EXISTING_FILE)
    done, path, reason = validate_path(str(tmp_path / 'no.txt'), options)
    assert done is False and path is None
    assert reason is not None and 'does not exist' in reason


def test_new_file_exists(tmp_path: Path) -> None:
    """Test an existing path is rejected for NON_EXISTING_FILE."""
    target = tmp_path / 'a.txt'
    target.write_text('x')
    options = PathAskOptions(kind=WizardPathKind.NON_EXISTING_FILE)
    done, _, reason = validate_path(str(target), options)
    assert done is False and reason is not None and 'already exists' in reason


def test_dir_not_file(tmp_path: Path) -> None:
    """Test an existing directory is rejected where a file is wanted."""
    options = PathAskOptions(kind=WizardPathKind.FILE)
    done, _, reason = validate_path(str(tmp_path), options)
    assert done is False and reason is not None and 'not a file' in reason


def test_file_not_dir(tmp_path: Path) -> None:
    """Test an existing file is rejected where a directory is wanted."""
    target = tmp_path / 'a.txt'
    target.write_text('x')
    options = PathAskOptions(kind=WizardPathKind.DIR)
    done, _, reason = validate_path(str(target), options)
    assert done is False and reason is not None and 'not a directory' in reason


def test_existing_dir_ok(tmp_path: Path) -> None:
    """Test an existing directory is accepted for EXISTING_DIR."""
    options = PathAskOptions(kind=WizardPathKind.EXISTING_DIR)
    done, path, reason = validate_path(str(tmp_path), options)
    assert done is True and path == tmp_path and reason is None


def test_start_loc_seed() -> None:
    """Test the initial directory and file come from the seed text."""
    assert _start_location('/a/b/c.csv', None) == ('/a/b', 'c.csv')


def test_start_loc_default() -> None:
    """Test the default path seeds the location when no text is given."""
    assert _start_location('', Path('/a/b')) == ('/a', 'b')


def test_start_loc_empty() -> None:
    """Test an empty seed and no default give an empty location."""
    assert _start_location('', None) == ('', '')


PICKERS: list[tuple[WizardPathKind, str]] = [
    (WizardPathKind.EXISTING_FILE, 'askopenfilename'),
    (WizardPathKind.FILE, 'asksaveasfilename'),
    (WizardPathKind.NON_EXISTING_FILE, 'asksaveasfilename'),
    (WizardPathKind.EXISTING_DIR, 'askdirectory'),
    (WizardPathKind.NON_EXISTING_DIR, 'askdirectory'),
    (WizardPathKind.DIR, 'askdirectory')]
"""Each path kind paired with the native dialog its picker opens."""


@pytest.mark.parametrize('kind, dialog', PICKERS)
def test_pick_path(monkeypatch: pytest.MonkeyPatch, kind: WizardPathKind,
                   dialog: str) -> None:
    """Test the picker opens the dialog matching the path kind."""
    target = f'backlogops_gui.wizard_path.filedialog.{dialog}'
    with gui_root() as root:
        monkeypatch.setattr(target, lambda **kw: 'chosen')
        options = PathAskOptions(kind=kind)
        assert pick_path(root, options, '') == 'chosen'
        monkeypatch.setattr(target, lambda **kw: '')
        assert pick_path(root, options, '') is None


def test_path_row_get() -> None:
    """Test a path row returns its pre-filled text."""
    with gui_root() as root:
        row = PathRow(root, PathAskOptions(), '/seed')
        assert row.get() == '/seed'


def test_path_row_disable() -> None:
    """Test disabling a path row disables its entry and button."""
    with gui_root() as root:
        row = PathRow(root, PathAskOptions(), '')
        row.set_enabled(False)
        # pylint: disable-next=protected-access
        assert str(row._entry.cget('state')) == 'disabled'
        # pylint: disable-next=protected-access
        assert str(row._button.cget('state')) == 'disabled'
        row.set_enabled(True)
        # pylint: disable-next=protected-access
        assert str(row._entry.cget('state')) == 'normal'


def test_path_row_browse(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test browsing fills the entry and fires the change callback."""
    seen: list[int] = []

    def changed() -> None:
        """Record that the change callback ran."""
        seen.append(1)
    with gui_root() as root:
        monkeypatch.setattr('backlogops_gui.wizard_path.pick_path',
                            lambda *a: '/picked')
        row = PathRow(root, PathAskOptions(), '', changed)
        # pylint: disable-next=protected-access
        row._browse()
        assert row.get() == '/picked'
        assert seen == [1]


def test_path_row_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the picker keeps the existing text unchanged."""
    with gui_root() as root:
        monkeypatch.setattr('backlogops_gui.wizard_path.pick_path',
                            lambda *a: None)
        row = PathRow(root, PathAskOptions(), 'keep')
        # pylint: disable-next=protected-access
        row._browse()
        assert row.get() == 'keep'
