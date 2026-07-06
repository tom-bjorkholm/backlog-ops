#! /usr/local/bin/python3
"""Tests for the Jira option dialogs and their option dataclasses."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from pathlib import Path
from typing import Callable
import tkinter as tk
import pytest
from backlogops import JiraMoveToEnd, NoTextIO, OnMissingKey
from backlogops_gui.jira_dialogs import (
    JiraBacklogUpdateDialog, JiraBacklogUpdateOptions, JiraRankDialog,
    JiraRankOptions, JiraReadDialog, JiraReadOptions, JiraReleaseUpdateDialog,
    JiraReleaseUpdateOptions, PassphraseDialog, ask_backlog_update,
    ask_jira_passphrase, ask_jira_rank, ask_jira_read_options,
    ask_release_update)
from backlogops_gui.modal_dialog import ModalDialog
from .gui_test_helpers import MsgRecorder, gui_root
from .dialog_test_helpers import cancel_show, no_wait

MESSAGEBOX = 'backlogops_gui.jira_dialogs.messagebox'
FILE_DIALOG = 'backlogops_gui.jira_dialogs.filedialog.askopenfilename'
_BL_FIELDS = {'p': ['title', 'status'], 'q': ['title', 'team']}
"""Two presets mapped to their updatable fields for the dialog tests."""


def _pick(path: str) -> Callable[..., str]:
    """Return a file chooser stand-in that returns the given path."""
    def choose(**_kwargs: object) -> str:
        return path
    return choose


def test_jira_options() -> None:
    """Test the Jira option dataclasses hold the entered selection."""
    jira = JiraReadOptions('scrum', 'project = SCRUM')
    assert jira.preset_name == 'scrum'
    assert jira.issue_filter == 'project = SCRUM'
    update = JiraReleaseUpdateOptions('scrum', OnMissingKey.ADD, ['R1'])
    assert update.preset_name == 'scrum'
    assert update.on_missing is OnMissingKey.ADD
    assert update.selected == ['R1']
    backlog = JiraBacklogUpdateOptions('scrum', OnMissingKey.RAISE, ['title'],
                                       True)
    assert backlog.fields == ['title']
    assert backlog.reconcile_links is True


def test_jira_select_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test selecting a Jira preset shows its default filter."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = JiraReadDialog(root, {'a': 'filter a', 'b': 'filter b'})
        # pylint: disable-next=protected-access
        dialog._preset.set('b')
        # pylint: disable-next=protected-access
        dialog._preset_changed(object())
        # pylint: disable-next=protected-access
        assert dialog._filter.get() == 'filter b'
        # pylint: disable-next=protected-access
        dialog._filter.set('edited')
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.options == JiraReadOptions('b', 'edited')


def test_jira_needs_preset(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test confirming without a Jira preset keeps the dialog open."""
    rec = MsgRecorder()
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(MESSAGEBOX, rec)
    with gui_root() as root:
        dialog = JiraReadDialog(root, {})
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.options is None
        assert rec.calls == [('No Jira preset', 'Select a Jira preset.')]


def test_jira_options_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the Jira read dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_jira_read_options(root, {'p': 'filter'}) is None


def test_rel_update_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the release-update dialog stores the preset, mode and picks."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = JiraReleaseUpdateDialog(root, ['p', 'q'], ['R1', 'R2'])
        # pylint: disable-next=protected-access
        dialog._mode.set(OnMissingKey.ADD.name)
        # pylint: disable-next=protected-access
        dialog._picks['R2'].set(False)
        # pylint: disable-next=protected-access
        dialog._confirm()
        expected = JiraReleaseUpdateOptions('p', OnMissingKey.ADD, ['R1'])
        assert dialog.options == expected


