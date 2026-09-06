#! /usr/local/bin/python3
"""Format the result of a Jira operation into a text listing.

These helpers turn the named tuples returned by the add, update, rank,
order and rename operations into a labelled, copy-pasteable listing.
:func:`_build_report` opens a listing with a banner naming what did not
happen, then shows the problem sections, the skipped sections and last
what succeeded. A user who sees only the top of a small pop-up therefore
still sees that not everything was written. Each section shows a heading
with its count, then one line per entry or a ``(none)`` line when it is
empty. The CLI prints the listing and the GUI shows it in a pop-up whose
title it marks using :func:`report_has_problems`.

The functions live apart from the write logic in
:mod:`backlogops.jira_write` so that the write, update and rank modules can
share them without depending on each other in a cycle.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import NamedTuple, Sequence
from backlogops.backlog import Backlog
from backlogops.jira_write import AddedToJira, FailedItem
from backlogops.jira_write_status import StatusMismatch
from backlogops.jira_write_fields import FailedField, FailedLink

_PROBLEM_BANNER = 'NOT EVERYTHING SUCCEEDED IN JIRA:'
"""First line of a listing where something asked for did not happen."""
_SKIPPED_BANNER = 'Skipped:'
"""First line of the banner part naming what was deliberately skipped."""
_ALL_OK_BANNER = 'Everything requested succeeded in Jira.'
"""Whole banner of a listing with neither problems nor skipped entries."""


class _ReportSection(NamedTuple):
    """One labelled section of a Jira result listing.

    Fields:
        heading: The section label, shown with the entry count in
            parentheses.
        body: The already indented lines describing the entries, one line
            per entry and empty when the section has no entry.
    """

    heading: str
    body: list[str]

    def lines(self) -> list[str]:
        """Return the heading with its count, then the body or (none)."""
        return [f'{self.heading} ({len(self.body)}):',
                *(self.body or ['  (none)'])]

    def banner_line(self) -> str:
        """Return the banner line naming the section and its count."""
        return f'  {self.heading}: {len(self.body)}'


def report_has_problems(report: str) -> bool:
    """Return whether a formatted Jira listing reports a problem.

    A listing where something the user asked for did not happen opens with
    the problem banner. The GUI marks the pop-up title of such a listing,
    so a user whose log is hidden behind another window still sees that
    not everything succeeded.
    """
    return report.startswith(_PROBLEM_BANNER)


def _banner_part(heading: str,
                 sections: Sequence[_ReportSection]) -> list[str]:
    """Return the heading and one count line per non-empty section."""
    used = [section for section in sections if section.body]
    return [heading, *(section.banner_line() for section in used)] \
        if used else []


def _banner(problems: Sequence[_ReportSection],
            skipped: Sequence[_ReportSection]) -> list[str]:
    """Return the opening lines naming what did not happen in Jira.

    A non-empty problem section makes the listing open with the problem
    banner, which :func:`report_has_problems` detects. Skipped entries are
    named under their own heading without that alarm, since they were
    skipped by the policy the user chose. A listing with neither says that
    everything succeeded.
    """
    lines = _banner_part(_PROBLEM_BANNER, problems)
    lines.extend(_banner_part(_SKIPPED_BANNER, skipped))
    return lines or [_ALL_OK_BANNER]


def _build_report(*, problems: Sequence[_ReportSection],
                  done: Sequence[_ReportSection],
                  skipped: Sequence[_ReportSection] = ()) -> str:
    """Return the banner and the sections of one Jira result listing.

    The banner comes first, then the problem sections, the skipped
    sections and the sections of what was done, separated by blank lines.
    What did not happen comes before what did, so it is visible without
    scrolling a small pop-up.
    """
    blocks = ['\n'.join(_banner(problems, skipped))]
    blocks.extend('\n'.join(section.lines())
                  for section in (*problems, *skipped, *done))
    return '\n\n'.join(blocks)


def _result_section(heading: str, backlog: Backlog) -> _ReportSection:
    """Return the heading and the key-and-title lines for one backlog."""
    body = [f'  {item.key}  {item.title}' for item in backlog]
    return _ReportSection(heading, body)


def _key_section(heading: str, names: list[str]) -> _ReportSection:
    """Return a heading with its count and one indented line per name.

    This is shared by the backlog-update and release-update listings for
    their key-only or name-only sections.
    """
    return _ReportSection(heading, [f'  {n}' for n in names])


def _failed_section(heading: str, failed: list[FailedItem]) -> _ReportSection:
    """Return the heading and the key, title and reason of each failure."""
    body = [f'  {entry.item.key}  {entry.item.title}  - {entry.reason}'
            for entry in failed]
    return _ReportSection(heading, body)


def _status_section(heading: str,
                    mismatch: list[StatusMismatch]) -> _ReportSection:
    """Return the heading and the key, title and status of each mismatch."""
    body = [f'  {bad.item.key}  {bad.item.title}  - expected '
            f'{bad.expected.name}, Jira status {bad.actual!r}'
            for bad in mismatch]
    return _ReportSection(heading, body)


def _field_section(heading: str, fields: list[FailedField]) -> _ReportSection:
    """Return the heading and the key, field and reason of each refusal."""
    body = [f'  {bad.item.key}  {bad.field}  - {bad.reason}'
            for bad in fields]
    return _ReportSection(heading, body)


def _link_section(heading: str, links: list[FailedLink]) -> _ReportSection:
    """Return the heading and the source, target and reason of each link."""
    body = [f'  {link.item.key} -> {link.target}  ({link.relation})  '
            f'- {link.reason}' for link in links]
    return _ReportSection(heading, body)


def format_add_result(result: AddedToJira) -> str:
    """Return a listing of the added, present, failed and unmatched items.

    The listing opens with a banner naming what Jira refused, then shows
    the refused items, field values, statuses and links, and last the
    added and already-present items. Each section has a heading with its
    count, then one ``key  title`` line per item, or a ``(none)`` line
    when the section is empty. An item whose issue was created but whose
    field value or link Jira refused is in ``Added to Jira`` and again in
    the section naming what was refused. The CLI prints this text and the
    GUI shows it in a copy-pasteable pop-up.
    """
    return _build_report(
        problems=[_failed_section('Failed to add', result.failed),
                  _status_section('Status not set in Jira',
                                  result.status_mismatch),
                  _field_section('Fields not set', result.failed_fields),
                  _link_section('Links not written', result.failed_links)],
        done=[_result_section('Added to Jira', result.stored),
              _result_section('Already in Jira', result.already_present)])
