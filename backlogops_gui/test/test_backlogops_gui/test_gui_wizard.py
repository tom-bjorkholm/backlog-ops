#! /usr/local/bin/python3
"""Tests for the Tkinter wizard bridge."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from pathlib import Path
from typing import Sequence, cast
import pytest
from tableio_cfg_json import AnswerChoiceField, AnswerTextField, AskField, \
    AskChoiceField, AskTextField, PathAskOptions, TableCell, TableColumn, \
    WizardAbort, WizardBack, WizardCancelLevel, WizardPathKind
from backlogops import NoTextIO
from backlogops_gui.gui_wizard import TkWizardBridge
from .gui_test_helpers import gui_root


def _drive(root: tk.Tk, bridge: TkWizardBridge,
           answers: Sequence[object]) -> None:
    """Schedule finishing each prompt with the next queued answer."""
    queue = list(answers)

    def step() -> None:
        """Finish the current prompt, then queue the next finish."""
        # pylint: disable-next=protected-access
        window = bridge._window_obj()
        # pylint: disable-next=protected-access
        window._finish(queue.pop(0))
        if queue:
            root.after(0, step)
    root.after(0, step)


def test_error_file_is_sink() -> None:
    """Test the diagnostics stream discards its output without a log."""
    bridge = TkWizardBridge(cast(tk.Misc, object()))
    assert isinstance(bridge.error_file(), NoTextIO)


def test_error_file_uses_log() -> None:
    """Test diagnostics go to the provided log when one is given."""
    log = NoTextIO()
    bridge = TkWizardBridge(cast(tk.Misc, object()), log)
    assert bridge.error_file() is log


def test_close_without_window() -> None:
    """Test closing is safe when no wizard window was opened."""
    TkWizardBridge(cast(tk.Misc, object())).close()


def test_real_text() -> None:
    """Test a real window returns the entered free text."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish('typed'))
        assert bridge.ask_text('Name?') == 'typed'
        bridge.close()


def test_real_text_null() -> None:
    """Test an empty answer is reported as None when the cell is nullable."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish(''))
        assert bridge.ask_text('Name?', nullable=True) is None
        bridge.close()


def test_real_text_empty() -> None:
    """Test an empty answer is the empty string when not nullable."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish(''))
        assert bridge.ask_text('Name?') == ''
        bridge.close()


def test_real_reask() -> None:
    """Test a re-ask reason is shown above the question."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish('again'))
        assert bridge.ask_text('Name?', 'try again') == 'again'
        bridge.close()


def test_real_reuse_window() -> None:
    """Test a second question reuses the window and clears the first."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish('one'))
        assert bridge.ask_text('Q1?') == 'one'
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish('two'))
        assert bridge.ask_text('Q2?') == 'two'
        bridge.close()


def test_real_yes_no() -> None:
    """Test a real window returns the yes/no choice."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish(True))
        assert bridge.ask_yes_no('Add?', False) is True
        bridge.close()


def test_real_choice() -> None:
    """Test a real window returns the selected choice value."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish('b'))
        assert bridge.ask_choice('Pick', choices=['a', 'b', 'c']) == 'b'
        bridge.close()


def test_real_multi() -> None:
    """Test a real window returns the selected choice values."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish(['a', 'c']))
        assert bridge.ask_multi('Pick', choices=['a', 'b', 'c']) == ['a', 'c']
        bridge.close()


def test_real_table() -> None:
    """Test a real window returns the table the user filled in."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        columns = [TableColumn(header='X')]
        cells = [[TableCell(value='v')]]
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish([['v']]))
        assert bridge.ask_table(columns, cells, 'Q') == [['v']]
        bridge.close()


def test_table_variable_add() -> None:
    """Test a variable table returns the seed row plus an added row."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        columns = [TableColumn(header='Src'), TableColumn(header='Dst')]
        cells = [[TableCell(value='a'), TableCell(value='b')]]

        def drive() -> None:
            # pylint: disable-next=protected-access
            window = bridge._window_obj()
            # pylint: disable-next=protected-access
            assert window._editor is not None
            # pylint: disable-next=protected-access
            window._editor.add_row()
            # pylint: disable-next=protected-access
            window._finish(window._editor.values())

        root.after(0, drive)
        result = bridge.ask_table(columns, cells, 'Q', min_rows=0, max_rows=3)
        assert result == [['a', 'b'], ['a', 'b']]
        bridge.close()


def test_real_show_and_close() -> None:
    """Test showing a message opens the window, then close removes it."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        bridge.show('a message')
        bridge.close()


