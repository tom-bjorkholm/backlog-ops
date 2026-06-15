# Table of Contents

* [backlogops\_gui.gui\_wizard](#backlogops_gui.gui_wizard)
  * [TkWizardBridge](#backlogops_gui.gui_wizard.TkWizardBridge)
    * [\_\_init\_\_](#backlogops_gui.gui_wizard.TkWizardBridge.__init__)
    * [ask](#backlogops_gui.gui_wizard.TkWizardBridge.ask)
    * [ask\_yes\_no](#backlogops_gui.gui_wizard.TkWizardBridge.ask_yes_no)
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
    * [show\_error](#backlogops_gui.application.BacklogApp.show_error)
    * [show\_info](#backlogops_gui.application.BacklogApp.show_info)
    * [start](#backlogops_gui.application.BacklogApp.start)
    * [run\_wizard](#backlogops_gui.application.BacklogApp.run_wizard)
    * [run\_teams\_wizard](#backlogops_gui.application.BacklogApp.run_teams_wizard)
    * [write\_config](#backlogops_gui.application.BacklogApp.write_config)
    * [read\_backlog\_file](#backlogops_gui.application.BacklogApp.read_backlog_file)
    * [new\_demo\_backlog](#backlogops_gui.application.BacklogApp.new_demo_backlog)
    * [open\_backlog](#backlogops_gui.application.BacklogApp.open_backlog)
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
  * [estimate\_date](#backlogops_gui.backlog_window.estimate_date)
  * [set\_plan](#backlogops_gui.backlog_window.set_plan)
  * [extract\_keys](#backlogops_gui.backlog_window.extract_keys)
  * [BacklogWindow](#backlogops_gui.backlog_window.BacklogWindow)
    * [\_\_init\_\_](#backlogops_gui.backlog_window.BacklogWindow.__init__)
* [backlogops\_gui.io\_dialogs](#backlogops_gui.io_dialogs)
  * [format\_value](#backlogops_gui.io_dialogs.format_value)
  * [ReadOptions](#backlogops_gui.io_dialogs.ReadOptions)
  * [WriteOptions](#backlogops_gui.io_dialogs.WriteOptions)
  * [choose\_input\_file](#backlogops_gui.io_dialogs.choose_input_file)
  * [choose\_output\_file](#backlogops_gui.io_dialogs.choose_output_file)
  * [choose\_config\_file](#backlogops_gui.io_dialogs.choose_config_file)
  * [ask\_read\_options](#backlogops_gui.io_dialogs.ask_read_options)
  * [ask\_write\_options](#backlogops_gui.io_dialogs.ask_write_options)
  * [choose\_key\_list\_output](#backlogops_gui.io_dialogs.choose_key_list_output)
  * [DepOptions](#backlogops_gui.io_dialogs.DepOptions)
  * [StartChoice](#backlogops_gui.io_dialogs.StartChoice)
  * [ask\_keys](#backlogops_gui.io_dialogs.ask_keys)
  * [ask\_dep\_options](#backlogops_gui.io_dialogs.ask_dep_options)
  * [ask\_start\_date](#backlogops_gui.io_dialogs.ask_start_date)
  * [ask\_levels](#backlogops_gui.io_dialogs.ask_levels)
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
  * [make\_table](#backlogops_gui.table_view.make_table)

<a id="backlogops_gui.gui_wizard"></a>

# backlogops\_gui.gui\_wizard

Graphical bridge that drives the synchronous teams wizard.

The teams configuration wizard asks its questions through a
:class:`WizardUiBridge`, extended here as a :class:`YesNoUiBridge` so
yes/no questions can offer dedicated buttons. This module answers every
call by updating one reused, fixed-size window, so the whole wizard session
happens in a single pop-up that does not jump around the display. A
cancelled prompt raises :class:`EOFError`, which the wizard documents as
the way an interrupted input is reported.

<a id="backlogops_gui.gui_wizard.TkWizardBridge"></a>

## TkWizardBridge Objects

```python
class TkWizardBridge(YesNoUiBridge)
```

Bridge that answers wizard prompts in one reused Tkinter window.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc,
             log: Optional[TextIO] = None,
             ask_fn: Optional[
                 Callable[[str, Optional[str], Optional[Sequence[str]]],
                          str | int]] = None,
             show_fn: Optional[Callable[[str], None]] = None,
             yes_no_fn: Optional[Callable[[str, bool], bool]] = None) -> None
```

Store the parent window, log sink, and optional test callables.

**Arguments**:

- `parent` - The window the wizard window is shown over.
- `log` - Stream that receives low-level wizard diagnostics.
- `ask_fn` - Replacement for the question prompt, used by tests.
- `show_fn` - Replacement for the message display, used by tests.
- `yes_no_fn` - Replacement for the yes/no prompt, used by tests.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.ask"></a>

#### ask

```python
def ask(question: str,
        re_ask_reason: Optional[str] = None,
        choices: Optional[Sequence[str]] = None) -> str | int
```

Ask one question and return the user's answer.

Returns the entered text, the zero-based index of a selected
choice, or an empty string when the user requests the default.

**Raises**:

- `EOFError` - The user cancelled the wizard.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.ask_yes_no"></a>

#### ask\_yes\_no

```python
def ask_yes_no(question: str, default: bool) -> bool
```

Ask one yes/no question with dedicated buttons.

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
runs the teams configuration wizard, writes the running configuration to a
file, and creates a demonstration backlog. Each backlog opens in its own
window. On macOS the menu bar sits at the top of the display rather than in
the window, so the main window body shows a short description, the current
configuration status, and a log of the most recent diagnostic messages, to
make clear that the application is running. The teams configuration is
taken from the file given with ``-c`` or from the configured locations;
when no configuration is found the wizard runs at startup, and cancelling
it ends the application.

<a id="backlogops_gui.application.initial_config"></a>

#### initial\_config

```python
def initial_config(
    config_arg: Optional[str],
    sink: Optional[TextIO] = None
) -> tuple[Optional[AvailableTeamsConfig], Optional[str]]
```

Return the startup configuration and an optional error message.

The configuration is looked up as documented for
:func:`backlogops.get_available_teams`. A failure is mapped to a None
configuration and the error text, so the caller can decide whether to
show the error and whether to run the wizard.

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
def __init__(root: tk.Tk,
             config: Optional[AvailableTeamsConfig] = None) -> None
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

Return the loaded teams configuration, or None when absent.

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

Load the startup configuration, running the wizard if needed.

A configuration named with ``-c`` that cannot be read is reported
before the wizard runs. When no configuration is loaded and the
wizard is cancelled, the application is not ready to run.

**Arguments**:

- `config_arg` - The file from ``-c``, or None to search defaults.
  

**Returns**:

  Whether the application is ready to enter its main loop.

<a id="backlogops_gui.application.BacklogApp.run_wizard"></a>

#### run\_wizard

```python
def run_wizard() -> Optional[AvailableTeamsConfig]
```

Run the teams wizard and return its configuration, or None.

<a id="backlogops_gui.application.BacklogApp.run_teams_wizard"></a>

#### run\_teams\_wizard

```python
def run_teams_wizard() -> None
```

Run the wizard and make a new configuration active on success.

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
def open_backlog(data: BacklogReleases, title: str) -> None
```

Open one backlog and its releases in a new window.

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
few columns, is kept narrow so its columns are not spread out. The first
version offers saving to a file and closing the window. Saving is kept in a
module function so it can be tested without a display.

<a id="backlogops_gui.backlog_window.save_backlog"></a>

#### save\_backlog

```python
def save_backlog(parent: tk.Misc, data: BacklogReleases,
                 presets: Optional[dict[str, OutputFormatConfig]],
                 sink: TextIO, on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None
```

Ask where and how to save a backlog and write it.

**Arguments**:

- `parent` - The window the dialogs are shown over.
- `data` - The backlog and releases to write.
- `presets` - Named output presets, or None when none are configured.
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

<a id="backlogops_gui.backlog_window.extract_keys"></a>

#### extract\_keys

```python
def extract_keys(parent: tk.Misc, data: BacklogReleases, sink: TextIO,
                 on_error: Callable[[str, str], None],
                 on_info: Callable[[str, str], None]) -> None
```

Ask for levels and a file, then write the backlog keys to it.

<a id="backlogops_gui.backlog_window.BacklogWindow"></a>

## BacklogWindow Objects

```python
class BacklogWindow()
```

A top-level window showing one backlog and its releases.

<a id="backlogops_gui.backlog_window.BacklogWindow.__init__"></a>

#### \_\_init\_\_

```python
def __init__(root: tk.Misc, data: BacklogReleases, title: str,
             presets: Callable[[], Optional[dict[str, OutputFormatConfig]]],
             teams: Callable[[], Optional[AvailableTeams]], sink: TextIO,
             on_error: Callable[[str, str],
                                None], on_info: Callable[[str, str],
                                                         None]) -> None
```

Build the window, its menu and the two tables.

**Arguments**:

- `root` - The parent window the new window belongs to.
- `data` - The backlog and releases to show.
- `title` - The window title, typically the source file name.
- `presets` - Callable returning the current output presets.
- `teams` - Callable returning the loaded teams configuration.
- `sink` - Stream that receives low-level write diagnostics.
- `on_error` - Callback used to report a write failure.
- `on_info` - Callback used to report a successful write.

<a id="backlogops_gui.io_dialogs"></a>

# backlogops\_gui.io\_dialogs

File choosers and format-option dialogs for backlog files.

The format options mirror the command line: the format is either inferred
from the file name, taken from a named preset stored in the teams
configuration, or read from a stand-alone configuration file. Writing also
offers to put the releases before the backlog. The chosen format is
returned as a single value understood by the resolver in
:mod:`backlogops_gui.backlog_io`.

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

<a id="backlogops_gui.io_dialogs.choose_key_list_output"></a>

#### choose\_key\_list\_output

```python
def choose_key_list_output(parent: tk.Misc) -> Optional[str]
```

Ask for a key list file to create, or None when cancelled.

<a id="backlogops_gui.io_dialogs.DepOptions"></a>

## DepOptions Objects

```python
@dataclass
class DepOptions()
```

The options selected for ordering a backlog by dependencies.

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
def read_backlog(path: str,
                 value: Optional[str],
                 presets: Optional[dict[str, InputFormatConfig]],
                 sink: Optional[TextIO] = None) -> BacklogReleases
```

Read and validate a backlog and releases from one file.

**Arguments**:

- `path` - The data file to read.
- `value` - The format selection, as documented for the module.
- `presets` - Named input presets, or None when none are configured.
- `sink` - Stream for diagnostics, or None to discard them.
  

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
                  sink: Optional[TextIO] = None) -> None
```

Write a backlog and releases to one file.

**Arguments**:

- `data` - The backlog and releases to write.
- `path` - The data file to create.
- `value` - The format selection, as documented for the module.
- `presets` - Named output presets, or None when none are configured.
- `releases_first` - Whether to write the releases before the backlog.
- `sink` - Stream for diagnostics, or None to discard them.

<a id="backlogops_gui.table_view"></a>

# backlogops\_gui.table\_view

Build read-only tables of a backlog and its releases.

A backlog and its releases are shown as two tables. The table data is
derived from the same row conversion the file writer uses, so the columns
match what would be written to a file. The columns are the union of the
field names met in the rows, kept in first-seen order, and every cell is
rendered as text so the table can show any value type.

<a id="backlogops_gui.table_view.backlog_table"></a>

#### backlog\_table

```python
def backlog_table(data: BacklogReleases) -> tuple[list[str], list[list[str]]]
```

Return the columns and text rows for the backlog table.

<a id="backlogops_gui.table_view.release_table"></a>

#### release\_table

```python
def release_table(data: BacklogReleases) -> tuple[list[str], list[list[str]]]
```

Return the columns and text rows for the releases table.

<a id="backlogops_gui.table_view.make_table"></a>

#### make\_table

```python
def make_table(parent: tk.Misc,
               columns: Sequence[str],
               rows: Sequence[Sequence[str]],
               width: int = COLUMN_WIDTH,
               stretch: bool = True) -> ttk.Treeview
```

Create a read-only Treeview showing the given columns and rows.

When ``stretch`` is True the columns share the table width; when False
each column keeps ``width`` pixels, so a table with few columns stays
narrow instead of spreading the columns across the whole width.

