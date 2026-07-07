#! /usr/local/bin/python3
"""Format the result of a Jira write operation into a text listing.

These helpers turn the named tuples returned by the add and update
operations into a labelled, copy-pasteable listing. Each section shows a
heading with its count, then one line per entry or a ``(none)`` line when
it is empty. The CLI prints the listing and the GUI shows it in a pop-up.

The functions live apart from the write logic in
:mod:`backlogops.jira_write` so that the write, update and rank modules can
share them without depending on each other in a cycle.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from backlogops.backlog import Backlog
from backlogops.jira_write import AddedToJira, FailedItem, StatusMismatch
from backlogops.jira_write_fields import FailedLink


def _labeled_lines(heading: str, count: int, body: list[str]) -> list[str]:
    """Return a heading with its count then the body, or a (none) line.

    An empty body becomes a single ``  (none)`` line, so every section
    shows either its items or that it has none. This is shared by the
    add-backlog and add-releases result listings.
    """
    return [f'{heading} ({count}):', *(body or ['  (none)'])]


def _result_section(heading: str, backlog: Backlog) -> list[str]:
    """Return the heading and the key-and-title lines for one backlog."""
    return _labeled_lines(heading, len(backlog),
                          [f'  {item.key}  {item.title}' for item in backlog])


def _key_section(heading: str, names: list[str]) -> list[str]:
    """Return a heading with its count and one indented line per name.

    This is shared by the backlog-update and release-update listings for
    their key-only or name-only sections.
    """
    return _labeled_lines(heading, len(names), [f'  {n}' for n in names])


def _outcome_prefix(updated: list[str], already_correct: list[str],
                    ignored: list[str]) -> list[str]:
    """Return the updated, already-correct and ignored key sections.

    This is the shared start of the backlog-update and release-update
    listings, before each adds its own trailing sections.
    """
    lines = _key_section('Updated in Jira', updated)
    lines.append('')
    lines.extend(_key_section('Already correct in Jira', already_correct))
    lines.append('')
    lines.extend(_key_section('Not in Jira (ignored)', ignored))
    return lines


def format_add_result(result: AddedToJira) -> str:
    """Return a listing of the added, present, failed and unmatched items.

    Each section has a heading with its count, then one ``key  title`` line
    per item, or a ``(none)`` line when the section is empty. The CLI
    prints this text and the GUI shows it in a copy-pasteable pop-up.
    """
    lines = _result_section('Added to Jira', result.stored)
    lines.append('')
    lines.extend(_result_section('Already in Jira', result.already_present))
    lines.append('')
    lines.extend(_failed_section('Failed to add', result.failed))
    lines.append('')
    lines.extend(_status_section('Status not set in Jira',
                                 result.status_mismatch))
    lines.append('')
    lines.extend(_link_section('Links not written', result.failed_links))
    return '\n'.join(lines)


def _failed_section(heading: str, failed: list[FailedItem]) -> list[str]:
    """Return the heading and the key, title and reason of each failure."""
    body = [f'  {entry.item.key}  {entry.item.title}  - {entry.reason}'
            for entry in failed]
    return _labeled_lines(heading, len(failed), body)


def _status_section(heading: str, mismatch: list[StatusMismatch]) -> list[str]:
    """Return the heading and the key, title and status of each mismatch."""
    body = [f'  {bad.item.key}  {bad.item.title}  - expected '
            f'{bad.expected.name}, Jira status {bad.actual!r}'
            for bad in mismatch]
    return _labeled_lines(heading, len(mismatch), body)


def _link_section(heading: str, links: list[FailedLink]) -> list[str]:
    """Return the heading and the source, target and reason of each link."""
    body = [f'  {link.item.key} -> {link.target}  ({link.relation})  '
            f'- {link.reason}' for link in links]
    return _labeled_lines(heading, len(links), body)
