#!/usr/local/bin/python3
"""Encrypt a Jira API token to a file with a pass phrase.

Read a clear text API token from a file or from standard input, encrypt it
with a pass phrase and write the encrypted token to a file. The pass phrase
is requested on the terminal and is not echoed. The clear text token file
is not modified, unless the the encrypted token file is the same as the
clear text token file, in which case the clear text token file is overwritten
with the encrypted token. The encrypted token file is written atomically,
so that it is either the old version or the new version, and never a
half-written file.
"""

# PYTHON_ARGCOMPLETE_OK
# Copyright (c) 2026, Tom Björkholm
# MIT License

import argparse
import sys
from getpass import getpass
from pathlib import Path
from typing import Optional
from backlogops import encrypt_token_to_file, encrypt_token_file
from backlogops_cli._command_io import parsed_args


DESCRIPTION = 'Encrypt a Jira API token file with a pass phrase.'


def _ok_to_overwrite(filename: Path) -> bool:
    """Return True if the file can be overwritten, False otherwise."""
    txt = f'The output file {filename} already exists. Overwrite? [y/n] '
    while True:
        answer = input(txt)
        if answer.lower().strip() in ('y', 'ye', 'yes'):
            return True
        if answer.lower().strip() in ('n', 'no'):
            return False
        print('Please answer yes or no.')
    return False  # pragma: no cover


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for the encrypt-token-file command."""
    descr = DESCRIPTION + '. The pass phrase is requested on the terminal.'
    descr += ' The clear text token file is not modified, unless the output'
    descr += ' file is the same as the input file, in which case the clear'
    descr += ' text token file is overwritten with the encrypted token.'
    parser = argparse.ArgumentParser(description=descr)
    inhelp = 'The clear text token file to read from. Omit to read from stdin.'
    parser.add_argument('-i', '--infile', required=False, help=inhelp)
    parser.add_argument('-o', '--outfile', required=True,
                        help='The encrypted token file to write to.')
    return parser


EXCEPTIONS = (FileNotFoundError, ValueError, FileExistsError,
              NotADirectoryError, OSError)


def _run(parsed: argparse.Namespace) -> int:
    """Run the encrypt-token-file command with the given parsed arguments.

    Args:
        parsed: The parsed command line arguments.
    Returns:
        0 if the command was successful, 1 if there was an error
    """
    outfile = Path(parsed.outfile)
    token: Optional[str] = None
    pphrase1 = 'a'
    phrase2 = 'b'
    while pphrase1 != phrase2 or not pphrase1:
        pphrase1 = getpass('Enter the pass phrase to encrypt the token with: ')
        if not pphrase1:
            print('No pass phrase entered. Exiting.')
            return 1
        phrase2 = getpass('Re-enter the pass phrase to confirm: ')
        if pphrase1 != phrase2:
            print('Pass phrases do not match. Please try again.')
    if not parsed.infile:
        print('Enter the clear text token on a single line, then press Enter.')
        token = input().strip()
        if not token:
            print('No token entered. Exiting.')
            return 1
        try:
            encrypt_token_to_file(token, passphrase=pphrase1, filename=outfile,
                                  ok_to_overwrite=_ok_to_overwrite)
            return 0
        except EXCEPTIONS as e:
            print(f'Error encrypting token: {e}')
            return 1
    infile = Path(parsed.infile)
    try:
        encrypt_token_file(clear_file=infile, encrypted_file=outfile,
                           passphrase=pphrase1,
                           ok_to_overwrite=_ok_to_overwrite)
        return 0
    except EXCEPTIONS as e:
        print(f'Error encrypting token file: {e}')
        return 1
    return 2  # pragma: no cover  # this should never be reached


def main(arguments: Optional[list[str]] = None) -> int:
    """Encrypt a Jira API token file with a pass phrase.

    Args:
        arguments: The command line arguments to parse. If None, the arguments
            are taken from sys.argv.
    Returns:
        0 if the command was successful, 1 if there was an error.
    """
    parsed = parsed_args(build_parser(), arguments)
    return _run(parsed)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
