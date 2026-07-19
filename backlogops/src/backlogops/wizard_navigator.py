#! /usr/local/bin/python3
"""Re-runnable navigation for the interactive backlog-ops wizards.

The :class:`_Navigator` drives a wizard body: an ordinary function that asks
its questions through the navigator and reads its per-question defaults from
an optional starting configuration. Every question has a stable position in
the nesting of levels and counted items, so an answered value is remembered
by that position and offered again as the default when the question is
re-asked, whether the user went back to it or forward into it once more.

The field-reading and parsing helpers the navigator calls live in
:mod:`backlogops.wizard_helpers`; the one-screen form toolkit lives in
:mod:`backlogops.wizard_forms`. The small domain helper
:func:`_ask_level_display` is shared by the configuration and preset wizards.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass, field
from functools import partial
from typing import Callable, Optional, Sequence, TextIO, TypeVar
from tableio import FileAccess
from tableio_cfg_json import TioJsonConfig, WizardBack, WizardCancelLevel, \
    WizardUiBridge
from backlogops.backlog import Status
from backlogops.jira_io_config import JiraColumnMap, JiraIssueTypeMap
from backlogops.levels import Level, LevelDisplay, Levels
from backlogops.work_hours import ExceptionWorkHours, ScheduleWorkHours
from backlogops.wizard_forms import FormField, FormResult, run_form, _no_rule
from backlogops.wizard_helpers import _RenameKind, _read_exceptions, \
    _read_int, _read_issue_type_map, _read_jira_map, _read_levels, \
    _read_preset_name, _read_renames, _read_schedule, _read_status_map, \
    _read_tableio, _read_text

_T = TypeVar('_T')
_D = TypeVar('_D')


@dataclass
class _Walk:
    """The traversal position while one run of a wizard body proceeds.

    Attributes:
        visit: How many questions the current run has reached so far.
        prefix: The chosen child index at each entered level.
        counters: The next child index at each active level.
    """

    visit: int = 0
    prefix: list[int] = field(default_factory=list)
    counters: list[int] = field(default_factory=lambda: [0])


# pylint: disable-next=too-many-public-methods
class _Navigator:
    """Drive a re-runnable wizard body with back, cancel and pre-fill.

    Going back un-confirms the most recent question and replays the rest;
    cancelling a level un-confirms that level; both keep the remembered
    values so the re-asked questions start pre-filled. Answering a count
    forgets the remembered items beyond the new count, so lowering a count
    drops the surplus while raising it keeps what was already entered. When
    the body is run backward the body is first replayed against its default,
    so the wizard opens on the last question with the earlier ones filled.
    """

    def __init__(self, ui_bridge: WizardUiBridge) -> None:
        """Store the bridge and start with no remembered answers."""
        self._ui = ui_bridge
        self._seeds: dict[tuple[int, ...], object] = {}
        self._confirmed = 0
        self._pending_back = False
        self._filling = False
        self._walk = _Walk()

    def run(self, body: Callable[['_Navigator', Optional[_D]], _T],
            default: Optional[_D] = None, backward: bool = False) -> _T:
        """Run the body, restarting it to honour back and cancel requests.

        A back request un-confirms the most recent answer and replays the
        rest, re-asking the previous question pre-filled. A cancel request
        that reaches the outermost body has no outer level to return to, so
        the question is asked again. When ``backward`` is set and a
        ``default`` is given the body is first replayed against the default,
        so the wizard opens on its last question with the earlier ones
        pre-filled. An abort request propagates to the caller.
        """
        if backward and default is not None:
            self._fill(body, default)
            self._go_back()
        while True:
            self._reset_run()
            try:
                return body(self, default)
            except WizardBack:
                self._go_back()
            except WizardCancelLevel:
                self._ui.show('There is no outer level to return to.')

    def _fill(self, body: Callable[['_Navigator', Optional[_D]], object],
              default: _D) -> None:
        """Replay the body against the default to remember its answers."""
        self._filling = True
        self._reset_run()
        body(self, default)
        self._filling = False

    def _reset_run(self) -> None:
        """Reset the traversal state, keeping the remembered answers."""
        self._walk = _Walk()

    def _go_back(self) -> None:
        """Un-confirm the most recent question so it is asked again."""
        if self._confirmed > 0:
            self._confirmed -= 1
            self._pending_back = True

    def level(self, body_fn: Callable[[], _T]) -> _T:
        """Run a sub-level, restarting it when the user cancels the level.

        A cancel-level request un-confirms the answers collected inside
        this level and asks its first question again, pre-filled from what
        was entered. A cancel at the level's first question has nothing to
        un-confirm here, so it propagates to the enclosing level.
        """
        walk = self._walk
        child = walk.counters[-1]
        walk.counters[-1] += 1
        walk.prefix.append(child)
        walk.counters.append(0)
        start = walk.visit
        try:
            return self._run_level(body_fn, start)
        finally:
            walk.prefix.pop()
            walk.counters.pop()

    def _run_level(self, body_fn: Callable[[], _T], start: int) -> _T:
        """Run a level body, restarting it on a cancel-level request."""
        while True:
            self._walk.counters[-1] = 0
            self._walk.visit = start
            try:
                return body_fn()
            except WizardCancelLevel:
                if self._confirmed <= start:
                    raise
                self._confirmed = start
                self._pending_back = False

    def show(self, message: str) -> None:
        """Show a message, unless replaying or pre-filling from a default."""
        if not self._filling and self._walk.visit >= self._confirmed:
            self._ui.show(message)

    def error_file(self) -> TextIO:
        """Return the bridge's diagnostics stream."""
        return self._ui.error_file()

    def ask_text(self, question: str, *, default: Optional[str] = None,
                 allow_empty: bool = False, seed: Optional[str] = None) -> str:
        """Ask for text, pre-filled from a seed or the given default."""
        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, str) else default
            return _read_text(self._ui, question, pre, allow_empty)
        result = self._ask(ask, seed)
        assert isinstance(result, str)
        return result

    def ask_int(self, question: str, default: int, minimum: int,
                maximum: Optional[int] = None, *,
                seed: Optional[int] = None) -> int:
        """Ask for a whole number within the given bounds, pre-filled."""
        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, int) and not isinstance(sd, bool) \
                else default
            return _read_int(self._ui, question, pre, minimum, maximum)
        result = self._ask(ask, seed)
        assert isinstance(result, int)
        return result

    def ask_count(self, question: str, maximum: Optional[int] = None, *,
                  seed: Optional[int] = None) -> int:
        """Ask how many items to collect, forgetting any surplus items.

        The items follow the count as siblings in the current level, so a
        lowered count forgets the remembered items past it.
        """
        scope = tuple(self._walk.prefix)
        child = self._walk.counters[-1]
        count = self.ask_int(question, 0, 0, maximum, seed=seed)
        self._forget_beyond(scope, child + count)
        return count

    def counted(self, count: int, seeds: Sequence[_D],
                build: Callable[[Optional[_D]], _T]) -> list[_T]:
        """Collect ``count`` items in a dedicated level, forgetting surplus.

        The items live in their own nesting level, so the count that drives
        them may be asked anywhere, such as on a shared form. Item ``k`` is
        built by ``build`` from ``seeds[k]`` when it exists and from None
        otherwise, so raising a count reuses the earlier items as seeds
        while extra items start blank. A cancel-level within an item
        re-asks that item, and a lowered count forgets the items past it so
        a later raise does not resurrect them.
        """
        return self.level(lambda: self._collect(count, seeds, build))

    def _collect(self, count: int, seeds: Sequence[_D],
                 build: Callable[[Optional[_D]], _T]) -> list[_T]:
        """Forget the surplus items of this level, then collect ``count``."""
        self._forget_beyond(tuple(self._walk.prefix), count - 1)
        return [self.level(partial(self._build_item, seeds, build, k))
                for k in range(count)]

    @staticmethod
    def _build_item(seeds: Sequence[_D], build: Callable[[Optional[_D]], _T],
                    index: int) -> _T:
        """Build one counted item, seeded from ``seeds`` when it reaches it."""
        return build(seeds[index] if index < len(seeds) else None)

    def ask_choice(self, question: str, choices: Sequence[str],
                   default: Optional[str] = None, *,
                   seed: Optional[str] = None) -> str:
        """Ask the user to pick one of choices, pre-filled from a seed."""
        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, str) and sd in choices else default
            return self._ui.ask_choice(question, choices=choices, default=pre)
        result = self._ask(ask, seed)
        assert isinstance(result, str)
        return result

    def ask_form(self, question: str, fields: Sequence[FormField],
                 rule: Callable[[FormResult], tuple[Optional[str], set[str]]]
                 = _no_rule, *,
                 seed: Optional[FormResult] = None) -> FormResult:
        """Ask a whole form on one screen, pre-filled from a seed result."""
        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, FormResult) else None
            return run_form(self._ui, question, fields, rule, pre)
        result = self._ask(ask, seed)
        assert isinstance(result, FormResult)
        return result

    def ask_preset_name(self, question: str, used: set[str], *,
                        seed: Optional[str] = None) -> str:
        """Ask for an unused letters-and-digits name, pre-filled."""
        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, str) else None
            return _read_preset_name(self._ui, question, used, pre)
        result = self._ask(ask, seed)
        assert isinstance(result, str)
        return result

    def ask_tableio(self, file_access: FileAccess, *,
                    seed: Optional[TioJsonConfig] = None) -> TioJsonConfig:
        """Ask for one TableIO endpoint configuration as one step.

        When the step is reached by going back it re-opens the embedded
        endpoint wizard on its last question; a seed pre-fills its answers.
        """
        def ask(sd: object, backward: bool) -> object:
            pre = sd if isinstance(sd, TioJsonConfig) else None
            return _read_tableio(self._ui, file_access, pre, backward)
        result = self._ask(ask, seed)
        assert isinstance(result, TioJsonConfig)
        return result

    def ask_schedule(self, *, seed: Optional[ScheduleWorkHours] = None
                     ) -> ScheduleWorkHours:
        """Ask the weekly work-hours schedule as one table question."""
        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, dict) else None
            return _read_schedule(self._ui, pre)
        result = self._ask(ask, seed)
        assert isinstance(result, dict)
        return result

    def ask_exceptions(self, question: str, *,
                       seed: Optional[list[ExceptionWorkHours]] = None
                       ) -> list[ExceptionWorkHours]:
        """Ask the work-hour exception periods as one variable-row table."""
        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, list) else None
            return _read_exceptions(self._ui, question, pre)
        result = self._ask(ask, seed)
        assert isinstance(result, list)
        return result

    def ask_levels(self, *, seed: Optional[list[Level]] = None) -> list[Level]:
        """Ask the backlog item levels as one variable-row table."""
        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, list) else None
            return _read_levels(self._ui, pre)
        result = self._ask(ask, seed)
        assert isinstance(result, list)
        return result

    def ask_renames(self, fields: list[str], allow_extra: bool,
                    target_header: str, is_input: bool = False, *,
                    seed: Optional[dict[str, Optional[str]]] = None
                    ) -> dict[str, Optional[str]]:
        """Ask one column-rename map as one variable-row table.

        With ``is_input`` false the table stores an internal-to-external
        output map; with it true the table stores an external-to-internal
        input map. Either way the internal field names are pre-filled, and
        a seed map pre-fills the earlier renames.
        """
        kind = _RenameKind(fields, allow_extra, target_header, is_input)

        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, dict) else None
            return _read_renames(self._ui, kind, pre)
        result = self._ask(ask, seed)
        assert isinstance(result, dict)
        return result

    def ask_status_map(self, question: str,
                       default_map: Optional[dict[str, Status]] = None, *,
                       seed: Optional[dict[str, Status]] = None
                       ) -> dict[str, Status]:
        """Ask the input status-name map as one variable-row table."""
        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, dict) else None
            return _read_status_map(self._ui, question, default_map, pre)
        result = self._ask(ask, seed)
        assert isinstance(result, dict)
        return result

    def ask_jira_map(self, fields: list[str], default_map: JiraColumnMap, *,
                     seed: Optional[JiraColumnMap] = None) -> JiraColumnMap:
        """Ask one Jira column map as one variable-row table.

        Each internal field is shown pre-filled with the kind and path of
        the seed map or, when no seed is given, of the default map.
        """
        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, dict) else None
            return _read_jira_map(self._ui, fields, default_map, pre)
        result = self._ask(ask, seed)
        assert isinstance(result, dict)
        return result

    def ask_issue_type_map(self, levels: Levels, *,
                           seed: Optional[JiraIssueTypeMap] = None
                           ) -> JiraIssueTypeMap:
        """Ask the level-to-issue-type write map as one fixed-row table.

        Each level is shown with its number and name and an editable Jira
        issue type pre-filled from the seed map, or to the level name.
        """
        def ask(sd: object, _bw: bool) -> object:
            pre = sd if isinstance(sd, dict) else None
            return _read_issue_type_map(self._ui, levels, pre)
        result = self._ask(ask, seed)
        assert isinstance(result, dict)
        return result

    def _ask(self, ask_fn: Callable[[object, bool], object],
             seed: object = None) -> object:
        """Return the remembered answer when replaying, else ask live.

        A live question starts pre-filled from its remembered value, or
        from the seed when it has never been answered. The answer is
        remembered by the question's position, so going back to it or
        forward into it again offers it as the default.
        """
        path = self._next_path()
        position = self._walk.visit
        self._walk.visit += 1
        if position < self._confirmed:
            return self._seeds[path]
        if self._filling:
            self._seeds[path] = seed
            self._confirmed = position + 1
            return seed
        default = self._seeds.get(path, seed)
        answer = ask_fn(default, self._pending_back)
        self._seeds[path] = answer
        self._confirmed = position + 1
        self._pending_back = False
        return answer

    def _next_path(self) -> tuple[int, ...]:
        """Return the position of the next question in the current level."""
        walk = self._walk
        child = walk.counters[-1]
        walk.counters[-1] += 1
        return tuple(walk.prefix + [child])

    def _forget_beyond(self, scope: tuple[int, ...], limit: int) -> None:
        """Forget the remembered answers of items after ``limit`` in a level.

        A path is dropped when it lies within ``scope`` and its own index
        in that level is beyond ``limit``, so a lowered count drops the
        surplus items while a higher count keeps what was entered. The
        limit is the last index to keep, whether the count precedes the
        items as a sibling or drives a dedicated sub-level.
        """
        depth = len(scope)
        for path in list(self._seeds):
            if (len(path) > depth and path[:depth] == scope
                    and path[depth] > limit):
                del self._seeds[path]


def _ask_level_display(nav: _Navigator, question: str,
                       seed: Optional[LevelDisplay] = None) -> LevelDisplay:
    """Ask how to show levels, defaulting to both number and name."""
    choices = [display.name.lower() for display in LevelDisplay]
    pre = seed.name.lower() if isinstance(seed, LevelDisplay) else None
    answer = nav.ask_choice(question, choices,
                            default=LevelDisplay.BOTH.name.lower(), seed=pre)
    return LevelDisplay[answer.upper()]
