#! /usr/local/bin/python3
"""Interactively build an AvailableTeams workforce configuration.

The public helpers :func:`available_teams_wizard` and
:func:`teams_config_wizard` ask the user for the company work hours, the
persons and their personal work-hour exceptions, the teams with their
members, and optional TableIO presets. They drive any ``WizardUiBridge``
of ``tableio_cfg_json``, so the same wizard logic runs on a console text
interface, a Textual full-screen interface or a graphical user interface.

Each repeated part is asked by first requesting a count and then
collecting exactly that many items, so there are no open-ended "add
another?" prompts. Each counted group is collected inside its own level
whose opening question is the count, so a cancel-level request from any
item returns to that count question and re-asks the group. The wizard is
driven through a small navigator that records every answer and replays
them when the body is re-run, which is how it honours the bridge's back,
cancel-level and abort requests: going back drops the most recently asked
question, even across levels.

Individual field values are validated as they are entered, and date
ranges are kept non-empty. Cross-item rules that span a whole workforce,
such as non-overlapping exception periods and per-person capacity, are
checked when the result is stored.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from typing import Callable, Optional, Sequence, TextIO, TypeVar
from tableio import FileAccess, access_capabilities
from tableio_cfg_json import TableCell, TableColumn, TioJsonConfig, \
    WizardAbort, WizardBack, WizardCancelLevel, WizardUiBridge, \
    tio_json_config_wizard
from backlogops.available_teams import AvailableTeams
from backlogops.backlog_ops_config import BacklogOpsConfig
from backlogops.io_config import InputFormatConfig, OutputFormatConfig, \
    PRESET_NAME_RE, make_input_config, make_output_config
from backlogops.levels import DEFAULT_LEVELS, Level, levels_from_list
from backlogops.person import Person
from backlogops.team import FteException, Membership, Team
from backlogops.work_hours import CompanyWorkHours, DEFAULT_WORK_WEEK, \
    ExceptionWorkHours, ScheduleWorkHours, WeekDay

_T = TypeVar('_T')


class _Navigator:
    """Drive a re-runnable wizard body with back, cancel and abort.

    The wizard body is an ordinary function that asks questions through
    this navigator. Every answered question is recorded, so the body can
    be replayed from the start to implement navigation: going back drops
    the most recently asked question and replays the rest, which re-asks
    the previous question even when it lives in an outer level.
    """

    def __init__(self, ui_bridge: WizardUiBridge) -> None:
        """Store the bridge and start with no recorded answers."""
        self._ui = ui_bridge
        self._answers: list[object] = []
        self._cursor = 0

    def run(self, body: Callable[['_Navigator'], _T]) -> _T:
        """Run the body, restarting it to honour back and cancel requests.

        A back request drops the most recent answer and replays the rest,
        re-asking the previous question. A cancel request that reaches the
        outermost body has no outer level to return to, so the question is
        asked again. An abort request propagates to the caller.
        """
        while True:
            self._cursor = 0
            try:
                return body(self)
            except WizardBack:
                if self._answers:
                    self._answers.pop()
            except WizardCancelLevel:
                self._ui.show('There is no outer level to return to.')

    def level(self, body_fn: Callable[[], _T]) -> _T:
        """Run a sub-level, restarting it when the user cancels the level.

        A cancel-level request discards the answers collected inside this
        level and asks its first question again. A cancel raised at the
        level's first question has no answer to discard here, so it
        propagates to the enclosing level.
        """
        start = self._cursor
        while True:
            try:
                return body_fn()
            except WizardCancelLevel:
                if self._cursor <= start:
                    raise
                del self._answers[start:]
                self._cursor = start

    def show(self, message: str) -> None:
        """Show a message, unless recorded answers are being replayed."""
        if not self._replaying():
            self._ui.show(message)

    def error_file(self) -> TextIO:
        """Return the bridge's diagnostics stream."""
        return self._ui.error_file()

    def ask_text(self, question: str, *, default: Optional[str] = None,
                 allow_empty: bool = False) -> str:
        """Ask for text with an optional default and re-ask on empty."""
        result = self._ask(lambda: _read_text(self._ui, question, default,
                                              allow_empty))
        assert isinstance(result, str)
        return result

    def ask_number(self, question: str, default: float,
                   minimum: Optional[float], maximum: Optional[float]
                   ) -> float:
        """Ask for a floating point value within optional bounds."""
        result = self._ask(lambda: _read_number(self._ui, question, default,
                                                minimum, maximum))
        assert isinstance(result, float)
        return result

    def ask_int(self, question: str, default: int, minimum: int,
                maximum: Optional[int] = None) -> int:
        """Ask for a whole number within the given bounds."""
        result = self._ask(lambda: _read_int(self._ui, question, default,
                                             minimum, maximum))
        assert isinstance(result, int)
        return result

    def ask_count(self, question: str, maximum: Optional[int] = None) -> int:
        """Ask how many items to collect, defaulting to none."""
        return self.ask_int(question, 0, 0, maximum)

    def ask_yes_no(self, question: str, default: bool) -> bool:
        """Ask a yes/no question through the bridge's dedicated control."""
        result = self._ask(lambda: self._ui.ask_yes_no(question, default))
        assert isinstance(result, bool)
        return result

    def ask_choice(self, question: str, choices: Sequence[str]) -> str:
        """Ask the user to pick one of choices through the bridge."""
        result = self._ask(lambda: self._ui.ask_choice(question,
                                                       choices=choices))
        assert isinstance(result, str)
        return result

    def ask_date(self, question: str) -> date:
        """Ask for a required ISO 8601 date such as ``2026-06-13``."""
        result = self._ask(lambda: _read_date(self._ui, question))
        assert isinstance(result, date)
        return result

    def ask_end_date(self, question: str, start_date: date) -> date:
        """Ask for an end date that is not before ``start_date``."""
        result = self._ask(lambda: _read_end_date(self._ui, question,
                                                  start_date))
        assert isinstance(result, date)
        return result

    def ask_opt_date(self, question: str) -> Optional[date]:
        """Ask for an optional ISO date; an empty answer returns ``None``."""
        result = self._ask(lambda: _read_opt_date(self._ui, question, None))
        assert result is None or isinstance(result, date)
        return result

    def ask_membership_end(self, question: str,
                           start_date: Optional[date]) -> Optional[date]:
        """Ask for an optional end date not before the start date."""
        result = self._ask(lambda: _read_opt_date(self._ui, question,
                                                  start_date))
        assert result is None or isinstance(result, date)
        return result

    def ask_person_name(self, question: str,
                        persons: dict[str, Person]) -> str:
        """Ask for a person name that is not already used."""
        result = self._ask(lambda: _read_unique_name(self._ui, question,
                                                     persons))
        assert isinstance(result, str)
        return result

    def ask_preset_name(self, question: str, used: set[str]) -> str:
        """Ask for a preset name of letters and digits that is unused."""
        result = self._ask(lambda: _read_preset_name(self._ui, question, used))
        assert isinstance(result, str)
        return result

    def ask_tableio(self, file_access: FileAccess) -> TioJsonConfig:
        """Ask for one TableIO endpoint configuration as one step."""
        result = self._ask(lambda: _read_tableio(self._ui, file_access))
        assert isinstance(result, TioJsonConfig)
        return result

    def ask_schedule(self) -> ScheduleWorkHours:
        """Ask the weekly work-hours schedule as one table question."""
        result = self._ask(lambda: _read_schedule(self._ui))
        assert isinstance(result, dict)
        return result

    def ask_levels(self) -> list[Level]:
        """Ask the backlog item levels as one variable-row table."""
        result = self._ask(lambda: _read_levels(self._ui))
        assert isinstance(result, list)
        return result

    def ask_column_map(self, from_label: str, to_label: str) -> dict[str, str]:
        """Ask for column-name mappings as a count and one table."""
        count = self.ask_count('Number of column-name mappings')
        if count == 0:
            return {}
        result = self._ask(lambda: _read_column_map(self._ui, count,
                                                    from_label, to_label))
        assert isinstance(result, dict)
        return result

    def _ask(self, ask_fn: Callable[[], object]) -> object:
        """Return the recorded answer when replaying, else ask live."""
        if self._cursor < len(self._answers):
            value = self._answers[self._cursor]
            self._cursor += 1
            return value
        value = ask_fn()
        self._answers.append(value)
        self._cursor += 1
        return value

    def _replaying(self) -> bool:
        """Return whether recorded answers are being replayed."""
        return self._cursor < len(self._answers)


