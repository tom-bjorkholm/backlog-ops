#! /usr/local/bin/python3
"""Convert backlog items and releases to and from table rows.

A backlog item or a release is represented in a table as one row keyed by
its internal field name. These conversions are shared by the file IO and
by the formatting of table data, so they live in their own module to keep
the dependency order between those parts simple.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from collections.abc import Mapping
from dataclasses import fields
from datetime import date
from typing import Optional, TextIO
from tableio import Value
from backlogops.backlog import BacklogItem, DEPENDENCY_FIELDS, Status, \
    get_backlog_item
from backlogops.levels import Levels
from backlogops.releases import Release, get_release

BACKLOG_FIELDS = [item_field.name for item_field in fields(BacklogItem)
                  if item_field.name != 'extra_fields']
"""Internal backlog column names, in a stable write order."""

RELEASE_FIELDS = [item_field.name for item_field in fields(Release)]
"""Internal release column names, in a stable write order."""


def _is_empty(value: object) -> bool:
    """Return whether a cell value should be treated as absent."""
    return value is None or value == ''


def _date_cell(value: Optional[date]) -> Value:
    """Return a date as an ISO string cell, or None when absent."""
    return value.isoformat() if value is not None else None


def _cell_from_field(name: str, value: object) -> Value:
    """Return the cell value for one named backlog item field."""
    if name == 'status':
        assert isinstance(value, Status)
        return value.name
    if name in DEPENDENCY_FIELDS:
        assert isinstance(value, list)
        return ' '.join(value)
    if isinstance(value, date):
        return value.isoformat()
    assert value is None or isinstance(value, (str, int, float, bool))
    return value


def _extra_cell(value: object) -> Value:
    """Return an extra field value as a cell value."""
    if isinstance(value, date):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def item_to_row(item: BacklogItem) -> dict[str, Value]:
    """Return one backlog item as a row keyed by internal field name."""
    row: dict[str, Value] = {}
    for name in BACKLOG_FIELDS:
        row[name] = _cell_from_field(name, getattr(item, name))
    for key, value in item.extra_fields.items():
        row[key] = _extra_cell(value)
    return row


def release_to_row(release: Release) -> dict[str, Value]:
    """Return one release as a row keyed by internal field name."""
    return {'name': release.name,
            'planned_date': _date_cell(release.planned_date),
            'estimated_date': _date_cell(release.estimated_date)}


def _split_deps(value: object) -> list[str]:
    """Return the dependency keys parsed from one space separated cell."""
    if value is None:
        return []
    text = str(value).strip()
    return text.split() if text else []


def _maybe_int(value: object) -> object:
    """Return an integer when a numeric cell should be one, else the value."""
    if isinstance(value, bool):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return value
    return value


def _present_cells(row: Mapping[str, object]) -> dict[str, object]:
    """Return the row without cells that are absent (None or empty)."""
    return {key: value for key, value in row.items() if not _is_empty(value)}


def row_to_item(row: Mapping[str, object], levels: Optional[Levels] = None,
                stderr_file: TextIO = sys.stderr) -> BacklogItem:
    """Return a backlog item from a row keyed by internal field name."""
    prepared = _present_cells(row)
    for name in DEPENDENCY_FIELDS:
        if name in prepared:
            prepared[name] = _split_deps(row[name])
    for name in ('story_points', 'level'):
        if name in prepared:
            prepared[name] = _maybe_int(row[name])
    return get_backlog_item(prepared, levels, stderr_file)


def row_to_release(row: Mapping[str, object],
                   stderr_file: TextIO = sys.stderr) -> Release:
    """Return a release from a row keyed by internal field name."""
    return get_release(_present_cells(row), stderr_file, strict=False)
