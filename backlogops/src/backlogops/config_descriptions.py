#! /usr/local/bin/python3
"""What each configuration member is for, for the configuration editor.

A configuration class carries its own docstring, so the editor of
``edit_cfg_json`` can label a configuration object without being told
anything. A *member* carries nothing at runtime: a string literal written
after an assignment is discarded and an annotation on an instance attribute
is recorded nowhere. This module is therefore where backlog-ops says what
its members are for, as the ``edit_cfg_json.Descriptions`` mappings the
editor takes.

A member is named by the absolute ``config_as_json.ConfigPath`` that
addresses it, and the :data:`EVERY` step stands for every element of a list
and every value of a dict at that point. A selector may cross the boundary
into a nested configuration object, so one mapping describes a whole tree.

The same classes appear in more than one place: an ``InputFormatConfig`` is
both a value of ``input_configs`` and the whole of a stand-alone input
preset file, and a work-hours exception belongs both to a person and to the
company. Each class is therefore described once, relative to itself, and
:func:`prefixed` puts one of those mappings under the path where the class
is used. So every mapping here says the same thing about one member
wherever that member appears, and
:data:`CONFIG_DESCRIPTIONS` is built from the others rather than beside
them.

Nothing the editor works out for itself is repeated here. It reads the
class of a nested configuration object and shows its docstring, the enum
class of a member and shows its summary line and the names it accepts, the
kind of value a member holds, and whether its class may leave it out of the
file. So a text here neither lists the names of an enum, nor spells out
``true`` and ``false``, nor calls a number a number, nor says that a member
may be left out.

What a name means is another matter, and it is the one thing a list of
names does not say. It is written where it is read once for every member
that holds it: in the summary line of the enum class, which is the line the
editor shows and the only line of that docstring it shows. A choice with
more names than fit in one such line has the meaning of them said about the
member instead, which is why ``token_storage`` explains its modes here and
``level_display`` does not.

The nested TableIO endpoint is described by ``tableio_cfg_json``, which
owns those members: :func:`tio_json_descriptions` is asked for their text
under the path of the member holding the endpoint, so the TableIO
documentation is neither repeated here nor able to drift from it. What is
written here about that endpoint is the one line about the member itself.

One more thing is deliberately left out: a limit that lives inside a
validator is not read by the editor and is stated in words where it
matters.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from config_as_json import ConfigPath
from edit_cfg_json import Descriptions
from tableio_cfg_json import tio_json_descriptions

EVERY = '['
"""The path step meaning every element of a list or every value of a dict.

