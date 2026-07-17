#! /usr/local/bin/python3
"""Tests for the backlogops_cli encrypt_token_file command.

The tests cover the overwrite prompt on its own, the pass phrase entry
and confirmation loop (including a mismatch that is retried and an empty
entry that aborts), reading the clear text token from a file or from
standard input, the file-not-found and bad-output-directory error paths,
the overwrite prompt wired into the command, and command discovery.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import io
from pathlib import Path
import pytest
from backlogops.jira_token import decrypt_token
from backlogops_cli.list import command_modules
from backlogops_cli import encrypt_token_file as etf
from backlogops_cli.encrypt_token_file import _ok_to_overwrite


def test_ok_to_overwrite_yes(monkeypatch: pytest.MonkeyPatch,
                             tmp_path: Path) -> None:
    """Test a 'yes' answer allows the overwrite."""
    monkeypatch.setattr('sys.stdin', io.StringIO('yes\n'))
    assert _ok_to_overwrite(tmp_path / 'f') is True


def test_ok_to_overwrite_no(monkeypatch: pytest.MonkeyPatch,
                            tmp_path: Path) -> None:
    """Test a 'n' answer refuses the overwrite."""
    monkeypatch.setattr('sys.stdin', io.StringIO('n\n'))
    assert _ok_to_overwrite(tmp_path / 'f') is False


def test_ok_overwrite_retry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
                            capsys: pytest.CaptureFixture[str]) -> None:
    """Test an unrecognised answer is rejected and the question repeats."""
    monkeypatch.setattr('sys.stdin', io.StringIO('maybe\ny\n'))
    assert _ok_to_overwrite(tmp_path / 'f') is True
    assert 'Please answer yes or no.' in capsys.readouterr().out


def test_requires_outfile() -> None:
    """Test the command requires the output file argument."""
    with pytest.raises(SystemExit):
        etf.build_parser().parse_args([])


def test_parser_no_infile() -> None:
    """Test the input file argument is optional."""
    parsed = etf.build_parser().parse_args(['-o', 'out.enc'])
    assert parsed.infile is None
    assert parsed.outfile == 'out.enc'


def test_passphrase_mismatch(monkeypatch: pytest.MonkeyPatch,
                             tmp_path: Path) -> None:
    """Test a mismatched confirmation is retried until it matches."""
    answers = iter(['first', 'second', 'secret', 'secret'])
    monkeypatch.setattr(etf, 'getpass', lambda _prompt: next(answers))
    infile = tmp_path / 'clear.txt'
    infile.write_text('tok')
    outfile = tmp_path / 'token.enc'
    code = etf.main(['-i', str(infile), '-o', str(outfile)])
    assert code == 0
    assert decrypt_token(outfile.read_text(), 'secret') == 'tok'


def test_empty_pass_exits(monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
                          capsys: pytest.CaptureFixture[str]) -> None:
    """Test an empty pass phrase aborts before any file is written."""
    monkeypatch.setattr(etf, 'getpass', lambda _prompt: '')
    outfile = tmp_path / 'token.enc'
    code = etf.main(['-o', str(outfile)])
    assert code == 1
    assert not outfile.exists()
    assert 'No pass phrase entered' in capsys.readouterr().out


def test_stdin_empty_token(monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
                           capsys: pytest.CaptureFixture[str]) -> None:
    """Test an empty token read from stdin is rejected."""
    monkeypatch.setattr(etf, 'getpass', lambda _prompt: 'secret')
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'))
    outfile = tmp_path / 'token.enc'
    code = etf.main(['-o', str(outfile)])
    assert code == 1
    assert not outfile.exists()
    assert 'No token entered' in capsys.readouterr().out


def test_stdin_token_ok(monkeypatch: pytest.MonkeyPatch,
                        tmp_path: Path) -> None:
    """Test a token entered on stdin is encrypted to the output file."""
    monkeypatch.setattr(etf, 'getpass', lambda _prompt: 'secret')
    monkeypatch.setattr('sys.stdin', io.StringIO('tok\n'))
    outfile = tmp_path / 'token.enc'
    code = etf.main(['-o', str(outfile)])
    assert code == 0
    assert decrypt_token(outfile.read_text(), 'secret') == 'tok'


def test_infile_ok(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test a token read from an input file is encrypted successfully."""
    monkeypatch.setattr(etf, 'getpass', lambda _prompt: 'secret')
    infile = tmp_path / 'clear.txt'
    infile.write_text('tok')
    outfile = tmp_path / 'token.enc'
    code = etf.main(['-i', str(infile), '-o', str(outfile)])
    assert code == 0
    assert decrypt_token(outfile.read_text(), 'secret') == 'tok'


