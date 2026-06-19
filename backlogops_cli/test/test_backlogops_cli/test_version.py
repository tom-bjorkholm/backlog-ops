#! /usr/local/bin/python3
"""Test the version command."""

import pytest
from backlogops_cli.version import main


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the version command."""
    # Note: this test is using real network access to pypi.org.
    main()
    out, err = capsys.readouterr()
    assert 'backlogops-cli ..' in out
    assert 'versionreporter .' in out
    assert 'tableio ..' in out
    assert 'tableio-cfg-json' in out
    assert 'config-as-json ..' in out
    assert 'mformat ..' in out
    assert 'backlogops ..' in out
    assert err == ''