def _parse_date(answer: str) -> Optional[date]:
    """Return the ISO date in ``answer``, or ``None`` when it is invalid."""
    try:
        return date.fromisoformat(answer)
    except ValueError:
        return None


def _read_text(ui: WizardUiBridge, question: str, default: Optional[str],
               allow_empty: bool) -> str:
    """Ask for a text value with an optional default and re-ask on empty."""
    prompt = question if default is None else f'{question} [{default}]'
    reason: Optional[str] = None
    while True:
        answer = ui.ask_text(prompt, reason, nullable=True)
        if answer is not None:
            return answer
        if default is not None:
            return default
        if allow_empty:
            return ''
        reason = 'Please enter a non-empty value.'


def _read_number(ui: WizardUiBridge, question: str, default: float,
                 minimum: Optional[float], maximum: Optional[float]) -> float:
    """Ask for a floating point value within optional bounds."""
    reason: Optional[str] = None
    while True:
        answer = ui.ask_text(f'{question} [{default}]', reason, nullable=True)
        if answer is None:
            return default
        try:
            value = float(answer)
        except ValueError:
            reason = 'Please enter a number.'
            continue
        if minimum is not None and value < minimum:
            reason = f'Please enter a value of at least {minimum}.'
        elif maximum is not None and value > maximum:
            reason = f'Please enter a value of at most {maximum}.'
        else:
            return value


