#! /usr/local/bin/python3
"""Reusable navigation and field-input helpers for the wizards.

The :class:`_Navigator` drives a re-runnable wizard body, recording every
answer so the body can be replayed to honour the bridge's back,
cancel-level and abort requests: going back drops the most recently asked
question, even across levels. The ``_read_*`` and ``_parse_*`` helpers ask
and validate one wizard field each through any ``WizardUiBridge`` of
``tableio_cfg_json``: scalar fields such as text, numbers and dates, and
whole-table fields such as the weekly work-hours schedule, the column
rename maps and the backlog item levels. The small domain helpers
:func:`_ask_level_display` and :func:`_backlog_map_fields` are shared by
the configuration and the preset wizards.

Individual field values are validated as they are entered, and date ranges
are kept non-empty. Cross-item rules that span a whole result are checked
by the caller when the result is stored.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from typing import Callable, Optional, Sequence, TextIO, TypeVar
from tableio import FileAccess, access_capabilities
from tableio_cfg_json import TableCell, TableColumn, TioJsonConfig, \
    WizardBack, WizardCancelLevel, WizardUiBridge, tio_json_config_wizard
from backlogops.backlog import Status
from backlogops.io_config import PRESET_NAME_RE
from backlogops.jira_io_config import JiraAttrPath, JiraAttrType, \
    JiraColumnMap, JiraIssueTypeMap
from backlogops.levels import DEFAULT_LEVELS, Level, LevelDisplay, Levels, \
    levels_from_list
from backlogops.person import Person
from backlogops.table_rows import BACKLOG_FIELDS, LEVEL_COLUMN, \
    LEVEL_NAME_COLUMN
from backlogops.work_hours import DEFAULT_WORK_WEEK, ScheduleWorkHours, \
    WeekDay


_T = TypeVar('_T')


# pylint: disable-next=too-many-public-methods
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

    def ask_choice(self, question: str, choices: Sequence[str],
                   default: Optional[str] = None) -> str:
        """Ask the user to pick one of choices through the bridge."""
        result = self._ask(lambda: self._ui.ask_choice(question,
                                                       choices=choices,
                                                       default=default))
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

    def ask_renames(self, fields: list[str], allow_extra: bool,
                    target_header: str, is_input: bool = False
                    ) -> dict[str, Optional[str]]:
        """Ask one column-rename map as one variable-row table.

        With ``is_input`` false the table stores an internal-to-external
        output map; with it true the table stores an external-to-internal
        input map. Either way the internal field names are pre-filled.
        """
        def read() -> dict[str, Optional[str]]:
            """Ask one rename table through the bound user interface."""
            return _read_renames(self._ui, fields, allow_extra, target_header,
                                 is_input)
        result = self._ask(read)
        assert isinstance(result, dict)
        return result

    def ask_status_map(self, question: str,
                       default_map: Optional[dict[str, Status]] = None
                       ) -> dict[str, Status]:
        """Ask the input status-name map as one variable-row table."""
        result = self._ask(lambda: _read_status_map(self._ui, question,
                                                    default_map))
        assert isinstance(result, dict)
        return result

    def ask_jira_map(self, fields: list[str],
                     default_map: JiraColumnMap) -> JiraColumnMap:
        """Ask one Jira column map as one variable-row table.

        Each internal field is shown pre-filled with the kind and path of
        the default map, or blank when the default leaves it unmapped.
        """
        result = self._ask(lambda: _read_jira_map(self._ui, fields,
                                                  default_map))
        assert isinstance(result, dict)
        return result

    def ask_issue_type_map(self, levels: Levels) -> JiraIssueTypeMap:
        """Ask the level-to-issue-type write map as one fixed-row table.

        Each level is shown with its number and name and an editable Jira
        issue type pre-filled to the level name, so the defaults are
        visible and only real overrides are kept.
        """
        result = self._ask(lambda: _read_issue_type_map(self._ui, levels))
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


def _ask_level_display(nav: _Navigator, question: str) -> LevelDisplay:
    """Ask how to show levels, defaulting to both number and name."""
    choices = [display.name.lower() for display in LevelDisplay]
    answer = nav.ask_choice(question, choices,
                            default=LevelDisplay.BOTH.name.lower())
    return LevelDisplay[answer.upper()]


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


_MAX_EXTRA_COLUMNS = 30
"""How many extra-field rows the user may add to a backlog rename table."""

_RENAME_INSTRUCTION = ('Column renaming (same name keeps it, a blank '
                       'output column drops it; add a row for an extra '
                       'field):')
"""Instruction shown above an output column-rename table."""

_RENAME_REASON = ('Each internal field may appear once and two columns may '
                  'not share a name.')
"""Re-ask reason for an inconsistent output rename table."""

_INPUT_INSTRUCTION = ('Column reading (same name reads it as-is, a different '
                      'name reads that file column into the field; add a row '
                      'to read an extra field, or a blank-field row to drop a '
                      'file column):')
"""Instruction shown above an input column-rename table."""

_INPUT_REASON = 'Each input file column may appear only once.'
"""Re-ask reason for an inconsistent input rename table."""


def _backlog_map_fields() -> list[str]:
    """Return the backlog internal field names offered for renaming.

    The numeric ``level`` and the named ``level name`` columns are offered
    as two independent entries, so each can be renamed or dropped on its
    own when the level display writes both columns.
    """
    fields = list(BACKLOG_FIELDS)
    fields.insert(fields.index(LEVEL_COLUMN) + 1, LEVEL_NAME_COLUMN)
    return fields


def _rename_check(table: list[list[Optional[str]]],
                  position: tuple[int, int]) -> tuple[bool, str]:
    """Advise when an output column lacks its internal field name."""
    row, col = position
    if col == 1 and table[row][1] and not table[row][0]:
        return (False, 'Enter the internal field name for this column.')
    return (True, '')


def _parse_column_renames(table: Sequence[Sequence[Optional[str]]]
                          ) -> Optional[dict[str, Optional[str]]]:
    """Return the rename map from a table, or None when it is invalid.

    A row with a blank internal field is ignored. A blank output column
    drops that field (maps to None). An output column equal to the
    internal field is no rename and is omitted. The table is rejected when
    an internal field repeats or when two columns would share a name.
    """
    mapping: dict[str, Optional[str]] = {}
    kept_names: list[str] = []
    for source, target in ((row[0], row[1]) for row in table):
        if not source:
            continue
        if source in mapping:
            return None
        if not target:
            mapping[source] = None
            continue
        kept_names.append(target)
        if target != source:
            mapping[source] = target
    if len(kept_names) != len(set(kept_names)):
        return None
    return mapping


def _parse_input_renames(table: Sequence[Sequence[Optional[str]]]
                         ) -> Optional[dict[str, Optional[str]]]:
    """Return the file-to-internal map from a table, or None if invalid.

    Each row pairs an internal field (column 0) with the input file column
    read into it (column 1). A blank file column leaves that field
    unmapped. A file column equal to the internal field is no rename and is
    omitted. A row with a file column but a blank internal field drops that
    file column (maps it to None). The table is rejected when one file
    column appears more than once.
    """
    mapping: dict[str, Optional[str]] = {}
    seen: set[str] = set()
    for internal, source in ((row[0], row[1]) for row in table):
        if not source:
            continue
        if source in seen:
            return None
        seen.add(source)
        if not internal:
            mapping[source] = None
        elif source != internal:
            mapping[source] = internal
    return mapping


def _rename_cells(fields: list[str]) -> list[list[TableCell]]:
    """Return seed rows with each editable column pre-filled to its field."""
    return [[TableCell(value=field), TableCell(value=field)]
            for field in fields]


def _read_renames(ui: WizardUiBridge, fields: list[str], allow_extra: bool,
                  target_header: str, is_input: bool
                  ) -> dict[str, Optional[str]]:
    """Ask one column-rename map as one variable-row table.

    Each known internal field is shown as a read-only row pre-filled with
    the same column name, so leaving the table unchanged renames nothing
    and the known fields cannot be deleted. A backlog table also accepts
    added rows for extra fields; an added row is fully editable, so its
    internal name can be typed. A releases table is locked to its own
    fields. The variable-row editor accepts the table on a blank answer.
    With ``is_input`` true the table is parsed as an external-to-internal
    input map, otherwise as an internal-to-external output map.
    """
    columns = [TableColumn(header='Internal field', read_only=True),
               TableColumn(header=target_header)]
    cells = _rename_cells(fields)
    max_rows = len(fields) + _MAX_EXTRA_COLUMNS if allow_extra else len(fields)
    instruction = _INPUT_INSTRUCTION if is_input else _RENAME_INSTRUCTION
    check = None if is_input else _rename_check
    parse = _parse_input_renames if is_input else _parse_column_renames
    reason: Optional[str] = None
    while True:
        table = ui.ask_table(columns, cells, instruction, re_ask_reason=reason,
                             partial_check=check, min_rows=len(fields),
                             max_rows=max_rows)
        mapping = parse(table)
        if mapping is not None:
            return mapping
        reason = _INPUT_REASON if is_input else _RENAME_REASON
        cells = _cells_from_table(table)


_MAX_LEVELS = 99
"""Upper bound on the number of backlog item levels the wizard accepts."""

_LEVELS_INSTRUCTION = (
    'Backlog item levels (a level name and its aliases are also matched '
    'against Jira issue types when reading from Jira, so include every '
    'Jira issue type you read as the level name or one of its aliases):')
"""Instruction shown above the backlog item levels table."""


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
        table = ui.ask_table(columns, cells, _LEVELS_INSTRUCTION,
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


_ISSUE_TYPE_INSTRUCTION = (
    'Jira issue type to create for each level when writing to Jira (blank '
    'or the level name keeps the level name; used only when writing, not '
    'when reading):')
"""Instruction shown above a level-to-issue-type write map table."""


def _issue_type_cells(levels: Levels) -> list[list[TableCell]]:
    """Return table rows pre-filled from the levels for the issue map."""
    return [[TableCell(value=str(level.level)), TableCell(value=level.name),
             TableCell(value=level.name)] for level in levels.values()]


def _parse_issue_types(table: list[list[Optional[str]]]) -> JiraIssueTypeMap:
    """Return the level-to-issue-type map, keeping only real overrides.

    A blank issue type, or one equal to the level name, keeps the level
    name and is omitted, so only levels whose Jira issue type differs from
    the level name are stored.
    """
    result: JiraIssueTypeMap = {}
    for row in table:
        number = _parse_level_int(row[0])
        name = row[1]
        issue_type = (row[2] or '').strip()
        if number is not None and issue_type and issue_type != name:
            result[number] = issue_type
    return result


def _read_issue_type_map(ui: WizardUiBridge,
                         levels: Levels) -> JiraIssueTypeMap:
    """Ask the level-to-issue-type write map as one fixed-row table.

    Each level is a read-only number and name with an editable Jira issue
    type pre-filled to the level name, so the defaults are visible and
    leaving the table unchanged writes each level's own name.
    """
    columns = [TableColumn(header='Level', read_only=True),
               TableColumn(header='Internal name', read_only=True),
               TableColumn(header='Jira issue type')]
    cells = _issue_type_cells(levels)
    count = len(cells)
    table = ui.ask_table(columns, cells, _ISSUE_TYPE_INSTRUCTION,
                         min_rows=count, max_rows=count)
    return _parse_issue_types(table)


_STATUS_NAMES = [status.name for status in Status]
"""Internal status names offered as status-map targets."""

_MAX_STATUS_MAP = 50
"""Upper bound on the number of status-name mappings the wizard accepts."""

_STATUS_TARGETS_HINT = ('Internal status is one of '
                        + ', '.join(_STATUS_NAMES) + '.')
"""Hint listing the valid internal status names."""


def _status_target(text: Optional[str]) -> Optional[str]:
    """Return the internal status name in ``text`` (case-insensitive)."""
    if text is None:
        return None
    upper = text.strip().upper()
    return upper if upper in _STATUS_NAMES else None


def _status_check(table: list[list[Optional[str]]],
                  position: tuple[int, int]) -> tuple[bool, str]:
    """Give early feedback that a status-map row is complete and valid."""
    row = position[0]
    name, target = table[row][0], table[row][1]
    if target and _status_target(target) is None:
        return (False, _STATUS_TARGETS_HINT)
    if target and not name:
        return (False, 'Enter the file status name for this row.')
    return (True, '')


def _parse_status_map(table: list[list[Optional[str]]]
                      ) -> Optional[dict[str, Status]]:
    """Return the status map from a table, or None when a row is invalid.

    A row with a blank file status name is ignored. A non-blank file
    status name needs a valid internal status. A file status name that
    repeats (case-insensitively) makes the table invalid.
    """
    mapping: dict[str, Status] = {}
    seen: set[str] = set()
    for name, target in ((row[0], row[1]) for row in table):
        if not name:
            continue
        status_name = _status_target(target)
        if status_name is None:
            return None
        lowered = name.lower()
        if lowered in seen:
            return None
        seen.add(lowered)
        mapping[name] = Status[status_name]
    return mapping


def _merge_status_defaults(default_map: Optional[dict[str, Status]],
                           mapping: dict[str, Status]) -> dict[str, Status]:
    """Return defaults updated with user-entered status map rows."""
    if default_map is None:
        return mapping
    result = dict(default_map)
    names = {name.lower(): name for name in result}
    for name, status in mapping.items():
        old_name = names.get(name.lower())
        if old_name is not None and old_name != name:
            del result[old_name]
        result[name] = status
        names[name.lower()] = name
    return result


def _status_map_cells(default_map: Optional[dict[str, Status]]
                      ) -> list[list[TableCell]]:
    """Return seed rows for a status-name mapping table."""
    if default_map is None:
        return []
    return [[TableCell(value=name), TableCell(value=status.name)]
            for name, status in default_map.items()]


def _read_status_map(ui: WizardUiBridge, question: str,
                     default_map: Optional[dict[str, Status]] = None
                     ) -> dict[str, Status]:
    """Ask the input status-name map as one variable-row table.

    Each row maps an extra file status name to an internal status. The
    table starts with ``default_map`` when one is given and otherwise
    empty. It may be left empty for no extra names. An invalid table is
    re-asked with the user's own rows kept.
    """
    columns = [TableColumn(header='File status name'),
               TableColumn(header='Internal status')]
    cells = _status_map_cells(default_map)
    instruction = f'{question} {_STATUS_TARGETS_HINT}'
    reason: Optional[str] = None
    while True:
        table = ui.ask_table(columns, cells, instruction, re_ask_reason=reason,
                             partial_check=_status_check, min_rows=0,
                             max_rows=_MAX_STATUS_MAP)
        mapping = _parse_status_map(table)
        if mapping is not None:
            return _merge_status_defaults(default_map, mapping)
        reason = ('Map each file status name once to '
                  + ', '.join(_STATUS_NAMES) + '.')
        cells = _cells_from_table(table)


_JIRA_KINDS = [kind.name for kind in JiraAttrType]
"""Attribute kind names offered as Jira column-map targets."""

_MAX_JIRA_EXTRA = 30
"""How many extra-field rows the user may add to a Jira column map."""

_JIRA_MAP_INSTRUCTION = (
    'Jira attribute paths (Kind is one of ' + ', '.join(_JIRA_KINDS)
    + '; a FIELD path uses dots like status.name; a FILTERED_FIELD path '
    'uses semicolons like issuelinks;type.name;Blocks;inwardIssue.key; '
    'blank leaves a field unmapped):')
"""Instruction shown above a Jira column-map table."""

_JIRA_MAP_REASON = 'Give each mapped field a valid kind and path.'
"""Re-ask reason for an inconsistent Jira column-map table."""


def _path_text(attr: JiraAttrPath) -> str:
    """Return a Jira path as text for the wizard table."""
    if attr.kind is JiraAttrType.FIELD:
        return '.'.join(attr.path)
    if attr.kind is JiraAttrType.FILTERED_FIELD:
        return ';'.join(attr.path)
    return attr.path[0]


def _jira_map_cells(fields: list[str],
                    default_map: JiraColumnMap) -> list[list[TableCell]]:
    """Return seed rows pre-filled from the default Jira column map."""
    rows: list[list[TableCell]] = []
    for field in fields:
        attrs = default_map.get(field, ())
        if not attrs:
            rows.append([TableCell(value=field), TableCell(value=''),
                         TableCell(value='')])
        for attr in attrs:
            rows.append([TableCell(value=field),
                         TableCell(value=attr.kind.name),
                         TableCell(value=_path_text(attr))])
    return rows


def _jira_map_check(table: list[list[Optional[str]]],
                    position: tuple[int, int]) -> tuple[bool, str]:
    """Give early feedback that a Jira column-map row is valid."""
    row, col = position
    kind, path = table[row][1], table[row][2]
    if col == 1 and kind and kind.strip().upper() not in _JIRA_KINDS:
        return (False, 'Kind is one of ' + ', '.join(_JIRA_KINDS) + '.')
    if col == 2 and path and not kind:
        return (False, 'Enter the kind for this path.')
    return (True, '')


def _attr_from_cells(kind_text: str, path_text: str) -> Optional[JiraAttrPath]:
    """Return a JiraAttrPath from a kind cell and a path cell, or None."""
    name = kind_text.strip().upper()
    if name not in _JIRA_KINDS:
        return None
    kind = JiraAttrType[name]
    text = path_text.strip()
    if kind is JiraAttrType.FIELD:
        steps = tuple(part for part in text.split('.') if part)
    elif kind is JiraAttrType.FILTERED_FIELD:
        steps = tuple(part.strip() for part in text.split(';')
                      if part.strip())
    else:
        steps = (text,) if text else ()
    if not steps or (kind is JiraAttrType.FILTERED_FIELD and len(steps) != 4):
        return None
    return JiraAttrPath(kind=kind, path=steps)


def _parse_jira_map(table: list[list[Optional[str]]]
                    ) -> Optional[JiraColumnMap]:
    """Return the Jira column map from a table, or None when invalid.

    A row with a blank kind and path leaves that field unmapped. A row
    with only one of kind and path is invalid. Repeated internal fields
    become multiple paths for the same field.
    """
    result: JiraColumnMap = {}
    for field, kind_text, path_text in ((r[0], r[1], r[2]) for r in table):
        if not field:
            continue
        if not kind_text and not path_text:
            continue
        if not kind_text or not path_text:
            return None
        attr = _attr_from_cells(kind_text, path_text)
        if attr is None:
            return None
        result.setdefault(field, ())
        result[field] = (*result[field], attr)
    return result


def _read_jira_map(ui: WizardUiBridge, fields: list[str],
                   default_map: JiraColumnMap) -> JiraColumnMap:
    """Ask one Jira column map as one variable-row table.

    Each internal field is a read-only, pre-filled row; its kind and path
    cells start from the default map or blank. Added rows are fully
    editable so an extra field can be mapped. An invalid table is re-asked
    with the user's own rows kept.
    """
    columns = [TableColumn(header='Internal field', read_only=True),
               TableColumn(header='Kind'), TableColumn(header='Path')]
    cells = _jira_map_cells(fields, default_map)
    reason: Optional[str] = None
    while True:
        table = ui.ask_table(columns, cells, _JIRA_MAP_INSTRUCTION,
                             re_ask_reason=reason,
                             partial_check=_jira_map_check,
                             min_rows=len(fields),
                             max_rows=len(cells) + _MAX_JIRA_EXTRA)
        mapping = _parse_jira_map(table)
        if mapping is not None:
            return mapping
        reason = _JIRA_MAP_REASON
        cells = _cells_from_table(table)
