# Table of Contents

* [backlogops\_gui.jira\_update](#backlogops_gui.jira_update)
  * [JiraUpdater](#backlogops_gui.jira_update.JiraUpdater)
    * [releases\_action](#backlogops_gui.jira_update.JiraUpdater.releases_action)
    * [backlog\_action](#backlogops_gui.jira_update.JiraUpdater.backlog_action)
    * [\_update\_releases](#backlogops_gui.jira_update.JiraUpdater._update_releases)
    * [\_releases\_worker](#backlogops_gui.jira_update.JiraUpdater._releases_worker)
    * [\_preset\_fields](#backlogops_gui.jira_update.JiraUpdater._preset_fields)
    * [\_update\_backlog](#backlogops_gui.jira_update.JiraUpdater._update_backlog)
    * [\_backlog\_worker](#backlogops_gui.jira_update.JiraUpdater._backlog_worker)
* [backlogops\_gui.backlog\_dialogs](#backlogops_gui.backlog_dialogs)
  * [DepOptions](#backlogops_gui.backlog_dialogs.DepOptions)
  * [ReleaseOrderOptions](#backlogops_gui.backlog_dialogs.ReleaseOrderOptions)
  * [StartChoice](#backlogops_gui.backlog_dialogs.StartChoice)
  * [KeysDialog](#backlogops_gui.backlog_dialogs.KeysDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.KeysDialog.__init__)
    * [\_build\_text](#backlogops_gui.backlog_dialogs.KeysDialog._build_text)
    * [\_load](#backlogops_gui.backlog_dialogs.KeysDialog._load)
    * [\_confirm](#backlogops_gui.backlog_dialogs.KeysDialog._confirm)
  * [DepOptionsDialog](#backlogops_gui.backlog_dialogs.DepOptionsDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.DepOptionsDialog.__init__)
    * [\_build](#backlogops_gui.backlog_dialogs.DepOptionsDialog._build)
    * [\_build\_mode](#backlogops_gui.backlog_dialogs.DepOptionsDialog._build_mode)
    * [\_build\_space](#backlogops_gui.backlog_dialogs.DepOptionsDialog._build_space)
    * [\_confirm](#backlogops_gui.backlog_dialogs.DepOptionsDialog._confirm)
  * [StartDateDialog](#backlogops_gui.backlog_dialogs.StartDateDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.StartDateDialog.__init__)
    * [\_build](#backlogops_gui.backlog_dialogs.StartDateDialog._build)
    * [\_confirm](#backlogops_gui.backlog_dialogs.StartDateDialog._confirm)
  * [LevelsDialog](#backlogops_gui.backlog_dialogs.LevelsDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.LevelsDialog.__init__)
    * [\_build](#backlogops_gui.backlog_dialogs.LevelsDialog._build)
    * [\_confirm](#backlogops_gui.backlog_dialogs.LevelsDialog._confirm)
  * [DateOrderDialog](#backlogops_gui.backlog_dialogs.DateOrderDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.DateOrderDialog.__init__)
    * [\_build](#backlogops_gui.backlog_dialogs.DateOrderDialog._build)
    * [\_confirm](#backlogops_gui.backlog_dialogs.DateOrderDialog._confirm)
  * [ReleaseOrderDialog](#backlogops_gui.backlog_dialogs.ReleaseOrderDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.ReleaseOrderDialog.__init__)
    * [\_build](#backlogops_gui.backlog_dialogs.ReleaseOrderDialog._build)
    * [\_confirm](#backlogops_gui.backlog_dialogs.ReleaseOrderDialog._confirm)
  * [BufferDialog](#backlogops_gui.backlog_dialogs.BufferDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.BufferDialog.__init__)
    * [\_build](#backlogops_gui.backlog_dialogs.BufferDialog._build)
    * [\_confirm](#backlogops_gui.backlog_dialogs.BufferDialog._confirm)
  * [ask\_keys](#backlogops_gui.backlog_dialogs.ask_keys)
  * [ask\_dep\_options](#backlogops_gui.backlog_dialogs.ask_dep_options)
  * [ask\_start\_date](#backlogops_gui.backlog_dialogs.ask_start_date)
  * [ask\_levels](#backlogops_gui.backlog_dialogs.ask_levels)
  * [ask\_date\_order](#backlogops_gui.backlog_dialogs.ask_date_order)
  * [ask\_release\_order](#backlogops_gui.backlog_dialogs.ask_release_order)
  * [ask\_buffer\_days](#backlogops_gui.backlog_dialogs.ask_buffer_days)
* [backlogops\_gui.report\_windows](#backlogops_gui.report_windows)
  * [show\_change\_list](#backlogops_gui.report_windows.show_change_list)
  * [show\_text\_report](#backlogops_gui.report_windows.show_text_report)
* [backlogops\_gui.choice\_dialogs](#backlogops_gui.choice_dialogs)
  * [ConfigChoice](#backlogops_gui.choice_dialogs.ConfigChoice)
  * [PresetKind](#backlogops_gui.choice_dialogs.PresetKind)
  * [NoConfigDialog](#backlogops_gui.choice_dialogs.NoConfigDialog)
    * [\_\_init\_\_](#backlogops_gui.choice_dialogs.NoConfigDialog.__init__)
    * [\_build](#backlogops_gui.choice_dialogs.NoConfigDialog._build)
    * [\_add\_button](#backlogops_gui.choice_dialogs.NoConfigDialog._add_button)
    * [\_show](#backlogops_gui.choice_dialogs.NoConfigDialog._show)
    * [\_choose](#backlogops_gui.choice_dialogs.NoConfigDialog._choose)
  * [ask\_no\_config\_choice](#backlogops_gui.choice_dialogs.ask_no_config_choice)
  * [PresetKindDialog](#backlogops_gui.choice_dialogs.PresetKindDialog)
    * [\_\_init\_\_](#backlogops_gui.choice_dialogs.PresetKindDialog.__init__)
    * [\_build](#backlogops_gui.choice_dialogs.PresetKindDialog._build)
    * [\_add\_button](#backlogops_gui.choice_dialogs.PresetKindDialog._add_button)
    * [\_show](#backlogops_gui.choice_dialogs.PresetKindDialog._show)
    * [\_choose](#backlogops_gui.choice_dialogs.PresetKindDialog._choose)
  * [ask\_preset\_kind](#backlogops_gui.choice_dialogs.ask_preset_kind)
* [backlogops\_gui.format\_dialogs](#backlogops_gui.format_dialogs)
  * [format\_value](#backlogops_gui.format_dialogs.format_value)
  * [ReadOptions](#backlogops_gui.format_dialogs.ReadOptions)
  * [WriteOptions](#backlogops_gui.format_dialogs.WriteOptions)
  * [FormatDialog](#backlogops_gui.format_dialogs.FormatDialog)
    * [\_\_init\_\_](#backlogops_gui.format_dialogs.FormatDialog.__init__)
    * [\_build](#backlogops_gui.format_dialogs.FormatDialog._build)
    * [\_add\_radio](#backlogops_gui.format_dialogs.FormatDialog._add_radio)
    * [\_add\_preset\_row](#backlogops_gui.format_dialogs.FormatDialog._add_preset_row)
    * [\_add\_file\_row](#backlogops_gui.format_dialogs.FormatDialog._add_file_row)
    * [\_browse](#backlogops_gui.format_dialogs.FormatDialog._browse)
    * [\_confirm](#backlogops_gui.format_dialogs.FormatDialog._confirm)
    * [\_selected\_value](#backlogops_gui.format_dialogs.FormatDialog._selected_value)
  * [ask\_read\_options](#backlogops_gui.format_dialogs.ask_read_options)
  * [ask\_write\_options](#backlogops_gui.format_dialogs.ask_write_options)
* [backlogops\_gui.jira\_dialogs](#backlogops_gui.jira_dialogs)
  * [MISSING\_MODE\_TEXT](#backlogops_gui.jira_dialogs.MISSING_MODE_TEXT)
  * [LINK\_MODE\_TEXT](#backlogops_gui.jira_dialogs.LINK_MODE_TEXT)
  * [JiraPresetOptions](#backlogops_gui.jira_dialogs.JiraPresetOptions)
  * [JiraReadOptions](#backlogops_gui.jira_dialogs.JiraReadOptions)
  * [JiraWriteOptions](#backlogops_gui.jira_dialogs.JiraWriteOptions)
  * [JiraReleaseUpdateOptions](#backlogops_gui.jira_dialogs.JiraReleaseUpdateOptions)
  * [JiraBacklogUpdateOptions](#backlogops_gui.jira_dialogs.JiraBacklogUpdateOptions)
  * [JiraReadDialog](#backlogops_gui.jira_dialogs.JiraReadDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraReadDialog.__init__)
    * [\_build](#backlogops_gui.jira_dialogs.JiraReadDialog._build)
    * [\_preset\_changed](#backlogops_gui.jira_dialogs.JiraReadDialog._preset_changed)
    * [\_confirm](#backlogops_gui.jira_dialogs.JiraReadDialog._confirm)
  * [ask\_jira\_read\_options](#backlogops_gui.jira_dialogs.ask_jira_read_options)
  * [JiraWriteDialog](#backlogops_gui.jira_dialogs.JiraWriteDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraWriteDialog.__init__)
    * [\_build](#backlogops_gui.jira_dialogs.JiraWriteDialog._build)
    * [\_confirm](#backlogops_gui.jira_dialogs.JiraWriteDialog._confirm)
  * [ask\_jira\_write\_options](#backlogops_gui.jira_dialogs.ask_jira_write_options)
  * [JiraReleaseUpdateDialog](#backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog.__init__)
    * [\_build](#backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog._build)
    * [\_build\_preset](#backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog._build_preset)
    * [\_build\_mode](#backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog._build_mode)
    * [\_build\_releases](#backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog._build_releases)
    * [\_confirm](#backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog._confirm)
  * [ask\_release\_update](#backlogops_gui.jira_dialogs.ask_release_update)
  * [JiraBacklogUpdateDialog](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog.__init__)
    * [\_build](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._build)
    * [\_build\_preset](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._build_preset)
    * [\_build\_mode](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._build_mode)
    * [\_build\_links](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._build_links)
    * [\_build\_fields](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._build_fields)
    * [\_preset\_changed](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._preset_changed)
    * [\_confirm](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._confirm)
  * [ask\_backlog\_update](#backlogops_gui.jira_dialogs.ask_backlog_update)
  * [PassphraseDialog](#backlogops_gui.jira_dialogs.PassphraseDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.PassphraseDialog.__init__)
    * [\_build](#backlogops_gui.jira_dialogs.PassphraseDialog._build)
    * [\_confirm](#backlogops_gui.jira_dialogs.PassphraseDialog._confirm)
  * [ask\_jira\_passphrase](#backlogops_gui.jira_dialogs.ask_jira_passphrase)
* [backlogops\_gui.gui\_style](#backlogops_gui.gui_style)
  * [style\_input](#backlogops_gui.gui_style.style_input)
  * [\_style\_combobox](#backlogops_gui.gui_style._style_combobox)
  * [focus\_first\_input](#backlogops_gui.gui_style.focus_first_input)
  * [\_first\_input](#backlogops_gui.gui_style._first_input)
  * [\_is\_input](#backlogops_gui.gui_style._is_input)
* [backlogops\_gui.gui\_wizard](#backlogops_gui.gui_wizard)
  * [TkWizardBridge](#backlogops_gui.gui_wizard.TkWizardBridge)
    * [\_\_init\_\_](#backlogops_gui.gui_wizard.TkWizardBridge.__init__)
    * [ask\_text](#backlogops_gui.gui_wizard.TkWizardBridge.ask_text)
    * [ask\_yes\_no](#backlogops_gui.gui_wizard.TkWizardBridge.ask_yes_no)
    * [ask\_choice](#backlogops_gui.gui_wizard.TkWizardBridge.ask_choice)
    * [ask\_multi](#backlogops_gui.gui_wizard.TkWizardBridge.ask_multi)
    * [ask\_table](#backlogops_gui.gui_wizard.TkWizardBridge.ask_table)
    * [show](#backlogops_gui.gui_wizard.TkWizardBridge.show)
    * [error\_file](#backlogops_gui.gui_wizard.TkWizardBridge.error_file)
    * [close](#backlogops_gui.gui_wizard.TkWizardBridge.close)
    * [\_window\_obj](#backlogops_gui.gui_wizard.TkWizardBridge._window_obj)
* [backlogops\_gui.jira\_base](#backlogops_gui.jira_base)
  * [JiraAction](#backlogops_gui.jira_base.JiraAction)
    * [\_\_init\_\_](#backlogops_gui.jira_base.JiraAction.__init__)
    * [\_config](#backlogops_gui.jira_base.JiraAction._config)
    * [\_available](#backlogops_gui.jira_base.JiraAction._available)
    * [\_presets](#backlogops_gui.jira_base.JiraAction._presets)
    * [\_connections](#backlogops_gui.jira_base.JiraAction._connections)
    * [\_jira\_connection](#backlogops_gui.jira_base.JiraAction._jira_connection)
    * [\_prepare\_jira\_token](#backlogops_gui.jira_base.JiraAction._prepare_jira_token)
    * [\_start](#backlogops_gui.jira_base.JiraAction._start)
    * [\_dispatch](#backlogops_gui.jira_base.JiraAction._dispatch)
    * [\_after](#backlogops_gui.jira_base.JiraAction._after)
    * [\_fail](#backlogops_gui.jira_base.JiraAction._fail)
    * [\_finish](#backlogops_gui.jira_base.JiraAction._finish)
* [backlogops\_gui.\_migrate\_warn](#backlogops_gui._migrate_warn)
  * [GuiMigrateWarnHook](#backlogops_gui._migrate_warn.GuiMigrateWarnHook)
    * [migrate\_instructions](#backlogops_gui._migrate_warn.GuiMigrateWarnHook.migrate_instructions)
  * [GuiPresetMigrateWarnHook](#backlogops_gui._migrate_warn.GuiPresetMigrateWarnHook)
    * [migrate\_instructions](#backlogops_gui._migrate_warn.GuiPresetMigrateWarnHook.migrate_instructions)
* [backlogops\_gui.application](#backlogops_gui.application)
  * [initial\_config](#backlogops_gui.application.initial_config)
  * [\_config\_failure](#backlogops_gui.application._config_failure)
  * [BacklogApp](#backlogops_gui.application.BacklogApp)
    * [\_\_init\_\_](#backlogops_gui.application.BacklogApp.__init__)
    * [in\_presets](#backlogops_gui.application.BacklogApp.in_presets)
    * [out\_presets](#backlogops_gui.application.BacklogApp.out_presets)
    * [available\_teams](#backlogops_gui.application.BacklogApp.available_teams)
    * [levels](#backlogops_gui.application.BacklogApp.levels)
    * [status\_map](#backlogops_gui.application.BacklogApp.status_map)
    * [gui\_display](#backlogops_gui.application.BacklogApp.gui_display)
    * [show\_error](#backlogops_gui.application.BacklogApp.show_error)
    * [show\_info](#backlogops_gui.application.BacklogApp.show_info)
    * [start](#backlogops_gui.application.BacklogApp.start)
    * [\_resolve\_missing\_config](#backlogops_gui.application.BacklogApp._resolve_missing_config)
    * [\_adopt\_startup\_wizard](#backlogops_gui.application.BacklogApp._adopt_startup_wizard)
    * [\_adopt\_loaded\_config](#backlogops_gui.application.BacklogApp._adopt_loaded_config)
    * [\_run\_bridge\_wizard](#backlogops_gui.application.BacklogApp._run_bridge_wizard)
    * [run\_wizard](#backlogops_gui.application.BacklogApp.run_wizard)
    * [\_load\_config\_file](#backlogops_gui.application.BacklogApp._load_config_file)
    * [run\_config\_wizard](#backlogops_gui.application.BacklogApp.run_config_wizard)
    * [create\_preset\_file](#backlogops_gui.application.BacklogApp.create_preset_file)
    * [migrate\_preset\_file](#backlogops_gui.application.BacklogApp.migrate_preset_file)
    * [\_migrate\_preset](#backlogops_gui.application.BacklogApp._migrate_preset)
    * [\_migrate\_failed](#backlogops_gui.application.BacklogApp._migrate_failed)
    * [write\_config](#backlogops_gui.application.BacklogApp.write_config)
    * [\_write\_to\_chosen](#backlogops_gui.application.BacklogApp._write_to_chosen)
    * [read\_backlog\_file](#backlogops_gui.application.BacklogApp.read_backlog_file)
    * [new\_demo\_backlog](#backlogops_gui.application.BacklogApp.new_demo_backlog)
    * [open\_backlog](#backlogops_gui.application.BacklogApp.open_backlog)
    * [report\_versions](#backlogops_gui.application.BacklogApp.report_versions)
    * [\_write\_version\_report](#backlogops_gui.application.BacklogApp._write_version_report)
    * [build\_menu](#backlogops_gui.application.BacklogApp.build_menu)
    * [\_add\_file\_menu](#backlogops_gui.application.BacklogApp._add_file_menu)
    * [\_add\_config\_menu](#backlogops_gui.application.BacklogApp._add_config_menu)
    * [\_add\_help\_menu](#backlogops_gui.application.BacklogApp._add_help_menu)
    * [build\_body](#backlogops_gui.application.BacklogApp.build_body)
    * [\_add\_warning](#backlogops_gui.application.BacklogApp._add_warning)
    * [\_build\_log\_view](#backlogops_gui.application.BacklogApp._build_log_view)
    * [\_status\_text](#backlogops_gui.application.BacklogApp._status_text)
    * [\_update\_status](#backlogops_gui.application.BacklogApp._update_status)
    * [refresh\_log](#backlogops_gui.application.BacklogApp.refresh_log)
    * [\_log\_selection](#backlogops_gui.application.BacklogApp._log_selection)
    * [\_copy\_log](#backlogops_gui.application.BacklogApp._copy_log)
    * [\_schedule\_refresh](#backlogops_gui.application.BacklogApp._schedule_refresh)
  * [\_build\_parser](#backlogops_gui.application._build_parser)
  * [main](#backlogops_gui.application.main)
* [backlogops\_gui.tcltk\_version](#backlogops_gui.tcltk_version)
  * [\_parse\_tcltk\_version](#backlogops_gui.tcltk_version._parse_tcltk_version)
  * [\_old\_version\_warning](#backlogops_gui.tcltk_version._old_version_warning)
  * [\_bad\_version\_warning](#backlogops_gui.tcltk_version._bad_version_warning)
  * [warning\_for\_version](#backlogops_gui.tcltk_version.warning_for_version)
  * [check\_tcltk\_version](#backlogops_gui.tcltk_version.check_tcltk_version)
* [backlogops\_gui.jira\_read](#backlogops_gui.jira_read)
  * [JiraReader](#backlogops_gui.jira_read.JiraReader)
    * [read\_backlog](#backlogops_gui.jira_read.JiraReader.read_backlog)
    * [\_preset\_filters](#backlogops_gui.jira_read.JiraReader._preset_filters)
    * [\_read\_worker](#backlogops_gui.jira_read.JiraReader._read_worker)
    * [\_consistency\_warning](#backlogops_gui.jira_read.JiraReader._consistency_warning)
* [backlogops\_gui.backlog\_actions](#backlogops_gui.backlog_actions)
  * [save\_backlog](#backlogops_gui.backlog_actions.save_backlog)
  * [\_apply\_change](#backlogops_gui.backlog_actions._apply_change)
  * [order\_by\_keys](#backlogops_gui.backlog_actions.order_by_keys)
  * [order\_by\_deps](#backlogops_gui.backlog_actions.order_by_deps)
  * [\_release\_order\_message](#backlogops_gui.backlog_actions._release_order_message)
  * [order\_by\_release](#backlogops_gui.backlog_actions.order_by_release)
  * [save\_changes](#backlogops_gui.backlog_actions.save_changes)
  * [show\_changes](#backlogops_gui.backlog_actions.show_changes)
  * [\_date\_report](#backlogops_gui.backlog_actions._date_report)
  * [\_content\_report](#backlogops_gui.backlog_actions._content_report)
  * [\_run\_change](#backlogops_gui.backlog_actions._run_change)
  * [estimate\_date](#backlogops_gui.backlog_actions.estimate_date)
  * [set\_plan](#backlogops_gui.backlog_actions.set_plan)
  * [adjust\_content](#backlogops_gui.backlog_actions.adjust_content)
  * [plan\_dates](#backlogops_gui.backlog_actions.plan_dates)
  * [order\_dates](#backlogops_gui.backlog_actions.order_dates)
  * [extract\_keys](#backlogops_gui.backlog_actions.extract_keys)
  * [apply\_add\_result](#backlogops_gui.backlog_actions.apply_add_result)
  * [apply\_update\_result](#backlogops_gui.backlog_actions.apply_update_result)
* [backlogops\_gui.close\_binding](#backlogops_gui.close_binding)
  * [\_close\_events](#backlogops_gui.close_binding._close_events)
  * [bind\_close](#backlogops_gui.close_binding.bind_close)
* [backlogops\_gui.backlog\_window](#backlogops_gui.backlog_window)
  * [BacklogWindow](#backlogops_gui.backlog_window.BacklogWindow)
    * [\_\_init\_\_](#backlogops_gui.backlog_window.BacklogWindow.__init__)
    * [\_report\_error](#backlogops_gui.backlog_window.BacklogWindow._report_error)
    * [\_report\_info](#backlogops_gui.backlog_window.BacklogWindow._report_info)
    * [\_build\_tables](#backlogops_gui.backlog_window.BacklogWindow._build_tables)
    * [\_refresh\_tables](#backlogops_gui.backlog_window.BacklogWindow._refresh_tables)
    * [\_add\_warning](#backlogops_gui.backlog_window.BacklogWindow._add_warning)
    * [\_add\_menu](#backlogops_gui.backlog_window.BacklogWindow._add_menu)
    * [\_add\_actions](#backlogops_gui.backlog_window.BacklogWindow._add_actions)
    * [\_add\_jira\_actions](#backlogops_gui.backlog_window.BacklogWindow._add_jira_actions)
    * [\_add\_table](#backlogops_gui.backlog_window.BacklogWindow._add_table)
    * [\_make\_tree](#backlogops_gui.backlog_window.BacklogWindow._make_tree)
    * [\_save](#backlogops_gui.backlog_window.BacklogWindow._save)
    * [\_order\_by\_keys](#backlogops_gui.backlog_window.BacklogWindow._order_by_keys)
    * [\_order\_by\_deps](#backlogops_gui.backlog_window.BacklogWindow._order_by_deps)
    * [\_order\_by\_release](#backlogops_gui.backlog_window.BacklogWindow._order_by_release)
    * [\_estimate\_date](#backlogops_gui.backlog_window.BacklogWindow._estimate_date)
    * [\_set\_plan](#backlogops_gui.backlog_window.BacklogWindow._set_plan)
    * [\_adjust\_content](#backlogops_gui.backlog_window.BacklogWindow._adjust_content)
    * [\_plan\_dates](#backlogops_gui.backlog_window.BacklogWindow._plan_dates)
    * [\_order\_dates](#backlogops_gui.backlog_window.BacklogWindow._order_dates)
    * [\_extract\_keys](#backlogops_gui.backlog_window.BacklogWindow._extract_keys)
    * [\_jira\_add](#backlogops_gui.backlog_window.BacklogWindow._jira_add)
    * [\_on\_jira\_added](#backlogops_gui.backlog_window.BacklogWindow._on_jira_added)
    * [\_show\_add\_report](#backlogops_gui.backlog_window.BacklogWindow._show_add_report)
    * [\_releases\_add](#backlogops_gui.backlog_window.BacklogWindow._releases_add)
    * [\_on\_releases\_added](#backlogops_gui.backlog_window.BacklogWindow._on_releases_added)
    * [\_releases\_update](#backlogops_gui.backlog_window.BacklogWindow._releases_update)
    * [\_on\_releases\_updated](#backlogops_gui.backlog_window.BacklogWindow._on_releases_updated)
    * [\_backlog\_update](#backlogops_gui.backlog_window.BacklogWindow._backlog_update)
    * [\_on\_backlog\_updated](#backlogops_gui.backlog_window.BacklogWindow._on_backlog_updated)
    * [\_show\_update\_report](#backlogops_gui.backlog_window.BacklogWindow._show_update_report)
* [backlogops\_gui.blog\_version\_reporter](#backlogops_gui.blog_version_reporter)
  * [BloGuiVersionReporter](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter)
    * [package\_names](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter.package_names)
    * [get\_main\_package\_name](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter.get_main_package_name)
* [backlogops\_gui.wizard\_table](#backlogops_gui.wizard_table)
  * [\_uniform](#backlogops_gui.wizard_table._uniform)
  * [\_new\_row\_template](#backlogops_gui.wizard_table._new_row_template)
  * [Cell](#backlogops_gui.wizard_table.Cell)
  * [\_cell\_text](#backlogops_gui.wizard_table._cell_text)
  * [TableEditor](#backlogops_gui.wizard_table.TableEditor)
    * [\_\_init\_\_](#backlogops_gui.wizard_table.TableEditor.__init__)
    * [is\_variable](#backlogops_gui.wizard_table.TableEditor.is_variable)
    * [values](#backlogops_gui.wizard_table.TableEditor.values)
    * [add\_row](#backlogops_gui.wizard_table.TableEditor.add_row)
    * [remove\_row](#backlogops_gui.wizard_table.TableEditor.remove_row)
    * [\_build\_grid\_area](#backlogops_gui.wizard_table.TableEditor._build_grid_area)
    * [\_build\_scroll](#backlogops_gui.wizard_table.TableEditor._build_scroll)
    * [\_scroll\_to\_end](#backlogops_gui.wizard_table.TableEditor._scroll_to_end)
    * [\_build\_header](#backlogops_gui.wizard_table.TableEditor._build_header)
    * [\_append\_cells](#backlogops_gui.wizard_table.TableEditor._append_cells)
    * [\_build\_cell](#backlogops_gui.wizard_table.TableEditor._build_cell)
    * [\_editable\_widget](#backlogops_gui.wizard_table.TableEditor._editable_widget)
    * [\_bind\_change](#backlogops_gui.wizard_table.TableEditor._bind_change)
    * [\_feedback](#backlogops_gui.wizard_table.TableEditor._feedback)
    * [\_show](#backlogops_gui.wizard_table.TableEditor._show)
* [backlogops\_gui.modal\_dialog](#backlogops_gui.modal_dialog)
  * [ModalDialog](#backlogops_gui.modal_dialog.ModalDialog)
    * [\_\_init\_\_](#backlogops_gui.modal_dialog.ModalDialog.__init__)
    * [\_show](#backlogops_gui.modal_dialog.ModalDialog._show)
    * [\_add\_buttons](#backlogops_gui.modal_dialog.ModalDialog._add_buttons)
    * [\_confirm](#backlogops_gui.modal_dialog.ModalDialog._confirm)
    * [\_cancel](#backlogops_gui.modal_dialog.ModalDialog._cancel)
* [backlogops\_gui.python\_version](#backlogops_gui.python_version)
  * [check\_python\_version](#backlogops_gui.python_version.check_python_version)
* [backlogops\_gui.log\_buffer](#backlogops_gui.log_buffer)
  * [LogBuffer](#backlogops_gui.log_buffer.LogBuffer)
    * [\_\_init\_\_](#backlogops_gui.log_buffer.LogBuffer.__init__)
    * [write](#backlogops_gui.log_buffer.LogBuffer.write)
    * [text](#backlogops_gui.log_buffer.LogBuffer.text)
* [backlogops\_gui.jira\_write](#backlogops_gui.jira_write)
  * [JiraWriter](#backlogops_gui.jira_write.JiraWriter)
    * [backlog\_action](#backlogops_gui.jira_write.JiraWriter.backlog_action)
    * [releases\_action](#backlogops_gui.jira_write.JiraWriter.releases_action)
    * [\_ask](#backlogops_gui.jira_write.JiraWriter._ask)
    * [\_add\_backlog](#backlogops_gui.jira_write.JiraWriter._add_backlog)
    * [\_backlog\_worker](#backlogops_gui.jira_write.JiraWriter._backlog_worker)
    * [\_add\_releases](#backlogops_gui.jira_write.JiraWriter._add_releases)
    * [\_releases\_worker](#backlogops_gui.jira_write.JiraWriter._releases_worker)
* [backlogops\_gui.backlog\_io](#backlogops_gui.backlog_io)
  * [\_sink](#backlogops_gui.backlog_io._sink)
  * [read\_backlog](#backlogops_gui.backlog_io.read_backlog)
  * [write\_backlog](#backlogops_gui.backlog_io.write_backlog)
* [backlogops\_gui.table\_view](#backlogops_gui.table_view)
  * [\_columns](#backlogops_gui.table_view._columns)
  * [\_cell\_text](#backlogops_gui.table_view._cell_text)
  * [\_table](#backlogops_gui.table_view._table)
  * [backlog\_table](#backlogops_gui.table_view.backlog_table)
  * [release\_table](#backlogops_gui.table_view.release_table)
  * [\_tag\_name](#backlogops_gui.table_view._tag_name)
  * [\_tag\_font](#backlogops_gui.table_view._tag_font)
  * [\_ensure\_tag](#backlogops_gui.table_view._ensure_tag)
  * [\_format\_cell](#backlogops_gui.table_view._format_cell)
  * [supports\_cell\_tags](#backlogops_gui.table_view.supports_cell_tags)
  * [\_row\_format](#backlogops_gui.table_view._row_format)
  * [\_color\_cells](#backlogops_gui.table_view._color_cells)
  * [\_insert\_row](#backlogops_gui.table_view._insert_row)
  * [make\_table](#backlogops_gui.table_view.make_table)
* [backlogops\_gui.wizard\_window](#backlogops_gui.wizard_window)
  * [WizardWindow](#backlogops_gui.wizard_window.WizardWindow)
    * [\_\_init\_\_](#backlogops_gui.wizard_window.WizardWindow.__init__)
    * [\_build\_messages](#backlogops_gui.wizard_window.WizardWindow._build_messages)
    * [show](#backlogops_gui.wizard_window.WizardWindow.show)
    * [close](#backlogops_gui.wizard_window.WizardWindow.close)
    * [ask\_text](#backlogops_gui.wizard_window.WizardWindow.ask_text)
    * [\_text\_result](#backlogops_gui.wizard_window.WizardWindow._text_result)
    * [ask\_yes\_no](#backlogops_gui.wizard_window.WizardWindow.ask_yes_no)
    * [ask\_choice](#backlogops_gui.wizard_window.WizardWindow.ask_choice)
    * [ask\_multi](#backlogops_gui.wizard_window.WizardWindow.ask_multi)
    * [ask\_table](#backlogops_gui.wizard_window.WizardWindow.ask_table)
    * [\_run\_multi](#backlogops_gui.wizard_window.WizardWindow._run_multi)
    * [\_choice\_list](#backlogops_gui.wizard_window.WizardWindow._choice_list)
    * [\_preset\_indexes](#backlogops_gui.wizard_window.WizardWindow._preset_indexes)
    * [\_pick\_one](#backlogops_gui.wizard_window.WizardWindow._pick_one)
    * [\_pick\_many](#backlogops_gui.wizard_window.WizardWindow._pick_many)
    * [\_begin](#backlogops_gui.wizard_window.WizardWindow._begin)
    * [\_add\_label](#backlogops_gui.wizard_window.WizardWindow._add_label)
    * [\_add\_buttons](#backlogops_gui.wizard_window.WizardWindow._add_buttons)
    * [\_add\_table\_buttons](#backlogops_gui.wizard_window.WizardWindow._add_table_buttons)
    * [\_add\_nav\_buttons](#backlogops_gui.wizard_window.WizardWindow._add_nav_buttons)
    * [\_wait](#backlogops_gui.wizard_window.WizardWindow._wait)
    * [\_finish](#backlogops_gui.wizard_window.WizardWindow._finish)
    * [\_back](#backlogops_gui.wizard_window.WizardWindow._back)
    * [\_cancel\_level](#backlogops_gui.wizard_window.WizardWindow._cancel_level)
    * [\_cancel](#backlogops_gui.wizard_window.WizardWindow._cancel)
    * [\_navigate](#backlogops_gui.wizard_window.WizardWindow._navigate)
* [backlogops\_gui.jira\_actions](#backlogops_gui.jira_actions)
  * [JiraActions](#backlogops_gui.jira_actions.JiraActions)
    * [\_\_init\_\_](#backlogops_gui.jira_actions.JiraActions.__init__)
* [backlogops\_gui.file\_choosers](#backlogops_gui.file_choosers)
  * [choose\_input\_file](#backlogops_gui.file_choosers.choose_input_file)
  * [choose\_output\_file](#backlogops_gui.file_choosers.choose_output_file)
  * [choose\_config\_file](#backlogops_gui.file_choosers.choose_config_file)
  * [choose\_existing\_config](#backlogops_gui.file_choosers.choose_existing_config)
  * [choose\_preset\_to\_migrate](#backlogops_gui.file_choosers.choose_preset_to_migrate)
  * [choose\_migrated\_preset](#backlogops_gui.file_choosers.choose_migrated_preset)
  * [choose\_key\_list\_output](#backlogops_gui.file_choosers.choose_key_list_output)
  * [choose\_changes\_output](#backlogops_gui.file_choosers.choose_changes_output)

<a id="backlogops_gui.jira_update"></a>

# backlogops\_gui.jira\_update

Update the shown releases and backlog in Jira.

The updater offers a handler for updating the shown releases and a handler
for updating the shown backlog, each available only when a configuration
with Jira presets is loaded. A handler asks for a preset and the update
options, then updates on a worker thread and hands the result back to the
GUI thread. The backlog-update dialog offers the columns each preset can
update, taken from the library.

<a id="backlogops_gui.jira_update.JiraUpdater"></a>

## JiraUpdater Objects

```python
class JiraUpdater(JiraAction)
```

Updates the shown releases and backlog in Jira.

<a id="backlogops_gui.jira_update.JiraUpdater.releases_action"></a>

#### releases\_action

```python
def releases_action() -> Optional[Callable[
    [BacklogReleases, Callable[[UpdatedReleasesInJira], None]], None]]
```

Return the update-releases handler, or None when unavailable.

<a id="backlogops_gui.jira_update.JiraUpdater.backlog_action"></a>

#### backlog\_action

```python
def backlog_action() -> Optional[Callable[
    [BacklogReleases, Callable[[UpdatedBacklogInJira], None]], None]]
```

Return the update-backlog handler, or None when unavailable.

<a id="backlogops_gui.jira_update.JiraUpdater._update_releases"></a>

#### \_update\_releases

```python
def _update_releases(data: BacklogReleases,
                     on_done: Callable[[UpdatedReleasesInJira], None]) -> None
```

Ask for a preset, mode and releases, then update them in Jira.

<a id="backlogops_gui.jira_update.JiraUpdater._releases_worker"></a>

#### \_releases\_worker

```python
def _releases_worker(options: JiraReleaseUpdateOptions, data: BacklogReleases,
                     on_done: Callable[[UpdatedReleasesInJira], None]) -> None
```

Update the releases on a worker and schedule the GUI update.

<a id="backlogops_gui.jira_update.JiraUpdater._preset_fields"></a>

#### \_preset\_fields

```python
def _preset_fields() -> dict[str, list[str]]
```

Return each preset name mapped to its updatable backlog fields.

<a id="backlogops_gui.jira_update.JiraUpdater._update_backlog"></a>

#### \_update\_backlog

```python
def _update_backlog(data: BacklogReleases,
                    on_done: Callable[[UpdatedBacklogInJira], None]) -> None
```

Ask for a preset, fields and mode, then update the backlog.

<a id="backlogops_gui.jira_update.JiraUpdater._backlog_worker"></a>

#### \_backlog\_worker

```python
def _backlog_worker(options: JiraBacklogUpdateOptions, data: BacklogReleases,
                    on_done: Callable[[UpdatedBacklogInJira], None]) -> None
```

Update the backlog on a worker and schedule the GUI update.

<a id="backlogops_gui.backlog_dialogs"></a>

# backlogops\_gui.backlog\_dialogs

Modal dialogs collecting options for the backlog operations.

These dialogs gather the options for the actions offered by a backlog
window: the leading keys for a reordering, the order-by-dependencies
options, the start date for a ready-date estimate, the levels to extract
keys at, the buffer in calendar days, and the two release-ordering
choices. Each dialog stores its result and the matching ``ask_`` wrapper
returns it, or None when the dialog is cancelled.

<a id="backlogops_gui.backlog_dialogs.DepOptions"></a>

## DepOptions Objects

```python
@dataclass
class DepOptions()
```

The options selected for ordering a backlog by dependencies.

<a id="backlogops_gui.backlog_dialogs.ReleaseOrderOptions"></a>

## ReleaseOrderOptions Objects

```python
@dataclass
class ReleaseOrderOptions()
```

The options selected for ordering a backlog by release order.

<a id="backlogops_gui.backlog_dialogs.StartChoice"></a>

## StartChoice Objects

```python
@dataclass
class StartChoice()
```

The start date selected for estimating ready dates.

<a id="backlogops_gui.backlog_dialogs.KeysDialog"></a>

## KeysDialog Objects

```python
class KeysDialog(ModalDialog)
```

Modal dialog collecting the leading keys for a reordering.

<a id="backlogops_gui.backlog_dialogs.KeysDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, sink: TextIO) -> None
```

Build, show and wait for the key entry dialog.

<a id="backlogops_gui.backlog_dialogs.KeysDialog._build_text"></a>

#### \_build\_text

```python
def _build_text() -> tk.Text
```

Add the entry label, text box and the load-from-file button.

<a id="backlogops_gui.backlog_dialogs.KeysDialog._load"></a>

#### \_load

```python
def _load() -> None
```

Read a key list file into the text box, reporting failures.

<a id="backlogops_gui.backlog_dialogs.KeysDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Split the text on whitespace and close the dialog.

<a id="backlogops_gui.backlog_dialogs.DepOptionsDialog"></a>

## DepOptionsDialog Objects

```python
class DepOptionsDialog(ModalDialog)
```

Modal dialog collecting the order-by-dependencies options.

<a id="backlogops_gui.backlog_dialogs.DepOptionsDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the dependency options dialog.

<a id="backlogops_gui.backlog_dialogs.DepOptionsDialog._build"></a>

#### \_build

```python
def _build() -> None
```

Add the later check box, the mode chooser and the key entry.

<a id="backlogops_gui.backlog_dialogs.DepOptionsDialog._build_mode"></a>

#### \_build\_mode

```python
def _build_mode() -> None
```

Add the placement-mode label and chooser.

<a id="backlogops_gui.backlog_dialogs.DepOptionsDialog._build_space"></a>

#### \_build\_space

```python
def _build_space() -> None
```

Add the space-around label and key entry.

<a id="backlogops_gui.backlog_dialogs.DepOptionsDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the selected options and close the dialog.

<a id="backlogops_gui.backlog_dialogs.StartDateDialog"></a>

## StartDateDialog Objects

```python
class StartDateDialog(ModalDialog)
```

Modal dialog collecting the start date for the estimate.

<a id="backlogops_gui.backlog_dialogs.StartDateDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the start date dialog.

<a id="backlogops_gui.backlog_dialogs.StartDateDialog._build"></a>

#### \_build

```python
def _build() -> None
```

Add the start date label and entry.

<a id="backlogops_gui.backlog_dialogs.StartDateDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Parse the date, keeping the dialog open on a bad value.

<a id="backlogops_gui.backlog_dialogs.LevelsDialog"></a>

## LevelsDialog Objects

```python
class LevelsDialog(ModalDialog)
```

Modal dialog selecting the levels to extract keys at.

<a id="backlogops_gui.backlog_dialogs.LevelsDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the level selection dialog.

<a id="backlogops_gui.backlog_dialogs.LevelsDialog._build"></a>

#### \_build

```python
def _build() -> dict[int, tk.BooleanVar]
```

Add a check box for each default level and return its variables.

<a id="backlogops_gui.backlog_dialogs.LevelsDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the chosen levels, requiring at least one selection.

<a id="backlogops_gui.backlog_dialogs.DateOrderDialog"></a>

## DateOrderDialog Objects

```python
class DateOrderDialog(ModalDialog)
```

Modal dialog choosing planned or estimated date for ordering.

<a id="backlogops_gui.backlog_dialogs.DateOrderDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the date order dialog.

<a id="backlogops_gui.backlog_dialogs.DateOrderDialog._build"></a>

#### \_build

```python
def _build() -> None
```

Add the estimated-date check box, off for the planned date.

<a id="backlogops_gui.backlog_dialogs.DateOrderDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the chosen date kind and close the dialog.

<a id="backlogops_gui.backlog_dialogs.ReleaseOrderDialog"></a>

## ReleaseOrderDialog Objects

```python
class ReleaseOrderDialog(ModalDialog)
```

Modal dialog choosing options for ordering by release order.

<a id="backlogops_gui.backlog_dialogs.ReleaseOrderDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the release-order dialog.

<a id="backlogops_gui.backlog_dialogs.ReleaseOrderDialog._build"></a>

#### \_build

```python
def _build() -> None
```

Add the honor-dependencies and direction check boxes.

<a id="backlogops_gui.backlog_dialogs.ReleaseOrderDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the chosen release-order options and close.

<a id="backlogops_gui.backlog_dialogs.BufferDialog"></a>

## BufferDialog Objects

```python
class BufferDialog(ModalDialog)
```

Modal dialog collecting the buffer in calendar days.

<a id="backlogops_gui.backlog_dialogs.BufferDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the buffer days dialog.

<a id="backlogops_gui.backlog_dialogs.BufferDialog._build"></a>

#### \_build

```python
def _build() -> None
```

Add the buffer label and entry prefilled with the default.

<a id="backlogops_gui.backlog_dialogs.BufferDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Parse the buffer, keeping the dialog open on a bad value.

<a id="backlogops_gui.backlog_dialogs.ask_keys"></a>

#### ask\_keys

```python
def ask_keys(parent: tk.Misc, sink: TextIO) -> Optional[list[str]]
```

Ask for the leading keys, or None when the dialog is cancelled.

<a id="backlogops_gui.backlog_dialogs.ask_dep_options"></a>

#### ask\_dep\_options

```python
def ask_dep_options(parent: tk.Misc) -> Optional[DepOptions]
```

Ask for the dependency options, or None when cancelled.

<a id="backlogops_gui.backlog_dialogs.ask_start_date"></a>

#### ask\_start\_date

```python
def ask_start_date(parent: tk.Misc) -> Optional[StartChoice]
```

Ask for the start date, or None when the dialog is cancelled.

<a id="backlogops_gui.backlog_dialogs.ask_levels"></a>

#### ask\_levels

```python
def ask_levels(parent: tk.Misc) -> Optional[list[int]]
```

Ask for the levels to extract, or None when cancelled.

<a id="backlogops_gui.backlog_dialogs.ask_date_order"></a>

#### ask\_date\_order

```python
def ask_date_order(parent: tk.Misc) -> Optional[bool]
```

Ask whether to order by estimated date, or None when cancelled.

<a id="backlogops_gui.backlog_dialogs.ask_release_order"></a>

#### ask\_release\_order

```python
def ask_release_order(parent: tk.Misc) -> Optional[ReleaseOrderOptions]
```

Ask for the release-order options, or None when cancelled.

<a id="backlogops_gui.backlog_dialogs.ask_buffer_days"></a>

#### ask\_buffer\_days

```python
def ask_buffer_days(parent: tk.Misc) -> Optional[int]
```

Ask for the buffer in days, or None when the dialog is cancelled.

<a id="backlogops_gui.report_windows"></a>

# backlogops\_gui.report\_windows

Read-only text pop-ups for change listings and text reports.

A change listing is shown with a Save-to-file and a Dismiss button, so the
user can keep a record of what an action changed. A text report is shown
read-only but copy-pasteable, with only a Dismiss button. Both return the
created window so a caller or a test can drive or close it.

<a id="backlogops_gui.report_windows.show_change_list"></a>

#### show\_change\_list

```python
def show_change_list(parent: tk.Misc, title: str, text: str,
                     on_save: Callable[[], None]) -> tk.Toplevel
```

Show a change listing with Save-to-file and Dismiss buttons.

The listing is shown read-only. The Save button calls ``on_save`` and
the Dismiss button closes the window. The created window is returned
so a caller (or a test) can drive or close it.

<a id="backlogops_gui.report_windows.show_text_report"></a>

#### show\_text\_report

```python
def show_text_report(parent: tk.Misc, title: str, text: str) -> tk.Toplevel
```

Show read-only, copy-pasteable text with a Dismiss button.

The text is shown in a disabled text box, which still lets the user
select and copy it. The created window is returned so a caller or a
test can drive or close it.

<a id="backlogops_gui.choice_dialogs"></a>

# backlogops\_gui.choice\_dialogs

Modal button-choice dialogs shown outside a backlog window.

These dialogs present a short explanation and a column of buttons, each
selecting one enumerated value, with no OK or Cancel. The no-configuration
dialog offers to run the wizard, load a file, or exit at startup. The
preset-kind dialog asks whether a stand-alone preset file is an input or
an output preset before it is migrated.

<a id="backlogops_gui.choice_dialogs.ConfigChoice"></a>

## ConfigChoice Objects

```python
class ConfigChoice(Enum)
```

The action chosen in the no-configuration startup dialog.

<a id="backlogops_gui.choice_dialogs.PresetKind"></a>

## PresetKind Objects

```python
class PresetKind(Enum)
```

Whether a stand-alone preset file is an input or output preset.

<a id="backlogops_gui.choice_dialogs.NoConfigDialog"></a>

## NoConfigDialog Objects

```python
class NoConfigDialog()
```

Modal dialog offering to create, load, or exit without a config.

<a id="backlogops_gui.choice_dialogs.NoConfigDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the no-configuration dialog.

<a id="backlogops_gui.choice_dialogs.NoConfigDialog._build"></a>

#### \_build

```python
def _build() -> None
```

Add the explanation and the three action buttons.

<a id="backlogops_gui.choice_dialogs.NoConfigDialog._add_button"></a>

#### \_add\_button

```python
def _add_button(text: str, choice: ConfigChoice) -> None
```

Add one action button that selects the given choice.

<a id="backlogops_gui.choice_dialogs.NoConfigDialog._show"></a>

#### \_show

```python
def _show() -> None
```

Grab the focus and wait for the dialog to close.

<a id="backlogops_gui.choice_dialogs.NoConfigDialog._choose"></a>

#### \_choose

```python
def _choose(choice: ConfigChoice) -> None
```

Record the chosen action and close the dialog.

<a id="backlogops_gui.choice_dialogs.ask_no_config_choice"></a>

#### ask\_no\_config\_choice

```python
def ask_no_config_choice(parent: tk.Misc) -> ConfigChoice
```

Ask whether to run the wizard, load a file, or exit.

<a id="backlogops_gui.choice_dialogs.PresetKindDialog"></a>

## PresetKindDialog Objects

```python
class PresetKindDialog()
```

Modal dialog asking whether a preset is for input or output.

<a id="backlogops_gui.choice_dialogs.PresetKindDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the preset kind dialog.

<a id="backlogops_gui.choice_dialogs.PresetKindDialog._build"></a>

#### \_build

```python
def _build() -> None
```

Add the explanation and the two kind buttons.

<a id="backlogops_gui.choice_dialogs.PresetKindDialog._add_button"></a>

#### \_add\_button

```python
def _add_button(text: str, kind: PresetKind) -> None
```

Add one button that selects the given preset kind.

<a id="backlogops_gui.choice_dialogs.PresetKindDialog._show"></a>

#### \_show

```python
def _show() -> None
```

Grab the focus and wait for the dialog to close.

<a id="backlogops_gui.choice_dialogs.PresetKindDialog._choose"></a>

#### \_choose

```python
def _choose(kind: PresetKind) -> None
```

Record the chosen kind and close the dialog.

<a id="backlogops_gui.choice_dialogs.ask_preset_kind"></a>

#### ask\_preset\_kind

```python
def ask_preset_kind(parent: tk.Misc) -> Optional[PresetKind]
```

Ask whether a preset file is an input or output preset.

Returns the chosen kind, or None when the dialog is closed without a
choice.

<a id="backlogops_gui.format_dialogs"></a>

# backlogops\_gui.format\_dialogs

File-format option dialogs for reading and writing backlog files.

The format options mirror the command line: the format is either inferred
from the file name, taken from a named preset stored in the teams
configuration, or read from a stand-alone configuration file. Writing also
offers to put the releases before the backlog. The chosen format is
returned as a single value understood by the resolver in
:mod:`backlogops_gui.backlog_io`.

<a id="backlogops_gui.format_dialogs.format_value"></a>

#### format\_value

```python
def format_value(mode: int, preset: str, path: str) -> Optional[str]
```

Return the resolver value for a selected mode and inputs.

A preset or file mode with an empty input falls back to inference, so
an unfinished selection behaves like inferring from the file name.

<a id="backlogops_gui.format_dialogs.ReadOptions"></a>

## ReadOptions Objects

```python
@dataclass
class ReadOptions()
```

The format selection entered for reading a file.

<a id="backlogops_gui.format_dialogs.WriteOptions"></a>

## WriteOptions Objects

```python
@dataclass
class WriteOptions()
```

The format selection and ordering entered for writing a file.

<a id="backlogops_gui.format_dialogs.FormatDialog"></a>

## FormatDialog Objects

```python
class FormatDialog(ModalDialog)
```

Modal dialog collecting the format selection for one file.

<a id="backlogops_gui.format_dialogs.FormatDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, presets: Sequence[str],
             with_releases_first: bool) -> None
```

Build, show and wait for the modal format dialog.

<a id="backlogops_gui.format_dialogs.FormatDialog._build"></a>

#### \_build

```python
def _build(with_releases_first: bool) -> None
```

Create the radio buttons, inputs and action buttons.

<a id="backlogops_gui.format_dialogs.FormatDialog._add_radio"></a>

#### \_add\_radio

```python
def _add_radio(text: str, mode: int) -> None
```

Add one mode radio button.

<a id="backlogops_gui.format_dialogs.FormatDialog._add_preset_row"></a>

#### \_add\_preset\_row

```python
def _add_preset_row() -> None
```

Add the preset radio button and its choices, when available.

<a id="backlogops_gui.format_dialogs.FormatDialog._add_file_row"></a>

#### \_add\_file\_row

```python
def _add_file_row() -> None
```

Add the configuration-file radio button, entry and browse.

<a id="backlogops_gui.format_dialogs.FormatDialog._browse"></a>

#### \_browse

```python
def _browse() -> None
```

Pick a configuration file and select the file mode.

<a id="backlogops_gui.format_dialogs.FormatDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the selected format value and close the dialog.

<a id="backlogops_gui.format_dialogs.FormatDialog._selected_value"></a>

#### \_selected\_value

```python
def _selected_value() -> Optional[str]
```

Return the format value for the selected mode.

<a id="backlogops_gui.format_dialogs.ask_read_options"></a>

#### ask\_read\_options

```python
def ask_read_options(
        parent: tk.Misc,
        presets: Optional[Sequence[str]]) -> Optional[ReadOptions]
```

Ask how to read a file, or None when the dialog is cancelled.

<a id="backlogops_gui.format_dialogs.ask_write_options"></a>

#### ask\_write\_options

```python
def ask_write_options(
        parent: tk.Misc,
        presets: Optional[Sequence[str]]) -> Optional[WriteOptions]
```

Ask how to write a file, or None when the dialog is cancelled.

<a id="backlogops_gui.jira_dialogs"></a>

# backlogops\_gui.jira\_dialogs

Modal dialogs collecting the options for the Jira operations.

Reading from Jira picks a Jira preset and an editable issue filter. Adding
to Jira picks a write preset and whether to skip items whose key already
exists. Updating releases picks a preset, what to do with a missing
release name, and which releases to update. Updating the backlog picks a
preset, what to do with a missing item key, which columns to update, and
how parent and dependency links are reconciled. A separate dialog collects
the masked pass phrase for an encrypted Jira API token.

<a id="backlogops_gui.jira_dialogs.MISSING_MODE_TEXT"></a>

#### MISSING\_MODE\_TEXT

Label shown for each missing-name mode in the release-update dialog.

<a id="backlogops_gui.jira_dialogs.LINK_MODE_TEXT"></a>

#### LINK\_MODE\_TEXT

Label shown for each link-update mode in the backlog-update dialog.

The keys mirror the CLI ``--links`` values; ``reconcile`` maps to
:class:`LinkUpdate.RECONCILE` and ``add`` to :class:`LinkUpdate.ADD_MISSING`.

<a id="backlogops_gui.jira_dialogs.JiraPresetOptions"></a>

## JiraPresetOptions Objects

```python
@dataclass
class JiraPresetOptions()
```

Base for the Jira option dataclasses that name a Jira preset.

<a id="backlogops_gui.jira_dialogs.JiraReadOptions"></a>

## JiraReadOptions Objects

```python
@dataclass
class JiraReadOptions(JiraPresetOptions)
```

The Jira preset and issue filter selected for reading from Jira.

<a id="backlogops_gui.jira_dialogs.JiraWriteOptions"></a>

## JiraWriteOptions Objects

```python
@dataclass
class JiraWriteOptions(JiraPresetOptions)
```

The Jira write preset and existing-key choice for adding to Jira.

<a id="backlogops_gui.jira_dialogs.JiraReleaseUpdateOptions"></a>

## JiraReleaseUpdateOptions Objects

```python
@dataclass
class JiraReleaseUpdateOptions(JiraPresetOptions)
```

The preset, missing-name mode and selected names for updating.

<a id="backlogops_gui.jira_dialogs.JiraBacklogUpdateOptions"></a>

## JiraBacklogUpdateOptions Objects

```python
@dataclass
class JiraBacklogUpdateOptions(JiraPresetOptions)
```

The preset, missing-key mode, fields and link policy for updating.

<a id="backlogops_gui.jira_dialogs.JiraReadDialog"></a>

## JiraReadDialog Objects

```python
class JiraReadDialog(ModalDialog)
```

Modal dialog collecting the Jira preset and issue filter.

<a id="backlogops_gui.jira_dialogs.JiraReadDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, preset_filters: Mapping[str, str]) -> None
```

Build, show and wait for the Jira read dialog.

<a id="backlogops_gui.jira_dialogs.JiraReadDialog._build"></a>

#### \_build

```python
def _build(names: Sequence[str]) -> None
```

Add the preset chooser and editable filter field.

<a id="backlogops_gui.jira_dialogs.JiraReadDialog._preset_changed"></a>

#### \_preset\_changed

```python
def _preset_changed(_event: object) -> None
```

Show the selected preset's default issue filter.

<a id="backlogops_gui.jira_dialogs.JiraReadDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the selected preset and filter, requiring a preset.

<a id="backlogops_gui.jira_dialogs.ask_jira_read_options"></a>

#### ask\_jira\_read\_options

```python
def ask_jira_read_options(
        parent: tk.Misc,
        preset_filters: Mapping[str, str]) -> Optional[JiraReadOptions]
```

Ask which Jira preset and filter to read, or None when cancelled.

<a id="backlogops_gui.jira_dialogs.JiraWriteDialog"></a>

## JiraWriteDialog Objects

```python
class JiraWriteDialog(ModalDialog)
```

Modal dialog collecting the Jira write preset and skip choice.

<a id="backlogops_gui.jira_dialogs.JiraWriteDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, presets: Sequence[str]) -> None
```

Build, show and wait for the Jira write dialog.

<a id="backlogops_gui.jira_dialogs.JiraWriteDialog._build"></a>

#### \_build

```python
def _build(names: Sequence[str]) -> None
```

Add the preset chooser and the skip-existing checkbox.

<a id="backlogops_gui.jira_dialogs.JiraWriteDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the selected preset and skip choice, requiring a preset.

<a id="backlogops_gui.jira_dialogs.ask_jira_write_options"></a>

#### ask\_jira\_write\_options

```python
def ask_jira_write_options(
        parent: tk.Misc, presets: Sequence[str]) -> Optional[JiraWriteOptions]
```

Ask which write preset and skip choice, or None when cancelled.

<a id="backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog"></a>

## JiraReleaseUpdateDialog Objects

```python
class JiraReleaseUpdateDialog(ModalDialog)
```

Modal dialog for the release-update preset, mode and selection.

<a id="backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, presets: Sequence[str],
             release_names: Sequence[str]) -> None
```

Build, show and wait for the release-update dialog.

<a id="backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog._build"></a>

#### \_build

```python
def _build(names: Sequence[str], release_names: Sequence[str]) -> None
```

Add the preset chooser, the mode radios and the release picks.

<a id="backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog._build_preset"></a>

#### \_build\_preset

```python
def _build_preset(names: Sequence[str]) -> None
```

Add the Jira preset label and read-only chooser.

<a id="backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog._build_mode"></a>

#### \_build\_mode

```python
def _build_mode() -> None
```

Add the radios choosing what to do with a missing release.

<a id="backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog._build_releases"></a>

#### \_build\_releases

```python
def _build_releases(release_names: Sequence[str]) -> None
```

Add a checkbox per release, all selected by default.

<a id="backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the preset, mode and picks, requiring a preset.

<a id="backlogops_gui.jira_dialogs.ask_release_update"></a>

#### ask\_release\_update

```python
def ask_release_update(
        parent: tk.Misc, presets: Sequence[str],
        release_names: Sequence[str]) -> Optional[JiraReleaseUpdateOptions]
```

Ask the preset, missing-name mode and releases, None when cancelled.

<a id="backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog"></a>

## JiraBacklogUpdateDialog Objects

```python
class JiraBacklogUpdateDialog(ModalDialog)
```

Modal dialog for the backlog-update preset, mode, fields and links.

The field checkboxes depend on the selected preset, so they are rebuilt
whenever the preset changes. ``preset_fields`` maps each preset name to
the internal fields it can update.

<a id="backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, preset_fields: Mapping[str,
                                                     Sequence[str]]) -> None
```

Build, show and wait for the backlog-update dialog.

<a id="backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._build"></a>

#### \_build

```python
def _build(names: Sequence[str]) -> None
```

Add the preset, the mode radios, the links box and the fields.

<a id="backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._build_preset"></a>

#### \_build\_preset

```python
def _build_preset(names: Sequence[str]) -> None
```

Add the Jira preset label and read-only chooser.

<a id="backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._build_mode"></a>

#### \_build\_mode

```python
def _build_mode() -> None
```

Add the radios choosing what to do with a missing key.

<a id="backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._build_links"></a>

#### \_build\_links

```python
def _build_links() -> None
```

Add the radios choosing how parent and dependency links update.

<a id="backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._build_fields"></a>

#### \_build\_fields

```python
def _build_fields() -> None
```

Rebuild the field checkboxes for the selected preset.

<a id="backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._preset_changed"></a>

#### \_preset\_changed

```python
def _preset_changed(_event: object) -> None
```

Rebuild the field checkboxes for the newly selected preset.

<a id="backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the preset, mode, fields and link policy, requiring both.

<a id="backlogops_gui.jira_dialogs.ask_backlog_update"></a>

#### ask\_backlog\_update

```python
def ask_backlog_update(
    parent: tk.Misc, preset_fields: Mapping[str, Sequence[str]]
) -> Optional[JiraBacklogUpdateOptions]
```

Ask the preset, mode, fields and link policy, None when cancelled.

<a id="backlogops_gui.jira_dialogs.PassphraseDialog"></a>

## PassphraseDialog Objects

```python
class PassphraseDialog(ModalDialog)
```

Modal dialog collecting a masked pass phrase.

<a id="backlogops_gui.jira_dialogs.PassphraseDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the pass phrase dialog.

<a id="backlogops_gui.jira_dialogs.PassphraseDialog._build"></a>

#### \_build

```python
def _build() -> None
```

Add the masked pass phrase entry.

<a id="backlogops_gui.jira_dialogs.PassphraseDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the entered pass phrase and close the dialog.

<a id="backlogops_gui.jira_dialogs.ask_jira_passphrase"></a>

#### ask\_jira\_passphrase

```python
def ask_jira_passphrase(parent: tk.Misc) -> Optional[str]
```

Ask for the Jira token pass phrase, or None when cancelled.

<a id="backlogops_gui.gui_style"></a>

# backlogops\_gui.gui\_style

Shared look and focus helpers for the Tkinter input windows.

Editable input widgets blend into the window background on some
platforms, so the user cannot tell an entry, drop-down or list from the
surrounding window. :func:`style_input` gives such a widget a white
field and a thin border so it stands out. :func:`focus_first_input`
puts the keyboard focus on the first editable widget of a window, so the
user can start typing as soon as the window opens.

<a id="backlogops_gui.gui_style.style_input"></a>

#### style\_input

```python
def style_input(widget: tk.Widget) -> None
```

Make one editable input widget stand out from the background.

A classic entry, text box or list gets a white field and a thin
solid border. A drop-down keeps its arrow but gets a white field
through a shared ttk style. Any other widget is left unchanged. The
ttk styling is best-effort: a native theme that ignores field colors
leaves the drop-down as it is.

<a id="backlogops_gui.gui_style._style_combobox"></a>

#### \_style\_combobox

```python
def _style_combobox(widget: ttk.Combobox) -> None
```

Give a drop-down a white field through a shared ttk style.

<a id="backlogops_gui.gui_style.focus_first_input"></a>

#### focus\_first\_input

```python
def focus_first_input(window: tk.Misc) -> None
```

Give the keyboard focus to the first editable input, if any.

<a id="backlogops_gui.gui_style._first_input"></a>

#### \_first\_input

```python
def _first_input(parent: tk.Misc) -> Optional[tk.Misc]
```

Return the first editable input under parent, in child order.

<a id="backlogops_gui.gui_style._is_input"></a>

#### \_is\_input

```python
def _is_input(widget: tk.Misc) -> bool
```

Return whether the widget is an editable input to fill in.

<a id="backlogops_gui.gui_wizard"></a>

# backlogops\_gui.gui\_wizard

Graphical bridge that drives the synchronous config wizard.

The backlog-ops configuration wizard asks its questions through a
:class:`WizardUiBridge`. This module provides :class:`TkWizardBridge`, a
concrete bridge that overrides every typed ask method of that base class
with a real Tkinter control. All questions are answered in one reused
:class:`~backlogops_gui.wizard_window.WizardWindow`, so the whole wizard
session happens in a single pop-up that does not jump around the display.

<a id="backlogops_gui.gui_wizard.TkWizardBridge"></a>

## TkWizardBridge Objects

```python
class TkWizardBridge(WizardUiBridge)
```

Bridge that answers wizard prompts in one reused Tkinter window.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, log: Optional[TextIO] = None) -> None
```

Store the parent window and the optional diagnostics log.

**Arguments**:

- `parent` - The window the wizard window is shown over.
- `log` - Stream that receives low-level wizard diagnostics.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.ask_text"></a>

#### ask\_text

```python
def ask_text(question: str,
             re_ask_reason: Optional[str] = None,
             nullable: bool = False,
             *,
             default: Optional[str] = None,
             sensitive: bool = False) -> Optional[str]
```

Ask for free text; see WizardUiBridge.ask_text.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.ask_yes_no"></a>

#### ask\_yes\_no

```python
def ask_yes_no(question: str,
               default: bool,
               re_ask_reason: Optional[str] = None) -> bool
```

Ask a yes/no question with dedicated yes and no buttons.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.ask_choice"></a>

#### ask\_choice

```python
def ask_choice(question: str,
               *,
               choices: Sequence[str],
               default: Optional[str] = None,
               re_ask_reason: Optional[str] = None) -> str
```

Ask the user to pick one choice from a single-selection list.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.ask_multi"></a>

#### ask\_multi

```python
def ask_multi(question: str,
              *,
              choices: Sequence[str],
              default: Optional[Sequence[str]] = None,
              min_select: int = 0,
              max_select: Optional[int] = None,
              re_ask_reason: Optional[str] = None) -> list[str]
```

Ask the user to pick several choices from a multi-selection list.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.ask_table"></a>

#### ask\_table

```python
def ask_table(columns: Sequence[TableColumn],
              cells: list[list[TableCell]],
              question: str,
              *,
              re_ask_reason: Optional[str] = None,
              partial_check: Optional[PartialCheck] = None,
              min_rows: Optional[int] = None,
              max_rows: Optional[int] = None) -> list[list[Optional[str]]]
```

Ask the user to fill an editable table of the given rows.

With both ``min_rows`` and ``max_rows`` given the table has a
variable number of rows: add-row and remove-row buttons grow the
table up to ``max_rows`` and shrink it down to ``min_rows``.
Otherwise the rows given in ``cells`` are fixed and only filled.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.show"></a>

#### show

```python
def show(message: str) -> None
```

Show an informational message to the user.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.error_file"></a>

#### error\_file

```python
def error_file() -> TextIO
```

Return the stream used for low-level wizard diagnostics.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.close"></a>

#### close

```python
def close() -> None
```

Close the wizard window when one was opened.

<a id="backlogops_gui.gui_wizard.TkWizardBridge._window_obj"></a>

#### \_window\_obj

```python
def _window_obj() -> WizardWindow
```

Return the wizard window, creating it on first use.

<a id="backlogops_gui.jira_base"></a>

# backlogops\_gui.jira\_base

Shared behavior for the Jira operations of the application.

The Jira read, write and update operations all resolve a Jira connection
and materialize an encrypted API token before starting, run their network
call on a worker thread, and hand success or failure back to the GUI
thread. :class:`JiraAction` holds a reference to the running
:class:`~backlogops_gui.application.BacklogApp` and provides those shared
steps, so each concrete Jira collaborator only implements the call, the
success reporting and, where needed, the dialog that gathers its options.

<a id="backlogops_gui.jira_base.JiraAction"></a>

## JiraAction Objects

```python
class JiraAction()
```

Base for the Jira menu actions, sharing the app and worker steps.

<a id="backlogops_gui.jira_base.JiraAction.__init__"></a>

#### \_\_init\_\_

```python
def __init__(app: 'BacklogApp') -> None
```

Store the application whose window, log and config are used.

<a id="backlogops_gui.jira_base.JiraAction._config"></a>

#### \_config

```python
def _config() -> BacklogOpsConfig
```

Return the active configuration, which the caller ensured is set.

<a id="backlogops_gui.jira_base.JiraAction._available"></a>

#### \_available

```python
def _available() -> bool
```

Return whether a configuration with Jira presets is loaded.

<a id="backlogops_gui.jira_base.JiraAction._presets"></a>

#### \_presets

```python
def _presets() -> list[str]
```

Return the Jira preset names of the configuration, sorted.

<a id="backlogops_gui.jira_base.JiraAction._connections"></a>

#### \_connections

```python
def _connections() -> JiraConnections
```

Return the Jira connections of the configuration.

<a id="backlogops_gui.jira_base.JiraAction._jira_connection"></a>

#### \_jira\_connection

```python
def _jira_connection(preset_name: str) -> JiraConnectConfig
```

Return the Jira connection used by the named preset.

<a id="backlogops_gui.jira_base.JiraAction._prepare_jira_token"></a>

#### \_prepare\_jira\_token

```python
def _prepare_jira_token(preset_name: str) -> bool
```

Materialize an encrypted Jira token before the worker starts.

<a id="backlogops_gui.jira_base.JiraAction._start"></a>

#### \_start

```python
def _start(preset_name: str, verb: str, worker: Callable[[], None]) -> None
```

Prepare the token, log the start, and run the worker on a thread.

``verb`` is spliced into the "<verb> using preset '<name>'..." start
message logged before the worker thread runs. Nothing runs when the
token could not be materialized.

<a id="backlogops_gui.jira_base.JiraAction._dispatch"></a>

#### \_dispatch

```python
def _dispatch(title: str, preset_name: str, call: Callable[[], _R],
              done: Callable[[_R], None]) -> None
```

Run the Jira call and hand its result to the GUI thread.

A call raising one of the known Jira errors is reported under
``title`` for ``preset_name``; otherwise the result is passed to
``done``. Both run on the GUI thread if the main window still exists.

<a id="backlogops_gui.jira_base.JiraAction._after"></a>

#### \_after

```python
def _after(callback: Callable[[], None]) -> None
```

Schedule a GUI-thread callback if the main window still exists.

<a id="backlogops_gui.jira_base.JiraAction._fail"></a>

#### \_fail

```python
def _fail(title: str, preset_name: str, message: str) -> None
```

Log and report a failed Jira operation for one preset.

<a id="backlogops_gui.jira_base.JiraAction._finish"></a>

#### \_finish

```python
def _finish(on_done: Callable[[_R], None], result: _R, summary: str) -> None
```

Hand the result to the window and log a completion summary.

<a id="backlogops_gui._migrate_warn"></a>

# backlogops\_gui.\_migrate\_warn

Backward-compatibility warning hooks for the graphical interface.

When the application reads a file that needed backward-compatible
normalization (Reading an Old Configuration File), one of these hooks
prints the standard migration warning followed by menu-specific
instructions. ``GuiMigrateWarnHook`` is used when the old file is the
running backlog-ops configuration and points at the ``Write
configuration…`` menu action. ``GuiPresetMigrateWarnHook`` is used when
the old file is a stand-alone input or output preset file and points at
the ``Migrate IO preset file…`` menu action, because rewriting the
running configuration would not update that preset file. The warning is
written to the diagnostics stream, which the application shows in its log
view. The leading underscore in the module name marks it as an internal
helper.

<a id="backlogops_gui._migrate_warn.GuiMigrateWarnHook"></a>

## GuiMigrateWarnHook Objects

```python
class GuiMigrateWarnHook(MigrateCfgWarnHook)
```

Tell the user to migrate an old config file from the menu.

<a id="backlogops_gui._migrate_warn.GuiMigrateWarnHook.migrate_instructions"></a>

#### migrate\_instructions

```python
@classmethod
def migrate_instructions(cls) -> str
```

Return the graphical interface migration instructions.

**Returns**:

  Text that points the user at the ``Write configuration…`` menu
  action to rewrite the configuration in the current format.

<a id="backlogops_gui._migrate_warn.GuiPresetMigrateWarnHook"></a>

## GuiPresetMigrateWarnHook Objects

```python
class GuiPresetMigrateWarnHook(MigrateCfgWarnHook)
```

Tell the user to migrate an old preset file from the menu.

<a id="backlogops_gui._migrate_warn.GuiPresetMigrateWarnHook.migrate_instructions"></a>

#### migrate\_instructions

```python
@classmethod
def migrate_instructions(cls) -> str
```

Return the graphical interface preset migration instructions.

**Returns**:

  Text that points the user at the ``Migrate IO preset file…``
  menu action to rewrite the preset file in the current format.

<a id="backlogops_gui.application"></a>

# backlogops\_gui.application

Tkinter application for backlog operations.

The application opens a main window whose menu reads a backlog from a file,
loads or replaces the active configuration from a file, runs the teams
configuration wizard, creates a stand-alone input or output
preset file, migrates a stand-alone preset file to the current format,
writes the running configuration to a file, and creates a
demonstration backlog. Each backlog opens in its own
window. On macOS the menu bar sits at the top of the display rather than in
the window, so the main window body shows a short description, the current
configuration status, and a log of the most recent diagnostic messages, to
make clear that the application is running. The teams configuration is
taken from the file given with ``-c`` or from the configured locations;
when no configuration is found a startup dialog offers to run the wizard,
load a configuration file, or exit. Cancelling the wizard or a dialog
returns to that choice, so the application ends only when the user exits.
The Jira menu actions of a backlog window are delegated to the collaborator
objects in :mod:`backlogops_gui.jira_read`, :mod:`backlogops_gui.jira_write`
and :mod:`backlogops_gui.jira_update`.

<a id="backlogops_gui.application.initial_config"></a>

#### initial\_config

```python
def initial_config(
    config_arg: Optional[str],
    sink: Optional[TextIO] = None
) -> tuple[Optional[BacklogOpsConfig], Optional[str]]
```

Return the startup configuration and an optional error message.

The configuration is looked up as documented for
:func:`backlogops.get_backlog_ops_config`. A failure is mapped to a
None configuration and the error text, so the caller can decide
whether to show the error and offer the no-configuration choices.
Diagnostics are captured, so a loader that reports a missing file and
then calls ``sys.exit`` becomes an error message instead of ending
the program.

**Arguments**:

- `config_arg` - The file from ``-c``, or None to search the defaults.
- `sink` - Stream for diagnostics, or None to discard them.
  

**Returns**:

  The loaded configuration and None, or None and the error text.

<a id="backlogops_gui.application._config_failure"></a>

#### \_config\_failure

```python
def _config_failure(captured: StringIO, fallback: str) -> str
```

Return the captured diagnostics, or the fallback when there are none.

<a id="backlogops_gui.application.BacklogApp"></a>

## BacklogApp Objects

```python
class BacklogApp()
```

The backlog operations application and its menu actions.

<a id="backlogops_gui.application.BacklogApp.__init__"></a>

#### \_\_init\_\_

```python
def __init__(root: tk.Tk, config: Optional[BacklogOpsConfig] = None) -> None
```

Store the window, config, log and Jira collaborators.

<a id="backlogops_gui.application.BacklogApp.in_presets"></a>

#### in\_presets

```python
def in_presets() -> Optional[dict[str, InputFormatConfig]]
```

Return the input presets of the current configuration.

<a id="backlogops_gui.application.BacklogApp.out_presets"></a>

#### out\_presets

```python
def out_presets() -> Optional[dict[str, OutputFormatConfig]]
```

Return the output presets of the current configuration.

<a id="backlogops_gui.application.BacklogApp.available_teams"></a>

#### available\_teams

```python
def available_teams() -> Optional[AvailableTeams]
```

Return the loaded workforce, or None when absent.

<a id="backlogops_gui.application.BacklogApp.levels"></a>

#### levels

```python
def levels() -> Optional[Levels]
```

Return the configured backlog item levels, or None when absent.

<a id="backlogops_gui.application.BacklogApp.status_map"></a>

#### status\_map

```python
def status_map() -> Optional[dict[str, Status]]
```

Return the library-wide status input map, or None when absent.

<a id="backlogops_gui.application.BacklogApp.gui_display"></a>

#### gui\_display

```python
def gui_display() -> GuiDisplayConfig
```

Return the GUI display configuration (level display and maps).

<a id="backlogops_gui.application.BacklogApp.show_error"></a>

#### show\_error

```python
def show_error(title: str, message: str) -> None
```

Show an error message to the user.

<a id="backlogops_gui.application.BacklogApp.show_info"></a>

#### show\_info

```python
def show_info(title: str, message: str) -> None
```

Show an informational message to the user.

<a id="backlogops_gui.application.BacklogApp.start"></a>

#### start

```python
def start(config_arg: Optional[str]) -> bool
```

Load the startup configuration, offering choices if needed.

A configuration named with ``-c`` that cannot be read is reported
before the no-configuration dialog is shown. When no configuration
is loaded the user may run the wizard, load a file, or exit, and
the application is ready only once a configuration is in place.

**Arguments**:

- `config_arg` - The file from ``-c``, or None to search defaults.
  

**Returns**:

  Whether the application is ready to enter its main loop.

<a id="backlogops_gui.application.BacklogApp._resolve_missing_config"></a>

#### \_resolve\_missing\_config

```python
def _resolve_missing_config() -> bool
```

Offer to create, load, or exit until a configuration is ready.

The no-configuration dialog is shown repeatedly: running the
wizard or loading a file makes the application ready, while
cancelling either one returns to the dialog. Only the exit choice,
or closing the dialog, ends the application.

<a id="backlogops_gui.application.BacklogApp._adopt_startup_wizard"></a>

#### \_adopt\_startup\_wizard

```python
def _adopt_startup_wizard() -> bool
```

Run the startup wizard, adopting a configuration it produces.

<a id="backlogops_gui.application.BacklogApp._adopt_loaded_config"></a>

#### \_adopt\_loaded\_config

```python
def _adopt_loaded_config() -> bool
```

Load a chosen configuration file, adopting it on success.

<a id="backlogops_gui.application.BacklogApp._run_bridge_wizard"></a>

#### \_run\_bridge\_wizard

```python
def _run_bridge_wizard(wizard: Callable[[WizardUiBridge], _WizardConfig],
                       error_title: str) -> Optional[_WizardConfig]
```

Run a wizard over a fresh Tk bridge, returning its config or None.

An abandoned wizard ends in ``EOFError`` and yields None; any other
wizard failure is reported under ``error_title`` and also yields
None. The bridge window is always closed afterwards.

<a id="backlogops_gui.application.BacklogApp.run_wizard"></a>

#### run\_wizard

```python
def run_wizard() -> Optional[BacklogOpsConfig]
```

Run the config wizard and return its configuration, or None.

<a id="backlogops_gui.application.BacklogApp._load_config_file"></a>

#### \_load\_config\_file

```python
def _load_config_file() -> None
```

Load a chosen configuration file and make it the active config.

Opens a file chooser; if the user cancels nothing changes. On a
successful load the in-RAM configuration is replaced, the status
line is updated, and a confirmation dialog is shown. On failure
the current configuration is kept and an error is reported.

<a id="backlogops_gui.application.BacklogApp.run_config_wizard"></a>

#### run\_config\_wizard

```python
def run_config_wizard() -> None
```

Run the wizard and make a new configuration active on success.

<a id="backlogops_gui.application.BacklogApp.create_preset_file"></a>

#### create\_preset\_file

```python
def create_preset_file() -> None
```

Run the IO preset wizard and write the preset to a chosen file.

<a id="backlogops_gui.application.BacklogApp.migrate_preset_file"></a>

#### migrate\_preset\_file

```python
def migrate_preset_file() -> None
```

Migrate a stand-alone IO preset file to the current format.

The user picks an existing preset file, says whether it is an
input or output preset, and picks a destination. The destination
receives the ``.cfg`` extension when missing and must not already
exist. Cancelling any step does nothing; the outcome is reported.

<a id="backlogops_gui.application.BacklogApp._migrate_preset"></a>

#### \_migrate\_preset

```python
def _migrate_preset(in_path: str, out_path: str, kind: PresetKind) -> None
```

Migrate one preset file and report success or failure.

``migrate_cfg`` raises ``SystemExit`` when the input is missing or
the output already exists, and the configuration classes raise the
``IO_ERRORS`` when the file cannot be read or written. Either way
the captured diagnostics are logged and shown to the user.

<a id="backlogops_gui.application.BacklogApp._migrate_failed"></a>

#### \_migrate\_failed

```python
def _migrate_failed(captured: StringIO, fallback: str) -> None
```

Log captured diagnostics and report a preset migration failure.

<a id="backlogops_gui.application.BacklogApp.write_config"></a>

#### write\_config

```python
def write_config() -> None
```

Write the running configuration to a chosen file.

<a id="backlogops_gui.application.BacklogApp._write_to_chosen"></a>

#### \_write\_to\_chosen

```python
def _write_to_chosen(config: Config, fail_title: str, ok_title: str) -> None
```

Write a configuration to a user-chosen file and report the outcome.

The chosen filename receives the ``.cfg`` extension when missing. A
cancelled chooser writes nothing; a write failure is reported under
``fail_title`` and a success under ``ok_title``.

<a id="backlogops_gui.application.BacklogApp.read_backlog_file"></a>

#### read\_backlog\_file

```python
def read_backlog_file() -> None
```

Read a backlog from a chosen file into a new window.

<a id="backlogops_gui.application.BacklogApp.new_demo_backlog"></a>

#### new\_demo\_backlog

```python
def new_demo_backlog() -> None
```

Open a demonstration backlog in a new window.

<a id="backlogops_gui.application.BacklogApp.open_backlog"></a>

#### open\_backlog

```python
def open_backlog(data: BacklogReleases,
                 title: str,
                 warning: Optional[str] = None) -> None
```

Open one backlog and its releases in a new window.

<a id="backlogops_gui.application.BacklogApp.report_versions"></a>

#### report\_versions

```python
def report_versions() -> None
```

Report version information into the log on a worker thread.

The report queries PyPI for newer releases, which can take several
seconds, so it runs on a daemon thread that only writes to the log
buffer. The periodic refresh then shows the result in the window.

<a id="backlogops_gui.application.BacklogApp._write_version_report"></a>

#### \_write\_version\_report

```python
def _write_version_report() -> None
```

Write the version report to the log buffer.

This runs on a worker thread and must not touch any widgets. A
failure, such as missing network access, is written to the log
rather than raised on the worker thread where it would be lost.

<a id="backlogops_gui.application.BacklogApp.build_menu"></a>

#### build\_menu

```python
def build_menu() -> None
```

Build the menu bar of the main window.

<a id="backlogops_gui.application.BacklogApp._add_file_menu"></a>

#### \_add\_file\_menu

```python
def _add_file_menu(menubar: tk.Menu) -> None
```

Add the file menu with the backlog and exit actions.

<a id="backlogops_gui.application.BacklogApp._add_config_menu"></a>

#### \_add\_config\_menu

```python
def _add_config_menu(menubar: tk.Menu) -> None
```

Add the configuration menu with the wizard and write actions.

<a id="backlogops_gui.application.BacklogApp._add_help_menu"></a>

#### \_add\_help\_menu

```python
def _add_help_menu(menubar: tk.Menu) -> None
```

Add the help menu with the version report action.

<a id="backlogops_gui.application.BacklogApp.build_body"></a>

#### build\_body

```python
def build_body() -> None
```

Build the main window body and start the log refresh.

<a id="backlogops_gui.application.BacklogApp._add_warning"></a>

#### \_add\_warning

```python
def _add_warning(warning: Optional[str]) -> None
```

Show a red warning label in the main window, when present.

<a id="backlogops_gui.application.BacklogApp._build_log_view"></a>

#### \_build\_log\_view

```python
def _build_log_view() -> None
```

Build the read-only log view in the main window.

<a id="backlogops_gui.application.BacklogApp._status_text"></a>

#### \_status\_text

```python
def _status_text() -> str
```

Return the configuration status line for the main window.

<a id="backlogops_gui.application.BacklogApp._update_status"></a>

#### \_update\_status

```python
def _update_status() -> None
```

Refresh the configuration status line, when it is shown.

<a id="backlogops_gui.application.BacklogApp.refresh_log"></a>

#### refresh\_log

```python
def refresh_log() -> None
```

Copy the latest log lines into the read-only log view.

<a id="backlogops_gui.application.BacklogApp._log_selection"></a>

#### \_log\_selection

```python
def _log_selection() -> Optional[tuple[str, str]]
```

Return the selected log range, or None when nothing is selected.

<a id="backlogops_gui.application.BacklogApp._copy_log"></a>

#### \_copy\_log

```python
def _copy_log(_event: object) -> str
```

Copy the selected log text to the clipboard.

<a id="backlogops_gui.application.BacklogApp._schedule_refresh"></a>

#### \_schedule\_refresh

```python
def _schedule_refresh() -> None
```

Refresh the log view and schedule the next refresh.

<a id="backlogops_gui.application._build_parser"></a>

#### \_build\_parser

```python
def _build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the GUI launcher.

<a id="backlogops_gui.application.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> None
```

Start the backlog operations GUI.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.

<a id="backlogops_gui.tcltk_version"></a>

# backlogops\_gui.tcltk\_version

Tcl/Tk version checks for the backlog operations GUI.

<a id="backlogops_gui.tcltk_version._parse_tcltk_version"></a>

#### \_parse\_tcltk\_version

```python
def _parse_tcltk_version(version_text: str) -> Optional[tuple[int, int, int]]
```

Return a comparable Tcl/Tk version tuple, or None if malformed.

<a id="backlogops_gui.tcltk_version._old_version_warning"></a>

#### \_old\_version\_warning

```python
def _old_version_warning(version_text: str) -> str
```

Return the warning text for an older Tcl/Tk version.

<a id="backlogops_gui.tcltk_version._bad_version_warning"></a>

#### \_bad\_version\_warning

```python
def _bad_version_warning(version_text: str) -> str
```

Return the warning text for malformed or unreadable version data.

<a id="backlogops_gui.tcltk_version.warning_for_version"></a>

#### warning\_for\_version

```python
def warning_for_version(version_text: str) -> Optional[str]
```

Return a warning for unsupported Tcl/Tk versions, if needed.

<a id="backlogops_gui.tcltk_version.check_tcltk_version"></a>

#### check\_tcltk\_version

```python
def check_tcltk_version(root: tk.Tk) -> Optional[str]
```

Return a warning if the running Tcl/Tk version may be unsuitable.

<a id="backlogops_gui.jira_read"></a>

# backlogops\_gui.jira\_read

Read a backlog and its releases from Jira into a new window.

The reader asks for a Jira preset and an issue filter, then reads on a
worker thread and opens the result in a new backlog window on the GUI
thread. Jira data that is not fully consistent still opens, but with a
warning that disables the backlog operations, so the user can inspect and
save it without acting on inconsistent data.

<a id="backlogops_gui.jira_read.JiraReader"></a>

## JiraReader Objects

```python
class JiraReader(JiraAction)
```

Reads a backlog from Jira into a new window.

<a id="backlogops_gui.jira_read.JiraReader.read_backlog"></a>

#### read\_backlog

```python
def read_backlog() -> None
```

Read a backlog from Jira into a new window.

<a id="backlogops_gui.jira_read.JiraReader._preset_filters"></a>

#### \_preset\_filters

```python
def _preset_filters() -> dict[str, str]
```

Return Jira preset names mapped to their default filters.

<a id="backlogops_gui.jira_read.JiraReader._read_worker"></a>

#### \_read\_worker

```python
def _read_worker(options: JiraReadOptions) -> None
```

Read Jira data on a worker and schedule the GUI update.

<a id="backlogops_gui.jira_read.JiraReader._consistency_warning"></a>

#### \_consistency\_warning

```python
def _consistency_warning(data: BacklogReleases) -> Optional[str]
```

Return a warning if the Jira data is not fully consistent.

<a id="backlogops_gui.backlog_actions"></a>

# backlogops\_gui.backlog\_actions

Backlog operations driven from a backlog window.

Each function asks for the options an operation needs, runs the operation
on the backlog data, refreshes the view, and reports the outcome through
``on_error`` and ``on_info`` callbacks. Keeping the operations in module
functions lets them be tested without a display and keeps the window class
focused on its widgets. Saving to a file and the Jira result appliers live
here too, so the same reporting pattern is shared.

<a id="backlogops_gui.backlog_actions.save_backlog"></a>

#### save\_backlog

```python
def save_backlog(parent: tk.Misc, data: BacklogReleases,
                 presets: Optional[dict[str, OutputFormatConfig]],
                 levels: Optional[Levels], sink: TextIO,
                 on_error: Callable[[str, str],
                                    None], on_info: Callable[[str, str],
                                                             None]) -> None
```

Ask where and how to save a backlog and write it.

**Arguments**:

- `parent` - The window the dialogs are shown over.
- `data` - The backlog and releases to write.
- `presets` - Named output presets, or None when none are configured.
- `levels` - The levels used to write level names, or None for the
  default levels.
- `sink` - Stream that receives low-level write diagnostics.
- `on_error` - Callback used to report a write failure.
- `on_info` - Callback used to report a successful write.

<a id="backlogops_gui.backlog_actions._apply_change"></a>

#### \_apply\_change

```python
def _apply_change(change: Callable[[], None], refresh: Callable[[], None],
                  on_error: Callable[[str, str],
                                     None], on_info: Callable[[str, str],
                                                              None],
                  fail_title: str, ok_title: str, ok_message: str) -> None
```

Run a backlog change, refresh the view and report the outcome.

A change that raises one of the known data errors is reported through
``on_error`` and leaves the view unchanged. A successful change
refreshes the view and is reported through ``on_info``.

<a id="backlogops_gui.backlog_actions.order_by_keys"></a>

#### order\_by\_keys

```python
def order_by_keys(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                  refresh: Callable[[], None], on_error: Callable[[str, str],
                                                                  None],
                  on_info: Callable[[str, str], None]) -> None
```

Ask for leading keys and move those items to the front.

<a id="backlogops_gui.backlog_actions.order_by_deps"></a>

#### order\_by\_deps

```python
def order_by_deps(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                  refresh: Callable[[], None], on_error: Callable[[str, str],
                                                                  None],
                  on_info: Callable[[str, str], None]) -> None
```

Ask for the options and order the backlog by dependencies.

<a id="backlogops_gui.backlog_actions._release_order_message"></a>

#### \_release\_order\_message

```python
def _release_order_message(honor: bool, later: bool) -> str
```

Return the success message describing a release-order action.

<a id="backlogops_gui.backlog_actions.order_by_release"></a>

#### order\_by\_release

```python
def order_by_release(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                     refresh: Callable[[],
                                       None], on_error: Callable[[str, str],
                                                                 None],
                     on_info: Callable[[str, str], None]) -> None
```

Ask for options and order the backlog by release order.

<a id="backlogops_gui.backlog_actions.save_changes"></a>

#### save\_changes

```python
def save_changes(parent: tk.Misc, write_changes: Optional[Callable[[str],
                                                                   None]],
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None
```

Ask for a file and write the change list to it.

A ``write_changes`` of None means there are no changes, so nothing is
written and that is reported through ``on_info`` instead.

<a id="backlogops_gui.backlog_actions.show_changes"></a>

#### show\_changes

```python
def show_changes(parent: tk.Misc, title: str, text: str,
                 write_changes: Optional[Callable[[str], None]],
                 on_error: Callable[[str, str],
                                    None], on_info: Callable[[str, str],
                                                             None]) -> None
```

Show the change listing in a pop-up that can save it to a file.

<a id="backlogops_gui.backlog_actions._date_report"></a>

#### \_date\_report

```python
def _date_report(changes: ReleaseDateChanges,
                 sink: TextIO) -> tuple[str, Optional[Callable[[str], None]]]
```

Return the date change listing and a writer, None when empty.

The native save dialog has already confirmed the overwrite, so the
writer allows overwriting an existing file.

<a id="backlogops_gui.backlog_actions._content_report"></a>

#### \_content\_report

```python
def _content_report(
        changes: ReleaseChanges,
        sink: TextIO) -> tuple[str, Optional[Callable[[str], None]]]
```

Return the content change listing and a writer, None when empty.

The native save dialog has already confirmed the overwrite, so the
writer allows overwriting an existing file.

<a id="backlogops_gui.backlog_actions._run_change"></a>

#### \_run\_change

```python
def _run_change(parent: tk.Misc,
                change: Callable[[], tuple[str, Optional[Callable[[str],
                                                                  None]]]],
                refresh: Callable[[], None], on_error: Callable[[str, str],
                                                                None],
                on_info: Callable[[str, str],
                                  None], fail_title: str, title: str) -> None
```

Run a change returning a report, refresh, then show the pop-up.

A change that raises one of the known data errors is reported and
leaves the view unchanged. A successful change refreshes the view and
shows the change listing in a pop-up that can save it to a file.

<a id="backlogops_gui.backlog_actions.estimate_date"></a>

#### estimate\_date

```python
def estimate_date(parent: tk.Misc, data: BacklogReleases,
                  teams: Optional[AvailableTeams], sink: TextIO,
                  refresh: Callable[[], None], on_error: Callable[[str, str],
                                                                  None],
                  on_info: Callable[[str, str], None]) -> None
```

Ask for the start date and estimate the ready dates.

<a id="backlogops_gui.backlog_actions.set_plan"></a>

#### set\_plan

```python
def set_plan(data: BacklogReleases, sink: TextIO, refresh: Callable[[], None],
             on_error: Callable[[str, str], None],
             on_info: Callable[[str, str], None]) -> None
```

Copy the estimated ready dates to the planned ready dates.

<a id="backlogops_gui.backlog_actions.adjust_content"></a>

#### adjust\_content

```python
def adjust_content(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                   refresh: Callable[[], None], on_error: Callable[[str, str],
                                                                   None],
                   on_info: Callable[[str, str], None]) -> None
```

Ask for a buffer and adjust the release content to the estimate.

<a id="backlogops_gui.backlog_actions.plan_dates"></a>

#### plan\_dates

```python
def plan_dates(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
               refresh: Callable[[], None], on_error: Callable[[str, str],
                                                               None],
               on_info: Callable[[str, str], None]) -> None
```

Ask for a buffer and set planned release dates from the estimate.

<a id="backlogops_gui.backlog_actions.order_dates"></a>

#### order\_dates

```python
def order_dates(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                refresh: Callable[[], None], on_error: Callable[[str, str],
                                                                None],
                on_info: Callable[[str, str], None]) -> None
```

Ask for the date kind and order the releases by that date.

<a id="backlogops_gui.backlog_actions.extract_keys"></a>

#### extract\_keys

```python
def extract_keys(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None
```

Ask for levels and a file, then write the backlog keys to it.

<a id="backlogops_gui.backlog_actions.apply_add_result"></a>

#### apply\_add\_result

```python
def apply_add_result(data: BacklogReleases, result: AddedToJira,
                     refresh: Callable[[], None],
                     show_report: Callable[[str], None]) -> None
```

Rekey the shown backlog, refresh the view and show the two lists.

The added items take their new Jira keys (order preserved), the view
is rebuilt, and the added and already-present lists are shown to the
user through ``show_report``.

<a id="backlogops_gui.backlog_actions.apply_update_result"></a>

#### apply\_update\_result

```python
def apply_update_result(data: BacklogReleases, result: UpdatedBacklogInJira,
                        refresh: Callable[[], None],
                        show_report: Callable[[str], None]) -> None
```

Rekey any added items, refresh the view and show the update lists.

Only the items added under the ``ADD`` policy took new Jira keys, so
the shown backlog is rekeyed with the add result's key map, the view is
rebuilt, and the update outcome is shown through ``show_report``.

<a id="backlogops_gui.close_binding"></a>

# backlogops\_gui.close\_binding

Bind the close-window key to a secondary window's close action.

On macOS the Tk toolkit does not close a window when the user presses
Cmd-W, so every secondary window binds that key here. Cmd-W is bound on
every platform, where it is harmless without a Command key, and Ctrl-W is
added on Windows, its customary close-window shortcut. The bound action
defaults to destroying the window but may be the window's own cancel or
abort handler, so the key behaves exactly like the window close button.

<a id="backlogops_gui.close_binding._close_events"></a>

#### \_close\_events

```python
def _close_events() -> list[str]
```

Return the key patterns that close a window on this platform.

<a id="backlogops_gui.close_binding.bind_close"></a>

#### bind\_close

```python
def bind_close(win: tk.Toplevel,
               on_close: Optional[Callable[[], None]] = None) -> None
```

Bind the close-window key to run the window's close action.

**Arguments**:

- `win` - The secondary window to close on the key press.
- `on_close` - The close action, defaulting to destroying the window.
  A window that cancels or aborts on close passes its own
  handler, so the key matches its window close button.

<a id="backlogops_gui.backlog_window"></a>

# backlogops\_gui.backlog\_window

A window that shows one backlog and its releases as two tables.

The window shows the backlog and the releases as two read-only tables and
carries a menu with the actions that can be done to the backlog. The
backlog table fills the window, while the releases table, which has only a
few columns, is kept narrow so its columns are not spread out. The menu
offers reordering, ready-date estimation, release planning, key
extraction, the Jira operations, saving to a file and closing the window.
The operations themselves live in :mod:`backlogops_gui.backlog_actions`,
so they can be tested without a display.

<a id="backlogops_gui.backlog_window.BacklogWindow"></a>

## BacklogWindow Objects

```python
class BacklogWindow()
```

A top-level window showing one backlog and its releases.

<a id="backlogops_gui.backlog_window.BacklogWindow.__init__"></a>

#### \_\_init\_\_

```python
def __init__(
    root: tk.Misc,
    data: BacklogReleases,
    title: str,
    presets: Callable[[], Optional[dict[str, OutputFormatConfig]]],
    teams: Callable[[], Optional[AvailableTeams]],
    sink: TextIO,
    levels: Callable[[], Optional[Levels]] = lambda: None,
    gui_display: Callable[[], GuiDisplayConfig] = GuiDisplayConfig,
    warning: Optional[str] = None,
    add_to_jira: Optional[Callable[
        [BacklogReleases, Callable[[AddedToJira], None]], None]] = None,
    add_releases: Optional[
        Callable[[BacklogReleases, Callable[[AddedReleasesToJira], None]],
                 None]] = None,
    update_releases: Optional[
        Callable[[BacklogReleases, Callable[[UpdatedReleasesInJira], None]],
                 None]] = None,
    update_backlog: Optional[
        Callable[[BacklogReleases, Callable[[UpdatedBacklogInJira], None]],
                 None]] = None
) -> None
```

Build the window, its menu and the two tables.

**Arguments**:

- `root` - The parent window the new window belongs to.
- `data` - The backlog and releases to show.
- `title` - The window title, typically the source file name.
- `presets` - Callable returning the current output presets.
- `teams` - Callable returning the loaded teams configuration.
- `sink` - Stream that receives low-level write diagnostics.
- `levels` - Callable returning the configured levels, or None for
  the default levels.
- `gui_display` - Callable returning the GUI display configuration,
  which decides the level display and the per-table column
  renaming for the tables.
- `warning` - Warning text to show over the tables. When present,
  backlog operations are disabled and only saving remains.
- `add_to_jira` - Handler that adds the shown backlog to Jira and
  calls back with the result, or None when adding is
  unavailable (no configuration or no write presets).
- `add_releases` - Handler that adds the shown releases to Jira and
  calls back with the result, or None when adding is
  unavailable (no configuration or no write presets).
- `update_releases` - Handler that updates the shown releases in Jira
  and calls back with the result, or None when updating is
  unavailable (no configuration or no write presets).
- `update_backlog` - Handler that updates the shown backlog in Jira
  and calls back with the result, or None when updating is
  unavailable (no configuration or no write presets).

<a id="backlogops_gui.backlog_window.BacklogWindow._report_error"></a>

#### \_report\_error

```python
def _report_error(title: str, message: str) -> None
```

Show an error message over this backlog window.

<a id="backlogops_gui.backlog_window.BacklogWindow._report_info"></a>

#### \_report\_info

```python
def _report_info(title: str, message: str) -> None
```

Show an informational message over this backlog window.

<a id="backlogops_gui.backlog_window.BacklogWindow._build_tables"></a>

#### \_build\_tables

```python
def _build_tables() -> None
```

Build the backlog and releases tables from the current data.

<a id="backlogops_gui.backlog_window.BacklogWindow._refresh_tables"></a>

#### \_refresh\_tables

```python
def _refresh_tables() -> None
```

Rebuild the tables after the backlog data has changed.

<a id="backlogops_gui.backlog_window.BacklogWindow._add_warning"></a>

#### \_add\_warning

```python
def _add_warning() -> None
```

Show a highly visible warning over restricted backlog data.

<a id="backlogops_gui.backlog_window.BacklogWindow._add_menu"></a>

#### \_add\_menu

```python
def _add_menu() -> None
```

Add the backlog menu with the action, save and close items.

<a id="backlogops_gui.backlog_window.BacklogWindow._add_actions"></a>

#### \_add\_actions

```python
def _add_actions(menu: tk.Menu) -> None
```

Add the backlog operation items to the menu.

<a id="backlogops_gui.backlog_window.BacklogWindow._add_jira_actions"></a>

#### \_add\_jira\_actions

```python
def _add_jira_actions(menu: tk.Menu) -> None
```

Add the Jira operation items to the menu.

<a id="backlogops_gui.backlog_window.BacklogWindow._add_table"></a>

#### \_add\_table

```python
def _add_table(heading: str, columns: list[str], rows: list[list[ValueFmt]],
               narrow: bool) -> tk.Widget
```

Add one labeled, scrollable table and return its frame.

The narrow table keeps its few columns at a fixed width and does
not take the spare space, so it stays clearly narrower than the
backlog table that fills the window.

<a id="backlogops_gui.backlog_window.BacklogWindow._make_tree"></a>

#### \_make\_tree

```python
@staticmethod
def _make_tree(frame: tk.Misc, columns: list[str], rows: list[list[ValueFmt]],
               narrow: bool) -> ttk.Treeview
```

Build the Treeview, keeping a narrow table from stretching.

<a id="backlogops_gui.backlog_window.BacklogWindow._save"></a>

#### \_save

```python
def _save() -> None
```

Save the backlog through the shared save helper.

<a id="backlogops_gui.backlog_window.BacklogWindow._order_by_keys"></a>

#### \_order\_by\_keys

```python
def _order_by_keys() -> None
```

Order the backlog by leading keys and refresh the tables.

<a id="backlogops_gui.backlog_window.BacklogWindow._order_by_deps"></a>

#### \_order\_by\_deps

```python
def _order_by_deps() -> None
```

Order the backlog by dependencies and refresh the tables.

<a id="backlogops_gui.backlog_window.BacklogWindow._order_by_release"></a>

#### \_order\_by\_release

```python
def _order_by_release() -> None
```

Order the backlog by release order and refresh the tables.

<a id="backlogops_gui.backlog_window.BacklogWindow._estimate_date"></a>

#### \_estimate\_date

```python
def _estimate_date() -> None
```

Estimate the ready dates and refresh the tables.

<a id="backlogops_gui.backlog_window.BacklogWindow._set_plan"></a>

#### \_set\_plan

```python
def _set_plan() -> None
```

Copy the estimated dates to the planned dates and refresh.

<a id="backlogops_gui.backlog_window.BacklogWindow._adjust_content"></a>

#### \_adjust\_content

```python
def _adjust_content() -> None
```

Adjust the release content to the estimate and refresh.

<a id="backlogops_gui.backlog_window.BacklogWindow._plan_dates"></a>

#### \_plan\_dates

```python
def _plan_dates() -> None
```

Set planned release dates from the estimate and refresh.

<a id="backlogops_gui.backlog_window.BacklogWindow._order_dates"></a>

#### \_order\_dates

```python
def _order_dates() -> None
```

Order the releases by date and refresh the tables.

<a id="backlogops_gui.backlog_window.BacklogWindow._extract_keys"></a>

#### \_extract\_keys

```python
def _extract_keys() -> None
```

Extract backlog keys at chosen levels to a key list file.

<a id="backlogops_gui.backlog_window.BacklogWindow._jira_add"></a>

#### \_jira\_add

```python
def _jira_add() -> None
```

Add the shown backlog to Jira, adjusting the view on success.

<a id="backlogops_gui.backlog_window.BacklogWindow._on_jira_added"></a>

#### \_on\_jira\_added

```python
def _on_jira_added(result: AddedToJira) -> None
```

Rekey the shown backlog and show the two result lists.

<a id="backlogops_gui.backlog_window.BacklogWindow._show_add_report"></a>

#### \_show\_add\_report

```python
def _show_add_report(text: str) -> None
```

Show the add result text in a copy-pasteable pop-up.

<a id="backlogops_gui.backlog_window.BacklogWindow._releases_add"></a>

#### \_releases\_add

```python
def _releases_add() -> None
```

Add the shown releases to Jira and show the result lists.

<a id="backlogops_gui.backlog_window.BacklogWindow._on_releases_added"></a>

#### \_on\_releases\_added

```python
def _on_releases_added(result: AddedReleasesToJira) -> None
```

Show the added, present and failed release lists.

A release name never changes, so the shown releases already match
what was added and no rebuild of the tables is needed.

<a id="backlogops_gui.backlog_window.BacklogWindow._releases_update"></a>

#### \_releases\_update

```python
def _releases_update() -> None
```

Update the shown releases in Jira and show the result lists.

<a id="backlogops_gui.backlog_window.BacklogWindow._on_releases_updated"></a>

#### \_on\_releases\_updated

```python
def _on_releases_updated(result: UpdatedReleasesInJira) -> None
```

Show the update outcome per release in a pop-up.

The lists are the updated, already-correct, ignored, added and
failed releases. An update changes only the Jira versions, not the
shown releases, so no rebuild of the tables is needed.

<a id="backlogops_gui.backlog_window.BacklogWindow._backlog_update"></a>

#### \_backlog\_update

```python
def _backlog_update() -> None
```

Update the shown backlog in Jira and show the result lists.

<a id="backlogops_gui.backlog_window.BacklogWindow._on_backlog_updated"></a>

#### \_on\_backlog\_updated

```python
def _on_backlog_updated(result: UpdatedBacklogInJira) -> None
```

Rekey any added items, refresh the view and show the outcome.

Only items added under the ``ADD`` policy took new Jira keys, so the
shown backlog is rekeyed for them, the tables are rebuilt, and the
update outcome is shown in a copy-pasteable pop-up.

<a id="backlogops_gui.backlog_window.BacklogWindow._show_update_report"></a>

#### \_show\_update\_report

```python
def _show_update_report(text: str) -> None
```

Show the backlog update result text in a copy-pasteable pop-up.

<a id="backlogops_gui.blog_version_reporter"></a>

# backlogops\_gui.blog\_version\_reporter

Version reporter for the backlogops_gui package.

<a id="backlogops_gui.blog_version_reporter.BloGuiVersionReporter"></a>

## BloGuiVersionReporter Objects

```python
class BloGuiVersionReporter(BloVersionReporter)
```

Version reporter for the backlogops_gui package.

<a id="backlogops_gui.blog_version_reporter.BloGuiVersionReporter.package_names"></a>

#### package\_names

```python
@override
def package_names() -> list[str]
```

Return the package names that this package reports.

<a id="backlogops_gui.blog_version_reporter.BloGuiVersionReporter.get_main_package_name"></a>

#### get\_main\_package\_name

```python
@override
@classmethod
def get_main_package_name(cls) -> str
```

Return the name of the main package.

<a id="backlogops_gui.wizard_table"></a>

# backlogops\_gui.wizard\_table

An editable grid of cells for one wizard table question.

A table question shown by the wizard is rendered as a grid of cells. A
fixed table fills its seed rows only; a variable table, asked with both a
minimum and a maximum row count, offers add-row and remove-row buttons and
shows its grid in a scrolling area. :class:`TableEditor` builds the grid,
reads the final cell strings back, and runs the optional per-cell partial
check for early feedback.

<a id="backlogops_gui.wizard_table._uniform"></a>

#### \_uniform

```python
def _uniform(values: list[_V], default: _V) -> _V
```

Return the value shared by every entry, or the default.

<a id="backlogops_gui.wizard_table._new_row_template"></a>

#### \_new\_row\_template

```python
def _new_row_template(columns: Sequence[TableColumn],
                      rows: Sequence[Sequence[TableCell]]) -> list[TableCell]
```

Return the cell descriptors used for rows added at run time.

For each column the new cell keeps the value, choices and nullable
flag shared by every seed cell of that column, and falls back to an
empty string, no choices and not-nullable when they differ. A cell in
an added row is always editable, even in a read-only column.

<a id="backlogops_gui.wizard_table.Cell"></a>

## Cell Objects

```python
@dataclass(frozen=True)
class Cell()
```

One built table cell: its widget and how its value is read.

A read-only cell keeps the fixed text it shows in its label. An
editable cell keeps the widget the user types in or selects from, and
whether an empty cell is reported as ``None``.

<a id="backlogops_gui.wizard_table._cell_text"></a>

#### \_cell\_text

```python
def _cell_text(cell: Cell) -> Optional[str]
```

Return the final string a cell holds, or None for an empty cell.

<a id="backlogops_gui.wizard_table.TableEditor"></a>

## TableEditor Objects

```python
class TableEditor()
```

An editable grid of cells for one table question.

A fixed table fills the seed rows only. A variable table, asked with
both a minimum and a maximum row count, adds editable rows up to the
maximum and removes the last row down to the minimum. A variable
table shows its grid in a scrolling area, so a long table stays
usable while the wizard window is resized.

<a id="backlogops_gui.wizard_table.TableEditor.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc,
             columns: Sequence[TableColumn],
             rows: Sequence[Sequence[TableCell]],
             partial_check: Optional[PartialCheck],
             min_rows: Optional[int] = None,
             max_rows: Optional[int] = None) -> None
```

Build the header and one widget per cell of the seed rows.

<a id="backlogops_gui.wizard_table.TableEditor.is_variable"></a>

#### is\_variable

```python
def is_variable() -> bool
```

Return whether the table can add and remove rows.

<a id="backlogops_gui.wizard_table.TableEditor.values"></a>

#### values

```python
def values() -> list[list[Optional[str]]]
```

Return the whole table as rows of final cell strings.

<a id="backlogops_gui.wizard_table.TableEditor.add_row"></a>

#### add\_row

```python
def add_row() -> None
```

Append one editable row, up to the maximum row count.

<a id="backlogops_gui.wizard_table.TableEditor.remove_row"></a>

#### remove\_row

```python
def remove_row() -> None
```

Remove the last row, down to the minimum row count.

<a id="backlogops_gui.wizard_table.TableEditor._build_grid_area"></a>

#### \_build\_grid\_area

```python
def _build_grid_area(parent: tk.Misc) -> tk.Frame
```

Return the frame holding the grid, scrolling when variable.

<a id="backlogops_gui.wizard_table.TableEditor._build_scroll"></a>

#### \_build\_scroll

```python
def _build_scroll(parent: tk.Misc) -> tk.Frame
```

Build an expanding scrolling area and return its inner frame.

<a id="backlogops_gui.wizard_table.TableEditor._scroll_to_end"></a>

#### \_scroll\_to\_end

```python
def _scroll_to_end() -> None
```

Bring the newly added last row into the scrolling area.

<a id="backlogops_gui.wizard_table.TableEditor._build_header"></a>

#### \_build\_header

```python
def _build_header() -> None
```

Show one bold heading label per column.

<a id="backlogops_gui.wizard_table.TableEditor._append_cells"></a>

#### \_append\_cells

```python
def _append_cells(row: Sequence[TableCell], added: bool) -> None
```

Build and store one widget per column of one new table row.

<a id="backlogops_gui.wizard_table.TableEditor._build_cell"></a>

#### \_build\_cell

```python
def _build_cell(index: int, col: int, pair: tuple[TableColumn, TableCell],
                added: bool) -> Cell
```

Build one read-only label or one editable cell widget.

<a id="backlogops_gui.wizard_table.TableEditor._editable_widget"></a>

#### \_editable\_widget

```python
def _editable_widget(cell: TableCell) -> tk.Widget
```

Return a drop-down for a cell with choices, else a text entry.

<a id="backlogops_gui.wizard_table.TableEditor._bind_change"></a>

#### \_bind\_change

```python
def _bind_change(widget: tk.Widget, row: int, col: int) -> None
```

Show early per-cell feedback when an edited cell changes.

<a id="backlogops_gui.wizard_table.TableEditor._feedback"></a>

#### \_feedback

```python
def _feedback(row: int, col: int) -> None
```

Run the partial check and show its message for one cell.

<a id="backlogops_gui.wizard_table.TableEditor._show"></a>

#### \_show

```python
def _show(message: str) -> None
```

Show a status message below the grid.

<a id="backlogops_gui.modal_dialog"></a>

# backlogops\_gui.modal\_dialog

Base for the small modal option dialogs of the application.

A modal option dialog is a top-level window with an OK and a Cancel
button. :class:`ModalDialog` builds the window and its close handler, adds
the two buttons, focuses the first input and waits for the window to
close. A subclass builds its own inputs and overrides :meth:`_confirm` to
store the entered values before the window closes.

<a id="backlogops_gui.modal_dialog.ModalDialog"></a>

## ModalDialog Objects

```python
class ModalDialog()
```

Base for small modal dialogs with OK and Cancel buttons.

<a id="backlogops_gui.modal_dialog.ModalDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, title: str) -> None
```

Create the modal top-level window and its close handler.

<a id="backlogops_gui.modal_dialog.ModalDialog._show"></a>

#### \_show

```python
def _show() -> None
```

Add buttons, focus the first input and wait for the close.

<a id="backlogops_gui.modal_dialog.ModalDialog._add_buttons"></a>

#### \_add\_buttons

```python
def _add_buttons() -> None
```

Add the confirm and cancel buttons.

<a id="backlogops_gui.modal_dialog.ModalDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Close the dialog; subclasses override to store their values.

<a id="backlogops_gui.modal_dialog.ModalDialog._cancel"></a>

#### \_cancel

```python
def _cancel() -> None
```

Mark the dialog cancelled and close it.

<a id="backlogops_gui.python_version"></a>

# backlogops\_gui.python\_version

Python version support check for the backlog operations GUI.

<a id="backlogops_gui.python_version.check_python_version"></a>

#### check\_python\_version

```python
def check_python_version(
        reporter: Optional[BloVersionReporter] = None) -> Optional[str]
```

Return a warning when the running Python version is unsupported.

The version reporter writes an explanation and upgrade instructions
only when the running Python version is no longer supported by the
application, and writes nothing otherwise. Its output is captured so
it can be shown in the main window instead of on standard output.

**Arguments**:

- `reporter` - The reporter to query, or None to use the GUI reporter.
  

**Returns**:

  The captured warning text, or None when Python is still supported.

<a id="backlogops_gui.log_buffer"></a>

# backlogops\_gui.log\_buffer

A bounded text sink that keeps the most recent log lines.

The graphical application routes the diagnostics that the library would
write to ``stderr`` into a log buffer instead of discarding them, so the
most recent lines can be shown in the main window. The buffer keeps only a
bounded number of the latest lines, so a long-running session cannot
exhaust memory.

<a id="backlogops_gui.log_buffer.LogBuffer"></a>

## LogBuffer Objects

```python
class LogBuffer(io.StringIO)
```

A text sink keeping only the most recent written lines.

<a id="backlogops_gui.log_buffer.LogBuffer.__init__"></a>

#### \_\_init\_\_

```python
def __init__(max_lines: int = DEFAULT_MAX_LINES) -> None
```

Create an empty buffer keeping at most ``max_lines`` lines.

<a id="backlogops_gui.log_buffer.LogBuffer.write"></a>

#### write

```python
@override
def write(s: str) -> int
```

Append text, keeping only the most recent completed lines.

The text is split on newlines; completed lines join the bounded
store and any text after the last newline is kept as the pending
last line. Nothing is stored in the underlying string buffer, so
memory stays bounded regardless of how much is written.

<a id="backlogops_gui.log_buffer.LogBuffer.text"></a>

#### text

```python
def text() -> str
```

Return the kept lines, including any unfinished last line.

<a id="backlogops_gui.jira_write"></a>

# backlogops\_gui.jira\_write

Add a shown backlog and its releases to Jira.

The writer offers a handler for adding the shown backlog and a handler for
adding the shown releases, each available only when a configuration with
Jira presets is loaded. A handler asks for a write preset and whether to
skip items whose key already exists, then adds on a worker thread and
hands the result back to the GUI thread.

<a id="backlogops_gui.jira_write.JiraWriter"></a>

## JiraWriter Objects

```python
class JiraWriter(JiraAction)
```

Adds a shown backlog and its releases to Jira.

<a id="backlogops_gui.jira_write.JiraWriter.backlog_action"></a>

#### backlog\_action

```python
def backlog_action() -> Optional[Callable[
    [BacklogReleases, Callable[[AddedToJira], None]], None]]
```

Return the add-backlog handler, or None when it is unavailable.

<a id="backlogops_gui.jira_write.JiraWriter.releases_action"></a>

#### releases\_action

```python
def releases_action() -> Optional[Callable[
    [BacklogReleases, Callable[[AddedReleasesToJira], None]], None]]
```

Return the add-releases handler, or None when unavailable.

<a id="backlogops_gui.jira_write.JiraWriter._ask"></a>

#### \_ask

```python
def _ask() -> Optional[JiraWriteOptions]
```

Ask for the write preset and skip-existing choice.

<a id="backlogops_gui.jira_write.JiraWriter._add_backlog"></a>

#### \_add\_backlog

```python
def _add_backlog(data: BacklogReleases, on_done: Callable[[AddedToJira],
                                                          None]) -> None
```

Ask for a preset and add the shown backlog to Jira.

<a id="backlogops_gui.jira_write.JiraWriter._backlog_worker"></a>

#### \_backlog\_worker

```python
def _backlog_worker(options: JiraWriteOptions, data: BacklogReleases,
                    on_done: Callable[[AddedToJira], None]) -> None
```

Add the backlog on a worker and schedule the GUI update.

<a id="backlogops_gui.jira_write.JiraWriter._add_releases"></a>

#### \_add\_releases

```python
def _add_releases(data: BacklogReleases,
                  on_done: Callable[[AddedReleasesToJira], None]) -> None
```

Ask for a preset and add the shown releases to Jira.

<a id="backlogops_gui.jira_write.JiraWriter._releases_worker"></a>

#### \_releases\_worker

```python
def _releases_worker(options: JiraWriteOptions, data: BacklogReleases,
                     on_done: Callable[[AddedReleasesToJira], None]) -> None
```

Add the releases on a worker and schedule the GUI update.

<a id="backlogops_gui.backlog_io"></a>

# backlogops\_gui.backlog\_io

Read and write a backlog and releases with format options.

These helpers wrap the library read and write functions and resolve the
format the same way the command line does: an empty value infers the
format from the file name, a value of only letters and digits is a preset
name looked up in the presets from the teams configuration, and any other
value is the path of a stand-alone format configuration file. Diagnostics
go to the given sink, because a graphical application shows them in a log
view rather than on a console.

<a id="backlogops_gui.backlog_io._sink"></a>

#### \_sink

```python
def _sink(sink: Optional[TextIO]) -> TextIO
```

Return the given diagnostics sink, or a discarding one.

<a id="backlogops_gui.backlog_io.read_backlog"></a>

#### read\_backlog

```python
def read_backlog(
        path: str,
        value: Optional[str],
        presets: Optional[dict[str, InputFormatConfig]],
        sink: Optional[TextIO] = None,
        levels: Optional[Levels] = None,
        status_map: Optional[dict[str, Status]] = None) -> BacklogReleases
```

Read and validate a backlog and releases from one file.

**Arguments**:

- `path` - The data file to read.
- `value` - The format selection, as documented for the module.
- `presets` - Named input presets, or None when none are configured.
- `sink` - Stream for diagnostics, or None to discard them.
- `levels` - The backlog item levels to honour, or None for the
  default levels.
- `status_map` - The library-wide status input map, or None when absent.
  The resolved input configuration's own status map overrides it
  per name.
  

**Returns**:

  The validated backlog and releases read from the file.

<a id="backlogops_gui.backlog_io.write_backlog"></a>

#### write\_backlog

```python
def write_backlog(data: BacklogReleases,
                  path: str,
                  value: Optional[str],
                  presets: Optional[dict[str, OutputFormatConfig]],
                  releases_first: bool,
                  sink: Optional[TextIO] = None,
                  levels: Optional[Levels] = None) -> None
```

Write a backlog and releases to one file.

**Arguments**:

- `data` - The backlog and releases to write.
- `path` - The data file to create.
- `value` - The format selection, as documented for the module.
- `presets` - Named output presets, or None when none are configured.
- `releases_first` - Whether to write the releases before the backlog.
- `sink` - Stream for diagnostics, or None to discard them.
- `levels` - The levels used to write level names, or None for the
  default levels.

<a id="backlogops_gui.table_view"></a>

# backlogops\_gui.table\_view

Build tables of a backlog and its releases with cell formatting.

A backlog and its releases are shown as two tables. The table data and the
cell formatting are derived from the same formatting the file writer uses,
so the on-screen colors match a written spreadsheet: the status cell and the
estimated-ready-date cell are highlighted by the format rules, and the other
cells are left plain. The columns are the union of the field names met in the
rows, kept in first-seen order, and every cell is rendered as text so the
table can show any value type. A per-table column-name map can rename a
column or drop it from the display, as the GUI display configuration decides.

<a id="backlogops_gui.table_view._columns"></a>

#### \_columns

```python
def _columns(rows: Sequence[dict[str, ValueFmt]]) -> list[str]
```

Return the column names met in the rows, in first-seen order.

<a id="backlogops_gui.table_view._cell_text"></a>

#### \_cell\_text

```python
def _cell_text(value: Value) -> str
```

Return one cell value rendered as display text.

<a id="backlogops_gui.table_view._table"></a>

#### \_table

```python
def _table(
    rows: Sequence[dict[str,
                        ValueFmt]]) -> tuple[list[str], list[list[ValueFmt]]]
```

Return the columns and column-aligned formatted rows.

Each row becomes one cell per column, in column order, so a cell that a
row does not have becomes a blank, unformatted cell.

<a id="backlogops_gui.table_view.backlog_table"></a>

#### backlog\_table

```python
def backlog_table(
        data: BacklogReleases,
        levels: Optional[Levels] = None,
        display: LevelDisplay = LevelDisplay.BOTH,
        names: Optional[Mapping[str, Optional[str]]] = None,
        sink: Optional[TextIO] = None
) -> tuple[list[str], list[list[ValueFmt]]]
```

Return the columns and formatted rows for the backlog table.

The level of each item is shown as its number, its name, or both, as
``display`` decides, using ``levels`` to translate a number to a name.
The ``names`` map then renames or drops columns, as documented for
:func:`backlogops.apply_column_map`.

<a id="backlogops_gui.table_view.release_table"></a>

#### release\_table

```python
def release_table(
    data: BacklogReleases,
    names: Optional[Mapping[str, Optional[str]]] = None
) -> tuple[list[str], list[list[ValueFmt]]]
```

Return the columns and formatted rows for the releases table.

The ``names`` map renames or drops columns, as documented for
:func:`backlogops.apply_column_map`.

<a id="backlogops_gui.table_view._tag_name"></a>

#### \_tag\_name

```python
def _tag_name(fmt: Fmt) -> str
```

Return a stable tag name identifying one cell format.

<a id="backlogops_gui.table_view._tag_font"></a>

#### \_tag\_font

```python
def _tag_font(tree: ttk.Treeview, fmt: Fmt) -> tuple[str, int, str]
```

Return a font descriptor for the bold and italic of a format.

<a id="backlogops_gui.table_view._ensure_tag"></a>

#### \_ensure\_tag

```python
def _ensure_tag(tree: ttk.Treeview, fmt: Fmt) -> str
```

Configure and return the tag for one non-plain cell format.

<a id="backlogops_gui.table_view._format_cell"></a>

#### \_format\_cell

```python
def _format_cell(tree: ttk.Treeview, item: str, column: str, fmt: Fmt) -> None
```

Color one table cell, leaving plain cells untouched.

<a id="backlogops_gui.table_view.supports_cell_tags"></a>

#### supports\_cell\_tags

```python
def supports_cell_tags(tree: ttk.Treeview) -> bool
```

Return whether this Tk build supports per-cell Treeview tags.

Per-cell tags are a Tk 8.7+ feature. On an older Tk the ``tag cell``
subcommand does not exist, so the probe raises and coloring falls back
to whole-row tags, which Tk has supported for far longer.

<a id="backlogops_gui.table_view._row_format"></a>

#### \_row\_format

```python
def _row_format(row: Sequence[ValueFmt]) -> Fmt
```

Return the first non-plain cell format in a row, else plain.

<a id="backlogops_gui.table_view._color_cells"></a>

#### \_color\_cells

```python
def _color_cells(tree: ttk.Treeview, item: str, columns: Sequence[str],
                 row: Sequence[ValueFmt]) -> None
```

Color each formatted cell of an inserted row separately.

<a id="backlogops_gui.table_view._insert_row"></a>

#### \_insert\_row

```python
def _insert_row(tree: ttk.Treeview, columns: Sequence[str],
                row: Sequence[ValueFmt], cell_tags: bool) -> None
```

Insert one row as text and color it per cell or per row.

With per-cell tags every formatted cell keeps its own color. Without
them the whole row takes the format of its first formatted cell, so an
older Tk still highlights the row instead of failing to build the table.

<a id="backlogops_gui.table_view.make_table"></a>

#### make\_table

```python
def make_table(parent: tk.Misc,
               columns: Sequence[str],
               rows: Sequence[Sequence[ValueFmt]],
               width: int = COLUMN_WIDTH,
               stretch: bool = True) -> ttk.Treeview
```

Create a read-only Treeview showing the given columns and rows.

Each cell is colored by the format rules, so a late estimate or a done
or rejected status appears with the same highlight and font as in a
written spreadsheet. On a Tk too old for per-cell tags the whole row is
colored instead, so the table still builds and shows the highlight. When
``stretch`` is True the columns share the table width; when False each
column keeps ``width`` pixels, so a table with few columns stays narrow
instead of spreading across the whole width.

<a id="backlogops_gui.wizard_window"></a>

# backlogops\_gui.wizard\_window

One reused window that asks every wizard prompt in turn.

The wizard bridge answers all of its questions in a single
:class:`WizardWindow`, so the whole wizard session happens in one pop-up
that does not jump around the display. The window offers a text entry, a
yes/no button pair, a single- and a multi-selection list, and an editable
table, and keeps a lasting message area above the changing content. Every
prompt also offers back, out-one-level and abort buttons, which raise the
matching :class:`WizardNavigation` request so the wizard can step within
the configuration or abandon it.

<a id="backlogops_gui.wizard_window.WizardWindow"></a>

## WizardWindow Objects

```python
class WizardWindow()
```

One reused window that asks every wizard prompt in turn.

<a id="backlogops_gui.wizard_window.WizardWindow.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Create the fixed-size window and its lasting message area.

<a id="backlogops_gui.wizard_window.WizardWindow._build_messages"></a>

#### \_build\_messages

```python
def _build_messages() -> tk.Text
```

Build the read-only area that keeps the wizard messages.

<a id="backlogops_gui.wizard_window.WizardWindow.show"></a>

#### show

```python
def show(message: str) -> None
```

Append one lasting message to the message area.

<a id="backlogops_gui.wizard_window.WizardWindow.close"></a>

#### close

```python
def close() -> None
```

Destroy the wizard window.

<a id="backlogops_gui.wizard_window.WizardWindow.ask_text"></a>

#### ask\_text

```python
def ask_text(question: str,
             re_ask: Optional[str],
             nullable: bool,
             default: Optional[str] = None,
             sensitive: bool = False) -> Optional[str]
```

Ask one free-text question and return the entered text.

A sensitive question masks the typed text; a default value is
pre-filled and returned when the answer is left empty.

<a id="backlogops_gui.wizard_window.WizardWindow._text_result"></a>

#### \_text\_result

```python
@staticmethod
def _text_result(result: str, nullable: bool,
                 default: Optional[str]) -> Optional[str]
```

Return the answer after the default and nullable rules.

<a id="backlogops_gui.wizard_window.WizardWindow.ask_yes_no"></a>

#### ask\_yes\_no

```python
def ask_yes_no(question: str, default: bool, re_ask: Optional[str]) -> bool
```

Ask one yes/no question with dedicated buttons.

<a id="backlogops_gui.wizard_window.WizardWindow.ask_choice"></a>

#### ask\_choice

```python
def ask_choice(question: str, choices: Sequence[str], default: Optional[str],
               re_ask: Optional[str]) -> str
```

Ask the user to pick exactly one choice and return it.

<a id="backlogops_gui.wizard_window.WizardWindow.ask_multi"></a>

#### ask\_multi

```python
def ask_multi(question: str, choices: Sequence[str],
              default: Optional[Sequence[str]], min_select: int,
              max_select: Optional[int], re_ask: Optional[str]) -> list[str]
```

Ask the user to pick several choices within the count bounds.

<a id="backlogops_gui.wizard_window.WizardWindow.ask_table"></a>

#### ask\_table

```python
def ask_table(columns: Sequence[TableColumn],
              cells: Sequence[Sequence[TableCell]], question: str,
              re_ask: Optional[str], partial_check: Optional[PartialCheck],
              min_rows: Optional[int],
              max_rows: Optional[int]) -> list[list[Optional[str]]]
```

Ask the user to fill the given table rows and return them.

<a id="backlogops_gui.wizard_window.WizardWindow._run_multi"></a>

#### \_run\_multi

```python
def _run_multi(question: str, re_ask: Optional[str], choices: Sequence[str],
               default: Optional[Sequence[str]]) -> list[str]
```

Show a multi-selection list once and return the picked values.

<a id="backlogops_gui.wizard_window.WizardWindow._choice_list"></a>

#### \_choice\_list

```python
def _choice_list(choices: Sequence[str], marked: Optional[str | Sequence[str]],
                 mode: str) -> tk.Listbox
```

Build a selection list, preselecting the marked choices.

<a id="backlogops_gui.wizard_window.WizardWindow._preset_indexes"></a>

#### \_preset\_indexes

```python
@staticmethod
def _preset_indexes(choices: Sequence[str],
                    marked: Optional[str | Sequence[str]]) -> list[int]
```

Return the indexes to preselect from a default value or list.

<a id="backlogops_gui.wizard_window.WizardWindow._pick_one"></a>

#### \_pick\_one

```python
def _pick_one(listbox: tk.Listbox, choices: Sequence[str]) -> None
```

Finish a single-choice question with the selected value.

<a id="backlogops_gui.wizard_window.WizardWindow._pick_many"></a>

#### \_pick\_many

```python
def _pick_many(listbox: tk.Listbox, choices: Sequence[str]) -> None
```

Finish a multi-choice question with the selected values.

<a id="backlogops_gui.wizard_window.WizardWindow._begin"></a>

#### \_begin

```python
def _begin(question: str, re_ask: Optional[str]) -> None
```

Clear the content area and show the question and any reason.

<a id="backlogops_gui.wizard_window.WizardWindow._add_label"></a>

#### \_add\_label

```python
def _add_label(text: str, color: str) -> None
```

Add one wrapped label to the content area.

<a id="backlogops_gui.wizard_window.WizardWindow._add_buttons"></a>

#### \_add\_buttons

```python
def _add_buttons(on_ok: Callable[[], None]) -> None
```

Add the confirm and navigation buttons.

<a id="backlogops_gui.wizard_window.WizardWindow._add_table_buttons"></a>

#### \_add\_table\_buttons

```python
def _add_table_buttons(editor: TableEditor) -> None
```

Add confirm, optional add/remove-row and navigation buttons.

<a id="backlogops_gui.wizard_window.WizardWindow._add_nav_buttons"></a>

#### \_add\_nav\_buttons

```python
def _add_nav_buttons(box: tk.Frame) -> None
```

Add the back, out-one-level and abort navigation buttons.

<a id="backlogops_gui.wizard_window.WizardWindow._wait"></a>

#### \_wait

```python
def _wait() -> object
```

Focus the first input, then wait for an answer or navigation.

<a id="backlogops_gui.wizard_window.WizardWindow._finish"></a>

#### \_finish

```python
def _finish(value: object) -> None
```

Store the answer and release the waiting prompt.

<a id="backlogops_gui.wizard_window.WizardWindow._back"></a>

#### \_back

```python
def _back() -> None
```

Request a step back to the previous question.

<a id="backlogops_gui.wizard_window.WizardWindow._cancel_level"></a>

#### \_cancel\_level

```python
def _cancel_level() -> None
```

Request leaving the current level by one step.

<a id="backlogops_gui.wizard_window.WizardWindow._cancel"></a>

#### \_cancel

```python
def _cancel() -> None
```

Request abandoning the whole configuration.

<a id="backlogops_gui.wizard_window.WizardWindow._navigate"></a>

#### \_navigate

```python
def _navigate(request: type[WizardNavigation]) -> None
```

Record a navigation request and release the waiting prompt.

<a id="backlogops_gui.jira_actions"></a>

# backlogops\_gui.jira\_actions

The Jira read, write and update collaborators of the application.

The Jira menu actions of a backlog window are split across three
collaborators so each stays focused as the Jira support grows.
:class:`JiraActions` groups them behind one attribute of the application,
so the application talks to ``self.jira.reader``, ``self.jira.writer`` and
``self.jira.updater``.

<a id="backlogops_gui.jira_actions.JiraActions"></a>

## JiraActions Objects

```python
class JiraActions()
```

Groups the Jira read, write and update collaborators.

<a id="backlogops_gui.jira_actions.JiraActions.__init__"></a>

#### \_\_init\_\_

```python
def __init__(app: 'BacklogApp') -> None
```

Create the reader, writer and updater for the application.

<a id="backlogops_gui.file_choosers"></a>

# backlogops\_gui.file\_choosers

Native file choosers for the backlog operations application.

Each helper opens a native open- or save-file dialog for one purpose and
returns the chosen path, or None when the user cancels. Keeping the
choosers in one module lets the tests drive them by patching a single
``filedialog`` reference.

<a id="backlogops_gui.file_choosers.choose_input_file"></a>

#### choose\_input\_file

```python
def choose_input_file(parent: tk.Misc) -> Optional[str]
```

Ask for an existing backlog file, or None when cancelled.

<a id="backlogops_gui.file_choosers.choose_output_file"></a>

#### choose\_output\_file

```python
def choose_output_file(parent: tk.Misc) -> Optional[str]
```

Ask for a backlog file to create, or None when cancelled.

<a id="backlogops_gui.file_choosers.choose_config_file"></a>

#### choose\_config\_file

```python
def choose_config_file(parent: tk.Misc) -> Optional[str]
```

Ask for a configuration file to create, or None when cancelled.

<a id="backlogops_gui.file_choosers.choose_existing_config"></a>

#### choose\_existing\_config

```python
def choose_existing_config(parent: tk.Misc) -> Optional[str]
```

Ask for an existing configuration file, or None when cancelled.

<a id="backlogops_gui.file_choosers.choose_preset_to_migrate"></a>

#### choose\_preset\_to\_migrate

```python
def choose_preset_to_migrate(parent: tk.Misc) -> Optional[str]
```

Ask for an existing preset file to migrate, or None when cancelled.

<a id="backlogops_gui.file_choosers.choose_migrated_preset"></a>

#### choose\_migrated\_preset

```python
def choose_migrated_preset(parent: tk.Misc) -> Optional[str]
```

Ask for a migrated preset file to create, or None when cancelled.

<a id="backlogops_gui.file_choosers.choose_key_list_output"></a>

#### choose\_key\_list\_output

```python
def choose_key_list_output(parent: tk.Misc) -> Optional[str]
```

Ask for a key list file to create, or None when cancelled.

<a id="backlogops_gui.file_choosers.choose_changes_output"></a>

#### choose\_changes\_output

```python
def choose_changes_output(parent: tk.Misc) -> Optional[str]
```

Ask for a changes file to create, or None when cancelled.

