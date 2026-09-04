#! /usr/local/bin/python3
"""Tests that a diagnostic names the whole path down to the value.

``config_as_json`` reports a configuration value by the path from the top
level of the file down to it, such as
``available_teams.teams[0].members[0].fte_exceptions[0].end_date``, so
that a message about one of the many members that share a name says which
of them it is about. The library hands each configuration class that path
when it constructs one, and every class here passes it on. A class that
stopped doing so would still be constructed, would report a plain member
name, and would warn about itself.

Both halves are checked here. One value at a time is broken in a complete
configuration file, and the refusal has to name the whole path down to
it; then reading and writing that same file has to warn about nothing.
The cases are chosen one per way of nesting a configuration: a list of
plain JSON objects, a nested object in a member, in a dict value and in a
list element, and one built by a factory of this library.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import json
import warnings
from inspect import signature
from pathlib import Path
from typing import Iterator, Sequence
import pytest
from config_as_json import Config, JsonType
from config_as_json import _deprecated_support
from backlogops import BacklogOpsConfig, NoTextIO, read_backlog_ops_config
from .shared_test_data import write_full_config

REFUSALS = (TypeError, ValueError, KeyError)
"""Every way a configuration class of this library refuses a value."""

BROKEN_PATHS = [
    (('levels', 0, 'name'), 5, 'levels[0].name'),
    (('levels', 0, 'aliases', 0), 7, 'levels[0].aliases[0]'),
    (('available_teams', 'persons', 'ada', 'exceptions', 0, 'start_date'),
     'not-a-date',
     'available_teams.persons[ada].exceptions[0].start_date'),
    (('available_teams', 'teams', 0, 'members', 0, 'fte_exceptions', 0,
      'end_date'), 'not-a-date',
     'available_teams.teams[0].members[0].fte_exceptions[0].end_date'),
    (('available_teams', 'company_work_hours', 'work_hours', 'MONDAY'),
     'not-a-number', 'available_teams.company_work_hours.work_hours'),
    (('input_configs', 'excel', 'status_input_map', 'Klar'), 'NO_SUCH_STATUS',
     'input_configs[excel].status_input_map[Klar]'),
    (('gui_display', 'backlog_to_external', 'key'), 5,
     'gui_display.backlog_to_external'),
    (('jira', 'connections', 'cloud', 'base_url'), 5,
     'jira.connections[cloud].base_url'),
    (('input_configs', 'excel', 'tableio', 'format_name'), 'No Such Format',
     'input_configs[excel].tableio.format_name')]
"""One value to break, and the path the refusal about it has to name."""


def _reached(data: JsonType, steps: Sequence[int | str]) -> JsonType:
    """Return the part of a configuration that a path of steps reaches."""
    for step in steps:
        if isinstance(step, int):
            assert isinstance(data, list)
            data = data[step]
        else:
            assert isinstance(data, dict)
            data = data[step]
    return data


def _replace(data: JsonType, steps: Sequence[int | str],
             value: JsonType) -> None:
    """Put ``value`` where a path of dict keys and list indices reaches."""
    holder = _reached(data, steps[:-1])
    last = steps[-1]
    if isinstance(last, int):
        assert isinstance(holder, list)
        holder[last] = value
    else:
        assert isinstance(holder, dict)
        holder[last] = value


def _broken_file(tmp_path: Path, steps: Sequence[int | str],
                 value: JsonType) -> Path:
    """Write a complete configuration file with one value broken.

    Args:
        tmp_path: Folder the two configuration files are written in.
        steps: Dict keys and list indices reaching the value to break.
        value: What to put there instead of what belongs there.

    Returns:
        The file holding the configuration with that one broken value.
    """
    source = tmp_path / 'config.json'
    write_full_config(source)
    data: JsonType = json.loads(source.read_text(encoding='utf-8'))
    _replace(data, steps, value)
    broken = tmp_path / 'broken.json'
    broken.write_text(json.dumps(data), encoding='utf-8')
    return broken


def _deprecations(caught: Sequence[warnings.WarningMessage]) -> list[str]:
    """Return what ``config_as_json`` deprecated among caught warnings."""
    return [str(one.message) for one in caught
            if issubclass(one.category, DeprecationWarning)
            and 'config_as_json' in one.filename]


def _below(cls: type[Config]) -> Iterator[type[Config]]:
    """Yield every class derived from one class, however deep."""
    for derived in cls.__subclasses__():
        yield derived
        yield from _below(derived)


def _own_classes() -> list[type[Config]]:
    """Return every configuration class this library declares itself."""
    return [cls for cls in _below(Config)
            if cls.__module__.startswith('backlogops')]


@pytest.mark.parametrize('steps, value, path', BROKEN_PATHS)
def test_diagnostic_path(tmp_path: Path, steps: Sequence[int | str],
                         value: JsonType, path: str) -> None:
    """One broken value is refused by the whole path down to it."""
    broken = _broken_file(tmp_path, steps, value)
    with pytest.raises(REFUSALS) as refusal:
        read_backlog_ops_config(broken, NoTextIO())
    assert path in str(refusal.value)


def test_classes_take_path() -> None:
    """Every configuration class of this library accepts the path.

    A class that the library constructs as a nested configuration is
    given the path for reaching it, and one that does not accept
    ``member_name`` is constructed without it and loses the path from
    every diagnostic it raises. A class added later is covered without
    being listed here, because the classes are found by what they derive
    from rather than by name.
    """
    classes = _own_classes()
    assert BacklogOpsConfig in classes
    without = [cls.__qualname__ for cls in classes
               if 'member_name' not in signature(cls.__init__).parameters]
    assert without == []


def test_no_deprecation(tmp_path: Path) -> None:
    """Building, reading and writing a configuration warns about nothing.

    A configuration class or a nested-config factory that does not accept
    ``member_name`` is used without it and warns that it should be
    changed, so a warning here names the one that stopped passing the
    path on. The library warns once per callable per process, so what it
    has already warned about is forgotten first; without that an earlier
    test in the same session would have used up the one warning this test
    is looking for.
    """
    # pylint: disable-next=protected-access
    _deprecated_support._MEMBER_NAME_WARNED.clear()
    source = tmp_path / 'config.json'
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        write_full_config(source)
        config = read_backlog_ops_config(source, NoTextIO())
        config.write(to_json_filename=tmp_path / 'written.json',
                     stderr_file=NoTextIO())
    assert _deprecations(caught) == []
