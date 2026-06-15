# Table of Contents

* [backlogops\_gui.gui\_wizard](#backlogops_gui.gui_wizard)
  * [\_AskDialog](#backlogops_gui.gui_wizard._AskDialog)
    * [\_\_init\_\_](#backlogops_gui.gui_wizard._AskDialog.__init__)
    * [\_build](#backlogops_gui.gui_wizard._AskDialog._build)
    * [\_add\_label](#backlogops_gui.gui_wizard._AskDialog._add_label)
    * [\_add\_choices](#backlogops_gui.gui_wizard._AskDialog._add_choices)
    * [\_add\_entry](#backlogops_gui.gui_wizard._AskDialog._add_entry)
    * [\_add\_buttons](#backlogops_gui.gui_wizard._AskDialog._add_buttons)
    * [\_confirm](#backlogops_gui.gui_wizard._AskDialog._confirm)
    * [\_default](#backlogops_gui.gui_wizard._AskDialog._default)
    * [\_cancel](#backlogops_gui.gui_wizard._AskDialog._cancel)
  * [TkWizardBridge](#backlogops_gui.gui_wizard.TkWizardBridge)
    * [\_\_init\_\_](#backlogops_gui.gui_wizard.TkWizardBridge.__init__)
    * [ask](#backlogops_gui.gui_wizard.TkWizardBridge.ask)
    * [error\_file](#backlogops_gui.gui_wizard.TkWizardBridge.error_file)
    * [show](#backlogops_gui.gui_wizard.TkWizardBridge.show)
    * [\_ask\_modal](#backlogops_gui.gui_wizard.TkWizardBridge._ask_modal)
    * [\_show\_modal](#backlogops_gui.gui_wizard.TkWizardBridge._show_modal)
* [backlogops\_gui.application](#backlogops_gui.application)
  * [initial\_config](#backlogops_gui.application.initial_config)
  * [BacklogApp](#backlogops_gui.application.BacklogApp)
    * [\_\_init\_\_](#backlogops_gui.application.BacklogApp.__init__)
    * [in\_presets](#backlogops_gui.application.BacklogApp.in_presets)
    * [out\_presets](#backlogops_gui.application.BacklogApp.out_presets)
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
    * [\_add\_file\_menu](#backlogops_gui.application.BacklogApp._add_file_menu)
    * [\_add\_config\_menu](#backlogops_gui.application.BacklogApp._add_config_menu)
  * [\_build\_parser](#backlogops_gui.application._build_parser)
  * [\_add\_warning](#backlogops_gui.application._add_warning)
  * [main](#backlogops_gui.application.main)
* [backlogops\_gui.tcltk\_version](#backlogops_gui.tcltk_version)
  * [\_parse\_tcltk\_version](#backlogops_gui.tcltk_version._parse_tcltk_version)
  * [\_old\_version\_warning](#backlogops_gui.tcltk_version._old_version_warning)
  * [\_bad\_version\_warning](#backlogops_gui.tcltk_version._bad_version_warning)
  * [warning\_for\_version](#backlogops_gui.tcltk_version.warning_for_version)
  * [check\_tcltk\_version](#backlogops_gui.tcltk_version.check_tcltk_version)
* [backlogops\_gui.backlog\_window](#backlogops_gui.backlog_window)
  * [save\_backlog](#backlogops_gui.backlog_window.save_backlog)
  * [BacklogWindow](#backlogops_gui.backlog_window.BacklogWindow)
    * [\_\_init\_\_](#backlogops_gui.backlog_window.BacklogWindow.__init__)
    * [\_add\_menu](#backlogops_gui.backlog_window.BacklogWindow._add_menu)
    * [\_add\_table](#backlogops_gui.backlog_window.BacklogWindow._add_table)
    * [\_save](#backlogops_gui.backlog_window.BacklogWindow._save)
* [backlogops\_gui.io\_dialogs](#backlogops_gui.io_dialogs)
  * [format\_value](#backlogops_gui.io_dialogs.format_value)
  * [ReadOptions](#backlogops_gui.io_dialogs.ReadOptions)
  * [WriteOptions](#backlogops_gui.io_dialogs.WriteOptions)
  * [choose\_input\_file](#backlogops_gui.io_dialogs.choose_input_file)
  * [choose\_output\_file](#backlogops_gui.io_dialogs.choose_output_file)
  * [choose\_config\_file](#backlogops_gui.io_dialogs.choose_config_file)
  * [\_FormatDialog](#backlogops_gui.io_dialogs._FormatDialog)
    * [\_\_init\_\_](#backlogops_gui.io_dialogs._FormatDialog.__init__)
    * [\_build](#backlogops_gui.io_dialogs._FormatDialog._build)
    * [\_add\_radio](#backlogops_gui.io_dialogs._FormatDialog._add_radio)
    * [\_add\_preset\_row](#backlogops_gui.io_dialogs._FormatDialog._add_preset_row)
    * [\_add\_file\_row](#backlogops_gui.io_dialogs._FormatDialog._add_file_row)
    * [\_add\_buttons](#backlogops_gui.io_dialogs._FormatDialog._add_buttons)
    * [\_browse](#backlogops_gui.io_dialogs._FormatDialog._browse)
    * [\_confirm](#backlogops_gui.io_dialogs._FormatDialog._confirm)
    * [\_selected\_value](#backlogops_gui.io_dialogs._FormatDialog._selected_value)
    * [\_cancel](#backlogops_gui.io_dialogs._FormatDialog._cancel)
  * [ask\_read\_options](#backlogops_gui.io_dialogs.ask_read_options)
  * [ask\_write\_options](#backlogops_gui.io_dialogs.ask_write_options)
* [backlogops\_gui.backlog\_io](#backlogops_gui.backlog_io)
  * [read\_backlog](#backlogops_gui.backlog_io.read_backlog)
  * [write\_backlog](#backlogops_gui.backlog_io.write_backlog)
* [backlogops\_gui.table\_view](#backlogops_gui.table_view)
  * [\_columns](#backlogops_gui.table_view._columns)
  * [\_cell\_text](#backlogops_gui.table_view._cell_text)
  * [\_table](#backlogops_gui.table_view._table)
  * [backlog\_table](#backlogops_gui.table_view.backlog_table)
  * [release\_table](#backlogops_gui.table_view.release_table)
  * [make\_table](#backlogops_gui.table_view.make_table)

<a id="backlogops_gui.gui_wizard"></a>

# backlogops\_gui.gui\_wizard

Graphical bridge that drives the synchronous teams wizard.

The teams configuration wizard asks its questions through a
:class:`WizardUiBridge` by calling :meth:`ask` in a loop. This module
provides a bridge that answers each call with a modal Tkinter dialog, so
the existing synchronous wizard can run unchanged inside a menu callback.
A cancelled dialog raises :class:`EOFError`, which the wizard documents as
the way an interrupted input is reported.

<a id="backlogops_gui.gui_wizard._AskDialog"></a>

## \_AskDialog Objects

```python
class _AskDialog()
```

Modal dialog that asks one wizard question and stores the answer.

<a id="backlogops_gui.gui_wizard._AskDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, question: str, re_ask_reason: Optional[str],
             choices: Optional[Sequence[str]]) -> None
```

Build, show and wait for the modal question dialog.

<a id="backlogops_gui.gui_wizard._AskDialog._build"></a>

#### \_build

```python
def _build(question: str, re_ask_reason: Optional[str],
           choices: Optional[Sequence[str]]) -> None
```

Create the widgets for the question and the answer area.

<a id="backlogops_gui.gui_wizard._AskDialog._add_label"></a>

#### \_add\_label

```python
def _add_label(text: str, color: str) -> None
```

Add one wrapped text label to the dialog.

<a id="backlogops_gui.gui_wizard._AskDialog._add_choices"></a>

#### \_add\_choices

```python
def _add_choices(choices: Sequence[str]) -> None
```

Add a single-selection list of the offered choices.

<a id="backlogops_gui.gui_wizard._AskDialog._add_entry"></a>

#### \_add\_entry

```python
def _add_entry() -> None
```

Add a free-text entry for the answer.

<a id="backlogops_gui.gui_wizard._AskDialog._add_buttons"></a>

#### \_add\_buttons

```python
def _add_buttons(has_choices: bool) -> None
```

Add the confirm, default and cancel buttons.

<a id="backlogops_gui.gui_wizard._AskDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the selected or entered answer and close the dialog.

<a id="backlogops_gui.gui_wizard._AskDialog._default"></a>

#### \_default

```python
def _default() -> None
```

Answer with an empty string to request the default value.

<a id="backlogops_gui.gui_wizard._AskDialog._cancel"></a>

#### \_cancel

```python
def _cancel() -> None
```

Mark the dialog cancelled and close it.

<a id="backlogops_gui.gui_wizard.TkWizardBridge"></a>

## TkWizardBridge Objects

```python
class TkWizardBridge(WizardUiBridge)
```

Bridge that answers wizard questions with Tkinter dialogs.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc,
             ask_fn: Optional[
                 Callable[[str, Optional[str], Optional[Sequence[str]]],
                          str | int]] = None,
             show_fn: Optional[Callable[[str], None]] = None) -> None
```

Store the parent window and optional injected dialog callables.

**Arguments**:

- `parent` - The window the modal dialogs are shown over.
- `ask_fn` - Replacement for the modal question dialog, used by
  tests to script answers without a display.
- `show_fn` - Replacement for the modal message dialog.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.ask"></a>

#### ask

```python
def ask(question: str,
        re_ask_reason: Optional[str] = None,
        choices: Optional[Sequence[str]] = None) -> str | int
```

Ask one question and return the user's answer.

Returns the entered text, or the zero-based index of a selected
choice, or an empty string when the user requests the default.

**Raises**:

- `EOFError` - The user cancelled the dialog.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.error_file"></a>

#### error\_file

```python
def error_file() -> TextIO
```

Return a sink that discards low-level wizard diagnostics.

<a id="backlogops_gui.gui_wizard.TkWizardBridge.show"></a>

#### show

```python
def show(message: str) -> None
```

Show an informational message to the user.

<a id="backlogops_gui.gui_wizard.TkWizardBridge._ask_modal"></a>

#### \_ask\_modal

```python
def _ask_modal(question: str, re_ask_reason: Optional[str],
               choices: Optional[Sequence[str]]) -> str | int
```

Ask one question with a modal dialog over the parent window.

<a id="backlogops_gui.gui_wizard.TkWizardBridge._show_modal"></a>

#### \_show\_modal

```python
def _show_modal(message: str) -> None
```

Show one informational message with a modal dialog.

<a id="backlogops_gui.application"></a>

# backlogops\_gui.application

Tkinter application for backlog operations.

The application opens a main window whose menu reads a backlog from a file,
runs the teams configuration wizard, writes the running configuration to a
file, and creates a demonstration backlog. Each backlog opens in its own
window. The teams configuration is taken from the file given with ``-c`` or
from the configured locations; when no configuration is found the wizard
runs at startup, and cancelling it ends the application.

<a id="backlogops_gui.application.initial_config"></a>

#### initial\_config

```python
def initial_config(
    config_arg: Optional[str]
) -> tuple[Optional[AvailableTeamsConfig], Optional[str]]
```

Return the startup configuration and an optional error message.

The configuration is looked up as documented for
:func:`backlogops.get_available_teams`. A failure is mapped to a None
configuration and the error text, so the caller can decide whether to
show the error and whether to run the wizard.

**Arguments**:

- `config_arg` - The file from ``-c``, or None to search the defaults.
  

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

Store the main window and the current configuration.

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

<a id="backlogops_gui.application._build_parser"></a>

#### \_build\_parser

```python
def _build_parser() -> argparse.ArgumentParser
```

Build the command line parser for the GUI launcher.

<a id="backlogops_gui.application._add_warning"></a>

#### \_add\_warning

```python
def _add_warning(root: tk.Tk) -> None
```

Add a Tcl/Tk version warning label when one applies.

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

<a id="backlogops_gui.backlog_window"></a>

# backlogops\_gui.backlog\_window

A window that shows one backlog and its releases as two tables.

The window shows the backlog and the releases as two read-only tables and
carries a menu with the actions that can be done to the backlog. The first
version offers saving to a file and closing the window. Saving is kept in a
module function so it can be tested without a display.

<a id="backlogops_gui.backlog_window.save_backlog"></a>

#### save\_backlog

```python
def save_backlog(parent: tk.Misc, data: BacklogReleases,
                 presets: Optional[dict[str, OutputFormatConfig]],
                 on_error: Callable[[str, str],
                                    None], on_info: Callable[[str, str],
                                                             None]) -> None
```

Ask where and how to save a backlog and write it.

**Arguments**:

- `parent` - The window the dialogs are shown over.
- `data` - The backlog and releases to write.
- `presets` - Named output presets, or None when none are configured.
- `on_error` - Callback used to report a write failure.
- `on_info` - Callback used to report a successful write.

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
- `on_error` - Callback used to report a write failure.
- `on_info` - Callback used to report a successful write.

<a id="backlogops_gui.backlog_window.BacklogWindow._add_menu"></a>

#### \_add\_menu

```python
def _add_menu() -> None
```

Add the backlog menu with the save and close actions.

<a id="backlogops_gui.backlog_window.BacklogWindow._add_table"></a>

#### \_add\_table

```python
def _add_table(heading: str, columns: list[str],
               rows: list[list[str]]) -> None
```

Add one labeled, scrollable table to the window.

<a id="backlogops_gui.backlog_window.BacklogWindow._save"></a>

#### \_save

```python
def _save() -> None
```

Save the backlog through the shared save helper.

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

<a id="backlogops_gui.io_dialogs._FormatDialog"></a>

## \_FormatDialog Objects

```python
class _FormatDialog()
```

Modal dialog collecting the format selection for one file.

<a id="backlogops_gui.io_dialogs._FormatDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, presets: Sequence[str],
             with_releases_first: bool) -> None
```

Build, show and wait for the modal format dialog.

<a id="backlogops_gui.io_dialogs._FormatDialog._build"></a>

#### \_build

```python
def _build(with_releases_first: bool) -> None
```

Create the radio buttons, inputs and action buttons.

<a id="backlogops_gui.io_dialogs._FormatDialog._add_radio"></a>

#### \_add\_radio

```python
def _add_radio(text: str, mode: int) -> None
```

Add one mode radio button.

<a id="backlogops_gui.io_dialogs._FormatDialog._add_preset_row"></a>

#### \_add\_preset\_row

```python
def _add_preset_row() -> None
```

Add the preset radio button and its choices, when available.

<a id="backlogops_gui.io_dialogs._FormatDialog._add_file_row"></a>

#### \_add\_file\_row

```python
def _add_file_row() -> None
```

Add the configuration-file radio button, entry and browse.

<a id="backlogops_gui.io_dialogs._FormatDialog._add_buttons"></a>

#### \_add\_buttons

```python
def _add_buttons() -> None
```

Add the confirm and cancel buttons.

<a id="backlogops_gui.io_dialogs._FormatDialog._browse"></a>

#### \_browse

```python
def _browse() -> None
```

Pick a configuration file and select the file mode.

<a id="backlogops_gui.io_dialogs._FormatDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the selected format value and close the dialog.

<a id="backlogops_gui.io_dialogs._FormatDialog._selected_value"></a>

#### \_selected\_value

```python
def _selected_value() -> Optional[str]
```

Return the format value for the selected mode.

<a id="backlogops_gui.io_dialogs._FormatDialog._cancel"></a>

#### \_cancel

```python
def _cancel() -> None
```

Mark the dialog cancelled and close it.

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

<a id="backlogops_gui.backlog_io"></a>

# backlogops\_gui.backlog\_io

Read and write a backlog and releases with format options.

These helpers wrap the library read and write functions and resolve the
format the same way the command line does: an empty value infers the
format from the file name, a value of only letters and digits is a preset
name looked up in the presets from the teams configuration, and any other
value is the path of a stand-alone format configuration file. Diagnostics
go to a sink, because a graphical application reports failures as dialogs.

<a id="backlogops_gui.backlog_io.read_backlog"></a>

#### read\_backlog

```python
def read_backlog(
        path: str, value: Optional[str],
        presets: Optional[dict[str, InputFormatConfig]]) -> BacklogReleases
```

Read and validate a backlog and releases from one file.

**Arguments**:

- `path` - The data file to read.
- `value` - The format selection, as documented for the module.
- `presets` - Named input presets, or None when none are configured.
  

**Returns**:

  The validated backlog and releases read from the file.

<a id="backlogops_gui.backlog_io.write_backlog"></a>

#### write\_backlog

```python
def write_backlog(data: BacklogReleases, path: str, value: Optional[str],
                  presets: Optional[dict[str, OutputFormatConfig]],
                  releases_first: bool) -> None
```

Write a backlog and releases to one file.

**Arguments**:

- `data` - The backlog and releases to write.
- `path` - The data file to create.
- `value` - The format selection, as documented for the module.
- `presets` - Named output presets, or None when none are configured.
- `releases_first` - Whether to write the releases before the backlog.

<a id="backlogops_gui.table_view"></a>

# backlogops\_gui.table\_view

Build read-only tables of a backlog and its releases.

A backlog and its releases are shown as two tables. The table data is
derived from the same row conversion the file writer uses, so the columns
match what would be written to a file. The columns are the union of the
field names met in the rows, kept in first-seen order, and every cell is
rendered as text so the table can show any value type.

<a id="backlogops_gui.table_view._columns"></a>

#### \_columns

```python
def _columns(rows: Sequence[dict[str, Value]]) -> list[str]
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
        rows: Sequence[dict[str, Value]]) -> tuple[list[str], list[list[str]]]
```

Return the columns and text rows for a sequence of row dicts.

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
def make_table(parent: tk.Misc, columns: Sequence[str],
               rows: Sequence[Sequence[str]]) -> ttk.Treeview
```

Create a read-only Treeview showing the given columns and rows.

