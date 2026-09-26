#! /usr/local/bin/python3
"""Wizard questions about how backlog items are estimated.

A backlog item nobody has estimated can be given a best guess by level,
in story points and, where remaining time estimates are also used, in
remaining time. Both guesses are asked the same way: one form says
whether to guess at all and whether to fill in the levels between and
beyond the ones given, and one variable-row table then gives a value to
each level. :func:`_read_guess` asks that table for either kind, told
how by a :class:`_GuessKind`.

Remaining time also needs a focus factor: the configuration has a
default one, and each team may have one of its own, which is asked only
when remaining time is enabled.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from dataclasses import dataclass
from datetime import timedelta
from functools import partial
from typing import Callable, Optional, TextIO
from config_as_json import Config
from wizard_ui_bridge import TableCell, TableColumn, WizardUiBridge
from backlogops.default_story_points import DefaultStoryPointLevel, \
    DefaultStoryPoints
from backlogops.duration_text import format_duration, parse_duration
from backlogops.remaining_time_config import DefaultRemainingTimeLevel, \
    RemainingTimeConfig
from backlogops.team import FOCUS_FACTOR_RANGE
from backlogops.wizard_forms import FormField, FormResult, number_field, \
    yes_no_field
from backlogops.wizard_helpers import _MAX_LEVELS, _cells_from_table, \
    _parse_level_int
from backlogops.wizard_navigator import _Navigator


@dataclass(frozen=True)
class _GuessKind[V, D: Config]:
    """How one kind of guess by level is asked as a table.

    Attributes:
        header: The header of the value column.
        instruction: The text shown above the table.
        value_error: The feedback on a value cell that cannot be read.
        row_error: The re-ask reason when a row cannot be read.
        parse: Returns the value a cell says, or None when it says none.
        rows: Returns the level and value text of each level of a guess.
        build: Returns the guess of the given levels and values, with the
            interpolate and extrapolate settings.
    """

    header: str
    instruction: str
    value_error: str
    row_error: str
    parse: Callable[[Optional[str]], Optional[V]]
    rows: Callable[[D], list[tuple[int, str]]]
    build: Callable[[list[tuple[int, V]], bool, bool], D]


def _guess_check[V, D: Config](kind: _GuessKind[V, D],
                               table: list[list[Optional[str]]],
                               position: tuple[int, int]) -> tuple[bool, str]:
    """Give early feedback that a level or value cell is valid."""
    row, col = position
    if col == 0:
        ok = _parse_level_int(table[row][0]) is not None
        return (ok, '' if ok else 'Enter the level as a whole number.')
    ok = kind.parse(table[row][1]) is not None
    return (ok, '' if ok else kind.value_error)


def _guess_cells[V, D: Config](kind: _GuessKind[V, D], seed: Optional[D],
                               rows: int) -> list[list[TableCell]]:
    """Return the table rows filled from a seed, or ``rows`` empty ones."""
    given = kind.rows(seed) if seed is not None else []
    if not given:
        return [[TableCell(value=''), TableCell(value='')]
                for _ in range(rows)]
    return [[TableCell(value=str(level)), TableCell(value=text)]
            for level, text in given]


def _parse_guess[V, D: Config](kind: _GuessKind[V, D],
                               table: list[list[Optional[str]]]
                               ) -> Optional[list[tuple[int, V]]]:
    """Return the level and value of every row, or None on a bad cell.

    The values are only read here; whether they make sense together is
    left to the validation of the configuration class itself.
    """
    pairs: list[tuple[int, V]] = []
    for row in table:
        number = _parse_level_int(row[0])
        value = kind.parse(row[1])
        if number is None or value is None:
            return None
        pairs.append((number, value))
    return pairs


def _guess_problem(guess: Config, error_file: TextIO) -> Optional[str]:
    """Return a re-ask reason when the guess is refused, else None.

    Validating the built configuration is what checks it, so the wizard
    refuses exactly what a stored file refuses, and the same call sorts
    the levels and builds the lookup of the returned object.
    """
    try:
        guess.validate(error_file)
    except (TypeError, ValueError, KeyError) as problem:
        return str(problem.args[0]) if problem.args else str(problem)
    return None


def _read_guess[V, D: Config](ui: WizardUiBridge, kind: _GuessKind[V, D],
                              interpolate: bool, extrapolate: bool,
                              seed: Optional[D] = None) -> D:
    """Ask a guess by level as one variable-row table question.

    Two rows are asked for when a level between or beyond the given ones
    is to be guessed, because a growth factor is worked out from two
    levels. Each cell is checked as it is entered, and the whole table is
    then checked by validating the configuration it builds.
    """
    columns = [TableColumn(header='Level'), TableColumn(header=kind.header)]
    least = 2 if interpolate or extrapolate else 1
    cells = _guess_cells(kind, seed, least)
    reason: Optional[str] = None
    while True:
        table = ui.ask_table(columns, cells, kind.instruction,
                             re_ask_reason=reason,
                             partial_check=partial(_guess_check, kind),
                             min_rows=least, max_rows=_MAX_LEVELS)
        pairs = _parse_guess(kind, table)
        if pairs is not None:
            guess = kind.build(pairs, interpolate, extrapolate)
            reason = _guess_problem(guess, ui.error_file())
            if reason is None:
                return guess
        else:
            reason = kind.row_error
        cells = _cells_from_table(table)


def _parse_points(text: Optional[str]) -> Optional[float]:
    """Return ``text`` as story points, or None when it is no number."""
    if text is None:
        return None
    try:
        return float(text.strip())
    except ValueError:
        return None


def _points_rows(points: DefaultStoryPoints) -> list[tuple[int, str]]:
    """Return the level and story points text of each given level."""
    return [(level.level, f'{level.story_points:g}')
            for level in points.levels]


def _points_level(number: int, points: float) -> DefaultStoryPointLevel:
    """Return the default story points of one level."""
    level = DefaultStoryPointLevel()
    level.level = number
    level.story_points = points
    return level


def _points_guess(pairs: list[tuple[int, float]], interpolate: bool,
                  extrapolate: bool) -> DefaultStoryPoints:
    """Return the default story points of the given levels and settings."""
    points = DefaultStoryPoints()
    points.interpolate = interpolate
    points.extrapolate = extrapolate
    points.levels = [_points_level(number, size) for number, size in pairs]
    return points


_POINTS_KIND = _GuessKind(
    header='Story points',
    instruction='Story points to work a backlog item of each level with, '
                'while the item has no story points of its own and has no '
                'children (a level you leave out is guessed from these '
                'when you asked for that):',
    value_error='Enter the story points as a number.',
    row_error='Enter a whole-number level and its story points as a number '
              'in every row.',
    parse=_parse_points, rows=_points_rows, build=_points_guess)
"""How the default story points table is asked."""


def _read_def_points(ui: WizardUiBridge, interpolate: bool, extrapolate: bool,
                     seed: Optional[DefaultStoryPoints] = None
                     ) -> DefaultStoryPoints:
    """Ask the default story points as one variable-row table question."""
    return _read_guess(ui, _POINTS_KIND, interpolate, extrapolate, seed)


def _parse_time(text: Optional[str]) -> Optional[timedelta]:
    """Return ``text`` as a remaining time, or None when it is none."""
    return None if text is None else parse_duration(text)


def _time_rows(config: RemainingTimeConfig) -> list[tuple[int, str]]:
    """Return the level and remaining time text of each given level."""
    return [(level.level, format_duration(level.remaining_time))
            for level in config.levels]


def _time_level(number: int, time: timedelta) -> DefaultRemainingTimeLevel:
    """Return the default remaining time of one level."""
    level = DefaultRemainingTimeLevel()
    level.level = number
    level.remaining_time = time
    return level


def _time_guess(focus: float, pairs: list[tuple[int, timedelta]],
                interpolate: bool, extrapolate: bool) -> RemainingTimeConfig:
    """Return remaining time enabled with a focus factor and a guess."""
    config = RemainingTimeConfig()
    config.enable_remaining_time = True
    config.default_focus_factor = focus
    config.interpolate = interpolate
    config.extrapolate = extrapolate
    config.levels = [_time_level(number, time) for number, time in pairs]
    return config


def _time_kind(focus: float) -> _GuessKind[timedelta, RemainingTimeConfig]:
    """Return how the default remaining time table is asked."""
    return _GuessKind(
        header='Remaining time',
        instruction='Remaining time (hours:minutes:seconds of focused work '
                    'of one person, optionally after whole weeks and days '
                    'of 24 hours, such as 1d 2:30:00) to work a backlog '
                    'item of each level with, while the item has no '
                    'remaining time of its own and has no children (a '
                    'level you leave out is guessed from these when you '
                    'asked for that):',
        value_error='Enter the remaining time as hours:minutes:seconds.',
        row_error='Enter a whole-number level and its remaining time as '
                  'hours:minutes:seconds in every row.',
        parse=_parse_time, rows=_time_rows, build=partial(_time_guess, focus))


def _guess_fields(unit: str) -> list[FormField]:
    """Return the fields asking whether and how to guess a size."""
    return [
        yes_no_field('guess', 'Guess the size of backlog items that have no '
                     f'{unit}?', False),
        yes_no_field('interpolate', 'Also guess a level between the levels '
                     'you give?', True),
        yes_no_field('extrapolate', 'Also guess a level above the highest '
                     'or below the lowest level you give?', True)]


def _guess_disabled(values: FormResult) -> set[str]:
    """Return the filling-in questions, when nothing is guessed at all."""
    return set() if values.flag('guess') else {'interpolate', 'extrapolate'}


def _guess_seed(guess: bool, interpolate: bool,
                extrapolate: bool) -> dict[str, object]:
    """Return the values of the guess fields of a stored guess."""
    return {'guess': guess, 'interpolate': interpolate,
            'extrapolate': extrapolate}


_DEF_POINTS_QUESTION = (
    'A backlog item that nobody has estimated is worked with no story '
    'points at all unless you give a best guess for its level here. An '
    'item that has story points of its own, and an item that is only a '
    'container for its children, takes nothing from that guess.')
"""Instruction shown above the default story points form."""


def _def_points_rule(values: FormResult) -> tuple[Optional[str], set[str]]:
    """Disable the filling-in questions when nothing is guessed at all."""
    return None, _guess_disabled(values)


def _build_def_points(nav: _Navigator, default: Optional[DefaultStoryPoints]
                      ) -> DefaultStoryPoints:
    """Ask what an unestimated backlog item is worked with.

    Whether to guess at all, and whether to fill in the levels between
    and beyond the ones given, are asked on one form; the levels
    themselves are then one table, which is only asked for when there is
    a guess to make.
    """
    seed = None if default is None else FormResult(_guess_seed(
        bool(default.levels), default.interpolate, default.extrapolate))
    values = nav.ask_form(_DEF_POINTS_QUESTION, _guess_fields('story points'),
                          _def_points_rule, seed=seed)
    if not values.flag('guess'):
        return DefaultStoryPoints()
    interpolate = values.flag('interpolate')
    extrapolate = values.flag('extrapolate')
    return nav.ask_guess(lambda ui, sd: _read_def_points(
        ui, interpolate, extrapolate, sd), DefaultStoryPoints, seed=default)


_FOCUS_HELP = (
    'The focus factor is the fraction of the working time that counts as '
    'focused work on the backlog items. It makes up for meetings, other '
    'work and optimism or pessimism in the estimates. Common values are '
    'from 0.1 to 0.5.')
"""What a focus factor is, shown with a question that asks one."""


def _focus_field(default: float) -> FormField:
    """Return the field asking a focus factor within the allowed range."""
    lowest, highest = FOCUS_FACTOR_RANGE
    return number_field('focus', f'Focus factor ({lowest} to {highest})',
                        default=default, minimum=lowest, maximum=highest)


_REMAINING_QUESTION = (
    'Estimating in story points is recommended. Enable remaining time '
    'estimates only when the backlog items must be estimated in remaining '
    'time, which is ideal focused work time of one person. Story points '
    'stay in use either way, so both kinds of estimates may be used, such '
    'as while moving from remaining time to story points. ' + _FOCUS_HELP)
"""Instruction shown above the remaining time form."""


def _remaining_fields() -> list[FormField]:
    """Return the fields of the remaining time form."""
    return [yes_no_field('enable', 'Also estimate in remaining time?', False),
            _focus_field(0.3)] + _guess_fields('remaining time')


def _remaining_rule(values: FormResult) -> tuple[Optional[str], set[str]]:
    """Disable the rest when remaining time is not used at all."""
    if not values.flag('enable'):
        return None, {'focus', 'guess', 'interpolate', 'extrapolate'}
    return None, _guess_disabled(values)


def _remaining_seed(default: Optional[RemainingTimeConfig]
                    ) -> Optional[FormResult]:
    """Return the form values of a stored remaining time configuration."""
    if default is None:
        return None
    return FormResult({'enable': default.enable_remaining_time,
                       'focus': default.default_focus_factor,
                       **_guess_seed(bool(default.levels), default.interpolate,
                                     default.extrapolate)})


def _build_remaining(nav: _Navigator, default: Optional[RemainingTimeConfig]
                     ) -> RemainingTimeConfig:
    """Ask whether remaining time is used, and how it is guessed.

    Whether to use remaining time, the default focus factor, whether to
    guess at all, and whether to fill in the levels between and beyond
    the ones given, are asked on one form. When remaining time is not
    used, nothing more is asked. The levels are then one table, which is
    only asked for when there is a guess to make.
    """
    values = nav.ask_form(_REMAINING_QUESTION, _remaining_fields(),
                          _remaining_rule, seed=_remaining_seed(default))
    if not values.flag('enable'):
        return RemainingTimeConfig()
    kind = _time_kind(values.number('focus'))
    if not values.flag('guess'):
        return kind.build([], False, False)
    interpolate = values.flag('interpolate')
    extrapolate = values.flag('extrapolate')
    return nav.ask_guess(lambda ui, sd: _read_guess(ui, kind, interpolate,
                                                    extrapolate, sd),
                         RemainingTimeConfig, seed=default)


def _team_focus_fields(default: float) -> list[FormField]:
    """Return the fields asking whether and which own focus factor."""
    return [yes_no_field('own_focus', 'Does the team have a focus factor '
                         'of its own?', False),
            _focus_field(default)]


def _team_focus_rule(values: FormResult) -> tuple[Optional[str], set[str]]:
    """Disable the focus factor when the team has none of its own.

    A team form that does not ask for a focus factor has no answer to
    the question, which counts as having none of its own.
    """
    if values.raw('own_focus') is not True:
        return None, {'focus'}
    return None, set()


def _team_focus_seed(focus_factor: Optional[float]) -> dict[str, object]:
    """Return the values of the focus fields of a stored team."""
    return {'own_focus': focus_factor is not None, 'focus': focus_factor}


def _team_focus(values: FormResult) -> Optional[float]:
    """Return the own focus factor a team form gives, or None."""
    return values.number('focus') if values.flag('own_focus') else None
