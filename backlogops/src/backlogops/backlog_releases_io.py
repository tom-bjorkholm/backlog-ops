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
from typing import Optional, TextIO, TypeVar
from config_as_json import PathOrStr
from tableio import CAP_IGNORABLE, Capabilities, DictData, FileAccess, \
    TableIO, Value, ValueFmt, access_capabilities, tio_config_create
from backlogops.backlog import Backlog
from backlogops.backlog_releases import BacklogReleases
from backlogops.io_config import InputFormatConfig, OutputFormatConfig
from backlogops.table_create import FileExistsCb
from backlogops.levels import Levels
from backlogops.releases import Releases
from backlogops.format_rules import FormatRules
from backlogops.apply_format_rules import format_backlog, format_releases
from backlogops.table_rows import BACKLOG_FIELDS, RELEASE_FIELDS, \
    row_to_item, row_to_release

BACKLOG_HEADING = 'Backlog'
"""Heading written before the backlog table."""

RELEASE_HEADING = 'Releases'
"""Heading written before the releases table."""

_RenameCell = TypeVar('_RenameCell', Value, ValueFmt)


def _rename(row: dict[str, _RenameCell],
            names: dict[str, str]) -> dict[str, _RenameCell]:
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


def _write_table(tableio: TableIO,
                 section: tuple[str, DictData[ValueFmt], list[str]],
                 names: dict[str, str], rules: FormatRules) -> None:
    """Write one heading and one formatted, bordered table."""
    heading, rows, column_order = section
    tableio.write_heading(heading)
    external_rows = [_rename(row, names) for row in rows]
    external_order = [names.get(name, name) for name in column_order]
    tableio.write_table_dictdata(external_rows, column_order=external_order,
                                 missing_ok=True,
                                 first_row_format=rules.first_row_format,
                                 filtered_data_range=rules.filtered_data_range,
                                 border_style=rules.border_style)


def _ordered_sections(data: BacklogReleases, rules: FormatRules
                      ) -> list[tuple[str, DictData[ValueFmt], list[str]]]:
    """Return the non-empty tables to write, in the requested order."""
    backlog_rows = format_backlog(data.backlog, rules)
    release_rows = format_releases(data.releases, rules)
    backlog = (BACKLOG_HEADING, backlog_rows, _backlog_order(data.backlog))
    releases = (RELEASE_HEADING, release_rows, RELEASE_FIELDS)
    sections = [backlog, releases] if rules.backlog_first else \
        [releases, backlog]
    return [section for section in sections if section[1]]


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def write_backlog_releases(data: BacklogReleases, data_file: PathOrStr,
                           config: OutputFormatConfig,
                           format_rules: Optional[FormatRules] = None,
                           stderr_file: TextIO = sys.stderr,
                           file_exists_callback: Optional[FileExistsCb]
                           = None) -> None:
    """Write a backlog, releases, or both to one file.

    Each non-empty table is written with a heading before it, so several
    tables can share one file. Internal field names are translated to
    external column names through the output configuration. The format
    rules decide the table order, the borders, the filter range and the
    cell formatting; when omitted the default :class:`FormatRules` apply.

    Args:
        data: The backlog and releases to write.
        data_file: The data file to create.
        config: The output configuration (format and column-name map).
        format_rules: How to format the written data, or None for the
                      default format rules.
        stderr_file: Stream used for user-facing diagnostics.
        file_exists_callback: Called when the file already exists, as
                              documented for :mod:`backlogops.table_create`.
                              None refuses an existing file.
    """
    rules = FormatRules() if format_rules is None else format_rules
    capabilities = _write_capabilities(stderr_file)
    sections = _ordered_sections(data, rules)
    with tio_config_create(config=config.tableio, file_name=data_file,
                           file_access=FileAccess.CREATE,
                           capabilities=capabilities,
                           file_exists_callback=file_exists_callback
                           ) as tableio:
        for section in sections:
            _write_table(tableio, section, config.to_external, rules)