def test_real_abort() -> None:
    """Test the abort button raises a wizard-abort request."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._cancel())
        with pytest.raises(WizardAbort):
            bridge.ask_text('Name?')
        bridge.close()


def test_real_back() -> None:
    """Test the back button raises a wizard-back request."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._back())
        with pytest.raises(WizardBack):
            bridge.ask_text('Name?')
        bridge.close()


def test_real_cancel_level() -> None:
    """Test the out-one-level button raises a cancel-level request."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._cancel_level())
        with pytest.raises(WizardCancelLevel):
            bridge.ask_text('Name?')
        bridge.close()


def test_multi_min_select() -> None:
    """Test picking fewer than the minimum re-asks until enough are picked."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        _drive(root, bridge, [[], ['a']])
        assert bridge.ask_multi('Pick', choices=['a', 'b'],
                                min_select=1) == ['a']
        bridge.close()


def test_multi_max_select() -> None:
    """Test picking more than the maximum re-asks until few enough remain."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        _drive(root, bridge, [['a', 'b'], ['a']])
        assert bridge.ask_multi('Pick', choices=['a', 'b'],
                                max_select=1) == ['a']
        bridge.close()


def test_sensitive_default() -> None:
    """Test a sensitive question rejects a pre-filled default value."""
    bridge = TkWizardBridge(cast(tk.Misc, object()))
    with pytest.raises(ValueError):
        bridge.ask_text('PW?', default='x', sensitive=True)


def test_real_int() -> None:
    """Test a real window returns the entered integer."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish('7'))
        assert bridge.ask_int('N?') == 7
        bridge.close()


def test_int_default() -> None:
    """Test an empty integer answer keeps the pre-filled default."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish(''))
        assert bridge.ask_int('N?', default=3) == 3
        bridge.close()


def test_int_reask() -> None:
    """Test an invalid integer re-asks until an in-range value is given."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        _drive(root, bridge, ['x', '4'])
        assert bridge.ask_int('N?', min_value=1, max_value=10) == 4
        bridge.close()


def test_real_path(tmp_path: Path) -> None:
    """Test a real window returns the entered existing file path."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        target = tmp_path / 'f.txt'
        target.write_text('x')
        options = PathAskOptions(kind=WizardPathKind.EXISTING_FILE)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish(str(target)))
        assert bridge.ask_path('P?', options=options) == target
        bridge.close()


def test_path_nullable() -> None:
    """Test an empty path answer is None when the question is nullable."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._finish(''))
        options = PathAskOptions(nullable=True)
        assert bridge.ask_path('P?', options=options) is None
        bridge.close()


def test_path_reask(tmp_path: Path) -> None:
    """Test a missing path re-asks until an existing file is entered."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        target = tmp_path / 'f.txt'
        target.write_text('x')
        options = PathAskOptions(kind=WizardPathKind.EXISTING_FILE)
        _drive(root, bridge, [str(tmp_path / 'no.txt'), str(target)])
        assert bridge.ask_path('P?', options=options) == target
        bridge.close()


def test_real_form() -> None:
    """Test a real window returns every answer of a submitted form."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        name = AskTextField('Name', None, default='Bob')
        fmt = AskChoiceField('Fmt', None, choices=('a', 'b'), default='a')
        fields: list[AskField] = [name, fmt]

        def submit() -> None:
            """Submit the form once its window is built."""
            # pylint: disable-next=protected-access
            form = bridge._window_obj()._form
            assert form is not None
            form.submit()
        root.after(0, submit)
        answers = bridge.ask_form('Fill', fields)
        assert list(answers) == [AnswerTextField(name, 'Bob'),
                                 AnswerChoiceField(fmt, 'a')]
        bridge.close()


def test_form_back() -> None:
    """Test the back button on a form raises a wizard-back request."""
    with gui_root() as root:
        bridge = TkWizardBridge(root)
        fields = [AskTextField('Name', None)]
        # pylint: disable-next=protected-access
        root.after(0, lambda: bridge._window_obj()._back())
        with pytest.raises(WizardBack):
            bridge.ask_form('Fill', fields)
        bridge.close()
