#! /usr/local/bin/python3
"""Tests for the backlog-operation option dialogs and dataclasses."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
import pytest
from backlogops import DependencyMode, NoTextIO
from backlogops_gui.backlog_dialogs import (
    BufferDialog, DateOrderDialog, DepOptions, DepOptionsDialog, KeysDialog,
    LevelsDialog, ReleaseOrderDialog, ReleaseOrderOptions, StartChoice,
    StartDateDialog, ask_buffer_days, ask_date_order, ask_dep_options,
    ask_keys, ask_levels, ask_release_order, ask_start_date)
from backlogops_gui.modal_dialog import ModalDialog
from .gui_test_helpers import MsgRecorder, gui_root
from .dialog_test_helpers import cancel_show, confirm_show, no_wait

MESSAGEBOX = 'backlogops_gui.backlog_dialogs.messagebox'
ASK_OPEN = 'backlogops_gui.backlog_dialogs.filedialog.askopenfilename'


def test_action_dataclasses() -> None:
    """Test the action dataclasses hold the entered selection."""
    options = DepOptions(True, DependencyMode.EARLY, ['A'])
    assert options.later is True
    assert options.mode is DependencyMode.EARLY
    assert options.space_around == ['A']
    assert StartChoice(None).start_date is None
    assert StartChoice(date(2026, 6, 15)).start_date == date(2026, 6, 15)
    release = ReleaseOrderOptions(honor_dependencies=True, later=False)
    assert release.honor_dependencies is True
    assert release.later is False


def test_buffer_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the buffer dialog returns a valid number of days."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = BufferDialog(root)
        # pylint: disable-next=protected-access
        dialog._text.set('3')
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.days == 3


@pytest.mark.parametrize('text', ['x', '-1'])
def test_buffer_bad(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    """Test a non-numeric or negative buffer is rejected with an error."""
    rec = MsgRecorder()
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(MESSAGEBOX, rec)
    with gui_root() as root:
        dialog = BufferDialog(root)
        # pylint: disable-next=protected-access
        dialog._text.set(text)
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.days is None
        assert len(rec.calls) == 1


def test_ask_buffer_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled buffer dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_buffer_days(root) is None


def test_date_order_est(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the date order dialog stores the estimated choice."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = DateOrderDialog(root)
        # pylint: disable-next=protected-access
        dialog._estimated.set(True)
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.by_estimated is True


def test_date_order_planned(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the date order dialog defaults to the planned date."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = DateOrderDialog(root)
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.by_estimated is False


def test_ask_date_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the wrapper returns the confirmed planned-date choice."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        assert ask_date_order(root) is False


def test_ask_date_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled date order dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_date_order(root) is None


def test_release_order_honor(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the release-order dialog stores the honor and later choice."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = ReleaseOrderDialog(root)
        # pylint: disable-next=protected-access
        dialog._honor.set(True)
        # pylint: disable-next=protected-access
        dialog._later.set(True)
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.options is not None
        assert dialog.options.honor_dependencies is True
        assert dialog.options.later is True


def test_release_order_plain(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the release-order dialog defaults to plain release order."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = ReleaseOrderDialog(root)
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.options is not None
        assert dialog.options.honor_dependencies is False
        assert dialog.options.later is False


def test_ask_release_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the wrapper returns the confirmed release-order options."""
    monkeypatch.setattr(ModalDialog, '_show', confirm_show)
    with gui_root() as root:
        options = ask_release_order(root)
        assert options is not None
        assert options.honor_dependencies is False
        assert options.later is False


def test_ask_release_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled release-order dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_release_order(root) is None


def test_ask_wrappers_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test each ask wrapper returns the dialog result when confirmed."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        assert ask_buffer_days(root) is None
        assert ask_keys(root, NoTextIO()) is None
        assert ask_dep_options(root) is None
        assert ask_start_date(root) is None
        assert ask_levels(root) is None
        assert ask_release_order(root) is None


def test_keys_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the keys dialog splits the entered text into keys."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = KeysDialog(root, NoTextIO())
        # pylint: disable-next=protected-access
        dialog._text.insert('1.0', 'A B\nC')
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.keys == ['A', 'B', 'C']


