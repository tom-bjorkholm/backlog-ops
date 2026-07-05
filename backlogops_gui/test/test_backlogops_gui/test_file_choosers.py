#! /usr/local/bin/python3
"""Tests for the native file choosers of the application."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Callable, Optional
import pytest
from backlogops_gui.file_choosers import (
    choose_changes_output, choose_config_file, choose_existing_config,
    choose_input_file, choose_key_list_output, choose_migrated_preset,
    choose_output_file, choose_preset_to_migrate)
from .gui_test_helpers import gui_root

CHOOSERS: list[tuple[Callable[[tk.Misc], Optional[str]], str]] = [
    (choose_input_file, 'askopenfilename'),
    (choose_output_file, 'asksaveasfilename'),
    (choose_config_file, 'asksaveasfilename'),
    (choose_existing_config, 'askopenfilename'),
    (choose_key_list_output, 'asksaveasfilename'),
    (choose_changes_output, 'asksaveasfilename'),
    (choose_preset_to_migrate, 'askopenfilename'),
    (choose_migrated_preset, 'asksaveasfilename')]
"""Each file chooser paired with the file dialog it calls."""


@pytest.mark.parametrize('func, dialog_name', CHOOSERS)
def test_choosers(monkeypatch: pytest.MonkeyPatch,
                  func: Callable[[tk.Misc], Optional[str]],
                  dialog_name: str) -> None:
    """Test a chooser returns the picked name, or None when cancelled."""
    target = f'backlogops_gui.file_choosers.filedialog.{dialog_name}'
    with gui_root() as root:
        monkeypatch.setattr(target, lambda **kw: 'picked.csv')
        assert func(root) == 'picked.csv'
        monkeypatch.setattr(target, lambda **kw: '')
        assert func(root) is None
