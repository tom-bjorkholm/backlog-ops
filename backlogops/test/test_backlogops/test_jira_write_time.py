#! /usr/local/bin/python3
"""Tests for writing a remaining time estimate to Jira.

The pure helpers are checked directly: the rounding to what Jira stores,
the placing of a time tracking estimate as the writable remaining
estimate text, the split of an update into plain fields and edit
operations, and the read-back that tells a stored estimate from one Jira
silently ignored or refused to show.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import timedelta
from types import SimpleNamespace
from typing import Optional, cast
import pytest
from jira import JIRA, JIRAError
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType
from backlogops.jira_write_fields import _place_value
from backlogops.jira_write_time import (
    _jira_value, _split_edits, _unstored_time)

TT = JiraAttrPath(JiraAttrType.FIELD,
                  ('timetracking', 'remainingEstimateSeconds'))
"""The default map's first remaining time path."""

EST = JiraAttrPath(JiraAttrType.FIELD, ('timeestimate',))
"""The default map's second remaining time path."""

CUSTOM = JiraAttrPath(JiraAttrType.CUSTOM_FIELD, ('Hours left',))
"""A remaining time mapped to a numeric custom field."""

EDIT_62M: dict[str, object] = {'timetracking': {'remainingEstimate': '62m'}}
"""The time tracking entry that writes an estimate of 62 minutes."""


@pytest.mark.parametrize('attr, value, expected', [
    (TT, timedelta(hours=1, seconds=61), 3720),
    (TT, timedelta(hours=1), 3600),
    (TT, timedelta(0), 0),
    (TT, timedelta(microseconds=1), 60),
    (EST, timedelta(seconds=61), 120),
    (CUSTOM, timedelta(seconds=3661, microseconds=200000), 3662),
    (CUSTOM, timedelta(seconds=3661), 3661),
    (TT, None, None),
    (TT, 'text', 'text'),
    (CUSTOM, 5.0, 5.0)])
def test_jira_value(attr: JiraAttrPath, value: object,
                    expected: object) -> None:
    """Test a remaining time rounds up to what its Jira path stores."""
    assert _jira_value(attr, value) == expected


@pytest.mark.parametrize('attr', [TT, EST])
def test_place_time(attr: JiraAttrPath) -> None:
    """Test both read-only time paths write the remaining estimate text."""
    fields: dict[str, object] = {}
    _place_value(fields, attr, 3720, {})
    assert fields == EDIT_62M


def test_place_zero() -> None:
    """Test an estimate of no work left is written as zero minutes."""
    fields: dict[str, object] = {}
    _place_value(fields, TT, 0, {})
    assert fields == {'timetracking': {'remainingEstimate': '0m'}}


def test_place_custom() -> None:
    """Test a custom field path gets the raw seconds under its field id."""
    fields: dict[str, object] = {}
    _place_value(fields, CUSTOM, 3661, {'Hours left': 'customfield_1'})
    assert fields == {'customfield_1': 3661}


def test_split_edits() -> None:
    """Test time tracking becomes an edit operation, the rest plain fields."""
    plain, edits = _split_edits({'summary': 'T', **EDIT_62M})
    assert plain == {'summary': 'T'}
    assert edits == {'timetracking': [{'edit': {'remainingEstimate': '62m'}}]}


def test_split_no_edits() -> None:
    """Test an update without time tracking has no edit operations."""
    assert _split_edits({'summary': 'T'}) == ({'summary': 'T'}, {})


# pylint: disable-next=too-few-public-methods
class _ReadBack:
    """A stand-in client answering the time tracking read-back."""

    def __init__(self, seconds: Optional[int], fail: bool = False) -> None:
        """Start with the stored remaining seconds and the failing flag."""
        self.seconds = seconds
        self.fail = fail
        self.asked: list[tuple[str, object]] = []

    def issue(self, key: str, fields: object = None) -> SimpleNamespace:
        """Return the issue's time tracking, or raise when set to fail."""
        self.asked.append((key, fields))
        if self.fail:
            raise JIRAError(status_code=403, text='no permission')
        tracking = SimpleNamespace(remainingEstimateSeconds=self.seconds)
        return SimpleNamespace(fields=SimpleNamespace(timetracking=tracking))


def _unstored(client: _ReadBack, written: dict[str, object],
              refused: Optional[list[tuple[str, str]]] = None
              ) -> list[tuple[str, str]]:
    """Return the read-back result for a write to issue ``K-1``."""
    return _unstored_time(cast(JIRA, client), 'K-1', written, refused or [])


def test_read_back_stored() -> None:
    """Test an estimate Jira stored is not reported."""
    client = _ReadBack(3720)
    assert not _unstored(client, EDIT_62M)
    assert client.asked == [('K-1', 'timetracking')]


@pytest.mark.parametrize('seconds', [None, 3600])
def test_read_back_ignored(seconds: Optional[int]) -> None:
    """Test an estimate Jira silently did not store is refused."""
    result = _unstored(_ReadBack(seconds), EDIT_62M)
    assert len(result) == 1
    field, reason = result[0]
    assert field == 'timetracking'
    assert '3720 s written' in reason and f'{seconds!r} s stored' in reason


def test_read_back_fails() -> None:
    """Test a read-back Jira refuses is reported with Jira's reason."""
    result = _unstored(_ReadBack(3720, fail=True), EDIT_62M)
    assert result == [('timetracking', 'could not read the remaining '
                       'estimate back: no permission')]


def test_read_back_refused() -> None:
    """Test an estimate already refused is not read back again."""
    client = _ReadBack(None)
    assert not _unstored(client, EDIT_62M, [('timetracking', 'bad')])
    assert not client.asked


@pytest.mark.parametrize('written', [
    {'summary': 'T'}, {'timetracking': 'odd'},
    {'timetracking': {'remainingEstimate': '1h'}},
    {'timetracking': {'originalEstimate': '5m'}}])
def test_read_back_skipped(written: dict[str, object]) -> None:
    """Test no read-back without a written remaining estimate text."""
    client = _ReadBack(None)
    assert not _unstored(client, written)
    assert not client.asked