def _read_int(ui: WizardUiBridge, question: str, default: int, minimum: int,
              maximum: Optional[int]) -> int:
    """Ask for a whole number within the given bounds.

    The bridge's typed ask_int re-asks invalid or out-of-range answers,
    and an empty answer keeps the default.
    """
    answer = ui.ask_int(f'{question} [{default}]', nullable=True,
                        min_value=minimum, max_value=maximum)
    return default if answer is None else answer


def _read_date(ui: WizardUiBridge, question: str) -> date:
    """Ask for a required ISO 8601 date such as ``2026-06-13``."""
    reason: Optional[str] = None
    while True:
        answer = ui.ask_text(f'{question} (YYYY-MM-DD)', reason, nullable=True)
        parsed = _parse_date(answer) if answer is not None else None
        if parsed is not None:
            return parsed
        reason = 'Please enter a date as YYYY-MM-DD.'


def _read_end_date(ui: WizardUiBridge, question: str, start_date: date
                   ) -> date:
    """Ask for an end date that is not before ``start_date``."""
    reason: Optional[str] = None
    while True:
        answer = ui.ask_text(f'{question} (YYYY-MM-DD)', reason, nullable=True)
        parsed = _parse_date(answer) if answer is not None else None
        if parsed is None:
            reason = 'Please enter a date as YYYY-MM-DD.'
        elif parsed < start_date:
            reason = 'The end date must not be before the start date.'
        else:
            return parsed


def _read_opt_date(ui: WizardUiBridge, question: str,
                   start_date: Optional[date]) -> Optional[date]:
    """Ask for an optional ISO date not before an optional start date."""
    reason: Optional[str] = None
    while True:
        answer = ui.ask_text(f'{question} (YYYY-MM-DD, blank for none)',
                             reason, nullable=True)
        if answer is None:
            return None
        parsed = _parse_date(answer)
        if parsed is None:
            reason = 'Please enter a date as YYYY-MM-DD, or leave blank.'
        elif start_date is not None and parsed < start_date:
            reason = 'The end date must not be before the start date.'
        else:
            return parsed


def _read_unique_name(ui: WizardUiBridge, question: str,
                      persons: dict[str, Person]) -> str:
    """Ask for a person name that is not already a key in ``persons``."""
    reason: Optional[str] = None
    while True:
        answer = ui.ask_text(question, reason, nullable=True)
        if answer is None:
            reason = 'Please enter a non-empty value.'
        elif answer.lower() in persons:
            reason = f'A person named {answer!r} already exists.'
        else:
            return answer


