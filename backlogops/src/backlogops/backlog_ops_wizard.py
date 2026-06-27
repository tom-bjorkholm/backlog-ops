#! /usr/local/bin/python3
"""Interactively build a workforce or a full backlog-ops configuration.

The public helpers :func:`available_teams_wizard` and
:func:`backlog_ops_wizard` ask the user for the company work hours, the
persons and their personal work-hour exceptions, the teams with their
members, and, for the full configuration, the named TableIO presets, the
backlog item levels and the GUI display. They drive any ``WizardUiBridge``
of ``tableio_cfg_json``, so the same wizard logic runs on a console text
interface, a Textual full-screen interface or a graphical user interface.

Each repeated part is asked by first requesting a count and then collecting
exactly that many items, so there are no open-ended "add another?" prompts.
The navigation machinery and the per-field readers live in
:mod:`backlogops.wizard_helpers`; the input and output preset questions live
in :mod:`backlogops.io_preset_wizard`.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional
from tableio_cfg_json import WizardAbort, WizardUiBridge
from backlogops.available_teams import AvailableTeams
from backlogops.backlog_ops_config import BacklogOpsConfig
from backlogops.io_config import GuiDisplayConfig
from backlogops.levels import DEFAULT_LEVELS, Level
from backlogops.person import Person
from backlogops.table_rows import RELEASE_FIELDS
from backlogops.team import FteException, Membership, Team
from backlogops.work_hours import CompanyWorkHours, ExceptionWorkHours
from backlogops.wizard_helpers import _Navigator, _ask_level_display, \
    _backlog_map_fields
from backlogops.io_preset_wizard import _build_input_presets, \
    _build_output_presets


_GUI_LEVEL_QUESTION = \
    'How to show levels in the GUI (numeric, name or both)'
"""Wizard prompt for how the GUI shows levels."""


_GUI_COLUMN_HEADER = 'Shown column (blank hides it)'
"""Header of the renamed-column column in a GUI rename table."""


_GLOBAL_STATUS_QUESTION = 'Global extra status name mapping (all inputs):'
"""Wizard prompt for the library-wide status-name map."""


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


def backlog_ops_wizard(ui_bridge: WizardUiBridge) -> BacklogOpsConfig:
    """Interactively create a backlog-ops configuration.

    The workforce is entered as by :func:`available_teams_wizard`, the
    user may then add any number of named input and output TableIO
    configuration presets, edit the backlog item levels, and finally
    choose how the GUI renames columns and shows levels. Each input preset
    asks how it reads the backlog and releases file columns into the
    internal fields, and each output preset asks how it renames those
    columns and how levels are written; the column tables start pre-filled
    with the internal field names so leaving them unchanged renames
    nothing. The levels start filled in with the default levels; when the
    user leaves them at the defaults they are stored as "use the defaults"
    rather than written out.

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
    """Ask for workforce, TableIO presets, levels and GUI display."""
    teams = _collect_teams(nav)
    config = BacklogOpsConfig(available_teams=teams)
    config.input_configs = nav.level(lambda: _build_input_presets(nav))
    config.output_configs = nav.level(lambda: _build_output_presets(nav))
    config.levels = _levels_or_none(nav.ask_levels())
    config.status_input_map = nav.ask_status_map(_GLOBAL_STATUS_QUESTION)
    config.gui_display = _build_gui_display(nav)
    return config


def _build_gui_display(nav: _Navigator) -> GuiDisplayConfig:
    """Ask the GUI column renaming and level display, and return it."""
    gui_display = GuiDisplayConfig()
    gui_display.backlog_to_external = nav.level(
        lambda: nav.ask_renames(_backlog_map_fields(), True,
                                _GUI_COLUMN_HEADER))
    gui_display.release_to_external = nav.level(
        lambda: nav.ask_renames(list(RELEASE_FIELDS), False,
                                _GUI_COLUMN_HEADER))
    gui_display.level_display = _ask_level_display(nav, _GUI_LEVEL_QUESTION)
    return gui_display


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
