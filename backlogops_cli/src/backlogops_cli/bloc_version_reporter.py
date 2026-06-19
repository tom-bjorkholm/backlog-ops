#! /usr/local/bin/python3
"""Version reporter for the backlogops_cli package."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import override
from backlogops.blo_version_reporter import BloVersionReporter


class BloCliVersionReporter(BloVersionReporter):
    """Version reporter for the backlogops_cli package."""

    @override
    def package_names(self) -> list[str]:
        """Return the package names that this package reports."""
        ret = ['backlogops-cli']
        ret += super().package_names()
        return ret

    @override
    @classmethod
    def get_main_package_name(cls) -> str:
        """Return the name of the main package."""
        return 'backlogops-cli'
