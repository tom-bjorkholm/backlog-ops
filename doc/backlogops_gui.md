# Table of Contents

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
  * [main](#backlogops_gui.application.main)
* [backlogops\_gui.tcltk\_version](#backlogops_gui.tcltk_version)
  * [warning\_for\_version](#backlogops_gui.tcltk_version.warning_for_version)
  * [check\_tcltk\_version](#backlogops_gui.tcltk_version.check_tcltk_version)
* [backlogops\_gui.backlog\_window](#backlogops_gui.backlog_window)
  * [save\_backlog](#backlogops_gui.backlog_window.save_backlog)
  * [order\_by\_keys](#backlogops_gui.backlog_window.order_by_keys)
  * [order\_by\_deps](#backlogops_gui.backlog_window.order_by_deps)
  * [order\_by\_release](#backlogops_gui.backlog_window.order_by_release)
  * [save\_changes](#backlogops_gui.backlog_window.save_changes)
  * [show\_changes](#backlogops_gui.backlog_window.show_changes)
  * [estimate\_date](#backlogops_gui.backlog_window.estimate_date)
  * [set\_plan](#backlogops_gui.backlog_window.set_plan)
  * [adjust\_content](#backlogops_gui.backlog_window.adjust_content)
  * [plan\_dates](#backlogops_gui.backlog_window.plan_dates)
  * [order\_dates](#backlogops_gui.backlog_window.order_dates)
  * [extract\_keys](#backlogops_gui.backlog_window.extract_keys)
  * [apply\_add\_result](#backlogops_gui.backlog_window.apply_add_result)
  * [BacklogWindow](#backlogops_gui.backlog_window.BacklogWindow)
    * [\_\_init\_\_](#backlogops_gui.backlog_window.BacklogWindow.__init__)
* [backlogops\_gui.io\_dialogs](#backlogops_gui.io_dialogs)
  * [ConfigChoice](#backlogops_gui.io_dialogs.ConfigChoice)
  * [PresetKind](#backlogops_gui.io_dialogs.PresetKind)
  * [format\_value](#backlogops_gui.io_dialogs.format_value)
  * [ReadOptions](#backlogops_gui.io_dialogs.ReadOptions)
  * [WriteOptions](#backlogops_gui.io_dialogs.WriteOptions)
  * [JiraReadOptions](#backlogops_gui.io_dialogs.JiraReadOptions)
  * [JiraWriteOptions](#backlogops_gui.io_dialogs.JiraWriteOptions)
  * [JiraReleaseUpdateOptions](#backlogops_gui.io_dialogs.JiraReleaseUpdateOptions)
  * [choose\_input\_file](#backlogops_gui.io_dialogs.choose_input_file)
  * [choose\_output\_file](#backlogops_gui.io_dialogs.choose_output_file)
  * [choose\_config\_file](#backlogops_gui.io_dialogs.choose_config_file)
  * [choose\_existing\_config](#backlogops_gui.io_dialogs.choose_existing_config)
  * [choose\_preset\_to\_migrate](#backlogops_gui.io_dialogs.choose_preset_to_migrate)
  * [choose\_migrated\_preset](#backlogops_gui.io_dialogs.choose_migrated_preset)
  * [ask\_no\_config\_choice](#backlogops_gui.io_dialogs.ask_no_config_choice)
  * [ask\_preset\_kind](#backlogops_gui.io_dialogs.ask_preset_kind)
  * [ask\_read\_options](#backlogops_gui.io_dialogs.ask_read_options)
  * [ask\_write\_options](#backlogops_gui.io_dialogs.ask_write_options)
  * [ask\_jira\_read\_options](#backlogops_gui.io_dialogs.ask_jira_read_options)
  * [ask\_jira\_write\_options](#backlogops_gui.io_dialogs.ask_jira_write_options)
  * [MISSING\_MODE\_TEXT](#backlogops_gui.io_dialogs.MISSING_MODE_TEXT)
  * [ask\_release\_update](#backlogops_gui.io_dialogs.ask_release_update)
  * [ask\_jira\_passphrase](#backlogops_gui.io_dialogs.ask_jira_passphrase)
  * [choose\_key\_list\_output](#backlogops_gui.io_dialogs.choose_key_list_output)
  * [choose\_changes\_output](#backlogops_gui.io_dialogs.choose_changes_output)
  * [ask\_buffer\_days](#backlogops_gui.io_dialogs.ask_buffer_days)
  * [show\_change\_list](#backlogops_gui.io_dialogs.show_change_list)
  * [show\_text\_report](#backlogops_gui.io_dialogs.show_text_report)
  * [DepOptions](#backlogops_gui.io_dialogs.DepOptions)
  * [ReleaseOrderOptions](#backlogops_gui.io_dialogs.ReleaseOrderOptions)
  * [StartChoice](#backlogops_gui.io_dialogs.StartChoice)
  * [ask\_keys](#backlogops_gui.io_dialogs.ask_keys)
  * [ask\_dep\_options](#backlogops_gui.io_dialogs.ask_dep_options)
  * [ask\_start\_date](#backlogops_gui.io_dialogs.ask_start_date)
  * [ask\_levels](#backlogops_gui.io_dialogs.ask_levels)
  * [ask\_date\_order](#backlogops_gui.io_dialogs.ask_date_order)
  * [ask\_release\_order](#backlogops_gui.io_dialogs.ask_release_order)
* [backlogops\_gui.blog\_version\_reporter](#backlogops_gui.blog_version_reporter)
  * [BloGuiVersionReporter](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter)
    * [package\_names](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter.package_names)
    * [get\_main\_package\_name](#backlogops_gui.blog_version_reporter.BloGuiVersionReporter.get_main_package_name)
* [backlogops\_gui.python\_version](#backlogops_gui.python_version)
  * [check\_python\_version](#backlogops_gui.python_version.check_python_version)
* [backlogops\_gui.log\_buffer](#backlogops_gui.log_buffer)
  * [LogBuffer](#backlogops_gui.log_buffer.LogBuffer)
    * [\_\_init\_\_](#backlogops_gui.log_buffer.LogBuffer.__init__)
    * [write](#backlogops_gui.log_buffer.LogBuffer.write)
    * [text](#backlogops_gui.log_buffer.LogBuffer.text)
* [backlogops\_gui.backlog\_io](#backlogops_gui.backlog_io)
  * [read\_backlog](#backlogops_gui.backlog_io.read_backlog)
  * [write\_backlog](#backlogops_gui.backlog_io.write_backlog)
* [backlogops\_gui.table\_view](#backlogops_gui.table_view)
  * [backlog\_table](#backlogops_gui.table_view.backlog_table)
  * [release\_table](#backlogops_gui.table_view.release_table)
  * [supports\_cell\_tags](#backlogops_gui.table_view.supports_cell_tags)
  * [make\_table](#backlogops_gui.table_view.make_table)

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
with a real Tkinter control: a text entry, a yes/no button pair, a
single- and a multi-selection list, and an editable table. All questions
are answered in one reused window, so the whole wizard session happens in
a single pop-up that does not jump around the display.
Every prompt also offers back, out-one-level and abort buttons, which
raise the matching :class:`WizardNavigation` request so the wizard can
step within the configuration or abandon it.

A table question may have a fixed set of rows or, when it is asked with
both a minimum and a maximum row count, a variable set of rows. A
variable table offers add-row and remove-row buttons and shows its grid
in a scrolling area, so a long table stays usable in the fixed window.

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

<a id="backlogops_gui.application"></a>

# backlogops\_gui.application

Tkinter application for backlog operations.

The application opens a main window whose menu reads a backlog from a file,
runs the teams configuration wizard, creates a stand-alone input or output
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

Store the main window, configuration, and a log buffer.

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

<a id="backlogops_gui.backlog_window"></a>

# backlogops\_gui.backlog\_window

A window that shows one backlog and its releases as two tables.

The window shows the backlog and the releases as two read-only tables and
carries a menu with the actions that can be done to the backlog. The
backlog table fills the window, while the releases table, which has only a
few columns, is kept narrow so its columns are not spread out. The menu
offers reordering, ready-date estimation, release planning, key
extraction, saving to a file and closing the window. Saving is kept in a
module function so it can be tested without a display.

<a id="backlogops_gui.backlog_window.save_backlog"></a>

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

<a id="backlogops_gui.backlog_window.order_by_keys"></a>

#### order\_by\_keys

```python
def order_by_keys(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                  refresh: Callable[[], None], on_error: Callable[[str, str],
                                                                  None],
                  on_info: Callable[[str, str], None]) -> None
```

Ask for leading keys and move those items to the front.

<a id="backlogops_gui.backlog_window.order_by_deps"></a>

#### order\_by\_deps

```python
def order_by_deps(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                  refresh: Callable[[], None], on_error: Callable[[str, str],
                                                                  None],
                  on_info: Callable[[str, str], None]) -> None
```

Ask for the options and order the backlog by dependencies.

<a id="backlogops_gui.backlog_window.order_by_release"></a>

#### order\_by\_release

```python
def order_by_release(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                     refresh: Callable[[],
                                       None], on_error: Callable[[str, str],
                                                                 None],
                     on_info: Callable[[str, str], None]) -> None
```

Ask for options and order the backlog by release order.

<a id="backlogops_gui.backlog_window.save_changes"></a>

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

<a id="backlogops_gui.backlog_window.show_changes"></a>

#### show\_changes

```python
def show_changes(parent: tk.Misc, title: str, text: str,
                 write_changes: Optional[Callable[[str], None]],
                 on_error: Callable[[str, str],
                                    None], on_info: Callable[[str, str],
                                                             None]) -> None
```

Show the change listing in a pop-up that can save it to a file.

<a id="backlogops_gui.backlog_window.estimate_date"></a>

#### estimate\_date

```python
def estimate_date(parent: tk.Misc, data: BacklogReleases,
                  teams: Optional[AvailableTeams], sink: TextIO,
                  refresh: Callable[[], None], on_error: Callable[[str, str],
                                                                  None],
                  on_info: Callable[[str, str], None]) -> None
```

Ask for the start date and estimate the ready dates.

<a id="backlogops_gui.backlog_window.set_plan"></a>

#### set\_plan

```python
def set_plan(data: BacklogReleases, sink: TextIO, refresh: Callable[[], None],
             on_error: Callable[[str, str], None],
             on_info: Callable[[str, str], None]) -> None
```

Copy the estimated ready dates to the planned ready dates.

<a id="backlogops_gui.backlog_window.adjust_content"></a>

#### adjust\_content

```python
def adjust_content(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                   refresh: Callable[[], None], on_error: Callable[[str, str],
                                                                   None],
                   on_info: Callable[[str, str], None]) -> None
```

Ask for a buffer and adjust the release content to the estimate.

<a id="backlogops_gui.backlog_window.plan_dates"></a>

#### plan\_dates

```python
def plan_dates(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
               refresh: Callable[[], None], on_error: Callable[[str, str],
                                                               None],
               on_info: Callable[[str, str], None]) -> None
```

Ask for a buffer and set planned release dates from the estimate.

<a id="backlogops_gui.backlog_window.order_dates"></a>

#### order\_dates

```python
def order_dates(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                refresh: Callable[[], None], on_error: Callable[[str, str],
                                                                None],
                on_info: Callable[[str, str], None]) -> None
```

Ask for the date kind and order the releases by that date.

<a id="backlogops_gui.backlog_window.extract_keys"></a>

#### extract\_keys

```python
def extract_keys(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None
```

Ask for levels and a file, then write the backlog keys to it.

<a id="backlogops_gui.backlog_window.apply_add_result"></a>

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

<a id="backlogops_gui.io_dialogs"></a>

# backlogops\_gui.io\_dialogs

File choosers and format-option dialogs for backlog files.

The format options mirror the command line: the format is either inferred
from the file name, taken from a named preset stored in the teams
configuration, or read from a stand-alone configuration file. Writing also
offers to put the releases before the backlog. The chosen format is
returned as a single value understood by the resolver in
:mod:`backlogops_gui.backlog_io`.

<a id="backlogops_gui.io_dialogs.ConfigChoice"></a>

## ConfigChoice Objects

```python
class ConfigChoice(Enum)
```

The action chosen in the no-configuration startup dialog.

<a id="backlogops_gui.io_dialogs.PresetKind"></a>

## PresetKind Objects

```python
class PresetKind(Enum)
```

Whether a stand-alone preset file is an input or output preset.

<a id="backlogops_gui.io_dialogs.format_value"></a>

#### format\_value

```python
def format_value(mode: int, preset: str, path: str) -> Optional[str]
```

Return the resolver value for a selected mode and inputs.

A preset or file mode with an empty input falls back to inference, so
an unfinished selection behaves like inferring from the file name.

<a id="backlogops_gui.io_dialogs.ReadOptions"></a>

## ReadOptions Objects

```python
@dataclass
class ReadOptions()
```

The format selection entered for reading a file.

<a id="backlogops_gui.io_dialogs.WriteOptions"></a>

## WriteOptions Objects

```python
@dataclass
class WriteOptions()
```

The format selection and ordering entered for writing a file.

<a id="backlogops_gui.io_dialogs.JiraReadOptions"></a>

## JiraReadOptions Objects

```python
@dataclass
class JiraReadOptions()
```

The Jira preset and issue filter selected for reading from Jira.

<a id="backlogops_gui.io_dialogs.JiraWriteOptions"></a>

## JiraWriteOptions Objects

```python
@dataclass
class JiraWriteOptions()
```

The Jira write preset and existing-key choice for adding to Jira.

<a id="backlogops_gui.io_dialogs.JiraReleaseUpdateOptions"></a>

## JiraReleaseUpdateOptions Objects

```python
@dataclass
class JiraReleaseUpdateOptions()
```

The preset, missing-name mode and selected names for updating.

<a id="backlogops_gui.io_dialogs.choose_input_file"></a>

#### choose\_input\_file

```python
def choose_input_file(parent: tk.Misc) -> Optional[str]
```

Ask for an existing backlog file, or None when cancelled.

<a id="backlogops_gui.io_dialogs.choose_output_file"></a>

#### choose\_output\_file

```python
def choose_output_file(parent: tk.Misc) -> Optional[str]
```

Ask for a backlog file to create, or None when cancelled.

<a id="backlogops_gui.io_dialogs.choose_config_file"></a>

#### choose\_config\_file

```python
def choose_config_file(parent: tk.Misc) -> Optional[str]
```

Ask for a configuration file to create, or None when cancelled.

<a id="backlogops_gui.io_dialogs.choose_existing_config"></a>

#### choose\_existing\_config

```python
def choose_existing_config(parent: tk.Misc) -> Optional[str]
```

Ask for an existing configuration file, or None when cancelled.

<a id="backlogops_gui.io_dialogs.choose_preset_to_migrate"></a>

#### choose\_preset\_to\_migrate

```python
def choose_preset_to_migrate(parent: tk.Misc) -> Optional[str]
```

Ask for an existing preset file to migrate, or None when cancelled.

<a id="backlogops_gui.io_dialogs.choose_migrated_preset"></a>

#### choose\_migrated\_preset

```python
def choose_migrated_preset(parent: tk.Misc) -> Optional[str]
```

Ask for a migrated preset file to create, or None when cancelled.

<a id="backlogops_gui.io_dialogs.ask_no_config_choice"></a>

#### ask\_no\_config\_choice

```python
def ask_no_config_choice(parent: tk.Misc) -> ConfigChoice
```

Ask whether to run the wizard, load a file, or exit.

<a id="backlogops_gui.io_dialogs.ask_preset_kind"></a>

#### ask\_preset\_kind

```python
def ask_preset_kind(parent: tk.Misc) -> Optional[PresetKind]
```

Ask whether a preset file is an input or output preset.

Returns the chosen kind, or None when the dialog is closed without a
choice.

<a id="backlogops_gui.io_dialogs.ask_read_options"></a>

#### ask\_read\_options

```python
def ask_read_options(
        parent: tk.Misc,
        presets: Optional[Sequence[str]]) -> Optional[ReadOptions]
```

Ask how to read a file, or None when the dialog is cancelled.

<a id="backlogops_gui.io_dialogs.ask_write_options"></a>

#### ask\_write\_options

```python
def ask_write_options(
        parent: tk.Misc,
        presets: Optional[Sequence[str]]) -> Optional[WriteOptions]
```

Ask how to write a file, or None when the dialog is cancelled.

<a id="backlogops_gui.io_dialogs.ask_jira_read_options"></a>

#### ask\_jira\_read\_options

```python
def ask_jira_read_options(
        parent: tk.Misc,
        preset_filters: Mapping[str, str]) -> Optional[JiraReadOptions]
```

Ask which Jira preset and filter to read, or None when cancelled.

<a id="backlogops_gui.io_dialogs.ask_jira_write_options"></a>

#### ask\_jira\_write\_options

```python
def ask_jira_write_options(
        parent: tk.Misc, presets: Sequence[str]) -> Optional[JiraWriteOptions]
```

Ask which write preset and skip choice, or None when cancelled.

<a id="backlogops_gui.io_dialogs.MISSING_MODE_TEXT"></a>

#### MISSING\_MODE\_TEXT

Label shown for each missing-name mode in the release-update dialog.

<a id="backlogops_gui.io_dialogs.ask_release_update"></a>

#### ask\_release\_update

```python
def ask_release_update(
        parent: tk.Misc, presets: Sequence[str],
        release_names: Sequence[str]) -> Optional[JiraReleaseUpdateOptions]
```

Ask the preset, missing-name mode and releases, None when cancelled.

<a id="backlogops_gui.io_dialogs.ask_jira_passphrase"></a>

#### ask\_jira\_passphrase

```python
def ask_jira_passphrase(parent: tk.Misc) -> Optional[str]
```

Ask for the Jira token pass phrase, or None when cancelled.

<a id="backlogops_gui.io_dialogs.choose_key_list_output"></a>

#### choose\_key\_list\_output

```python
def choose_key_list_output(parent: tk.Misc) -> Optional[str]
```

Ask for a key list file to create, or None when cancelled.

<a id="backlogops_gui.io_dialogs.choose_changes_output"></a>

#### choose\_changes\_output

```python
def choose_changes_output(parent: tk.Misc) -> Optional[str]
```

Ask for a changes file to create, or None when cancelled.

<a id="backlogops_gui.io_dialogs.ask_buffer_days"></a>

#### ask\_buffer\_days

```python
def ask_buffer_days(parent: tk.Misc) -> Optional[int]
```

Ask for the buffer in days, or None when the dialog is cancelled.

<a id="backlogops_gui.io_dialogs.show_change_list"></a>

#### show\_change\_list

```python
def show_change_list(parent: tk.Misc, title: str, text: str,
                     on_save: Callable[[], None]) -> tk.Toplevel
```

Show a change listing with Save-to-file and Dismiss buttons.

The listing is shown read-only. The Save button calls ``on_save`` and
the Dismiss button closes the window. The created window is returned
so a caller (or a test) can drive or close it.

<a id="backlogops_gui.io_dialogs.show_text_report"></a>

#### show\_text\_report

```python
def show_text_report(parent: tk.Misc, title: str, text: str) -> tk.Toplevel
```

Show read-only, copy-pasteable text with a Dismiss button.

The text is shown in a disabled text box, which still lets the user
select and copy it. The created window is returned so a caller or a
test can drive or close it.

<a id="backlogops_gui.io_dialogs.DepOptions"></a>

## DepOptions Objects

```python
@dataclass
class DepOptions()
```

The options selected for ordering a backlog by dependencies.

<a id="backlogops_gui.io_dialogs.ReleaseOrderOptions"></a>

## ReleaseOrderOptions Objects

```python
@dataclass
class ReleaseOrderOptions()
```

The options selected for ordering a backlog by release order.

<a id="backlogops_gui.io_dialogs.StartChoice"></a>

## StartChoice Objects

```python
@dataclass
class StartChoice()
```

The start date selected for estimating ready dates.

<a id="backlogops_gui.io_dialogs.ask_keys"></a>

#### ask\_keys

```python
def ask_keys(parent: tk.Misc, sink: TextIO) -> Optional[list[str]]
```

Ask for the leading keys, or None when the dialog is cancelled.

<a id="backlogops_gui.io_dialogs.ask_dep_options"></a>

#### ask\_dep\_options

```python
def ask_dep_options(parent: tk.Misc) -> Optional[DepOptions]
```

Ask for the dependency options, or None when cancelled.

<a id="backlogops_gui.io_dialogs.ask_start_date"></a>

#### ask\_start\_date

```python
def ask_start_date(parent: tk.Misc) -> Optional[StartChoice]
```

Ask for the start date, or None when the dialog is cancelled.

<a id="backlogops_gui.io_dialogs.ask_levels"></a>

#### ask\_levels

```python
def ask_levels(parent: tk.Misc) -> Optional[list[int]]
```

Ask for the levels to extract, or None when cancelled.

<a id="backlogops_gui.io_dialogs.ask_date_order"></a>

#### ask\_date\_order

```python
def ask_date_order(parent: tk.Misc) -> Optional[bool]
```

Ask whether to order by estimated date, or None when cancelled.

<a id="backlogops_gui.io_dialogs.ask_release_order"></a>

#### ask\_release\_order

```python
def ask_release_order(parent: tk.Misc) -> Optional[ReleaseOrderOptions]
```

Ask for the release-order options, or None when cancelled.

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

