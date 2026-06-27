#! /usr/local/bin/python3
"""Read and write a backlog and its releases as tables with TableIO.

A backlog and its releases form two tables. They are written to one file
(and read back) using TableIO, which supports several tables in one sheet
separated by headings. Reading walks the tables in the file and tells a
backlog table from a releases table by their columns: a table with a
``key`` column is the backlog, a table with a ``name`` column is the
releases.

The internal field names of the data model can differ from the column
names in the file. An :class:`InputFormatConfig` carries one
external-to-internal map per table (``backlog_to_internal`` and
``release_to_internal``), and an :class:`OutputFormatConfig` carries one
internal-to-external map per table (``backlog_to_external`` and
``release_to_external``). Each map honours the three cases of
:func:`backlogops.table_rows.apply_column_map`: an absent name is read or
written unchanged, a mapped name is renamed, and a name mapped to None
drops that column. The dependency lists of a backlog item are stored as
one space separated string per dependency kind, and the extra fields of a
backlog item become extra columns.

The level of a backlog item is written as a numeric ``level`` column, a
named ``level name`` column, or both, as the output configuration's
:class:`LevelDisplay` decides. Both columns are recognised when reading;
when both appear the numeric ``level`` column wins and the ``level name``
column is ignored.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Optional, TextIO
from config_as_json import PathOrStr
from tableio import CAP_IGNORABLE, Capabilities, DictData, FileAccess, \
    TableIO, Value, ValueFmt, access_capabilities, tio_config_create
from backlogops.backlog import Backlog, Status
from backlogops.backlog_releases import BacklogReleases
from backlogops.io_config import InputFormatConfig, OutputFormatConfig
from backlogops.table_create import FileExistsCb
from backlogops.levels import DEFAULT_LEVELS, Levels
from backlogops.releases import Releases
from backlogops.format_rules import FormatRules
from backlogops.apply_format_rules import format_backlog, format_releases
from backlogops.table_rows import BACKLOG_FIELDS, RELEASE_FIELDS, \
    apply_column_map, display_level_order, display_level_rows, \
    fold_level_name, map_column_order, row_to_item, row_to_release

BACKLOG_HEADING = 'Backlog'
"""Heading written before the backlog table."""

RELEASE_HEADING = 'Releases'
"""Heading written before the releases table."""


@dataclass
class _Section:
    """One table to write: heading, formatted rows, order and name map."""

    heading: str
    rows: DictData[ValueFmt]
    order: list[str]
    names: Mapping[str, Optional[str]]


def _is_backlog_table(rows: DictData[Value]) -> bool:
    """Return whether a table of internal-named rows is the backlog."""
    return 'key' in rows[0]


def _is_release_table(rows: DictData[Value]) -> bool:
    """Return whether a table of internal-named rows is the releases."""
    return 'name' in rows[0]


def _classify_rows(config: InputFormatConfig, rows: DictData[Value]
                   ) -> tuple[DictData[Value], DictData[Value]]:
    """Map one input table and return it as backlog or release rows.

    The backlog input map is applied first; a resulting ``key`` column
    marks the backlog. Otherwise the release input map is applied and a
    resulting ``name`` column marks the releases. A table that matches
    neither is rejected.
    """
    backlog = [apply_column_map(row, config.backlog_to_internal)
               for row in rows]
    if _is_backlog_table(backlog):
        return backlog, []
    release = [apply_column_map(row, config.release_to_internal)
               for row in rows]
    if _is_release_table(release):
        return [], release
    raise ValueError('A table has neither a key column (backlog) '
                     'nor a name column (releases).')


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
            backlog, release = _classify_rows(config, result.data)
            backlog_rows.extend(backlog)
            release_rows.extend(release)
    return backlog_rows, release_rows


def _merge_status_maps(global_map: Optional[dict[str, Status]],
                       preset_map: Optional[dict[str, Status]]
                       ) -> dict[str, Status]:
    """Return the effective status name map, preset entries winning.

    The keys are lowercased so a status name matches regardless of case
    and a preset entry overrides a global entry that differs only in case.

    Args:
        global_map: The library-wide status map, or None when absent.
        preset_map: The per-input override status map, or None when absent.

    Returns:
        The merged status map keyed by lowercased status name.
    """
    result: dict[str, Status] = {}
    for source in (global_map, preset_map):
        if source:
            for name, status in source.items():
                result[name.lower()] = status
    return result


def read_backlog_releases(data_file: PathOrStr, config: InputFormatConfig,
                          levels: Optional[Levels] = None,
                          status_map: Optional[dict[str, Status]] = None,
                          stderr_file: TextIO = sys.stderr) -> BacklogReleases:
    """Read a backlog, releases, or both from one file.

    Each table in the file is read and classified by its columns. The
    column names are translated to internal field names through the input
    configuration before classification and conversion. A ``level`` and a
    ``level name`` column are both recognised; when both are present the
    numeric ``level`` column is used and the ``level name`` column is
    ignored. A string status is matched case-insensitively against the
    effective status map, which merges the given library-wide ``status_map``
    with the input configuration's own ``status_input_map`` (the latter
    overriding per name). Field values are converted to their internal
    types; consistency across items is not checked here.

    Args:
        data_file: The data file to read.
        config: The input configuration (format, column-name maps and
                per-input status map).
        levels: The levels used to resolve a string level, or None for
                the default levels.
        status_map: The library-wide status map, or None when absent. It
                is merged with the input configuration's own status map.
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
    fold_level_name(backlog_rows, stderr_file)
    effective = _merge_status_maps(status_map, config.status_input_map)
    backlog: Backlog = [row_to_item(row, levels, effective, stderr_file)
                        for row in backlog_rows]
    releases: Releases = [row_to_release(row, stderr_file)
                          for row in release_rows]
    return BacklogReleases(backlog=backlog, releases=releases)


