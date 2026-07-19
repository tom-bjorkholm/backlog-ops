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

from functools import partial
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
from backlogops.wizard_helpers import _backlog_map_fields
from backlogops.wizard_navigator import _Navigator, _ask_level_display
from backlogops.wizard_forms import FormField, FormResult, choice_field, \
    date_field, int_field, number_field, opt_date_field, text_field, \
    unique_name_field, yes_no_field
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


def available_teams_wizard(ui_bridge: WizardUiBridge, *,
                           default: Optional[AvailableTeams] = None,
                           backward: bool = False) -> AvailableTeams:
    """Interactively create an available workforce configuration.

    Args:
        ui_bridge: Bridge between the wizard and the user interface.
        default: Workforce whose values pre-fill the wizard. This can be
            what a configuration file already holds, what the user answered
            before going back in an enclosing wizard, or a starting point
            the application suggests.
        backward: When True, the wizard starts at its last question instead
            of the first. This is set to True when the user asked to go back
            into this wizard from a later question in an enclosing wizard.

    Returns:
        The workforce entered by the user. Field values are individually
        valid, but whole-workforce consistency is only enforced when the
        result is stored.

    Raises:
        EOFError: The input ended, or the user abandoned the wizard.
    """
    navigator = _Navigator(ui_bridge)
    try:
        return navigator.run(_collect_teams, default, backward)
    except WizardAbort as abort:
        raise EOFError('Configuration abandoned by the user.') from abort


