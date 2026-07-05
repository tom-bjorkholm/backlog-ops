#! /usr/local/bin/python3
"""Modal dialogs collecting the options for the Jira operations.

Reading from Jira picks a Jira preset and an editable issue filter. Adding
to Jira picks a write preset and whether to skip items whose key already
exists. Updating releases picks a preset, what to do with a missing
release name, and which releases to update. Updating the backlog picks a
preset, what to do with a missing item key, which columns to update, and
how parent and dependency links are reconciled. A separate dialog collects
the masked pass phrase for an encrypted Jira API token.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import messagebox, ttk
from dataclasses import dataclass
from collections.abc import Mapping
from typing import Optional, Sequence
from backlogops import OnMissingKey
from backlogops_gui.gui_style import style_input
from backlogops_gui.modal_dialog import ModalDialog

MISSING_MODE_TEXT = {
    OnMissingKey.RAISE: 'Stop with an error',
    OnMissingKey.IGNORE: 'Ignore it',
    OnMissingKey.ADD: 'Add it to Jira'}
"""Label shown for each missing-name mode in the release-update dialog."""


LINK_MODE_TEXT = {
    'reconcile': 'Reconcile (also remove links the backlog no longer has)',
    'add': 'Only add missing links'}
"""Label shown for each link-update mode in the backlog-update dialog.

The keys mirror the CLI ``--links`` values; ``reconcile`` maps to
:class:`LinkUpdate.RECONCILE` and ``add`` to :class:`LinkUpdate.ADD_MISSING`.
"""


@dataclass
class JiraPresetOptions:
    """Base for the Jira option dataclasses that name a Jira preset."""

    preset_name: str


@dataclass
class JiraReadOptions(JiraPresetOptions):
    """The Jira preset and issue filter selected for reading from Jira."""

    issue_filter: str


@dataclass
class JiraWriteOptions(JiraPresetOptions):
    """The Jira write preset and existing-key choice for adding to Jira."""

    skip_existing: bool


@dataclass
class JiraReleaseUpdateOptions(JiraPresetOptions):
    """The preset, missing-name mode and selected names for updating."""

    on_missing: OnMissingKey
    selected: list[str]


@dataclass
class JiraBacklogUpdateOptions(JiraPresetOptions):
    """The preset, missing-key mode, fields and link policy for updating."""

    on_missing: OnMissingKey
    fields: list[str]
    reconcile_links: bool


# pylint: disable-next=too-few-public-methods
class JiraReadDialog(ModalDialog):
    """Modal dialog collecting the Jira preset and issue filter."""

    def __init__(self, parent: tk.Misc,
                 preset_filters: Mapping[str, str]) -> None:
        """Build, show and wait for the Jira read dialog."""
        super().__init__(parent, 'Read backlog from Jira')
        self.options: Optional[JiraReadOptions] = None
        self._filters = dict(preset_filters)
        names = sorted(self._filters)
        first = names[0] if names else ''
        self._preset = tk.StringVar(self._win, first)
        self._filter = tk.StringVar(self._win, self._filters.get(first, ''))
        self._build(names)
        self._show()

    def _build(self, names: Sequence[str]) -> None:
        """Add the preset chooser and editable filter field."""
        tk.Label(self._win, text='Jira preset:').pack(anchor='w', padx=12,
                                                      pady=(10, 2))
        box = ttk.Combobox(self._win, textvariable=self._preset,
                           values=list(names), state='readonly', width=35)
        box.bind('<<ComboboxSelected>>', self._preset_changed)
        style_input(box)
        box.pack(anchor='w', padx=12)
        tk.Label(self._win, text='Jira issue filter:'
                 ).pack(anchor='w', padx=12, pady=(8, 2))
        entry = tk.Entry(self._win, textvariable=self._filter, width=80)
        style_input(entry)
        entry.pack(anchor='w', padx=12, fill='x')

    def _preset_changed(self, _event: object) -> None:
        """Show the selected preset's default issue filter."""
        self._filter.set(self._filters.get(self._preset.get(), ''))

    def _confirm(self) -> None:
        """Store the selected preset and filter, requiring a preset."""
        name = self._preset.get()
        if not name:
            messagebox.showerror('No Jira preset', 'Select a Jira preset.',
                                 parent=self._win)
            return
        self.options = JiraReadOptions(name, self._filter.get())
        super()._confirm()


def ask_jira_read_options(parent: tk.Misc, preset_filters: Mapping[str, str]
                          ) -> Optional[JiraReadOptions]:
    """Ask which Jira preset and filter to read, or None when cancelled."""
    dialog = JiraReadDialog(parent, preset_filters)
    if dialog.cancelled:
        return None
    return dialog.options


