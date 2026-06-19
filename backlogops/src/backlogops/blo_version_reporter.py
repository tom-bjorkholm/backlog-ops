#! /usr/local/bin/python3
"""Version reporter for the backlogops package."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from datetime import date
from typing import override
from packaging.version import Version
from versionreporter import VersionReporter


class BloVersionReporter(VersionReporter):
    """Version reporter for the backlogops package."""

    @override
    def package_names(self) -> list[str]:
        """Return the package names that this package reports."""
        ret = ['backlogops', 'tableio', 'tableio-cfg-json', 'config-as-json',
               'mformat']
        ret += super().package_names()
        return ret

    @override
    def get_app_support_expires(self) -> dict[date, str]:
        """Return when this package will stop supporting older Python."""
        return {date(year=2026, month=1, day=1): '3.11',
                date(year=2027, month=10, day=1): '3.12'}

    @override
    @classmethod
    def get_main_package_name(cls) -> str:
        """Return the package treated as the main application package."""
        return 'backlogops'

    @override
    @classmethod
    def recommended_python(cls) -> Version:
        """Return the Python version this package recommends."""
        return Version('3.14')
