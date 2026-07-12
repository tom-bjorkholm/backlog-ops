#! /usr/local/bin/python3
"""Native path picking and validation for the wizard bridge.

A path question in the Tkinter wizard shows an editable path entry next
to a Browse button that opens the native open-file, save-file or
directory dialog chosen by the :class:`WizardPathKind`. :func:`validate_path`
then checks the typed or picked path against the same rules the wizard's
console and textual bridges apply, so a graphical answer is accepted or
rejected the same way. :class:`PathRow` bundles the entry and the Browse
button, and is reused both by the standalone path question and by a path
field inside a form.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Callable, Optional
from tableio_cfg_json import PathAskOptions, WizardPathKind
from backlogops_gui.gui_style import style_input

_PATH_REQUIRED = 'Please enter a path.'
ENTRY_WIDTH = 34


def validate_path(text: str, options: PathAskOptions
                  ) -> tuple[bool, Optional[Path], Optional[str]]:
    """Return whether a path answer is final, its value, and a retry reason.

    An empty answer takes the default, is None when the question is
    nullable, or is re-asked otherwise. A non-empty answer becomes a Path
    and is checked against the option's WizardPathKind.
    """
    if text == '' and options.default is not None:
        return (True, options.default, None)
    if text == '' and options.nullable:
        return (True, None, None)
    if text == '':
        return (False, None, _PATH_REQUIRED)
    path = Path(text)
    reason = _path_error(path, options.kind)
    return (reason is None, path if reason is None else None, reason)


def _path_error(path: Path, kind: WizardPathKind) -> Optional[str]:
    """Return the validation error for a path, or None when accepted."""
    exists, error = _path_exists(path)
    if error is not None:
        return error
    if _must_not_exist(kind) and exists:
        return 'Path already exists.'
    if _must_exist(kind) and not exists:
        return 'Path does not exist.'
    if exists and _must_be_file(kind) and not path.is_file():
        return 'Path is not a file.'
    if exists and _must_be_dir(kind) and not path.is_dir():
        return 'Path is not a directory.'
    return None


def _path_exists(path: Path) -> tuple[bool, Optional[str]]:
    """Return whether a path exists, or an error for an unusable path."""
    try:
        return (path.exists(), None)
    except OSError as error:
        return (False, f'Invalid path: {error}.')


def _must_exist(kind: WizardPathKind) -> bool:
    """Return whether the kind requires an existing path."""
    return kind in (WizardPathKind.EXISTING_FILE, WizardPathKind.EXISTING_DIR)


def _must_not_exist(kind: WizardPathKind) -> bool:
    """Return whether the kind requires a path that does not exist."""
    return kind in (WizardPathKind.NON_EXISTING_FILE,
                    WizardPathKind.NON_EXISTING_DIR)


def _must_be_file(kind: WizardPathKind) -> bool:
    """Return whether the kind rejects an existing directory."""
    return kind in (WizardPathKind.EXISTING_FILE, WizardPathKind.FILE)


def _must_be_dir(kind: WizardPathKind) -> bool:
    """Return whether the kind rejects an existing file."""
    return kind in (WizardPathKind.EXISTING_DIR, WizardPathKind.DIR)


def _is_dir_kind(kind: WizardPathKind) -> bool:
    """Return whether the kind asks for a directory rather than a file."""
    return kind in (WizardPathKind.EXISTING_DIR,
                    WizardPathKind.NON_EXISTING_DIR, WizardPathKind.DIR)


def pick_path(parent: tk.Misc, options: PathAskOptions,
              initial: str) -> Optional[str]:
    """Open the native dialog for the kind, or None when cancelled."""
    initial_dir, initial_file = _start_location(initial, options.default)
    name = _open_dialog(parent, options.kind, initial_dir, initial_file)
    return name or None


def _start_location(initial: str, default: Optional[Path]) -> tuple[str, str]:
    """Return the initial directory and file name for a path dialog."""
    seed = initial or ('' if default is None else str(default))
    if seed == '':
        return ('', '')
    path = Path(seed)
    return (str(path.parent), path.name)


def _open_dialog(parent: tk.Misc, kind: WizardPathKind, initial_dir: str,
                 initial_file: str) -> str:
    """Open the open-file, save-file or directory dialog for a kind."""
    if _is_dir_kind(kind):
        return filedialog.askdirectory(parent=parent, initialdir=initial_dir)
    if kind == WizardPathKind.EXISTING_FILE:
        return filedialog.askopenfilename(parent=parent,
                                          initialdir=initial_dir,
                                          initialfile=initial_file)
    return filedialog.asksaveasfilename(parent=parent, initialdir=initial_dir,
                                        initialfile=initial_file)


class PathRow:
    """An editable path entry paired with a native Browse button."""

    def __init__(self, parent: tk.Misc, options: PathAskOptions, initial: str,
                 on_change: Optional[Callable[[], None]] = None) -> None:
        """Build the entry and Browse button inside a new frame."""
        self._options = options
        self._on_change = on_change
        self.frame = tk.Frame(parent)
        self._entry = tk.Entry(self.frame, width=ENTRY_WIDTH)
        if initial != '':
            self._entry.insert(0, initial)
        style_input(self._entry)
        self._entry.pack(side='left')
        self._button = tk.Button(self.frame, text='Browse…',
                                 command=self._browse)
        self._button.pack(side='left', padx=6)
        if on_change is not None:
            self._entry.bind('<KeyRelease>', lambda _event: on_change())

    def get(self) -> str:
        """Return the current path text."""
        return self._entry.get()

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable both the entry and the Browse button."""
        state = 'normal' if enabled else 'disabled'
        self._entry['state'] = state
        self._button['state'] = state

    def _browse(self) -> None:
        """Open the native picker and fill the entry with the choice."""
        chosen = pick_path(self.frame, self._options, self.get())
        if chosen is None:
            return
        self._entry.delete(0, 'end')
        self._entry.insert(0, chosen)
        if self._on_change is not None:
            self._on_change()
