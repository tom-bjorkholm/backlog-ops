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
from typing import Optional, TextIO, TypeVar
from tableio import DictData, Value, ValueFmt
from backlogops.backlog import BacklogItem, DEPENDENCY_FIELDS, Status, \
    get_backlog_item
from backlogops.levels import LevelDisplay, Levels, level_name
from backlogops.releases import Release, get_release

BACKLOG_FIELDS = [item_field.name for item_field in fields(BacklogItem)
                  if item_field.name != 'extra_fields']
"""Internal backlog column names, in a stable write order."""

RELEASE_FIELDS = [item_field.name for item_field in fields(Release)]
"""Internal release column names, in a stable write order."""

LEVEL_COLUMN = 'level'
"""Default column name carrying the numeric backlog item level."""

LEVEL_NAME_COLUMN = 'level name'
"""Default column name carrying the named backlog item level."""

_Cell = TypeVar('_Cell')


def apply_column_map(row: Mapping[str, _Cell],
                     names: Mapping[str, Optional[str]]) -> dict[str, _Cell]:
    """Return one row with its columns renamed or dropped by a name map.

    Three cases are honoured for each column name: a name absent from the
    map is kept unchanged, a name mapped to another string is renamed, and
    a name mapped to None drops that column from the row.
    """
    result: dict[str, _Cell] = {}
    for name, value in row.items():
        if name not in names:
            result[name] = value
            continue
        new_name = names[name]
        if new_name is not None:
            result[new_name] = value
    return result


def map_column_order(order: list[str],
                     names: Mapping[str, Optional[str]]) -> list[str]:
    """Return a column order with names renamed or dropped by a name map.

    The same three cases as :func:`apply_column_map` are honoured, so the
    order stays consistent with rows passed through that function.
    """
    result: list[str] = []
    for name in order:
        if name not in names:
            result.append(name)
            continue
        new_name = names[name]
        if new_name is not None:
            result.append(new_name)
    return result


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


def _display_columns(display: LevelDisplay) -> tuple[bool, bool]:
    """Return whether to write the numeric and the named level column."""
    numeric = display in (LevelDisplay.NUMERIC, LevelDisplay.BOTH)
    named = display in (LevelDisplay.NAME, LevelDisplay.BOTH)
    return numeric, named


def display_level_order(order: list[str], display: LevelDisplay) -> list[str]:
    """Return a column order with the level column expanded for display.

    The single internal ``level`` column is replaced by the numeric
    column, the named column, or both, as chosen by ``display``. Every
    other column is kept in place.
    """
    numeric, named = _display_columns(display)
    result: list[str] = []
    for name in order:
        if name != LEVEL_COLUMN:
            result.append(name)
            continue
        if numeric:
            result.append(LEVEL_COLUMN)
        if named:
            result.append(LEVEL_NAME_COLUMN)
    return result


def _name_cell_text(value: Value, levels: Levels) -> tuple[str, bool]:
    """Return the displayed level name and whether a name was found.

    A level number with a configured name uses that name. A number
    without a configured name falls back to the number as text, so no
    value is ever lost; the second return value reports that fallback.
    """
    if isinstance(value, int) and not isinstance(value, bool):
        name = level_name(value, levels)
        if name is not None:
            return name, True
        return str(value), False
    return ('' if value is None else str(value)), False


def _expand_level_cell(row: dict[str, ValueFmt], levels: Levels,
                       display: LevelDisplay,
                       unnamed: list[Value]) -> dict[str, ValueFmt]:
    """Return one row with its level cell expanded into display columns."""
    if LEVEL_COLUMN not in row:
        return dict(row)
    numeric, named = _display_columns(display)
    result: dict[str, ValueFmt] = {}
    for key, cell in row.items():
        if key != LEVEL_COLUMN:
            result[key] = cell
            continue
        if numeric:
            result[LEVEL_COLUMN] = cell
        if named:
            text, found = _name_cell_text(cell.value, levels)
            result[LEVEL_NAME_COLUMN] = ValueFmt(value=text, fmt=cell.fmt)
            if not found and cell.value not in unnamed:
                unnamed.append(cell.value)
    return result


def _report_unnamed(unnamed: list[Value], stderr_file: TextIO) -> None:
    """Inform that some level numbers had no configured name."""
    if not unnamed:
        return
    numbers = ', '.join(str(value) for value in unnamed)
    print('Levels without a configured name are shown as their number: '
          f'{numbers}.', file=stderr_file)


def display_level_rows(rows: DictData[ValueFmt], levels: Levels,
                       display: LevelDisplay, stderr_file: TextIO = sys.stderr
                       ) -> DictData[ValueFmt]:
    """Return rows with the level column expanded for display.

    Each row's single internal ``level`` cell becomes the numeric column,
    the named column, or both, as chosen by ``display``. A level number
    with no configured name is shown as its number, and one information
    message then lists those numbers.
    """
    unnamed: list[Value] = []
    result = [_expand_level_cell(row, levels, display, unnamed)
              for row in rows]
    _report_unnamed(unnamed, stderr_file)
    return result


def fold_level_name(rows: DictData[Value],
                    stderr_file: TextIO = sys.stderr) -> None:
    """Fold a ``level name`` column into the ``level`` column in place.

    When a row has both columns the numeric ``level`` column is kept and
    the ``level name`` column is discarded. When only the ``level name``
    column is present its value becomes the level, to be resolved by the
    item conversion. The ``level name`` column is always removed so it is
    never stored as an extra field. One information message is printed
    when both columns appeared together.
    """
    both_seen = False
    for row in rows:
        if LEVEL_NAME_COLUMN not in row:
            continue
        name_value = row.pop(LEVEL_NAME_COLUMN)
        if _is_empty(name_value):
            continue
        if LEVEL_COLUMN in row and not _is_empty(row[LEVEL_COLUMN]):
            both_seen = True
        else:
            row[LEVEL_COLUMN] = name_value
    if both_seen:
        print('Both a level and a level name column were found; using the '
              'numeric level column and ignoring the level name column.',
              file=stderr_file)
