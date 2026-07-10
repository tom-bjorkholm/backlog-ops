#! /usr/local/bin/python3
"""Modal dialogs collecting the options for the Jira operations.

Reading from Jira picks a Jira preset and an editable issue filter. Adding
to Jira picks a write preset, whether to skip items whose key already
exists, and optionally a rank anchor. Updating releases picks a preset,
what to do with a missing release name, and which releases to update.
Updating the backlog picks a preset, what to do with a missing item key,
which columns to update, how parent and dependency links are reconciled,
and optionally a rank anchor. Ranking items picks a preset, filter, keys,
an anchor and whether to honour relations. A separate dialog collects the
masked pass phrase for an encrypted Jira API token.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dataclasses import dataclass
from collections.abc import Mapping
from typing import Optional, Sequence, TextIO
from backlogops import (
    JiraRankAnchor, OnMissingKey, ReleaseRename, read_key_list)
from backlogops_gui.gui_style import style_input
from backlogops_gui.modal_dialog import ModalDialog

KEY_READ_ERRORS = (ValueError, TypeError, KeyError, OSError)
"""Errors caught when loading a key list file into the rank dialog."""

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


RANK_ANCHOR_TEXT = {
    JiraRankAnchor.BACKLOG_TOP: 'Top of the backlog',
    JiraRankAnchor.BACKLOG_BOTTOM: 'Bottom of the backlog',
    JiraRankAnchor.FIRST_KEY: 'Keep the first listed item fixed',
    JiraRankAnchor.LAST_KEY: 'Keep the last listed item fixed'}
"""Label shown for each anchor in the rank dialogs."""


ORDER_MODE_TEXT = {
    'date': 'By release date (earliest first, undated last)',
    'window': 'By the order shown in this window',
    'names': 'By the names entered below (one per line)'}
"""Label shown for each order source in the release-order dialog."""


def _anchor_radios(win: tk.Misc, var: tk.StringVar) -> None:
    """Add the four rank-anchor radios bound to ``var`` to ``win``."""
    tk.Label(win, text='Rank anchor:').pack(anchor='w', padx=12, pady=(8, 2))
    for anchor, text in RANK_ANCHOR_TEXT.items():
        tk.Radiobutton(win, variable=var, value=anchor.name,
                       text=text).pack(anchor='w', padx=24)


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
    """The Jira write preset, existing-key choice and rank anchor to add."""

    skip_existing: bool
    rank_anchor: Optional[JiraRankAnchor]


@dataclass
class JiraReleaseUpdateOptions(JiraPresetOptions):
    """The preset, missing-name mode and selected names for updating."""

    on_missing: OnMissingKey
    selected: list[str]


@dataclass
class JiraBacklogUpdateOptions(JiraPresetOptions):
    """The preset, missing-key mode, fields, links and rank for updating."""

    on_missing: OnMissingKey
    fields: list[str]
    reconcile_links: bool
    rank_anchor: Optional[JiraRankAnchor]


@dataclass
class JiraRankOptions(JiraPresetOptions):
    """The preset, filter, keys, anchor and relations chosen for ranking."""

    issue_filter: str
    keys: list[str]
    anchor: JiraRankAnchor
    honor_relations: bool


@dataclass
class JiraRenameOptions(JiraPresetOptions):
    """The preset and old-to-new renames chosen for renaming releases."""

    renames: list[ReleaseRename]


@dataclass
class JiraOrderOptions(JiraPresetOptions):
    """The preset, order source and typed names chosen for ordering.

    ``mode`` is one of the keys of :data:`ORDER_MODE_TEXT`; ``names`` holds
    the names entered by the user and is only used for the ``names`` mode.
    """

    mode: str
    names: list[str]


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
        self._rank = tk.BooleanVar(self._win, False)
        self._anchor = tk.StringVar(self._win,
                                    JiraRankAnchor.BACKLOG_BOTTOM.name)
        self._build(names)
        self._show()

    def _build(self, names: Sequence[str]) -> None:
        """Add the preset chooser, skip checkbox and rank controls."""
        tk.Label(self._win, text='Jira write preset:'
                 ).pack(anchor='w', padx=12, pady=(10, 2))
        box = ttk.Combobox(self._win, textvariable=self._preset,
                           values=list(names), state='readonly', width=35)
        style_input(box)
        box.pack(anchor='w', padx=12)
        tk.Checkbutton(self._win, variable=self._skip,
                       text='Skip items whose key already exists in Jira'
                       ).pack(anchor='w', padx=12, pady=(8, 2))
        tk.Checkbutton(self._win, variable=self._rank,
                       text='Also set the Jira rank order to match this '
                       'backlog').pack(anchor='w', padx=12, pady=(8, 2))
        _anchor_radios(self._win, self._anchor)

    def _confirm(self) -> None:
        """Store the preset, skip and rank choices, requiring a preset."""
        name = self._preset.get()
        if not name:
            messagebox.showerror('No Jira preset',
                                 'Select a Jira write preset.',
                                 parent=self._win)
            return
        anchor = (JiraRankAnchor[self._anchor.get()] if self._rank.get()
                  else None)
        self.options = JiraWriteOptions(name, self._skip.get(), anchor)
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
        self._rank = tk.BooleanVar(self._win, False)
        self._anchor = tk.StringVar(self._win,
                                    JiraRankAnchor.BACKLOG_BOTTOM.name)
        self._picks: dict[str, tk.BooleanVar] = {}
        self._fields_frame = tk.Frame(self._win)
        self._build(names)
        self._show()

    def _build(self, names: Sequence[str]) -> None:
        """Add the preset, mode radios, links box, rank controls and fields."""
        self._build_preset(names)
        self._build_mode()
        self._build_links()
        self._build_rank()
        tk.Label(self._win, text='Columns to update:'
                 ).pack(anchor='w', padx=12, pady=(8, 2))
        self._fields_frame.pack(anchor='w', fill='x')
        self._build_fields()

    def _build_rank(self) -> None:
        """Add the opt-in rank checkbox and the anchor radios."""
        tk.Checkbutton(self._win, variable=self._rank,
                       text='Also set the Jira rank order to match this '
                       'backlog').pack(anchor='w', padx=12, pady=(8, 2))
        _anchor_radios(self._win, self._anchor)

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
        anchor = (JiraRankAnchor[self._anchor.get()] if self._rank.get()
                  else None)
        self.options = JiraBacklogUpdateOptions(
            name, OnMissingKey[self._mode.get()], fields,
            self._links.get() == 'reconcile', anchor)
        super()._confirm()


def ask_backlog_update(parent: tk.Misc,
                       preset_fields: Mapping[str, Sequence[str]]
                       ) -> Optional[JiraBacklogUpdateOptions]:
    """Ask the preset, mode, fields and link policy, None when cancelled."""
    dialog = JiraBacklogUpdateDialog(parent, preset_fields)
    if dialog.cancelled:
        return None
    return dialog.options


# pylint: disable-next=too-few-public-methods,too-many-instance-attributes
class JiraRankDialog(ModalDialog):
    """Modal dialog for the preset, filter, keys, anchor and relations."""

    def __init__(self, parent: tk.Misc, preset_filters: Mapping[str, str],
                 sink: TextIO) -> None:
        """Build, show and wait for the rank-items dialog."""
        super().__init__(parent, 'Rank items in Jira')
        self.options: Optional[JiraRankOptions] = None
        self._sink = sink
        self._filters = dict(preset_filters)
        names = sorted(self._filters)
        first = names[0] if names else ''
        self._preset = tk.StringVar(self._win, first)
        self._filter = tk.StringVar(self._win, self._filters.get(first, ''))
        self._anchor = tk.StringVar(self._win, JiraRankAnchor.BACKLOG_TOP.name)
        self._honor = tk.BooleanVar(self._win, False)
        self._text = self._build(names)
        self._show()

    def _build(self, names: Sequence[str]) -> tk.Text:
        """Add the preset, filter, anchor controls and the key entry box."""
        self._build_preset(names)
        self._build_filter()
        self._build_anchor()
        return self._build_keys()

    def _build_preset(self, names: Sequence[str]) -> None:
        """Add the Jira preset label and read-only chooser."""
        tk.Label(self._win, text='Jira preset:').pack(anchor='w', padx=12,
                                                      pady=(10, 2))
        box = ttk.Combobox(self._win, textvariable=self._preset,
                           values=list(names), state='readonly', width=35)
        box.bind('<<ComboboxSelected>>', self._preset_changed)
        style_input(box)
        box.pack(anchor='w', padx=12)

    def _build_filter(self) -> None:
        """Add the editable issue filter, prefilled from the preset."""
        tk.Label(self._win, text='Jira issue filter:'
                 ).pack(anchor='w', padx=12, pady=(8, 2))
        entry = tk.Entry(self._win, textvariable=self._filter, width=80)
        style_input(entry)
        entry.pack(anchor='w', padx=12, fill='x')

    def _build_anchor(self) -> None:
        """Add the anchor radios and the honour-relations checkbox."""
        _anchor_radios(self._win, self._anchor)
        tk.Checkbutton(self._win, variable=self._honor,
                       text='Honour dependencies and parent/child relations'
                       ).pack(anchor='w', padx=12, pady=(8, 2))

    def _build_keys(self) -> tk.Text:
        """Add the key entry label, text box and load-from-file button."""
        tk.Label(self._win,
                 text='Keys to move (separated by spaces or newlines):'
                 ).pack(anchor='w', padx=12, pady=(8, 2))
        text = tk.Text(self._win, width=40, height=8)
        style_input(text)
        text.pack(padx=12, pady=2)
        tk.Button(self._win, text='Load from file…',
                  command=self._load).pack(anchor='w', padx=12, pady=4)
        return text

    def _preset_changed(self, _event: object) -> None:
        """Show the selected preset's default issue filter."""
        self._filter.set(self._filters.get(self._preset.get(), ''))

    def _load(self) -> None:
        """Read a key list file into the text box, reporting failures."""
        name = filedialog.askopenfilename(parent=self._win,
                                          title='Read key list')
        if not name:
            return
        try:
            keys = read_key_list(name, stderr_file=self._sink)
        except KEY_READ_ERRORS as error:
            messagebox.showerror('Could not read key list', str(error),
                                 parent=self._win)
            return
        self._text.delete('1.0', 'end')
        self._text.insert('end', '\n'.join(keys))

    def _confirm(self) -> None:
        """Store the preset, filter, keys and end, requiring preset+keys."""
        name = self._preset.get()
        if not name:
            messagebox.showerror('No Jira preset', 'Select a Jira preset.',
                                 parent=self._win)
            return
        keys = self._text.get('1.0', 'end').split()
        if not keys:
            messagebox.showerror('No keys', 'Enter at least one key.',
                                 parent=self._win)
            return
        self.options = JiraRankOptions(name, self._filter.get(), keys,
                                       JiraRankAnchor[self._anchor.get()],
                                       self._honor.get())
        super()._confirm()


