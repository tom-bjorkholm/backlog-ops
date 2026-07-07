# Table of Contents

* [backlogops\_gui.jira\_update](#backlogops_gui.jira_update)
  * [JiraUpdater](#backlogops_gui.jira_update.JiraUpdater)
    * [releases\_action](#backlogops_gui.jira_update.JiraUpdater.releases_action)
    * [backlog\_action](#backlogops_gui.jira_update.JiraUpdater.backlog_action)
* [backlogops\_gui.backlog\_dialogs](#backlogops_gui.backlog_dialogs)
  * [DepOptions](#backlogops_gui.backlog_dialogs.DepOptions)
  * [ReleaseOrderOptions](#backlogops_gui.backlog_dialogs.ReleaseOrderOptions)
  * [StartChoice](#backlogops_gui.backlog_dialogs.StartChoice)
  * [KeysDialog](#backlogops_gui.backlog_dialogs.KeysDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.KeysDialog.__init__)
  * [DepOptionsDialog](#backlogops_gui.backlog_dialogs.DepOptionsDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.DepOptionsDialog.__init__)
  * [StartDateDialog](#backlogops_gui.backlog_dialogs.StartDateDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.StartDateDialog.__init__)
  * [LevelsDialog](#backlogops_gui.backlog_dialogs.LevelsDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.LevelsDialog.__init__)
  * [DateOrderDialog](#backlogops_gui.backlog_dialogs.DateOrderDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.DateOrderDialog.__init__)
  * [ReleaseOrderDialog](#backlogops_gui.backlog_dialogs.ReleaseOrderDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.ReleaseOrderDialog.__init__)
  * [BufferDialog](#backlogops_gui.backlog_dialogs.BufferDialog)
    * [\_\_init\_\_](#backlogops_gui.backlog_dialogs.BufferDialog.__init__)
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
  * [ask\_no\_config\_choice](#backlogops_gui.choice_dialogs.ask_no_config_choice)
  * [PresetKindDialog](#backlogops_gui.choice_dialogs.PresetKindDialog)
    * [\_\_init\_\_](#backlogops_gui.choice_dialogs.PresetKindDialog.__init__)
  * [ask\_preset\_kind](#backlogops_gui.choice_dialogs.ask_preset_kind)
* [backlogops\_gui.format\_dialogs](#backlogops_gui.format_dialogs)
  * [format\_value](#backlogops_gui.format_dialogs.format_value)
  * [ReadOptions](#backlogops_gui.format_dialogs.ReadOptions)
  * [WriteOptions](#backlogops_gui.format_dialogs.WriteOptions)
  * [FormatDialog](#backlogops_gui.format_dialogs.FormatDialog)
    * [\_\_init\_\_](#backlogops_gui.format_dialogs.FormatDialog.__init__)
  * [ask\_read\_options](#backlogops_gui.format_dialogs.ask_read_options)
  * [ask\_write\_options](#backlogops_gui.format_dialogs.ask_write_options)
* [backlogops\_gui.jira\_dialogs](#backlogops_gui.jira_dialogs)
  * [KEY\_READ\_ERRORS](#backlogops_gui.jira_dialogs.KEY_READ_ERRORS)
  * [MISSING\_MODE\_TEXT](#backlogops_gui.jira_dialogs.MISSING_MODE_TEXT)
  * [LINK\_MODE\_TEXT](#backlogops_gui.jira_dialogs.LINK_MODE_TEXT)
  * [RANK\_ANCHOR\_TEXT](#backlogops_gui.jira_dialogs.RANK_ANCHOR_TEXT)
  * [JiraPresetOptions](#backlogops_gui.jira_dialogs.JiraPresetOptions)
  * [JiraReadOptions](#backlogops_gui.jira_dialogs.JiraReadOptions)
  * [JiraWriteOptions](#backlogops_gui.jira_dialogs.JiraWriteOptions)
  * [JiraReleaseUpdateOptions](#backlogops_gui.jira_dialogs.JiraReleaseUpdateOptions)
  * [JiraBacklogUpdateOptions](#backlogops_gui.jira_dialogs.JiraBacklogUpdateOptions)
  * [JiraRankOptions](#backlogops_gui.jira_dialogs.JiraRankOptions)
  * [JiraReadDialog](#backlogops_gui.jira_dialogs.JiraReadDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraReadDialog.__init__)
  * [ask\_jira\_read\_options](#backlogops_gui.jira_dialogs.ask_jira_read_options)
  * [JiraWriteDialog](#backlogops_gui.jira_dialogs.JiraWriteDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraWriteDialog.__init__)
  * [ask\_jira\_write\_options](#backlogops_gui.jira_dialogs.ask_jira_write_options)
  * [JiraReleaseUpdateDialog](#backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog.__init__)
  * [ask\_release\_update](#backlogops_gui.jira_dialogs.ask_release_update)
  * [JiraBacklogUpdateDialog](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog.__init__)
  * [ask\_backlog\_update](#backlogops_gui.jira_dialogs.ask_backlog_update)
  * [JiraRankDialog](#backlogops_gui.jira_dialogs.JiraRankDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraRankDialog.__init__)
  * [ask\_jira\_rank](#backlogops_gui.jira_dialogs.ask_jira_rank)
  * [PassphraseDialog](#backlogops_gui.jira_dialogs.PassphraseDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.PassphraseDialog.__init__)
  * [ask\_jira\_passphrase](#backlogops_gui.jira_dialogs.ask_jira_passphrase)
* [backlogops\_gui.gui\_style](#backlogops_gui.gui_style)
  * [style\_input](#backlogops_gui.gui_style.style_input)
  * [focus\_first\_input](#backlogops_gui.gui_style.focus_first_input)
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
* [backlogops\_gui.jira\_base](#backlogops_gui.jira_base)
  * [JiraAction](#backlogops_gui.jira_base.JiraAction)
    * [\_\_init\_\_](#backlogops_gui.jira_base.JiraAction.__init__)
* [backlogops\_gui.application](#backlogops_gui.application)
  * [initial\_config](#backlogops_gui.application.initial_config)
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
    * [run\_wizard](#backlogops_gui.application.BacklogApp.run_wizard)
    * [run\_config\_wizard](#backlogops_gui.application.BacklogApp.run_config_wizard)
    * [create\_preset\_file](#backlogops_gui.application.BacklogApp.create_preset_file)
    * [migrate\_preset\_file](#backlogops_gui.application.BacklogApp.migrate_preset_file)
    * [write\_config](#backlogops_gui.application.BacklogApp.write_config)
    * [read\_backlog\_file](#backlogops_gui.application.BacklogApp.read_backlog_file)
    * [new\_demo\_backlog](#backlogops_gui.application.BacklogApp.new_demo_backlog)
    * [open\_backlog](#backlogops_gui.application.BacklogApp.open_backlog)
    * [report\_versions](#backlogops_gui.application.BacklogApp.report_versions)
    * [build\_menu](#backlogops_gui.application.BacklogApp.build_menu)
    * [build\_body](#backlogops_gui.application.BacklogApp.build_body)
    * [refresh\_log](#backlogops_gui.application.BacklogApp.refresh_log)
  * [main](#backlogops_gui.application.main)
* [backlogops\_gui.jira\_rank](#backlogops_gui.jira_rank)
  * [JiraRanker](#backlogops_gui.jira_rank.JiraRanker)
    * [rank\_action](#backlogops_gui.jira_rank.JiraRanker.rank_action)
* [backlogops\_gui.tcltk\_version](#backlogops_gui.tcltk_version)
  * [warning\_for\_version](#backlogops_gui.tcltk_version.warning_for_version)
  * [check\_tcltk\_version](#backlogops_gui.tcltk_version.check_tcltk_version)
* [backlogops\_gui.jira\_read](#backlogops_gui.jira_read)
  * [JiraReader](#backlogops_gui.jira_read.JiraReader)
    * [read\_backlog](#backlogops_gui.jira_read.JiraReader.read_backlog)
* [backlogops\_gui.backlog\_actions](#backlogops_gui.backlog_actions)
  * [save\_backlog](#backlogops_gui.backlog_actions.save_backlog)
  * [order\_by\_keys](#backlogops_gui.backlog_actions.order_by_keys)
  * [order\_by\_deps](#backlogops_gui.backlog_actions.order_by_deps)
  * [order\_by\_release](#backlogops_gui.backlog_actions.order_by_release)
  * [save\_changes](#backlogops_gui.backlog_actions.save_changes)
  * [show\_changes](#backlogops_gui.backlog_actions.show_changes)
  * [estimate\_date](#backlogops_gui.backlog_actions.estimate_date)
  * [set\_plan](#backlogops_gui.backlog_actions.set_plan)
  * [adjust\_content](#backlogops_gui.backlog_actions.adjust_content)
  * [plan\_dates](#backlogops_gui.backlog_actions.plan_dates)
  * [order\_dates](#backlogops_gui.backlog_actions.order_dates)
  * [extract\_keys](#backlogops_gui.backlog_actions.extract_keys)
  * [apply\_add\_result](#backlogops_gui.backlog_actions.apply_add_result)
  * [apply\_update\_result](#backlogops_gui.backlog_actions.apply_update_result)
* [backlogops\_gui.close\_binding](#backlogops_gui.close_binding)
  * [bind\_close](#backlogops_gui.close_binding.bind_close)
* [backlogops\_gui.backlog\_window](#backlogops_gui.backlog_window)
  * [BacklogWindow](#backlogops_gui.backlog_window.BacklogWindow)
    * [\_\_init\_\_](#backlogops_gui.backlog_window.BacklogWindow.__init__)
* [backlogops\_gui.blog\_version\_reporter](#backlogops_gui.blog_version_reporter)
  * [BloGuiVersionReporter](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter)
    * [package\_names](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter.package_names)
    * [get\_main\_package\_name](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter.get_main_package_name)
* [backlogops\_gui.wizard\_table](#backlogops_gui.wizard_table)
  * [Cell](#backlogops_gui.wizard_table.Cell)
  * [TableEditor](#backlogops_gui.wizard_table.TableEditor)
    * [\_\_init\_\_](#backlogops_gui.wizard_table.TableEditor.__init__)
    * [is\_variable](#backlogops_gui.wizard_table.TableEditor.is_variable)
    * [values](#backlogops_gui.wizard_table.TableEditor.values)
    * [add\_row](#backlogops_gui.wizard_table.TableEditor.add_row)
    * [remove\_row](#backlogops_gui.wizard_table.TableEditor.remove_row)
* [backlogops\_gui.modal\_dialog](#backlogops_gui.modal_dialog)
  * [ModalDialog](#backlogops_gui.modal_dialog.ModalDialog)
    * [\_\_init\_\_](#backlogops_gui.modal_dialog.ModalDialog.__init__)
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
* [backlogops\_gui.backlog\_io](#backlogops_gui.backlog_io)
  * [read\_backlog](#backlogops_gui.backlog_io.read_backlog)
  * [write\_backlog](#backlogops_gui.backlog_io.write_backlog)
* [backlogops\_gui.table\_view](#backlogops_gui.table_view)
  * [backlog\_table](#backlogops_gui.table_view.backlog_table)
  * [release\_table](#backlogops_gui.table_view.release_table)
  * [supports\_cell\_tags](#backlogops_gui.table_view.supports_cell_tags)
  * [make\_table](#backlogops_gui.table_view.make_table)
* [backlogops\_gui.wizard\_window](#backlogops_gui.wizard_window)
  * [WizardWindow](#backlogops_gui.wizard_window.WizardWindow)
    * [\_\_init\_\_](#backlogops_gui.wizard_window.WizardWindow.__init__)
    * [show](#backlogops_gui.wizard_window.WizardWindow.show)
    * [close](#backlogops_gui.wizard_window.WizardWindow.close)
    * [ask\_text](#backlogops_gui.wizard_window.WizardWindow.ask_text)
    * [ask\_yes\_no](#backlogops_gui.wizard_window.WizardWindow.ask_yes_no)
    * [ask\_choice](#backlogops_gui.wizard_window.WizardWindow.ask_choice)
    * [ask\_multi](#backlogops_gui.wizard_window.WizardWindow.ask_multi)
    * [ask\_table](#backlogops_gui.wizard_window.WizardWindow.ask_table)
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
to Jira picks a write preset, whether to skip items whose key already
exists, and optionally a rank anchor. Updating releases picks a preset,
what to do with a missing release name, and which releases to update.
Updating the backlog picks a preset, what to do with a missing item key,
which columns to update, how parent and dependency links are reconciled,
and optionally a rank anchor. Ranking items picks a preset, filter, keys,
an anchor and whether to honour relations. A separate dialog collects the
masked pass phrase for an encrypted Jira API token.

<a id="backlogops_gui.jira_dialogs.KEY_READ_ERRORS"></a>

#### KEY\_READ\_ERRORS

Errors caught when loading a key list file into the rank dialog.

<a id="backlogops_gui.jira_dialogs.MISSING_MODE_TEXT"></a>

#### MISSING\_MODE\_TEXT

Label shown for each missing-name mode in the release-update dialog.

<a id="backlogops_gui.jira_dialogs.LINK_MODE_TEXT"></a>

#### LINK\_MODE\_TEXT

Label shown for each link-update mode in the backlog-update dialog.

The keys mirror the CLI ``--links`` values; ``reconcile`` maps to
:class:`LinkUpdate.RECONCILE` and ``add`` to :class:`LinkUpdate.ADD_MISSING`.

<a id="backlogops_gui.jira_dialogs.RANK_ANCHOR_TEXT"></a>

#### RANK\_ANCHOR\_TEXT

Label shown for each anchor in the rank dialogs.

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

The Jira write preset, existing-key choice and rank anchor to add.

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

The preset, missing-key mode, fields, links and rank for updating.

<a id="backlogops_gui.jira_dialogs.JiraRankOptions"></a>

## JiraRankOptions Objects

```python
@dataclass
class JiraRankOptions(JiraPresetOptions)
```

The preset, filter, keys, anchor and relations chosen for ranking.

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

<a id="backlogops_gui.jira_dialogs.ask_backlog_update"></a>

#### ask\_backlog\_update

```python
def ask_backlog_update(
    parent: tk.Misc, preset_fields: Mapping[str, Sequence[str]]
) -> Optional[JiraBacklogUpdateOptions]
```

Ask the preset, mode, fields and link policy, None when cancelled.

<a id="backlogops_gui.jira_dialogs.JiraRankDialog"></a>

## JiraRankDialog Objects

```python
class JiraRankDialog(ModalDialog)
```

Modal dialog for the preset, filter, keys, anchor and relations.

<a id="backlogops_gui.jira_dialogs.JiraRankDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, preset_filters: Mapping[str, str],
             sink: TextIO) -> None
```

Build, show and wait for the rank-items dialog.

<a id="backlogops_gui.jira_dialogs.ask_jira_rank"></a>

#### ask\_jira\_rank

```python
def ask_jira_rank(parent: tk.Misc, preset_filters: Mapping[str, str],
                  sink: TextIO) -> Optional[JiraRankOptions]
```

Ask the preset, filter, keys, anchor and relations; None if cancel.

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

<a id="backlogops_gui.gui_style.focus_first_input"></a>

#### focus\_first\_input

```python
def focus_first_input(window: tk.Misc) -> None
```

Give the keyboard focus to the first editable input, if any.

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

<a id="backlogops_gui.application.BacklogApp.run_wizard"></a>

#### run\_wizard

```python
def run_wizard() -> Optional[BacklogOpsConfig]
```

Run the config wizard and return its configuration, or None.

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

<a id="backlogops_gui.application.BacklogApp.write_config"></a>

#### write\_config

```python
def write_config() -> None
```

Write the running configuration to a chosen file.

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

<a id="backlogops_gui.application.BacklogApp.build_menu"></a>

#### build\_menu

```python
def build_menu() -> None
```

Build the menu bar of the main window.

<a id="backlogops_gui.application.BacklogApp.build_body"></a>

#### build\_body

```python
def build_body() -> None
```

Build the main window body and start the log refresh.

<a id="backlogops_gui.application.BacklogApp.refresh_log"></a>

#### refresh\_log

```python
def refresh_log() -> None
```

Copy the latest log lines into the read-only log view.

<a id="backlogops_gui.application.main"></a>

#### main

```python
def main(args: Optional[list[str]] = None) -> None
```

Start the backlog operations GUI.

**Arguments**:

- `args` - Optional replacement for ``sys.argv[1:]``, mainly for tests.

<a id="backlogops_gui.jira_rank"></a>

# backlogops\_gui.jira\_rank

Move issues to the front or end of a Jira backlog by rank.

The ranker offers a handler that asks for a preset, the keys to move and
which end to move them to, then ranks them in Jira on a worker thread and
hands the result back to the GUI thread. It is available only when a
configuration with Jira presets is loaded. The backlog and the current
ranking come from Jira through the preset, not from the shown backlog, so
the handler does not need the shown data.

<a id="backlogops_gui.jira_rank.JiraRanker"></a>

## JiraRanker Objects

```python
class JiraRanker(JiraAction)
```

Moves issues to the front or end of a Jira backlog by rank.

<a id="backlogops_gui.jira_rank.JiraRanker.rank_action"></a>

#### rank\_action

```python
def rank_action(
) -> Optional[Callable[[Callable[[RankedInJira], None]], None]]
```

Return the rank handler, or None when it is unavailable.

<a id="backlogops_gui.tcltk_version"></a>

# backlogops\_gui.tcltk\_version

Tcl/Tk version checks for the backlog operations GUI.

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
                 None]] = None,
    rank_in_jira: Optional[Callable[[Callable[[RankedInJira], None]],
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
- `rank_in_jira` - Handler that asks for keys and an end and moves
  those issues in the Jira rank order, calling back with the
  result, or None when ranking is unavailable (no
  configuration or no Jira presets).

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

<a id="backlogops_gui.table_view.supports_cell_tags"></a>

#### supports\_cell\_tags

```python
def supports_cell_tags(tree: ttk.Treeview) -> bool
```

Return whether this Tk build supports per-cell Treeview tags.

Per-cell tags are a Tk 8.7+ feature. On an older Tk the ``tag cell``
subcommand does not exist, so the probe raises and coloring falls back
to whole-row tags, which Tk has supported for far longer.

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

<a id="backlogops_gui.jira_actions"></a>

# backlogops\_gui.jira\_actions

The Jira read, write and update collaborators of the application.

The Jira menu actions of a backlog window are split across four
collaborators so each stays focused as the Jira support grows.
:class:`JiraActions` groups them behind one attribute of the application,
so the application talks to ``self.jira.reader``, ``self.jira.writer``,
``self.jira.updater`` and ``self.jira.ranker``.

<a id="backlogops_gui.jira_actions.JiraActions"></a>

## JiraActions Objects

```python
class JiraActions()
```

Groups the Jira read, write, update and rank collaborators.

<a id="backlogops_gui.jira_actions.JiraActions.__init__"></a>

#### \_\_init\_\_

```python
def __init__(app: 'BacklogApp') -> None
```

Create the reader, writer, updater and ranker for the app.

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

