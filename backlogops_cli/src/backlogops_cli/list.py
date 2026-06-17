#! /usr/local/bin/python3
"""List the commands available in backlogops_cli."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import os
import pkgutil
import importlib
from types import ModuleType
import backlogops_cli

DESCRIPTION = 'List all commands available in backlogops_cli'


def _python_prefix() -> str:
    """Return the 'python -m' prefix matching the running OS."""
    runner = 'python' if os.name == 'nt' else 'python3'
    return f'{runner} -m'


def _is_command(module: ModuleType) -> bool:
    """Tell whether a module is a usable backlogops_cli command."""
    has_main = callable(getattr(module, 'main', None))
    description = getattr(module, 'DESCRIPTION', None)
    return has_main and isinstance(description, str)


def command_modules() -> list[tuple[str, ModuleType]]:
    """Return sorted (name, module) pairs for all command modules."""
    found: list[tuple[str, ModuleType]] = []
    for info in pkgutil.iter_modules(backlogops_cli.__path__):
        if info.ispkg or info.name.startswith('_'):
            continue
        module = importlib.import_module(f'backlogops_cli.{info.name}')
        if _is_command(module):
            found.append((info.name, module))
    found.sort(key=lambda item: item[0])
    return found


def _description_lines(description: str) -> list[str]:
    """Return the description as indented lines, one per text line."""
    return [f'     {line}' for line in description.splitlines()]


def format_listing(commands: list[tuple[str, ModuleType]]) -> str:
    """Format the command listing for printing to the user."""
    prefix = _python_prefix()
    lines: list[str] = []
    for name, module in commands:
        lines.append(f'  {prefix} backlogops_cli.{name}')
        lines.extend(_description_lines(module.DESCRIPTION))
    return '\n'.join(lines)


def main() -> None:
    """Print the list of available backlogops_cli commands."""
    print(format_listing(command_modules()))


if __name__ == '__main__':  # pragma: no cover
    main()