def ask_jira_rank(parent: tk.Misc, preset_filters: Mapping[str, str],
                  sink: TextIO) -> Optional[JiraRankOptions]:
    """Ask the preset, filter, keys, anchor and relations; None if cancel."""
    dialog = JiraRankDialog(parent, preset_filters, sink)
    if dialog.cancelled:
        return None
    return dialog.options


# pylint: disable-next=too-few-public-methods
class JiraRenameDialog(ModalDialog):
    """Modal dialog for the rename preset and a new name per release."""

    def __init__(self, parent: tk.Misc, presets: Sequence[str],
                 release_names: Sequence[str]) -> None:
        """Build, show and wait for the rename-releases dialog."""
        super().__init__(parent, 'Rename releases in Jira')
        self.options: Optional[JiraRenameOptions] = None
        names = sorted(presets)
        self._preset = tk.StringVar(self._win, names[0] if names else '')
        self._new: dict[str, tk.StringVar] = {}
        self._build(names, release_names)
        self._show()

    def _build(self, names: Sequence[str],
               release_names: Sequence[str]) -> None:
        """Add the preset chooser and a new-name entry per release."""
        tk.Label(self._win, text='Jira preset:').pack(anchor='w', padx=12,
                                                      pady=(10, 2))
        box = ttk.Combobox(self._win, textvariable=self._preset,
                           values=list(names), state='readonly', width=35)
        style_input(box)
        box.pack(anchor='w', padx=12)
        tk.Label(self._win, text='New name for each release (blank keeps it):'
                 ).pack(anchor='w', padx=12, pady=(8, 2))
        for name in release_names:
            self._add_rename_row(name)

    def _add_rename_row(self, name: str) -> None:
        """Add one labelled new-name entry for the release ``name``."""
        row = tk.Frame(self._win)
        row.pack(anchor='w', padx=24, fill='x')
        tk.Label(row, text=name, width=24, anchor='w').pack(side='left')
        var = tk.StringVar(self._win)
        self._new[name] = var
        entry = tk.Entry(row, textvariable=var, width=30)
        style_input(entry)
        entry.pack(side='left')

    def _renames(self) -> list[ReleaseRename]:
        """Return a rename for each entry that changes the release name."""
        renames: list[ReleaseRename] = []
        for old, var in self._new.items():
            new = var.get().strip()
            if new and new != old:
                renames.append(ReleaseRename(old, new))
        return renames

    def _confirm(self) -> None:
        """Store the preset and renames, requiring a preset and a rename."""
        name = self._preset.get()
        if not name:
            messagebox.showerror('No Jira preset', 'Select a Jira preset.',
                                 parent=self._win)
            return
        renames = self._renames()
        if not renames:
            messagebox.showerror('No renames', 'Enter at least one new name.',
                                 parent=self._win)
            return
        self.options = JiraRenameOptions(name, renames)
        super()._confirm()


