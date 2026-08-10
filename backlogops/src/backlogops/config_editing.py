#! /usr/local/bin/python3
"""Build the edit model that a configuration editor of a UI shows.

The wizard asks one question after another, which is what building a
configuration from nothing wants. Editing an existing one wants the other
shape: the whole configuration on the screen at once, folded where it is
deep, so a single value can be changed without walking past everything
else. ``edit_cfg_json`` is that editor, and this module is everything of it
that is not a widget, so that the command line and the graphical interface
show one configuration the same way.

:func:`edit_model_for` reads the input file and returns the model to show.
Which class is edited is the class of the configuration object it is given,
so the caller decides whether a complete backlog-ops configuration or a
stand-alone preset is being edited, and the descriptions of that class
follow from it. A caller that has a class rather than an object, such as a
command line naming the kind of file it edits, gets the object from
:func:`default_edit_config`.

What the editor may do to a file is :data:`EDIT_SETTINGS`. Saving is the
editor's own: it validates the whole configuration through the
configuration class and only then writes, keeping what it wrote over as a
``.bak`` file, because an editor overwrites the file it read.

Three things the editor cannot do are worth knowing before it is offered
instead of the wizard, and all three are of ``edit_cfg_json`` itself rather
than of this configuration:

* A dict whose keys the application validates for itself cannot gain or
  lose a key. That is the status map, the column-name maps of a preset and
  of the display, and the Jira column and issue-type maps: their values are
  editable, and a new entry is the wizard's to create.
* A member left out of the file has no row, so the levels can be edited
  only in a configuration that already states them.
* A person is keyed by their own name in lower case, so renaming one means
  adding an entry under the new key and removing the old one; editing the
  name alone leaves a configuration the class refuses.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import sys
from typing import Optional, TextIO
from config_as_json import Config, PathOrStr
from edit_cfg_json import ConfigLoadError, Descriptions, EditModel, Settings, \
    default_config, load_config
from backlogops.backlog_ops_config import BacklogOpsConfig
from backlogops.config_descriptions import CONFIG_DESCRIPTIONS, \
    INPUT_DESCRIPTIONS, OUTPUT_DESCRIPTIONS
from backlogops.config_file_io import CONFIG_EXTENSION
from backlogops.io_config import InputFormatConfig, OutputFormatConfig

EDIT_SETTINGS = Settings(file_extension=CONFIG_EXTENSION,
                         extension_enforced=False, backup_suffix='.bak',
                         backup_count=1, confirm_overwrite=True)
"""What the editor may do to a configuration file of this application.

The extension is added to a destination that has none, and a name with
another extension is accepted, which is how the wizard commands complete a
file name too. Overwriting a file this session has not written is confirmed
first and the previous content is then kept as that name plus ``.bak``,
because the editor writes over the file it read and that file may hold a
configuration somebody else wrote.

The default key combinations apply: none of them is taken by the
application around the editor.
"""

CLASS_DESCRIPTIONS: dict[type[Config], Descriptions] = {
    BacklogOpsConfig: CONFIG_DESCRIPTIONS,
    InputFormatConfig: INPUT_DESCRIPTIONS,
    OutputFormatConfig: OUTPUT_DESCRIPTIONS}
"""What each editable configuration class says about its own members."""


def descriptions_for(config: Config) -> Optional[Descriptions]:
    """Return what the class of one configuration says about its members.

    Args:
        config: The configuration object that is to be edited.

    Returns:
        The descriptions of that class, or None for a class this library
        says nothing about, which the editor shows without descriptions.
    """
    return CLASS_DESCRIPTIONS.get(type(config))


def default_edit_config(config_type: type[Config]) -> Config:
    """Return a configuration holding the declared defaults of one class.

    It is the door for a caller that has a class rather than an object,
    which is what a command line naming the kind of file it edits has.

    Args:
        config_type: The configuration class to be edited.

    Returns:
        A configuration object holding only what that class declares.

    Raises:
        ValueError: The editor cannot construct that class on its own.
    """
    try:
        return default_config(config_type)
    except ConfigLoadError as error:
        raise ValueError(str(error)) from error


def edit_model_for(config: Config, *, in_file: Optional[PathOrStr] = None,
                   out_file: Optional[PathOrStr] = None,
                   stderr_file: TextIO = sys.stderr) -> EditModel:
    """Read the configuration to edit and return the model of a session.

    The class of ``config`` decides which class is edited and supplies the
    values a member the input file leaves out falls back to. The object
    itself is never modified: what a save wrote is
    ``EditModel.saved_config``.

    Args:
        config: Configuration object of the class to edit, holding the
            values to start from when there is no input file.
        in_file: Configuration file to read, or None to edit the values
            that ``config`` holds.
        out_file: Configuration file a save writes, or None to write the
            input file. With neither, the editor asks the user for one
            before it can save. A destination named here is one this
            session chose, so it is given the configuration extension when
            it has none; the input file is inherited and taken as it is.
        stderr_file: Stream used for user-facing diagnostics.

    Returns:
        The model of one editing session, for a UI backend to show.

    Raises:
        ValueError: The input file cannot be opened for editing. The
            message holds what the configuration class said about it.
    """
    try:
        loaded = load_config(config, in_file=in_file, settings=EDIT_SETTINGS)
    except ConfigLoadError as error:
        raise ValueError(str(error)) from error
    model = EditModel(loaded.config, loaded.report,
                      descriptions=descriptions_for(config), out_file=in_file,
                      settings=EDIT_SETTINGS, stderr_file=stderr_file)
    if out_file is not None:
        model.set_out_file(out_file)
    return model
