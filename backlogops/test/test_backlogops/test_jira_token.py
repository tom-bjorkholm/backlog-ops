#! /usr/local/bin/python3
"""Tests for pass-phrase encryption of a Jira API token.

The tests cover the encrypt and decrypt round trip, the fresh salt that
makes two encryptions of one token differ, the rejection of a wrong
pass phrase, a corrupt blob and an empty pass phrase, and the two
file-based helpers that write an encrypted token to a file atomically
and with owner-only permissions.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import os
import stat
import sys
from pathlib import Path
import pytest
from backlogops.jira_token import (
    decrypt_token, encrypt_token, encrypt_token_file, encrypt_token_to_file)

_WIN = sys.platform == 'win32'


def _allow(_path: Path) -> bool:
    """Return True, allowing any overwrite."""
    return True


def _deny(_path: Path) -> bool:
    """Return False, refusing any overwrite."""
    return False


def test_round_trip() -> None:
    """Test a token decrypts back to itself with the same pass phrase."""
    blob = encrypt_token('my-secret', 'pass phrase')
    assert decrypt_token(blob, 'pass phrase') == 'my-secret'


def test_unicode_round_trip() -> None:
    """Test a token with non-ASCII characters survives the round trip."""
    blob = encrypt_token('töken-π-🔑', 'pass phrase')
    assert decrypt_token(blob, 'pass phrase') == 'töken-π-🔑'


def test_unique_salt() -> None:
    """Test two encryptions of one token differ but both decrypt back."""
    first = encrypt_token('tok', 'pw')
    second = encrypt_token('tok', 'pw')
    assert first != second
    assert decrypt_token(first, 'pw') == 'tok'
    assert decrypt_token(second, 'pw') == 'tok'


def test_wrong_pass() -> None:
    """Test decrypting with a wrong pass phrase is rejected."""
    blob = encrypt_token('tok', 'right')
    with pytest.raises(ValueError):
        decrypt_token(blob, 'wrong')


def test_corrupt_blob() -> None:
    """Test decrypting a blob that is not valid is rejected."""
    with pytest.raises(ValueError):
        decrypt_token('not-a-valid-blob', 'pw')


def test_empty_pass() -> None:
    """Test encrypting with an empty pass phrase is refused."""
    with pytest.raises(ValueError):
        encrypt_token('tok', '')


def test_round_trip_file(tmp_path: Path) -> None:
    """Test a token written to a file decrypts back to itself."""
    target = tmp_path / 'token.enc'
    encrypt_token_to_file('tok', passphrase='pw', filename=target,
                          ok_to_overwrite=_deny)
    assert decrypt_token(target.read_text(), 'pw') == 'tok'


@pytest.mark.skipif(_WIN, reason='POSIX permission bits are not used')
def test_file_permissions(tmp_path: Path) -> None:
    """Test the encrypted file is written with owner-only permissions."""
    target = tmp_path / 'token.enc'
    encrypt_token_to_file('tok', passphrase='pw', filename=target,
                          ok_to_overwrite=_deny)
    mode = stat.S_IMODE(target.stat().st_mode)
    assert mode == 0o600


def test_no_suffix_name(tmp_path: Path) -> None:
    """Test a target file name without a suffix still round-trips."""
    target = tmp_path / 'token'
    encrypt_token_to_file('tok', passphrase='pw', filename=target,
                          ok_to_overwrite=_deny)
    assert decrypt_token(target.read_text(), 'pw') == 'tok'


def test_overwrite_allowed(tmp_path: Path) -> None:
    """Test an existing file is replaced when overwrite is allowed."""
    target = tmp_path / 'token.enc'
    target.write_text('old')
    encrypt_token_to_file('new', passphrase='pw', filename=target,
                          ok_to_overwrite=_allow)
    assert decrypt_token(target.read_text(), 'pw') == 'new'


def test_overwrite_refused(tmp_path: Path) -> None:
    """Test an existing file is left untouched when overwrite is refused."""
    target = tmp_path / 'token.enc'
    target.write_text('old')
    with pytest.raises(FileExistsError):
        encrypt_token_to_file('new', passphrase='pw', filename=target,
                              ok_to_overwrite=_deny)
    assert target.read_text() == 'old'


def test_missing_parent_dir(tmp_path: Path) -> None:
    """Test a target in a non-existent directory is rejected."""
    target = tmp_path / 'missing' / 'token.enc'
    with pytest.raises(NotADirectoryError):
        encrypt_token_to_file('tok', passphrase='pw', filename=target,
                              ok_to_overwrite=_deny)


def test_parent_not_a_dir(tmp_path: Path) -> None:
    """Test a target whose parent is a file, not a directory, is rejected."""
    parent = tmp_path / 'not_a_dir'
    parent.write_text('x')
    target = parent / 'token.enc'
    with pytest.raises(NotADirectoryError):
        encrypt_token_to_file('tok', passphrase='pw', filename=target,
                              ok_to_overwrite=_deny)


def test_stale_tmp_removed(tmp_path: Path) -> None:
    """Test a leftover temporary file is removed when overwrite is allowed."""
    target = tmp_path / 'token.enc'
    tmpfile = target.with_suffix(target.suffix + '.in_progress')
    tmpfile.write_text('stale')
    encrypt_token_to_file('tok', passphrase='pw', filename=target,
                          ok_to_overwrite=_allow)
    assert decrypt_token(target.read_text(), 'pw') == 'tok'
    assert not tmpfile.exists()


def test_stale_tmp_refused(tmp_path: Path) -> None:
    """Test a leftover temporary file blocks the write when refused."""
    target = tmp_path / 'token.enc'
    tmpfile = target.with_suffix(target.suffix + '.in_progress')
    tmpfile.write_text('stale')
    with pytest.raises(FileExistsError):
        encrypt_token_to_file('tok', passphrase='pw', filename=target,
                              ok_to_overwrite=_deny)
    assert not target.exists()


def test_move_fail_cleanup(tmp_path: Path,
                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a failed atomic move removes the temporary file it left behind.

    The move is made to fail after the temporary file has been written, so
    the finally clause must delete it and no target file must appear.
    """
    target = tmp_path / 'token.enc'
    tmpfile = target.with_suffix(target.suffix + '.in_progress')

    def _boom(_src: object, _dst: object) -> None:
        """Fail the atomic move to simulate a crash before it completes."""
        raise OSError('simulated crash before move')
    monkeypatch.setattr(os, 'replace', _boom)
    with pytest.raises(OSError):
        encrypt_token_to_file('tok', passphrase='pw', filename=target,
                              ok_to_overwrite=_deny)
    assert not tmpfile.exists()
    assert not target.exists()


