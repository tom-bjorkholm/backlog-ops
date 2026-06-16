#! /usr/local/bin/python3
"""Tests for release conversion and consistency checks."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date, datetime
from io import StringIO

import pytest

from backlogops.releases import Release, check_releases
from backlogops.releases import get_release, get_releases
from backlogops.no_text_io import NoTextIO


def _valid_data() -> dict[str, object]:
    """Return dictionary data for one valid release."""
    return {'name': 'R1', 'planned_date': '2026-06-12',
            'estimated_date': '2026-07-01'}


def test_release_from_dict() -> None:
    """Test creating one release from dictionary data."""
    release = get_release(_valid_data())
    assert release == Release(name='R1', planned_date=date(2026, 6, 12),
                              estimated_date=date(2026, 7, 1))


def test_release_only_name() -> None:
    """Test a release with only the mandatory name has no dates."""
    release = get_release({'name': 'R1'})
    assert release == Release(name='R1')


def test_release_date_obj() -> None:
    """Test existing date objects are accepted unchanged."""
    data: dict[str, object] = {'name': 'R1',
                               'planned_date': date(2026, 6, 12),
                               'estimated_date': date(2026, 7, 1)}
    release = get_release(data)
    assert release.planned_date == date(2026, 6, 12)
    assert release.estimated_date == date(2026, 7, 1)


def test_release_date_from_dt() -> None:
    """Test a spreadsheet datetime is narrowed to a comparable date."""
    data: dict[str, object] = {'name': 'R1',
                               'planned_date': datetime(2026, 6, 12, 9, 30)}
    release = get_release(data)
    assert release.planned_date == date(2026, 6, 12)
    assert not isinstance(release.planned_date, datetime)


def test_release_none_dates() -> None:
    """Test an explicit None is accepted for an optional date field."""
    data: dict[str, object] = {'name': 'R1', 'planned_date': None,
                               'estimated_date': None}
    release = get_release(data)
    assert release.planned_date is None
    assert release.estimated_date is None


def test_extra_strict_err() -> None:
    """Test an unknown key is an error when strict is True (default)."""
    data = _valid_data()
    data['description'] = 'A release description'
    stderr_file = StringIO()
    with pytest.raises(KeyError):
        get_release(data, stderr_file=stderr_file)
    assert 'description' in stderr_file.getvalue()


def test_extra_not_strict() -> None:
    """Test an unknown key is ignored when strict is False."""
    data = _valid_data()
    data['description'] = 'A release description'
    release = get_release(data, strict=False)
    assert release == Release(name='R1', planned_date=date(2026, 6, 12),
                              estimated_date=date(2026, 7, 1))


def test_release_missing_name() -> None:
    """Test a missing mandatory name is reported and rejected."""
    stderr_file = StringIO()
    with pytest.raises(KeyError):
        get_release({'planned_date': '2026-06-12'}, stderr_file=stderr_file)
    assert 'name' in stderr_file.getvalue()


@pytest.mark.parametrize('field_name, value', [
    ('name', True),
    ('planned_date', 'not-a-date'),
    ('planned_date', '2026-13-01'),
    ('estimated_date', 42)])
def test_release_bad_type(field_name: str, value: object) -> None:
    """Test invalid field values are reported and rejected."""
    data = _valid_data()
    data[field_name] = value
    stderr_file = StringIO()
    with pytest.raises(TypeError):
        get_release(data, stderr_file=stderr_file)
    assert field_name in stderr_file.getvalue()


def test_get_releases() -> None:
    """Test creating several releases from a list of dictionaries."""
    releases = get_releases([{'name': 'R1'}, _valid_data()])
    assert [release.name for release in releases] == ['R1', 'R1']
    assert releases[1].planned_date == date(2026, 6, 12)


def test_get_releases_strict() -> None:
    """Test get_releases rejects unknown keys when strict is True."""
    with pytest.raises(KeyError):
        get_releases([{'name': 'R1', 'oops': 1}], NoTextIO())


def test_get_releases_lenient() -> None:
    """Test get_releases ignores unknown keys when strict is False."""
    releases = get_releases([{'name': 'R1', 'oops': 1}], NoTextIO(),
                            strict=False)
    assert releases == [Release(name='R1')]


def test_internal_ok() -> None:
    """Test a fully populated valid release passes the internal check."""
    release = Release(name='R1', planned_date=date(2026, 6, 12),
                      estimated_date=date(2026, 7, 1))
    release.check_consistency(NoTextIO())


def test_internal_only_name() -> None:
    """Test a release with only a name passes the internal check."""
    Release(name='R1').check_consistency(NoTextIO())


@pytest.mark.parametrize('field_name, value', [
    ('name', 7),
    ('planned_date', '2026-06-12'),
    ('estimated_date', 1)])
def test_internal_type_err(field_name: str, value: object) -> None:
    """Test wrong field types are reported by the internal check."""
    release = Release(name='R1')
    setattr(release, field_name, value)
    with pytest.raises(TypeError):
        release.check_consistency(NoTextIO())


@pytest.mark.parametrize('value', ['', 'R 1', 'R,1', 'a(b)'])
def test_internal_name_err(value: str) -> None:
    """Test an invalid release name is reported as a ValueError."""
    release = Release(name=value)
    with pytest.raises(ValueError):
        release.check_consistency(NoTextIO())


def test_check_releases_ok() -> None:
    """Test a list of uniquely named valid releases passes."""
    releases = [Release(name='R1'), Release(name='R2')]
    check_releases(releases, NoTextIO())


def test_check_releases_empty() -> None:
    """Test an empty list of releases passes the check."""
    check_releases([], NoTextIO())


def test_check_releases_dup() -> None:
    """Test duplicate release names are reported as a ValueError."""
    releases = [Release(name='R1'), Release(name='R1')]
    stderr_file = StringIO()
    with pytest.raises(ValueError):
        check_releases(releases, stderr_file=stderr_file)
    assert 'R1' in stderr_file.getvalue()


def test_check_releases_bad() -> None:
    """Test an internally invalid release is reported by the check."""
    releases = [Release(name='R 1')]
    with pytest.raises(ValueError):
        check_releases(releases, NoTextIO())