def test_infile_not_found(monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
                          capsys: pytest.CaptureFixture[str]) -> None:
    """Test a missing input file is reported and returns an error code."""
    monkeypatch.setattr(etf, 'getpass', lambda _prompt: 'secret')
    infile = tmp_path / 'missing.txt'
    outfile = tmp_path / 'token.enc'
    code = etf.main(['-i', str(infile), '-o', str(outfile)])
    assert code == 1
    assert 'Error encrypting token file' in capsys.readouterr().out


def test_bad_outfile_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
                         capsys: pytest.CaptureFixture[str]) -> None:
    """Test an output file in a missing directory is reported."""
    monkeypatch.setattr(etf, 'getpass', lambda _prompt: 'secret')
    infile = tmp_path / 'clear.txt'
    infile.write_text('tok')
    outfile = tmp_path / 'missing' / 'token.enc'
    code = etf.main(['-i', str(infile), '-o', str(outfile)])
    assert code == 1
    assert 'Error encrypting token file' in capsys.readouterr().out


def test_overwrite_declined(monkeypatch: pytest.MonkeyPatch,
                            tmp_path: Path) -> None:
    """Test declining the overwrite prompt leaves the output untouched."""
    monkeypatch.setattr(etf, 'getpass', lambda _prompt: 'secret')
    monkeypatch.setattr('sys.stdin', io.StringIO('n\n'))
    infile = tmp_path / 'clear.txt'
    infile.write_text('tok')
    outfile = tmp_path / 'token.enc'
    outfile.write_text('old')
    code = etf.main(['-i', str(infile), '-o', str(outfile)])
    assert code == 1
    assert outfile.read_text() == 'old'


def test_overwrite_confirmed(monkeypatch: pytest.MonkeyPatch,
                             tmp_path: Path) -> None:
    """Test confirming the overwrite prompt replaces the output file."""
    monkeypatch.setattr(etf, 'getpass', lambda _prompt: 'secret')
    monkeypatch.setattr('sys.stdin', io.StringIO('y\n'))
    infile = tmp_path / 'clear.txt'
    infile.write_text('tok')
    outfile = tmp_path / 'token.enc'
    outfile.write_text('old')
    code = etf.main(['-i', str(infile), '-o', str(outfile)])
    assert code == 0
    assert decrypt_token(outfile.read_text(), 'secret') == 'tok'


def test_stdin_no_overwrite(monkeypatch: pytest.MonkeyPatch,
                            tmp_path: Path) -> None:
    """Test declining the overwrite for a stdin token keeps the output."""
    monkeypatch.setattr(etf, 'getpass', lambda _prompt: 'secret')
    monkeypatch.setattr('sys.stdin', io.StringIO('tok\nn\n'))
    outfile = tmp_path / 'token.enc'
    outfile.write_text('old')
    code = etf.main(['-o', str(outfile)])
    assert code == 1
    assert outfile.read_text() == 'old'


def test_in_command_list() -> None:
    """Test the encrypt_token_file command is discovered by list."""
    assert 'encrypt_token_file' in [name for name, _ in command_modules()]