def _read_preset_name(ui: WizardUiBridge, question: str, used: set[str]
                      ) -> str:
    """Ask for a preset name of letters and digits that is unused."""
    reason: Optional[str] = None
    while True:
        answer = ui.ask_text(question, reason, nullable=True)
        if answer is None or PRESET_NAME_RE.match(answer) is None:
            reason = 'Use only letters and digits for a preset name.'
        elif answer in used:
            reason = f'A preset named {answer!r} already exists.'
        else:
            return answer


def _read_tableio(ui: WizardUiBridge, file_access: FileAccess
                  ) -> TioJsonConfig:
    """Ask for one TableIO endpoint configuration through the wizard."""
    capabilities = access_capabilities(file_access, error_file=ui.error_file())
    return tio_json_config_wizard(capabilities, file_access, ui)


def _num_text(value: float) -> str:
    """Return a compact decimal text for a default numeric value."""
    return f'{value:g}'


def _is_nonneg(text: Optional[str]) -> bool:
    """Return whether ``text`` parses as a number that is at least zero."""
    if text is None:
        return False
    try:
        return float(text) >= 0.0
    except ValueError:
        return False


def _sched_check(table: list[list[Optional[str]]],
                 position: tuple[int, int]) -> tuple[bool, str]:
    """Give early feedback that an edited work-hours cell is a number."""
    row, col = position
    if col != 1:
        return (True, '')
    ok = _is_nonneg(table[row][1])
    return (ok, '' if ok else 'Enter work hours as a number that is >= 0.')


def _map_check(table: list[list[Optional[str]]],
               position: tuple[int, int]) -> tuple[bool, str]:
    """Give early feedback that an edited mapping cell is not empty."""
    row, col = position
    ok = bool(table[row][col])
    return (ok, '' if ok else 'Enter a non-empty name.')


def _parse_schedule(days: Sequence[WeekDay],
                    table: Sequence[Sequence[Optional[str]]]
                    ) -> Optional[ScheduleWorkHours]:
    """Return the weekly schedule from a table, or None when invalid."""
    schedule: ScheduleWorkHours = {}
    for day, row in zip(days, table):
        hours = row[1]
        if not _is_nonneg(hours):
            return None
        assert hours is not None
        schedule[day] = float(hours)
    return schedule


def _parse_column_map(table: Sequence[Sequence[Optional[str]]]
                      ) -> Optional[dict[str, str]]:
    """Return the column-name mapping from a table, or None when invalid."""
    mapping: dict[str, str] = {}
    for row in table:
        source, target = row[0], row[1]
        if not source or not target:
            return None
        mapping[source] = target
    return mapping


def _read_schedule(ui: WizardUiBridge) -> ScheduleWorkHours:
    """Ask the weekly work-hours schedule as one table question."""
    days = list(WeekDay)
    columns = [TableColumn(header='Day', read_only=True),
               TableColumn(header='Work hours')]
    cells = [[TableCell(value=day.name.capitalize()),
              TableCell(value=_num_text(DEFAULT_WORK_WEEK[day]))]
             for day in days]
    reason: Optional[str] = None
    while True:
        table = ui.ask_table(columns, cells,
                             'Company work hours per week day:',
                             re_ask_reason=reason, partial_check=_sched_check)
        schedule = _parse_schedule(days, table)
        if schedule is not None:
            return schedule
        reason = 'Enter work hours as a number that is at least zero.'


def _read_column_map(ui: WizardUiBridge, count: int, from_label: str,
                     to_label: str) -> dict[str, str]:
    """Ask the given number of column-name mappings as one table."""
    columns = [TableColumn(header=f'{from_label} name'),
               TableColumn(header=f'{to_label} name')]
    cells = [[TableCell(), TableCell()] for _ in range(count)]
    reason: Optional[str] = None
    while True:
        table = ui.ask_table(columns, cells, 'Column-name mappings:',
                             re_ask_reason=reason, partial_check=_map_check)
        mapping = _parse_column_map(table)
        if mapping is not None:
            return mapping
        reason = 'Enter a non-empty name in every cell.'


_MAX_LEVELS = 99
"""Upper bound on the number of backlog item levels the wizard accepts."""


def _parse_level_int(text: Optional[str]) -> Optional[int]:
    """Return ``text`` as an int (sign allowed), or None when invalid."""
    if text is None:
        return None
    try:
        return int(text.strip())
    except ValueError:
        return None