def _write_capabilities(stderr_file: TextIO) -> Capabilities:
    """Return CREATE capabilities that prefer borders, format and filter.

    The border, cell formatting, highlight and filter features are
    requested as ignorable, so a backend that supports them (such as an
    Excel backend like XlsxWriter or OpenPyXL) is preferred, while
    formats without them (such as CSV) and backends without them
    (such as pylightxl for Excel) are still allowed.
    """
    base = access_capabilities(FileAccess.CREATE, error_file=stderr_file)
    return base._replace(filtered_data_range=CAP_IGNORABLE,
                         can_write_borders=CAP_IGNORABLE,
                         can_fmt_row=CAP_IGNORABLE,
                         can_fmt_value=CAP_IGNORABLE,
                         can_write_highlight=CAP_IGNORABLE)


def _backlog_order(backlog: Backlog) -> list[str]:
    """Return the backlog column order, with extra fields appended."""
    extra = sorted({name for item in backlog for name in item.extra_fields})
    return BACKLOG_FIELDS + extra


def _write_table(tableio: TableIO, section: _Section,
                 rules: FormatRules) -> None:
    """Write one heading and one formatted, bordered table."""
    tableio.write_heading(section.heading)
    external_rows = [apply_column_map(row, section.names)
                     for row in section.rows]
    external_order = map_column_order(section.order, section.names)
    tableio.write_table_dictdata(external_rows, column_order=external_order,
                                 missing_ok=True,
                                 first_row_format=rules.first_row_format,
                                 filtered_data_range=rules.filtered_data_range,
                                 border_style=rules.border_style)


def _backlog_section(data: BacklogReleases, rules: FormatRules, levels: Levels,
                     config: OutputFormatConfig,
                     stderr_file: TextIO) -> _Section:
    """Return the backlog heading, rows and order with levels expanded."""
    display = config.level_display
    rows = display_level_rows(format_backlog(data.backlog, rules), levels,
                              display, stderr_file)
    order = display_level_order(_backlog_order(data.backlog), display)
    return _Section(BACKLOG_HEADING, rows, order, config.backlog_to_external)


def _ordered_sections(data: BacklogReleases, rules: FormatRules,
                      levels: Levels, config: OutputFormatConfig,
                      stderr_file: TextIO) -> list[_Section]:
    """Return the non-empty tables to write, in the requested order."""
    backlog = _backlog_section(data, rules, levels, config, stderr_file)
    release_rows = format_releases(data.releases, rules)
    releases = _Section(RELEASE_HEADING, release_rows, list(RELEASE_FIELDS),
                        config.release_to_external)
    sections = [backlog, releases] if rules.backlog_first else \
        [releases, backlog]
    return [section for section in sections if section.rows]


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def write_backlog_releases(data: BacklogReleases, data_file: PathOrStr,
                           config: OutputFormatConfig,
                           format_rules: Optional[FormatRules] = None,
                           levels: Optional[Levels] = None,
                           stderr_file: TextIO = sys.stderr,
                           file_exists_callback: Optional[FileExistsCb]
                           = None) -> None:
    """Write a backlog, releases, or both to one file.

    Each non-empty table is written with a heading before it, so several
    tables can share one file. Internal field names are translated to
    external column names through the output configuration, using its
    backlog map for the backlog table and its releases map for the
    releases table; a name mapped to None drops that column. The level of
    a backlog item is written as its number, its name, or both, as the
    output configuration's :class:`LevelDisplay` decides, using ``levels``
    to translate a number to a name. The format rules decide the table
    order, the borders, the filter range and the cell formatting; when
    omitted the default :class:`FormatRules` apply.

    Args:
        data: The backlog and releases to write.
        data_file: The data file to create.
        config: The output configuration (format, per-table column-name
                maps and level display).
        format_rules: How to format the written data, or None for the
                      default format rules.
        levels: The levels used to translate a level number to a name, or
                None for the default levels.
        stderr_file: Stream used for user-facing diagnostics.
        file_exists_callback: Called when the file already exists, as
                              documented for :mod:`backlogops.table_create`.
                              None refuses an existing file.
    """
    rules = FormatRules() if format_rules is None else format_rules
    chosen_levels = DEFAULT_LEVELS if levels is None else levels
    capabilities = _write_capabilities(stderr_file)
    sections = _ordered_sections(data, rules, chosen_levels, config,
                                 stderr_file)
    with tio_config_create(config=config.tableio, file_name=data_file,
                           file_access=FileAccess.CREATE,
                           capabilities=capabilities,
                           file_exists_callback=file_exists_callback
                           ) as tableio:
        for section in sections:
            _write_table(tableio, section, rules)