def backlog_ops_wizard(ui_bridge: WizardUiBridge, *,
                       default: Optional[BacklogOpsConfig] = None,
                       backward: bool = False) -> BacklogOpsConfig:
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
        default: Configuration whose values pre-fill the wizard. This can be
            what a configuration file already holds, what the user answered
            before going back in an enclosing wizard, or a starting point
            the application suggests.
        backward: When True, the wizard starts at its last question instead
            of the first. This is set to True when the user asked to go back
            into this wizard from a later question in an enclosing wizard.

    Returns:
        The backlog-ops configuration, ready to be written to a file.

    Raises:
        EOFError: The input ended, or the user abandoned the wizard.
    """
    navigator = _Navigator(ui_bridge)
    try:
        return navigator.run(_collect_config, default, backward)
    except WizardAbort as abort:
        raise EOFError('Configuration abandoned by the user.') from abort


def _collect_teams(nav: _Navigator,
                   default: Optional[AvailableTeams]) -> AvailableTeams:
    """Ask for the company, the persons and the teams of a workforce."""
    nav.show(_WORKFORCE_HEAD)
    company = _build_company(nav, default)
    persons = nav.level(lambda: _build_persons(nav, default))
    names = [person.name for person in persons.values()]
    teams = nav.level(lambda: _build_teams(nav, names, default))
    return AvailableTeams(persons=persons, teams=teams,
                          company_work_hours=company)


def _collect_config(nav: _Navigator,
                    default: Optional[BacklogOpsConfig]) -> BacklogOpsConfig:
    """Ask for workforce, TableIO presets, levels and GUI display."""
    teams = _collect_teams(nav, default.available_teams if default else None)
    config = BacklogOpsConfig(available_teams=teams)
    nav.show(_INPUT_PRESETS_HEAD)
    config.input_configs = nav.level(lambda: _build_input_presets(
        nav, default.input_configs if default else None))
    nav.show(_OUTPUT_PRESETS_HEAD)
    config.output_configs = nav.level(lambda: _build_output_presets(
        nav, default.output_configs if default else None))
    nav.show(_LEVELS_HEAD)
    config.levels = _levels_or_none(nav.ask_levels(
        seed=default.levels if default else None))
    nav.show(_STATUS_MAP_HEAD)
    config.status_input_map = nav.ask_status_map(
        _GLOBAL_STATUS_QUESTION, DEF_STATUS_INPUT_MAP,
        seed=default.status_input_map if default else None)
    nav.show(_GUI_DISPLAY_HEAD)
    config.gui_display = _build_gui_display(
        nav, default.gui_display if default else None)
    nav.show(_JIRA_HEAD)
    config.jira = _build_jira_config(nav, config.get_levels(),
                                     default.jira if default else None)
    return config


def _build_gui_display(nav: _Navigator, default: Optional[GuiDisplayConfig]
                       ) -> GuiDisplayConfig:
    """Ask the GUI column renaming and level display, and return it."""
    gui_display = GuiDisplayConfig()
    gui_display.backlog_to_external = nav.level(
        lambda: nav.ask_renames(_backlog_map_fields(), True,
                                _GUI_COLUMN_HEADER,
                                seed=default.backlog_to_external
                                if default else None))
    gui_display.release_to_external = nav.level(
        lambda: nav.ask_renames(list(RELEASE_FIELDS), False,
                                _GUI_COLUMN_HEADER,
                                seed=default.release_to_external
                                if default else None))
    gui_display.level_display = _ask_level_display(
        nav, _GUI_LEVEL_QUESTION, default.level_display if default else None)
    return gui_display


def _levels_or_none(levels: list[Level]) -> Optional[list[Level]]:
    """Return the levels, or None when they match the default levels."""
    if {level.level: level for level in levels} == DEFAULT_LEVELS:
        return None
    return levels


def _build_company(nav: _Navigator,
                   default: Optional[AvailableTeams]) -> CompanyWorkHours:
    """Ask for the company weekly schedule and holiday periods.

    The weekly schedule is one table and the holiday, closure and
    special-work periods are a second table, so the whole company work
    schedule is two screens.
    """
    company = default.company_work_hours if default else None
    work_hours = nav.ask_schedule(seed=company.work_hours if company else None)
    exceptions = nav.ask_exceptions(
        'Company holiday, closure and special-work periods.',
        seed=company.exceptions if company else None)
    return CompanyWorkHours(work_hours=work_hours, exceptions=exceptions)


def _exc_seed(exc: Optional[ExceptionWorkHours]) -> Optional[FormResult]:
    """Return the work-hour exception form values from an exception."""
    if exc is None:
        return None
    return FormResult({'start': exc.start_date, 'end': exc.end_date,
                       'hours': exc.hours_per_day,
                       'new_days': exc.new_work_days})


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


def _ask_exception(nav: _Navigator, seed: Optional[ExceptionWorkHours] = None
                   ) -> ExceptionWorkHours:
    """Ask for one work-hour exception period on a single form."""
    values = nav.ask_form('Configure the work-hour exception period.',
                          _exception_fields(), _period_rule,
                          seed=_exc_seed(seed))
    return ExceptionWorkHours(start_date=values.day('start'),
                              end_date=values.day('end'),
                              hours_per_day=values.number('hours'),
                              new_work_days=values.flag('new_days'))


def _build_persons(nav: _Navigator,
                   default: Optional[AvailableTeams]) -> dict[str, Person]:
    """Ask for a counted list of persons and their exceptions."""
    people = list(default.persons.values()) if default else []
    count = nav.ask_count('Number of persons', seed=len(people))
    persons: dict[str, Person] = {}
    for k in range(count):
        seed = people[k] if k < len(people) else None
        person = nav.level(partial(_ask_person, nav, persons, seed))
        persons[person.name.lower()] = person
    return persons


def _person_fields(taken: set[str]) -> list[FormField]:
    """Return the name and exception-count fields of a person form."""
    return [unique_name_field('name', 'Person name', taken),
            int_field('n_exc', 'Number of vacation or work-hour exceptions',
                      default=0, minimum=0)]


def _person_seed(seed: Optional[Person]) -> Optional[FormResult]:
    """Return the person form values from a person."""
    if seed is None:
        return None
    return FormResult({'name': seed.name, 'n_exc': len(seed.exceptions)})


def _ask_person(nav: _Navigator, persons: dict[str, Person],
                seed: Optional[Person] = None) -> Person:
    """Ask a person's name and exception count, then the exceptions.

    The name and the number of personal work-hour exceptions are one
    form; each exception period is then a separate form.
    """
    values = nav.ask_form('Configure the person.',
                          _person_fields(set(persons)),
                          seed=_person_seed(seed))
    seq = seed.exceptions if seed else []
    exceptions = nav.counted(values.whole('n_exc'), seq,
                             partial(_ask_exception, nav))
    return Person(name=values.text('name'), exceptions=exceptions)


def _build_teams(nav: _Navigator, person_names: list[str],
                 default: Optional[AvailableTeams]) -> list[Team]:
    """Ask for a counted list of teams and their memberships."""
    teams = default.teams if default else []
    count = nav.ask_count('Number of teams', seed=len(teams))
    return [nav.level(partial(_ask_team, nav, person_names,
                              teams[k] if k < len(teams) else None))
            for k in range(count)]


def _team_fields(person_names: list[str],
                 seed: Optional[Team]) -> list[FormField]:
    """Return the fields of the combined team form.

    The team name, the number of members and aliases, the velocity and
    the sprint length are asked together. The member count is capped at
    the number of persons, since a person joins a team at most once. The
    full-time-equivalent sum is asked later, after the members, so it can
    default to the entered member count.
    """
    max_members = len(person_names)
    members = min(len(seed.members), max_members) if seed else 0
    aliases = len(seed.aliases) if seed else 0
    return [
        text_field('name', 'Team name'),
        int_field('members', 'Number of team members', default=members,
                  minimum=0, maximum=max_members),
        int_field('aliases', 'Number of team aliases', default=aliases,
                  minimum=0),
        number_field('velocity', 'Team velocity', default=0.0, minimum=0.0),
        int_field('sprint', 'Sprint length in working days', default=10,
                  minimum=1)]


def _team_seed(team: Optional[Team]) -> Optional[FormResult]:
    """Return the combined team form values from a team."""
    if team is None:
        return None
    return FormResult({'name': team.name, 'members': len(team.members),
                       'aliases': len(team.aliases),
                       'velocity': team.velocity,
                       'sprint': team.sprint_length})


def _ask_team(nav: _Navigator, person_names: list[str],
              seed: Optional[Team] = None) -> Team:
    """Ask for one team on one form, then its members, sum-FTE and aliases.

    The name, member and alias counts, velocity and sprint length are one
    form. The members follow, then the full-time-equivalent sum (which
    defaults to the number of members entered), then the aliases.
    """
    values = nav.ask_form('Configure the team.',
                          _team_fields(person_names, seed),
                          seed=_team_seed(seed))
    members = _build_members(nav, person_names, values.whole('members'),
                             seed.members if seed else [])
    sum_fte = _ask_sum_fte(nav, values.number('velocity'), len(members),
                           seed.sum_fte_at_velocity if seed else None)
    aliases = _build_aliases(nav, values.whole('aliases'),
                             seed.aliases if seed else [])
    return Team(name=values.text('name'), velocity=values.number('velocity'),
                sum_fte_at_velocity=sum_fte,
                sprint_length=values.whole('sprint'), aliases=aliases,
                members=members)


def _ask_sum_fte(nav: _Navigator, velocity: float, member_count: int,
                 seed: Optional[float]) -> float:
    """Ask the sum of full-time equivalents that matches the velocity.

    It defaults to the number of members entered, the common case where
    every member works full time, and its question names the velocity.
    """
    default = seed if seed is not None else float(member_count)
    question = ('Sum of full-time equivalents in this team for the velocity '
                f'of {velocity:g}')
    values = nav.ask_form('Configure the team full-time-equivalent sum.',
                          [number_field('sum_fte', question, default=default)],
                          seed=FormResult({'sum_fte': default}))
    return values.number('sum_fte')


def _build_aliases(nav: _Navigator, count: int, seq: list[str]) -> list[str]:
    """Collect ``count`` team aliases, pre-filled from the seed aliases."""
    def build(seed: Optional[str]) -> str:
        """Ask one team alias, pre-filled from a seed alias."""
        return nav.ask_text('Team alias', seed=seed)
    return nav.counted(count, seq, build)


def _build_members(nav: _Navigator, person_names: list[str], count: int,
                   seq: list[Membership]) -> list[Membership]:
    """Collect ``count`` memberships of distinct persons, seeded when known.

    A person joins a team at most once, so each membership is chosen from
    the persons not yet members of this team; the count is capped at the
    number of persons on the team form.
    """
    available = list(person_names)

    def build(seed: Optional[Membership]) -> Membership:
        """Ask one membership from the remaining persons, then reserve it."""
        member = _ask_membership(nav, available, seed)
        available.remove(member.person_name)
        return member
    return nav.counted(count, seq, build)


def _membership_fields(person_names: list[str]) -> list[FormField]:
    """Return the fields of the one-screen team membership form."""
    return [
        choice_field('person', 'Select the person:', person_names),
        number_field('fte', 'Full-time equivalent in this team', default=1.0,
                     minimum=0.0, maximum=1.0),
        opt_date_field('start', 'Membership start date'),
        opt_date_field('end', 'Membership end date'),
        int_field('n_fte', 'Number of full-time-equivalent exceptions',
                  default=0, minimum=0)]


def _member_seed(member: Optional[Membership]) -> Optional[FormResult]:
    """Return the membership form values from a membership."""
    if member is None:
        return None
    return FormResult({'person': member.person_name, 'fte': member.fte,
                       'start': member.start_date, 'end': member.end_date,
                       'n_fte': len(member.fte_exceptions)})


def _ask_membership(nav: _Navigator, person_names: list[str],
                    seed: Optional[Membership] = None) -> Membership:
    """Ask a membership and its FTE-exception count, then the exceptions.

    The person, full-time equivalent, dates and the number of FTE
    exceptions are one form; each FTE exception period is then a separate
    form.
    """
    values = nav.ask_form('Configure the team membership.',
                          _membership_fields(person_names), _period_rule,
                          seed=_member_seed(seed))
    seq = seed.fte_exceptions if seed else []
    fte_exceptions = nav.counted(values.whole('n_fte'), seq,
                                 partial(_ask_fte_exception, nav))
    return Membership(person_name=values.text('person'),
                      fte=values.number('fte'),
                      start_date=values.opt_day('start'),
                      end_date=values.opt_day('end'),
                      fte_exceptions=fte_exceptions)


def _fte_exception_fields() -> list[FormField]:
    """Return the fields of the one-screen full-time-equivalent form."""
    return [
        date_field('start', 'Exception start date'),
        date_field('end', 'Exception end date'),
        number_field('fte', 'Full-time equivalent during the period',
                     default=1.0, minimum=0.0, maximum=1.0)]


def _fte_seed(exc: Optional[FteException]) -> Optional[FormResult]:
    """Return the full-time-equivalent exception form values."""
    if exc is None:
        return None
    return FormResult({'start': exc.start_date, 'end': exc.end_date,
                       'fte': exc.fte})


def _ask_fte_exception(nav: _Navigator,
                       seed: Optional[FteException] = None) -> FteException:
    """Ask for one full-time-equivalent exception period on a single form."""
    values = nav.ask_form('Configure the full-time-equivalent exception.',
                          _fte_exception_fields(), _period_rule,
                          seed=_fte_seed(seed))
    return FteException(start_date=values.day('start'),
                        end_date=values.day('end'), fte=values.number('fte'))
