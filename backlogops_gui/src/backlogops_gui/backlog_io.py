#! /usr/local/bin/python3
"""Read and write a backlog and releases with format options.

These helpers wrap the library read and write functions and resolve the
format the same way the command line does: an empty value infers the
format from the file name, a value of only letters and digits is a preset
name looked up in the presets from the teams configuration, and any other
value is the path of a stand-alone format configuration file. Diagnostics
go to the given sink, because a graphical application shows them in a log
view rather than on a console.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional, TextIO
from backlogops import (
    BacklogReleases, FormatRules, InputFormatConfig, Levels,
    OutputFormatConfig, NoTextIO, Status, allow_overwrite,
    read_backlog_releases, write_backlog_releases, resolve_input_config,
    resolve_output_config)
from backlogops_gui._migrate_warn import GuiMigrateWarnHook


def _sink(sink: Optional[TextIO]) -> TextIO:
    """Return the given diagnostics sink, or a discarding one."""
    return sink if sink is not None else NoTextIO()


def read_backlog(path: str, value: Optional[str],
                 presets: Optional[dict[str, InputFormatConfig]],
                 sink: Optional[TextIO] = None,
                 levels: Optional[Levels] = None,
                 status_map: Optional[dict[str, Status]] = None
                 ) -> BacklogReleases:
    """Read and validate a backlog and releases from one file.

    Args:
        path: The data file to read.
        value: The format selection, as documented for the module.
        presets: Named input presets, or None when none are configured.
        sink: Stream for diagnostics, or None to discard them.
        levels: The backlog item levels to honour, or None for the
            default levels.
        status_map: The library-wide status input map, or None when absent.
            The resolved input configuration's own status map overrides it
            per name.

    Returns:
        The validated backlog and releases read from the file.
    """
    out = _sink(sink)
    config = resolve_input_config(value, data_file=path, presets=presets,
                                  auto_ch_hook=GuiMigrateWarnHook(),
                                  stderr_file=out)
    data = read_backlog_releases(path, config, levels, status_map, out)
    data.check_consistency(out)
    return data


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def write_backlog(data: BacklogReleases, path: str, value: Optional[str],
                  presets: Optional[dict[str, OutputFormatConfig]],
                  releases_first: bool, sink: Optional[TextIO] = None,
                  levels: Optional[Levels] = None) -> None:
    """Write a backlog and releases to one file.

    Args:
        data: The backlog and releases to write.
        path: The data file to create.
        value: The format selection, as documented for the module.
        presets: Named output presets, or None when none are configured.
        releases_first: Whether to write the releases before the backlog.
        sink: Stream for diagnostics, or None to discard them.
        levels: The levels used to write level names, or None for the
            default levels.
    """
    out = _sink(sink)
    config = resolve_output_config(value, data_file=path, presets=presets,
                                   auto_ch_hook=GuiMigrateWarnHook(),
                                   stderr_file=out)
    rules = FormatRules(backlog_first=not releases_first)
    write_backlog_releases(data, path, config, rules, levels=levels,
                           stderr_file=out,
                           file_exists_callback=allow_overwrite)
