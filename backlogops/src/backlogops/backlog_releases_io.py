#! /usr/local/bin/python3
"""Read and write a backlog and its releases as tables with TableIO.

A backlog and its releases form two tables. They are written to one file
(and read back) using TableIO, which supports several tables in one sheet
separated by headings. Reading walks the tables in the file and tells a
backlog table from a releases table by their columns: a table with a
``key`` column is the backlog, a table with a ``name`` column is the
releases.

The internal field names of the data model can differ from the column
names in the file. An :class:`InputFormatConfig` carries a map from
external column name to internal field name, and an
:class:`OutputFormatConfig` carries a map from internal field name to
external column name. The dependency lists of a backlog item are stored
as one space separated string per dependency kind, and the extra fields
of a backlog item become extra columns.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from collections.abc import Mapping
from dataclasses import fields
from datetime import date
from typing import Optional, TextIO
from config_as_json import PathOrStr
from tableio import CAP_IGNORABLE, Capabilities, DictData, FileAccess, \
    TableBorderStyle, TableIO, Value, access_capabilities, tio_config_create
from backlogops.backlog import Backlog, BacklogItem, DEPENDENCY_FIELDS, \
    Status, get_backlog_item
from backlogops.backlog_releases import BacklogReleases
from backlogops.io_config import InputFormatConfig, OutputFormatConfig
from backlogops.levels import Levels
from backlogops.releases import Release, Releases, get_release

BACKLOG_FIELDS = [item_field.name for item_field in fields(BacklogItem)
                  if item_field.name != 'extra_fields']
"""Internal backlog column names, in a stable write order."""

RELEASE_FIELDS = [item_field.name for item_field in fields(Release)]
"""Internal release column names, in a stable write order."""

BACKLOG_HEADING = 'Backlog'
"""Heading written before the backlog table."""

RELEASE_HEADING = 'Releases'
"""Heading written before the releases table."""

BORDER_STYLE = TableBorderStyle.OUTER_FIRST_ROW_THICK_INNER_THIN
"""Thick outer and first-row borders with thin inner lines."""


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


def _rename(row: dict[str, Value], names: dict[str, str]) -> dict[str, Value]:
    """Return the row with its keys translated through a name map."""
    return {names.get(key, key): value for key, value in row.items()}


def _is_backlog_table(rows: DictData[Value]) -> bool:
    """Return whether a table of internal-named rows is the backlog."""
    return 'key' in rows[0]


def _is_release_table(rows: DictData[Value]) -> bool:
    """Return whether a table of internal-named rows is the releases."""
    return 'name' in rows[0]


def _collect_tables(config: InputFormatConfig, data_file: PathOrStr,
                    stderr_file: TextIO
                    ) -> tuple[DictData[Value], DictData[Value]]:
    """Read every table and split it into backlog and release rows."""
    capabilities = access_capabilities(FileAccess.READ, error_file=stderr_file)
    backlog_rows: DictData[Value] = []
    release_rows: DictData[Value] = []
    with tio_config_create(config=config.tableio, file_name=data_file,
                           file_access=FileAccess.READ,
                           capabilities=capabilities) as tableio:
        while True:
            result = tableio.read_table_dictdata()
            if not result.data:
                break
            rows = [_rename(row, config.to_internal) for row in result.data]
            if _is_backlog_table(rows):
                backlog_rows.extend(rows)
            elif _is_release_table(rows):
                release_rows.extend(rows)
            else:
                raise ValueError('A table has neither a key column (backlog) '
                                 'nor a name column (releases).')
    return backlog_rows, release_rows


def read_backlog_releases(data_file: PathOrStr, config: InputFormatConfig,
                          levels: Optional[Levels] = None,
                          stderr_file: TextIO = sys.stderr) -> BacklogReleases:
    """Read a backlog, releases, or both from one file.

    Each table in the file is read and classified by its columns. The
    column names are translated to internal field names through the input
    configuration before classification and conversion. Field values are
    converted to their internal types; consistency across items is not
    checked here.

    Args:
        data_file: The data file to read.
        config: The input configuration (format and column-name map).
        levels: The levels used to resolve a string level, or None for
                the default levels.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The backlog and releases found in the file. Either may be empty.

    Raises:
        KeyError: A mandatory field is missing in a row.
        TypeError: A field value has a type that cannot be converted.
        ValueError: A table cannot be classified as backlog or releases.
    """
    backlog_rows, release_rows = _collect_tables(config, data_file,
                                                 stderr_file)
    backlog: Backlog = [row_to_item(row, levels, stderr_file)
                        for row in backlog_rows]
    releases: Releases = [row_to_release(row, stderr_file)
                          for row in release_rows]
    return BacklogReleases(backlog=backlog, releases=releases)


def _write_capabilities(stderr_file: TextIO) -> Capabilities:
    """Return CREATE capabilities that prefer borders and a filter area.

    The border and filter features are requested as ignorable, so a
    backend that supports them (such as an Excel writer) is preferred,
    while formats without them (such as CSV) are still allowed.
    """
    base = access_capabilities(FileAccess.CREATE, error_file=stderr_file)
    return base._replace(filtered_data_range=CAP_IGNORABLE,
                         can_write_borders=CAP_IGNORABLE)


def _backlog_order(backlog: Backlog) -> list[str]:
    """Return the backlog column order, with extra fields appended."""
    extra = sorted({name for item in backlog for name in item.extra_fields})
    return BACKLOG_FIELDS + extra


def _write_table(tableio: TableIO, heading: str, rows: DictData[Value],
                 column_order: list[str], names: dict[str, str]) -> None:
    """Write one heading and one bordered, filterable table."""
    tableio.write_heading(heading)
    external_rows = [_rename(row, names) for row in rows]
    external_order = [names.get(name, name) for name in column_order]
    tableio.write_table_dictdata(external_rows, column_order=external_order,
                                 missing_ok=True, filtered_data_range=True,
                                 border_style=BORDER_STYLE)


def _ordered_sections(data: BacklogReleases, backlog_first: bool
                      ) -> list[tuple[str, DictData[Value], list[str]]]:
    """Return the non-empty tables to write, in the requested order."""
    backlog_rows = [item_to_row(item) for item in data.backlog]
    release_rows = [release_to_row(release) for release in data.releases]
    backlog = (BACKLOG_HEADING, backlog_rows, _backlog_order(data.backlog))
    releases = (RELEASE_HEADING, release_rows, RELEASE_FIELDS)
    sections = [backlog, releases] if backlog_first else [releases, backlog]
    return [section for section in sections if section[1]]


def write_backlog_releases(data: BacklogReleases, data_file: PathOrStr,
                           config: OutputFormatConfig,
                           backlog_first: bool = True,
                           stderr_file: TextIO = sys.stderr) -> None:
    """Write a backlog, releases, or both to one file.

    Each non-empty table is written with a heading before it, so several
    tables can share one file. Internal field names are translated to
    external column names through the output configuration. When both
    tables are present, ``backlog_first`` decides their order.

    Args:
        data: The backlog and releases to write.
        data_file: The data file to create.
        config: The output configuration (format and column-name map).
        backlog_first: Whether to write the backlog before the releases.
        stderr_file: Stream used for user-facing diagnostics.
    """
    capabilities = _write_capabilities(stderr_file)
    sections = _ordered_sections(data, backlog_first)
    with tio_config_create(config=config.tableio, file_name=data_file,
                           file_access=FileAccess.CREATE,
                           capabilities=capabilities) as tableio:
        for heading, rows, column_order in sections:
            _write_table(tableio, heading, rows, column_order,
                         config.to_external)
