#! /usr/local/bin/python3
"""Interactively build an AvailableTeams workforce configuration.

The public helper :func:`available_teams_wizard` asks the user for the
company work hours, the persons and their personal work-hour exceptions,
and the teams with their members. It takes a ``WizardUiBridge`` (the same
bridge abstraction used by ``tableio_cfg_json``) so the same wizard logic
can drive a console text interface or a graphical user interface.

Individual field values are validated as they are entered, and date
ranges are kept non-empty. Cross-item rules that span a whole workforce,
such as non-overlapping exception periods and per-person capacity, are
checked when the result is stored; an invalid combination is reported
then and the workforce must be entered again.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from datetime import date
from typing import Optional, Sequence
from config_as_json import string_best_match
from tableio_cfg_json import WizardUiBridge
from backlogops.available_teams import AvailableTeams
from backlogops.person import Person
from backlogops.team import FteException, Membership, Team
from backlogops.work_hours import CompanyWorkHours, DEFAULT_WORK_WEEK, \
    ExceptionWorkHours, ScheduleWorkHours, WeekDay


def available_teams_wizard(ui_bridge: WizardUiBridge) -> AvailableTeams:
    """Interactively create an available workforce configuration.

    Args:
        ui_bridge: Bridge between the wizard and the user interface.

    Returns:
        The workforce entered by the user. Field values are individually
        valid, but whole-workforce consistency is only enforced when the
        result is stored.

    Raises:
        EOFError: The input ended before all required answers were read.
    """
    ui_bridge.show('Configure the available workforce.')
    company = _build_company(ui_bridge)
    persons = _build_persons(ui_bridge)
    names = [person.name for person in persons.values()]
    teams = _build_teams(ui_bridge, names)
    return AvailableTeams(persons=persons, teams=teams,
                          company_work_hours=company)


def _as_text(answer: object) -> str:
    """Return a bridge answer as text, accepting a numeric index too."""
    return answer if isinstance(answer, str) else str(answer)


def _ask_text(ui_bridge: WizardUiBridge, question: str, *,
              default: Optional[str] = None, allow_empty: bool = False) -> str:
    """Ask for a text value with an optional default and re-ask on empty."""
    prompt = question if default is None else f'{question} [{default}]'
    re_ask: Optional[str] = None
    while True:
        answer = _as_text(ui_bridge.ask(prompt, re_ask))
        if answer != '':
            return answer
        if default is not None:
            return default
        if allow_empty:
            return ''
        re_ask = 'Please enter a non-empty value.'


def _ask_number(ui_bridge: WizardUiBridge, question: str, default: float,
                minimum: Optional[float], maximum: Optional[float]) -> float:
    """Ask for a floating point value within optional bounds."""
    re_ask: Optional[str] = None
    while True:
        answer = _as_text(ui_bridge.ask(f'{question} [{default}]', re_ask))
        if answer == '':
            return default
        try:
            value = float(answer)
        except ValueError:
            re_ask = 'Please enter a number.'
            continue
        if minimum is not None and value < minimum:
            re_ask = f'Please enter a value of at least {minimum}.'
        elif maximum is not None and value > maximum:
            re_ask = f'Please enter a value of at most {maximum}.'
        else:
            return value


def _ask_int(ui_bridge: WizardUiBridge, question: str, default: int,
             minimum: int) -> int:
    """Ask for an integer value that is at least ``minimum``."""
    re_ask: Optional[str] = None
    while True:
        answer = _as_text(ui_bridge.ask(f'{question} [{default}]', re_ask))
        if answer == '':
            return default
        try:
            value = int(answer)
        except ValueError:
            re_ask = 'Please enter a whole number.'
            continue
        if value < minimum:
            re_ask = f'Please enter a value of at least {minimum}.'
        else:
            return value


def _ask_yes_no(ui_bridge: WizardUiBridge, question: str,
                default: bool) -> bool:
    """Ask a yes/no question, returning ``default`` for an empty answer."""
    hint = 'Y/n' if default else 'y/N'
    re_ask: Optional[str] = None
    while True:
        answer = _as_text(ui_bridge.ask(f'{question} ({hint})', re_ask))
        if answer == '':
            return default
        lowered = answer.strip().lower()
        if lowered in ('y', 'yes'):
            return True
        if lowered in ('n', 'no'):
            return False
        re_ask = "Please answer 'yes' or 'no'."


def _ask_date(ui_bridge: WizardUiBridge, question: str) -> date:
    """Ask for a required ISO 8601 date such as ``2026-06-13``."""
    re_ask: Optional[str] = None
    while True:
        answer = _as_text(ui_bridge.ask(f'{question} (YYYY-MM-DD)', re_ask))
        parsed = _parse_date(answer)
        if parsed is not None:
            return parsed
        re_ask = 'Please enter a date as YYYY-MM-DD.'


def _ask_end_date(ui_bridge: WizardUiBridge, question: str,
                  start_date: date) -> date:
    """Ask for an end date that is not before ``start_date``."""
    while True:
        end_date = _ask_date(ui_bridge, question)
        if end_date >= start_date:
            return end_date
        ui_bridge.show('The end date must not be before the start date.')


def _ask_opt_date(ui_bridge: WizardUiBridge, question: str) -> Optional[date]:
    """Ask for an optional ISO date; an empty answer returns ``None``."""
    re_ask: Optional[str] = None
    while True:
        answer = _as_text(ui_bridge.ask(f'{question} (YYYY-MM-DD, '
                                        'blank for none)', re_ask))
        if answer == '':
            return None
        parsed = _parse_date(answer)
        if parsed is not None:
            return parsed
        re_ask = 'Please enter a date as YYYY-MM-DD, or leave blank.'


def _parse_date(answer: str) -> Optional[date]:
    """Return the ISO date in ``answer``, or ``None`` when it is invalid."""
    try:
        return date.fromisoformat(answer)
    except ValueError:
        return None


def _ask_choice(ui_bridge: WizardUiBridge, question: str,
                choices: Sequence[str]) -> str:
    """Ask the user to pick one of ``choices`` by number or by name."""
    re_ask: Optional[str] = None
    while True:
        answer = ui_bridge.ask(question, re_ask, choices)
        if isinstance(answer, int) and not isinstance(answer, bool):
            if 0 <= answer < len(choices):
                return choices[answer]
            re_ask = 'Please pick one of the listed choices.'
            continue
        try:
            return string_best_match(_as_text(answer), choices, 'choice',
                                     ui_bridge.error_file())
        except ValueError:
            re_ask = 'Please pick one of the listed choices.'


def _build_company(ui_bridge: WizardUiBridge) -> CompanyWorkHours:
    """Ask for the company weekly schedule and exception periods."""
    ui_bridge.show('Company work hours per week day:')
    work_hours = _build_schedule(ui_bridge)
    exceptions = _build_exceptions(ui_bridge,
                                   'company holiday, closure or special '
                                   'work period')
    return CompanyWorkHours(work_hours=work_hours, exceptions=exceptions)


def _build_schedule(ui_bridge: WizardUiBridge) -> ScheduleWorkHours:
    """Ask for the work hours of each week day."""
    schedule: ScheduleWorkHours = {}
    for week_day in WeekDay:
        schedule[week_day] = _ask_number(
            ui_bridge, f'Work hours on {week_day.name.capitalize()}',
            DEFAULT_WORK_WEEK[week_day], 0.0, None)
    return schedule


def _build_exceptions(ui_bridge: WizardUiBridge,
                      label: str) -> list[ExceptionWorkHours]:
    """Loop asking for work-hour exception periods of the given kind."""
    exceptions: list[ExceptionWorkHours] = []
    while _ask_yes_no(ui_bridge, f'Add a {label}?', False):
        exceptions.append(_ask_exception(ui_bridge))
    return exceptions


def _ask_exception(ui_bridge: WizardUiBridge) -> ExceptionWorkHours:
    """Ask for one work-hour exception period."""
    start_date = _ask_date(ui_bridge, 'Start date')
    end_date = _ask_end_date(ui_bridge, 'End date', start_date)
    hours = _ask_number(ui_bridge, 'Work hours per day during the period', 0.0,
                        0.0, None)
    new_work_days = _ask_yes_no(
        ui_bridge, 'Does this add work on days that are normally free?', False)
    return ExceptionWorkHours(start_date=start_date, end_date=end_date,
                              hours_per_day=hours, new_work_days=new_work_days)


def _build_persons(ui_bridge: WizardUiBridge) -> dict[str, Person]:
    """Loop asking for persons and their personal work-hour exceptions."""
    persons: dict[str, Person] = {}
    while _ask_yes_no(ui_bridge, 'Add a person?', False):
        name = _ask_person_name(ui_bridge, persons)
        exceptions = _build_exceptions(
            ui_bridge, f'vacation or work-hour exception for {name}')
        persons[name.lower()] = Person(name=name, exceptions=exceptions)
    return persons


def _ask_person_name(ui_bridge: WizardUiBridge,
                     persons: dict[str, Person]) -> str:
    """Ask for a person name that is not already used."""
    re_ask: Optional[str] = None
    while True:
        name = _ask_text(ui_bridge, 'Person name')
        if name.lower() not in persons:
            return name
        re_ask = f'A person named {name!r} already exists.'
        ui_bridge.show(re_ask)


def _build_teams(ui_bridge: WizardUiBridge,
                 person_names: list[str]) -> list[Team]:
    """Loop asking for teams and their memberships."""
    teams: list[Team] = []
    while _ask_yes_no(ui_bridge, 'Add a team?', False):
        teams.append(_ask_team(ui_bridge, person_names))
    return teams


def _ask_team(ui_bridge: WizardUiBridge, person_names: list[str]) -> Team:
    """Ask for one team and its memberships."""
    name = _ask_text(ui_bridge, 'Team name')
    velocity = _ask_number(ui_bridge, 'Team velocity', 0.0, 0.0, None)
    sum_fte = _ask_number(ui_bridge,
                          'Sum of full-time equivalents at that velocity', 1.0,
                          None, None)
    sprint_length = _ask_int(ui_bridge, 'Sprint length in working days', 10, 1)
    aliases = _build_aliases(ui_bridge)
    members = _build_members(ui_bridge, person_names)
    return Team(name=name, velocity=velocity, sum_fte_at_velocity=sum_fte,
                sprint_length=sprint_length, aliases=aliases, members=members)


def _build_aliases(ui_bridge: WizardUiBridge) -> list[str]:
    """Loop asking for team aliases until an empty answer is given."""
    aliases: list[str] = []
    while _ask_yes_no(ui_bridge, 'Add an alias for the team?', False):
        aliases.append(_ask_text(ui_bridge, 'Team alias'))
    return aliases


def _build_members(ui_bridge: WizardUiBridge,
                   person_names: list[str]) -> list[Membership]:
    """Loop asking for team memberships referencing known persons.

    A person who is already a member of this team is not offered again,
    so each person joins the team at most once.
    """
    if not person_names:
        ui_bridge.show('No persons defined yet, so the team has no members.')
        return []
    members: list[Membership] = []
    available = list(person_names)
    while available and _ask_yes_no(ui_bridge, 'Add a team member?', False):
        membership = _ask_membership(ui_bridge, available)
        members.append(membership)
        available.remove(membership.person_name)
    return members


def _ask_membership(ui_bridge: WizardUiBridge,
                    person_names: list[str]) -> Membership:
    """Ask for one team membership."""
    person_name = _ask_choice(ui_bridge, 'Select the person:', person_names)
    fte = _ask_number(ui_bridge, 'Full-time equivalent in this team', 1.0, 0.0,
                      1.0)
    start_date = _ask_opt_date(ui_bridge, 'Membership start date')
    end_date = _ask_membership_end(ui_bridge, start_date)
    fte_exceptions = _build_fte_exceptions(ui_bridge)
    return Membership(person_name=person_name, fte=fte, start_date=start_date,
                      end_date=end_date, fte_exceptions=fte_exceptions)


def _ask_membership_end(ui_bridge: WizardUiBridge,
                        start_date: Optional[date]) -> Optional[date]:
    """Ask for an optional membership end date not before the start date."""
    while True:
        end_date = _ask_opt_date(ui_bridge, 'Membership end date')
        if end_date is None or start_date is None or end_date >= start_date:
            return end_date
        ui_bridge.show('The end date must not be before the start date.')


def _build_fte_exceptions(ui_bridge: WizardUiBridge) -> list[FteException]:
    """Loop asking for full-time-equivalent exception periods."""
    exceptions: list[FteException] = []
    while _ask_yes_no(ui_bridge,
                      'Add a full-time-equivalent exception period?', False):
        exceptions.append(_ask_fte_exception(ui_bridge))
    return exceptions


def _ask_fte_exception(ui_bridge: WizardUiBridge) -> FteException:
    """Ask for one full-time-equivalent exception period."""
    start_date = _ask_date(ui_bridge, 'Exception start date')
    end_date = _ask_end_date(ui_bridge, 'Exception end date', start_date)
    fte = _ask_number(ui_bridge, 'Full-time equivalent during the period', 1.0,
                      0.0, 1.0)
    return FteException(start_date=start_date, end_date=end_date, fte=fte)