It is the ``config_as_json`` selector step, spelled once here so that a
description path reads as the tree it walks.
"""


def prefixed(prefix: ConfigPath, members: Descriptions) -> Descriptions:
    """Return the descriptions of one class, put where the class is used.

    Args:
        prefix: The path of the member holding that configuration, ending
            with :data:`EVERY` where it holds several of them.
        members: The descriptions of that class, relative to itself.

    Returns:
        The same descriptions, each under the absolute path of its member.
    """
    return {prefix + path: text for path, text in members.items()}


_HOURS_EXCEPTION: Descriptions = {
    ('start_date',): 'First day of the exception, as YYYY-MM-DD.',
    ('end_date',): 'Last day of the exception, as YYYY-MM-DD. Not before '
                   'the first day.',
    ('hours_per_day',): 'Work hours per day during the exception. Zero for '
                        'a holiday or a closed period. Not negative.',
    ('new_work_days',): 'Whether these hours also apply to days the '
                        'schedule gives no work hours, which is what an '
                        'exception for work on a closed day needs. '
                        'Otherwise the exception only changes the days '
                        'that already have work hours.'}
"""Every member of one work-hours exception, of a person or the company."""

_FTE_EXCEPTION: Descriptions = {
    ('start_date',): 'First day of the exception, as YYYY-MM-DD.',
    ('end_date',): 'Last day of the exception, as YYYY-MM-DD. Not before '
                   'the first day.',
    ('fte',): 'Full-time equivalent this person gives the team during the '
              'exception, such as 0.5 for half time. Not negative.'}
"""Every member of one full-time-equivalent exception of a membership."""

_MEMBERSHIP: Descriptions = {
    ('person_name',): 'Name of the person, which must be one of the names '
                      'under persons. Matched without regard to case.',
    ('fte',): 'Full-time equivalent this person gives the team outside the '
              'exceptions below. 1.0 is full time. Not negative.',
    ('start_date',): 'First day of the membership, as YYYY-MM-DD, or empty '
                     'for a membership that was always there.',
    ('end_date',): 'Last day of the membership, as YYYY-MM-DD, or empty '
                   'for a membership that does not end.',
    ('fte_exceptions',): 'Periods where this person gives the team another '
                         'share of their time, such as a learning period. '
                         'The periods must not overlap.'}
"""Every member of one team membership, plus its exception list."""

_TEAM: Descriptions = {
    ('name',): 'Name of the team, as a backlog item names the team that '
               'does it. Unique across the teams, and not empty.',
    ('velocity',): 'Story points the team completes per sprint, as it was '
                   'measured. Not negative.',
    ('sum_fte_at_velocity',): 'Sum of the full-time equivalents of the '
                              'members when that velocity was measured. It '
                              'is what rescales the velocity when the team '
                              'grows or shrinks, so it must be positive.',
    ('sprint_length',): 'Length of one sprint in working days, not calendar '
                        'days. Must be positive.',
    ('aliases',): 'Other names a backlog may use for this team. Each is '
                  'unique across the teams and matched without case.',
    ('members',): 'Who is in the team, and for how much of their time. One '
                  'person may be in several teams, and over several '
                  'periods of time.'}
"""Every member of one team, plus its alias and membership lists."""

_PERSON: Descriptions = {
    ('name',): 'Name of the person. The key of this entry must be this '
               'name in lower case.',
    ('exceptions',): 'Periods where this person works other hours than the '
                     'company schedule: vacation, part time, or ordered '
                     'over-time. The company periods apply as well and are '
                     'not repeated here. The periods must not overlap.'}
"""Every member of one person, plus their work-hours exception list."""

_WORKFORCE: Descriptions = {
    ('persons',): 'Everybody who works on this backlog, keyed by their '
                  'name in lower case. A person is here once, however many '
                  'teams they are in.',
    ('teams',): 'The teams that do the work, in no particular order. A '
                'backlog item names its team by the team name or an alias.',
    ('company_work_hours',): 'The working week and the days the whole '
                             'company is closed, which is what every '
                             "person's own hours are counted against.",
    ('company_work_hours', 'work_hours'): 'Work hours of each week day, '
                                          'keyed by the day name in upper '
                                          'case. Every day of the week has '
                                          'an entry, and a day nobody works '
                                          'has zero.',
    ('company_work_hours', 'exceptions'): 'National holidays, company-wide '
                                          'vacations, and every other '
                                          'period the company works other '
                                          'hours. The periods must not '
                                          'overlap.'}
"""Every member of the workforce, without the lists it holds."""

WORKFORCE_DESCRIPTIONS: Descriptions = {
    **_WORKFORCE,
    **prefixed(('persons', EVERY), _PERSON),
    **prefixed(('persons', EVERY, 'exceptions', EVERY), _HOURS_EXCEPTION),
    **prefixed(('company_work_hours', 'exceptions', EVERY), _HOURS_EXCEPTION),
    **prefixed(('teams', EVERY), _TEAM),
    **prefixed(('teams', EVERY, 'members', EVERY), _MEMBERSHIP),
    **prefixed(('teams', EVERY, 'members', EVERY, 'fte_exceptions', EVERY),
               _FTE_EXCEPTION)}
"""What every member of an ``AvailableTeamsConfig`` is for."""

_TABLEIO: Descriptions = {
    ('tableio',): 'How the file itself is read or written: its format, and '
                  'the settings of that format. A setting that is not in '
                  'the file keeps its default and has no line here.',
    **tio_json_descriptions(('tableio',))}
"""What the nested TableIO endpoint of one preset and its settings are for.