def ask_jira_rename(parent: tk.Misc, presets: Sequence[str],
                    release_names: Sequence[str]
                    ) -> Optional[JiraRenameOptions]:
    """Ask the preset and renames, or None when cancelled."""
    dialog = JiraRenameDialog(parent, presets, release_names)
    if dialog.cancelled:
        return None
    return dialog.options


# pylint: disable-next=too-few-public-methods
class JiraOrderDialog(ModalDialog):
    """Modal dialog for the order preset, order source and typed names."""

    def __init__(self, parent: tk.Misc, presets: Sequence[str]) -> None:
        """Build, show and wait for the order-releases dialog."""
        super().__init__(parent, 'Order releases in Jira')
        self.options: Optional[JiraOrderOptions] = None
        names = sorted(presets)
        self._preset = tk.StringVar(self._win, names[0] if names else '')
        self._mode = tk.StringVar(self._win, 'date')
        self._text = self._build(names)
        self._show()

    def _build(self, names: Sequence[str]) -> tk.Text:
        """Add the preset chooser, the order-source radios and name box."""
        tk.Label(self._win, text='Jira preset:').pack(anchor='w', padx=12,
                                                      pady=(10, 2))
        box = ttk.Combobox(self._win, textvariable=self._preset,
                           values=list(names), state='readonly', width=35)
        style_input(box)
        box.pack(anchor='w', padx=12)
        tk.Label(self._win, text='Order the releases:').pack(anchor='w',
                                                             padx=12,
                                                             pady=(8, 2))
        for mode, text in ORDER_MODE_TEXT.items():
            tk.Radiobutton(self._win, variable=self._mode, value=mode,
                           text=text).pack(anchor='w', padx=24)
        return self._build_names()

    def _build_names(self) -> tk.Text:
        """Add the name entry box used by the by-names order source."""
        tk.Label(self._win, text='Names in wanted order (one per line):'
                 ).pack(anchor='w', padx=12, pady=(8, 2))
        text = tk.Text(self._win, width=40, height=8)
        style_input(text)
        text.pack(padx=12, pady=2)
        return text

    def _names(self) -> list[str]:
        """Return the entered names, one per non-blank line."""
        lines = self._text.get('1.0', 'end').splitlines()
        return [name for name in (line.strip() for line in lines) if name]

    def _confirm(self) -> None:
        """Store the preset, order source and names, requiring a preset."""
        name = self._preset.get()
        if not name:
            messagebox.showerror('No Jira preset', 'Select a Jira preset.',
                                 parent=self._win)
            return
        names = self._names()
        if self._mode.get() == 'names' and not names:
            messagebox.showerror('No names', 'Enter at least one name.',
                                 parent=self._win)
            return
        self.options = JiraOrderOptions(name, self._mode.get(), names)
        super()._confirm()


def ask_jira_order(parent: tk.Misc, presets: Sequence[str]
                   ) -> Optional[JiraOrderOptions]:
    """Ask the preset, order source and names, or None when cancelled."""
    dialog = JiraOrderDialog(parent, presets)
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
