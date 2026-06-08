# Table of Contents

* [backlogops\_gui.application](#backlogops_gui.application)
  * [build\_main\_window](#backlogops_gui.application.build_main_window)
  * [main](#backlogops_gui.application.main)
* [backlogops\_gui.tcltk\_version](#backlogops_gui.tcltk_version)
  * [warning\_for\_version](#backlogops_gui.tcltk_version.warning_for_version)
  * [check\_tcltk\_version](#backlogops_gui.tcltk_version.check_tcltk_version)

<a id="backlogops_gui.application"></a>

# backlogops\_gui.application

Tkinter placeholder application for backlog operations.

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

