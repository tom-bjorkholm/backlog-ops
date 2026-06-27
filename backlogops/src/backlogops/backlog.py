#! /usr/local/bin/python3
"""Internal representation of a backlog."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from datetime import date
from dataclasses import dataclass, field, fields
from enum import IntEnum, auto
from typing import Optional, TextIO
from backlogops.levels import Levels, DEFAULT_LEVELS, level_number_from_name
from backlogops.backlog_helpers import build_item_kwargs, check_key_syntax
from backlogops.backlog_helpers import construct, field_type_hints, find_cycle
from backlogops.backlog_helpers import report_bad_value, check_field_types
from backlogops.backlog_helpers import report_unknown_reference

DEPENDENCY_FIELDS = ('depends_on_f2s', 'depends_on_f2f', 'depends_on_s2s')
"""Names of the fields that hold dependency keys of a backlog item."""


class Status(IntEnum):
    """Status of a backlog item.

    The meaning of each status is:
    - TODO: The backlog item is not started yet. It will be done
            sometimes in the future. The complete story points on
            the item consumes FTE time.
    - IN_PROGRESS: The backlog item is in progress. We do not know
            how much of it is done, so the complete story points on
            the item consumes FTE time.
    - DONE: The backlog item is finished. No work left to do.
            The story points on the item will not consume any more
            FTE time.
    - REJECTED: The backlog item is rejected. The work will not be done.
            This is only present in the backlog to record the explicit
            decision not to do the work.
            The story points on the item will not consume any more
            FTE time.
    """

    TODO = auto()
    IN_PROGRESS = auto()
    DONE = auto()
    REJECTED = auto()


@dataclass
class BacklogItem:  # pylint: disable=too-many-instance-attributes
    """Internal representation of a backlog item.

    The backlog item has a number of defined fields that are used
    by the backlog operations. In addition, it has a number of extra
    fields that store useful information (like descriptions) that are
    not used by the backlog operations.

    Fields:
        key: The key of the backlog item. Required. Must be unique.
             Must not be empty, must not contain whitespace and must
             not contain any of the characters , . ; : ( ) [ ] { }.
        level: The level of the backlog item. Required. Must be an integer.
        title: The title of the backlog item. Required.
        story_points: The story points of the backlog item.
        status: The status of the backlog item.
        parent_key: The key of the parent backlog item. Optional.
                    Must exist as a key in the backlog.
                    Parent keys are used to build the hierarchy of the backlog.
                    The parent key must be at a higher level than the current
                    item. Parent keys introduce implicit dependencies between
                    items: the current item cannot start before the parent
                    item starts, and the parent item cannot finish before
                    all its children have finished.
        release: The release of the backlog item. Optional.
                 Follows the same character rules as the key.
                 Must not be empty string.
        team: The team responsible for the backlog item. Optional.
              Must not be empty string. Must be a valid team name.
              If None the item can be done by any team. If not None.
              the item can only be done by the specified team.
        depends_on_f2s: The list of keys of the backlog items that must
                        have been finished before the current item can
                        start. May be empty.
        depends_on_f2f: The list of keys of the backlog items that must
                        have been finished before the current item can
                        finish. May be empty.
        depends_on_s2s: The list of keys of the backlog items that must
                        have been started before the current item can
                        start. May be empty.
        planned_ready_date: The planned ready date of the backlog item.
                            The date that is communicated to the
                            customer. Optional.
        estimated_ready_date: The estimated ready date of the backlog
                              item. Optional.
        extra_fields: Additional input fields not used by the backlog
                      operations, stored by name.
    """

    key: str
    level: int
    title: str
    story_points: int
    status: Status
    parent_key: Optional[str] = None
    release: Optional[str] = None
    team: Optional[str] = None
    depends_on_f2s: list[str] = field(default_factory=list)
    depends_on_f2f: list[str] = field(default_factory=list)
    depends_on_s2s: list[str] = field(default_factory=list)
    planned_ready_date: Optional[date] = None
    estimated_ready_date: Optional[date] = None
    extra_fields: dict[str, object] = field(default_factory=dict)

    def __getitem__(self, field_name: str) -> object:
        """Return a mandatory or extra field by name."""
        # pylint: disable-next=no-member
        if field_name in self.__dataclass_fields__:
            return getattr(self, field_name)
        return self.extra_fields[field_name]

    def __setitem__(self, field_name: str, value: object) -> None:
        """Set a mandatory or extra field by name."""
        # pylint: disable-next=no-member
        if field_name in self.__dataclass_fields__:
            setattr(self, field_name, value)
        else:
            self.extra_fields[field_name] = value

    def __contains__(self, field_name: str) -> bool:
        """Check if a mandatory or extra field exists by name."""
        # pylint: disable-next=no-member
        return field_name in self.__dataclass_fields__ or \
            field_name in self.extra_fields

    def to_dict(self) -> dict[str, object]:
        """Return a dictionary representation of the backlog item."""
        result = {}
        # pylint: disable-next=no-member
        for field_name in self.__dataclass_fields__:
            result[field_name] = getattr(self, field_name)
        for field_name, value in self.extra_fields.items():
            result[field_name] = value
        return result

    def _check_field_types(self, stderr_file: TextIO) -> None:
        """Check that every field holds a value of its declared type."""
        check_field_types(self, stderr_file)

    def _check_key_constraints(self, stderr_file: TextIO) -> None:
        """Check the key, release and dependency keys for valid syntax."""
        check_key_syntax('key', self.key, stderr_file)
        if self.release is not None:
            check_key_syntax('release', self.release, stderr_file)
        for dep_field in DEPENDENCY_FIELDS:
            for index, dep_key in enumerate(getattr(self, dep_field)):
                check_key_syntax(f'{dep_field}[{index}]', dep_key, stderr_file)

    def _check_no_field_shadow(self, stderr_file: TextIO) -> None:
        """Check that no extra field shadows a named field."""
        # pylint: disable-next=no-member
        named = set(self.__dataclass_fields__)
        for extra_key in self.extra_fields:
            if extra_key in named:
                report_bad_value('extra_fields', extra_key,
                                 'shadows a named backlog item field',
                                 stderr_file)

    def check_consistency(self, stderr_file: TextIO = sys.stderr) -> None:
        """Check the internal consistency of the backlog item.

        The documented constraints are checked on all member variables.
        Field types are verified, the key, release and dependency keys
        are checked for valid syntax, and the extra fields are checked
        not to shadow a named field. References between items are not
        checked here; that is done by :func:`check_backlog_consistency`.

        Args:
            stderr_file: The file to report errors to.

        Raises:
            TypeError: If a field has the wrong type.
            ValueError: If a field value violates a constraint, or if an
                extra field shadows a named field.
        """
        self._check_field_types(stderr_file)
        self._check_key_constraints(stderr_file)
        self._check_no_field_shadow(stderr_file)


type Backlog = list[BacklogItem]
"""Internal representation of a backlog."""


def prepare_item_data(data: dict[str, object], levels: Levels,
                      stderr_file: TextIO = sys.stderr) -> dict[str, object]:
    """Return item data with a string level resolved to its number.

    A ``level`` given as a string is matched against the level names and
    aliases in ``levels`` and replaced by the level number. Integer
    levels and absent levels are returned unchanged, so that type and
    missing-field checks happen as usual when the data is converted.

    Args:
        data: The raw input data for one backlog item.
        levels: The levels used to resolve a string level.
        stderr_file: The file to report errors to.

    Returns:
        The input data, with a string level replaced by its number.

    Raises:
        ValueError: If a string level matches no level name or alias.
    """
    level_value = data.get('level')
    if not isinstance(level_value, str):
        return data
    number = level_number_from_name(level_value, levels, stderr_file)
    return {**data, 'level': number}


def _resolve_status(data: dict[str, object],
                    status_map: Optional[dict[str, Status]]
                    ) -> dict[str, object]:
    """Return item data with a mapped status name replaced by its Status.

    A string status is matched case-insensitively against ``status_map``;
    a match replaces it with the mapped Status, so an explicit mapping
    takes precedence over the built-in status-name matching. A status not
    in the map, an empty map, or a non-string status is left unchanged for
    the normal conversion to handle.

    Args:
        data: The raw input data for one backlog item.
        status_map: The extra status names mapped to Status members, or
                    None when no extra names are configured.

    Returns:
        The input data, with a mapped string status replaced by its Status.
    """
    if not status_map:
        return data
    value = data.get('status')
    if not isinstance(value, str):
        return data
    lookup = {name.lower(): status for name, status in status_map.items()}
    mapped = lookup.get(value.lower())
    if mapped is None:
        return data
    return {**data, 'status': mapped}


def get_backlog_item(data: dict[str, object], levels: Optional[Levels] = None,
                     status_map: Optional[dict[str, Status]] = None,
                     stderr_file: TextIO = sys.stderr) -> BacklogItem:
    """Get a backlog item from a dictionary.

    The dictionary is expected to hold the mandatory fields of the
    BacklogItem dataclass and any number of extra fields. Field values
    are converted to their declared types (for example ISO date strings
    to ``date`` and status names to ``Status``) and checked. A ``level``
    given as a string is resolved to its level number using ``levels``.
    When ``levels`` is None the default levels are used. A string status
    is first matched case-insensitively against ``status_map`` (an
    explicit match takes precedence); an unmapped status falls back to the
    built-in status-name matching. Errors are reported to the given file
    object.

    Args:
        data: The dictionary to get the backlog item from.
        levels: The levels used to resolve a string level, or None to
                use :data:`DEFAULT_LEVELS`.
        status_map: Extra status names mapped to Status members, matched
                    case-insensitively, or None for no extra names.
        stderr_file: The file to report errors to.

    Raises:
        KeyError: If a mandatory field is missing.
        TypeError: If a field has a type that cannot be converted.
        ValueError: If a string level matches no level name or alias.

    Returns:
        The backlog item.
    """
    chosen_levels = DEFAULT_LEVELS if levels is None else levels
    field_types = field_type_hints(BacklogItem)
    prepared = prepare_item_data(data, chosen_levels, stderr_file)
    prepared = _resolve_status(prepared, status_map)
    item_kwargs = build_item_kwargs(fields(BacklogItem), field_types, prepared,
                                    stderr_file)
    return construct(BacklogItem, item_kwargs)


def get_backlog(datalist: list[dict[str, object]],
                levels: Optional[Levels] = None,
                status_map: Optional[dict[str, Status]] = None,
                stderr_file: TextIO = sys.stderr) -> Backlog:
    """Get a backlog from a list of dictionaries.

    Each dictionary is converted to a backlog item as documented for
    :func:`get_backlog_item`.

    Args:
        datalist: The list of dictionaries to get the backlog from.
        levels: The levels used to convert level names to level numbers,
                or None to use :data:`DEFAULT_LEVELS`.
        status_map: Extra status names mapped to Status members, matched
                    case-insensitively, or None for no extra names.
        stderr_file: The file to report errors to.

    Raises:
        KeyError: If a mandatory field is missing.
        TypeError: If a field has a type that cannot be converted.
        ValueError: If a string level matches no level name or alias.

    Returns:
        The backlog.
    """
    return [get_backlog_item(data, levels, status_map, stderr_file)
            for data in datalist]


def check_unique_keys(backlog: Backlog,
                      stderr_file: TextIO = sys.stderr) -> set[str]:
    """Check that all backlog item keys are unique.

    Args:
        backlog: The backlog to check.
        stderr_file: The file to report errors to.

    Returns:
        The set of all keys, for reuse by later checks.

    Raises:
        ValueError: If two items share the same key.
    """
    keys: set[str] = set()
    for item in backlog:
        if item.key in keys:
            report_bad_value('key', item.key, 'duplicate backlog item key',
                             stderr_file)
        keys.add(item.key)
    return keys


def check_key_references(backlog: Backlog, known_keys: set[str],
                         stderr_file: TextIO = sys.stderr) -> None:
    """Check that parent and dependency keys reference existing items.

    Args:
        backlog: The backlog to check.
        known_keys: The set of keys that exist in the backlog.
        stderr_file: The file to report errors to.

    Raises:
        KeyError: If a parent_key or dependency key is unknown.
    """
    for item in backlog:
        if item.parent_key is not None and \
                item.parent_key not in known_keys:
            report_unknown_reference('parent_key', item.key, item.parent_key,
                                     stderr_file)
        for dep_field in DEPENDENCY_FIELDS:
            for dep_key in getattr(item, dep_field):
                if dep_key not in known_keys:
                    report_unknown_reference(dep_field, item.key, dep_key,
                                             stderr_file)


def event_start(key: str) -> str:
    """Return the start-event node name for a backlog item key."""
    return f'{key}:start'


def event_finish(key: str) -> str:
    """Return the finish-event node name for a backlog item key."""
    return f'{key}:finish'


def item_dependency_edges(item: BacklogItem) -> list[tuple[str, str]]:
    """Return the directed scheduling edges implied by one item.

    Each item has a start event and a finish event. An edge ``a -> b``
    means that event ``a`` cannot happen before event ``b`` (``a``
    depends on ``b``). An item finish depends on its own start. The
    dependency lists add finish-to-start, finish-to-finish and
    start-to-start edges. A parent relation adds two implicit edges: the
    child cannot start before the parent starts, and the parent cannot
    finish before the child finishes.

    Args:
        item: The backlog item to take the edges from.

    Returns:
        The directed (source, target) event edges of the item.
    """
    start = event_start(item.key)
    finish = event_finish(item.key)
    edges = [(finish, start)]
    edges += [(start, event_finish(dep)) for dep in item.depends_on_f2s]
    edges += [(finish, event_finish(dep)) for dep in item.depends_on_f2f]
    edges += [(start, event_start(dep)) for dep in item.depends_on_s2s]
    if item.parent_key is not None:
        edges.append((start, event_start(item.parent_key)))
        edges.append((event_finish(item.parent_key), finish))
    return edges


def build_dependency_graph(backlog: Backlog) -> dict[str, list[str]]:
    """Return the scheduling-event dependency graph of a backlog.

    The nodes are the start and finish events of the items, named
    ``'<key>:start'`` and ``'<key>:finish'`` (``:`` cannot appear in a
    key). The edges combine the explicit dependency lists with the
    implicit parent relations, as described in
    :func:`item_dependency_edges`. A cycle in this graph is an
    unsatisfiable set of scheduling constraints.

    Args:
        backlog: The backlog to build the graph from.

    Returns:
        A mapping from each event node to the events it depends on.
    """
    graph: dict[str, list[str]] = {}
    for item in backlog:
        for source, target in item_dependency_edges(item):
            graph.setdefault(source, []).append(target)
    return graph


def check_no_cycles(backlog: Backlog,
                    stderr_file: TextIO = sys.stderr) -> None:
    """Check that the scheduling-event graph of a backlog has no cycles.

    The graph combines the explicit dependencies with the implicit
    parent relations. A self dependency is treated as a cycle of length
    one. A valid parent and child nesting is not a cycle, because the
    parent and child start and finish events stay distinct.

    Args:
        backlog: The backlog to check.
        stderr_file: The file to report errors to.

    Raises:
        ValueError: If a dependency cycle is found.
    """
    cycle = find_cycle(build_dependency_graph(backlog))
    if cycle is not None:
        message = 'Dependency cycle in backlog: ' + ' -> '.join(cycle)
        print(message, file=stderr_file)
        raise ValueError(message)


def check_parent_levels(backlog: Backlog, items_by_key: dict[str, BacklogItem],
                        stderr_file: TextIO = sys.stderr) -> None:
    """Check that each parent is at a higher level than its child.

    A parent is a bigger backlog item than its children, so its level
    number must be strictly higher than the item that references it. The
    parent references are assumed to exist, as already checked by
    :func:`check_key_references`.

    Args:
        backlog: The backlog to check.
        items_by_key: A mapping from each key to its backlog item.
        stderr_file: The file to report errors to.

    Raises:
        ValueError: If a parent is not at a higher level than its child.
    """
    for item in backlog:
        if item.parent_key is None:
            continue
        parent = items_by_key[item.parent_key]
        if parent.level <= item.level:
            report_bad_value('parent_key', item.parent_key,
                             f'parent level {parent.level} is not higher '
                             f'than item level {item.level}', stderr_file)


def check_backlog_consistency(backlog: Backlog,
                              stderr_file: TextIO = sys.stderr) -> None:
    """Check the consistency of a backlog.

    Every item is checked for internal consistency, all keys are checked
    for uniqueness, parent and dependency keys are checked to reference
    existing items, each parent is checked to be at a higher level than
    its child, and the scheduling-event graph is checked to be free of
    cycles.

    Args:
        backlog: The backlog to check.
        stderr_file: The file to report errors to.

    Raises:
        KeyError: If a key reference is invalid.
        TypeError: If a field has the wrong type.
        ValueError: If a field value violates a constraint, if keys are
            not unique, if a parent is not at a higher level than its
            child, or if there is a dependency cycle.
    """
    for item in backlog:
        item.check_consistency(stderr_file)
    known_keys = check_unique_keys(backlog, stderr_file)
    items_by_key = {item.key: item for item in backlog}
    check_key_references(backlog, known_keys, stderr_file)
    check_parent_levels(backlog, items_by_key, stderr_file)
    check_no_cycles(backlog, stderr_file)
