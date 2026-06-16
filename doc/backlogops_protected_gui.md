# Table of Contents

* [backlogops\_gui.gui\_wizard](#backlogops_gui.gui_wizard)
  * [\_WizardWindow](#backlogops_gui.gui_wizard._WizardWindow)
    * [\_\_init\_\_](#backlogops_gui.gui_wizard._WizardWindow.__init__)
    * [\_build\_messages](#backlogops_gui.gui_wizard._WizardWindow._build_messages)
    * [show](#backlogops_gui.gui_wizard._WizardWindow.show)
    * [close](#backlogops_gui.gui_wizard._WizardWindow.close)
    * [ask](#backlogops_gui.gui_wizard._WizardWindow.ask)
    * [ask\_yes\_no](#backlogops_gui.gui_wizard._WizardWindow.ask_yes_no)
    * [\_ask\_text](#backlogops_gui.gui_wizard._WizardWindow._ask_text)
    * [\_ask\_choice](#backlogops_gui.gui_wizard._WizardWindow._ask_choice)
    * [\_pick](#backlogops_gui.gui_wizard._WizardWindow._pick)
    * [\_begin](#backlogops_gui.gui_wizard._WizardWindow._begin)
    * [\_add\_label](#backlogops_gui.gui_wizard._WizardWindow._add_label)
    * [\_add\_buttons](#backlogops_gui.gui_wizard._WizardWindow._add_buttons)
    * [\_wait](#backlogops_gui.gui_wizard._WizardWindow._wait)
    * [\_finish](#backlogops_gui.gui_wizard._WizardWindow._finish)
    * [\_cancel](#backlogops_gui.gui_wizard._WizardWindow._cancel)
  * [TkWizardBridge](#backlogops_gui.gui_wizard.TkWizardBridge)
    * [\_\_init\_\_](#backlogops_gui.gui_wizard.TkWizardBridge.__init__)
    * [ask](#backlogops_gui.gui_wizard.TkWizardBridge.ask)
    * [ask\_yes\_no](#backlogops_gui.gui_wizard.TkWizardBridge.ask_yes_no)
    * [show](#backlogops_gui.gui_wizard.TkWizardBridge.show)
    * [error\_file](#backlogops_gui.gui_wizard.TkWizardBridge.error_file)
    * [close](#backlogops_gui.gui_wizard.TkWizardBridge.close)
    * [\_window\_obj](#backlogops_gui.gui_wizard.TkWizardBridge._window_obj)
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
    * [\_add\_file\_menu](#backlogops_gui.application.BacklogApp._add_file_menu)
    * [\_add\_config\_menu](#backlogops_gui.application.BacklogApp._add_config_menu)
    * [build\_body](#backlogops_gui.application.BacklogApp.build_body)
    * [\_build\_log\_view](#backlogops_gui.application.BacklogApp._build_log_view)
    * [\_status\_text](#backlogops_gui.application.BacklogApp._status_text)
    * [\_update\_status](#backlogops_gui.application.BacklogApp._update_status)
    * [\_refresh\_log](#backlogops_gui.application.BacklogApp._refresh_log)
    * [\_schedule\_refresh](#backlogops_gui.application.BacklogApp._schedule_refresh)
  * [\_build\_parser](#backlogops_gui.application._build_parser)
  * [main](#backlogops_gui.application.main)
* [backlogops\_gui.tcltk\_version](#backlogops_gui.tcltk_version)
  * [\_parse\_tcltk\_version](#backlogops_gui.tcltk_version._parse_tcltk_version)
  * [\_old\_version\_warning](#backlogops_gui.tcltk_version._old_version_warning)
  * [\_bad\_version\_warning](#backlogops_gui.tcltk_version._bad_version_warning)
  * [warning\_for\_version](#backlogops_gui.tcltk_version.warning_for_version)
  * [check\_tcltk\_version](#backlogops_gui.tcltk_version.check_tcltk_version)
* [backlogops\_gui.backlog\_window](#backlogops_gui.backlog_window)
  * [save\_backlog](#backlogops_gui.backlog_window.save_backlog)
  * [\_apply\_change](#backlogops_gui.backlog_window._apply_change)
  * [order\_by\_keys](#backlogops_gui.backlog_window.order_by_keys)
  * [order\_by\_deps](#backlogops_gui.backlog_window.order_by_deps)
  * [estimate\_date](#backlogops_gui.backlog_window.estimate_date)
  * [set\_plan](#backlogops_gui.backlog_window.set_plan)
  * [extract\_keys](#backlogops_gui.backlog_window.extract_keys)
  * [BacklogWindow](#backlogops_gui.backlog_window.BacklogWindow)
    * [\_\_init\_\_](#backlogops_gui.backlog_window.BacklogWindow.__init__)
    * [\_build\_tables](#backlogops_gui.backlog_window.BacklogWindow._build_tables)
    * [\_refresh\_tables](#backlogops_gui.backlog_window.BacklogWindow._refresh_tables)
    * [\_add\_menu](#backlogops_gui.backlog_window.BacklogWindow._add_menu)
    * [\_add\_actions](#backlogops_gui.backlog_window.BacklogWindow._add_actions)
    * [\_add\_table](#backlogops_gui.backlog_window.BacklogWindow._add_table)
    * [\_make\_tree](#backlogops_gui.backlog_window.BacklogWindow._make_tree)
    * [\_save](#backlogops_gui.backlog_window.BacklogWindow._save)
    * [\_order\_by\_keys](#backlogops_gui.backlog_window.BacklogWindow._order_by_keys)
    * [\_order\_by\_deps](#backlogops_gui.backlog_window.BacklogWindow._order_by_deps)
    * [\_estimate\_date](#backlogops_gui.backlog_window.BacklogWindow._estimate_date)
    * [\_set\_plan](#backlogops_gui.backlog_window.BacklogWindow._set_plan)
    * [\_extract\_keys](#backlogops_gui.backlog_window.BacklogWindow._extract_keys)
* [backlogops\_gui.io\_dialogs](#backlogops_gui.io_dialogs)
  * [format\_value](#backlogops_gui.io_dialogs.format_value)
  * [ReadOptions](#backlogops_gui.io_dialogs.ReadOptions)
  * [WriteOptions](#backlogops_gui.io_dialogs.WriteOptions)
  * [choose\_input\_file](#backlogops_gui.io_dialogs.choose_input_file)
  * [choose\_output\_file](#backlogops_gui.io_dialogs.choose_output_file)
  * [choose\_config\_file](#backlogops_gui.io_dialogs.choose_config_file)
  * [\_ModalDialog](#backlogops_gui.io_dialogs._ModalDialog)
    * [\_\_init\_\_](#backlogops_gui.io_dialogs._ModalDialog.__init__)
    * [\_show](#backlogops_gui.io_dialogs._ModalDialog._show)
    * [\_add\_buttons](#backlogops_gui.io_dialogs._ModalDialog._add_buttons)
    * [\_confirm](#backlogops_gui.io_dialogs._ModalDialog._confirm)
    * [\_cancel](#backlogops_gui.io_dialogs._ModalDialog._cancel)
  * [\_FormatDialog](#backlogops_gui.io_dialogs._FormatDialog)
    * [\_\_init\_\_](#backlogops_gui.io_dialogs._FormatDialog.__init__)
    * [\_build](#backlogops_gui.io_dialogs._FormatDialog._build)
    * [\_add\_radio](#backlogops_gui.io_dialogs._FormatDialog._add_radio)
    * [\_add\_preset\_row](#backlogops_gui.io_dialogs._FormatDialog._add_preset_row)
    * [\_add\_file\_row](#backlogops_gui.io_dialogs._FormatDialog._add_file_row)
    * [\_browse](#backlogops_gui.io_dialogs._FormatDialog._browse)
    * [\_confirm](#backlogops_gui.io_dialogs._FormatDialog._confirm)
    * [\_selected\_value](#backlogops_gui.io_dialogs._FormatDialog._selected_value)
  * [ask\_read\_options](#backlogops_gui.io_dialogs.ask_read_options)
  * [ask\_write\_options](#backlogops_gui.io_dialogs.ask_write_options)
  * [choose\_key\_list\_output](#backlogops_gui.io_dialogs.choose_key_list_output)
  * [DepOptions](#backlogops_gui.io_dialogs.DepOptions)
  * [StartChoice](#backlogops_gui.io_dialogs.StartChoice)
  * [\_KeysDialog](#backlogops_gui.io_dialogs._KeysDialog)
    * [\_\_init\_\_](#backlogops_gui.io_dialogs._KeysDialog.__init__)
    * [\_build\_text](#backlogops_gui.io_dialogs._KeysDialog._build_text)
    * [\_load](#backlogops_gui.io_dialogs._KeysDialog._load)
    * [\_confirm](#backlogops_gui.io_dialogs._KeysDialog._confirm)
  * [\_DepOptionsDialog](#backlogops_gui.io_dialogs._DepOptionsDialog)
    * [\_\_init\_\_](#backlogops_gui.io_dialogs._DepOptionsDialog.__init__)
    * [\_build](#backlogops_gui.io_dialogs._DepOptionsDialog._build)
    * [\_build\_mode](#backlogops_gui.io_dialogs._DepOptionsDialog._build_mode)
    * [\_build\_space](#backlogops_gui.io_dialogs._DepOptionsDialog._build_space)
    * [\_confirm](#backlogops_gui.io_dialogs._DepOptionsDialog._confirm)
  * [\_StartDateDialog](#backlogops_gui.io_dialogs._StartDateDialog)
    * [\_\_init\_\_](#backlogops_gui.io_dialogs._StartDateDialog.__init__)
    * [\_build](#backlogops_gui.io_dialogs._StartDateDialog._build)
    * [\_confirm](#backlogops_gui.io_dialogs._StartDateDialog._confirm)
  * [\_LevelsDialog](#backlogops_gui.io_dialogs._LevelsDialog)
    * [\_\_init\_\_](#backlogops_gui.io_dialogs._LevelsDialog.__init__)
    * [\_build](#backlogops_gui.io_dialogs._LevelsDialog._build)
    * [\_confirm](#backlogops_gui.io_dialogs._LevelsDialog._confirm)
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
  * [\_insert\_row](#backlogops_gui.table_view._insert_row)
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

<a id="backlogops_gui.gui_wizard._WizardWindow"></a>

## \_WizardWindow Objects

```python
class _WizardWindow()
```

One reused window that asks every wizard prompt in turn.

<a id="backlogops_gui.gui_wizard._WizardWindow.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Create the fixed-size window and its lasting message area.

<a id="backlogops_gui.gui_wizard._WizardWindow._build_messages"></a>

#### \_build\_messages

```python
def _build_messages() -> tk.Text
```

Build the read-only area that keeps the wizard messages.

<a id="backlogops_gui.gui_wizard._WizardWindow.show"></a>

#### show

```python
def show(message: str) -> None
```

Append one lasting message to the message area.

<a id="backlogops_gui.gui_wizard._WizardWindow.close"></a>

#### close

```python
def close() -> None
```

Destroy the wizard window.

<a id="backlogops_gui.gui_wizard._WizardWindow.ask"></a>

#### ask

```python
def ask(question: str, re_ask: Optional[str],
        choices: Optional[Sequence[str]]) -> str | int
```

Ask one free-text or choice question and return the answer.

<a id="backlogops_gui.gui_wizard._WizardWindow.ask_yes_no"></a>

#### ask\_yes\_no

```python
def ask_yes_no(question: str, default: bool) -> bool
```

Ask one yes/no question with dedicated buttons.

<a id="backlogops_gui.gui_wizard._WizardWindow._ask_text"></a>

#### \_ask\_text

```python
def _ask_text(question: str, re_ask: Optional[str]) -> str
```

Ask one free-text question and return the entered text.

<a id="backlogops_gui.gui_wizard._WizardWindow._ask_choice"></a>

#### \_ask\_choice

```python
def _ask_choice(question: str, re_ask: Optional[str],
                choices: Sequence[str]) -> str | int
```

Ask one question with a single-selection list of choices.

<a id="backlogops_gui.gui_wizard._WizardWindow._pick"></a>

#### \_pick

```python
def _pick(listbox: tk.Listbox) -> None
```

Finish a choice question with the selected zero-based index.

<a id="backlogops_gui.gui_wizard._WizardWindow._begin"></a>

#### \_begin

```python
def _begin(question: str, re_ask: Optional[str]) -> None
```

Clear the content area and show the question and any reason.

<a id="backlogops_gui.gui_wizard._WizardWindow._add_label"></a>

#### \_add\_label

```python
def _add_label(text: str, color: str) -> None
```

Add one wrapped label to the content area.

<a id="backlogops_gui.gui_wizard._WizardWindow._add_buttons"></a>

#### \_add\_buttons

```python
def _add_buttons(on_ok: Callable[[], None],
                 on_default: Optional[Callable[[], None]]) -> None
```

Add the confirm, optional default, and cancel buttons.

<a id="backlogops_gui.gui_wizard._WizardWindow._wait"></a>

#### \_wait

```python
def _wait() -> object
```

Block until the current prompt is answered or cancelled.

<a id="backlogops_gui.gui_wizard._WizardWindow._finish"></a>

#### \_finish

```python
def _finish(value: object) -> None
```

Store the answer and release the waiting prompt.

<a id="backlogops_gui.gui_wizard._WizardWindow._cancel"></a>

#### \_cancel

```python
def _cancel() -> None
```

Mark the session cancelled and release the waiting prompt.

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

<a id="backlogops_gui.gui_wizard.TkWizardBridge._window_obj"></a>

#### \_window\_obj

```python
def _window_obj() -> _WizardWindow
```

Return the wizard window, creating it on first use.

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

<a id="backlogops_gui.application.BacklogApp.build_body"></a>

#### build\_body

```python
def build_body() -> None
```

Build the main window body and start the log refresh.

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

<a id="backlogops_gui.application.BacklogApp._refresh_log"></a>

#### \_refresh\_log

```python
def _refresh_log() -> None
```

Copy the latest log lines into the read-only log view.

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

<a id="backlogops_gui.backlog_window._apply_change"></a>

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

<a id="backlogops_gui.backlog_window.BacklogWindow._extract_keys"></a>

#### \_extract\_keys

```python
def _extract_keys() -> None
```

Extract backlog keys at chosen levels to a key list file.

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

<a id="backlogops_gui.io_dialogs._ModalDialog"></a>

## \_ModalDialog Objects

```python
class _ModalDialog()
```

Base for small modal dialogs with OK and Cancel buttons.

<a id="backlogops_gui.io_dialogs._ModalDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, title: str) -> None
```

Create the modal top-level window and its close handler.

<a id="backlogops_gui.io_dialogs._ModalDialog._show"></a>

#### \_show

```python
def _show() -> None
```

Add the buttons, grab the focus and wait for the close.

<a id="backlogops_gui.io_dialogs._ModalDialog._add_buttons"></a>

#### \_add\_buttons

```python
def _add_buttons() -> None
```

Add the confirm and cancel buttons.

<a id="backlogops_gui.io_dialogs._ModalDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Close the dialog; subclasses override to store their values.

<a id="backlogops_gui.io_dialogs._ModalDialog._cancel"></a>

#### \_cancel

```python
def _cancel() -> None
```

Mark the dialog cancelled and close it.

<a id="backlogops_gui.io_dialogs._FormatDialog"></a>

## \_FormatDialog Objects

```python
class _FormatDialog(_ModalDialog)
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

<a id="backlogops_gui.io_dialogs._KeysDialog"></a>

## \_KeysDialog Objects

```python
class _KeysDialog(_ModalDialog)
```

Modal dialog collecting the leading keys for a reordering.

<a id="backlogops_gui.io_dialogs._KeysDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc, sink: TextIO) -> None
```

Build, show and wait for the key entry dialog.

<a id="backlogops_gui.io_dialogs._KeysDialog._build_text"></a>

#### \_build\_text

```python
def _build_text() -> tk.Text
```

Add the entry label, text box and the load-from-file button.

<a id="backlogops_gui.io_dialogs._KeysDialog._load"></a>

#### \_load

```python
def _load() -> None
```

Read a key list file into the text box, reporting failures.

<a id="backlogops_gui.io_dialogs._KeysDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Split the text on whitespace and close the dialog.

<a id="backlogops_gui.io_dialogs._DepOptionsDialog"></a>

## \_DepOptionsDialog Objects

```python
class _DepOptionsDialog(_ModalDialog)
```

Modal dialog collecting the order-by-dependencies options.

<a id="backlogops_gui.io_dialogs._DepOptionsDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the dependency options dialog.

<a id="backlogops_gui.io_dialogs._DepOptionsDialog._build"></a>

#### \_build

```python
def _build() -> None
```

Add the later check box, the mode chooser and the key entry.

<a id="backlogops_gui.io_dialogs._DepOptionsDialog._build_mode"></a>

#### \_build\_mode

```python
def _build_mode() -> None
```

Add the placement-mode label and chooser.

<a id="backlogops_gui.io_dialogs._DepOptionsDialog._build_space"></a>

#### \_build\_space

```python
def _build_space() -> None
```

Add the space-around label and key entry.

<a id="backlogops_gui.io_dialogs._DepOptionsDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the selected options and close the dialog.

<a id="backlogops_gui.io_dialogs._StartDateDialog"></a>

## \_StartDateDialog Objects

```python
class _StartDateDialog(_ModalDialog)
```

Modal dialog collecting the start date for the estimate.

<a id="backlogops_gui.io_dialogs._StartDateDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the start date dialog.

<a id="backlogops_gui.io_dialogs._StartDateDialog._build"></a>

#### \_build

```python
def _build() -> None
```

Add the start date label and entry.

<a id="backlogops_gui.io_dialogs._StartDateDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Parse the date, keeping the dialog open on a bad value.

<a id="backlogops_gui.io_dialogs._LevelsDialog"></a>

## \_LevelsDialog Objects

```python
class _LevelsDialog(_ModalDialog)
```

Modal dialog selecting the levels to extract keys at.

<a id="backlogops_gui.io_dialogs._LevelsDialog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(parent: tk.Misc) -> None
```

Build, show and wait for the level selection dialog.

<a id="backlogops_gui.io_dialogs._LevelsDialog._build"></a>

#### \_build

```python
def _build() -> dict[int, tk.BooleanVar]
```

Add a check box for each default level and return its variables.

<a id="backlogops_gui.io_dialogs._LevelsDialog._confirm"></a>

#### \_confirm

```python
def _confirm() -> None
```

Store the chosen levels, requiring at least one selection.

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

<a id="backlogops_gui.backlog_io._sink"></a>

#### \_sink

```python
def _sink(sink: Optional[TextIO]) -> TextIO
```

Return the given diagnostics sink, or a discarding one.

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

Build tables of a backlog and its releases with cell formatting.

A backlog and its releases are shown as two tables. The table data and the
cell formatting are derived from the same formatting the file writer uses,
so the on-screen colors match a written spreadsheet: the status cell and the
estimated-ready-date cell are highlighted by the format rules, and the other
cells are left plain. The columns are the union of the field names met in the
rows, kept in first-seen order, and every cell is rendered as text so the
table can show any value type.

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
        data: BacklogReleases) -> tuple[list[str], list[list[ValueFmt]]]
```

Return the columns and formatted rows for the backlog table.

<a id="backlogops_gui.table_view.release_table"></a>

#### release\_table

```python
def release_table(
        data: BacklogReleases) -> tuple[list[str], list[list[ValueFmt]]]
```

Return the columns and formatted rows for the releases table.

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

<a id="backlogops_gui.table_view._insert_row"></a>

#### \_insert\_row

```python
def _insert_row(tree: ttk.Treeview, columns: Sequence[str],
                row: Sequence[ValueFmt]) -> None
```

Insert one row as text and color its formatted cells.

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
written spreadsheet. When ``stretch`` is True the columns share the table
width; when False each column keeps ``width`` pixels, so a table with few
columns stays narrow instead of spreading across the whole width.

