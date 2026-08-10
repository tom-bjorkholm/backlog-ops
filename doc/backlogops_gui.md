# Table of Contents

* [backlogops\_gui.jira\_rename](#backlogops_gui.jira_rename)
  * [JiraRenamer](#backlogops_gui.jira_rename.JiraRenamer)
    * [rename\_action](#backlogops_gui.jira_rename.JiraRenamer.rename_action)
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
* [backlogops\_gui.token\_dialog](#backlogops_gui.token_dialog)
  * [EncryptTokenRequest](#backlogops_gui.token_dialog.EncryptTokenRequest)
  * [EncryptTokenDialog](#backlogops_gui.token_dialog.EncryptTokenDialog)
    * [\_\_init\_\_](#backlogops_gui.token_dialog.EncryptTokenDialog.__init__)
  * [ask\_encrypt\_token](#backlogops_gui.token_dialog.ask_encrypt_token)
* [backlogops\_gui.choice\_dialogs](#backlogops_gui.choice_dialogs)
  * [ConfigChoice](#backlogops_gui.choice_dialogs.ConfigChoice)
  * [PresetKind](#backlogops_gui.choice_dialogs.PresetKind)
  * [SourceChoice](#backlogops_gui.choice_dialogs.SourceChoice)
  * [EditTargetChoice](#backlogops_gui.choice_dialogs.EditTargetChoice)
  * [ButtonChoiceDialog](#backlogops_gui.choice_dialogs.ButtonChoiceDialog)
    * [\_\_init\_\_](#backlogops_gui.choice_dialogs.ButtonChoiceDialog.__init__)
  * [ask\_no\_config\_choice](#backlogops_gui.choice_dialogs.ask_no_config_choice)
  * [ask\_preset\_kind](#backlogops_gui.choice_dialogs.ask_preset_kind)
  * [ask\_source\_choice](#backlogops_gui.choice_dialogs.ask_source_choice)
  * [ask\_edit\_target](#backlogops_gui.choice_dialogs.ask_edit_target)
* [backlogops\_gui.format\_dialogs](#backlogops_gui.format_dialogs)
  * [format\_value](#backlogops_gui.format_dialogs.format_value)
  * [ReadOptions](#backlogops_gui.format_dialogs.ReadOptions)
  * [WriteOptions](#backlogops_gui.format_dialogs.WriteOptions)
  * [FormatDialog](#backlogops_gui.format_dialogs.FormatDialog)
    * [\_\_init\_\_](#backlogops_gui.format_dialogs.FormatDialog.__init__)
  * [ask\_read\_options](#backlogops_gui.format_dialogs.ask_read_options)
  * [ask\_write\_options](#backlogops_gui.format_dialogs.ask_write_options)
* [backlogops\_gui.jira\_dialogs](#backlogops_gui.jira_dialogs)
  * [MISSING\_MODE\_TEXT](#backlogops_gui.jira_dialogs.MISSING_MODE_TEXT)
  * [LINK\_MODE\_TEXT](#backlogops_gui.jira_dialogs.LINK_MODE_TEXT)
  * [RANK\_ANCHOR\_TEXT](#backlogops_gui.jira_dialogs.RANK_ANCHOR_TEXT)
  * [ORDER\_MODE\_TEXT](#backlogops_gui.jira_dialogs.ORDER_MODE_TEXT)
  * [JiraPresetOptions](#backlogops_gui.jira_dialogs.JiraPresetOptions)
  * [JiraReadOptions](#backlogops_gui.jira_dialogs.JiraReadOptions)
  * [JiraWriteOptions](#backlogops_gui.jira_dialogs.JiraWriteOptions)
  * [JiraReleaseWriteOptions](#backlogops_gui.jira_dialogs.JiraReleaseWriteOptions)
  * [JiraReleaseUpdateOptions](#backlogops_gui.jira_dialogs.JiraReleaseUpdateOptions)
  * [JiraBacklogUpdateOptions](#backlogops_gui.jira_dialogs.JiraBacklogUpdateOptions)
  * [JiraRankOptions](#backlogops_gui.jira_dialogs.JiraRankOptions)
  * [JiraRenameOptions](#backlogops_gui.jira_dialogs.JiraRenameOptions)
  * [JiraOrderOptions](#backlogops_gui.jira_dialogs.JiraOrderOptions)
  * [JiraReadDialog](#backlogops_gui.jira_dialogs.JiraReadDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraReadDialog.__init__)
  * [ask\_jira\_read\_options](#backlogops_gui.jira_dialogs.ask_jira_read_options)
  * [JiraWriteDialog](#backlogops_gui.jira_dialogs.JiraWriteDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraWriteDialog.__init__)
  * [ask\_jira\_write\_options](#backlogops_gui.jira_dialogs.ask_jira_write_options)
  * [JiraReleaseWriteDialog](#backlogops_gui.jira_dialogs.JiraReleaseWriteDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraReleaseWriteDialog.__init__)
  * [ask\_release\_write](#backlogops_gui.jira_dialogs.ask_release_write)
  * [JiraReleaseUpdateDialog](#backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraReleaseUpdateDialog.__init__)
  * [ask\_release\_update](#backlogops_gui.jira_dialogs.ask_release_update)
  * [JiraBacklogUpdateDialog](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraBacklogUpdateDialog.__init__)
  * [ask\_backlog\_update](#backlogops_gui.jira_dialogs.ask_backlog_update)
  * [JiraRankDialog](#backlogops_gui.jira_dialogs.JiraRankDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraRankDialog.__init__)
  * [ask\_jira\_rank](#backlogops_gui.jira_dialogs.ask_jira_rank)
  * [JiraRenameDialog](#backlogops_gui.jira_dialogs.JiraRenameDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraRenameDialog.__init__)
  * [ask\_jira\_rename](#backlogops_gui.jira_dialogs.ask_jira_rename)
  * [JiraOrderDialog](#backlogops_gui.jira_dialogs.JiraOrderDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.JiraOrderDialog.__init__)
  * [ask\_jira\_order](#backlogops_gui.jira_dialogs.ask_jira_order)
  * [PassphraseDialog](#backlogops_gui.jira_dialogs.PassphraseDialog)
    * [\_\_init\_\_](#backlogops_gui.jira_dialogs.PassphraseDialog.__init__)
  * [ask\_jira\_passphrase](#backlogops_gui.jira_dialogs.ask_jira_passphrase)
* [backlogops\_gui.jira\_base](#backlogops_gui.jira_base)
  * [JiraAction](#backlogops_gui.jira_base.JiraAction)
    * [\_\_init\_\_](#backlogops_gui.jira_base.JiraAction.__init__)
* [backlogops\_gui.application](#backlogops_gui.application)
  * [initial\_config](#backlogops_gui.application.initial_config)
  * [BacklogApp](#backlogops_gui.application.BacklogApp)
    * [\_\_init\_\_](#backlogops_gui.application.BacklogApp.__init__)
    * [adopt\_config](#backlogops_gui.application.BacklogApp.adopt_config)
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
    * [run\_config\_editor](#backlogops_gui.application.BacklogApp.run_config_editor)
    * [run\_preset\_editor](#backlogops_gui.application.BacklogApp.run_preset_editor)
    * [create\_preset\_file](#backlogops_gui.application.BacklogApp.create_preset_file)
    * [migrate\_preset\_file](#backlogops_gui.application.BacklogApp.migrate_preset_file)
    * [write\_config](#backlogops_gui.application.BacklogApp.write_config)
    * [encrypt\_token](#backlogops_gui.application.BacklogApp.encrypt_token)
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
* [backlogops\_gui.key\_list\_box](#backlogops_gui.key_list_box)
  * [build\_key\_box](#backlogops_gui.key_list_box.build_key_box)
  * [load\_keys\_into](#backlogops_gui.key_list_box.load_keys_into)
* [backlogops\_gui.backlog\_window](#backlogops_gui.backlog_window)
  * [current\_time](#backlogops_gui.backlog_window.current_time)
  * [BacklogSource](#backlogops_gui.backlog_window.BacklogSource)
  * [JiraHandlers](#backlogops_gui.backlog_window.JiraHandlers)
  * [BacklogWindow](#backlogops_gui.backlog_window.BacklogWindow)
    * [\_\_init\_\_](#backlogops_gui.backlog_window.BacklogWindow.__init__)
* [backlogops\_gui.blog\_version\_reporter](#backlogops_gui.blog_version_reporter)
  * [BloGuiVersionReporter](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter)
    * [package\_names](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter.package_names)
    * [get\_main\_package\_name](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter.get_main_package_name)
* [backlogops\_gui.modal\_dialog](#backlogops_gui.modal_dialog)
  * [ModalDialog](#backlogops_gui.modal_dialog.ModalDialog)
    * [\_\_init\_\_](#backlogops_gui.modal_dialog.ModalDialog.__init__)
* [backlogops\_gui.jira\_order](#backlogops_gui.jira_order)
  * [JiraOrderer](#backlogops_gui.jira_order.JiraOrderer)
    * [order\_action](#backlogops_gui.jira_order.JiraOrderer.order_action)
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
* [backlogops\_gui.jira\_actions](#backlogops_gui.jira_actions)
  * [JiraActions](#backlogops_gui.jira_actions.JiraActions)
    * [\_\_init\_\_](#backlogops_gui.jira_actions.JiraActions.__init__)
* [backlogops\_gui.config\_edit](#backlogops_gui.config_edit)
  * [EDIT\_ERRORS](#backlogops_gui.config_edit.EDIT_ERRORS)
  * [EditorWindow](#backlogops_gui.config_edit.EditorWindow)
  * [editor\_window](#backlogops_gui.config_edit.editor_window)
  * [open\_editor\_window](#backlogops_gui.config_edit.open_editor_window)
  * [edit\_config](#backlogops_gui.config_edit.edit_config)
  * [edit\_preset\_file](#backlogops_gui.config_edit.edit_preset_file)
* [backlogops\_gui.file\_choosers](#backlogops_gui.file_choosers)
  * [choose\_input\_file](#backlogops_gui.file_choosers.choose_input_file)
  * [choose\_output\_file](#backlogops_gui.file_choosers.choose_output_file)
  * [choose\_config\_file](#backlogops_gui.file_choosers.choose_config_file)
  * [choose\_existing\_config](#backlogops_gui.file_choosers.choose_existing_config)
  * [choose\_existing\_preset](#backlogops_gui.file_choosers.choose_existing_preset)
  * [choose\_config\_to\_edit](#backlogops_gui.file_choosers.choose_config_to_edit)
  * [choose\_preset\_to\_edit](#backlogops_gui.file_choosers.choose_preset_to_edit)
  * [choose\_preset\_to\_migrate](#backlogops_gui.file_choosers.choose_preset_to_migrate)
  * [choose\_migrated\_preset](#backlogops_gui.file_choosers.choose_migrated_preset)
  * [choose\_key\_list\_output](#backlogops_gui.file_choosers.choose_key_list_output)
  * [choose\_changes\_output](#backlogops_gui.file_choosers.choose_changes_output)

<a id="backlogops_gui.jira_rename"></a>

# backlogops\_gui.jira\_rename

Rename the shown releases in Jira.

The renamer offers a handler that asks for a preset and a new name per shown
release, then renames the matching Jira versions on a worker thread and hands
the result back to the GUI thread. It is available only when a configuration
with Jira presets is loaded. The shown release names are the old names; a
blank entry keeps a release unchanged.

<a id="backlogops_gui.jira_rename.JiraRenamer"></a>

## JiraRenamer Objects

```python
class JiraRenamer(JiraAction)
```

Renames the shown releases in Jira.

<a id="backlogops_gui.jira_rename.JiraRenamer.rename_action"></a>

#### rename\_action

```python
def rename_action() -> Optional[Callable[
    [BacklogReleases, Callable[[RenamedReleasesInJira], None]], None]]
```

Return the rename-releases handler, or None when unavailable.

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

<a id="backlogops_gui.token_dialog"></a>

# backlogops\_gui.token\_dialog

Modal dialog collecting what is needed to encrypt a Jira token file.

The dialog gathers the clear text Jira API token, either typed directly or
read from a clear text file, the encrypted file to write, and a pass phrase
entered twice so the two entries can be confirmed to match. The typed token
wins when both a token and a clear text file are given. The token field is
shown in the clear so a pasted token can be checked, while the two pass
phrase fields are masked. The gathered values are returned as an
:class:`EncryptTokenRequest`, or None when the user cancels; performing the
encryption is left to the caller.

<a id="backlogops_gui.token_dialog.EncryptTokenRequest"></a>

## EncryptTokenRequest Objects

```python
@dataclass
class EncryptTokenRequest()
```

The token source, output file and pass phrase to encrypt with.

Exactly one of ``token`` and ``clear_file`` is set: ``token`` holds a
token typed into the dialog, ``clear_file`` a clear text token file to
read the token from instead.

<a id="backlogops_gui.token_dialog.EncryptTokenDialog"></a>

## EncryptTokenDialog Objects

```python
class EncryptTokenDialog(ModalDialog)
```

Modal dialog collecting the token, output file and pass phrase.

<a id="backlogops_gui.token_dialog.EncryptTokenDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the encrypt-token dialog.

<a id="backlogops_gui.token_dialog.ask_encrypt_token"></a>

#### ask\_encrypt\_token

```python
def ask_encrypt_token(parent: tk.Misc) -> Optional[EncryptTokenRequest]
```

Ask for the token, output file and pass phrase; None if cancelled.

<a id="backlogops_gui.choice_dialogs"></a>

# backlogops\_gui.choice\_dialogs

Modal button-choice dialogs shown outside a backlog window.

These dialogs present a short explanation and a column of buttons, each
selecting one enumerated value, with no OK or Cancel. The no-configuration
dialog offers to run the wizard, load a file, or exit at startup. The
preset-kind dialog asks whether a stand-alone preset file is an input or
an output preset before it is migrated. The source dialog asks whether to
start a wizard from scratch, base it on an existing file, or cancel. The
edit-target dialog asks whether the configuration editor opens the
configuration the application is using or one in a file. All four are built
from the same :class:`ButtonChoiceDialog`.

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

<a id="backlogops_gui.choice_dialogs.SourceChoice"></a>

## SourceChoice Objects

```python
class SourceChoice(Enum)
```

Whether a wizard starts empty, from a file, or is cancelled.

<a id="backlogops_gui.choice_dialogs.EditTargetChoice"></a>

## EditTargetChoice Objects

```python
class EditTargetChoice(Enum)
```

Whether the editor opens the configuration in use or one in a file.

<a id="backlogops_gui.choice_dialogs.ButtonChoiceDialog"></a>

## ButtonChoiceDialog Objects

```python
class ButtonChoiceDialog(Generic[_Choice])
```

Modal dialog presenting a column of single-choice buttons.

Each option is one button that records its value and closes the
dialog. Closing the window without pressing a button keeps the given
default value, so a caller can tell a real choice from a dismissal.

<a id="backlogops_gui.choice_dialogs.ButtonChoiceDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, title: str, text: str,
             options: Sequence[tuple[str, _Choice]], default: _Choice) -> None
```

Build, show and wait for the button-choice dialog.

<a id="backlogops_gui.choice_dialogs.ask_no_config_choice"></a>

#### ask\_no\_config\_choice

```python
def ask_no_config_choice(parent: tk.Misc) -> ConfigChoice
```

Ask whether to run the wizard, load a file, or exit.

<a id="backlogops_gui.choice_dialogs.ask_preset_kind"></a>

#### ask\_preset\_kind

```python
def ask_preset_kind(parent: tk.Misc) -> Optional[PresetKind]
```

Ask whether a preset file is an input or output preset.

Returns the chosen kind, or None when the dialog is closed without a
choice.

<a id="backlogops_gui.choice_dialogs.ask_source_choice"></a>

#### ask\_source\_choice

```python
def ask_source_choice(parent: tk.Misc, title: str, text: str) -> SourceChoice
```

Ask whether to start from scratch, base on a file, or cancel.

<a id="backlogops_gui.choice_dialogs.ask_edit_target"></a>

#### ask\_edit\_target

```python
def ask_edit_target(parent: tk.Misc) -> EditTargetChoice
```

Ask whether to edit the configuration in use or one in a file.

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
exists, and optionally a rank anchor. Adding releases picks a write preset
and whether to skip releases whose name already exists. Updating releases
picks a preset, what to do with a missing release name, and which releases
to update.
Updating the backlog picks a preset, what to do with a missing item key,
which columns to update, how parent and dependency links are reconciled,
and optionally a rank anchor. Ranking items picks a preset, filter, keys,
an anchor and whether to honour relations. A separate dialog collects the
masked pass phrase for an encrypted Jira API token.

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

<a id="backlogops_gui.jira_dialogs.ORDER_MODE_TEXT"></a>

#### ORDER\_MODE\_TEXT

Label shown for each order source in the release-order dialog.

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

<a id="backlogops_gui.jira_dialogs.JiraReleaseWriteOptions"></a>

## JiraReleaseWriteOptions Objects

```python
@dataclass
class JiraReleaseWriteOptions(JiraPresetOptions)
```

The Jira write preset and existing-name choice for adding releases.

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

<a id="backlogops_gui.jira_dialogs.JiraRenameOptions"></a>

## JiraRenameOptions Objects

```python
@dataclass
class JiraRenameOptions(JiraPresetOptions)
```

The preset and old-to-new renames chosen for renaming releases.

<a id="backlogops_gui.jira_dialogs.JiraOrderOptions"></a>

## JiraOrderOptions Objects

```python
@dataclass
class JiraOrderOptions(JiraPresetOptions)
```

The preset, order source and typed names chosen for ordering.

``mode`` is one of the keys of :data:`ORDER_MODE_TEXT`; ``names`` holds
the names entered by the user and is only used for the ``names`` mode.

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

<a id="backlogops_gui.jira_dialogs.JiraReleaseWriteDialog"></a>

## JiraReleaseWriteDialog Objects

```python
class JiraReleaseWriteDialog(ModalDialog)
```

Modal dialog for the release write preset and skip choice.

<a id="backlogops_gui.jira_dialogs.JiraReleaseWriteDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, presets: Sequence[str]) -> None
```

Build, show and wait for the add-releases dialog.

<a id="backlogops_gui.jira_dialogs.ask_release_write"></a>

#### ask\_release\_write

```python
def ask_release_write(
        parent: tk.Misc,
        presets: Sequence[str]) -> Optional[JiraReleaseWriteOptions]
```

Ask which release write preset and skip choice, None if cancelled.

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

<a id="backlogops_gui.jira_dialogs.JiraRenameDialog"></a>

## JiraRenameDialog Objects

```python
class JiraRenameDialog(ModalDialog)
```

Modal dialog for the rename preset and a new name per release.

<a id="backlogops_gui.jira_dialogs.JiraRenameDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, presets: Sequence[str],
             release_names: Sequence[str]) -> None
```

Build, show and wait for the rename-releases dialog.

<a id="backlogops_gui.jira_dialogs.ask_jira_rename"></a>

#### ask\_jira\_rename

```python
def ask_jira_rename(
        parent: tk.Misc, presets: Sequence[str],
        release_names: Sequence[str]) -> Optional[JiraRenameOptions]
```

Ask the preset and renames, or None when cancelled.

<a id="backlogops_gui.jira_dialogs.JiraOrderDialog"></a>

## JiraOrderDialog Objects

```python
class JiraOrderDialog(ModalDialog)
```

Modal dialog for the order preset, order source and typed names.

<a id="backlogops_gui.jira_dialogs.JiraOrderDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, presets: Sequence[str]) -> None
```

Build, show and wait for the order-releases dialog.

<a id="backlogops_gui.jira_dialogs.ask_jira_order"></a>

#### ask\_jira\_order

```python
def ask_jira_order(parent: tk.Misc,
                   presets: Sequence[str]) -> Optional[JiraOrderOptions]
```

Ask the preset, order source and names, or None when cancelled.

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

<a id="backlogops_gui.jira_base"></a>

# backlogops\_gui.jira\_base

Shared behavior for the Jira operations of the application.

All the Jira operations resolve a Jira connection and materialize an
encrypted API token before starting, run their network call on a worker
thread, and hand success or failure back to the GUI thread.
:class:`JiraAction` holds a reference to the running
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

The application opens a main window whose menu reads a backlog from a file
or from Jira, loads or replaces the active configuration from a file, runs
the teams configuration wizard, edits a configuration or a stand-alone
preset file in the folding editor of
:mod:`backlogops_gui.config_edit`, creates a stand-alone input or output
preset file, migrates a stand-alone preset file to the current format,
writes the running configuration to a file, and creates a demonstration
backlog. The configuration wizard and the preset wizard first ask whether
to start empty or be pre-filled from an existing file, so the user can
edit an existing configuration instead of entering everything again. Each
backlog opens in its own window, whose information region records where the
data came from and when, marks the window when the backlog has been
modified, and offers a "Read again" button that re-reads the same source.
On macOS the menu bar sits at the top of the display rather than in
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

Store the window, config, log and the action collaborators.

<a id="backlogops_gui.application.BacklogApp.adopt_config"></a>

#### adopt\_config

```python
def adopt_config(config: BacklogOpsConfig, source: str) -> None
```

Make one configuration the active one and say where it came from.

Every way a configuration becomes the active one goes through here —
loading a file, the wizard, and the editor — so the status line
cannot end up saying one thing while another is in use.

**Arguments**:

- `config` - The configuration to use from now on.
- `source` - Where it came from, as a file name or a short phrase.

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
def run_wizard(
        default: Optional[BacklogOpsConfig] = None
) -> Optional[BacklogOpsConfig]
```

Run the config wizard and return its configuration, or None.

<a id="backlogops_gui.application.BacklogApp.run_config_wizard"></a>

#### run\_config\_wizard

```python
def run_config_wizard() -> None
```

Ask the source, run the wizard, and activate a new config.

The wizard may start from scratch or be pre-filled from an
existing configuration file the user chooses. Its result becomes
the active configuration; writing it to a file stays with the
``Write configuration…`` action.

<a id="backlogops_gui.application.BacklogApp.run_config_editor"></a>

#### run\_config\_editor

```python
def run_config_editor() -> None
```

Edit the configuration in use, or one in a file, in the editor.

<a id="backlogops_gui.application.BacklogApp.run_preset_editor"></a>

#### run\_preset\_editor

```python
def run_preset_editor() -> None
```

Edit a stand-alone input or output preset file in the editor.

<a id="backlogops_gui.application.BacklogApp.create_preset_file"></a>

#### create\_preset\_file

```python
def create_preset_file() -> None
```

Ask the source, run the IO preset wizard, and write the preset.

The wizard may start from scratch or be pre-filled from an
existing preset file the user chooses; its direction is detected
from the file.

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

<a id="backlogops_gui.application.BacklogApp.encrypt_token"></a>

#### encrypt\_token

```python
def encrypt_token() -> None
```

Encrypt a Jira API token to a file chosen in a dialog.

The dialog gathers a typed token or a clear text token file, the
encrypted file to write, and the pass phrase entered twice. An
existing output file is only overwritten after confirmation, and
any failure is reported.

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
def open_backlog(
    data: BacklogReleases,
    title: str,
    warning: Optional[str] = None,
    *,
    source: Optional[BacklogSource] = None,
    reload: Optional[Callable[
        [Callable[[BacklogReleases, Optional[str]], None]], None]] = None
) -> None
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
save it without acting on inconsistent data. The window's "Read again"
button re-reads the same preset and filter and updates the window in place.

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
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> Optional[str]
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
  

**Returns**:

  The path written, or None when the save was cancelled or failed.

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

<a id="backlogops_gui.key_list_box"></a>

# backlogops\_gui.key\_list\_box

Shared key-list text box with a load-from-file button for dialogs.

The order-by-keys dialog and the Jira rank dialog both let the user type
or paste a list of keys and load it from a file. This module holds that
shared widget and the file reading so the two dialogs do not repeat it.

<a id="backlogops_gui.key_list_box.build_key_box"></a>

#### build\_key\_box

```python
def build_key_box(win: tk.Misc,
                  label: str,
                  command: Callable[[], None],
                  *,
                  label_pady: tuple[int, int] = (10, 2)) -> tk.Text
```

Add a key-entry label, text box and load-from-file button.

<a id="backlogops_gui.key_list_box.load_keys_into"></a>

#### load\_keys\_into

```python
def load_keys_into(win: tk.Misc, text: tk.Text, sink: TextIO) -> None
```

Read a key list file into the text box, reporting failures.

<a id="backlogops_gui.backlog_window"></a>

# backlogops\_gui.backlog\_window

A window that shows one backlog and its releases as two tables.

The window shows the backlog and the releases as two read-only tables and
carries two menus with the actions that can be done to the backlog. The
backlog table fills the window, while the releases table, which has only a
few columns, is kept narrow so its columns are not spread out. The
``Backlog`` menu offers reordering, ready-date estimation, release
planning, key extraction, saving to a file and closing the window; the
``Jira`` menu offers the Jira operations. The operations themselves live
in :mod:`backlogops_gui.backlog_actions`, so they can be tested without a
display.

<a id="backlogops_gui.backlog_window.current_time"></a>

#### current\_time

```python
def current_time() -> datetime
```

Return the current local time, wrapped so tests can control it.

<a id="backlogops_gui.backlog_window.BacklogSource"></a>

## BacklogSource Objects

```python
@dataclass
class BacklogSource()
```

Where a backlog window's data came from and when it was read.

A window's backlog is read from a file, from Jira, or is the built-in
demonstration backlog. ``read_time`` is the time of the most recent
read and is refreshed when the backlog is read again. Fields that do
not apply to the ``kind`` stay None: ``file_name`` and the optional
input ``preset_name`` describe a file source, while ``preset_name``
and ``issue_filter`` describe a Jira source.

<a id="backlogops_gui.backlog_window.JiraHandlers"></a>

## JiraHandlers Objects

```python
@dataclass
class JiraHandlers()
```

The optional Jira menu handlers a backlog window offers.

Each handler runs one Jira operation and calls back with its result, or
is None when that operation is unavailable (no configuration or no Jira
presets), which disables its menu item. Passing the handlers as one
group keeps the window constructor small.

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
    jira: Optional[JiraHandlers] = None,
    *,
    source: Optional[BacklogSource] = None,
    reload: Optional[Callable[
        [Callable[[BacklogReleases, Optional[str]], None]], None]] = None
) -> None
```

Build the window, its menu, its info region and the two tables.

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
- `jira` - The Jira menu handlers to offer, or None for none. Each
  handler is None when its operation is unavailable, which
  disables its menu item.
- `source` - Where the data came from and when it was read. When
  given, an information region is shown at the top of the
  window; when None no information region is shown.
- `reload` - Callback that re-reads the same source and delivers the
  fresh data and any warning to the given apply callback. When
  given, a "Read again" button is offered; None disables it.

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

<a id="backlogops_gui.jira_order"></a>

# backlogops\_gui.jira\_order

Order the releases in Jira.

The orderer offers a handler that asks for a preset and an order source, then
reorders the Jira versions on a worker thread and hands the result back to the
GUI thread. It is available only when a configuration with Jira presets is
loaded. The order source is the release date, the order of the releases shown
in the window, or a list of names entered in the dialog.

<a id="backlogops_gui.jira_order.JiraOrderer"></a>

## JiraOrderer Objects

```python
class JiraOrderer(JiraAction)
```

Orders the releases in Jira by date, window order or a name list.

<a id="backlogops_gui.jira_order.JiraOrderer.order_action"></a>

#### order\_action

```python
def order_action() -> Optional[Callable[
    [BacklogReleases, Callable[[OrderedReleasesInJira], None]], None]]
```

Return the order-releases handler, or None when unavailable.

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
skip items whose key already exists (releases are skipped by name), then
adds on a worker thread and hands the result back to the GUI thread.

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
        *,
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

<a id="backlogops_gui.jira_actions"></a>

# backlogops\_gui.jira\_actions

The Jira operation collaborators of the application.

The Jira menu actions of a backlog window are split across focused
collaborators so each stays focused as the Jira support grows.
:class:`JiraActions` groups them behind one attribute of the application,
so the application talks to ``self.jira.reader``, ``self.jira.writer``,
``self.jira.updater``, ``self.jira.ranker``, ``self.jira.renamer`` and
``self.jira.orderer``.

<a id="backlogops_gui.jira_actions.JiraActions"></a>

## JiraActions Objects

```python
class JiraActions()
```

Groups the Jira read, write, update, rank, rename and order actions.

<a id="backlogops_gui.jira_actions.JiraActions.__init__"></a>

#### \_\_init\_\_

```python
def __init__(app: 'BacklogApp') -> None
```

Create the Jira collaborators for the app.

<a id="backlogops_gui.config_edit"></a>

# backlogops\_gui.config\_edit

Edit a configuration in a window of the application.

The two edit actions of the configuration menu live here.
:func:`edit_config` opens the configuration the application is using, or one
in a file the user picks; :func:`edit_preset_file` opens a stand-alone input
or output preset file, whose direction is detected from the file itself.
What can be edited, what a save writes, and what each member is for all
belong to :mod:`backlogops.config_editing`, so the editor of the terminal
interface shows exactly the same configuration.

These are functions taking the application rather than a collaborator
object, because an editing session keeps nothing between two of them: the
model belongs to the session and everything else is the application's.

The editor is mounted in a :class:`tkinter.Toplevel` this module creates,
rather than started through ``edit_cfg_json_tk.edit``. That entry point
creates a ``tkinter.Tk`` and an event loop of its own, which is for an
application that runs neither yet: a second Tcl interpreter shares nothing
with the first, and a nested loop would not end when the editor window
closed, because Tcl runs its loop while any window of the process lives.
``EditorWidgets`` is what the library offers for a window an application
owns, and it takes the close action as an argument so that the editor never
destroys a window it did not create.

The window is not made modal. The editor opens dialogs of its own — a file
chooser for Save as…, a question before it overwrites a file, and one asking
for the key of a new entry — and a grab held by the editor window would keep
their clicks and keys from reaching them.

<a id="backlogops_gui.config_edit.EDIT_ERRORS"></a>

#### EDIT\_ERRORS

Errors raised when a configuration cannot be opened for editing.

<a id="backlogops_gui.config_edit.EditorWindow"></a>

## EditorWindow Objects

```python
class EditorWindow(NamedTuple)
```

One editor window and the widgets that have to be kept with it.

The widgets are carried beside the window because a ``StringVar`` unsets
its Tcl variable when it is collected, and the field it belongs to would
then lose both its text and the callback that writes into the model.

<a id="backlogops_gui.config_edit.editor_window"></a>

#### editor\_window

```python
def editor_window(parent: tk.Misc, model: EditModel,
                  title: str) -> EditorWindow
```

Create a window of the application with the editor mounted in it.

Every way out of the editor — its Close button, its key, the close
button of the window and the platform close key — goes through the
editor's own close action, so none of them can drop an unsaved change
without asking. Closing destroys this window and nothing else.

**Arguments**:

- `parent` - Widget the window belongs to, which is the main window.
- `model` - Model of the editing session to show.
- `title` - Title of the window, saying what is being edited.
  

**Returns**:

  The window and the widgets mounted in it.

<a id="backlogops_gui.config_edit.open_editor_window"></a>

#### open\_editor\_window

```python
def open_editor_window(parent: tk.Misc, model: EditModel, title: str) -> None
```

Show one edit model in a window of its own until it is closed.

The window and its widgets are held by the local name for as long as
this call waits for the window, which is as long as they are needed.

**Arguments**:

- `parent` - Widget the window belongs to, which is the main window.
- `model` - Model of the editing session to show.
- `title` - Title of the window, saying what is being edited.

<a id="backlogops_gui.config_edit.edit_config"></a>

#### edit\_config

```python
def edit_config(app: 'BacklogApp') -> None
```

Edit the configuration in use, or one in a file the user picks.

A configuration the editor saved becomes the active configuration,
whichever of the two was edited, because the user has just said that
those are the values they want. Cancelling any step, and closing the
editor without saving, leaves everything as it was.

<a id="backlogops_gui.config_edit.edit_preset_file"></a>

#### edit\_preset\_file

```python
def edit_preset_file(app: 'BacklogApp') -> None
```

Edit a stand-alone input or output preset file.

The direction of the file is detected from its own contents, so the user
picks a preset file and nothing else. What the editor writes is a file
and not a configuration of the application, so nothing is adopted.

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

<a id="backlogops_gui.file_choosers.choose_existing_preset"></a>

#### choose\_existing\_preset

```python
def choose_existing_preset(parent: tk.Misc) -> Optional[str]
```

Ask for an existing preset file to base on, or None when cancelled.

<a id="backlogops_gui.file_choosers.choose_config_to_edit"></a>

#### choose\_config\_to\_edit

```python
def choose_config_to_edit(parent: tk.Misc) -> Optional[str]
```

Ask for an existing configuration file to edit, or None to cancel.

<a id="backlogops_gui.file_choosers.choose_preset_to_edit"></a>

#### choose\_preset\_to\_edit

```python
def choose_preset_to_edit(parent: tk.Misc) -> Optional[str]
```

Ask for an existing preset file to edit, or None when cancelled.

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

