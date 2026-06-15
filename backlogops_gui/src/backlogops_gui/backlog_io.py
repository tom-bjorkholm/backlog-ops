#! /usr/local/bin/python3
"""Read and write a backlog and releases with format options.

These helpers wrap the library read and write functions and resolve the
format the same way the command line does: an empty value infers the
format from the file name, a value of only letters and digits is a preset
name looked up in the presets from the teams configuration, and any other
value is the path of a stand-alone format configuration file. Diagnostics
go to a sink, because a graphical application reports failures as dialogs.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Optional
from backlogops import (
    BacklogReleases, InputFormatConfig, OutputFormatConfig, NoTextIO,
    read_backlog_releases, write_backlog_releases, resolve_input_config,
    resolve_output_config)


def read_backlog(path: str, value: Optional[str],
                 presets: Optional[dict[str, InputFormatConfig]]
                 ) -> BacklogReleases:
    """Read and validate a backlog and releases from one file.

    Args:
        path: The data file to read.
        value: The format selection, as documented for the module.
        presets: Named input presets, or None when none are configured.

    Returns:
        The validated backlog and releases read from the file.
    """
    sink = NoTextIO()
    config = resolve_input_config(value, data_file=path, presets=presets,
                                  stderr_file=sink)
    data = read_backlog_releases(path, config, None, sink)
    data.check_consistency(sink)
    return data


def write_backlog(data: BacklogReleases, path: str, value: Optional[str],
                  presets: Optional[dict[str, OutputFormatConfig]],
                  releases_first: bool) -> None:
    """Write a backlog and releases to one file.

    Args:
        data: The backlog and releases to write.
        path: The data file to create.
        value: The format selection, as documented for the module.
        presets: Named output presets, or None when none are configured.
        releases_first: Whether to write the releases before the backlog.
    """
    sink = NoTextIO()
    config = resolve_output_config(value, data_file=path, presets=presets,
                                   stderr_file=sink)
    write_backlog_releases(data, path, config,
                           backlog_first=not releases_first, stderr_file=sink)
