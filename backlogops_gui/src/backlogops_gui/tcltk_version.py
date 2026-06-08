#! /usr/local/bin/python3
"""Tcl/Tk version checks for the backlog operations GUI."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import tkinter as tk
from typing import Optional, Protocol, runtime_checkable


MIN_TCLTK_VERSION = (9, 0, 2)
MIN_TCLTK_VERSION_TEXT = '9.0.2'


@runtime_checkable
class TclInterpreter(Protocol):  # pylint: disable=too-few-public-methods
    """Small part of the Tcl interpreter API used by the GUI."""

    def call(self, *args: object) -> object:
        """Call the Tcl interpreter and return the Tcl result."""
        raise NotImplementedError


class TclTkRoot(Protocol):  # pylint: disable=too-few-public-methods
    """Root object exposing the Tcl interpreter used by Tkinter."""

    @property
    def tk(self) -> object:
        """Return the Tcl interpreter object."""
        raise NotImplementedError


def _parse_tcltk_version(version_text: str) -> Optional[tuple[int, int, int]]:
    """Return a comparable Tcl/Tk version tuple, or None if malformed."""
    parts = version_text.split('.')
    if len(parts) != 3:
        return None
    version_parts: list[int] = []
    for part in parts:
        if not part.isdecimal():
            return None
        version_parts.append(int(part))
    return (version_parts[0], version_parts[1], version_parts[2])


def _old_version_warning(version_text: str) -> str:
    """Return the warning text for an older Tcl/Tk version."""
    return (
        'This application was developed for Tcl/Tk version '
        f'{MIN_TCLTK_VERSION_TEXT} or newer, but you are running version '
        f'{version_text}. This may affect the functionality.'
    )


def _bad_version_warning(version_text: str) -> str:
    """Return the warning text for malformed or unreadable version data."""
    return (
        'This application was developed for Tcl/Tk version '
        f'{MIN_TCLTK_VERSION_TEXT} or newer, but the running Tcl/Tk version '
        f'value {version_text!r} is malformed or cannot be read. '
        'This may affect the functionality.'
    )


def warning_for_version(version_text: str) -> Optional[str]:
    """Return a warning for unsupported Tcl/Tk versions, if needed."""
    version_tuple = _parse_tcltk_version(version_text)
    if version_tuple is None:
        return _bad_version_warning(version_text)
    if version_tuple < MIN_TCLTK_VERSION:
        return _old_version_warning(version_text)
    return None


def check_tcltk_version(root: TclTkRoot) -> Optional[str]:
    """Return a warning if the running Tcl/Tk version may be unsuitable."""
    tcl_interpreter = root.tk
    if not isinstance(tcl_interpreter, TclInterpreter):
        return _bad_version_warning(str(tcl_interpreter))
    try:
        version_value = tcl_interpreter.call('info', 'patchlevel')
    except (RuntimeError, tk.TclError) as error:
        return _bad_version_warning(str(error))
    return warning_for_version(str(version_value))