def test_rel_update_needs_p(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test confirming without a preset keeps the update dialog open."""
    rec = MsgRecorder()
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(MESSAGEBOX, rec)
    with gui_root() as root:
        dialog = JiraReleaseUpdateDialog(root, [], ['R1'])
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.options is None
        assert rec.calls == [('No Jira preset', 'Select a Jira preset.')]


def test_rel_update_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the release-update dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_release_update(root, ['p'], ['R1']) is None


@pytest.mark.parametrize('link, reconcile', [
    ('reconcile', True), ('add', False)])
def test_bl_update_ok(monkeypatch: pytest.MonkeyPatch, link: str,
                      reconcile: bool) -> None:
    """Test the dialog stores preset, mode, fields and link policy."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = JiraBacklogUpdateDialog(root, _BL_FIELDS)
        # pylint: disable-next=protected-access
        dialog._mode.set(OnMissingKey.ADD.name)
        # pylint: disable-next=protected-access
        dialog._links.set(link)
        # pylint: disable-next=protected-access
        dialog._picks['status'].set(False)
        # pylint: disable-next=protected-access
        dialog._confirm()
        expected = JiraBacklogUpdateOptions('p', OnMissingKey.ADD, ['title'],
                                            reconcile)
        assert dialog.options == expected


def test_bl_switch_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test switching the preset rebuilds the field checkboxes."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = JiraBacklogUpdateDialog(root, _BL_FIELDS)
        # pylint: disable-next=protected-access
        dialog._preset.set('q')
        # pylint: disable-next=protected-access
        dialog._preset_changed(None)
        # pylint: disable-next=protected-access
        assert sorted(dialog._picks) == ['team', 'title']


def test_bl_needs_field(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test confirming with no field ticked keeps the dialog open."""
    rec = MsgRecorder()
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(MESSAGEBOX, rec)
    with gui_root() as root:
        dialog = JiraBacklogUpdateDialog(root, _BL_FIELDS)
        # pylint: disable-next=protected-access
        for var in dialog._picks.values():
            var.set(False)
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.options is None
        assert rec.calls == [('No columns', 'Select at least one column.')]


def test_bl_update_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the backlog-update dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_backlog_update(root, _BL_FIELDS) is None


def test_passphrase_masked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the pass phrase dialog stores text in a masked entry."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = PassphraseDialog(root)
        # pylint: disable-next=protected-access
        entries = [w for w in dialog._win.winfo_children()
                   if isinstance(w, tk.Entry)]
        assert entries and entries[0].cget('show') == '*'
        # pylint: disable-next=protected-access
        dialog._text.set('secret')
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.passphrase == 'secret'


def test_pass_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the pass phrase dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_jira_passphrase(root) is None


def test_rank_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the rank dialog prefills the filter and stores the choice."""
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    with gui_root() as root:
        dialog = JiraRankDialog(root, {'a': 'fa', 'b': 'fb'}, NoTextIO())
        # pylint: disable-next=protected-access
        dialog._preset.set('b')
        # pylint: disable-next=protected-access
        dialog._preset_changed(object())
        # pylint: disable-next=protected-access
        assert dialog._filter.get() == 'fb'
        # pylint: disable-next=protected-access
        dialog._filter.set('project = X')
        # pylint: disable-next=protected-access
        dialog._end.set(JiraMoveToEnd.LAST.name)
        # pylint: disable-next=protected-access
        dialog._text.insert('1.0', 'X Y')
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.options == JiraRankOptions('b', 'project = X',
                                                 ['X', 'Y'],
                                                 JiraMoveToEnd.LAST)


def test_rank_load(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the load button fills the key box from a key list file."""
    keyfile = tmp_path / 'k.txt'
    keyfile.write_text('K1 K2\n', encoding='utf-8')
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(FILE_DIALOG, _pick(str(keyfile)))
    with gui_root() as root:
        dialog = JiraRankDialog(root, {'a': 'fa'}, NoTextIO())
        # pylint: disable-next=protected-access
        dialog._load()
        # pylint: disable-next=protected-access
        assert dialog._text.get('1.0', 'end').split() == ['K1', 'K2']


def test_rank_needs_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test confirming with no keys keeps the rank dialog open."""
    rec = MsgRecorder()
    monkeypatch.setattr(ModalDialog, '_show', no_wait)
    monkeypatch.setattr(MESSAGEBOX, rec)
    with gui_root() as root:
        dialog = JiraRankDialog(root, {'a': 'fa'}, NoTextIO())
        # pylint: disable-next=protected-access
        dialog._confirm()
        assert dialog.options is None
        assert rec.calls


def test_rank_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancelling the rank dialog returns nothing."""
    monkeypatch.setattr(ModalDialog, '_show', cancel_show)
    with gui_root() as root:
        assert ask_jira_rank(root, {'a': 'fa'}, NoTextIO()) is None