Only the line about the member itself is written here. Everything below it
belongs to ``tableio_cfg_json``, which is asked for it, so the formats,
implementations and values named are the ones registered now.
"""

_MAPPED_COLUMN = ('Empty drops the column altogether. A column that is not '
                  'named here keeps its own name.')
"""What one entry of a column-name map means, beyond being a rename."""

INPUT_DESCRIPTIONS: Descriptions = {
    ('backlog_to_internal',): 'What the backlog columns of the file are '
                              'called, keyed by the file column name and '
                              'naming the internal field it is read into. '
                              'Several file columns may be read into one '
                              'internal field.',
    ('backlog_to_internal', EVERY): 'Internal field this file column is '
                                    f'read into. {_MAPPED_COLUMN}',
    ('release_to_internal',): 'The same for the releases table of the file.',
    ('release_to_internal', EVERY): 'Internal field this file column is '
                                    f'read into. {_MAPPED_COLUMN}',
    ('status_input_map',): 'Extra status names this file uses, keyed by the '
                           'name in the file. They are matched without '
                           'regard to case, and they override the status '
                           'map of the whole configuration for this preset '
                           'alone.',
    ('status_input_map', EVERY): 'Internal status this name is read as: one '
                                 'of TODO, IN_PROGRESS, DONE or REJECTED.',
    **_TABLEIO}
"""What every member of an ``InputFormatConfig`` is for."""


def _display_members(action: str) -> Descriptions:
    """Return what the column maps and the level display say about a part.

    An output preset writes these columns to a file and the display shows
    them on a screen, so the one word that differs between the two is a
    parameter and everything else is said once.

    Args:
        action: What becomes of a column here, as a past participle:
            ``'written'`` for an output preset, ``'shown'`` for a display.

    Returns:
        The descriptions of those members, relative to the class.
    """
    column = f'Column name this internal field is {action} under. ' \
        f'{_MAPPED_COLUMN}'
    return {
        ('backlog_to_external',): 'What the backlog columns are called when '
                                  f'they are {action}, keyed by the internal '
                                  'field name and naming the column name to '
                                  'use.',
        ('backlog_to_external', EVERY): column,
        ('release_to_external',): 'The same for the releases table.',
        ('release_to_external', EVERY): column,
        ('level_display',): 'Which columns the level of a backlog item is '
                            f'{action} in.'}


OUTPUT_DESCRIPTIONS: Descriptions = {**_display_members('written'),
                                     **_TABLEIO}
"""What every member of an ``OutputFormatConfig`` is for."""

GUI_DESCRIPTIONS: Descriptions = _display_members('shown')
"""What every member of a ``GuiDisplayConfig`` is for.