def test_empty_pass_to_file(tmp_path: Path) -> None:
    """Test an empty pass phrase is refused before any file is written."""
    target = tmp_path / 'token.enc'
    with pytest.raises(ValueError):
        encrypt_token_to_file('tok', passphrase='', filename=target,
                              ok_to_overwrite=_deny)
    assert not target.exists()


def test_file_round_trip(tmp_path: Path) -> None:
    """Test a token read from a file is encrypted to another file."""
    clear_file = tmp_path / 'clear.txt'
    clear_file.write_text('tok\n')
    encrypted_file = tmp_path / 'token.enc'
    encrypt_token_file(clear_file=clear_file, encrypted_file=encrypted_file,
                       passphrase='pw', ok_to_overwrite=_deny)
    assert decrypt_token(encrypted_file.read_text(), 'pw') == 'tok'
    assert clear_file.read_text() == 'tok\n'


def test_same_file_inplace(tmp_path: Path) -> None:
    """Test the clear text file can be overwritten with its own encryption."""
    clear_file = tmp_path / 'token.txt'
    clear_file.write_text('tok')
    encrypt_token_file(clear_file=clear_file, encrypted_file=clear_file,
                       passphrase='pw', ok_to_overwrite=_allow)
    assert decrypt_token(clear_file.read_text(), 'pw') == 'tok'


def test_file_no_overwrite(tmp_path: Path) -> None:
    """Test encrypt_token_file leaves an existing output untouched."""
    clear_file = tmp_path / 'clear.txt'
    clear_file.write_text('tok')
    encrypted_file = tmp_path / 'token.enc'
    encrypted_file.write_text('old')
    with pytest.raises(FileExistsError):
        encrypt_token_file(clear_file=clear_file,
                           encrypted_file=encrypted_file, passphrase='pw',
                           ok_to_overwrite=_deny)
    assert encrypted_file.read_text() == 'old'


def test_missing_clear_file(tmp_path: Path) -> None:
    """Test a missing clear text token file is reported."""
    clear_file = tmp_path / 'clear.txt'
    encrypted_file = tmp_path / 'token.enc'
    with pytest.raises(FileNotFoundError):
        encrypt_token_file(clear_file=clear_file,
                           encrypted_file=encrypted_file, passphrase='pw',
                           ok_to_overwrite=_deny)


def test_empty_clear_file(tmp_path: Path) -> None:
    """Test a clear text token file holding only whitespace is rejected."""
    clear_file = tmp_path / 'clear.txt'
    clear_file.write_text('   \n')
    encrypted_file = tmp_path / 'token.enc'
    with pytest.raises(ValueError):
        encrypt_token_file(clear_file=clear_file,
                           encrypted_file=encrypted_file, passphrase='pw',
                           ok_to_overwrite=_deny)
    assert not encrypted_file.exists()


def test_strips_whitespace(tmp_path: Path) -> None:
    """Test surrounding whitespace around the clear text token is dropped."""
    clear_file = tmp_path / 'clear.txt'
    clear_file.write_text('  tok  \n')
    encrypted_file = tmp_path / 'token.enc'
    encrypt_token_file(clear_file=clear_file, encrypted_file=encrypted_file,
                       passphrase='pw', ok_to_overwrite=_deny)
    assert decrypt_token(encrypted_file.read_text(), 'pw') == 'tok'