def _split_aliases(text: Optional[str]) -> list[str]:
    """Return the trimmed, non-empty comma separated aliases in ``text``."""
    if text is None:
        return []
    return [alias.strip() for alias in text.split(',') if alias.strip()]


def _levels_check(table: list[list[Optional[str]]],
                  position: tuple[int, int]) -> tuple[bool, str]:
    """Give early feedback that a level number or name cell is valid."""
    row, col = position
    if col == 0:
        ok = _parse_level_int(table[row][0]) is not None
        return (ok, '' if ok else 'Enter the level as a whole number.')
    if col == 1:
        ok = bool(table[row][1])
        return (ok, '' if ok else 'Enter a non-empty level name.')
    return (True, '')


def _parse_levels(table: list[list[Optional[str]]]) -> Optional[list[Level]]:
    """Return the levels from a table, or None when a cell is invalid."""
    levels: list[Level] = []
    for row in table:
        number = _parse_level_int(row[0])
        name = row[1]
        if number is None or not name:
            return None
        levels.append(Level(level=number, name=name,
                            aliases=_split_aliases(row[2])))
    return levels


def _default_level_cells() -> list[list[TableCell]]:
    """Return the table rows pre-filled with the default levels."""
    return [[TableCell(value=str(level.level)),
             TableCell(value=level.name),
             TableCell(value=', '.join(level.aliases))]
            for level in DEFAULT_LEVELS.values()]


def _levels_problem(levels: list[Level], error_file: TextIO) -> Optional[str]:
    """Return a re-ask reason when the levels are inconsistent, else None.

    The whole-table rule reuses :func:`levels_from_list`, which rejects a
    repeated level number and any duplicate or malformed name or alias.
    """
    try:
        levels_from_list(levels, error_file)
    except (TypeError, ValueError, KeyError) as problem:
        return str(problem.args[0]) if problem.args else str(problem)
    return None


def _cells_from_table(table: list[list[Optional[str]]]
                      ) -> list[list[TableCell]]:
    """Return the user's table rows as seed cells for a re-ask."""
    return [[TableCell(value=('' if cell is None else cell)) for cell in row]
            for row in table]


def _read_levels(ui: WizardUiBridge) -> list[Level]:
    """Ask the backlog item levels as one variable-row table question.

    Each cell is checked as it is entered, and the whole table is then
    checked for consistency. An inconsistent table is re-asked with the
    user's own rows kept, so the reported duplicate can be corrected.
    """
    columns = [TableColumn(header='Level'), TableColumn(header='Name'),
               TableColumn(header='Aliases (comma separated)')]
    cells = _default_level_cells()
    reason: Optional[str] = None
    while True:
        table = ui.ask_table(columns, cells, 'Backlog item levels:',
                             re_ask_reason=reason, partial_check=_levels_check,
                             min_rows=1, max_rows=_MAX_LEVELS)
        levels = _parse_levels(table)
        if levels is not None:
            reason = _levels_problem(levels, ui.error_file())
            if reason is None:
                return levels
        else:
            reason = ('Enter a whole-number level and a non-empty name in '
                      'every row.')
        cells = _cells_from_table(table)


def available_teams_wizard(ui_bridge: WizardUiBridge) -> AvailableTeams:
    """Interactively create an available workforce configuration.

    Args:
        ui_bridge: Bridge between the wizard and the user interface.

    Returns:
        The workforce entered by the user. Field values are individually
        valid, but whole-workforce consistency is only enforced when the
        result is stored.

    Raises:
        EOFError: The input ended, or the user abandoned the wizard.
    """
    navigator = _Navigator(ui_bridge)
    try:
        return navigator.run(_collect_teams)
    except WizardAbort as abort:
        raise EOFError('Configuration abandoned by the user.') from abort


def teams_config_wizard(ui_bridge: WizardUiBridge) -> BacklogOpsConfig:
    """Interactively create a backlog-ops configuration.

    The workforce is entered as by :func:`available_teams_wizard`, the
    user may then add any number of named input and output TableIO
    configuration presets, and finally edit the backlog item levels. The
    levels start filled in with the default levels; when the user leaves
    them at the defaults they are stored as "use the defaults" rather
    than written out.

    Args:
        ui_bridge: Bridge between the wizard and the user interface.

    Returns:
        The backlog-ops configuration, ready to be written to a file.

    Raises:
        EOFError: The input ended, or the user abandoned the wizard.
    """
    navigator = _Navigator(ui_bridge)
    try:
        return navigator.run(_collect_config)
    except WizardAbort as abort:
        raise EOFError('Configuration abandoned by the user.') from abort