The same members as an output preset, without the TableIO endpoint, and
said of showing a column rather than of writing one, because the graphical
interface shows the tables rather than writing them.
"""

_CONNECTION: Descriptions = {
    ('base_url',): 'Address of the Jira server, such as '
                   'https://example.atlassian.net',
    ('login_email',): 'Email address the API token belongs to.',
    ('token_storage',): 'A clear mode keeps the token unprotected and is '
                        'meant for demonstration data only, while an '
                        'encrypted mode asks for a pass phrase whenever the '
                        'token is stored and whenever it is used. A file '
                        'mode keeps the token in the file named below, an '
                        'internal mode in this configuration itself.',
    ('token_file_path',): 'File holding the token, for a file storage mode. '
                          'Empty for an internal storage mode.',
    ('stored_token',): 'The token itself, for an internal storage mode: '
                       'encrypted text for an encrypted mode and the token '
                       'as it is for a clear mode. Empty for a file storage '
                       'mode. It is written by the wizard and by the token '
                       'encryption command rather than typed here.'}
"""Every member of one Jira connection."""

_JIRA_PRESET: Descriptions = {
    ('connection_name',): 'Name of the connection this preset uses, from '
                          'the connections above.',
    ('backlog_column_map_name',): 'Name of the backlog column map used to '
                                  'read, from the backlog column maps '
                                  'above.',
    ('release_column_map_name',): 'Name of the release column map, from the '
                                  'release column maps above.',
    ('backlog_write_map_name',): 'Name of the backlog column map used to '
                                 'write, when writing needs another one. '
                                 'Empty writes through the map used to read.',
    ('issue_type_map_name',): 'Name of the level-to-issue-type map used to '
                              'write, from the issue type maps above. Empty '
                              'writes each level under its own name.',
    ('def_project',): 'Jira project key this preset works in, such as ABC. '
                      'The releases are read from this project even when '
                      'the filter below is overridden.',
    ('def_filter',): 'Jira Query Language filter selecting the issues to '
                     'read, such as project = "ABC" ORDER BY rank ASC.'}
"""Every member of one Jira preset."""

JIRA_DESCRIPTIONS: Descriptions = {
    ('connections',): 'The Jira servers this configuration can reach, by a '
                      'name of your own. Several presets may share one.',
    ('backlog_column_maps',): 'Where the value of each backlog field is '
                              'found on a Jira issue, by a name of your '
                              'own. A preset names the map it uses.',
    ('backlog_column_maps', EVERY): 'One map, keyed by the internal backlog '
                                    'field name. An internal field that is '
                                    'not here is not read.',
    ('backlog_column_maps', EVERY, EVERY): 'Where that field is found: the '
                                           'kind (ATTRIBUTE, FIELD, '
                                           'CUSTOM_FIELD or FILTERED_FIELD) '
                                           'and then the path steps.',
    ('release_column_maps',): 'The same for the fields of a release, which '
                              'is a version in Jira.',
    ('release_column_maps', EVERY): 'One map, keyed by the internal release '
                                    'field name.',
    ('release_column_maps', EVERY, EVERY): 'Where that field is found: the '
                                           'kind and then the path steps.',
    ('issue_type_maps',): 'Which Jira issue type to create for a level, by '
                          'a name of your own. Used only when writing.',
    ('issue_type_maps', EVERY): 'One map, keyed by the level number as '
                                'text. A level that is not here is written '
                                'under its own name.',
    ('issue_type_maps', EVERY, EVERY): 'Jira issue type created for that '
                                       'level, such as Deluppgift.',
    ('presets',): 'The named presets, each tying the sections above '
                  'together. A preset name is what a command asks for '
                  'with -p.',
    **prefixed(('connections', EVERY), _CONNECTION),
    **prefixed(('presets', EVERY), _JIRA_PRESET)}
"""What every member of a ``JiraIOConfig`` is for."""

_LEVEL: Descriptions = {
    ('level',): 'A higher number is a bigger item, so a story is above a '
                'sub-task. Used once across the levels.',
    ('name',): 'Name of the level, such as Story. Unique across the levels '
               'and their aliases, and not empty.',
    ('aliases',): 'Other names for this level, as another tool may call it. '
                  'Each is unique across the levels and their aliases.'}
"""Every member of one backlog item level."""

_TOP_LEVEL: Descriptions = {
    ('available_teams',): 'Who does the work: the persons, the teams, and '
                          'the working week of the company. This is what an '
                          'estimate is calculated from.',
    ('input_configs',): 'Named input presets, each saying how to read a '
                        'backlog file. A preset name is what a command asks '
                        'for with -I.',
    ('output_configs',): 'Named output presets, each saying how to write a '
                         'backlog file. A preset name is what a command '
                         'asks for with -O.',
    ('gui_display',): 'What the graphical interface shows. A written file '
                      'follows its output preset above instead.',
    ('status_input_map',): 'Status names as files and Jira use them, keyed '
                           'by that name and matched without regard to '
                           'case. An input preset may override an entry for '
                           'itself.',
    ('status_input_map', EVERY): 'Internal status this name is read as: one '
                                 'of TODO, IN_PROGRESS, DONE or REJECTED.',
    ('jira',): 'Everything about Jira. A backlog kept in files alone needs '
               'none of it.',
    ('levels',): 'The levels of a backlog item, from the smallest upwards. '
                 'Without them the built-in levels are used: Sub-Task, '
                 'Story, Epic and Initiative.'}
"""What every member of the top-level configuration is for."""

CONFIG_DESCRIPTIONS: Descriptions = {
    **_TOP_LEVEL,
    **prefixed(('available_teams',), WORKFORCE_DESCRIPTIONS),
    **prefixed(('input_configs', EVERY), INPUT_DESCRIPTIONS),
    **prefixed(('output_configs', EVERY), OUTPUT_DESCRIPTIONS),
    **prefixed(('gui_display',), GUI_DESCRIPTIONS),
    **prefixed(('jira',), JIRA_DESCRIPTIONS),
    **prefixed(('levels', EVERY), _LEVEL)}
"""What every member of a ``BacklogOpsConfig`` is for.

One mapping for the whole tree, because a description selector crosses the
boundary into a nested configuration object. It is built from the mapping
of each class, so a member says the same thing here as it does in the
stand-alone preset file that holds the same class.
"""
