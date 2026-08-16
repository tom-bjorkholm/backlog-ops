#! /usr/local/bin/python3
"""What a configuration editor of a UI is told about this application.

The wizard asks one question after another, which is what building a
configuration from nothing wants. Editing an existing one wants the other
shape: the whole configuration on the screen at once, folded where it is
deep, so a single value can be changed without walking past everything
else. ``edit_cfg_json`` is that editor, and this module is the two answers
it asks the application for, so that the command line and the graphical
interface show one configuration the same way.

The first answer is :func:`descriptions_for`, which is what each editable
class says about its own members. Which class is edited is the class of the
configuration object the editor is given, so the caller decides whether a
complete backlog-ops configuration or a stand-alone preset is being edited,
and the descriptions of that class follow from it. A caller that has a
class rather than an object, such as a command line naming the kind of file
it edits, gets the object from ``edit_cfg_json.default_config``.

The second answer is :data:`EDIT_SETTINGS`, which is what the editor may do
to a file. Saving is the editor's own: it validates the whole configuration
through the configuration class and only then writes, keeping what it wrote
over as a ``.bak`` file, because an editor overwrites the file it read.

Nothing here opens an editor. A user interface that already runs its own
toolkit mounts the editor itself — ``edit_cfg_json_tk.TkEditorPanel`` in a
window of the application, ``edit_cfg_json_textual.edit`` in a terminal of
its own — and hands those two answers to it.

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

from typing import Optional
from config_as_json import Config
from edit_cfg_json import Descriptions, Settings
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
