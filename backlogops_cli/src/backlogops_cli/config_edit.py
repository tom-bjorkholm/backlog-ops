#! /usr/local/bin/python3
"""Edit a configuration file in a full-screen terminal editor.

The whole configuration is shown at once, folded where it is deep, so a
single value can be changed without walking through every question the
wizard asks. The editor is the one of ``edit-cfg-json-textual``, so it needs
a terminal; where the input is redirected, the wizard command is the way in.
One call runs the whole session: ``edit`` reads the file, shows it until the
user is done, and answers with the configuration that was saved.

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
from config_as_json import Config
from config_as_json.file_extension import fix_file_extension
from edit_cfg_json import ConfigLoadError, default_config
from edit_cfg_json_textual import edit
from backlogops import CONFIG_EXTENSION, EDIT_SETTINGS, descriptions_for
from backlogops_cli._command_io import add_kind_arg, kind_class, parsed_args

DESCRIPTION = 'Edit a configuration file in a full-screen editor'

EDIT_ERRORS = (ConfigLoadError, ValueError, TypeError, KeyError, OSError)
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


def _out_file(output: Optional[str], in_file: str) -> str:
    """Return the file a save writes, naming it as the editor will.

    Without ``-o`` that is the file that was read. A destination named on
    the command line is one this run chose, so it is given the
    configuration extension when it has none, which is what the editor
    would do with it; naming it here as well is what lets this command say
    afterwards which file was written.

    Args:
        output: The ``-o`` value, or None when there is none.
        in_file: The file that is being edited.

    Returns:
        The file that a save of this session writes.
    """
    if output is None:
        return in_file
    return output if Path(output).suffix else output + CONFIG_EXTENSION


def _edited(parsed: argparse.Namespace, in_file: str,
            out_file: str) -> Optional[Config]:
    """Run one editing session and return the configuration it saved.

    Args:
        parsed: The parsed command line, naming the kind of file to edit.
        in_file: The configuration file the editor reads.
        out_file: The configuration file a save writes.

    Returns:
        What the session saved, or None when it saved nothing.

    Raises:
        ConfigLoadError: The input file cannot be opened for editing.
    """
    config = default_config(kind_class(parsed))
    return edit(config, descriptions=descriptions_for(config), in_file=in_file,
                out_file=out_file, settings=EDIT_SETTINGS)


def main(args: Optional[list[str]] = None) -> int:
    """Open the configuration file in the editor and report what was saved.

    Closing an editor is not a failure, so a session that saved nothing
    still succeeds; it says so, because a user who meant to save would
    otherwise be told nothing at all.

    Args:
        args: Optional replacement for ``sys.argv[1:]``, mainly for tests.

    Returns:
        ``0`` when the session ran, whether or not anything was saved,
        ``1`` when the file cannot be opened for editing.
    """
    parsed = parsed_args(build_parser(), args)
    try:
        in_file = _input_file(parsed)
        out_file = _out_file(parsed.output, in_file)
        saved = _edited(parsed, in_file, out_file)
    except EDIT_ERRORS as error:
        print(f'Could not open the configuration: {error}', file=sys.stderr)
        return 1
    print('Closed without saving.' if saved is None
          else f'Saved to {out_file}')
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
