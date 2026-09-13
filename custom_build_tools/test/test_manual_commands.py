"""Check the command examples of the hand-written user manual.

The chapters under ``doc/using_backlogops`` are written by hand, unlike the
``doc/*.md`` files generated from the docstrings, so a withdrawn choice
value or a renamed flag survives there until a reader tries it. These tests
take every command line out of the fenced code blocks of the manual and
hand it to the very parser that command builds, so a stale example fails
the build instead of reaching a reader.

Two mistakes are caught. A command the parser rejects outright is one a
reader cannot run at all. A command that repeats an option which only
stores its last value is worse, because it runs and quietly does less than
it says: ``-l Epic -l Story`` extracts the stories alone.

Only fenced code blocks are read. A command named in running prose is
deliberately partial, such as one shown without its output file, and
checking those would report mistakes that are not there.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import argparse
import contextlib
import io
import re
import shlex
from importlib import import_module
from pathlib import Path
from typing import Iterator, NamedTuple, Optional

import pytest

MANUAL_DIR = Path(__file__).resolve().parents[2] / 'doc' / 'using_backlogops'
"""The folder holding the hand-written manual chapters."""
_COMMAND = re.compile(r'python3? -m backlogops_cli\.(\w+)\b(.*)$')
"""Matches a manual command line, capturing its module and arguments."""
_LEAST_EXAMPLES = 40
"""Fewest examples the manual is expected to hold.

A broken extractor would otherwise report no examples and pass, so the
count is asserted rather than trusted.
"""
_KEEPS_EVERY = frozenset({'_AppendAction', '_AppendConstAction',
                          '_ExtendAction', '_CountAction'})
"""Names of the argparse actions that a repeated option adds to.

Every other action stores, and so keeps only the last value it is given.
"""


class ManualCommand(NamedTuple):
    """One command line taken from a fenced block of the manual.

    Fields:
        where: The chapter file and line the command starts on.
        module: The ``backlogops_cli`` module the command runs.
        args: The command line arguments, as the shell would split them.
    """

    where: str
    module: str
    args: list[str]


def _as_command(where: str, line: str) -> Optional[ManualCommand]:
    """Return the command one manual line runs, or None for another line.

    The arguments are split as a shell would, so a quoted filter holding
    spaces stays one argument and a trailing comment is dropped.
    """
    match = _COMMAND.search(line)
    if match is None:
        return None
    return ManualCommand(where=where, module=match.group(1),
                         args=shlex.split(match.group(2), comments=True))


def _fenced_commands(path: Path) -> Iterator[ManualCommand]:
    """Yield the backlogops_cli commands in one manual chapter.

    A line ending in a backslash continues on the next one, so a wrapped
    example is checked as the single command it is meant to be.
    """
    inside = False
    buffer = ''
    start = 0
    lines = path.read_text(encoding='utf-8').splitlines()
    for number, raw in enumerate(lines, start=1):
        if raw.startswith('```'):
            inside = not inside
            continue
        if not inside:
            continue
        if not buffer:
            start = number
        buffer = f'{buffer} {raw.strip()}' if buffer else raw.strip()
        if buffer.endswith('\\'):
            buffer = buffer[:-1].rstrip()
            continue
        command = _as_command(f'{path.name}:{start}', buffer)
        buffer = ''
        if command is not None:
            yield command


def _manual_commands() -> list[ManualCommand]:
    """Return every command example of every manual chapter, in order."""
    return [command for path in sorted(MANUAL_DIR.glob('*.md'))
            for command in _fenced_commands(path)]


def _parser_for(module: str) -> Optional[argparse.ArgumentParser]:
    """Return the parser one CLI command builds, or None when it has none.

    A module that is not there raises, which is what reports a manual
    example naming a command that no longer exists.
    """
    command_module = import_module(f'backlogops_cli.{module}')
    if not hasattr(command_module, 'build_parser'):
        return None
    parser = command_module.build_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    return parser


def _parse_error(parser: argparse.ArgumentParser,
                 args: list[str]) -> Optional[str]:
    """Return why the parser refuses the arguments, or None when it does not.

    argparse writes its complaint to stderr and then exits, so the stream
    is captured and the exit caught to turn a refusal into a message.
    """
    complaint = io.StringIO()
    try:
        with contextlib.redirect_stderr(complaint):
            parser.parse_args(args)
    except SystemExit:
        reported = complaint.getvalue().strip().splitlines()
        return reported[-1] if reported else 'rejected without a reason'
    return None


def _action_for(parser: argparse.ArgumentParser,
                option: str) -> Optional[argparse.Action]:
    """Return what the parser does with one option string, if it knows it."""
    # pylint: disable-next=protected-access
    for action in parser._actions:
        if option in action.option_strings:
            return action
    return None


def _keeps_every_value(action: argparse.Action) -> bool:
    """Return whether repeating this option keeps the earlier values.

    The value a repeated option ends up with is no answer on its own,
    because an option taking several values at once already holds a list
    after a single use: ``-l Epic Story`` and ``-l Epic -l Story`` both
    leave a list, and only the second one threw a value away. What
    separates them is the action, so that is what is asked.
    """
    return type(action).__name__ in _KEEPS_EVERY


def _lost_options(parser: argparse.ArgumentParser,
                  args: list[str]) -> list[str]:
    """Return the repeated options whose earlier values are thrown away.

    An appending or counting option means something by being repeated,
    while a storing one keeps only the last value it is given. Repeating
    the latter therefore runs without complaint and silently does less
    than the example says, which is worse than being refused outright.
    """
    repeated = {arg for arg in args
                if arg.startswith('-') and args.count(arg) > 1}
    lost = []
    for option in sorted(repeated):
        action = _action_for(parser, option)
        if action is not None and not _keeps_every_value(action):
            lost.append(option)
    return lost


COMMANDS = _manual_commands()
"""Every command example found in the manual, checked one test each."""
IDS = [f'{command.where}-{command.module}' for command in COMMANDS]
"""Test ids naming the chapter, line and command of each example."""


def test_examples_found() -> None:
    """Test the manual examples are found, so no test passes vacuously."""
    assert len(COMMANDS) >= _LEAST_EXAMPLES


@pytest.mark.parametrize('command', COMMANDS, ids=IDS)
def test_example_parses(command: ManualCommand) -> None:
    """Test each manual example is accepted by its own command parser."""
    parser = _parser_for(command.module)
    if parser is None:
        pytest.skip(f'{command.module} builds no parser')
    problem = _parse_error(parser, command.args)
    assert problem is None, f'{command.where}: {problem}'


@pytest.mark.parametrize('command', COMMANDS, ids=IDS)
def test_example_keeps_values(command: ManualCommand) -> None:
    """Test no manual example repeats an option that keeps the last value."""
    parser = _parser_for(command.module)
    if parser is None:
        pytest.skip(f'{command.module} builds no parser')
    if _parse_error(parser, command.args) is not None:
        pytest.skip('the example does not parse, which is reported already')
    lost = _lost_options(parser, command.args)
    assert not lost, (f'{command.where}: {lost} given more than once, '
                      'so only the last value is used')