def _collect_teams(nav: _Navigator) -> AvailableTeams:
    """Ask for the company, the persons and the teams of a workforce."""
    nav.show('Configure the available workforce.')
    company = _build_company(nav)
    persons = nav.level(lambda: _build_persons(nav))
    names = [person.name for person in persons.values()]
    teams = nav.level(lambda: _build_teams(nav, names))
    return AvailableTeams(persons=persons, teams=teams,
                          company_work_hours=company)


def _collect_config(nav: _Navigator) -> BacklogOpsConfig:
    """Ask for the workforce, the named TableIO presets and the levels."""
    teams = _collect_teams(nav)
    config = BacklogOpsConfig(available_teams=teams)
    config.input_configs = nav.level(lambda: _build_input_presets(nav))
    config.output_configs = nav.level(lambda: _build_output_presets(nav))
    config.levels = _levels_or_none(nav.ask_levels())
    return config


def _levels_or_none(levels: list[Level]) -> Optional[list[Level]]:
    """Return the levels, or None when they match the default levels."""
    if {level.level: level for level in levels} == DEFAULT_LEVELS:
        return None
    return levels


def _build_company(nav: _Navigator) -> CompanyWorkHours:
    """Ask for the company weekly schedule and exception periods."""
    work_hours = nav.ask_schedule()
    question = 'Number of company holiday, closure or special-work periods'
    exceptions = nav.level(lambda: _build_exceptions(nav, question))
    return CompanyWorkHours(work_hours=work_hours, exceptions=exceptions)


def _build_exceptions(nav: _Navigator,
                      count_question: str) -> list[ExceptionWorkHours]:
    """Ask for a counted list of work-hour exception periods."""
    count = nav.ask_count(count_question)
    return [nav.level(lambda: _ask_exception(nav)) for _ in range(count)]


def _ask_exception(nav: _Navigator) -> ExceptionWorkHours:
    """Ask for one work-hour exception period."""
    start_date = nav.ask_date('Start date')
    end_date = nav.ask_end_date('End date', start_date)
    hours = nav.ask_number('Work hours per day during the period', 0.0, 0.0,
                           None)
    new_work_days = nav.ask_yes_no(
        'Does this add work on days that are normally free?', False)
    return ExceptionWorkHours(start_date=start_date, end_date=end_date,
                              hours_per_day=hours, new_work_days=new_work_days)


def _build_persons(nav: _Navigator) -> dict[str, Person]:
    """Ask for a counted list of persons and their exceptions."""
    count = nav.ask_count('Number of persons')
    persons: dict[str, Person] = {}
    for _ in range(count):
        person = nav.level(lambda: _ask_person(nav, persons))
        persons[person.name.lower()] = person
    return persons


def _ask_person(nav: _Navigator, persons: dict[str, Person]) -> Person:
    """Ask for one person and the personal work-hour exceptions."""
    name = nav.ask_person_name('Person name', persons)
    question = f'Number of vacation or work-hour exceptions for {name}'
    exceptions = nav.level(lambda: _build_exceptions(nav, question))
    return Person(name=name, exceptions=exceptions)


def _build_teams(nav: _Navigator, person_names: list[str]) -> list[Team]:
    """Ask for a counted list of teams and their memberships."""
    count = nav.ask_count('Number of teams')
    return [nav.level(lambda: _ask_team(nav, person_names))
            for _ in range(count)]


def _ask_team(nav: _Navigator, person_names: list[str]) -> Team:
    """Ask for one team and its memberships.

    The team members are asked first, then the velocity and the matching
    full-time-equivalent sum together. The sum defaults to the number of
    members, the common case where every member works full time.
    """
    name = nav.ask_text('Team name')
    members = nav.level(lambda: _build_members(nav, person_names))
    velocity = nav.ask_number('Team velocity', 0.0, 0.0, None)
    sum_fte = nav.ask_number('Sum of full-time equivalents at that velocity',
                             float(len(members)), None, None)
    sprint_length = nav.ask_int('Sprint length in working days', 10, 1)
    aliases = nav.level(lambda: _build_aliases(nav))
    return Team(name=name, velocity=velocity, sum_fte_at_velocity=sum_fte,
                sprint_length=sprint_length, aliases=aliases, members=members)


