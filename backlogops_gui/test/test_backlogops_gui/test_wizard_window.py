#! /usr/local/bin/python3
"""Tests for the reused wizard prompt window."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
import pytest
from backlogops_gui import wizard_window
from backlogops_gui.wizard_window import WizardWindow
from .gui_test_helpers import CloseSpy, gui_root


def test_choice_list_shown() -> None:
    """Test the choice list is packed and holds every choice.

    This guards against a regression where the single-selection list was
    built but never added to the window, so it stayed invisible.
    """
    with gui_root() as root:
        window = WizardWindow(tk.Frame(root))
        # pylint: disable-next=protected-access
        listbox = window._choice_list(['a', 'b', 'c'], None, 'browse')
        assert listbox.size() == 3
        assert listbox.winfo_manager() == 'pack'
        window.close()


def test_window_resizable() -> None:
    """Test the wizard window can be enlarged for large table questions."""
    with gui_root() as root:
        window = WizardWindow(tk.Frame(root))
        # pylint: disable-next=protected-access
        assert window._win.resizable() == (1, 1)
        window.close()


def test_buttons_at_bottom() -> None:
    """Test the wizard button row is anchored to the content bottom."""
    with gui_root() as root:
        window = WizardWindow(tk.Frame(root))
        # pylint: disable-next=protected-access
        window._add_buttons(lambda: None)
        # pylint: disable-next=protected-access
        button_bar = window._content.winfo_children()[-1]
        assert isinstance(button_bar, tk.Frame)
        assert button_bar.pack_info()['side'] == 'bottom'
        window.close()


def test_pick_one() -> None:
    """Test picking a single choice finishes with its value."""
    with gui_root() as root:
        window = WizardWindow(tk.Frame(root))
        # pylint: disable-next=protected-access
        listbox = tk.Listbox(window._content)
        listbox.insert('end', 'a')
        listbox.insert('end', 'b')
        listbox.selection_set(1)
        # pylint: disable-next=protected-access
        window._pick_one(listbox, ['a', 'b'])
        # pylint: disable-next=protected-access
        assert window._result == 'b'
        window.close()


def test_pick_many() -> None:
    """Test picking several choices finishes with the values in order."""
    with gui_root() as root:
        window = WizardWindow(tk.Frame(root))
        # pylint: disable-next=protected-access
        listbox = tk.Listbox(window._content, selectmode='multiple')
        for choice in ('a', 'b', 'c'):
            listbox.insert('end', choice)
        listbox.selection_set(0)
        listbox.selection_set(2)
        # pylint: disable-next=protected-access
        window._pick_many(listbox, ['a', 'b', 'c'])
        # pylint: disable-next=protected-access
        assert window._result == ['a', 'c']
        window.close()


def test_pick_one_none() -> None:
    """Test confirming a single choice with no selection picks nothing."""
    with gui_root() as root:
        window = WizardWindow(tk.Frame(root))
        # pylint: disable-next=protected-access
        listbox = tk.Listbox(window._content)
        listbox.insert('end', 'a')
        # pylint: disable-next=protected-access
        window._pick_one(listbox, ['a'])
        # pylint: disable-next=protected-access
        assert window._result == ''
        window.close()


def test_choice_preselect() -> None:
    """Test a default choice is preselected in the single-choice list.

    A string default marks one row, while a sequence default marks each
    of its rows, so the list opens with the configured values selected.
    """
    with gui_root() as root:
        window = WizardWindow(tk.Frame(root))
        # pylint: disable-next=protected-access
        listbox = window._choice_list(['a', 'b', 'c'], 'b', 'browse')
        selected = listbox.curselection()  # type: ignore[no-untyped-call]
        assert list(selected) == [1]
        # pylint: disable-next=protected-access
        assert WizardWindow._preset_indexes(['a', 'b', 'c'],
                                            ['a', 'c']) == [0, 2]
        window.close()


def test_text_sensitive() -> None:
    """Test a sensitive question masks the entry text."""
    with gui_root() as root:
        window = WizardWindow(tk.Frame(root))
        # pylint: disable-next=protected-access
        root.after(0, lambda: window._finish('secret'))
        result = window.ask_text('PW?', None, False, sensitive=True)
        assert result == 'secret'
        # pylint: disable-next=protected-access
        entries = [w for w in window._content.winfo_children()
                   if isinstance(w, tk.Entry)]
        assert entries and entries[0].cget('show') == '*'
        window.close()


def test_text_default() -> None:
    """Test an empty answer falls back to the pre-filled default."""
    with gui_root() as root:
        window = WizardWindow(tk.Frame(root))
        # pylint: disable-next=protected-access
        root.after(0, lambda: window._finish(''))
        assert window.ask_text('Name?', None, False, default='D') == 'D'
        window.close()


def test_binds_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the wizard window binds Cmd-W to its cancel action."""
    spy = CloseSpy()
    monkeypatch.setattr(wizard_window, 'bind_close', spy)
    with gui_root() as root:
        window = WizardWindow(tk.Frame(root))
        # pylint: disable-next=protected-access
        assert spy.calls == [(window._win, window._cancel)]
        window.close()
