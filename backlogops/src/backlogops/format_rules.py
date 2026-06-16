#! /usr/local/bin/python3
"""Rules for formatting table data."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from dataclasses import dataclass, field
from tableio import Fmt, Color, TableBorderStyle
from backlogops.backlog import Status


def default_status_format() -> dict[Status, Fmt]:
    """Return the default format specification for the status column."""
    return {
        Status.TODO: Fmt(),
        Status.IN_PROGRESS: Fmt(),
        Status.DONE: Fmt(italic=True, highlight=Color.GREEN),
        Status.REJECTED: Fmt(italic=True, highlight=Color.RED)}


@dataclass
class FormatRules:  # pylint: disable=too-many-instance-attributes
    """Rules for formatting table data."""

    backlog_first: bool = True
    """Whether to write the backlog before the releases."""

    border_style: TableBorderStyle = \
        TableBorderStyle.OUTER_FIRST_ROW_THICK_INNER_THIN
    """The border style to apply to the written table."""

    filtered_data_range: bool = True
    """Whether to mark the written data as a filtered data range."""

    first_row_format: Fmt = Fmt(bold=True)
    """The format specification for the column names row."""

    status_format: dict[Status, Fmt] = \
        field(default_factory=default_status_format)
    """The format specification for the status column."""

    estimate_late: Fmt = Fmt(bold=True, highlight=Color.RED)
    """The format for estimate values if later than planned."""

    estimate_early: Fmt = Fmt()
    """The format for estimate values if earlier than planned."""

    estimate_eq_planned: Fmt = Fmt()
    """The format for estimate values if equal to planned."""

    def get_status_format(self, status: Status) -> Fmt:
        """Return the format for a status."""
        return self.status_format.get(status, Fmt())

    def turn_off_cell_format(self) -> None:
        """Turn off all cell formatting.

        Make all cells plain, without any formatting.
        This does not affect the border style or the filtered data range.
        """
        self.first_row_format = Fmt()
        self.status_format = {status: Fmt() for status in Status}
        self.estimate_late = Fmt()
        self.estimate_early = Fmt()
        self.estimate_eq_planned = Fmt()

    def cell_format_used(self) -> bool:
        """Return True if any cell formatting is used."""
        return any([self.first_row_format != Fmt(),
                    any(fmt != Fmt() for fmt in self.status_format.values()),
                    self.estimate_late != Fmt(),
                    self.estimate_early != Fmt(),
                    self.estimate_eq_planned != Fmt()])
