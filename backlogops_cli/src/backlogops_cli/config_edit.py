#! /usr/local/bin/python3
"""Edit a configuration file in a full-screen terminal editor.

The whole configuration is shown at once, folded where it is deep, so a
single value can be changed without walking through every question the
wizard asks. The editor is the one of ``edit-cfg-json-textual``, so it needs
a terminal; where the input is redirected, the wizard command is the way in.

``-i`` says which file to edit and ``-k``/``--kind`` what kind of file it
is: the backlog-ops configuration, or a stand-alone input or output preset.
Without ``-o`` the file that was read is the file that Save writes, which is
what an editor is normally asked to do; with ``-o`` the input file is left
alone. Saving validates the whole configuration through its own class first
and refuses to write values the library would not read back, and what it
writes over is kept as that name plus ``.bak``.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from pathlib import Path
from typing import Optional
from config_as_json.file_extension import fix_file_extension
from edit_cfg_json import EditModel
from edit_cfg_json_textual import TextualEditor
from backlogops import (
    CONFIG_EXTENSION, default_edit_config, edit_model_for)
from backlogops_cli._command_io import add_kind_arg, kind_class, parsed_args

DESCRIPTION = 'Edit a configuration file in a full-screen editor'

EDIT_ERRORS = (ValueError, TypeError, KeyError, OSError)
"""Errors raised when the file to edit cannot be opened."""


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the config edit command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-i', '--input', dest='input', required=True,
                        help='Existing configuration file to edit. The '
                        f'{CONFIG_EXTENSION} extension is assumed when the '
                        'file is not found as named.')
    parser.add_argument('-o', '--output', dest='output',
                        help='Configuration file that Save writes. Without '
                        '-o the edited file is written, which leaves no '
                        f'second copy behind. The {CONFIG_EXTENSION} '
                        'extension is added to a name that has none.')
    add_kind_arg(parser)
    return parser


def _input_file(parsed: argparse.Namespace) -> str:
    """Return the file to edit, assuming the extension when needed.

    Raises:
        ValueError: Neither the given name nor the completed one is a file.
    """
    path = fix_file_extension(parsed.input, CONFIG_EXTENSION, for_reading=True)
    if not Path(path).is_file():
        raise ValueError(f'Configuration file to edit not found: {path}')
    return path


def _model_to_edit(parsed: argparse.Namespace) -> EditModel:
    """Return the edit model for the file and kind that were asked for.

    Raises:
        ValueError: The file cannot be found or cannot be opened for
            editing, or the class cannot be constructed.
    """
    return edit_model_for(default_edit_config(kind_class(parsed)),
                          in_file=_input_file(parsed), out_file=parsed.output,
                          stderr_file=sys.stderr)


def _report(model: EditModel) -> int:
    """Print what the session wrote, and answer with the exit code.

    Closing an editor is not a failure, so a session that saved nothing
    still succeeds; it says so, because a user who meant to save would
    otherwise be told nothing at all. What a save did is the editor's own
    message, which names the file it wrote and where what it wrote over is.
    """
    if model.saved_config is None:
        print('Closed without saving.')
        return 0
    print(model.save_message)
    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Open the configuration file in the editor and report what was saved.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` when the session ran, whether or not anything was saved,
        ``1`` when the file cannot be opened for editing.
    """
    parsed = parsed_args(build_parser(), args)
    try:
        model = _model_to_edit(parsed)
    except EDIT_ERRORS as error:
        print(f'Could not open the configuration: {error}', file=sys.stderr)
        return 1
    TextualEditor().run_editor(model)
    return _report(model)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
