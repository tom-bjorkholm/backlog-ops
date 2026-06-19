#! /usr/local/bin/python3
"""Print version information for the backlogops_cli package."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from backlogops_cli.bloc_version_reporter import BloCliVersionReporter

DESCRIPTION = 'Print version information for the backlogops_cli package'


def main() -> None:
    """Print version information for the backlogops_cli package."""
    vers = BloCliVersionReporter()
    vers.check_if_unsupported_python()
    vers.print()


if __name__ == '__main__':  # pragma: no cover
    main()