# pylint: disable-next=too-few-public-methods
class JiraWriteDialog(ModalDialog):
    """Modal dialog collecting the Jira write preset and skip choice."""

    def __init__(self, parent: tk.Misc, presets: Sequence[str]) -> None:
        """Build, show and wait for the Jira write dialog."""
        super().__init__(parent, 'Add backlog to Jira')
        self.options: Optional[JiraWriteOptions] = None
        names = sorted(presets)
        self._preset = tk.StringVar(self._win, names[0] if names else '')
        self._skip = tk.BooleanVar(self._win, False)
        self._build(names)
        self._show()

    def _build(self, names: Sequence[str]) -> None:
        """Add the preset chooser and the skip-existing checkbox."""
        tk.Label(self._win, text='Jira write preset:'
                 ).pack(anchor='w', padx=12, pady=(10, 2))
        box = ttk.Combobox(self._win, textvariable=self._preset,
                           values=list(names), state='readonly', width=35)
        style_input(box)
        box.pack(anchor='w', padx=12)
        tk.Checkbutton(self._win, variable=self._skip,
                       text='Skip items whose key already exists in Jira'
                       ).pack(anchor='w', padx=12, pady=(8, 2))

    def _confirm(self) -> None:
        """Store the selected preset and skip choice, requiring a preset."""
        name = self._preset.get()
        if not name:
            messagebox.showerror('No Jira preset',
                                 'Select a Jira write preset.',
                                 parent=self._win)
            return
        self.options = JiraWriteOptions(name, self._skip.get())
        super()._confirm()


def ask_jira_write_options(parent: tk.Misc, presets: Sequence[str]
                           ) -> Optional[JiraWriteOptions]:
    """Ask which write preset and skip choice, or None when cancelled."""
    dialog = JiraWriteDialog(parent, presets)
    if dialog.cancelled:
        return None
    return dialog.options


# pylint: disable-next=too-few-public-methods
class JiraReleaseUpdateDialog(ModalDialog):
    """Modal dialog for the release-update preset, mode and selection."""

    def __init__(self, parent: tk.Misc, presets: Sequence[str],
                 release_names: Sequence[str]) -> None:
        """Build, show and wait for the release-update dialog."""
        super().__init__(parent, 'Update releases in Jira')
        self.options: Optional[JiraReleaseUpdateOptions] = None
        names = sorted(presets)
        self._preset = tk.StringVar(self._win, names[0] if names else '')
        self._mode = tk.StringVar(self._win, OnMissingKey.RAISE.name)
        self._picks: dict[str, tk.BooleanVar] = {}
        self._build(names, release_names)
        self._show()

    def _build(self, names: Sequence[str],
               release_names: Sequence[str]) -> None:
        """Add the preset chooser, the mode radios and the release picks."""
        self._build_preset(names)
        self._build_mode()
        self._build_releases(release_names)

    def _build_preset(self, names: Sequence[str]) -> None:
        """Add the Jira preset label and read-only chooser."""
        tk.Label(self._win, text='Jira preset:').pack(anchor='w', padx=12,
                                                      pady=(10, 2))
        box = ttk.Combobox(self._win, textvariable=self._preset,
                           values=list(names), state='readonly', width=35)
        style_input(box)
        box.pack(anchor='w', padx=12)

    def _build_mode(self) -> None:
        """Add the radios choosing what to do with a missing release."""
        tk.Label(self._win, text='If a release name is not in Jira:'
                 ).pack(anchor='w', padx=12, pady=(8, 2))
        for mode, text in MISSING_MODE_TEXT.items():
            tk.Radiobutton(self._win, variable=self._mode, value=mode.name,
                           text=text).pack(anchor='w', padx=24)

    def _build_releases(self, release_names: Sequence[str]) -> None:
        """Add a checkbox per release, all selected by default."""
        tk.Label(self._win, text='Releases to update:').pack(anchor='w',
                                                             padx=12,
                                                             pady=(8, 2))
        for name in release_names:
            var = tk.BooleanVar(self._win, True)
            self._picks[name] = var
            check = tk.Checkbutton(self._win, variable=var, text=name)
            check.pack(anchor='w', padx=24)

    def _confirm(self) -> None:
        """Store the preset, mode and picks, requiring a preset."""
        name = self._preset.get()
        if not name:
            messagebox.showerror('No Jira preset', 'Select a Jira preset.',
                                 parent=self._win)
            return
        selected = [pick for pick, var in self._picks.items() if var.get()]
        mode = OnMissingKey[self._mode.get()]
        self.options = JiraReleaseUpdateOptions(name, mode, selected)
        super()._confirm()


def ask_release_update(parent: tk.Misc, presets: Sequence[str],
                       release_names: Sequence[str]
                       ) -> Optional[JiraReleaseUpdateOptions]:
    """Ask the preset, missing-name mode and releases, None when cancelled."""
    dialog = JiraReleaseUpdateDialog(parent, presets, release_names)
    if dialog.cancelled:
        return None
    return dialog.options


