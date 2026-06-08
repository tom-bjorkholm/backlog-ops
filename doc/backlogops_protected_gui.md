# Table of Contents

* [backlogops\_gui.application](#backlogops_gui.application)
  * [\_add\_label](#backlogops_gui.application._add_label)
  * [\_add\_quit\_button](#backlogops_gui.application._add_quit_button)
  * [build\_main\_window](#backlogops_gui.application.build_main_window)
  * [main](#backlogops_gui.application.main)
* [backlogops\_gui.tcltk\_version](#backlogops_gui.tcltk_version)
  * [\_parse\_tcltk\_version](#backlogops_gui.tcltk_version._parse_tcltk_version)
  * [\_old\_version\_warning](#backlogops_gui.tcltk_version._old_version_warning)
  * [\_bad\_version\_warning](#backlogops_gui.tcltk_version._bad_version_warning)
  * [warning\_for\_version](#backlogops_gui.tcltk_version.warning_for_version)
  * [check\_tcltk\_version](#backlogops_gui.tcltk_version.check_tcltk_version)

<a id="backlogops_gui.application"></a>

# backlogops\_gui.application

Tkinter placeholder application for backlog operations.

<a id="backlogops_gui.application._add_label"></a>

#### \_add\_label

```python
def _add_label(root: tk.Tk, text: str, justify: Literal['center',
                                                        'left']) -> None
```

Add one text label to the main window.

<a id="backlogops_gui.application._add_quit_button"></a>

#### \_add\_quit\_button

```python
def _add_quit_button(root: tk.Tk) -> None
```

Add the quit button to the main window.

<a id="backlogops_gui.application.build_main_window"></a>

#### build\_main\_window

```python
def build_main_window(root: tk.Tk) -> None
```

Build the placeholder widgets in the main window.

<a id="backlogops_gui.application.main"></a>

#### main

```python
def main() -> None
```

Start the backlog operations GUI.

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

