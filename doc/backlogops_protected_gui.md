# Table of Contents

* [backlogops\_gui.application](#backlogops_gui.application)
  * [PackedWidget](#backlogops_gui.application.PackedWidget)
    * [pack](#backlogops_gui.application.PackedWidget.pack)
  * [TkWindow](#backlogops_gui.application.TkWindow)
    * [title](#backlogops_gui.application.TkWindow.title)
    * [quit](#backlogops_gui.application.TkWindow.quit)
    * [mainloop](#backlogops_gui.application.TkWindow.mainloop)
  * [RootMaker](#backlogops_gui.application.RootMaker)
    * [\_\_call\_\_](#backlogops_gui.application.RootMaker.__call__)
  * [LabelMaker](#backlogops_gui.application.LabelMaker)
    * [\_\_call\_\_](#backlogops_gui.application.LabelMaker.__call__)
  * [ButtonMaker](#backlogops_gui.application.ButtonMaker)
    * [\_\_call\_\_](#backlogops_gui.application.ButtonMaker.__call__)
  * [\_make\_root](#backlogops_gui.application._make_root)
  * [\_make\_label](#backlogops_gui.application._make_label)
  * [\_make\_button](#backlogops_gui.application._make_button)
  * [\_add\_label](#backlogops_gui.application._add_label)
  * [\_add\_quit\_button](#backlogops_gui.application._add_quit_button)
  * [build\_main\_window](#backlogops_gui.application.build_main_window)
  * [main](#backlogops_gui.application.main)
* [backlogops\_gui.tcltk\_version](#backlogops_gui.tcltk_version)
  * [TclInterpreter](#backlogops_gui.tcltk_version.TclInterpreter)
    * [call](#backlogops_gui.tcltk_version.TclInterpreter.call)
  * [TclTkRoot](#backlogops_gui.tcltk_version.TclTkRoot)
    * [tk](#backlogops_gui.tcltk_version.TclTkRoot.tk)
  * [\_parse\_tcltk\_version](#backlogops_gui.tcltk_version._parse_tcltk_version)
  * [\_old\_version\_warning](#backlogops_gui.tcltk_version._old_version_warning)
  * [\_bad\_version\_warning](#backlogops_gui.tcltk_version._bad_version_warning)
  * [warning\_for\_version](#backlogops_gui.tcltk_version.warning_for_version)
  * [check\_tcltk\_version](#backlogops_gui.tcltk_version.check_tcltk_version)

<a id="backlogops_gui.application"></a>

# backlogops\_gui.application

Tkinter placeholder application for backlog operations.

<a id="backlogops_gui.application.PackedWidget"></a>

## PackedWidget Objects

```python
class PackedWidget(Protocol)
```

Widget that can be placed in the Tkinter layout.

<a id="backlogops_gui.application.PackedWidget.pack"></a>

#### pack

```python
def pack(*args: Any, **pack_options: Any) -> None
```

Place the widget in its parent container.

<a id="backlogops_gui.application.TkWindow"></a>

## TkWindow Objects

```python
class TkWindow(TclTkRoot, Protocol)
```

Small part of the Tk root window API used by the app.

<a id="backlogops_gui.application.TkWindow.title"></a>

#### title

```python
def title(text: str) -> None
```

Set the title of the window.

<a id="backlogops_gui.application.TkWindow.quit"></a>

#### quit

```python
def quit() -> None
```

Request that the Tkinter main loop exits.

<a id="backlogops_gui.application.TkWindow.mainloop"></a>

#### mainloop

```python
def mainloop() -> None
```

Run the Tkinter event loop.

<a id="backlogops_gui.application.RootMaker"></a>

## RootMaker Objects

```python
class RootMaker(Protocol)
```

Callable that creates the main window root.

<a id="backlogops_gui.application.RootMaker.__call__"></a>

#### \_\_call\_\_

```python
def __call__() -> TkWindow
```

Return the main window root.

<a id="backlogops_gui.application.LabelMaker"></a>

## LabelMaker Objects

```python
class LabelMaker(Protocol)
```

Callable that creates a label widget.

<a id="backlogops_gui.application.LabelMaker.__call__"></a>

#### \_\_call\_\_

```python
def __call__(master: TkWindow, text: str, wraplength: int,
             justify: Literal['center', 'left']) -> PackedWidget
```

Return a label widget.

<a id="backlogops_gui.application.ButtonMaker"></a>

## ButtonMaker Objects

```python
class ButtonMaker(Protocol)
```

Callable that creates a button widget.

<a id="backlogops_gui.application.ButtonMaker.__call__"></a>

#### \_\_call\_\_

```python
def __call__(master: TkWindow, text: str,
             command: Callable[[], None]) -> PackedWidget
```

Return a button widget.

<a id="backlogops_gui.application._make_root"></a>

#### \_make\_root

```python
def _make_root() -> TkWindow
```

Create the Tkinter root window.

<a id="backlogops_gui.application._make_label"></a>

#### \_make\_label

```python
def _make_label(master: TkWindow, text: str, wraplength: int,
                justify: Literal['center', 'left']) -> PackedWidget
```

Create a Tkinter label widget.

<a id="backlogops_gui.application._make_button"></a>

#### \_make\_button

```python
def _make_button(master: TkWindow, text: str,
                 command: Callable[[], None]) -> PackedWidget
```

Create a Tkinter button widget.

<a id="backlogops_gui.application._add_label"></a>

#### \_add\_label

```python
def _add_label(root: TkWindow, text: str, label_maker: LabelMaker,
               justify: Literal['center', 'left']) -> None
```

Add one text label to the main window.

<a id="backlogops_gui.application._add_quit_button"></a>

#### \_add\_quit\_button

```python
def _add_quit_button(root: TkWindow, button_maker: ButtonMaker) -> None
```

Add the quit button to the main window.

<a id="backlogops_gui.application.build_main_window"></a>

#### build\_main\_window

```python
def build_main_window(root: TkWindow,
                      label_maker: Optional[LabelMaker] = None,
                      button_maker: Optional[ButtonMaker] = None) -> None
```

Build the placeholder widgets in the main window.

<a id="backlogops_gui.application.main"></a>

#### main

```python
def main(root_maker: Optional[RootMaker] = None,
         label_maker: Optional[LabelMaker] = None,
         button_maker: Optional[ButtonMaker] = None) -> None
```

Start the backlog operations GUI.

<a id="backlogops_gui.tcltk_version"></a>

# backlogops\_gui.tcltk\_version

Tcl/Tk version checks for the backlog operations GUI.

<a id="backlogops_gui.tcltk_version.TclInterpreter"></a>

## TclInterpreter Objects

```python
@runtime_checkable
class TclInterpreter(Protocol)
```

Small part of the Tcl interpreter API used by the GUI.

<a id="backlogops_gui.tcltk_version.TclInterpreter.call"></a>

#### call

```python
def call(*args: object) -> object
```

Call the Tcl interpreter and return the Tcl result.

<a id="backlogops_gui.tcltk_version.TclTkRoot"></a>

## TclTkRoot Objects

```python
class TclTkRoot(Protocol)
```

Root object exposing the Tcl interpreter used by Tkinter.

<a id="backlogops_gui.tcltk_version.TclTkRoot.tk"></a>

#### tk

```python
@property
def tk() -> object
```

Return the Tcl interpreter object.

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
def check_tcltk_version(root: TclTkRoot) -> Optional[str]
```

Return a warning if the running Tcl/Tk version may be unsuitable.