def test_keys_load_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading keys from a file fills the text box."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(ASK_OPEN, lambda **kw: 'keys.txt')
    reader = 'backlogops_gui.backlog_dialogs.read_key_list'
    monkeypatch.setattr(reader, lambda name, stderr_file: ['X', 'Y'])
    with gui_root() as root:
        dialog = KeysDialog(root, NoTextIO())
        # pylint: disable-next=protected-access
        dialog._load()
        # pylint: disable-next=protected-access
        assert dialog._text.get('1.0', 'end').split() == ['X', 'Y']


def test_keys_load_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the load leaves the text box empty."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(ASK_OPEN, lambda **kw: '')
    with gui_root() as root:
        dialog = KeysDialog(root, NoTextIO())
        # pylint: disable-next=protected-access
        dialog._load()
        # pylint: disable-next=protected-access
        assert dialog._text.get('1.0', 'end').strip() == ''


def test_keys_load_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a key-list read failure is reported and loads nothing."""
    def boom(name: str, stderr_file: object) -> list[str]:
        raise ValueError('bad list')
    rec = MsgRecorder()
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(ASK_OPEN, lambda **kw: 'keys.txt')
    monkeypatch.setattr('backlogops_gui.backlog_dialogs.read_key_list', boom)
    monkeypatch.setattr(MESSAGEBOX, rec)
    with gui_root() as root:
        dialog = KeysDialog(root, NoTextIO())
        # pylint: disable-next=protected-access
        dialog._load()
        # pylint: disable-next=protected-access
        assert dialog._text.get('1.0', 'end').strip() == ''
        assert rec.calls == [('Could not read key list', 'bad list')]


def test_ask_keys_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled keys dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_keys(root, NoTextIO()) is None


def test_dep_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the dependency dialog keeps an empty space list as None."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = DepOptionsDialog(root)
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.options is not None
        assert dialog.options.space_around is None
        assert dialog.options.mode is DependencyMode.KEEP


def test_dep_space(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the dependency dialog captures the later, mode and space keys."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = DepOptionsDialog(root)
        # pylint: disable-next=protected-access
        dialog._later.set(True)
        # pylint: disable-next=protected-access
        dialog._mode.set(DependencyMode.EARLY.name)
        # pylint: disable-next=protected-access
        dialog._space.set('A B')
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.options is not None
        assert dialog.options.later is True
        assert dialog.options.mode is DependencyMode.EARLY
        assert dialog.options.space_around == ['A', 'B']


def test_ask_dep_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled dependency dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_dep_options(root) is None


def test_start_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an empty start date stands for today."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = StartDateDialog(root)
        # pylint: disable-next=protected-access
        dialog._date.set('')
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.choice is not None
        assert dialog.choice.start_date is None


def test_start_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a valid ISO date is captured as the start date."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = StartDateDialog(root)
        # pylint: disable-next=protected-access
        dialog._date.set('2026-06-15')
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.choice is not None
        assert dialog.choice.start_date == date(2026, 6, 15)


def test_start_bad(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an invalid start date is rejected with an error."""
    rec = MsgRecorder()
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(MESSAGEBOX, rec)
    with gui_root() as root:
        dialog = StartDateDialog(root)
        # pylint: disable-next=protected-access
        dialog._date.set('nope')
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.choice is None
        assert len(rec.calls) == 1


def test_ask_start_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled start date dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_start_date(root) is None


def test_levels_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the levels dialog returns the selected level numbers."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = LevelsDialog(root)
        # pylint: disable-next=protected-access
        number = sorted(dialog._chosen)[0]
        # pylint: disable-next=protected-access
        dialog._chosen[number].set(True)
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.levels == [number]


def test_levels_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test selecting no levels is rejected with an error."""
    rec = MsgRecorder()
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(MESSAGEBOX, rec)
    with gui_root() as root:
        dialog = LevelsDialog(root)
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.levels is None
        assert len(rec.calls) == 1


def test_ask_levels_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a cancelled levels dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_levels(root) is None
