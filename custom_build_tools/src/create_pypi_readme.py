#! /usr/local/bin/python3
"""Create the base/README_pypi.md and extend/README_pypi.md files."""

# Copyright (c) 2025 - 2026 Tom Björkholm
# MIT License
#

from enum import IntEnum, auto
from typing import NamedTuple, TypedDict, Optional
from pathlib import Path
import sys
from mformat.factory import create_mf, OptArgsDict
from mformat.mformat import MultiFormat
try:
    from build_spec import BuildSpec, BuildInformation
except ImportError:
    pass

class ReadmeType(IntEnum):
    """Type of README file."""

    BACKLOGOPS_API = auto()
    BACKLOGOPS_CLI = auto()
    BACKLOGOPS_GUI = auto()


class Paths(NamedTuple):
    """Paths to the destination README_pypi.md file and version files."""

    readme: Path
    setup: Path
    pyproject: Path


class PathsForPackages(TypedDict):
    """Paths for all packages."""

    backlogops_api: Paths
    backlogops_cli: Paths
    backlogops_gui: Paths


def get_paths() -> PathsForPackages:
    """Return the paths for all packages."""
    project_root = Path(__file__).resolve().parents[2]
    backlogops_api_dir = project_root / 'backlogops'
    backlogops_cli_dir = project_root / 'backlogops_cli'
    backlogops_gui_dir = project_root / 'backlogops_gui'
    api_paths = Paths(readme=backlogops_api_dir / 'README_pypi.md',
                      setup=backlogops_api_dir / 'setup.py',
                      pyproject=backlogops_api_dir / 'pyproject.toml')
    cli_paths = Paths(readme=backlogops_cli_dir / 'README_pypi.md',
                      setup=backlogops_cli_dir / 'setup.py',
                      pyproject=backlogops_cli_dir / 'pyproject.toml')
    gui_paths = Paths(readme=backlogops_gui_dir / 'README_pypi.md',
                      setup=backlogops_gui_dir / 'setup.py',
                      pyproject=backlogops_gui_dir / 'pyproject.toml')
    return {
        'backlogops_api': api_paths,
        'backlogops_cli': cli_paths,
        'backlogops_gui': gui_paths
    }


def file_exists_callback(file_name: str) -> None:
    """Allow the file to be overwritten."""
    _ = file_name


TITLES: dict[ReadmeType, str] = {
    ReadmeType.BACKLOGOPS_API: 'backlogpps',
    ReadmeType.BACKLOGOPS_CLI: 'backlogops-cli',
    ReadmeType.BACKLOGOPS_GUI: 'backlogops-gui'
}

P1 = 'There are 3 related packages for backlog operations:'
B1 = [
    'backlogops: a collection of library functions to manipulate backlogs',
    'backlogops-cli: command line interface to use the functions in the '
    'library',
    'backlogops-gui: graphical user interface to use the functions in '
    'the library',
]


def _write_installing(mft: MultiFormat, readme_type: ReadmeType) -> None:
    """Write the installing section."""
    mft.new_heading(level=2, text=f'Installing {TITLES[readme_type]}')
    mft.new_heading(level=3, text='On macOS and Linux')
    mft.new_paragraph(text=f'To install {TITLES[readme_type]}')
    mft.add_text(text='on macOS and Linux, run the following command:')
    mft.write_code_block(text=f'pip3 install --upgrade {TITLES[readme_type]}',
                         programming_language='sh')
    mft.new_heading(level=3, text='On Microsoft Windows')
    mft.new_paragraph(text=f'To install {TITLES[readme_type]}')
    mft.add_text(text='on Microsoft Windows, run the following command:')
    mft.write_code_block(text=f'pip install --upgrade {TITLES[readme_type]}',
                         programming_language='sh')


def create_pypi_readme(readme_type: ReadmeType, path: Path) -> None:
    """Create the README_pypi.md file."""
    args: OptArgsDict = {'file_exists_callback': file_exists_callback}
    with create_mf(format_name='md', file_name=str(path), args=args) as mft:
        mft.new_heading(level=1, text=f'{TITLES[readme_type]}')
        mft.new_paragraph(text=P1)
        for item in B1:
            mft.new_bullet_item(text=item)
        _write_installing(mft, readme_type)
        mft.new_heading(level=2, text='Test summary')
    print(f'Created {str(path)} file for {readme_type.name}', file=sys.stderr)


def get_version_in_file(path: Path) -> str:
    """Get the version from the pyproject.toml or setup.py file."""
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            lline = line.strip()
            if lline.startswith('version =') or lline.startswith('version='):
                word2 = lline.split('=')[1]
                word3 = word2.strip(' \t\n\r"\',')
                return word3
    return ''


def check_version(paths: PathsForPackages) -> None:
    """Check that the version information is consistent between the files."""
    versions: list[str] = []
    for key, path in paths.items():
        assert key in ['backlogops_api', 'backlogops_cli', 'backlogops_gui']
        assert isinstance(path, Paths)
        versions.append(get_version_in_file(path.pyproject))
    if len(versions) != 3:
        print(f'Expected 3 versions, got {len(versions)}', file=sys.stderr)
        sys.exit(1)
    for i in versions[1:]:
        if i != versions[0]:
            print(f'Versions are not consistent: {versions[0]} and {i}',
                  file=sys.stderr)
            sys.exit(1)


def create_pypi_readme_cmd(build_spec: Optional[BuildSpec] = None,
                           build_information: Optional[BuildInformation]
                           = None) -> None:
    """Create the README_pypi.md files for the base and extend packages."""
    _ = build_spec
    _ = build_information
    pkg_paths: PathsForPackages = get_paths()
    check_version(pkg_paths)
    create_pypi_readme(ReadmeType.BACKLOGOPS_API,
                       pkg_paths['backlogops_api'].readme)
    create_pypi_readme(ReadmeType.BACKLOGOPS_CLI,
                       pkg_paths['backlogops_cli'].readme)
    create_pypi_readme(ReadmeType.BACKLOGOPS_GUI,
                       pkg_paths['backlogops_gui'].readme)


if __name__ == "__main__":
    create_pypi_readme_cmd()
