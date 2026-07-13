#! /usr/local/bin/python3
"""Encrypt and decrypt a Jira API token with a pass phrase.

The encryption is pass-phrase based and stores no key of its own: a
Fernet key is derived from the pass phrase and a fresh random salt with
PBKDF2-HMAC-SHA256. The salt is stored next to the ciphertext, so the
same pass phrase recreates the key when the token is later read. The
caller supplies the pass phrase both when a token is encrypted and when
it is decrypted; there is no key store to manage.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import base64
import os
from pathlib import Path
from typing import Callable
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

_SALT_BYTES = 16
"""Number of random salt bytes prepended to the stored ciphertext."""

_KDF_ITERATIONS = 200_000
"""PBKDF2 iteration count used to derive the key from the pass phrase."""


def _key_from_passphrase(passphrase: str, salt: bytes) -> bytes:
    """Return a Fernet key derived from a pass phrase and a salt."""
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt,
                     iterations=_KDF_ITERATIONS)
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode('utf-8')))


def encrypt_token(token: str, passphrase: str) -> str:
    """Return the token encrypted with the pass phrase as a text blob.

    Args:
        token: The plain text API token to encrypt.
        passphrase: The pass phrase to derive the encryption key from.

    Returns:
        A url-safe base64 text blob holding the salt and the ciphertext.

    Raises:
        ValueError: If the pass phrase is empty.
    """
    if passphrase == '':
        raise ValueError('A pass phrase is required to encrypt a token.')
    salt = os.urandom(_SALT_BYTES)
    cipher = Fernet(_key_from_passphrase(passphrase, salt))
    blob = salt + cipher.encrypt(token.encode('utf-8'))
    return base64.urlsafe_b64encode(blob).decode('ascii')


def decrypt_token(blob_text: str, passphrase: str) -> str:
    """Return the token decrypted from a blob with the pass phrase.

    Args:
        blob_text: The text blob produced by :func:`encrypt_token`.
        passphrase: The pass phrase used when the token was encrypted.

    Returns:
        The decrypted plain text API token.

    Raises:
        ValueError: If the pass phrase is wrong or the blob is corrupt.
    """
    try:
        blob = base64.urlsafe_b64decode(blob_text.encode('ascii'))
        salt, ciphertext = blob[:_SALT_BYTES], blob[_SALT_BYTES:]
        cipher = Fernet(_key_from_passphrase(passphrase, salt))
        return cipher.decrypt(ciphertext).decode('utf-8')
    except (InvalidToken, ValueError, TypeError) as error:
        raise ValueError('Could not decrypt the token; wrong pass phrase '
                         'or corrupt data.') from error


type OkToOverwrite = Callable[[Path], bool]


def encrypt_token_to_file(token: str, *, passphrase: str, filename: Path,
                          ok_to_overwrite: OkToOverwrite) -> None:
    """Encrypt a token and write it to a file.

    This function writes the encrypted token to a temporary file first and then
    renames it to the target filename to ensure atomicity. If the target file
    already exists and it is ok to overwrite it, the file will be
    overwritten atomically as the last step. This guarantees that the target
    file is either the old version or the new version, and never a
    half-written file. The file is written with owner-only permissions.

    Args:
        token: The plain text API token to encrypt.
        passphrase: The pass phrase to derive the encryption key from.
        filename: The name of the file to write the encrypted blob to.
        ok_to_overwrite: A callback that is called with the filename if it
            already exists. If it returns True, the file will be overwritten;
            if it returns False, a FileAlreadyExistsError will be raised.

    Raises:
        ValueError: If the pass phrase is empty.
        FileExistsError: If the file already exists and ok_to_overwrite returns
                         False.
        NotADirectoryError: If the parent directory of the file does not exist.
        OSError: If the file could not be written.
    """
    parent_dir = filename.parent
    if not parent_dir.exists():
        pnot = f'The parent directory {parent_dir} does not exist.'
        raise NotADirectoryError(pnot)
    if not parent_dir.is_dir():
        pndir = f'The parent path {parent_dir} is not a directory.'
        raise NotADirectoryError(pndir)
    if filename.exists() and not ok_to_overwrite(filename):
        raise FileExistsError(f"The file {filename} already exists.")
    tmpfile = filename.with_suffix(filename.suffix + '.in_progress')
    if tmpfile.exists():
        if not ok_to_overwrite(tmpfile):
            texist = f'The temporary file {tmpfile} already exists.'
            raise FileExistsError(texist)
        os.remove(tmpfile)
    encrypted_blob = encrypt_token(token, passphrase)
    try:
        with open(tmpfile, 'w', encoding='utf-8') as f:
            f.write(encrypted_blob)
        os.chmod(tmpfile, 0o600)
        os.replace(tmpfile, filename)
    finally:
        if os.path.exists(tmpfile):
            os.remove(tmpfile)


def encrypt_token_file(*, clear_file: Path, encrypted_file: Path,
                       passphrase: str, ok_to_overwrite: OkToOverwrite) \
        -> None:
    """Encrypt a token read from a file and write it to a file.

    The clear text token is read from the file named by `clear_file`, and the
    encrypted blob is written to the file named by `encrypted_file`, which
    may be the same file. The encryption is done with the pass phrase supplied
    in the `passphrase` argument. If the `encrypted_file` already exists and
    it is ok to overwrite it, the file will be overwritten atomically as the
    last step. This guarantees that the target file is either the old version
    or the new version, and never a half-written file.

    Args:
        clear_file: The name of the file to read the plain text token from.
        encrypted_file: The name of the file to write the encrypted blob to.
        passphrase: The pass phrase to derive the encryption key from.
        ok_to_overwrite: A callback that is called with the filename if it
            already exists. If it returns True, the file will be overwritten;
            if it returns False, a FileAlreadyExistsError will be raised.

    Raises:
        FileNotFoundError: If the clear text token file does not exist.
        ValueError: If the pass phrase is empty.
        ValueError: If the clear text token file holds no token (empty file).
        FileExistsError: If the output file already exists and ok_to_overwrite
                         returns False.
        NotADirectoryError: If the parent directory of the output file does
                            not exist.
        OSError: If the output file could not be written or the input file
                 could not be read.
    """
    if not clear_file.exists():
        raise FileNotFoundError(f'The clear text token file {clear_file} '
                                'does not exist.')
    with open(clear_file, 'r', encoding='utf-8') as f:
        token = f.read().strip()
    if not token:
        raise ValueError(f'No token in clear text token file {clear_file}.')
    encrypt_token_to_file(token, passphrase=passphrase,
                          filename=encrypted_file,
                          ok_to_overwrite=ok_to_overwrite)