def _build_aliases(nav: _Navigator) -> list[str]:
    """Ask for a counted list of team aliases."""
    count = nav.ask_count('Number of team aliases')
    return [nav.ask_text('Team alias') for _ in range(count)]


def _build_members(nav: _Navigator,
                   person_names: list[str]) -> list[Membership]:
    """Ask for a counted list of team memberships of distinct persons.

    A person joins a team at most once, so each membership is chosen from
    the persons not yet members of this team, and the count cannot exceed
    the number of available persons.
    """
    if not person_names:
        nav.show('No persons defined yet, so the team has no members.')
        return []
    count = nav.ask_count('Number of team members', len(person_names))
    available = list(person_names)
    members: list[Membership] = []
    for _ in range(count):
        membership = nav.level(lambda: _ask_membership(nav, available))
        members.append(membership)
        available.remove(membership.person_name)
    return members


def _ask_membership(nav: _Navigator, person_names: list[str]) -> Membership:
    """Ask for one team membership."""
    person_name = nav.ask_choice('Select the person:', person_names)
    fte = nav.ask_number('Full-time equivalent in this team', 1.0, 0.0, 1.0)
    start_date = nav.ask_opt_date('Membership start date')
    end_date = nav.ask_membership_end('Membership end date', start_date)
    fte_exceptions = nav.level(lambda: _build_fte_exceptions(nav))
    return Membership(person_name=person_name, fte=fte, start_date=start_date,
                      end_date=end_date, fte_exceptions=fte_exceptions)


def _build_fte_exceptions(nav: _Navigator) -> list[FteException]:
    """Ask for a counted list of full-time-equivalent exception periods."""
    count = nav.ask_count('Number of full-time-equivalent exceptions')
    return [nav.level(lambda: _ask_fte_exception(nav)) for _ in range(count)]


def _ask_fte_exception(nav: _Navigator) -> FteException:
    """Ask for one full-time-equivalent exception period."""
    start_date = nav.ask_date('Exception start date')
    end_date = nav.ask_end_date('Exception end date', start_date)
    fte = nav.ask_number('Full-time equivalent during the period', 1.0, 0.0,
                         1.0)
    return FteException(start_date=start_date, end_date=end_date, fte=fte)


def _build_input_presets(nav: _Navigator) -> dict[str, InputFormatConfig]:
    """Ask for a counted list of named input presets."""
    count = nav.ask_count('Number of named input configurations')
    used: set[str] = set()
    result: dict[str, InputFormatConfig] = {}
    for _ in range(count):
        name, config = nav.level(lambda: _ask_input_preset(nav, used))
        used.add(name)
        result[name] = config
    return result


def _build_output_presets(nav: _Navigator) -> dict[str, OutputFormatConfig]:
    """Ask for a counted list of named output presets."""
    count = nav.ask_count('Number of named output configurations')
    used: set[str] = set()
    result: dict[str, OutputFormatConfig] = {}
    for _ in range(count):
        name, config = nav.level(lambda: _ask_output_preset(nav, used))
        used.add(name)
        result[name] = config
    return result


def _ask_input_preset(nav: _Navigator,
                      used: set[str]) -> tuple[str, InputFormatConfig]:
    """Ask for one named input preset and its column-name mapping."""
    name = nav.ask_preset_name('Preset name (letters and digits)', used)
    tableio = nav.ask_tableio(FileAccess.READ)
    column_map = nav.level(
        lambda: nav.ask_column_map('external column', 'internal field'))
    return name, make_input_config(tableio, column_map)


def _ask_output_preset(nav: _Navigator,
                       used: set[str]) -> tuple[str, OutputFormatConfig]:
    """Ask for one named output preset and its column-name mapping."""
    name = nav.ask_preset_name('Preset name (letters and digits)', used)
    tableio = nav.ask_tableio(FileAccess.CREATE)
    column_map = nav.level(
        lambda: nav.ask_column_map('internal field', 'external column'))
    return name, make_output_config(tableio, column_map)
