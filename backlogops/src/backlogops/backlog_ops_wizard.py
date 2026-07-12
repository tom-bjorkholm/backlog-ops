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
from backlogops.backlog_ops_config import BacklogOpsConfig, \
    DEF_STATUS_INPUT_MAP
from backlogops.io_config import GuiDisplayConfig
from backlogops.levels import DEFAULT_LEVELS, Level
from backlogops.person import Person
from backlogops.table_rows import RELEASE_FIELDS
from backlogops.team import FteException, Membership, Team
from backlogops.work_hours import CompanyWorkHours, ExceptionWorkHours
from backlogops.wizard_helpers import _Navigator, _ask_level_display, \
    _backlog_map_fields
from backlogops.wizard_forms import FormField, FormResult, choice_field, \
    date_field, int_field, number_field, opt_date_field, yes_no_field
from backlogops.io_preset_wizard import _build_input_presets, \
    _build_output_presets
from backlogops.jira_wizard import _build_jira_config


_GUI_LEVEL_QUESTION = \
    'How to show levels in the GUI (numeric, name or both)'
"""Wizard prompt for how the GUI shows levels."""


_GUI_COLUMN_HEADER = 'Shown column (blank hides it)'
"""Header of the renamed-column column in a GUI rename table."""


_GLOBAL_STATUS_QUESTION = 'Global extra status name mapping (all inputs):'
"""Wizard prompt for the library-wide status-name map."""


_WORKFORCE_HEAD = 'Configure the available workforce.'
"""Stage heading shown while collecting the workforce."""


_INPUT_PRESETS_HEAD = 'Configure the named input configurations.'
"""Stage heading shown while collecting the input presets."""


_OUTPUT_PRESETS_HEAD = 'Configure the named output configurations.'
"""Stage heading shown while collecting the output presets."""


_LEVELS_HEAD = 'Configure the backlog item levels.'
"""Stage heading shown while collecting the backlog item levels."""


_STATUS_MAP_HEAD = 'Configure the global status name mapping.'
"""Stage heading shown while collecting the global status map."""


_GUI_DISPLAY_HEAD = 'Configure the GUI display.'
"""Stage heading shown while collecting the GUI display."""


_JIRA_HEAD = 'Configure the Jira integration.'
"""Stage heading shown while collecting the Jira configuration."""


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
    rather than written out. Finally the user may configure the Jira
    integration: named connections, column maps and from-Jira read presets.

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
    nav.show(_WORKFORCE_HEAD)
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
    nav.show(_INPUT_PRESETS_HEAD)
    config.input_configs = nav.level(lambda: _build_input_presets(nav))
    nav.show(_OUTPUT_PRESETS_HEAD)
    config.output_configs = nav.level(lambda: _build_output_presets(nav))
    nav.show(_LEVELS_HEAD)
    config.levels = _levels_or_none(nav.ask_levels())
    nav.show(_STATUS_MAP_HEAD)
    config.status_input_map = nav.ask_status_map(_GLOBAL_STATUS_QUESTION,
                                                 DEF_STATUS_INPUT_MAP)
    nav.show(_GUI_DISPLAY_HEAD)
    config.gui_display = _build_gui_display(nav)
    nav.show(_JIRA_HEAD)
    config.jira = _build_jira_config(nav, config.get_levels())
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


def _period_rule(values: FormResult) -> tuple[Optional[str], set[str]]:
    """Reject an end date that falls before its start date."""
    start = values.opt_day('start')
    end = values.opt_day('end')
    if start is not None and end is not None and end < start:
        return 'The end date must not be before the start date.', set()
    return None, set()


def _exception_fields() -> list[FormField]:
    """Return the fields of the one-screen work-hour exception form."""
    return [
        date_field('start', 'Start date'),
        date_field('end', 'End date'),
        number_field('hours', 'Work hours per day during the period',
                     default=0.0, minimum=0.0),
        yes_no_field('new_days', 'Does this add work on days that are '
                     'normally free?', False)]


def _ask_exception(nav: _Navigator) -> ExceptionWorkHours:
    """Ask for one work-hour exception period on a single form."""
    values = nav.ask_form('Configure the work-hour exception period.',
                          _exception_fields(), _period_rule)
    return ExceptionWorkHours(start_date=values.day('start'),
                              end_date=values.day('end'),
                              hours_per_day=values.number('hours'),
                              new_work_days=values.flag('new_days'))


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


def _team_fields(member_count: int) -> list[FormField]:
    """Return the velocity, capacity and sprint fields of a team form.

    The full-time-equivalent sum defaults to the number of members, the
    common case where every member works full time.
    """
    return [
        number_field('velocity', 'Team velocity', default=0.0, minimum=0.0),
        number_field('sum_fte', 'Sum of full-time equivalents at that '
                     'velocity', default=float(member_count)),
        int_field('sprint', 'Sprint length in working days', default=10,
                  minimum=1)]


def _ask_team(nav: _Navigator, person_names: list[str]) -> Team:
    """Ask for one team and its memberships.

    The team members are asked first, then the velocity, the matching
    full-time-equivalent sum and the sprint length together on one form.
    """
    name = nav.ask_text('Team name')
    members = nav.level(lambda: _build_members(nav, person_names))
    params = nav.ask_form('Configure the team velocity and sprint.',
                          _team_fields(len(members)))
    aliases = nav.level(lambda: _build_aliases(nav))
    return Team(name=name, velocity=params.number('velocity'),
                sum_fte_at_velocity=params.number('sum_fte'),
                sprint_length=params.whole('sprint'), aliases=aliases,
                members=members)


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


def _membership_fields(person_names: list[str]) -> list[FormField]:
    """Return the fields of the one-screen team membership form."""
    return [
        choice_field('person', 'Select the person:', person_names),
        number_field('fte', 'Full-time equivalent in this team', default=1.0,
                     minimum=0.0, maximum=1.0),
        opt_date_field('start', 'Membership start date'),
        opt_date_field('end', 'Membership end date')]


def _ask_membership(nav: _Navigator, person_names: list[str]) -> Membership:
    """Ask for one team membership on a form, then its FTE exceptions."""
    values = nav.ask_form('Configure the team membership.',
                          _membership_fields(person_names), _period_rule)
    fte_exceptions = nav.level(lambda: _build_fte_exceptions(nav))
    return Membership(person_name=values.text('person'),
                      fte=values.number('fte'),
                      start_date=values.opt_day('start'),
                      end_date=values.opt_day('end'),
                      fte_exceptions=fte_exceptions)


def _build_fte_exceptions(nav: _Navigator) -> list[FteException]:
    """Ask for a counted list of full-time-equivalent exception periods."""
    count = nav.ask_count('Number of full-time-equivalent exceptions')
    return [nav.level(lambda: _ask_fte_exception(nav)) for _ in range(count)]


def _fte_exception_fields() -> list[FormField]:
    """Return the fields of the one-screen full-time-equivalent form."""
    return [
        date_field('start', 'Exception start date'),
        date_field('end', 'Exception end date'),
        number_field('fte', 'Full-time equivalent during the period',
                     default=1.0, minimum=0.0, maximum=1.0)]


def _ask_fte_exception(nav: _Navigator) -> FteException:
    """Ask for one full-time-equivalent exception period on a single form."""
    values = nav.ask_form('Configure the full-time-equivalent exception.',
                          _fte_exception_fields(), _period_rule)
    return FteException(start_date=values.day('start'),
                        end_date=values.day('end'), fte=values.number('fte'))
