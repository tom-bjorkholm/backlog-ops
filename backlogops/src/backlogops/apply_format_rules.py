#! /usr/local/bin/python3
"""Apply format rules to backlog and release table data."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from datetime import date
from typing import Optional
from tableio import DictData, Fmt, ValueFmt
from backlogops.backlog import Backlog, BacklogItem
from backlogops.releases import Release, Releases
from backlogops.format_rules import FormatRules
from backlogops.table_rows import item_to_row, release_to_row


def _estimate_format(estimated: Optional[date], planned: Optional[date],
                     rules: FormatRules) -> Fmt:
    """Return the estimate-cell format from estimated versus planned date.

    A missing estimated or planned date leaves the cell unformatted, as
    there is then nothing to compare.
    """
    if estimated is None or planned is None:
        return Fmt()
    if estimated > planned:
        return rules.estimate_late
    if estimated < planned:
        return rules.estimate_early
    return rules.estimate_eq_planned


def _item_cell_format(name: str, item: BacklogItem, estimate: Fmt,
                      rules: FormatRules) -> Fmt:
    """Return the format for one backlog cell named by its field."""
    if name == 'status':
        return rules.get_status_format(item.status)
    if name == 'estimated_ready_date':
        return estimate
    return Fmt()


def _format_item(item: BacklogItem, rules: FormatRules) -> dict[str, ValueFmt]:
    """Return one backlog item as a formatted row of cells."""
    estimate = _estimate_format(item.estimated_ready_date,
                                item.planned_ready_date, rules)
    return {name: ValueFmt(value=value,
                           fmt=_item_cell_format(name, item, estimate, rules))
            for name, value in item_to_row(item).items()}


def format_backlog(backlog: Backlog,
                   format_rules: FormatRules) -> DictData[ValueFmt]:
    """Format the backlog according to the format rules.

    Each backlog item becomes one row of formatted cells, keyed by the
    internal field name. The status cell is formatted by its status, and
    the estimated-ready-date cell by its relation to the planned-ready
    date; all other cells are left unformatted.

    Args:
        backlog: The backlog to format.
        format_rules: The format rules to apply.

    Returns:
        The formatted backlog rows, ready for TableIO.
    """
    return [_format_item(item, format_rules) for item in backlog]


def _format_release(release: Release,
                    rules: FormatRules) -> dict[str, ValueFmt]:
    """Return one release as a formatted row of cells."""
    estimate = _estimate_format(release.estimated_date, release.planned_date,
                                rules)
    return {name: ValueFmt(value=value,
                           fmt=estimate if name == 'estimated_date' else Fmt())
            for name, value in release_to_row(release).items()}


def format_releases(releases: Releases,
                    format_rules: FormatRules) -> DictData[ValueFmt]:
    """Format the releases according to the format rules.

    Each release becomes one row of formatted cells, keyed by the internal
    field name. The estimated-date cell is formatted by its relation to the
    planned date; the other cells are left unformatted.

    Args:
        releases: The releases to format.
        format_rules: The format rules to apply.

    Returns:
        The formatted release rows, ready for TableIO.
    """
    return [_format_release(release, format_rules) for release in releases]