# pylint: disable-next=too-few-public-methods,too-many-instance-attributes
class JiraBacklogUpdateDialog(ModalDialog):
    """Modal dialog for the backlog-update preset, mode, fields and links.

    The field checkboxes depend on the selected preset, so they are rebuilt
    whenever the preset changes. ``preset_fields`` maps each preset name to
    the internal fields it can update.
    """

    def __init__(self, parent: tk.Misc,
                 preset_fields: Mapping[str, Sequence[str]]) -> None:
        """Build, show and wait for the backlog-update dialog."""
        super().__init__(parent, 'Update backlog in Jira')
        self.options: Optional[JiraBacklogUpdateOptions] = None
        self._fields = {name: list(fields)
                        for name, fields in preset_fields.items()}
        names = sorted(self._fields)
        self._preset = tk.StringVar(self._win, names[0] if names else '')
        self._mode = tk.StringVar(self._win, OnMissingKey.RAISE.name)
        self._links = tk.StringVar(self._win, 'reconcile')
        self._picks: dict[str, tk.BooleanVar] = {}
        self._fields_frame = tk.Frame(self._win)
        self._build(names)
        self._show()

    def _build(self, names: Sequence[str]) -> None:
        """Add the preset, the mode radios, the links box and the fields."""
        self._build_preset(names)
        self._build_mode()
        self._build_links()
        tk.Label(self._win, text='Columns to update:'
                 ).pack(anchor='w', padx=12, pady=(8, 2))
        self._fields_frame.pack(anchor='w', fill='x')
        self._build_fields()

    def _build_preset(self, names: Sequence[str]) -> None:
        """Add the Jira preset label and read-only chooser."""
        tk.Label(self._win, text='Jira preset:').pack(anchor='w', padx=12,
                                                      pady=(10, 2))
        box = ttk.Combobox(self._win, textvariable=self._preset,
                           values=list(names), state='readonly', width=35)
        box.bind('<<ComboboxSelected>>', self._preset_changed)
        style_input(box)
        box.pack(anchor='w', padx=12)

    def _build_mode(self) -> None:
        """Add the radios choosing what to do with a missing key."""
        tk.Label(self._win, text='If an item key is not in Jira:'
                 ).pack(anchor='w', padx=12, pady=(8, 2))
        for mode, text in MISSING_MODE_TEXT.items():
            tk.Radiobutton(self._win, variable=self._mode, value=mode.name,
                           text=text).pack(anchor='w', padx=24)

    def _build_links(self) -> None:
        """Add the radios choosing how parent and dependency links update."""
        tk.Label(self._win, text='Parent and dependency links:'
                 ).pack(anchor='w', padx=12, pady=(8, 2))
        for value, text in LINK_MODE_TEXT.items():
            tk.Radiobutton(self._win, variable=self._links, value=value,
                           text=text).pack(anchor='w', padx=24)

    def _build_fields(self) -> None:
        """Rebuild the field checkboxes for the selected preset."""
        for child in self._fields_frame.winfo_children():
            child.destroy()
        self._picks = {}
        for name in self._fields.get(self._preset.get(), []):
            var = tk.BooleanVar(self._win, True)
            self._picks[name] = var
            tk.Checkbutton(self._fields_frame, variable=var, text=name
                           ).pack(anchor='w', padx=24)

    def _preset_changed(self, _event: object) -> None:
        """Rebuild the field checkboxes for the newly selected preset."""
        self._build_fields()

    def _confirm(self) -> None:
        """Store the preset, mode, fields and link policy, requiring both."""
        name = self._preset.get()
        if not name:
            messagebox.showerror('No Jira preset', 'Select a Jira preset.',
                                 parent=self._win)
            return
        fields = [pick for pick, var in self._picks.items() if var.get()]
        if not fields:
            messagebox.showerror('No columns', 'Select at least one column.',
                                 parent=self._win)
            return
        self.options = JiraBacklogUpdateOptions(name, OnMissingKey[
            self._mode.get()], fields, self._links.get() == 'reconcile')
        super()._confirm()


def ask_backlog_update(parent: tk.Misc,
                       preset_fields: Mapping[str, Sequence[str]]
                       ) -> Optional[JiraBacklogUpdateOptions]:
    """Ask the preset, mode, fields and link policy, None when cancelled."""
    dialog = JiraBacklogUpdateDialog(parent, preset_fields)
    if dialog.cancelled:
        return None
    return dialog.options


# pylint: disable-next=too-few-public-methods
class PassphraseDialog(ModalDialog):
    """Modal dialog collecting a masked pass phrase."""

    def __init__(self, parent: tk.Misc) -> None:
        """Build, show and wait for the pass phrase dialog."""
        super().__init__(parent, 'Jira API token pass phrase')
        self.passphrase: Optional[str] = None
        self._text = tk.StringVar(self._win)
        self._build()
        self._show()

    def _build(self) -> None:
        """Add the masked pass phrase entry."""
        tk.Label(self._win, text='Jira API token pass phrase:'
                 ).pack(anchor='w', padx=12, pady=(10, 2))
        entry = tk.Entry(self._win, textvariable=self._text, width=40,
                         show='*')
        style_input(entry)
        entry.pack(anchor='w', padx=12)

    def _confirm(self) -> None:
        """Store the entered pass phrase and close the dialog."""
        self.passphrase = self._text.get()
        super()._confirm()


def ask_jira_passphrase(parent: tk.Misc) -> Optional[str]:
    """Ask for the Jira token pass phrase, or None when cancelled."""
    dialog = PassphraseDialog(parent)
    if dialog.cancelled:
        return None
    return dialog.passphrase
