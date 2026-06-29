#! /usr/local/bin/python3
"""Tests for pass-phrase encryption of a Jira API token.

The tests cover the encrypt and decrypt round trip, the fresh salt that
makes two encryptions of one token differ, and the rejection of a wrong
pass phrase, a corrupt blob and an empty pass phrase.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import pytest
from backlogops.jira_token import decrypt_token, encrypt_token


def test_round_trip() -> None:
    """Test a token decrypts back to itself with the same pass phrase."""
    blob = encrypt_token('my-secret', 'pass phrase')
    assert decrypt_token(blob, 'pass phrase') == 'my-secret'


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
