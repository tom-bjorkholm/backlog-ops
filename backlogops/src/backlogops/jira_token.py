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
