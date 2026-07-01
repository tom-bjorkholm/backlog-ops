# Table of Contents

* [backlogops.available\_teams](#backlogops.available_teams)
  * [membership\_fte\_on](#backlogops.available_teams.membership_fte_on)
  * [candidate\_days](#backlogops.available_teams.candidate_days)
  * [check\_person\_capacity](#backlogops.available_teams.check_person_capacity)
  * [AvailableTeams](#backlogops.available_teams.AvailableTeams)
    * [check\_consistency](#backlogops.available_teams.AvailableTeams.check_consistency)
* [backlogops.apply\_format\_rules](#backlogops.apply_format_rules)
  * [format\_backlog](#backlogops.apply_format_rules.format_backlog)
  * [format\_releases](#backlogops.apply_format_rules.format_releases)
* [backlogops.backlog\_helpers](#backlogops.backlog_helpers)
  * [FORBIDDEN\_KEY\_CHARS](#backlogops.backlog_helpers.FORBIDDEN_KEY_CHARS)
  * [CONTROL\_CHAR\_NAMES](#backlogops.backlog_helpers.CONTROL_CHAR_NAMES)
  * [field\_type\_hints](#backlogops.backlog_helpers.field_type_hints)
  * [is\_mandatory\_field](#backlogops.backlog_helpers.is_mandatory_field)
  * [enum\_class\_of](#backlogops.backlog_helpers.enum_class_of)
  * [is\_union\_type](#backlogops.backlog_helpers.is_union_type)
  * [non\_optional\_type](#backlogops.backlog_helpers.non_optional_type)
  * [accepts\_none](#backlogops.backlog_helpers.accepts_none)
  * [value\_matches\_type](#backlogops.backlog_helpers.value_matches_type)
  * [report\_missing\_field](#backlogops.backlog_helpers.report_missing_field)
  * [report\_wrong\_type](#backlogops.backlog_helpers.report_wrong_type)
  * [report\_bad\_value](#backlogops.backlog_helpers.report_bad_value)
  * [report\_unknown\_reference](#backlogops.backlog_helpers.report_unknown_reference)
  * [check\_field\_types](#backlogops.backlog_helpers.check_field_types)
  * [convert\_to\_enum](#backlogops.backlog_helpers.convert_to_enum)
  * [convert\_to\_date](#backlogops.backlog_helpers.convert_to_date)
  * [convert\_to\_str](#backlogops.backlog_helpers.convert_to_str)
  * [convert\_field\_value](#backlogops.backlog_helpers.convert_field_value)
  * [is\_extra\_field\_map](#backlogops.backlog_helpers.is_extra_field_map)
  * [extra\_field\_name](#backlogops.backlog_helpers.extra_field_name)
  * [collect\_extra\_values](#backlogops.backlog_helpers.collect_extra_values)
  * [build\_item\_kwargs](#backlogops.backlog_helpers.build_item_kwargs)
  * [construct](#backlogops.backlog_helpers.construct)
  * [check\_key\_syntax](#backlogops.backlog_helpers.check_key_syntax)
  * [check\_label\_syntax](#backlogops.backlog_helpers.check_label_syntax)
  * [find\_cycle](#backlogops.backlog_helpers.find_cycle)
* [backlogops.key\_list\_io](#backlogops.key_list_io)
  * [TEXT\_EXTENSIONS](#backlogops.key_list_io.TEXT_EXTENSIONS)
  * [KEY\_COLUMN\_NAME](#backlogops.key_list_io.KEY_COLUMN_NAME)
  * [read\_key\_list](#backlogops.key_list_io.read_key_list)
  * [write\_key\_list](#backlogops.key_list_io.write_key_list)
* [backlogops.person](#backlogops.person)
  * [Person](#backlogops.person.Person)
    * [name](#backlogops.person.Person.name)
    * [exceptions](#backlogops.person.Person.exceptions)
* [backlogops.backlog\_releases](#backlogops.backlog_releases)
  * [BacklogReleases](#backlogops.backlog_releases.BacklogReleases)
    * [add\_to\_releases](#backlogops.backlog_releases.BacklogReleases.add_to_releases)
    * [check\_in\_releases](#backlogops.backlog_releases.BacklogReleases.check_in_releases)
    * [update\_releases](#backlogops.backlog_releases.BacklogReleases.update_releases)
    * [check\_release\_xref](#backlogops.backlog_releases.BacklogReleases.check_release_xref)
    * [check\_consistency](#backlogops.backlog_releases.BacklogReleases.check_consistency)
    * [move\_keys\_first](#backlogops.backlog_releases.BacklogReleases.move_keys_first)
    * [order\_by\_dependencies](#backlogops.backlog_releases.BacklogReleases.order_by_dependencies)
    * [estimate\_ready\_date](#backlogops.backlog_releases.BacklogReleases.estimate_ready_date)
    * [set\_plan\_from\_estimate](#backlogops.backlog_releases.BacklogReleases.set_plan_from_estimate)
    * [adjust\_release\_content](#backlogops.backlog_releases.BacklogReleases.adjust_release_content)
    * [release\_plan\_on\_estimate](#backlogops.backlog_releases.BacklogReleases.release_plan_on_estimate)
    * [order\_releases\_by\_date](#backlogops.backlog_releases.BacklogReleases.order_releases_by_date)
    * [backlog\_in\_release\_order](#backlogops.backlog_releases.BacklogReleases.backlog_in_release_order)
* [backlogops.demo\_backlog](#backlogops.demo_backlog)
  * [get\_demo\_backlog](#backlogops.demo_backlog.get_demo_backlog)
* [backlogops.no\_text\_io](#backlogops.no_text_io)
  * [NoTextIO](#backlogops.no_text_io.NoTextIO)
    * [write](#backlogops.no_text_io.NoTextIO.write)
    * [writelines](#backlogops.no_text_io.NoTextIO.writelines)
    * [flush](#backlogops.no_text_io.NoTextIO.flush)
    * [close](#backlogops.no_text_io.NoTextIO.close)
    * [seek](#backlogops.no_text_io.NoTextIO.seek)
    * [tell](#backlogops.no_text_io.NoTextIO.tell)
    * [truncate](#backlogops.no_text_io.NoTextIO.truncate)
* [backlogops.release\_change\_io](#backlogops.release_change_io)
  * [CONTENT\_HEADER](#backlogops.release_change_io.CONTENT_HEADER)
  * [DATE\_HEADER](#backlogops.release_change_io.DATE_HEADER)
  * [format\_content\_changes](#backlogops.release_change_io.format_content_changes)
  * [format\_date\_changes](#backlogops.release_change_io.format_date_changes)
  * [write\_content\_changes](#backlogops.release_change_io.write_content_changes)
  * [write\_date\_changes](#backlogops.release_change_io.write_date_changes)
* [backlogops.backlog\_ops\_config](#backlogops.backlog_ops_config)
  * [BacklogOpsConfig](#backlogops.backlog_ops_config.BacklogOpsConfig)
    * [\_\_init\_\_](#backlogops.backlog_ops_config.BacklogOpsConfig.__init__)
    * [nested\_configs](#backlogops.backlog_ops_config.BacklogOpsConfig.nested_configs)
    * [get\_validation\_plan](#backlogops.backlog_ops_config.BacklogOpsConfig.get_validation_plan)
    * [serialize\_converters](#backlogops.backlog_ops_config.BacklogOpsConfig.serialize_converters)
    * [check\_consistency](#backlogops.backlog_ops_config.BacklogOpsConfig.check_consistency)
    * [get\_levels](#backlogops.backlog_ops_config.BacklogOpsConfig.get_levels)
    * [get\_status\_input\_map](#backlogops.backlog_ops_config.BacklogOpsConfig.get_status_input_map)
    * [get\_gui\_level\_display](#backlogops.backlog_ops_config.BacklogOpsConfig.get_gui_level_display)
    * [get\_jira\_config](#backlogops.backlog_ops_config.BacklogOpsConfig.get_jira_config)
  * [write\_backlog\_ops\_config](#backlogops.backlog_ops_config.write_backlog_ops_config)
  * [read\_backlog\_ops\_config](#backlogops.backlog_ops_config.read_backlog_ops_config)
  * [get\_backlog\_ops\_config](#backlogops.backlog_ops_config.get_backlog_ops_config)
* [backlogops.table\_create](#backlogops.table_create)
  * [allow\_overwrite](#backlogops.table_create.allow_overwrite)
  * [create\_output\_table](#backlogops.table_create.create_output_table)
* [backlogops.jira\_io\_config](#backlogops.jira_io_config)
  * [JiraType](#backlogops.jira_io_config.JiraType)
  * [TokenStorage](#backlogops.jira_io_config.TokenStorage)
  * [CLEAR\_TOKEN\_WARNING](#backlogops.jira_io_config.CLEAR_TOKEN_WARNING)
  * [JiraAttrType](#backlogops.jira_io_config.JiraAttrType)
  * [JiraAttrPath](#backlogops.jira_io_config.JiraAttrPath)
  * [DEF\_BACKLOG\_COLUMN\_MAP](#backlogops.jira_io_config.DEF_BACKLOG_COLUMN_MAP)
  * [DEF\_RELEASE\_COLUMN\_MAP](#backlogops.jira_io_config.DEF_RELEASE_COLUMN_MAP)
  * [default\_jira\_filter](#backlogops.jira_io_config.default_jira_filter)
  * [JiraConnectConfig](#backlogops.jira_io_config.JiraConnectConfig)
    * [\_\_init\_\_](#backlogops.jira_io_config.JiraConnectConfig.__init__)
    * [parse\_converters](#backlogops.jira_io_config.JiraConnectConfig.parse_converters)
    * [get\_validation\_plan](#backlogops.jira_io_config.JiraConnectConfig.get_validation_plan)
    * [uses\_token\_file](#backlogops.jira_io_config.JiraConnectConfig.uses_token_file)
    * [uses\_encryption](#backlogops.jira_io_config.JiraConnectConfig.uses_encryption)
    * [has\_cached\_token](#backlogops.jira_io_config.JiraConnectConfig.has_cached_token)
    * [get\_token](#backlogops.jira_io_config.JiraConnectConfig.get_token)
    * [set\_token](#backlogops.jira_io_config.JiraConnectConfig.set_token)
  * [JiraPreset](#backlogops.jira_io_config.JiraPreset)
    * [\_\_init\_\_](#backlogops.jira_io_config.JiraPreset.__init__)
    * [get\_validation\_plan](#backlogops.jira_io_config.JiraPreset.get_validation_plan)
  * [JiraIOConfig](#backlogops.jira_io_config.JiraIOConfig)
    * [\_\_init\_\_](#backlogops.jira_io_config.JiraIOConfig.__init__)
    * [nested\_configs](#backlogops.jira_io_config.JiraIOConfig.nested_configs)
    * [get\_validation\_plan](#backlogops.jira_io_config.JiraIOConfig.get_validation_plan)
    * [serialize\_converters](#backlogops.jira_io_config.JiraIOConfig.serialize_converters)
    * [check\_consistency](#backlogops.jira_io_config.JiraIOConfig.check_consistency)
    * [get\_preset](#backlogops.jira_io_config.JiraIOConfig.get_preset)
* [backlogops.team](#backlogops.team)
  * [FteException](#backlogops.team.FteException)
    * [check\_consistency](#backlogops.team.FteException.check_consistency)
  * [Membership](#backlogops.team.Membership)
    * [check\_consistency](#backlogops.team.Membership.check_consistency)
  * [Team](#backlogops.team.Team)
    * [check\_consistency](#backlogops.team.Team.check_consistency)
* [backlogops.backlog](#backlogops.backlog)
  * [DEPENDENCY\_FIELDS](#backlogops.backlog.DEPENDENCY_FIELDS)
  * [Status](#backlogops.backlog.Status)
  * [BacklogItem](#backlogops.backlog.BacklogItem)
    * [to\_dict](#backlogops.backlog.BacklogItem.to_dict)
    * [check\_consistency](#backlogops.backlog.BacklogItem.check_consistency)
  * [prepare\_item\_data](#backlogops.backlog.prepare_item_data)
  * [get\_backlog\_item](#backlogops.backlog.get_backlog_item)
  * [get\_backlog](#backlogops.backlog.get_backlog)
  * [check\_unique\_keys](#backlogops.backlog.check_unique_keys)
  * [check\_key\_references](#backlogops.backlog.check_key_references)
  * [event\_start](#backlogops.backlog.event_start)
  * [event\_finish](#backlogops.backlog.event_finish)
  * [item\_dependency\_edges](#backlogops.backlog.item_dependency_edges)
  * [build\_dependency\_graph](#backlogops.backlog.build_dependency_graph)
  * [check\_no\_cycles](#backlogops.backlog.check_no_cycles)
  * [check\_parent\_levels](#backlogops.backlog.check_parent_levels)
  * [check\_backlog\_consistency](#backlogops.backlog.check_backlog_consistency)
* [backlogops.available\_teams\_config](#backlogops.available_teams_config)
  * [FteExceptionConfig](#backlogops.available_teams_config.FteExceptionConfig)
    * [\_\_init\_\_](#backlogops.available_teams_config.FteExceptionConfig.__init__)
    * [get\_validation\_plan](#backlogops.available_teams_config.FteExceptionConfig.get_validation_plan)
    * [serialize\_converters](#backlogops.available_teams_config.FteExceptionConfig.serialize_converters)
  * [ExceptionWorkHoursConfig](#backlogops.available_teams_config.ExceptionWorkHoursConfig)
    * [\_\_init\_\_](#backlogops.available_teams_config.ExceptionWorkHoursConfig.__init__)
    * [get\_validation\_plan](#backlogops.available_teams_config.ExceptionWorkHoursConfig.get_validation_plan)
    * [serialize\_converters](#backlogops.available_teams_config.ExceptionWorkHoursConfig.serialize_converters)
  * [MembershipConfig](#backlogops.available_teams_config.MembershipConfig)
    * [\_\_init\_\_](#backlogops.available_teams_config.MembershipConfig.__init__)
    * [nested\_configs](#backlogops.available_teams_config.MembershipConfig.nested_configs)
    * [get\_validation\_plan](#backlogops.available_teams_config.MembershipConfig.get_validation_plan)
    * [serialize\_converters](#backlogops.available_teams_config.MembershipConfig.serialize_converters)
  * [TeamConfig](#backlogops.available_teams_config.TeamConfig)
    * [\_\_init\_\_](#backlogops.available_teams_config.TeamConfig.__init__)
    * [nested\_configs](#backlogops.available_teams_config.TeamConfig.nested_configs)
    * [get\_validation\_plan](#backlogops.available_teams_config.TeamConfig.get_validation_plan)
  * [PersonConfig](#backlogops.available_teams_config.PersonConfig)
    * [\_\_init\_\_](#backlogops.available_teams_config.PersonConfig.__init__)
    * [nested\_configs](#backlogops.available_teams_config.PersonConfig.nested_configs)
    * [get\_validation\_plan](#backlogops.available_teams_config.PersonConfig.get_validation_plan)
  * [CompanyWorkHoursConfig](#backlogops.available_teams_config.CompanyWorkHoursConfig)
    * [\_\_init\_\_](#backlogops.available_teams_config.CompanyWorkHoursConfig.__init__)
    * [nested\_configs](#backlogops.available_teams_config.CompanyWorkHoursConfig.nested_configs)
    * [get\_validation\_plan](#backlogops.available_teams_config.CompanyWorkHoursConfig.get_validation_plan)
    * [serialize\_converters](#backlogops.available_teams_config.CompanyWorkHoursConfig.serialize_converters)
  * [AvailableTeamsConfig](#backlogops.available_teams_config.AvailableTeamsConfig)
    * [\_\_init\_\_](#backlogops.available_teams_config.AvailableTeamsConfig.__init__)
    * [nested\_configs](#backlogops.available_teams_config.AvailableTeamsConfig.nested_configs)
    * [get\_validation\_plan](#backlogops.available_teams_config.AvailableTeamsConfig.get_validation_plan)
  * [write\_available\_teams](#backlogops.available_teams_config.write_available_teams)
  * [read\_available\_teams](#backlogops.available_teams_config.read_available_teams)
* [backlogops.release\_backlog\_updates](#backlogops.release_backlog_updates)
  * [ReleaseChange](#backlogops.release_backlog_updates.ReleaseChange)
  * [BacklogReleaseChange](#backlogops.release_backlog_updates.BacklogReleaseChange)
  * [ReleaseDateChange](#backlogops.release_backlog_updates.ReleaseDateChange)
  * [ReleasesAndDateChanges](#backlogops.release_backlog_updates.ReleasesAndDateChanges)
  * [estimate\_release\_dates](#backlogops.release_backlog_updates.estimate_release_dates)
  * [release\_plan\_on\_estimate](#backlogops.release_backlog_updates.release_plan_on_estimate)
  * [adjust\_release\_content](#backlogops.release_backlog_updates.adjust_release_content)
* [backlogops.releases](#backlogops.releases)
  * [Release](#backlogops.releases.Release)
    * [check\_consistency](#backlogops.releases.Release.check_consistency)
  * [report\_unknown\_keys](#backlogops.releases.report_unknown_keys)
  * [get\_release](#backlogops.releases.get_release)
  * [get\_releases](#backlogops.releases.get_releases)
  * [check\_releases](#backlogops.releases.check_releases)
  * [order\_releases\_by\_date](#backlogops.releases.order_releases_by_date)
* [backlogops.jira\_read](#backlogops.jira_read)
  * [is\_appendable\_jira\_field](#backlogops.jira_read.is_appendable_jira_field)
  * [build\_backlog\_releases](#backlogops.jira_read.build_backlog_releases)
  * [resolve\_jql](#backlogops.jira_read.resolve_jql)
  * [read\_backlog\_from\_jira](#backlogops.jira_read.read_backlog_from_jira)
  * [read\_jira\_from\_config](#backlogops.jira_read.read_jira_from_config)
* [backlogops.table\_rows](#backlogops.table_rows)
  * [BACKLOG\_FIELDS](#backlogops.table_rows.BACKLOG_FIELDS)
  * [RELEASE\_FIELDS](#backlogops.table_rows.RELEASE_FIELDS)
  * [LEVEL\_COLUMN](#backlogops.table_rows.LEVEL_COLUMN)
  * [LEVEL\_NAME\_COLUMN](#backlogops.table_rows.LEVEL_NAME_COLUMN)
  * [apply\_column\_map](#backlogops.table_rows.apply_column_map)
  * [map\_column\_order](#backlogops.table_rows.map_column_order)
  * [item\_to\_row](#backlogops.table_rows.item_to_row)
  * [release\_to\_row](#backlogops.table_rows.release_to_row)
  * [row\_to\_item](#backlogops.table_rows.row_to_item)
  * [row\_to\_release](#backlogops.table_rows.row_to_release)
  * [display\_level\_order](#backlogops.table_rows.display_level_order)
  * [display\_level\_rows](#backlogops.table_rows.display_level_rows)
  * [fold\_level\_name](#backlogops.table_rows.fold_level_name)
* [backlogops.io\_config](#backlogops.io_config)
  * [EXTENSION\_FORMATS](#backlogops.io_config.EXTENSION_FORMATS)
  * [PRESET\_NAME\_RE](#backlogops.io_config.PRESET_NAME_RE)
  * [parse\_status\_input\_map](#backlogops.io_config.parse_status_input_map)
  * [InputFormatConfig](#backlogops.io_config.InputFormatConfig)
    * [\_\_init\_\_](#backlogops.io_config.InputFormatConfig.__init__)
    * [get\_validation\_plan](#backlogops.io_config.InputFormatConfig.get_validation_plan)
  * [OutputFormatConfig](#backlogops.io_config.OutputFormatConfig)
    * [\_\_init\_\_](#backlogops.io_config.OutputFormatConfig.__init__)
    * [parse\_converters](#backlogops.io_config.OutputFormatConfig.parse_converters)
  * [make\_input\_config](#backlogops.io_config.make_input_config)
  * [make\_output\_config](#backlogops.io_config.make_output_config)
  * [GuiDisplayConfig](#backlogops.io_config.GuiDisplayConfig)
    * [\_\_init\_\_](#backlogops.io_config.GuiDisplayConfig.__init__)
    * [parse\_converters](#backlogops.io_config.GuiDisplayConfig.parse_converters)
    * [get\_validation\_plan](#backlogops.io_config.GuiDisplayConfig.get_validation_plan)
  * [resolve\_input\_config](#backlogops.io_config.resolve_input_config)
  * [resolve\_output\_config](#backlogops.io_config.resolve_output_config)
* [backlogops.blo\_version\_reporter](#backlogops.blo_version_reporter)
  * [BloVersionReporter](#backlogops.blo_version_reporter.BloVersionReporter)
    * [package\_names](#backlogops.blo_version_reporter.BloVersionReporter.package_names)
    * [get\_app\_support\_expires](#backlogops.blo_version_reporter.BloVersionReporter.get_app_support_expires)
    * [get\_main\_package\_name](#backlogops.blo_version_reporter.BloVersionReporter.get_main_package_name)
    * [recommended\_python](#backlogops.blo_version_reporter.BloVersionReporter.recommended_python)
* [backlogops.date\_ranges](#backlogops.date_ranges)
  * [check\_date\_range](#backlogops.date_ranges.check_date_range)
  * [check\_no\_overlap](#backlogops.date_ranges.check_no_overlap)
* [backlogops.jira\_token](#backlogops.jira_token)
  * [encrypt\_token](#backlogops.jira_token.encrypt_token)
  * [decrypt\_token](#backlogops.jira_token.decrypt_token)
* [backlogops.levels](#backlogops.levels)
  * [LevelDisplay](#backlogops.levels.LevelDisplay)
  * [Level](#backlogops.levels.Level)
    * [check\_consistency](#backlogops.levels.Level.check_consistency)
  * [DEFAULT\_LEVELS](#backlogops.levels.DEFAULT_LEVELS)
  * [report\_duplicate\_label](#backlogops.levels.report_duplicate_label)
  * [check\_levels\_consistency](#backlogops.levels.check_levels_consistency)
  * [levels\_from\_list](#backlogops.levels.levels_from_list)
  * [level\_number\_from\_name](#backlogops.levels.level_number_from_name)
  * [level\_name](#backlogops.levels.level_name)
* [backlogops.backlog\_releases\_io](#backlogops.backlog_releases_io)
  * [BACKLOG\_HEADING](#backlogops.backlog_releases_io.BACKLOG_HEADING)
  * [RELEASE\_HEADING](#backlogops.backlog_releases_io.RELEASE_HEADING)
  * [read\_backlog\_releases](#backlogops.backlog_releases_io.read_backlog_releases)
  * [write\_backlog\_releases](#backlogops.backlog_releases_io.write_backlog_releases)
* [backlogops.backlog\_ops\_wizard](#backlogops.backlog_ops_wizard)
  * [available\_teams\_wizard](#backlogops.backlog_ops_wizard.available_teams_wizard)
  * [backlog\_ops\_wizard](#backlogops.backlog_ops_wizard.backlog_ops_wizard)
* [backlogops.order\_by\_dependencies](#backlogops.order_by_dependencies)
  * [DependencyMode](#backlogops.order_by_dependencies.DependencyMode)
  * [order\_by\_dependencies](#backlogops.order_by_dependencies.order_by_dependencies)
* [backlogops.backlog\_in\_release\_order](#backlogops.backlog_in_release_order)
  * [backlog\_in\_release\_order](#backlogops.backlog_in_release_order.backlog_in_release_order)
* [backlogops.move\_keys\_first](#backlogops.move_keys_first)
  * [move\_keys\_first](#backlogops.move_keys_first.move_keys_first)
  * [get\_keys\_in\_order](#backlogops.move_keys_first.get_keys_in_order)
* [backlogops.estimate\_ready\_date](#backlogops.estimate_ready_date)
  * [estimate\_ready\_date](#backlogops.estimate_ready_date.estimate_ready_date)
  * [set\_plan\_from\_estimate](#backlogops.estimate_ready_date.set_plan_from_estimate)
* [backlogops.work\_hours](#backlogops.work_hours)
  * [WeekDay](#backlogops.work_hours.WeekDay)
  * [DEFAULT\_WORK\_WEEK](#backlogops.work_hours.DEFAULT_WORK_WEEK)
  * [ExceptionWorkHours](#backlogops.work_hours.ExceptionWorkHours)
    * [check\_consistency](#backlogops.work_hours.ExceptionWorkHours.check_consistency)
  * [CompanyWorkHours](#backlogops.work_hours.CompanyWorkHours)
    * [check\_consistency](#backlogops.work_hours.CompanyWorkHours.check_consistency)
* [backlogops.format\_rules](#backlogops.format_rules)
  * [default\_status\_format](#backlogops.format_rules.default_status_format)
  * [FormatRules](#backlogops.format_rules.FormatRules)
    * [backlog\_first](#backlogops.format_rules.FormatRules.backlog_first)
    * [border\_style](#backlogops.format_rules.FormatRules.border_style)
    * [filtered\_data\_range](#backlogops.format_rules.FormatRules.filtered_data_range)
    * [first\_row\_format](#backlogops.format_rules.FormatRules.first_row_format)
    * [status\_format](#backlogops.format_rules.FormatRules.status_format)
    * [estimate\_late](#backlogops.format_rules.FormatRules.estimate_late)
    * [estimate\_early](#backlogops.format_rules.FormatRules.estimate_early)
    * [estimate\_eq\_planned](#backlogops.format_rules.FormatRules.estimate_eq_planned)
    * [get\_status\_format](#backlogops.format_rules.FormatRules.get_status_format)
    * [turn\_off\_cell\_format](#backlogops.format_rules.FormatRules.turn_off_cell_format)
    * [cell\_format\_used](#backlogops.format_rules.FormatRules.cell_format_used)
* [backlogops.io\_preset\_wizard](#backlogops.io_preset_wizard)
  * [preset\_wizard](#backlogops.io_preset_wizard.preset_wizard)

<a id="backlogops.available_teams"></a>

# backlogops.available\_teams

Define the available workforce: persons and teams.

<a id="backlogops.available_teams.membership_fte_on"></a>

#### membership\_fte\_on

```python
def membership_fte_on(membership: Membership, day: date) -> float
```

Return the full-time equivalent of a membership on a given day.

Days outside the membership date range give 0.0. A day covered by an
fte_exception gives that exception's full-time equivalent. Otherwise
the membership's base full-time equivalent applies.

**Arguments**:

- `membership` - The membership to evaluate.
- `day` - The day to evaluate the membership on.
  

**Returns**:

  The full-time equivalent the person gives to the team on the day.

<a id="backlogops.available_teams.candidate_days"></a>

#### candidate\_days

```python
def candidate_days(memberships: list[Membership]) -> set[date]
```

Return the days where the summed full-time equivalent can change.

The summed full-time equivalent is constant between the start and end
boundaries of the memberships and their fte_exceptions, so checking
those boundary days is enough to find its maximum. When there are no
boundaries (all memberships are fully open) a single day is returned,
on which every membership contributes its base full-time equivalent.

**Arguments**:

- `memberships` - The memberships of one person across all teams.
  

**Returns**:

  The set of days on which to evaluate the summed full-time
  equivalent.

<a id="backlogops.available_teams.check_person_capacity"></a>

#### check\_person\_capacity

```python
def check_person_capacity(person_name: str,
                          memberships: list[Membership],
                          stderr_file: TextIO = sys.stderr) -> None
```

Check a person is not allocated more than full time on any day.

The summed full-time equivalent over all of the person's memberships
is evaluated on every boundary day and must not exceed 1.0.

**Arguments**:

- `person_name` - The name of the person, for error messages.
- `memberships` - The memberships of the person across all teams.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `ValueError` - If the summed full-time equivalent exceeds 1.0 on any
  day.

<a id="backlogops.available_teams.AvailableTeams"></a>

## AvailableTeams Objects

```python
@dataclass
class AvailableTeams()
```

Define the available workforce that can do work.

The persons registry holds every person once, keyed by the lower-case
person name, so that personal availability is entered in a single
place. Teams reference their members by person name into this
registry. This lets a person move between teams or split time across
teams without duplicating the person.

Fields:
    persons: The registry of persons, keyed by lower-case person name.
    teams: The list of teams that are available to do work.
    company_work_hours: The company work hours that apply to everyone.

<a id="backlogops.available_teams.AvailableTeams.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of the available workforce.

Field types are verified, the company work hours and every person
and team are checked, team names and aliases are checked to be
unique case-insensitively across all teams, every membership is
checked to reference a known person, and no person is allocated
more than full time on any day.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a field value violates a constraint, if team
  labels are not unique, or if a person is over-allocated.
- `KeyError` - If a membership references an unknown person.

<a id="backlogops.apply_format_rules"></a>

# backlogops.apply\_format\_rules

Apply format rules to backlog and release table data.

<a id="backlogops.apply_format_rules.format_backlog"></a>

#### format\_backlog

```python
def format_backlog(backlog: Backlog,
                   format_rules: FormatRules) -> DictData[ValueFmt]
```

Format the backlog according to the format rules.

Each backlog item becomes one row of formatted cells, keyed by the
internal field name. The status cell is formatted by its status, and
the estimated-ready-date cell by its relation to the planned-ready
date; all other cells are left unformatted.

**Arguments**:

- `backlog` - The backlog to format.
- `format_rules` - The format rules to apply.
  

**Returns**:

  The formatted backlog rows, ready for TableIO.

<a id="backlogops.apply_format_rules.format_releases"></a>

#### format\_releases

```python
def format_releases(releases: Releases,
                    format_rules: FormatRules) -> DictData[ValueFmt]
```

Format the releases according to the format rules.

Each release becomes one row of formatted cells, keyed by the internal
field name. The estimated-date cell is formatted by its relation to the
planned date; the other cells are left unformatted.

**Arguments**:

- `releases` - The releases to format.
- `format_rules` - The format rules to apply.
  

**Returns**:

  The formatted release rows, ready for TableIO.

<a id="backlogops.backlog_helpers"></a>

# backlogops.backlog\_helpers

Helpers for converting and validating backlog item data.

These helpers turn plain dictionaries into validated backlog field
values and report problems in a uniform way. They are deliberately
generic: they operate on values and type hints, not on the backlog item
class, so that the backlog module can use them without a circular
import.

<a id="backlogops.backlog_helpers.FORBIDDEN_KEY_CHARS"></a>

#### FORBIDDEN\_KEY\_CHARS

Characters that must never appear in a key or dependency.

<a id="backlogops.backlog_helpers.CONTROL_CHAR_NAMES"></a>

#### CONTROL\_CHAR\_NAMES

Readable names for common invisible control characters.

<a id="backlogops.backlog_helpers.field_type_hints"></a>

#### field\_type\_hints

```python
def field_type_hints(cls: type) -> dict[str, object]
```

Return the resolved type hints for the fields of a class.

Postponed annotations and forward references are resolved, so that
callers receive concrete type objects (for example ``date`` and
``Status``) instead of their string annotations.

**Arguments**:

- `cls` - The class whose annotations should be resolved.
  

**Returns**:

  A mapping from field name to its resolved type hint.

<a id="backlogops.backlog_helpers.is_mandatory_field"></a>

#### is\_mandatory\_field

```python
def is_mandatory_field(item_field: Field[object]) -> bool
```

Return True when a field must be supplied by the input data.

A field is mandatory when it takes part in ``__init__`` and has
neither a default value nor a default factory.

**Arguments**:

- `item_field` - The dataclass field to inspect.
  

**Returns**:

  True if the field has no default and must be supplied.

<a id="backlogops.backlog_helpers.enum_class_of"></a>

#### enum\_class\_of

```python
def enum_class_of(data_type: object) -> Optional[type[Enum]]
```

Return the enum class of a type hint, or None.

**Arguments**:

- `data_type` - The type hint to inspect.
  

**Returns**:

  The enum class when ``data_type`` is an Enum subclass, else None.

<a id="backlogops.backlog_helpers.is_union_type"></a>

#### is\_union\_type

```python
def is_union_type(data_type: object) -> bool
```

Return True if a type hint is a ``Union`` or an ``X | Y`` union.

**Arguments**:

- `data_type` - The type hint to inspect.
  

**Returns**:

  True if the type hint is any kind of union.

<a id="backlogops.backlog_helpers.non_optional_type"></a>

#### non\_optional\_type

```python
def non_optional_type(data_type: object) -> object
```

Return the inner type of an ``Optional`` hint.

For ``Optional[X]`` (that is ``Union[X, None]``) the wrapped type
``X`` is returned. For a union with several non-None members, or for
a type hint that is not a union, the original hint is returned.

**Arguments**:

- `data_type` - The type hint to unwrap.
  

**Returns**:

  The single non-None union member, or the original type hint.

<a id="backlogops.backlog_helpers.accepts_none"></a>

#### accepts\_none

```python
def accepts_none(data_type: object) -> bool
```

Return True if ``None`` is a valid value for a type hint.

**Arguments**:

- `data_type` - The type hint to inspect.
  

**Returns**:

  True if the type hint is an optional or ``None`` accepting union.

<a id="backlogops.backlog_helpers.value_matches_type"></a>

#### value\_matches\_type

```python
def value_matches_type(value: object, data_type: object) -> bool
```

Return True if a value matches a supported type hint.

Supported hints are ``object``, optional and union types, enums, and
the ``str``, ``int``, ``date``, ``list[...]`` and ``dict[..., ...]``
forms used by backlog items.

**Arguments**:

- `value` - The runtime value to check.
- `data_type` - The type hint to check the value against.
  

**Returns**:

  True if the value is acceptable for the given type hint.

<a id="backlogops.backlog_helpers.report_missing_field"></a>

#### report\_missing\_field

```python
def report_missing_field(field_name: str,
                         stderr_file: TextIO = sys.stderr) -> NoReturn
```

Report a missing mandatory field and raise ``KeyError``.

**Arguments**:

- `field_name` - The name of the missing field.
- `stderr_file` - The file to report the error to.
  

**Raises**:

- `KeyError` - Always, after reporting the message.

<a id="backlogops.backlog_helpers.report_wrong_type"></a>

#### report\_wrong\_type

```python
def report_wrong_type(field_name: str,
                      value: object,
                      data_type: object,
                      stderr_file: TextIO = sys.stderr,
                      subject: str = 'Backlog item') -> NoReturn
```

Report a value of the wrong type and raise ``TypeError``.

**Arguments**:

- `field_name` - The name of the offending field.
- `value` - The value that has the wrong type.
- `data_type` - The type hint the value was expected to match.
- `stderr_file` - The file to report the error to.
- `subject` - What owns the field, used to start the message (for
  example ``'Backlog item'``, ``'Person'`` or ``'Team'``).
  

**Raises**:

- `TypeError` - Always, after reporting the message.

<a id="backlogops.backlog_helpers.report_bad_value"></a>

#### report\_bad\_value

```python
def report_bad_value(field_name: str,
                     value: object,
                     reason: str,
                     stderr_file: TextIO = sys.stderr,
                     subject: str = 'Backlog item') -> NoReturn
```

Report a value that violates a constraint and raise ``ValueError``.

**Arguments**:

- `field_name` - The name of the offending field.
- `value` - The value that violates the constraint.
- `reason` - A human readable explanation of the constraint.
- `stderr_file` - The file to report the error to.
- `subject` - What owns the field, used to start the message (for
  example ``'Backlog item'``, ``'Person'`` or ``'Team'``).
  

**Raises**:

- `ValueError` - Always, after reporting the message.

<a id="backlogops.backlog_helpers.report_unknown_reference"></a>

#### report\_unknown\_reference

```python
def report_unknown_reference(field_name: str,
                             owner_key: str,
                             referenced_key: str,
                             stderr_file: TextIO = sys.stderr,
                             subject: str = 'Backlog item') -> NoReturn
```

Report a reference to a missing key and raise ``KeyError``.

**Arguments**:

- `field_name` - The field that holds the reference.
- `owner_key` - The key of the item that owns the reference.
- `referenced_key` - The key that does not exist.
- `stderr_file` - The file to report the error to.
- `subject` - What owns the field, used to start the message (for
  example ``'Backlog item'`` or ``'Team'``).
  

**Raises**:

- `KeyError` - Always, after reporting the message.

<a id="backlogops.backlog_helpers.check_field_types"></a>

#### check\_field\_types

```python
def check_field_types(instance: object,
                      stderr_file: TextIO = sys.stderr,
                      subject: str = 'Backlog item') -> None
```

Check that every field of a dataclass holds its declared type.

The instance must be a dataclass instance. Each field value is
compared with its resolved type hint using
:func:`value_matches_type`, and the first mismatch is reported with
:func:`report_wrong_type`.

**Arguments**:

- `instance` - The dataclass instance to check.
- `stderr_file` - The file to report errors to.
- `subject` - What owns the fields, used to start error messages.
  

**Raises**:

- `TypeError` - If a field holds a value of the wrong type.

<a id="backlogops.backlog_helpers.convert_to_enum"></a>

#### convert\_to\_enum

```python
def convert_to_enum(field_name: str,
                    value: object,
                    enum_class: type[Enum],
                    stderr_file: TextIO = sys.stderr) -> Enum
```

Convert a value to a member of an enum class.

A value that is already a member of ``enum_class`` is returned
unchanged. A string is matched against the member names using
``string_to_enum_best_match`` (which allows case and unique prefix
matches). An integer is looked up as a raw enum value. Booleans are
rejected, even though a boolean is technically an integer.

**Arguments**:

- `field_name` - The name of the field being converted.
- `value` - The member, name or raw value to convert.
- `enum_class` - The enum class to convert to.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The matching enum member.
  

**Raises**:

- `TypeError` - If no enum member matches the value.

<a id="backlogops.backlog_helpers.convert_to_date"></a>

#### convert\_to\_date

```python
def convert_to_date(field_name: str,
                    value: object,
                    stderr_file: TextIO = sys.stderr) -> date
```

Convert a value to a ``datetime.date``.

A ``datetime`` is narrowed to its ``date`` part, dropping any time
component (spreadsheet date cells arrive as midnight ``datetime``
values). A value that is already a plain ``date`` is returned
unchanged. A string is parsed as an ISO 8601 date such as
``'2026-06-12'``.

**Arguments**:

- `field_name` - The name of the field being converted.
- `value` - The date, datetime or ISO 8601 string to convert.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The converted date.
  

**Raises**:

- `TypeError` - If the value is neither a date nor a valid ISO string.

<a id="backlogops.backlog_helpers.convert_to_str"></a>

#### convert\_to\_str

```python
def convert_to_str(field_name: str,
                   value: object,
                   stderr_file: TextIO = sys.stderr) -> str
```

Convert an unambiguous value to a ``str``.

A value that is already a string is returned unchanged. An integer
is converted to its decimal string, so a key entered as the number
``100`` becomes ``'100'``. A float without a fractional part is
converted as an integer (``100.0`` becomes ``'100'``); any other
float uses its own string form. A boolean is rejected, because
whether ``True`` should become ``'True'`` or ``'1'`` is ambiguous.

**Arguments**:

- `field_name` - The name of the field being converted.
- `value` - The value to convert to a string.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The converted string.
  

**Raises**:

- `TypeError` - If the value cannot be unambiguously converted.

<a id="backlogops.backlog_helpers.convert_field_value"></a>

#### convert\_field\_value

```python
def convert_field_value(field_name: str,
                        value: object,
                        data_type: object,
                        stderr_file: TextIO = sys.stderr) -> object
```

Convert and validate a single field value against its type hint.

``None`` is accepted for optional fields. Enum fields are converted
with :func:`convert_to_enum`, date fields with :func:`convert_to_date`,
string fields with :func:`convert_to_str`, and all other fields are
checked with :func:`value_matches_type`.

**Arguments**:

- `field_name` - The name of the field being converted.
- `value` - The raw input value.
- `data_type` - The resolved type hint of the field.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The converted value, ready to be stored on the backlog item.
  

**Raises**:

- `TypeError` - If the value cannot be converted to the field type.

<a id="backlogops.backlog_helpers.is_extra_field_map"></a>

#### is\_extra\_field\_map

```python
def is_extra_field_map(item_field: Field[object],
                       field_types: dict[str, object]) -> bool
```

Return True if a field is the ``dict[str, object]`` extras map.

The extras map stores input keys that do not correspond to a named
field. It is recognised by being a default-factory ``dict`` field
whose value type is ``object``.

**Arguments**:

- `item_field` - The dataclass field to inspect.
- `field_types` - The resolved type hints of the dataclass.
  

**Returns**:

  True if the field is the extras mapping field.

<a id="backlogops.backlog_helpers.extra_field_name"></a>

#### extra\_field\_name

```python
def extra_field_name(item_fields: Sequence[Field[object]],
                     field_types: dict[str, object]) -> Optional[str]
```

Return the name of the extras map field, if any.

**Arguments**:

- `item_fields` - The dataclass fields to search.
- `field_types` - The resolved type hints of the dataclass.
  

**Returns**:

  The name of the extras mapping field, or None.

<a id="backlogops.backlog_helpers.collect_extra_values"></a>

#### collect\_extra\_values

```python
def collect_extra_values(
        data: dict[str, object],
        known_names: set[str],
        extra_name: str,
        data_type: object,
        stderr_file: TextIO = sys.stderr) -> dict[str, object]
```

Collect the values for the extras mapping field.

The result merges an explicit ``extra_name`` mapping found in the
input with every input key that does not match a named field.

**Arguments**:

- `data` - The raw input data for one backlog item.
- `known_names` - The names of the named dataclass fields.
- `extra_name` - The name of the extras mapping field.
- `data_type` - The resolved type hint of the extras field.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The mapping of extra field names to their values.
  

**Raises**:

- `TypeError` - If an explicit extras mapping has the wrong type.

<a id="backlogops.backlog_helpers.build_item_kwargs"></a>

#### build\_item\_kwargs

```python
def build_item_kwargs(item_fields: Sequence[Field[object]],
                      field_types: dict[str, object],
                      data: dict[str, object],
                      stderr_file: TextIO = sys.stderr) -> dict[str, object]
```

Build the constructor keyword arguments for a backlog item.

Each named field present in ``data`` is converted to its declared
type. Missing mandatory fields are reported and rejected. Any input
keys that do not match a named field are gathered into the extras
mapping field.

**Arguments**:

- `item_fields` - The dataclass fields of the backlog item.
- `field_types` - The resolved type hints of the dataclass.
- `data` - The raw input data for one backlog item.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The keyword arguments to construct one backlog item.
  

**Raises**:

- `KeyError` - If a mandatory field is missing.
- `TypeError` - If a field value has a type that cannot be converted.

<a id="backlogops.backlog_helpers.construct"></a>

#### construct

```python
def construct(item_cls: Callable[..., T], item_kwargs: dict[str, object]) -> T
```

Construct an instance from validated keyword arguments.

**Arguments**:

- `item_cls` - The class (or callable) to instantiate.
- `item_kwargs` - The keyword arguments to pass to ``item_cls``.
  

**Returns**:

  The constructed instance.

<a id="backlogops.backlog_helpers.check_key_syntax"></a>

#### check\_key\_syntax

```python
def check_key_syntax(field_name: str,
                     value: object,
                     stderr_file: TextIO = sys.stderr,
                     subject: str = 'Backlog item') -> None
```

Check that a value is a well formed backlog key.

A backlog key (used by ``key`` and by the entries of the dependency
lists) must be a non-empty string that contains no whitespace and
none of the separator or bracket characters ``, . ; : ( ) [ ] { }``.
All other characters, including letters, digits, ``-``, ``_`` and
signs such as ``#`` or ``$``, are allowed.

**Arguments**:

- `field_name` - The name of the field being checked.
- `value` - The value that should be a valid key.
- `stderr_file` - The file to report errors to.
- `subject` - What owns the field, used to start error messages.
  

**Raises**:

- `TypeError` - If the value is not a string.
- `ValueError` - If the string is empty or contains a forbidden
  character.

<a id="backlogops.backlog_helpers.check_label_syntax"></a>

#### check\_label\_syntax

```python
def check_label_syntax(field_name: str,
                       value: object,
                       stderr_file: TextIO = sys.stderr,
                       subject: str = 'Backlog item') -> None
```

Check that a value is a readable human-facing label.

A label is a non-empty string without leading or trailing whitespace.
Ordinary spaces and punctuation are allowed inside the label, but
tabs, newlines, other whitespace characters and control-like Unicode
characters are rejected with a readable character name.

**Arguments**:

- `field_name` - The name of the field being checked.
- `value` - The value that should be a valid label.
- `stderr_file` - The file to report errors to.
- `subject` - What owns the field, used to start error messages.
  

**Raises**:

- `TypeError` - If the value is not a string.
- `ValueError` - If the string is empty, padded, or contains a
  control-like character.

<a id="backlogops.backlog_helpers.find_cycle"></a>

#### find\_cycle

```python
def find_cycle(graph: dict[str, list[str]]) -> Optional[list[str]]
```

Return a cycle in a directed graph, or None if it is acyclic.

The graph maps each node to the list of nodes it points to. A
returned cycle starts and ends with the same node, so a self
reference is reported as ``[node, node]``.

**Arguments**:

- `graph` - A mapping from each node to its successor nodes.
  

**Returns**:

  The nodes that form a cycle (with the start node repeated at the
  end), or None when the graph has no cycle.

<a id="backlogops.key_list_io"></a>

# backlogops.key\_list\_io

Read and write a key list as its own file.

A key list is an ordered list of backlog item keys stored on its own,
separate from the backlog. The file format is chosen from the file name
extension: a ``.txt`` or ``.dat`` file is plain UTF-8 text, and any
extension that TableIO supports (such as ``.csv``, ``.ods`` or ``.xlsx``)
is a one column table.

Two options apply to both shapes and describe whether the file carries a
column name. ``skip_column_names`` tells the reader that the first
row/line is a column name to skip, and ``add_column_name`` tells the
writer to write such a column name (``Keys``).

For a text file without a column name every whitespace separated word is
a key, in the order the words appear; with a column name the heading line
is skipped and every following non empty line holds exactly one key.

For a table file without a column name every row is data (read with list
reading); with a column name the first row names the column (read with
dict reading). A single column table usually has no column name, but it
may have one. Either way the table must have exactly one column.

<a id="backlogops.key_list_io.TEXT_EXTENSIONS"></a>

#### TEXT\_EXTENSIONS

File name extensions read and written as plain UTF-8 text.

<a id="backlogops.key_list_io.KEY_COLUMN_NAME"></a>

#### KEY\_COLUMN\_NAME

Column name of the single column of a key list table.

<a id="backlogops.key_list_io.read_key_list"></a>

#### read\_key\_list

```python
def read_key_list(file_name: PathOrStr,
                  *,
                  skip_column_names: bool = False,
                  stderr_file: TextIO = sys.stderr) -> list[str]
```

Read a key list from a file.

The file type is chosen from the file name extension. A ``.txt`` or
``.dat`` file is read as UTF-8 text; any other extension is read as a
TableIO table whose single column holds the keys.

``skip_column_names`` tells whether the file starts with a column
name. For a text file, when it is False the file is a free word list
and every whitespace separated word is a key, in the order the words
appear; when it is True the first line is a column heading and is
skipped, and every following non empty line must hold exactly one
word, which is a key. For a table file, when it is False every row is
data (list reading); when it is True the first row names the column
and is skipped (dict reading). A table must have exactly one column.

**Arguments**:

- `file_name` - The file to read the key list from.
- `skip_column_names` - Whether the file starts with a column name to
  skip.
- `stderr_file` - The stream to report errors to.
  

**Returns**:

  The keys in the order they appear in the file.
  

**Raises**:

- `FileNotFoundError` - If the file does not exist.
- `IsADirectoryError` - If the file is a directory.
- `PermissionError` - If the file is not readable.
- `UnicodeDecodeError` - If a text file is not valid UTF-8.
- `ValueError` - If a column text line holds more than one word, if a
  table has more than one column, or if the extension is not a
  supported table format.

<a id="backlogops.key_list_io.write_key_list"></a>

#### write\_key\_list

```python
def write_key_list(
        key_list: Sequence[str],
        file_name: PathOrStr,
        *,
        add_column_name: bool = False,
        stderr_file: TextIO = sys.stderr,
        file_exists_callback: Optional[FileExistsCb] = None) -> None
```

Write a key list to a file.

The file type is chosen from the file name extension. A ``.txt`` or
``.dat`` file is written as UTF-8 text with one key per line; any
other extension is written as a TableIO table with a single column.

``add_column_name`` decides whether the column name ``Keys`` is
written before the keys: as a heading line for a text file, and as a
header row for a table file. When it is False a text file holds only
the keys and a table file holds only data rows (list writing).

**Arguments**:

- `key_list` - The keys to write, in order.
- `file_name` - The file to create.
- `add_column_name` - Whether to write the column name ``Keys`` first.
- `stderr_file` - The stream to report errors to.
- `file_exists_callback` - Called when the file already exists, as
  documented for :mod:`backlogops.table_create`.
  None refuses an existing file.
  

**Raises**:

- `FileExistsError` - If the file exists and the callback refuses it.
- `IsADirectoryError` - If the file is a directory.
- `PermissionError` - If the file is not writable.
- `ValueError` - If the extension is not a supported table format.

<a id="backlogops.person"></a>

# backlogops.person

Define a person including any exceptions in work hours.

<a id="backlogops.person.Person"></a>

## Person Objects

```python
@dataclass
class Person()
```

Define a person including any exceptions in work hours.

<a id="backlogops.person.Person.name"></a>

#### name

The name of the person.

<a id="backlogops.person.Person.exceptions"></a>

#### exceptions

Any exceptions in work hours for the person.

These exceptions are used to mark personal vacation days,
and other planned days off. They can also mark any period
of time the person has other work hours, for instance periods
of part-time work or ordered over-time work.

<a id="backlogops.backlog_releases"></a>

# backlogops.backlog\_releases

Backlog and and its related releases.

<a id="backlogops.backlog_releases.BacklogReleases"></a>

## BacklogReleases Objects

```python
@dataclass
class BacklogReleases()
```

A backlog and its related releases.

The releases list describes the releases that the backlog items are
delivered in. A backlog item refers to its release by name through
its ``release`` field. The releases list may hold releases that no
backlog item refers to yet, but every release named by a backlog
item is expected to be present in the releases list.

Fields:
    backlog: The backlog of items.
    releases: The releases the backlog items are delivered in.

<a id="backlogops.backlog_releases.BacklogReleases.add_to_releases"></a>

#### add\_to\_releases

```python
@staticmethod
def add_to_releases(backlog: Backlog, releases: Releases) -> Releases
```

Add all releases mentioned in the backlog to the releases list.

For each backlog item that names a release, a release with that
name is added to the releases list when no release of that name
is present yet. A release added this way has no planned or
estimated date, because a backlog item only carries the release
name. The order of the existing releases is kept and any new
releases are appended in the order they are first met in the
backlog.

**Arguments**:

- `backlog` - The backlog to take the release names from.
- `releases` - The releases to add the missing releases to.
  The argument is not modified.
  

**Returns**:

  The releases list with the added releases. If all releases
  named by the backlog are already present, the argument
  object is returned unchanged. If any new releases are added,
  a new list is returned.

<a id="backlogops.backlog_releases.BacklogReleases.check_in_releases"></a>

#### check\_in\_releases

```python
@staticmethod
def check_in_releases(backlog: Backlog,
                      releases: Releases,
                      stderr_file: TextIO = sys.stderr) -> None
```

Check that all releases in the backlog are in the releases list.

For each backlog item that names a release, the release is
checked to be present by name in the releases list.

**Arguments**:

- `backlog` - The backlog to check.
- `releases` - The releases to check the backlog against.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a release named by the backlog is not present in
  the releases list.

<a id="backlogops.backlog_releases.BacklogReleases.update_releases"></a>

#### update\_releases

```python
def update_releases() -> None
```

Update the releases list to include all releases in the backlog.

For each backlog item that names a release, the release is added
to the releases list when it is not already present, as
documented for :meth:`add_to_releases`.

<a id="backlogops.backlog_releases.BacklogReleases.check_release_xref"></a>

#### check\_release\_xref

```python
def check_release_xref(stderr_file: TextIO = sys.stderr) -> None
```

Check that all releases in the backlog are in the releases list.

This is the cross reference check documented for
:meth:`check_in_releases`, applied to the member backlog and
releases.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a release named by the backlog is not present in
  the releases list.

<a id="backlogops.backlog_releases.BacklogReleases.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the internal consistency of the backlog and releases.

The backlog is checked for full consistency as documented for
:func:`check_backlog_consistency`, the releases are checked for
internal consistency and unique names as documented for
:func:`check_releases`, and every release named by the backlog
is checked to be present in the releases list.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a field value violates a constraint, or if
  release names are not unique.
- `KeyError` - If a key reference is invalid, or if a release
  named by the backlog is not in the releases list.

<a id="backlogops.backlog_releases.BacklogReleases.move_keys_first"></a>

#### move\_keys\_first

```python
def move_keys_first(keys: Sequence[str],
                    stderr_file: TextIO = sys.stderr) -> None
```

Move the items named by ``keys`` to the front of the backlog.

The named items lead the backlog in the order of ``keys``. Each
named item is preceded by its descendants in post order: a child
comes right before its own parent, and that parent right before
the grandparent, up to the named item. Siblings keep their
original backlog order. A named descendant is placed by its own
key instead, so it may end up after its named parent. A descendant
is pulled to the front only when it appears after its named
ancestor in the backlog, so that no item is moved to a later
position because of an ancestor's key. The remaining items keep
their original order after the front block. The behavior is the
one documented for :func:`backlogops.move_keys_first`.

**Arguments**:

- `keys` - The keys to move to the front, in the wanted order. The
  keys must be unique and must exist in the backlog.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a key is not found in the backlog.
- `ValueError` - If a key is not unique.

<a id="backlogops.backlog_releases.BacklogReleases.order_by_dependencies"></a>

#### order\_by\_dependencies

```python
def order_by_dependencies(*,
                          later: bool = False,
                          mode: DependencyMode = DependencyMode.KEEP,
                          space_around: Optional[str | Sequence[str]] = None,
                          stderr_file: TextIO = sys.stderr) -> None
```

Order the member backlog by dependencies.

The member backlog is replaced by a backlog ordered so that a
team can start the items in backlog order without starting an
item before the items it depends on. The behavior is the one
documented for :func:`backlogops.order_by_dependencies`.

**Arguments**:

- `later` - How a dependency that is not yet satisfied is resolved.
  If False (the default) the prerequisite item is pulled to
  a position just before the dependent item. If True the
  dependent item is pushed to a position just after its
  prerequisites.
- `mode` - How items that take part in a dependency are placed in
  relation to items that take part in no dependency, as
  documented for :class:`DependencyMode`. The default is
  KEEP.
- `space_around` - Key or keys of items that should have as many
  other items as possible placed between them and the items
  they depend on, and between them and the items that
  depend on them. It only works well for one or very few
  items. None means no item is treated this way.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If space_around is neither None, a string, nor a
  sequence of strings.
- `KeyError` - If a space_around key is not found in the backlog.
- `RuntimeError` - If space_around names more keys than allowed:
  more than five, or more than ten percent of a backlog of
  fewer than fifty items.

<a id="backlogops.backlog_releases.BacklogReleases.estimate_ready_date"></a>

#### estimate\_ready\_date

```python
def estimate_ready_date(
        available_teams: AvailableTeams,
        start_date: Optional[date] = None,
        stderr_file: TextIO = sys.stderr) -> ReleaseDateChanges
```

Estimate the ready date of the member backlog items.

The member backlog is replaced by a backlog whose items carry the
estimated ready date. The teams start working on the start date,
which defaults to today when None is given. The behavior is the
one documented for :func:`backlogops.estimate_ready_date`.

**Arguments**:

- `available_teams` - The available teams used to estimate the
  ready date, including absence, velocity and work
  hours.
- `start_date` - The day the teams start working, or None for today.
- `stderr_file` - The file to report warnings to.

<a id="backlogops.backlog_releases.BacklogReleases.set_plan_from_estimate"></a>

#### set\_plan\_from\_estimate

```python
def set_plan_from_estimate(stderr_file: TextIO = sys.stderr) -> None
```

Set the planned ready dates from the estimated ready dates.

The member backlog is replaced by a backlog whose items carry the
planned ready date taken from the estimated ready date, as
documented for :func:`backlogops.set_plan_from_estimate`.

**Arguments**:

- `stderr_file` - The file to report errors to.

<a id="backlogops.backlog_releases.BacklogReleases.adjust_release_content"></a>

#### adjust\_release\_content

```python
def adjust_release_content(buffer: timedelta,
                           stderr_file: TextIO = sys.stderr) -> ReleaseChanges
```

Adjust the release content to fit the planned release dates.

The member backlog is replaced by a backlog whose items carry the
adjusted release content. The behavior is the one documented for
:func:`backlogops.adjust_release_content`.

**Arguments**:

- `buffer` - The buffer or slack added to the estimated ready dates
  to gain confidence that an item fits a release. Must
  not be negative.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  A record of how the release content was changed.
  

**Raises**:

- `ValueError` - If the buffer is negative.

<a id="backlogops.backlog_releases.BacklogReleases.release_plan_on_estimate"></a>

#### release\_plan\_on\_estimate

```python
def release_plan_on_estimate(
        buffer: timedelta,
        stderr_file: TextIO = sys.stderr) -> ReleaseDateChanges
```

Set the planned release dates from the estimated release dates.

The member releases is replaced by releases whose items carry the
planned release dates taken from the estimated release dates, as
documented for :func:`backlogops.release_plan_on_estimate`.

**Arguments**:

- `buffer` - The buffer or slack to add to the estimated release dates
  to get the planned release dates. Must not be negative.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  A record of how the release dates were changed.
  

**Raises**:

- `ValueError` - If the buffer is negative.

<a id="backlogops.backlog_releases.BacklogReleases.order_releases_by_date"></a>

#### order\_releases\_by\_date

```python
def order_releases_by_date(by_estimated: bool = False,
                           stderr_file: TextIO = sys.stderr) -> None
```

Order the member releases by date.

The member releases are replaced by the releases ordered by date,
as documented for
:func:`backlogops.releases.order_releases_by_date`.

**Arguments**:

- `by_estimated` - If True, order by the estimated date instead of the
  planned date. Default is False.
- `stderr_file` - The file to report errors to.

<a id="backlogops.backlog_releases.BacklogReleases.backlog_in_release_order"></a>

#### backlog\_in\_release\_order

```python
def backlog_in_release_order(*,
                             honor_dependencies: bool = False,
                             later: bool = False,
                             stderr_file: TextIO = sys.stderr) -> None
```

Order the member backlog to follow the member release order.

The member backlog is replaced by a backlog whose items follow the
order of the member releases, exactly as documented for
:func:`backlogops.backlog_in_release_order`. The member releases
are used in their current list order and are not sorted or
otherwise changed; call :meth:`order_releases_by_date` first when a
date order is wanted.

Calling :meth:`check_consistency` before calling this method is
recommended.

**Arguments**:

- `honor_dependencies` - If True, never place an item before an item
  that must be delivered before it (a child before its
  parent, or a depends_on_f2s or depends_on_f2f prerequisite
  before its dependent), as documented for
  :func:`backlogops.backlog_in_release_order`. Default is
  False.
- `later` - When honoring dependencies, if False (the default) a
  prerequisite is pulled to an earlier release and the
  dependent keeps its release; if True the dependent is
  pushed to a later release and the prerequisite keeps its
  release, as documented for
  :func:`backlogops.backlog_in_release_order`. Has no effect
  when honor_dependencies is False. Default is False.
- `stderr_file` - The file to report a missing release reference to.

<a id="backlogops.demo_backlog"></a>

# backlogops.demo\_backlog

A demonstration backlog and releases for manual tests and examples.

The demo data has three level-2 items (epics), twenty level-1 items
(stories) and two level-0 items (tasks). The two tasks share the same
story as parent, and fifteen of the stories have an epic as parent. A few
dependencies are added between items. Two releases exist: ``Next`` with a
planned date one month ahead, and ``Later`` with no planned date. Five
items are assigned to ``Next`` and five to ``Later``; the rest have no
release. The items are returned in a deliberately mixed order, so the
backlog is neither dependency-ordered nor release-ordered, while still
passing all consistency checks.

<a id="backlogops.demo_backlog.get_demo_backlog"></a>

#### get\_demo\_backlog

```python
def get_demo_backlog() -> BacklogReleases
```

Return a demonstration backlog and its releases.

The returned data passes :meth:`BacklogReleases.check_consistency`.
It is useful for manual tests and for developers building
applications on top of this library.

**Returns**:

  A backlog with epics, stories and tasks, and the ``Next`` and
  ``Later`` releases.

<a id="backlogops.no_text_io"></a>

# backlogops.no\_text\_io

NoTextIO can be used as a TextIO object that does nothing.

<a id="backlogops.no_text_io.NoTextIO"></a>

## NoTextIO Objects

```python
class NoTextIO(io.StringIO)
```

NoTextIO can be used as a TextIO object that does nothing.

When a function expects a TextIO object for output, you can pass in
a NoTextIO object and no output will be produced.
The differrence compared to using StringIO to suppress output is that
the NoTextIO does not store any data, so no matter how much is
written to it, you do not risk running out of memory.

<a id="backlogops.no_text_io.NoTextIO.write"></a>

#### write

```python
@override
def write(s: str) -> int
```

Write a string to the NoTextIO object.

This method does nothing and returns 0.

<a id="backlogops.no_text_io.NoTextIO.writelines"></a>

#### writelines

```python
@override
def writelines(lines: Iterable[str]) -> None
```

Write a list of strings to the NoTextIO object.

This method does nothing and returns None.

<a id="backlogops.no_text_io.NoTextIO.flush"></a>

#### flush

```python
@override
def flush() -> None
```

Flush the NoTextIO object.

This method does nothing and returns None.

<a id="backlogops.no_text_io.NoTextIO.close"></a>

#### close

```python
@override
def close() -> None
```

Close the NoTextIO object.

This method does nothing and returns None.

<a id="backlogops.no_text_io.NoTextIO.seek"></a>

#### seek

```python
@override
def seek(offset: int, whence: int = io.SEEK_SET) -> int
```

Seek to a position in the NoTextIO object.

This method does nothing and returns 0.

<a id="backlogops.no_text_io.NoTextIO.tell"></a>

#### tell

```python
@override
def tell() -> int
```

Get the current position in the NoTextIO object.

This method does nothing and returns 0.

<a id="backlogops.no_text_io.NoTextIO.truncate"></a>

#### truncate

```python
@override
def truncate(size: int | None = None) -> int
```

Truncate the NoTextIO object.

This method does nothing and returns 0.

<a id="backlogops.release_change_io"></a>

# backlogops.release\_change\_io

Print and write release-change records as text or table files.

A release-change record is the small log produced by the release update
operations: which backlog item moved between releases
(:class:`ReleaseChange`) and how a release date moved
(:class:`ReleaseDateChange`). These functions render such a log as text
for the console and write it to a one-table file with TableIO, choosing
the file format from the file name extension.

<a id="backlogops.release_change_io.CONTENT_HEADER"></a>

#### CONTENT\_HEADER

Column names of a release content change table.

<a id="backlogops.release_change_io.DATE_HEADER"></a>

#### DATE\_HEADER

Column names of a release date change table.

<a id="backlogops.release_change_io.format_content_changes"></a>

#### format\_content\_changes

```python
def format_content_changes(changes: ReleaseChanges) -> str
```

Return release content changes as text for the console.

<a id="backlogops.release_change_io.format_date_changes"></a>

#### format\_date\_changes

```python
def format_date_changes(changes: ReleaseDateChanges) -> str
```

Return release date changes as text for the console.

<a id="backlogops.release_change_io.write_content_changes"></a>

#### write\_content\_changes

```python
def write_content_changes(
        changes: ReleaseChanges,
        file_name: PathOrStr,
        stderr_file: TextIO = sys.stderr,
        file_exists_callback: Optional[FileExistsCb] = None) -> None
```

Write release content changes to a one table file.

The file format is chosen from the file name extension, as for any
TableIO table. The single table has the columns ``backlog_key``,
``old_release`` and ``new_release``; an absent release is an empty
cell.

**Arguments**:

- `changes` - The release content changes to write, in order.
- `file_name` - The file to create.
- `stderr_file` - The stream to report errors to.
- `file_exists_callback` - Called when the file already exists, as
  documented for :mod:`backlogops.table_create`.
  None refuses an existing file.
  

**Raises**:

- `FileExistsError` - If the file exists and the callback refuses it.
- `ValueError` - If the extension is not a supported table format.

<a id="backlogops.release_change_io.write_date_changes"></a>

#### write\_date\_changes

```python
def write_date_changes(
        changes: ReleaseDateChanges,
        file_name: PathOrStr,
        stderr_file: TextIO = sys.stderr,
        file_exists_callback: Optional[FileExistsCb] = None) -> None
```

Write release date changes to a one table file.

The file format is chosen from the file name extension, as for any
TableIO table. The single table has the columns ``release``,
``old_date`` and ``new_date``; an absent date is an empty cell.

**Arguments**:

- `changes` - The release date changes to write, in order.
- `file_name` - The file to create.
- `stderr_file` - The stream to report errors to.
- `file_exists_callback` - Called when the file already exists, as
  documented for :mod:`backlogops.table_create`.
  None refuses an existing file.
  

**Raises**:

- `FileExistsError` - If the file exists and the callback refuses it.
- `ValueError` - If the extension is not a supported table format.

<a id="backlogops.backlog_ops_config"></a>

# backlogops.backlog\_ops\_config

Top-level backlog-ops configuration stored as config-as-json.

The :class:`BacklogOpsConfig` is the single configuration object an
application reads and writes. It groups together the available workforce,
the named TableIO input and output presets, and an optional set of
backlog item levels:

* ``available_teams`` is the workforce (persons, teams and company work
  hours), bridged to JSON by :class:`AvailableTeamsConfig`;
* ``input_configs`` and ``output_configs`` are named TableIO presets;
* ``jira`` is the Jira input and output configuration, bridged to JSON by
  :class:`backlogops.jira_io_config.JiraIOConfig`;
* ``levels`` is the optional list of backlog item levels. It is omitted
  from the file while it is ``None``; :meth:`BacklogOpsConfig.get_levels`
  then falls back to :data:`backlogops.levels.DEFAULT_LEVELS`.

Earlier file versions stored the workforce members (``persons``,
``teams`` and ``company_work_hours``) at the top level next to the
presets. :class:`_BacklogOpsReadOldConfig` moves those into the nested
``available_teams`` object so old files keep loading.

<a id="backlogops.backlog_ops_config.BacklogOpsConfig"></a>

## BacklogOpsConfig Objects

```python
class BacklogOpsConfig(Config)
```

Top-level backlog-ops configuration stored as config-as-json.

<a id="backlogops.backlog_ops_config.BacklogOpsConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*,
             available_teams: Optional[AvailableTeams] = None,
             from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create defaults, or read the configuration from JSON.

The supplied workforce establishes the schema of the nested
``available_teams`` member; the library's auto-wrap step turns it
into an :class:`AvailableTeamsConfig`. The presets default to
empty maps and the levels default to ``None`` (use the defaults).
The ``auto_ch_hook`` is notified when an old file needed
backward-compatible normalization while reading.

<a id="backlogops.backlog_ops_config.BacklogOpsConfig.nested_configs"></a>

#### nested\_configs

```python
@override
def nested_configs() -> NestedConfigs
```

Declare the workforce and the named TableIO preset maps.

<a id="backlogops.backlog_ops_config.BacklogOpsConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Convert the levels and status map, then check consistency.

<a id="backlogops.backlog_ops_config.BacklogOpsConfig.serialize_converters"></a>

#### serialize\_converters

```python
@override
def serialize_converters() -> SerializeConverters
```

Write the levels member as a list of JSON objects.

<a id="backlogops.backlog_ops_config.BacklogOpsConfig.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of the configured levels, when present.

The workforce and the preset maps are validated by their own
nested configurations. Only the optional levels need a check
here, and only when they are configured.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a level field has the wrong type.
- `ValueError` - If a level value violates a constraint or a level
  number is used more than once.
- `KeyError` - If a level name or alias is not unique.

<a id="backlogops.backlog_ops_config.BacklogOpsConfig.get_levels"></a>

#### get\_levels

```python
def get_levels() -> Levels
```

Return the configured levels, or the default levels.

**Returns**:

  The levels keyed by level number, taken from the
  configuration, or :data:`DEFAULT_LEVELS` when no levels are
  configured.

<a id="backlogops.backlog_ops_config.BacklogOpsConfig.get_status_input_map"></a>

#### get\_status\_input\_map

```python
def get_status_input_map() -> dict[str, Status]
```

Return the library-wide status input map.

**Returns**:

  The extra status names mapped to Status members, as configured
  at the top level. Empty when no extra names are configured.

<a id="backlogops.backlog_ops_config.BacklogOpsConfig.get_gui_level_display"></a>

#### get\_gui\_level\_display

```python
def get_gui_level_display() -> LevelDisplay
```

Return how levels should be shown in the GUI.

**Returns**:

  The :class:`LevelDisplay` configured for the GUI display.

<a id="backlogops.backlog_ops_config.BacklogOpsConfig.get_jira_config"></a>

#### get\_jira\_config

```python
def get_jira_config() -> JiraIOConfig
```

Return the Jira input and output configuration.

**Returns**:

  The :class:`JiraIOConfig` holding the Jira connections, column
  maps and from-Jira presets. Empty when none are configured.

<a id="backlogops.backlog_ops_config.write_backlog_ops_config"></a>

#### write\_backlog\_ops\_config

```python
def write_backlog_ops_config(config: BacklogOpsConfig,
                             filename: PathOrStr,
                             stderr_file: TextIO = sys.stderr) -> None
```

Validate and write a backlog-ops configuration to a JSON file.

**Arguments**:

- `config` - The configuration to store.
- `filename` - Destination JSON configuration file.
- `stderr_file` - Stream used for user-facing diagnostics.

<a id="backlogops.backlog_ops_config.read_backlog_ops_config"></a>

#### read\_backlog\_ops\_config

```python
def read_backlog_ops_config(
        filename: PathOrStr,
        stderr_file: TextIO = sys.stderr,
        auto_ch_hook: Optional[ConfigAutoChangeHook] = None
) -> BacklogOpsConfig
```

Read a backlog-ops configuration from a JSON configuration file.

**Arguments**:

- `filename` - Source JSON configuration file.
- `stderr_file` - Stream used for user-facing diagnostics.
- `auto_ch_hook` - Hook notified when an old file needed
  backward-compatible normalization while reading.
  

**Returns**:

  The loaded configuration.

<a id="backlogops.backlog_ops_config.get_backlog_ops_config"></a>

#### get\_backlog\_ops\_config

```python
def get_backlog_ops_config(
        filename: Optional[PathOrStr],
        stderr_file: TextIO = sys.stderr,
        auto_ch_hook: Optional[ConfigAutoChangeHook] = None
) -> BacklogOpsConfig
```

Return the BacklogOpsConfig to use, reading or reusing as needed.

If a filename is provided, the file is read and the BacklogOpsConfig
is stored and returned. If no filename is provided and there is a
stored BacklogOpsConfig, it is returned. If no filename is provided
and there is no stored BacklogOpsConfig, this function looks for one
in order of precedence:
- File named in $BACKLOGOPS_CFG environment variable
- File backlogops.cfg in folder specified by $BACKLOGOPS_DIR
environment variable
- $HOME/.backlogops.cfg
If a file is found, it is read and the BacklogOpsConfig is stored and
returned. If no file is found, an exception is raised.

**Arguments**:

- `filename` - Source JSON configuration file.
- `stderr_file` - Stream used for user-facing diagnostics.
- `auto_ch_hook` - Hook notified when an old file needed
  backward-compatible normalization while reading.
  

**Raises**:

- `FileNotFoundError` - If $BACKLOGOPS_CFG is set but the file does not
  exist.
- `NotADirectoryError` - If $BACKLOGOPS_DIR is set but the directory
  does not exist.
- `RuntimeError` - If no filename is provided and no stored
  BacklogOpsConfig is found and no file is found in
  the order of precedence.

**Returns**:

  The loaded configuration.

<a id="backlogops.table_create"></a>

# backlogops.table\_create

Open a TableIO file for creating a single table output.

Several writers create a file that holds one table whose format follows
the file name extension (a key list, a list of changes, and so on). They
all resolve the output configuration from the file name, request CREATE
capabilities, and open a TableIO context. This helper holds that shared
setup so each writer only describes the rows it writes.

The writers accept an optional ``file_exists_callback``. TableIO calls it
with the file name when a CREATE would overwrite an existing file:
returning from the callback allows the overwrite, raising refuses it.
Without a callback an existing file is refused. :func:`allow_overwrite` is
a ready callback that always allows the overwrite.

<a id="backlogops.table_create.allow_overwrite"></a>

#### allow\_overwrite

```python
def allow_overwrite(file_name: str) -> None
```

File-exists callback that always allows overwriting the file.

<a id="backlogops.table_create.create_output_table"></a>

#### create\_output\_table

```python
@contextmanager
def create_output_table(
        file_name: PathOrStr,
        stderr_file: TextIO = sys.stderr,
        file_exists_callback: Optional[FileExistsCb] = None
) -> Iterator[TableIO]
```

Yield a TableIO opened to create a one table file.

The output format is resolved from the file name extension and the
file is opened with CREATE access. The yielded TableIO is used to
write the table inside the ``with`` block.

**Arguments**:

- `file_name` - The file to create.
- `stderr_file` - The stream to report errors to.
- `file_exists_callback` - Called when the file already exists, as
  documented for the module. None refuses an
  existing file.
  

**Yields**:

  The TableIO ready to write one table to the file.

<a id="backlogops.jira_io_config"></a>

# backlogops.jira\_io\_config

Jira input and output configuration stored as config-as-json.

A :class:`JiraIOConfig` is the ``jira`` member of the top-level
:class:`backlogops.backlog_ops_config.BacklogOpsConfig`. It groups three
named, reusable parts:

* ``connections`` are named :class:`JiraConnectConfig` objects, each
  describing one Jira server and how its API token is stored;
* ``column_maps`` are named :data:`JiraColumnMap` maps from an internal
  field name to the paths that may reach the value on a Jira issue or
  version;
* ``from_jira_presets`` are named :class:`JiraPreset` objects that tie a
  connection, a backlog column map and a release column map together with
  a default project and a default issue filter for reading from Jira.

Keeping the connections and column maps in their own dictionaries lets
several presets share one connection or one map. A preset refers to them
by name, and :meth:`JiraIOConfig.check_consistency` rejects a preset that
refers to a name that is not defined.

The API token is never written into the configuration file in clear text
unless the user explicitly chooses a clear storage mode (meant for demo
data). The token itself is materialized only at use time by
:meth:`JiraConnectConfig.get_token`, into a private attribute that
config-as-json does not serialize.

<a id="backlogops.jira_io_config.JiraType"></a>

## JiraType Objects

```python
class JiraType(Enum)
```

Jira deployment type, cloud or server.

<a id="backlogops.jira_io_config.TokenStorage"></a>

## TokenStorage Objects

```python
class TokenStorage(Enum)
```

How the Jira API token is stored.

A ``CLEAR`` mode stores the token unprotected and is meant for demo
data only. An ``ENCRYPTED`` mode stores the token encrypted with a
pass phrase the user supplies when the token is stored and when it is
used. A ``FILE`` mode keeps the token in a separate file named by
``token_file_path``; an ``INTERNAL`` mode keeps it in the
configuration itself.

<a id="backlogops.jira_io_config.CLEAR_TOKEN_WARNING"></a>

#### CLEAR\_TOKEN\_WARNING

Warning shown when a token is stored with a clear storage mode.

<a id="backlogops.jira_io_config.JiraAttrType"></a>

## JiraAttrType Objects

```python
class JiraAttrType(Enum)
```

Where the value of a mapped column is found on a Jira object.

ATTRIBUTE is a direct attribute of the issue or version object, such
as ``issue.key`` or ``version.releaseDate``. FIELD is reached under
``issue.fields`` by the remaining path steps, such as
``issue.fields.status.name``. CUSTOM_FIELD is a custom field named by
its id (``customfield_10016``) or by its display name (``Story point
estimate``); the display name is resolved against the live custom
field mapping when reading. FILTERED_FIELD reads a list field under
``issue.fields`` and returns values from the list entries where a
nested attribute matches a configured value.

<a id="backlogops.jira_io_config.JiraAttrPath"></a>

## JiraAttrPath Objects

```python
@dataclass(frozen=True)
class JiraAttrPath()
```

A path to the value of one column on a Jira issue or version.

Fields:
    kind: How the path is interpreted, as documented for
        :class:`JiraAttrType`.
    path: The path steps. ATTRIBUTE and CUSTOM_FIELD use exactly one
        step; FIELD uses one or more steps reached under
        ``issue.fields``. FILTERED_FIELD uses four steps: list field
        name, filter path, expected filter value and value path. The
        filter and value paths use dots between nested attributes.

<a id="backlogops.jira_io_config.DEF_BACKLOG_COLUMN_MAP"></a>

#### DEF\_BACKLOG\_COLUMN\_MAP

A usable default backlog column map for a fresh Jira preset.

The ``level`` field maps to the Jira issue type name (such as 'Story'),
resolved to a level number through the configured levels. The ``release``
field maps to the Jira ``fixVersions`` field, which is a list of
versions; the reader reduces it to a single release name. The
``parent_key`` field maps both to the Cloud parent object and to the old
Jira Software ``Epic Link`` custom field. The ``depends_on_f2s`` field
maps Jira issue links of type ``Blocks`` where the current issue is
blocked by another issue. The ``team`` field maps to a custom field
named ``Team`` (the Atlassian Teams field); adjust it in the wizard when
a project names the field otherwise.

<a id="backlogops.jira_io_config.DEF_RELEASE_COLUMN_MAP"></a>

#### DEF\_RELEASE\_COLUMN\_MAP

A usable default release column map for a fresh Jira preset.

<a id="backlogops.jira_io_config.default_jira_filter"></a>

#### default\_jira\_filter

```python
def default_jira_filter(project: str) -> str
```

Return the default issue filter selecting a project, ordered by rank.

**Arguments**:

- `project` - The Jira project key to select issues from.
  

**Returns**:

  A Jira Query Language filter for every issue in the project,
  ordered by rank ascending.

<a id="backlogops.jira_io_config.JiraConnectConfig"></a>

## JiraConnectConfig Objects

```python
class JiraConnectConfig(Config)
```

Connection to one Jira server and how its API token is stored.

The connection holds the deployment type, the base URL and the login
email, plus the chosen :class:`TokenStorage`. For a file storage mode
the token lives in the file named by ``token_file_path``; for an
internal storage mode it lives in ``stored_token`` (clear text for a
clear mode, an encrypted blob for an encrypted mode). The clear text
token is materialized on demand by :meth:`get_token` into a private
attribute that is never serialized.

<a id="backlogops.jira_io_config.JiraConnectConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create connection defaults, then read them from JSON.

<a id="backlogops.jira_io_config.JiraConnectConfig.parse_converters"></a>

#### parse\_converters

```python
@override
def parse_converters() -> dict[str, ParseConverter]
```

Parse the enum members from their member names.

<a id="backlogops.jira_io_config.JiraConnectConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Check the base URL and the login email are strings.

<a id="backlogops.jira_io_config.JiraConnectConfig.uses_token_file"></a>

#### uses\_token\_file

```python
def uses_token_file() -> bool
```

Return whether the token is stored in a separate file.

<a id="backlogops.jira_io_config.JiraConnectConfig.uses_encryption"></a>

#### uses\_encryption

```python
def uses_encryption() -> bool
```

Return whether the token is stored encrypted with a pass phrase.

<a id="backlogops.jira_io_config.JiraConnectConfig.has_cached_token"></a>

#### has\_cached\_token

```python
def has_cached_token() -> bool
```

Return whether the clear text API token is already cached.

<a id="backlogops.jira_io_config.JiraConnectConfig.get_token"></a>

#### get\_token

```python
def get_token(passphrase: Optional[Callable[[], str]] = None,
              stderr_file: TextIO = sys.stderr) -> str
```

Return the clear text API token, materializing it once.

The token is read from its file or internal storage and decrypted
when an encrypted mode is used; the result is cached so a later
call returns it without asking for the pass phrase again.

**Arguments**:

- `passphrase` - Called to obtain the pass phrase for an encrypted
  mode. Not called for a clear mode.
- `stderr_file` - Stream used for user-facing diagnostics.
  

**Returns**:

  The clear text API token.
  

**Raises**:

- `ValueError` - If a needed token, file path or pass phrase is
  missing, or decryption fails.

<a id="backlogops.jira_io_config.JiraConnectConfig.set_token"></a>

#### set\_token

```python
def set_token(token: str,
              passphrase: Optional[Callable[[], str]] = None,
              stderr_file: TextIO = sys.stderr) -> None
```

Store a clear text API token according to the storage mode.

For an encrypted mode the token is encrypted with the pass phrase;
for a clear mode a strong warning is printed. The token is also
cached so a following :meth:`get_token` returns it directly.

**Arguments**:

- `token` - The clear text API token to store.
- `passphrase` - Called to obtain the pass phrase for an encrypted
  mode. Not called for a clear mode.
- `stderr_file` - Stream the clear-text warning is printed to.
  

**Raises**:

- `ValueError` - If a needed file path or pass phrase is missing.

<a id="backlogops.jira_io_config.JiraPreset"></a>

## JiraPreset Objects

```python
class JiraPreset(Config)
```

A named preset for reading a backlog and releases from Jira.

The preset names the connection to use, the backlog and release
column maps to use, the default project key, and the default issue
filter (Jira Query Language). The names refer to entries in the
enclosing :class:`JiraIOConfig`. The default project is used to read
the releases (versions) even when the caller overrides the issue
filter.

<a id="backlogops.jira_io_config.JiraPreset.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create preset defaults, then read them from JSON.

<a id="backlogops.jira_io_config.JiraPreset.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Check every preset member is a string.

<a id="backlogops.jira_io_config.JiraIOConfig"></a>

## JiraIOConfig Objects

```python
class JiraIOConfig(Config)
```

Jira input and output configuration as the top-level jira member.

Holds the named connections, the named column maps, and the named
presets for reading from Jira, each indexed by name so that several
presets can share one connection or one column map. The column maps
are validated and converted to :class:`JiraAttrPath` values on read
and written back as lists on write; an old file that omits any
sub-section loads with that sub-section empty.

<a id="backlogops.jira_io_config.JiraIOConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create empty defaults, then read the jira configuration.

<a id="backlogops.jira_io_config.JiraIOConfig.nested_configs"></a>

#### nested\_configs

```python
@override
def nested_configs() -> NestedConfigs
```

Declare the connections and presets as nested configurations.

<a id="backlogops.jira_io_config.JiraIOConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Convert the column maps, then check the preset references.

<a id="backlogops.jira_io_config.JiraIOConfig.serialize_converters"></a>

#### serialize\_converters

```python
@override
def serialize_converters() -> SerializeConverters
```

Write the column maps as lists of a kind and path steps.

<a id="backlogops.jira_io_config.JiraIOConfig.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check every preset refers to a defined connection and maps.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a preset refers to a connection or column map
  name that is not defined.

<a id="backlogops.jira_io_config.JiraIOConfig.get_preset"></a>

#### get\_preset

```python
def get_preset(name: str) -> JiraPreset
```

Return the named from-Jira preset.

**Arguments**:

- `name` - The preset name.
  

**Returns**:

  The named preset.
  

**Raises**:

- `KeyError` - If no preset of that name is configured.

<a id="backlogops.team"></a>

# backlogops.team

Define a team, its memberships and their availability over time.

<a id="backlogops.team.FteException"></a>

## FteException Objects

```python
@dataclass
class FteException()
```

Define a full-time equivalent exception.

The full-time equivalent exception is used to override the default
full-time equivalent for a specific period. This can be used to mark
a learning period for a new team member, or a period of time when the
team member works part-time outside of this team.

Fields:
    start_date: The first day of the exception (inclusive).
    end_date: The last day of the exception (inclusive). Must not be
              before start_date.
    fte: The full-time equivalent during the exception. Must not be
         negative.

<a id="backlogops.team.FteException.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of the full-time equivalent exception.

Field types are verified, the date range must be non-empty, and
the full-time equivalent must not be negative.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If the range is empty or the fte is negative.

<a id="backlogops.team.Membership"></a>

## Membership Objects

```python
@dataclass
class Membership()
```

Define how a person belongs to a team over a period of time.

A membership links a person, by name, to the team that holds it. The
person name is looked up in the central person registry of
:class:`~backlogops.available_teams.AvailableTeams`. A person may have
several memberships, in the same or in different teams, which models a
person moving between teams or splitting time across teams over time.

Fields:
    person_name: The name of the person, used as a key into the
                 person registry. Compared case-insensitively. Must
                 not be empty.
    fte: The full-time equivalent the person gives to this team
         outside of any fte_exceptions. 1.0 means full time. Must not
         be negative.
    start_date: The first day of the membership (inclusive), or None
                for a membership that is open at the start.
    end_date: The last day of the membership (inclusive), or None for
              a membership that is open at the end.
    fte_exceptions: Periods with a full-time equivalent that differs
                    from fte, for example a learning period or a period
                    of part-time work in another team. The periods must
                    not overlap.

<a id="backlogops.team.Membership.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of the membership.

Field types are verified, the person name must not be empty, the
full-time equivalent must not be negative, the membership date
range (when both ends are given) must be non-empty, every
fte_exception must be consistent, and the fte_exceptions must not
overlap.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a value is invalid or two fte_exceptions
  overlap.

<a id="backlogops.team.Team"></a>

## Team Objects

```python
@dataclass
class Team()
```

Define a team.

Fields:
    name: The name of the team. Compared case-insensitively. Must be
          unique across all teams and must not be empty.
    velocity: The velocity of the team. Must not be negative.
    sum_fte_at_velocity: The sum of the full-time equivalents of the
                         team members when velocity was measured. Used
                         to rescale the velocity when the team capacity
                         changes. Must be positive.
    sprint_length: The length of the sprint in working days. Must be
                   positive.
    aliases: The aliases for the team. A backlog might refer to the
             team using the team name or an alias. Compared
             case-insensitively. Each alias must be unique and not
             empty.
    members: The list of memberships of the team.

<a id="backlogops.team.Team.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of the team.

Field types are verified, the numeric fields must be within their
documented ranges, and every membership must be consistent.
Uniqueness of the name and aliases across teams is checked by
:meth:`AvailableTeams.check_consistency`, not here.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a field value violates a constraint.

<a id="backlogops.backlog"></a>

# backlogops.backlog

Internal representation of a backlog.

<a id="backlogops.backlog.DEPENDENCY_FIELDS"></a>

#### DEPENDENCY\_FIELDS

Names of the fields that hold dependency keys of a backlog item.

<a id="backlogops.backlog.Status"></a>

## Status Objects

```python
class Status(IntEnum)
```

Status of a backlog item.

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

<a id="backlogops.backlog.BacklogItem"></a>

## BacklogItem Objects

```python
@dataclass
class BacklogItem()
```

Internal representation of a backlog item.

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
             Must not be empty string, must not start or end with
             whitespace, and must not contain tabs, newlines or
             control characters.
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

<a id="backlogops.backlog.BacklogItem.to_dict"></a>

#### to\_dict

```python
def to_dict() -> dict[str, object]
```

Return a dictionary representation of the backlog item.

<a id="backlogops.backlog.BacklogItem.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the internal consistency of the backlog item.

The documented constraints are checked on all member variables.
Field types are verified, the key, release and dependency keys
are checked for valid syntax, and the extra fields are checked
not to shadow a named field. References between items are not
checked here; that is done by :func:`check_backlog_consistency`.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a field value violates a constraint, or if an
  extra field shadows a named field.

<a id="backlogops.backlog.prepare_item_data"></a>

#### prepare\_item\_data

```python
def prepare_item_data(data: dict[str, object],
                      levels: Levels,
                      stderr_file: TextIO = sys.stderr) -> dict[str, object]
```

Return item data with a string level resolved to its number.

A ``level`` given as a string is matched against the level names and
aliases in ``levels`` and replaced by the level number. Integer
levels and absent levels are returned unchanged, so that type and
missing-field checks happen as usual when the data is converted.

**Arguments**:

- `data` - The raw input data for one backlog item.
- `levels` - The levels used to resolve a string level.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The input data, with a string level replaced by its number.
  

**Raises**:

- `ValueError` - If a string level matches no level name or alias.

<a id="backlogops.backlog.get_backlog_item"></a>

#### get\_backlog\_item

```python
def get_backlog_item(data: dict[str, object],
                     levels: Optional[Levels] = None,
                     status_map: Optional[dict[str, Status]] = None,
                     stderr_file: TextIO = sys.stderr) -> BacklogItem
```

Get a backlog item from a dictionary.

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

**Arguments**:

- `data` - The dictionary to get the backlog item from.
- `levels` - The levels used to resolve a string level, or None to
  use :data:`DEFAULT_LEVELS`.
- `status_map` - Extra status names mapped to Status members, matched
  case-insensitively, or None for no extra names.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a mandatory field is missing.
- `TypeError` - If a field has a type that cannot be converted.
- `ValueError` - If a string level matches no level name or alias.
  

**Returns**:

  The backlog item.

<a id="backlogops.backlog.get_backlog"></a>

#### get\_backlog

```python
def get_backlog(datalist: list[dict[str, object]],
                levels: Optional[Levels] = None,
                status_map: Optional[dict[str, Status]] = None,
                stderr_file: TextIO = sys.stderr) -> Backlog
```

Get a backlog from a list of dictionaries.

Each dictionary is converted to a backlog item as documented for
:func:`get_backlog_item`.

**Arguments**:

- `datalist` - The list of dictionaries to get the backlog from.
- `levels` - The levels used to convert level names to level numbers,
  or None to use :data:`DEFAULT_LEVELS`.
- `status_map` - Extra status names mapped to Status members, matched
  case-insensitively, or None for no extra names.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a mandatory field is missing.
- `TypeError` - If a field has a type that cannot be converted.
- `ValueError` - If a string level matches no level name or alias.
  

**Returns**:

  The backlog.

<a id="backlogops.backlog.check_unique_keys"></a>

#### check\_unique\_keys

```python
def check_unique_keys(backlog: Backlog,
                      stderr_file: TextIO = sys.stderr) -> set[str]
```

Check that all backlog item keys are unique.

**Arguments**:

- `backlog` - The backlog to check.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The set of all keys, for reuse by later checks.
  

**Raises**:

- `ValueError` - If two items share the same key.

<a id="backlogops.backlog.check_key_references"></a>

#### check\_key\_references

```python
def check_key_references(backlog: Backlog,
                         known_keys: set[str],
                         stderr_file: TextIO = sys.stderr) -> None
```

Check that parent and dependency keys reference existing items.

**Arguments**:

- `backlog` - The backlog to check.
- `known_keys` - The set of keys that exist in the backlog.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a parent_key or dependency key is unknown.

<a id="backlogops.backlog.event_start"></a>

#### event\_start

```python
def event_start(key: str) -> str
```

Return the start-event node name for a backlog item key.

<a id="backlogops.backlog.event_finish"></a>

#### event\_finish

```python
def event_finish(key: str) -> str
```

Return the finish-event node name for a backlog item key.

<a id="backlogops.backlog.item_dependency_edges"></a>

#### item\_dependency\_edges

```python
def item_dependency_edges(item: BacklogItem) -> list[tuple[str, str]]
```

Return the directed scheduling edges implied by one item.

Each item has a start event and a finish event. An edge ``a -> b``
means that event ``a`` cannot happen before event ``b`` (``a``
depends on ``b``). An item finish depends on its own start. The
dependency lists add finish-to-start, finish-to-finish and
start-to-start edges. A parent relation adds two implicit edges: the
child cannot start before the parent starts, and the parent cannot
finish before the child finishes.

**Arguments**:

- `item` - The backlog item to take the edges from.
  

**Returns**:

  The directed (source, target) event edges of the item.

<a id="backlogops.backlog.build_dependency_graph"></a>

#### build\_dependency\_graph

```python
def build_dependency_graph(backlog: Backlog) -> dict[str, list[str]]
```

Return the scheduling-event dependency graph of a backlog.

The nodes are the start and finish events of the items, named
``'<key>:start'`` and ``'<key>:finish'`` (``:`` cannot appear in a
key). The edges combine the explicit dependency lists with the
implicit parent relations, as described in
:func:`item_dependency_edges`. A cycle in this graph is an
unsatisfiable set of scheduling constraints.

**Arguments**:

- `backlog` - The backlog to build the graph from.
  

**Returns**:

  A mapping from each event node to the events it depends on.

<a id="backlogops.backlog.check_no_cycles"></a>

#### check\_no\_cycles

```python
def check_no_cycles(backlog: Backlog,
                    stderr_file: TextIO = sys.stderr) -> None
```

Check that the scheduling-event graph of a backlog has no cycles.

The graph combines the explicit dependencies with the implicit
parent relations. A self dependency is treated as a cycle of length
one. A valid parent and child nesting is not a cycle, because the
parent and child start and finish events stay distinct.

**Arguments**:

- `backlog` - The backlog to check.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `ValueError` - If a dependency cycle is found.

<a id="backlogops.backlog.check_parent_levels"></a>

#### check\_parent\_levels

```python
def check_parent_levels(backlog: Backlog,
                        items_by_key: dict[str, BacklogItem],
                        stderr_file: TextIO = sys.stderr) -> None
```

Check that each parent is at a higher level than its child.

A parent is a bigger backlog item than its children, so its level
number must be strictly higher than the item that references it. The
parent references are assumed to exist, as already checked by
:func:`check_key_references`.

**Arguments**:

- `backlog` - The backlog to check.
- `items_by_key` - A mapping from each key to its backlog item.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `ValueError` - If a parent is not at a higher level than its child.

<a id="backlogops.backlog.check_backlog_consistency"></a>

#### check\_backlog\_consistency

```python
def check_backlog_consistency(backlog: Backlog,
                              stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of a backlog.

Every item is checked for internal consistency, all keys are checked
for uniqueness, parent and dependency keys are checked to reference
existing items, each parent is checked to be at a higher level than
its child, and the scheduling-event graph is checked to be free of
cycles.

**Arguments**:

- `backlog` - The backlog to check.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `KeyError` - If a key reference is invalid.
- `TypeError` - If a field has the wrong type.
- `ValueError` - If a field value violates a constraint, if keys are
  not unique, if a parent is not at a higher level than its
  child, or if there is a dependency cycle.

<a id="backlogops.available_teams_config"></a>

# backlogops.available\_teams\_config

Store and load AvailableTeams as a config-as-json configuration.

This module bridges the framework-neutral workforce data model in
:mod:`backlogops.available_teams` to the ``config_as_json`` library, in
the same way ``tableio_cfg_json`` bridges TableIO ``ConfigData`` with
``TioJsonConfig``. Each neutral data class gets a small bridge class that
multiply inherits from the data class and from ``Config``. The bridge
classes add JSON reading, writing, and validation, while the neutral data
classes stay the single source of truth for the data shape and the
consistency rules.

Application code that only wants to persist an ``AvailableTeams`` can use
:func:`write_available_teams` and :func:`read_available_teams` and never
touch the bridge classes directly.

<a id="backlogops.available_teams_config.FteExceptionConfig"></a>

## FteExceptionConfig Objects

```python
class FteExceptionConfig(FteException, _BridgeConfig)
```

JSON bridge for one full-time-equivalent exception.

<a id="backlogops.available_teams_config.FteExceptionConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create placeholder defaults, then read one FTE exception.

<a id="backlogops.available_teams_config.FteExceptionConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Parse the date members, then check exception consistency.

<a id="backlogops.available_teams_config.FteExceptionConfig.serialize_converters"></a>

#### serialize\_converters

```python
@override
def serialize_converters() -> SerializeConverters
```

Format the date members as ISO strings on write.

<a id="backlogops.available_teams_config.ExceptionWorkHoursConfig"></a>

## ExceptionWorkHoursConfig Objects

```python
class ExceptionWorkHoursConfig(ExceptionWorkHours, _BridgeConfig)
```

JSON bridge for one work-hours exception (holiday or special).

<a id="backlogops.available_teams_config.ExceptionWorkHoursConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create placeholder defaults, then read one work-hours exception.

<a id="backlogops.available_teams_config.ExceptionWorkHoursConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Parse the date members, then check exception consistency.

<a id="backlogops.available_teams_config.ExceptionWorkHoursConfig.serialize_converters"></a>

#### serialize\_converters

```python
@override
def serialize_converters() -> SerializeConverters
```

Format the date members as ISO strings on write.

<a id="backlogops.available_teams_config.MembershipConfig"></a>

## MembershipConfig Objects

```python
class MembershipConfig(Membership, _BridgeConfig)
```

JSON bridge for one team membership.

<a id="backlogops.available_teams_config.MembershipConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create placeholder defaults, then read one membership.

<a id="backlogops.available_teams_config.MembershipConfig.nested_configs"></a>

#### nested\_configs

```python
@override
def nested_configs() -> NestedConfigs
```

Declare the fte_exceptions list as nested Config objects.

<a id="backlogops.available_teams_config.MembershipConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Parse the optional dates, then check membership consistency.

<a id="backlogops.available_teams_config.MembershipConfig.serialize_converters"></a>

#### serialize\_converters

```python
@override
def serialize_converters() -> SerializeConverters
```

Format the date members as ISO strings on write.

<a id="backlogops.available_teams_config.TeamConfig"></a>

## TeamConfig Objects

```python
class TeamConfig(Team, _BridgeConfig)
```

JSON bridge for one team.

<a id="backlogops.available_teams_config.TeamConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create placeholder defaults, then read one team.

<a id="backlogops.available_teams_config.TeamConfig.nested_configs"></a>

#### nested\_configs

```python
@override
def nested_configs() -> NestedConfigs
```

Declare the members list as nested Config objects.

<a id="backlogops.available_teams_config.TeamConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Check the team consistency.

<a id="backlogops.available_teams_config.PersonConfig"></a>

## PersonConfig Objects

```python
class PersonConfig(Person, _BridgeConfig)
```

JSON bridge for one person.

<a id="backlogops.available_teams_config.PersonConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create placeholder defaults, then read one person.

<a id="backlogops.available_teams_config.PersonConfig.nested_configs"></a>

#### nested\_configs

```python
@override
def nested_configs() -> NestedConfigs
```

Declare the work-hour exceptions as nested Config objects.

<a id="backlogops.available_teams_config.PersonConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

No extra person-level checks beyond the nested exceptions.

<a id="backlogops.available_teams_config.CompanyWorkHoursConfig"></a>

## CompanyWorkHoursConfig Objects

```python
class CompanyWorkHoursConfig(CompanyWorkHours, _BridgeConfig)
```

JSON bridge for the company work hours.

<a id="backlogops.available_teams_config.CompanyWorkHoursConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create defaults, then read the company work hours.

<a id="backlogops.available_teams_config.CompanyWorkHoursConfig.nested_configs"></a>

#### nested\_configs

```python
@override
def nested_configs() -> NestedConfigs
```

Declare the work-hour exceptions as nested Config objects.

<a id="backlogops.available_teams_config.CompanyWorkHoursConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Normalize the week-day schedule, then check consistency.

<a id="backlogops.available_teams_config.CompanyWorkHoursConfig.serialize_converters"></a>

#### serialize\_converters

```python
@override
def serialize_converters() -> SerializeConverters
```

Write the week-day schedule with day-name keys.

<a id="backlogops.available_teams_config.AvailableTeamsConfig"></a>

## AvailableTeamsConfig Objects

```python
class AvailableTeamsConfig(AvailableTeams, _BridgeConfig)
```

JSON bridge for the available workforce (persons and teams).

<a id="backlogops.available_teams_config.AvailableTeamsConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*,
             neutral: Optional[AvailableTeams] = None,
             from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create the bridge from a neutral workforce or from JSON.

``AvailableTeams.__init__`` is intentionally not invoked because
it requires ``persons`` and ``teams`` arguments that the bridge
does not duplicate. ``Config.copy_initial_data`` establishes the
schema from the supplied or default neutral workforce instead.

<a id="backlogops.available_teams_config.AvailableTeamsConfig.nested_configs"></a>

#### nested\_configs

```python
@override
def nested_configs() -> NestedConfigs
```

Declare the persons, teams and company work hours.

<a id="backlogops.available_teams_config.AvailableTeamsConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Check the whole-workforce consistency.

<a id="backlogops.available_teams_config.write_available_teams"></a>

#### write\_available\_teams

```python
def write_available_teams(teams: AvailableTeams,
                          filename: PathOrStr,
                          stderr_file: TextIO = sys.stderr) -> None
```

Validate and write an available workforce to a JSON file.

**Arguments**:

- `teams` - The workforce to store.
- `filename` - Destination JSON configuration file.
- `stderr_file` - Stream used for user-facing diagnostics.

<a id="backlogops.available_teams_config.read_available_teams"></a>

#### read\_available\_teams

```python
def read_available_teams(
        filename: PathOrStr,
        stderr_file: TextIO = sys.stderr) -> AvailableTeamsConfig
```

Read an available workforce from a JSON configuration file.

**Arguments**:

- `filename` - Source JSON configuration file.
- `stderr_file` - Stream used for user-facing diagnostics.
  

**Returns**:

  The loaded workforce. The returned object is an ``AvailableTeams``.

<a id="backlogops.release_backlog_updates"></a>

# backlogops.release\_backlog\_updates

Interaction between releases and backlogs.

<a id="backlogops.release_backlog_updates.ReleaseChange"></a>

## ReleaseChange Objects

```python
@dataclass
class ReleaseChange()
```

A change of the release a backlog item is delivered in.

Both releases are optional, because a backlog item may carry no
release before the change and may end up with no release after it.

<a id="backlogops.release_backlog_updates.BacklogReleaseChange"></a>

## BacklogReleaseChange Objects

```python
class BacklogReleaseChange(NamedTuple)
```

A change of a backlog with changes to releases.

<a id="backlogops.release_backlog_updates.ReleaseDateChange"></a>

## ReleaseDateChange Objects

```python
@dataclass
class ReleaseDateChange()
```

A change of a release date.

Both dates are optional, because a release may have had no date
before the change and may have no date after it.

<a id="backlogops.release_backlog_updates.ReleasesAndDateChanges"></a>

## ReleasesAndDateChanges Objects

```python
class ReleasesAndDateChanges(NamedTuple)
```

Releases and their date changes.

<a id="backlogops.release_backlog_updates.estimate_release_dates"></a>

#### estimate\_release\_dates

```python
def estimate_release_dates(releases: Releases,
                           backlog: Backlog) -> ReleasesAndDateChanges
```

Find estimated release dates from backlog item estimates.

For each release, the estimated date is set to the latest estimated
ready date of the backlog items assigned to the release. A release
with no assigned item that carries an estimated ready date gets no
estimated date (``None``). A change is recorded only for a release
whose estimated date actually changes.

**Arguments**:

- `releases` - The releases to find the estimated dates for.
  The argument is not modified.
- `backlog` - The already estimated backlog to find the estimated dates
  from. The argument is not modified.
  

**Returns**:

  The releases with updated estimated dates and a record of how
  the estimated release dates were changed.

<a id="backlogops.release_backlog_updates.release_plan_on_estimate"></a>

#### release\_plan\_on\_estimate

```python
def release_plan_on_estimate(releases: Releases,
                             buffer: timedelta) -> ReleasesAndDateChanges
```

Set the planned release dates from the estimated release dates.

For each release the planned date is set to the estimated date plus
the buffer. A release with no estimated date gets no planned date
(``None``), as there is nothing to base the plan on. A change is
recorded only for a release whose planned date actually changes.

**Arguments**:

- `releases` - The releases to set the planned release dates for.
  The argument is not modified.
- `buffer` - The buffer or slack to add to the estimated release dates
  to get the planned release dates. Must not be negative.
  

**Returns**:

  The releases with updated planned release dates and a record of
  how the planned release dates were changed.
  

**Raises**:

- `ValueError` - If the buffer is negative.

<a id="backlogops.release_backlog_updates.adjust_release_content"></a>

#### adjust\_release\_content

```python
def adjust_release_content(releases: Releases, backlog: Backlog,
                           buffer: timedelta) -> BacklogReleaseChange
```

Adjust the release content to fit the planned release dates.

Each backlog item that carries an estimated ready date is placed in
the earliest release whose planned date is on or after the item's
estimated ready date plus the buffer. This pushes an item to a later
release when it no longer fits its current one, pulls it to an earlier
release when it now fits sooner, and assigns an item that has no
release yet to the release it is ready in time for. An item that no
planned release is late enough for is left out of every release (its
release becomes ``None``). An item with no estimated ready date keeps
its current release, as there is no basis to place it. A change is
recorded only for an item whose release actually changes.

**Arguments**:

- `releases` - The releases to fit the items into. The argument is not
  modified.
- `backlog` - The already estimated backlog to adjust. The argument is
  not modified.
- `buffer` - The buffer or slack added to the estimated ready dates to
  gain confidence that an item fits a release. Must not be
  negative.
  

**Returns**:

  The backlog with updated release content and a record of how the
  release content was changed.
  

**Raises**:

- `ValueError` - If the buffer is negative.

<a id="backlogops.releases"></a>

# backlogops.releases

Releases related to a backlog.

<a id="backlogops.releases.Release"></a>

## Release Objects

```python
@dataclass
class Release()
```

A release of some BacklogItems.

A release groups backlog items that are delivered together. A
backlog item refers to its release by name through its ``release``
field, so the release name is a stable human-facing label.

Fields:
    name: The name of the release. Required. Must be unique among
          the releases. Must not be empty, must not start or end
          with whitespace, and must not contain tabs, newlines or
          control characters.
    planned_date: The planned date of the release. Optional.
                  The date that is communicated to the customer.
    estimated_date: The estimated date of the release. Optional.
                    The date that the content of the release is
                    estimated to be ready. The estimated date and
                    the planned date are independent of each other;
                    no ordering between them is required.

<a id="backlogops.releases.Release.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the internal consistency of the release.

The field types are verified and the name is checked to be a
well formed label. Uniqueness of the name among several releases
is not checked here; that is done by :func:`check_releases`.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If the name violates the label syntax constraint.

<a id="backlogops.releases.report_unknown_keys"></a>

#### report\_unknown\_keys

```python
def report_unknown_keys(unknown: set[str],
                        stderr_file: TextIO = sys.stderr) -> NoReturn
```

Report unknown release input keys and raise ``KeyError``.

**Arguments**:

- `unknown` - The input keys that match no field of :class:`Release`.
- `stderr_file` - The file to report the error to.
  

**Raises**:

- `KeyError` - Always, after reporting the message.

<a id="backlogops.releases.get_release"></a>

#### get\_release

```python
def get_release(data: dict[str, object],
                stderr_file: TextIO = sys.stderr,
                strict: bool = True) -> Release
```

Get a release from a dictionary.

The dictionary is expected to hold the mandatory ``name`` field and
may hold the optional ``planned_date`` and ``estimated_date``
fields. Date fields given as ISO 8601 strings (such as
``'2026-06-12'``) are converted to ``date`` objects.

**Arguments**:

- `data` - The dictionary to get the release from.
- `stderr_file` - The file to report errors to.
- `strict` - When True (the default), any input key that matches no
  field of :class:`Release` is an error. When False such
  keys are silently ignored.
  

**Returns**:

  The release.
  

**Raises**:

- `KeyError` - If the mandatory ``name`` field is missing, or if
  ``strict`` is True and the data has a key that is not a
  release field.
- `TypeError` - If a field has a type that cannot be converted.

<a id="backlogops.releases.get_releases"></a>

#### get\_releases

```python
def get_releases(datalist: list[dict[str, object]],
                 stderr_file: TextIO = sys.stderr,
                 strict: bool = True) -> Releases
```

Get a list of releases from a list of dictionaries.

Each dictionary is converted to a release as documented for
:func:`get_release`, with the same ``strict`` handling of keys that
do not match a release field.

**Arguments**:

- `datalist` - The list of dictionaries to get the releases from.
- `stderr_file` - The file to report errors to.
- `strict` - Passed to :func:`get_release` for each dictionary. When
  True (the default), unknown keys are an error; when
  False they are ignored.
  

**Returns**:

  The list of releases.
  

**Raises**:

- `KeyError` - If a mandatory ``name`` field is missing, or if
  ``strict`` is True and a dictionary has a key that is not a
  release field.
- `TypeError` - If a field has a type that cannot be converted.

<a id="backlogops.releases.check_releases"></a>

#### check\_releases

```python
def check_releases(releases: Releases,
                   stderr_file: TextIO = sys.stderr) -> None
```

Check the internal consistency of a list of releases.

Every release is checked for internal consistency as documented for
:meth:`Release.check_consistency`, and the release names are checked
to be unique.

**Arguments**:

- `releases` - The list of releases to check.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a name violates the key syntax constraint, or if
  two releases share the same name.

<a id="backlogops.releases.order_releases_by_date"></a>

#### order\_releases\_by\_date

```python
def order_releases_by_date(releases: Releases,
                           by_estimated: bool = False,
                           stderr_file: TextIO = sys.stderr) -> Releases
```

Order a list of releases by date.

The releases are ordered by the planned date, or the estimated date if
``by_estimated`` is True. A release with a None date is placed at the end
of the list. Releases with the same date will keep their original order.

**Arguments**:

- `releases` - The list of releases to order.
- `by_estimated` - If True, order by the estimated date instead of the
  planned date. Default is False.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The ordered list of releases.

<a id="backlogops.jira_read"></a>

# backlogops.jira\_read

Read a backlog and its releases from Jira into BacklogReleases.

A configured :class:`JiraPreset` names the connection, the backlog and
release column maps, the default project and the default issue filter.
:func:`read_backlog_from_jira` connects to Jira, runs the issue
filter (Jira Query Language) to read the backlog items, reads the project
versions to read the releases, and maps each Jira attribute to an
internal field through the preset's column maps. Custom field display
names in a column map (such as 'Story point estimate') are resolved to
their field ids through the live custom field list of the Jira instance.

The caller may override the preset's filter for one read. When no filter
is configured at all, the default filter selects every issue in the
default project, ordered by rank, while the releases always come from the
default project's versions.

A cloud connection authenticates with the login email and the token; a
server connection uses the token as a personal access token. The token
is materialized through :meth:`JiraConnectConfig.get_token`, asking the
supplied pass phrase provider only when an encrypted storage mode needs
it.

<a id="backlogops.jira_read.is_appendable_jira_field"></a>

#### is\_appendable\_jira\_field

```python
def is_appendable_jira_field(name: str) -> bool
```

Return whether duplicate Jira values should be appended.

<a id="backlogops.jira_read.build_backlog_releases"></a>

#### build\_backlog\_releases

```python
def build_backlog_releases(
        issues: Iterable[object],
        versions: Iterable[object],
        fields_list: Iterable[Mapping[str, object]],
        *,
        backlog_map: JiraColumnMap,
        release_map: JiraColumnMap,
        levels: Optional[Levels] = None,
        status_map: Optional[dict[str, Status]] = None,
        stderr_file: TextIO = sys.stderr) -> BacklogReleases
```

Build a BacklogReleases from fetched Jira issues and versions.

Each issue is mapped through ``backlog_map`` into a backlog item, with
a string level resolved through ``levels`` and a string status matched
through ``status_map``; each version is mapped through ``release_map``
into a release. The issue attributes are read relative to the issue
itself and its ``fields``, while a version is read relative to itself.

**Arguments**:

- `issues` - The Jira issues to map into backlog items.
- `versions` - The Jira versions to map into releases.
- `fields_list` - The Jira field descriptors, used to resolve custom
  field display names to their ids.
- `backlog_map` - The internal-field to Jira attribute path map for the
  backlog items.
- `release_map` - The internal-field to Jira attribute path map for the
  releases.
- `levels` - The levels used to resolve a string level, or None for the
  default levels.
- `status_map` - Extra status names mapped to Status members, or None.
- `stderr_file` - Stream used for user-facing diagnostics.
  

**Returns**:

  The backlog and releases read from Jira.

<a id="backlogops.jira_read.resolve_jql"></a>

#### resolve\_jql

```python
def resolve_jql(preset: JiraPreset, filter_override: Optional[str]) -> str
```

Return the Jira Query Language filter to run for a preset.

A non-empty override wins over the preset's default filter, and an
empty filter falls back to the default project filter.

**Arguments**:

- `preset` - The preset that carries the default filter and project.
- `filter_override` - A filter to use instead of the preset's, or None.
  

**Returns**:

  The filter to run.
  

**Raises**:

- `ValueError` - If no filter and no default project are configured.

<a id="backlogops.jira_read.read_backlog_from_jira"></a>

#### read\_backlog\_from\_jira

```python
def read_backlog_from_jira(
        jira_config: JiraIOConfig,
        preset_name: str,
        *,
        filter_override: Optional[str] = None,
        passphrase: Optional[Callable[[], str]] = None,
        levels: Optional[Levels] = None,
        status_map: Optional[dict[str, Status]] = None,
        stderr_file: TextIO = sys.stderr) -> BacklogReleases
```

Read a backlog and its releases from Jira using a named preset.

The preset names the connection and the backlog and release column
maps, all looked up in ``jira_config``. The issues come from the
resolved filter and the releases from the default project's versions.

**Arguments**:

- `jira_config` - The Jira configuration holding the preset, connection
  and column maps.
- `preset_name` - The name of the from-Jira preset to use.
- `filter_override` - A Jira filter to use instead of the preset's.
- `passphrase` - Called to obtain the pass phrase for an encrypted
  token; not called for a clear token.
- `levels` - The levels used to resolve a string level, or None for the
  default levels.
- `status_map` - Extra status names mapped to Status members, or None.
- `stderr_file` - Stream used for user-facing diagnostics.
  

**Returns**:

  The backlog and releases read from Jira.
  

**Raises**:

- `KeyError` - If the preset or a referenced connection or map is
  missing.
- `ValueError` - If no filter and no default project are configured.

<a id="backlogops.jira_read.read_jira_from_config"></a>

#### read\_jira\_from\_config

```python
def read_jira_from_config(config: BacklogOpsConfig,
                          preset_name: str,
                          *,
                          filter_override: Optional[str] = None,
                          passphrase: Optional[Callable[[], str]] = None,
                          stderr_file: TextIO = sys.stderr) -> BacklogReleases
```

Read from Jira using the config's Jira settings, levels and status map.

**Arguments**:

- `config` - The backlog-ops configuration to take the Jira settings,
  levels and status map from.
- `preset_name` - The name of the from-Jira preset to use.
- `filter_override` - A Jira filter to use instead of the preset's.
- `passphrase` - Called to obtain the pass phrase for an encrypted
  token; not called for a clear token.
- `stderr_file` - Stream used for user-facing diagnostics.
  

**Returns**:

  The backlog and releases read from Jira.

<a id="backlogops.table_rows"></a>

# backlogops.table\_rows

Convert backlog items and releases to and from table rows.

A backlog item or a release is represented in a table as one row keyed by
its internal field name. These conversions are shared by the file IO and
by the formatting of table data, so they live in their own module to keep
the dependency order between those parts simple.

<a id="backlogops.table_rows.BACKLOG_FIELDS"></a>

#### BACKLOG\_FIELDS

Internal backlog column names, in a stable write order.

<a id="backlogops.table_rows.RELEASE_FIELDS"></a>

#### RELEASE\_FIELDS

Internal release column names, in a stable write order.

<a id="backlogops.table_rows.LEVEL_COLUMN"></a>

#### LEVEL\_COLUMN

Default column name carrying the numeric backlog item level.

<a id="backlogops.table_rows.LEVEL_NAME_COLUMN"></a>

#### LEVEL\_NAME\_COLUMN

Default column name carrying the named backlog item level.

<a id="backlogops.table_rows.apply_column_map"></a>

#### apply\_column\_map

```python
def apply_column_map(row: Mapping[str, _Cell],
                     names: Mapping[str, Optional[str]]) -> dict[str, _Cell]
```

Return one row with its columns renamed or dropped by a name map.

Three cases are honoured for each column name: a name absent from the
map is kept unchanged, a name mapped to another string is renamed, and
a name mapped to None drops that column from the row.

<a id="backlogops.table_rows.map_column_order"></a>

#### map\_column\_order

```python
def map_column_order(order: list[str],
                     names: Mapping[str, Optional[str]]) -> list[str]
```

Return a column order with names renamed or dropped by a name map.

The same three cases as :func:`apply_column_map` are honoured, so the
order stays consistent with rows passed through that function.

<a id="backlogops.table_rows.item_to_row"></a>

#### item\_to\_row

```python
def item_to_row(item: BacklogItem) -> dict[str, Value]
```

Return one backlog item as a row keyed by internal field name.

<a id="backlogops.table_rows.release_to_row"></a>

#### release\_to\_row

```python
def release_to_row(release: Release) -> dict[str, Value]
```

Return one release as a row keyed by internal field name.

<a id="backlogops.table_rows.row_to_item"></a>

#### row\_to\_item

```python
def row_to_item(row: Mapping[str, object],
                levels: Optional[Levels] = None,
                status_map: Optional[dict[str, Status]] = None,
                stderr_file: TextIO = sys.stderr) -> BacklogItem
```

Return a backlog item from a row keyed by internal field name.

A string status is matched case-insensitively against ``status_map``
before the built-in status-name matching, as documented for
:func:`backlogops.backlog.get_backlog_item`.

<a id="backlogops.table_rows.row_to_release"></a>

#### row\_to\_release

```python
def row_to_release(row: Mapping[str, object],
                   stderr_file: TextIO = sys.stderr) -> Release
```

Return a release from a row keyed by internal field name.

<a id="backlogops.table_rows.display_level_order"></a>

#### display\_level\_order

```python
def display_level_order(order: list[str], display: LevelDisplay) -> list[str]
```

Return a column order with the level column expanded for display.

The single internal ``level`` column is replaced by the numeric
column, the named column, or both, as chosen by ``display``. Every
other column is kept in place.

<a id="backlogops.table_rows.display_level_rows"></a>

#### display\_level\_rows

```python
def display_level_rows(rows: DictData[ValueFmt],
                       levels: Levels,
                       display: LevelDisplay,
                       stderr_file: TextIO = sys.stderr) -> DictData[ValueFmt]
```

Return rows with the level column expanded for display.

Each row's single internal ``level`` cell becomes the numeric column,
the named column, or both, as chosen by ``display``. A level number
with no configured name is shown as its number, and one information
message then lists those numbers.

<a id="backlogops.table_rows.fold_level_name"></a>

#### fold\_level\_name

```python
def fold_level_name(rows: DictData[Value],
                    stderr_file: TextIO = sys.stderr) -> None
```

Fold a ``level name`` column into the ``level`` column in place.

When a row has both columns the numeric ``level`` column is kept and
the ``level name`` column is discarded. When only the ``level name``
column is present its value becomes the level, to be resolved by the
item conversion. The ``level name`` column is always removed so it is
never stored as an extra field. One information message is printed
when both columns appeared together.

<a id="backlogops.io_config"></a>

# backlogops.io\_config

Configuration for reading and writing tables with TableIO.

A backlog and its releases are read from and written to tabular files
(Excel, ODS, CSV, and more) using TableIO. The durable TableIO settings
for one input or one output are stored as a :class:`TioJsonConfig`. On
top of that this module adds per-table column-name maps, so the columns
in a user's file can have other names than the internal field names of
the data model.

An input endpoint is described by an :class:`InputFormatConfig` and an
output endpoint by an :class:`OutputFormatConfig`. Both wrap one
``TioJsonConfig`` and the direction-specific column-name maps:

* an input endpoint carries one map per table, ``backlog_to_internal``
  and ``release_to_internal``, each translating an external file column
  name to an internal field name; several external names may map to the
  same internal field;
* an output endpoint carries one map per table, ``backlog_to_external``
  and ``release_to_external``, each translating an internal field name to
  the external column name to write.

Every input, output and GUI map honours three cases for a column name: a
name absent from the map is read, written or shown unchanged, a name
mapped to another string is renamed, and a name mapped to None drops that
column (for an input map the named file column is discarded).
The :class:`GuiDisplayConfig` carries the same per-table maps and level
display, but no TableIO endpoint, deciding how a backlog and its releases
are shown on screen.

:func:`resolve_input_config` and :func:`resolve_output_config` turn a
command-line value into such a configuration. The value may be empty
(then the format is inferred from the data file name extension), a preset
name (looked up among named presets stored elsewhere, typically in the
backlog-ops configuration file), or the name of a stand-alone configuration
file.

<a id="backlogops.io_config.EXTENSION_FORMATS"></a>

#### EXTENSION\_FORMATS

Map a data file name extension to a TableIO format name.

<a id="backlogops.io_config.PRESET_NAME_RE"></a>

#### PRESET\_NAME\_RE

A configuration value made only of letters and digits is a preset.

<a id="backlogops.io_config.parse_status_input_map"></a>

#### parse\_status\_input\_map

```python
def parse_status_input_map(
        member_name: str,
        raw: object,
        stderr_file: TextIO = sys.stderr) -> dict[str, Status]
```

Return a validated status-name map from raw configuration data.

Each key is an external status name and each value is a Status (or a
Status member name such as ``'IN_PROGRESS'``). Keys must be non-empty
strings and must be unique case-insensitively, because a status name
is matched without regard to case when reading a backlog. Each value
is converted to a Status member.

**Arguments**:

- `member_name` - The member name used in any error message.
- `raw` - The raw configuration value to validate and convert.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The status names mapped to their Status members.
  

**Raises**:

- `TypeError` - If ``raw`` is not a dict or a value is not a Status.
- `ValueError` - If a key is empty or duplicates another (case-insensitive).

<a id="backlogops.io_config.InputFormatConfig"></a>

## InputFormatConfig Objects

```python
class InputFormatConfig(_FormatConfig)
```

TableIO input endpoint with per-table file-to-internal maps.

The backlog table and the releases table each have their own map from
a file column name to an internal field name (``backlog_to_internal``
and ``release_to_internal``); each honours the three cases of
:func:`backlogops.table_rows.apply_column_map`: a file column absent
from the map is read unchanged, a mapped file column is renamed to the
internal field, and a file column mapped to None is discarded. Several
file columns may map to the same internal field. The maps default to
empty; an older file storing a single ``to_internal`` map has it copied
into both maps, keeping only release-field targets in the releases map.

The ``status_input_map`` maps extra external status names to Status
members (matched case-insensitively when reading), overriding the
global map of the top-level configuration for this preset. It defaults
to empty and is absent from an older file.

<a id="backlogops.io_config.InputFormatConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create the input map defaults, then run the shared constructor.

<a id="backlogops.io_config.InputFormatConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Check the column maps, then convert the status input map.

<a id="backlogops.io_config.OutputFormatConfig"></a>

## OutputFormatConfig Objects

```python
class OutputFormatConfig(_FormatConfig)
```

TableIO output endpoint with per-table internal-to-external maps.

The backlog table and the releases table each have their own
internal-to-external column-name map (``backlog_to_external`` and
``release_to_external``); each honours the three cases of
:func:`backlogops.table_rows.apply_column_map`. The endpoint also
carries a :class:`LevelDisplay`, deciding whether a backlog item level
is written as its number, its name, or both. The maps default to empty
and the display defaults to :data:`LevelDisplay.BOTH`; any of them may
be absent from an older file, in which case the default applies.

<a id="backlogops.io_config.OutputFormatConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create the output defaults, then run the shared constructor.

<a id="backlogops.io_config.OutputFormatConfig.parse_converters"></a>

#### parse\_converters

```python
@override
def parse_converters() -> dict[str, ParseConverter]
```

Parse the level display member from its enum member name.

<a id="backlogops.io_config.make_input_config"></a>

#### make\_input\_config

```python
def make_input_config(tableio: TioJsonConfig,
                      backlog_to_internal: dict[str, Optional[str]],
                      release_to_internal: dict[str, Optional[str]],
                      status_input_map: Optional[dict[str, Status]] = None,
                      stderr_file: TextIO = sys.stderr) -> InputFormatConfig
```

Return an input config from a TableIO config, maps and status map.

<a id="backlogops.io_config.make_output_config"></a>

#### make\_output\_config

```python
def make_output_config(tableio: TioJsonConfig,
                       backlog_to_external: dict[str, Optional[str]],
                       release_to_external: dict[str, Optional[str]],
                       level_display: LevelDisplay = LevelDisplay.BOTH,
                       stderr_file: TextIO = sys.stderr) -> OutputFormatConfig
```

Return an output config from a TableIO config, maps and display.

<a id="backlogops.io_config.GuiDisplayConfig"></a>

## GuiDisplayConfig Objects

```python
class GuiDisplayConfig(Config)
```

How a backlog and its releases are shown in the GUI.

This mirrors the display part of an :class:`OutputFormatConfig`,
without the TableIO endpoint configuration. It carries the per-table
column-name maps ``backlog_to_external`` and ``release_to_external``
(each honouring the three cases of
:func:`backlogops.table_rows.apply_column_map`) and a
:class:`LevelDisplay`. The maps default to empty and the display
defaults to :data:`LevelDisplay.BOTH`; any of them may be absent from
an older file, in which case the default applies.

<a id="backlogops.io_config.GuiDisplayConfig.__init__"></a>

#### \_\_init\_\_

```python
def __init__(from_json_data_text: Optional[str] = None,
             from_json_filename: Optional[PathOrStr] = None,
             stderr_file: TextIO = sys.stderr) -> None
```

Create the display defaults, then read them from JSON.

<a id="backlogops.io_config.GuiDisplayConfig.parse_converters"></a>

#### parse\_converters

```python
@override
def parse_converters() -> dict[str, ParseConverter]
```

Parse the level display member from its enum member name.

<a id="backlogops.io_config.GuiDisplayConfig.get_validation_plan"></a>

#### get\_validation\_plan

```python
@override
def get_validation_plan(stderr_file: TextIO) -> ValidationPlan
```

Check each column-name map allows a string or None value.

<a id="backlogops.io_config.resolve_input_config"></a>

#### resolve\_input\_config

```python
def resolve_input_config(
        value: Optional[str],
        *,
        data_file: PathOrStr,
        presets: Optional[dict[str, InputFormatConfig]] = None,
        auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
        stderr_file: TextIO = sys.stderr) -> InputFormatConfig
```

Resolve a command-line input config value to an input config.

An empty ``value`` infers the format from ``data_file``. A value of
only letters and digits is a preset name looked up in ``presets``.
Any other value is the path of a stand-alone input config file.

**Arguments**:

- `value` - The ``--input-config`` value, or None for inference.
- `data_file` - The input data file, used for format inference.
- `presets` - Named input presets, typically from the backlog-ops config.
- `auto_ch_hook` - Hook notified when a stand-alone input config file
  needed backward-compatible normalization while reading.
- `stderr_file` - Stream used for user-facing diagnostics.
  

**Returns**:

  The resolved input configuration.
  

**Raises**:

- `ValueError` - The format cannot be inferred or the preset is unknown.

<a id="backlogops.io_config.resolve_output_config"></a>

#### resolve\_output\_config

```python
def resolve_output_config(
        value: Optional[str],
        *,
        data_file: PathOrStr,
        presets: Optional[dict[str, OutputFormatConfig]] = None,
        auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
        stderr_file: TextIO = sys.stderr) -> OutputFormatConfig
```

Resolve a command-line output config value to an output config.

An empty ``value`` infers the format from ``data_file``. A value of
only letters and digits is a preset name looked up in ``presets``.
Any other value is the path of a stand-alone output config file.

**Arguments**:

- `value` - The ``--output-config`` value, or None for inference.
- `data_file` - The output data file, used for format inference.
- `presets` - Named output presets, typically from the backlog-ops config.
- `auto_ch_hook` - Hook notified when a stand-alone output config file
  needed backward-compatible normalization while reading.
- `stderr_file` - Stream used for user-facing diagnostics.
  

**Returns**:

  The resolved output configuration.
  

**Raises**:

- `ValueError` - The format cannot be inferred or the preset is unknown.

<a id="backlogops.blo_version_reporter"></a>

# backlogops.blo\_version\_reporter

Version reporter for the backlogops package.

<a id="backlogops.blo_version_reporter.BloVersionReporter"></a>

## BloVersionReporter Objects

```python
class BloVersionReporter(VersionReporter)
```

Version reporter for the backlogops package.

<a id="backlogops.blo_version_reporter.BloVersionReporter.package_names"></a>

#### package\_names

```python
@override
def package_names() -> list[str]
```

Return the package names that this package reports.

<a id="backlogops.blo_version_reporter.BloVersionReporter.get_app_support_expires"></a>

#### get\_app\_support\_expires

```python
@override
def get_app_support_expires() -> dict[date, str]
```

Return when this package will stop supporting older Python.

<a id="backlogops.blo_version_reporter.BloVersionReporter.get_main_package_name"></a>

#### get\_main\_package\_name

```python
@override
@classmethod
def get_main_package_name(cls) -> str
```

Return the package treated as the main application package.

<a id="backlogops.blo_version_reporter.BloVersionReporter.recommended_python"></a>

#### recommended\_python

```python
@override
@classmethod
def recommended_python(cls) -> Version
```

Return the Python version this package recommends.

<a id="backlogops.date_ranges"></a>

# backlogops.date\_ranges

Helpers for validating inclusive date ranges.

<a id="backlogops.date_ranges.check_date_range"></a>

#### check\_date\_range

```python
def check_date_range(field_name: str,
                     start: date,
                     end: date,
                     stderr_file: TextIO = sys.stderr,
                     subject: str = 'Backlog item') -> None
```

Check that an inclusive date range is not empty.

The range covers every day from ``start`` to ``end`` inclusive, so
``start`` must not be after ``end``.

**Arguments**:

- `field_name` - The name of the field that holds the range.
- `start` - The first day of the range.
- `end` - The last day of the range.
- `stderr_file` - The file to report errors to.
- `subject` - What owns the field, used to start error messages.
  

**Raises**:

- `ValueError` - If ``start`` is after ``end``.

<a id="backlogops.date_ranges.check_no_overlap"></a>

#### check\_no\_overlap

```python
def check_no_overlap(field_name: str,
                     ranges: list[tuple[date, date]],
                     stderr_file: TextIO = sys.stderr,
                     subject: str = 'Backlog item') -> None
```

Check that inclusive date ranges do not share a day.

Each range must already be valid (start not after end). The ranges
are sorted by start day and each is compared with the next, so an
overlap is found in a single pass.

**Arguments**:

- `field_name` - The name of the field that holds the ranges.
- `ranges` - The inclusive ``(start, end)`` ranges to check.
- `stderr_file` - The file to report errors to.
- `subject` - What owns the field, used to start error messages.
  

**Raises**:

- `ValueError` - If two ranges share a day.

<a id="backlogops.jira_token"></a>

# backlogops.jira\_token

Encrypt and decrypt a Jira API token with a pass phrase.

The encryption is pass-phrase based and stores no key of its own: a
Fernet key is derived from the pass phrase and a fresh random salt with
PBKDF2-HMAC-SHA256. The salt is stored next to the ciphertext, so the
same pass phrase recreates the key when the token is later read. The
caller supplies the pass phrase both when a token is encrypted and when
it is decrypted; there is no key store to manage.

<a id="backlogops.jira_token.encrypt_token"></a>

#### encrypt\_token

```python
def encrypt_token(token: str, passphrase: str) -> str
```

Return the token encrypted with the pass phrase as a text blob.

**Arguments**:

- `token` - The plain text API token to encrypt.
- `passphrase` - The pass phrase to derive the encryption key from.
  

**Returns**:

  A url-safe base64 text blob holding the salt and the ciphertext.
  

**Raises**:

- `ValueError` - If the pass phrase is empty.

<a id="backlogops.jira_token.decrypt_token"></a>

#### decrypt\_token

```python
def decrypt_token(blob_text: str, passphrase: str) -> str
```

Return the token decrypted from a blob with the pass phrase.

**Arguments**:

- `blob_text` - The text blob produced by :func:`encrypt_token`.
- `passphrase` - The pass phrase used when the token was encrypted.
  

**Returns**:

  The decrypted plain text API token.
  

**Raises**:

- `ValueError` - If the pass phrase is wrong or the blob is corrupt.

<a id="backlogops.levels"></a>

# backlogops.levels

Levels of a backlog item.

<a id="backlogops.levels.LevelDisplay"></a>

## LevelDisplay Objects

```python
class LevelDisplay(Enum)
```

How a backlog item level is represented in a table or display.

NUMERIC writes only the level number, NAME writes only the level
name, and BOTH writes the number and the name in separate columns.

<a id="backlogops.levels.Level"></a>

## Level Objects

```python
@dataclass
class Level()
```

A level of a backlog item.

Fields:
    level: The level of the backlog item. Required. Must be an integer.
           Usually a positive integer, but can be negative for special
           cases. A higher level means a bigger backlog item.
           A lower level means a smaller, more detailed backlog item.
    name: The name of the level. Required. Must be a string.
          Must not be empty, must not start or end with whitespace,
          and must not contain tabs, newlines or control characters.
          Must be unique within the Levels.
    aliases: The aliases of the level. Optional. Must be a list of strings.
             For instance if level 1 is called "Story", it may have the
             aliases "Task" and "Bug".
             The aliases are used if a backlog item is converted from a
             tool that have different names for the same level.
             Each alias must not be empty, must not start or end with
             whitespace, and must not contain tabs, newlines or control
             characters.
             Must be unique within the Levels and must not be the same
             as any name used in the Levels.

<a id="backlogops.levels.Level.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of the level.

The documented constraints are checked on all member variables.
The name and aliases are checked as human-facing labels.
Uniqueness across levels is checked by
:func:`check_levels_consistency`, not here.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a field value violates a constraint.

<a id="backlogops.levels.DEFAULT_LEVELS"></a>

#### DEFAULT\_LEVELS

The default levels for backlog items.

<a id="backlogops.levels.report_duplicate_label"></a>

#### report\_duplicate\_label

```python
def report_duplicate_label(label: str,
                           existing: str,
                           stderr_file: TextIO = sys.stderr) -> NoReturn
```

Report a duplicate level name or alias and raise ``KeyError``.

**Arguments**:

- `label` - The label that duplicates an earlier one.
- `existing` - The earlier label it collides with.
- `stderr_file` - The file to report the error to.
  

**Raises**:

- `KeyError` - Always, after reporting the message.

<a id="backlogops.levels.check_levels_consistency"></a>

#### check\_levels\_consistency

```python
def check_levels_consistency(levels: Levels,
                             stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of the levels.

The documented constraints are checked on all levels. Each dict key
must match the ``level`` field of its value. Names and aliases are
checked for uniqueness across all levels using case-insensitive
comparison, so that a name and an alias may not differ only in case.

**Arguments**:

- `levels` - The levels to check.
- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a field value violates a constraint, or a dict key
  does not match its level number.
- `KeyError` - If a name or alias is not unique (case-insensitive).

<a id="backlogops.levels.levels_from_list"></a>

#### levels\_from\_list

```python
def levels_from_list(level_list: list[Level],
                     stderr_file: TextIO = sys.stderr) -> Levels
```

Return the levels keyed by level number from a list of levels.

Each level is indexed under its own level number. A level number
that appears more than once is rejected, because the levels mapping
cannot hold two levels with the same number. The resulting mapping
is then checked with :func:`check_levels_consistency`.

**Arguments**:

- `level_list` - The levels to index by their level number.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The levels keyed by their level number.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If a level value violates a constraint or a level
  number is used more than once.
- `KeyError` - If a name or alias is not unique (case-insensitive).

<a id="backlogops.levels.level_number_from_name"></a>

#### level\_number\_from\_name

```python
def level_number_from_name(name: str,
                           levels: Levels,
                           stderr_file: TextIO = sys.stderr) -> int
```

Return the level number whose name or alias matches ``name``.

Matching is case-insensitive but otherwise exact (no prefix or
fuzzy matching). The level name and all of its aliases are
considered. The levels are assumed to be consistent, as checked by
:func:`check_levels_consistency`.

**Arguments**:

- `name` - The level name or alias to look up.
- `levels` - The levels to search.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  The level number of the matching level.
  

**Raises**:

- `ValueError` - If no level name or alias matches ``name``.

<a id="backlogops.levels.level_name"></a>

#### level\_name

```python
def level_name(number: int, levels: Levels) -> Optional[str]
```

Return the configured name for a level number, or None when unknown.

**Arguments**:

- `number` - The level number to look up.
- `levels` - The levels to search.
  

**Returns**:

  The name of the level with that number, or None when no level
  with that number is configured.

<a id="backlogops.backlog_releases_io"></a>

# backlogops.backlog\_releases\_io

Read and write a backlog and its releases as tables with TableIO.

A backlog and its releases form two tables. They are written to one file
(and read back) using TableIO, which supports several tables in one sheet
separated by headings. Reading walks the tables in the file and tells a
backlog table from a releases table by their columns: a table with a
``key`` column is the backlog, a table with a ``name`` column is the
releases.

The internal field names of the data model can differ from the column
names in the file. An :class:`InputFormatConfig` carries one
external-to-internal map per table (``backlog_to_internal`` and
``release_to_internal``), and an :class:`OutputFormatConfig` carries one
internal-to-external map per table (``backlog_to_external`` and
``release_to_external``). Each map honours the three cases of
:func:`backlogops.table_rows.apply_column_map`: an absent name is read or
written unchanged, a mapped name is renamed, and a name mapped to None
drops that column. The dependency lists of a backlog item are stored as
one space separated string per dependency kind, and the extra fields of a
backlog item become extra columns.

The level of a backlog item is written as a numeric ``level`` column, a
named ``level name`` column, or both, as the output configuration's
:class:`LevelDisplay` decides. Both columns are recognised when reading;
when both appear the numeric ``level`` column wins and the ``level name``
column is ignored.

<a id="backlogops.backlog_releases_io.BACKLOG_HEADING"></a>

#### BACKLOG\_HEADING

Heading written before the backlog table.

<a id="backlogops.backlog_releases_io.RELEASE_HEADING"></a>

#### RELEASE\_HEADING

Heading written before the releases table.

<a id="backlogops.backlog_releases_io.read_backlog_releases"></a>

#### read\_backlog\_releases

```python
def read_backlog_releases(data_file: PathOrStr,
                          config: InputFormatConfig,
                          levels: Optional[Levels] = None,
                          status_map: Optional[dict[str, Status]] = None,
                          stderr_file: TextIO = sys.stderr) -> BacklogReleases
```

Read a backlog, releases, or both from one file.

Each table in the file is read and classified by its columns. The
column names are translated to internal field names through the input
configuration before classification and conversion. A ``level`` and a
``level name`` column are both recognised; when both are present the
numeric ``level`` column is used and the ``level name`` column is
ignored. A string status is matched case-insensitively against the
effective status map, which merges the given library-wide ``status_map``
with the input configuration's own ``status_input_map`` (the latter
overriding per name). Field values are converted to their internal
types; consistency across items is not checked here.

**Arguments**:

- `data_file` - The data file to read.
- `config` - The input configuration (format, column-name maps and
  per-input status map).
- `levels` - The levels used to resolve a string level, or None for
  the default levels.
- `status_map` - The library-wide status map, or None when absent. It
  is merged with the input configuration's own status map.
- `stderr_file` - Stream used for user-facing diagnostics.
  

**Returns**:

  The backlog and releases found in the file. Either may be empty.
  

**Raises**:

- `KeyError` - A mandatory field is missing in a row.
- `TypeError` - A field value has a type that cannot be converted.
- `ValueError` - A table cannot be classified as backlog or releases.

<a id="backlogops.backlog_releases_io.write_backlog_releases"></a>

#### write\_backlog\_releases

```python
def write_backlog_releases(
        data: BacklogReleases,
        data_file: PathOrStr,
        config: OutputFormatConfig,
        format_rules: Optional[FormatRules] = None,
        levels: Optional[Levels] = None,
        stderr_file: TextIO = sys.stderr,
        file_exists_callback: Optional[FileExistsCb] = None) -> None
```

Write a backlog, releases, or both to one file.

Each non-empty table is written with a heading before it, so several
tables can share one file. Internal field names are translated to
external column names through the output configuration, using its
backlog map for the backlog table and its releases map for the
releases table; a name mapped to None drops that column. The level of
a backlog item is written as its number, its name, or both, as the
output configuration's :class:`LevelDisplay` decides, using ``levels``
to translate a number to a name. The format rules decide the table
order, the borders, the filter range and the cell formatting; when
omitted the default :class:`FormatRules` apply.

**Arguments**:

- `data` - The backlog and releases to write.
- `data_file` - The data file to create.
- `config` - The output configuration (format, per-table column-name
  maps and level display).
- `format_rules` - How to format the written data, or None for the
  default format rules.
- `levels` - The levels used to translate a level number to a name, or
  None for the default levels.
- `stderr_file` - Stream used for user-facing diagnostics.
- `file_exists_callback` - Called when the file already exists, as
  documented for :mod:`backlogops.table_create`.
  None refuses an existing file.

<a id="backlogops.backlog_ops_wizard"></a>

# backlogops.backlog\_ops\_wizard

Interactively build a workforce or a full backlog-ops configuration.

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

<a id="backlogops.backlog_ops_wizard.available_teams_wizard"></a>

#### available\_teams\_wizard

```python
def available_teams_wizard(ui_bridge: WizardUiBridge) -> AvailableTeams
```

Interactively create an available workforce configuration.

**Arguments**:

- `ui_bridge` - Bridge between the wizard and the user interface.
  

**Returns**:

  The workforce entered by the user. Field values are individually
  valid, but whole-workforce consistency is only enforced when the
  result is stored.
  

**Raises**:

- `EOFError` - The input ended, or the user abandoned the wizard.

<a id="backlogops.backlog_ops_wizard.backlog_ops_wizard"></a>

#### backlog\_ops\_wizard

```python
def backlog_ops_wizard(ui_bridge: WizardUiBridge) -> BacklogOpsConfig
```

Interactively create a backlog-ops configuration.

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

**Arguments**:

- `ui_bridge` - Bridge between the wizard and the user interface.
  

**Returns**:

  The backlog-ops configuration, ready to be written to a file.
  

**Raises**:

- `EOFError` - The input ended, or the user abandoned the wizard.

<a id="backlogops.order_by_dependencies"></a>

# backlogops.order\_by\_dependencies

Order a backlog by dependencies.

<a id="backlogops.order_by_dependencies.DependencyMode"></a>

## DependencyMode Objects

```python
class DependencyMode(Enum)
```

Mode to determine backlog position of items with dependencies.

EARLY: All items that take part in a dependency are placed as early
       as possible, before the items that take part in no
       dependency. This packs the dependency chains at the front and
       leaves a buffer of independent items after the last dependent
       item, to reduce the risk of delays in a chain of dependencies.
EVEN:  Items that take part in a dependency are spread out so that
       the dependency chains are as evenly distributed as possible
       over the complete backlog. The independent items fill the gaps
       between them. This may create a small time buffer between each
       item in a dependency chain.
KEEP:  Items that take part in no dependency keep their original
       relative order, and only the items that take part in a
       dependency are moved, and only as far as a dependency forces
       them to move. The idea is that someone has already put work
       into the order of the backlog, and we should not change it
       without a good reason. This is the default behavior.

<a id="backlogops.order_by_dependencies.order_by_dependencies"></a>

#### order\_by\_dependencies

```python
def order_by_dependencies(backlog: Backlog,
                          *,
                          later: bool = False,
                          mode: DependencyMode = DependencyMode.KEEP,
                          space_around: Optional[str | Sequence[str]] = None,
                          stderr_file: TextIO = sys.stderr) -> Backlog
```

Order a backlog by dependencies.

A new backlog is returned; the argument is not modified. If no item
takes part in any dependency the argument backlog is returned
unchanged (the same object). The backlog is ordered so that a team
can start the items in backlog order without starting an item before
the items it depends on. The dependencies are taken from the start
and finish event graph of the backlog, which combines the explicit
dependency lists with the implicit parent relations. The backlog
position of an item is the order in which the team starts it, so only
a dependency that constrains the start of an item moves that item;
a finish-to-finish dependency, which only constrains completion, does
not move an item by itself.

**Arguments**:

- `backlog` - The backlog to order. The argument is not modified.
- `later` - How a dependency that is not yet satisfied is resolved.
  If False (the default) the prerequisite item is pulled to a
  position just before the dependent item, and the dependent
  item keeps its position. If True the dependent item is pushed
  to a position just after its prerequisites, and the
  prerequisite items keep their position.
- `mode` - How items that take part in a dependency are placed in
  relation to items that take part in no dependency, as
  documented for :class:`DependencyMode`. The default is KEEP.
- `space_around` - Key or keys of items that should have as many other
  items as possible placed between them and the items they
  depend on, and between them and the items that depend on them.
  For each named item the prerequisites are pulled as early as
  possible and the items that depend on it are pushed as late as
  possible, and the named item is centered among the remaining
  items. This is useful when there is a big risk of delays in a
  chain of dependencies. It only works well for one or very few
  items. None means no item is treated this way.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  A new backlog with the items ordered by dependencies, or the
  argument backlog unchanged when no item takes part in a
  dependency.
  

**Raises**:

- `TypeError` - If space_around is neither None, a string, nor a
  sequence of strings.
- `KeyError` - If a space_around key is not the key of a backlog item.
- `RuntimeError` - If space_around names more keys than allowed: more
  than five, or more than ten percent of a backlog of fewer
  than fifty items.

<a id="backlogops.backlog_in_release_order"></a>

# backlogops.backlog\_in\_release\_order

Functions to sort backlog items in release order.

<a id="backlogops.backlog_in_release_order.backlog_in_release_order"></a>

#### backlog\_in\_release\_order

```python
def backlog_in_release_order(backlog: Backlog,
                             releases: Releases,
                             *,
                             honor_dependencies: bool = False,
                             later: bool = False,
                             stderr_file: TextIO = sys.stderr) -> Backlog
```

Return the backlog items ordered to follow the release order.

A new backlog is returned and the ``backlog`` argument is never
modified, not even when it is already in release order.

The release order is taken as is from the ``releases`` list: items
are grouped by release in the order the releases appear in that list.
This function does not sort the releases by date; order the releases
first (for example with
:func:`backlogops.releases.order_releases_by_date`) when a date order
is wanted. Items that share a release keep their original relative
order from ``backlog``. An item with no release, or with a release
that is not in the ``releases`` list, is placed after the items of the
last listed release, again keeping its original relative order. A
release named by an item but missing from ``releases`` is reported to
``stderr_file`` but does not raise.

When ``honor_dependencies`` is False (the default) this grouping by
release is the whole result, and ``later`` has no effect.

When ``honor_dependencies`` is True the result is still led by the
release order, but no item is placed before an item that must be
delivered before it. An item ``X`` must be delivered before an item
``Y`` when ``Y`` names ``X`` in ``depends_on_f2s`` or
``depends_on_f2f``, or when ``X`` is a child of ``Y`` (so a child is
always placed before its parent). A ``depends_on_s2s`` reference does
not affect the order, because it constrains only the start of an item,
not its delivery. The result is always a valid delivery order, and
references to keys that are not in the backlog are ignored.

A dependency can disagree with the release order: a prerequisite may
be planned for a *later* release than the item that depends on it.
The ``later`` argument chooses how to resolve such a conflict, and it
matters only when ``honor_dependencies`` is True:

- ``later`` False (the default) moves the *prerequisite earlier*. The
item that depends on it keeps its release, and the prerequisite is
delivered ahead of its own release so that it is ready in time. The
dependent's release wins and pulls its prerequisites forward. This
is useful when the planned release of the dependent must hold.

- ``later`` True moves the *dependent later*. The prerequisite keeps
its release, and the item that depends on it is delivered after the
prerequisite, behind its own release. The prerequisite's release
wins and pushes its dependents back. This is useful when the
planned release of the prerequisite must hold.

Worked example. Item ``builder`` is planned for the first release but
depends on item ``engine`` planned for the second release, so
``engine`` must be delivered before ``builder``. With ``later`` False
the result keeps ``builder`` in the first release and pulls ``engine``
in ahead of it, delivering ``engine`` early. With ``later`` True the
result keeps ``engine`` in the second release and pushes ``builder``
out to be delivered after it. Either way ``engine`` ends up before
``builder`` and the order stays a valid delivery order.

The ``later`` argument has the same meaning here as in
:func:`backlogops.order_by_dependencies`.

Calling :func:`check_backlog_consistency` before calling this function
is recommended.

**Arguments**:

- `backlog` - The backlog to order. This argument is not modified.
- `releases` - The releases to use for ordering. Their order in this
  list defines the release order; the list is not modified.
- `honor_dependencies` - If True, never place an item before an item
  that must be delivered before it, as described above. Default
  is False.
- `later` - Chooses how a dependency that disagrees with the release
  order is resolved when ``honor_dependencies`` is True. If
  False (the default) the prerequisite is pulled to an earlier
  release and the dependent keeps its release. If True the
  dependent is pushed to a later release and the prerequisite
  keeps its release. Has no effect when ``honor_dependencies``
  is False. Default is False.
- `stderr_file` - The file to report a missing release reference to.
  

**Returns**:

  A new backlog with the items ordered as described above.

<a id="backlogops.move_keys_first"></a>

# backlogops.move\_keys\_first

Reorder a backlog from a key list and extract keys by level.

<a id="backlogops.move_keys_first.move_keys_first"></a>

#### move\_keys\_first

```python
def move_keys_first(backlog: Backlog,
                    keys: Sequence[str],
                    stderr_file: TextIO = sys.stderr) -> Backlog
```

Move the items named by ``keys`` to the front of the backlog.

A new backlog is returned; the argument is not modified. The named
items lead the backlog in the order of ``keys``. Each named item is
preceded by its descendants in post order: a child comes right before
its own parent, and that parent right before the grandparent, all the
way up to the named item. For example, if ``E`` is a parent of ``S1``
and ``S2`` and ``S2`` is a parent of ``T``, moving ``E`` first yields
``S1, T, S2, E``. Siblings keep their original backlog order. A named
descendant is not pulled in this way; it is placed by its own key, so
it may end up after its named parent. A descendant is pulled to the
front only when it appears after its named ancestor in the backlog, so
that no item is moved to a later position because of an ancestor's
key. All items that are neither named nor pulled to the front keep
their original order after the front block.

**Arguments**:

- `backlog` - The backlog to reorder. The argument is not modified.
- `keys` - The keys to move to the front, in the wanted order. The keys
  must be unique and must exist in the backlog.
- `stderr_file` - The stream to report errors to.
  

**Returns**:

  A new backlog with the named items moved to the front.
  

**Raises**:

- `KeyError` - If a key is not found in the backlog.
- `ValueError` - If a key is not unique.

<a id="backlogops.move_keys_first.get_keys_in_order"></a>

#### get\_keys\_in\_order

```python
def get_keys_in_order(backlog: Backlog,
                      only_levels: int | str | Sequence[int | str],
                      levels: Optional[Levels] = None) -> list[str]
```

Return the keys of the backlog items at the given levels, in order.

The keys are returned in the order they appear in the backlog, keeping
only the items whose level is among ``only_levels``. A level may be
given as a level number or as a level name or alias. A name or alias
is resolved through ``levels`` (the default levels when ``levels`` is
None). A level number is used as is and need not be one of ``levels``.

**Arguments**:

- `backlog` - The backlog to take the keys from.
- `only_levels` - The levels to keep, as a single int or str or as a
  sequence of ints and strs.
- `levels` - The levels used to resolve a level name or alias, or None
  to use :data:`DEFAULT_LEVELS`.
  

**Returns**:

  The keys of the matching items, in backlog order.
  

**Raises**:

- `TypeError` - If ``only_levels`` is not an int, a str, or a sequence
  of ints and strs.
- `ValueError` - If a level name or alias matches no level.

<a id="backlogops.estimate_ready_date"></a>

# backlogops.estimate\_ready\_date

Estimate the ready date of backlog items.

<a id="backlogops.estimate_ready_date.estimate_ready_date"></a>

#### estimate\_ready\_date

```python
def estimate_ready_date(backlog: Backlog,
                        available_teams: AvailableTeams,
                        start_date: Optional[date] = None,
                        stderr_file: TextIO = sys.stderr) -> Backlog
```

Estimate the ready date of backlog items.

The teams start working on the start date, which defaults to today
when None is given. The backlog items are worked in their given
order. Each item is worked by its assigned team, or, when it names
no team, by the team that becomes free earliest. Only one team works
an item, and a team works one item at a time, in backlog order. When
a team's daily capacity covers more than one item, several items
finish on the same day, and the next item carries on from the
leftover capacity of the day the current one finished.

The story points an item still needs are turned into calendar time
from the team's velocity, rescaled by the team's effective capacity
on each day. That capacity follows every member's full-time
equivalent and actual work hours, so weekends, company holidays,
personal vacation, learning periods and ordered over-time all change
the pace. A standard work day is the longest day in the company
weekly schedule. The story points of TODO and IN_PROGRESS items are
all treated as still left to do; DONE and REJECTED items need no work
and get no estimated date. See also the Status enum.

A parent's estimated date is lifted to be no earlier than its latest
child's, applied through the whole hierarchy, because a parent cannot
be ready before its children even though work on the parent itself
may be scheduled earlier. A finished child does not delay its parent.

Dependencies between items are not considered; the backlog is assumed
to be ordered so that the teams can work the items in order. When an
item names a team that is not in the workforce, when no team is
available, or when the chosen team has no capacity for the item, the
item gets no estimated date and a warning is reported.

**Arguments**:

- `backlog` - The backlog to estimate the ready date of. The argument
  is not modified. The backlog must be ordered so that the
  teams can work the items in order.
- `available_teams` - The available teams used to estimate the ready
  date, including absence, velocity and work hours.
- `start_date` - The day the teams start working, or None for today.
- `stderr_file` - The file to report warnings to.
  

**Returns**:

  A new backlog whose items carry the estimated ready date. The
  other fields are copied unchanged from the given items.

<a id="backlogops.estimate_ready_date.set_plan_from_estimate"></a>

#### set\_plan\_from\_estimate

```python
def set_plan_from_estimate(backlog: Backlog,
                           stderr_file: TextIO = sys.stderr) -> Backlog
```

Set the planned ready dates from the estimated ready dates.

For each backlog item the planned ready date is set to the estimated
ready date, copying None when the estimated ready date is None.

**Arguments**:

- `backlog` - The backlog to set the planned ready dates of. The
  argument is not modified.
- `stderr_file` - The file to report errors to.
  

**Returns**:

  A new backlog whose items carry the planned ready date taken from
  the estimated ready date. The other fields are copied unchanged.

<a id="backlogops.work_hours"></a>

# backlogops.work\_hours

Work hours schedule and exceptions.

<a id="backlogops.work_hours.WeekDay"></a>

## WeekDay Objects

```python
class WeekDay(IntEnum)
```

Week day.

<a id="backlogops.work_hours.DEFAULT_WORK_WEEK"></a>

#### DEFAULT\_WORK\_WEEK

The default work week.

<a id="backlogops.work_hours.ExceptionWorkHours"></a>

## ExceptionWorkHours Objects

```python
@dataclass
class ExceptionWorkHours()
```

Exception work hours for a specific period.

The exception work hours are used to override the default work hours
for a specific period. This can be used to mark holidays or other days
with different work hours. It can also be used to mark a period with
ordered over-time work.
When used for an individual employee, the company exceptions are seen
as part of the schedule.

Fields:
    start_date: The first day of the exception (inclusive).
    end_date: The last day of the exception (inclusive). Must not be
              before start_date.
    hours_per_day: The work hours per day during the exception. Must
                   not be negative.
    new_work_days: If True, the exception adds new work days compared
                   to the schedule. That is the hours per day also
                   applies to days with no work hours in the schedule.
                   If False, the exception does not add new work days.
                   That is the hours per day only applies to days with
                   work hours in the schedule.
                   If an individual employee has an exception to work
                   during days the company is closed, the new_work_days
                   flag must be True.

Exceptions in one list (a company or a person) must not overlap, so
that the work hours of any day are defined by at most one exception.

<a id="backlogops.work_hours.ExceptionWorkHours.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of the exception work hours.

Field types are verified, the date range must be non-empty, and
the work hours per day must not be negative.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If the range is empty or the hours are negative.

<a id="backlogops.work_hours.CompanyWorkHours"></a>

## CompanyWorkHours Objects

```python
@dataclass
class CompanyWorkHours()
```

Company work hours.

The company work hours are used to define the work hours for a company.

Fields:
    work_hours: The work hours schedule for the company. Every week
                day must have non-negative work hours.
    exceptions: The list of exception work hours for the company.
                This should list national holidays and other days with
                different work hours. This should also include any days
                the company is closed for any reason (such as company
                wide vacations). The exceptions must not overlap.

<a id="backlogops.work_hours.CompanyWorkHours.check_consistency"></a>

#### check\_consistency

```python
def check_consistency(stderr_file: TextIO = sys.stderr) -> None
```

Check the consistency of the company work hours.

Field types are verified, the schedule must define non-negative
work hours for every week day, every exception must be consistent,
and the exceptions must not overlap.

**Arguments**:

- `stderr_file` - The file to report errors to.
  

**Raises**:

- `TypeError` - If a field has the wrong type.
- `ValueError` - If the schedule or an exception is invalid, or if
  two exceptions overlap.

<a id="backlogops.format_rules"></a>

# backlogops.format\_rules

Rules for formatting table data.

<a id="backlogops.format_rules.default_status_format"></a>

#### default\_status\_format

```python
def default_status_format() -> dict[Status, Fmt]
```

Return the default format specification for the status column.

<a id="backlogops.format_rules.FormatRules"></a>

## FormatRules Objects

```python
@dataclass
class FormatRules()
```

Rules for formatting table data.

<a id="backlogops.format_rules.FormatRules.backlog_first"></a>

#### backlog\_first

Whether to write the backlog before the releases.

<a id="backlogops.format_rules.FormatRules.border_style"></a>

#### border\_style

The border style to apply to the written table.

<a id="backlogops.format_rules.FormatRules.filtered_data_range"></a>

#### filtered\_data\_range

Whether to mark the written data as a filtered data range.

<a id="backlogops.format_rules.FormatRules.first_row_format"></a>

#### first\_row\_format

The format specification for the column names row.

<a id="backlogops.format_rules.FormatRules.status_format"></a>

#### status\_format

The format specification for the status column.

<a id="backlogops.format_rules.FormatRules.estimate_late"></a>

#### estimate\_late

The format for estimate values if later than planned.

<a id="backlogops.format_rules.FormatRules.estimate_early"></a>

#### estimate\_early

The format for estimate values if earlier than planned.

<a id="backlogops.format_rules.FormatRules.estimate_eq_planned"></a>

#### estimate\_eq\_planned

The format for estimate values if equal to planned.

<a id="backlogops.format_rules.FormatRules.get_status_format"></a>

#### get\_status\_format

```python
def get_status_format(status: Status) -> Fmt
```

Return the format for a status.

<a id="backlogops.format_rules.FormatRules.turn_off_cell_format"></a>

#### turn\_off\_cell\_format

```python
def turn_off_cell_format() -> None
```

Turn off all cell formatting.

Make all cells plain, without any formatting.
This does not affect the border style or the filtered data range.

<a id="backlogops.format_rules.FormatRules.cell_format_used"></a>

#### cell\_format\_used

```python
def cell_format_used() -> bool
```

Return True if any cell formatting is used.

<a id="backlogops.io_preset_wizard"></a>

# backlogops.io\_preset\_wizard

Interactively create a stand-alone TableIO input or output preset.

The public :func:`preset_wizard` asks whether to build an input or an
output preset and then the same questions the full configuration wizard
asks for one preset of that direction: the TableIO endpoint format and
options, how the backlog and releases file columns relate to the internal
fields, and, for an output preset, how levels are written. A stand-alone
preset has no name of its own; the file it is written to is the preset.

The ``_build_input_presets`` and ``_build_output_presets`` collectors ask a
counted list of *named* presets and are reused by the full configuration
wizard, where each preset additionally has a name.

<a id="backlogops.io_preset_wizard.preset_wizard"></a>

#### preset\_wizard

```python
def preset_wizard(
        ui_bridge: WizardUiBridge) -> InputFormatConfig | OutputFormatConfig
```

Interactively create a stand-alone input or output TableIO preset.

The wizard first asks whether to build an input or an output preset,
then asks exactly the questions the full configuration wizard asks for
one preset of that direction: the TableIO endpoint format and options,
how the backlog and releases file columns relate to the internal
fields, and, for an output preset, how levels are written. A
stand-alone preset has no name of its own; the file it is written to is
the preset, referred to by its file name where an input or output
configuration is taken.

**Arguments**:

- `ui_bridge` - Bridge between the wizard and the user interface.
  

**Returns**:

  The input or output format configuration, ready to be written to a
  stand-alone configuration file.
  

**Raises**:

- `EOFError` - The input ended, or the user abandoned the wizard.

