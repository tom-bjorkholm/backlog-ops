#! /usr/bin/env python3
"""Create package README_pypi.md files using mformat from the venv."""

# Copyright (c) 2025 - 2026 Tom Björkholm
# MIT License
#

from enum import IntEnum, auto
from pathlib import Path
import sys
from typing import NamedTuple, TypedDict

from mformat.factory import OptArgsDict, create_mf
from mformat.mformat import MultiFormat
from backlogops_cli import list as cli_list


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


TITLES: dict[ReadmeType, str] = {
    ReadmeType.BACKLOGOPS_API: 'backlogops',
    ReadmeType.BACKLOGOPS_CLI: 'backlogops-cli',
    ReadmeType.BACKLOGOPS_GUI: 'backlogops-gui'
}

P1 = 'There are 3 related packages for backlog operations:'
B1 = [
    'backlogops: a collection of library functions to manipulate backlogs',
    'backlogops-cli: command line interface to use the functions in the '
    'library. This is just a thin wrapper around the library functions. '
    'It serves a dual purpose as both an example of how to use the '
    'library and as a tool for the user to use the library.',
    'backlogops-gui: graphical user interface to use the functions in '
    'the library. It is based on TkInter. The ambition is to keep it '
    'as a thin wrapper around the library.'
]
P2 = 'The following functionality is available in all 3 packages:'
B2 = [
    'Reading backlog and releases from file types that TableIO supports '
    'reading from (Currently CSV, Excel, and ODS).',
    'Writing backlog and releases to file types that TableIO supports '
    'writing to (Currently CSV, Excel, ODS and 9 other file formats).',
    'File format is detected from the file extension, but may be overridden.',
    'Adjust release content to match fit the planned release dates.',
    'Create a demonstation backlog and releases (for exploring the features).',
    'Estimate ready date for the backlog items based on available teams, '
    'team velocity, vacation dates, periods with half time work, etc.',
    'Extract backlog keys at given backlog item levels.',
    'Reorder the backlog so that the dependencies are satisfied.',
    'Reordet the backlogs so that items identified by keys in a list '
    'comes first. If the key is at a higher level it will bring all '
    'all items it is a parent of in front of it (recursively).',
    'Set planned release dates from the estimated release dates.',
    'Calculate the release dates for from backlog items estimated '
    'ready dates, with a configurable buffer time.',
    'Validate the backlog and releases for consistency.',
    'A wizard to create an available teams configuration.'
]
P3 = 'The operating model that most of the functionality is designed for ' \
     'is that the teams work off a single backlog in the order of the ' \
     'backlog. The backlog items are ordered by priority and dependencies ' \
     'to allow the teams to work in the backlog order. ' \
     'Each backlog item and each release may have a planned ready date, ' \
     'that records what has been communicated to the customer. ' \
     'Each backlog item and each release may have an estimated ready date, ' \
     'that is calculated from the current backlog state, the team velocity, ' \
     'and what we know about the availability of the team members.'
P4 = 'Each backlog item has the following fields that are used by the ' \
     'algorithms in the library:'
B4 = ['key: The key of the backlog item. Required. Must be unique. '
      'Must not be empty, must not contain whitespace and must '
      'not contain any of the characters , . ; : ( ) [ ] { }.',
      'level: The level of the backlog item. Required. Must be an integer.',
      'title: The title of the backlog item. Required.',
      'story_points: The story points of the backlog item. Required.',
      'status: The status of the backlog item. Required.',
      'parent_key: The key of the parent backlog item. Optional. '
      'Must exist as a key in the backlog. '
      'Parent keys are used to build the hierarchy of the backlog. '
      'The parent key must be at a higher level than the current '
      'item. Parent keys introduce implicit dependencies between '
      'items: the current item cannot start before the parent '
      'item starts, and the parent item cannot finish before all '
      'its children have finished.',
      'release: The release of the backlog item. Optional. '
      'Follows the same character rules as the key. '
      'Must not be empty string.',
      'team: The team responsible for the backlog item. Optional. '
      'Must not be empty string. Must be a valid team name. '
      'If None the item can be done by any team. If not None. '
      'the item can only be done by the specified team.',
      'depends_on_f2s: The list of keys of the backlog items that must '
      'have been finished before the current item can start. May be empty.',
      'depends_on_f2f: The list of keys of the backlog items that must '
      'have been finished before the current item can finish. May be empty.',
      'depends_on_s2s: The list of keys of the backlog items that must '
      'have been started before the current item can start. May be empty.',
      'planned_ready_date: The planned ready date of the backlog item. '
      'The date that is communicated to the customer. Optional.',
      'estimated_ready_date: The estimated ready date of the backlog item. '
      'Optional.']
P5 = 'Additionally each backlog item can have any number of other fields.'


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


DOCS_ROOT = 'https://bitbucket.org/tom-bjorkholm/backlog-ops/src/master/doc/'
UL1 = DOCS_ROOT + 'backlogops_api.md'
UL2 = DOCS_ROOT + 'backlogops_protected_api.md'
UC1 = DOCS_ROOT + 'backlogops_cli.md'
UC2 = DOCS_ROOT + 'backlogops_protected_cli.md'
UG1 = DOCS_ROOT + 'backlogops_gui.md'
UG2 = DOCS_ROOT + 'backlogops_protected_gui.md'


def _write_api_docs(mft: MultiFormat) -> None:
    """Write the API docs section."""
    mft.new_heading(level=2, text='API documentation')
    mft.new_paragraph(text='For more detailed code documentation, '
                      'see the API documentation:')
    mft.new_bullet_item('')
    mft.add_url(url=UL1, text='Library public API')
    mft.new_bullet_item('')
    mft.add_url(url=UL2, text='Library protected API')
    mft.new_bullet_item('')
    mft.add_url(url=UC1, text='Library public CLI')
    mft.new_bullet_item('')
    mft.add_url(url=UC2, text='Library protected CLI')
    mft.new_bullet_item('')
    mft.add_url(url=UG1, text='Library public GUI')
    mft.new_bullet_item('')
    mft.add_url(url=UG2, text='Library protected GUI')


def _read_include(readme_path: Path) -> str:
    """Return include_pypi.md content from the README's folder."""
    include_path = readme_path.parent / 'include_pypi.md'
    return include_path.read_text(encoding='utf-8').strip()


def _list_command_output() -> str:
    """Return the backlogops_cli.list command listing as text."""
    return cli_list.format_listing(cli_list.command_modules())


def _format_code_block(text: str) -> str:
    """Format text as a markdown fenced code block (mformat style)."""
    return f'````text\n{text}\n````\n'


def _append_extra(readme_type: ReadmeType, readme_path: Path) -> None:
    """Append include content, optional list output and Test summary."""
    with open(readme_path, 'a', encoding='utf-8') as file:
        file.write(f'\n{_read_include(readme_path)}\n')
        if readme_type == ReadmeType.BACKLOGOPS_CLI:
            file.write(f'\n{_format_code_block(_list_command_output())}')
        file.write('\n## Test summary\n')


def create_pypi_readme(readme_type: ReadmeType, path: Path) -> None:
    """Create the README_pypi.md file."""
    args: OptArgsDict = {'file_exists_callback': file_exists_callback}
    with create_mf(format_name='md', file_name=str(path), args=args) as mft:
        mft.new_heading(level=1, text=f'{TITLES[readme_type]}')
        mft.new_paragraph(text=P1)
        for item in B1:
            mft.new_bullet_item(text=item)
        mft.new_heading(level=2, text='Available functionality')
        mft.new_paragraph(text=P2)
        for item in B2:
            mft.new_bullet_item(text=item)
        mft.new_heading(level=2, text='The operating model')
        mft.new_paragraph(text=P3)
        mft.new_heading(level=2, text='The backlog item fields')
        mft.new_paragraph(text=P4)
        for item in B4:
            mft.new_bullet_item(text=item)
        mft.new_paragraph(text=P5)
        _write_installing(mft, readme_type)
        _write_api_docs(mft)
    _append_extra(readme_type, path)
    print(f'Created {str(path)} file for {readme_type.name}', file=sys.stderr)


def get_version_in_file(path: Path) -> str:
    """Get the version from the pyproject.toml or setup.py file."""
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            lline = line.strip()
            if lline.startswith('version =') or lline.startswith('version='):
                word2 = lline.split('=')[1]
                return word2.strip(' \t\n\r"\',')
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
    for version in versions[1:]:
        if version != versions[0]:
            print(f'Versions are not consistent: {versions[0]} and {version}',
                  file=sys.stderr)
            sys.exit(1)


def create_pypi_readmes() -> None:
    """Create the README_pypi.md files for all packages."""
    pkg_paths: PathsForPackages = get_paths()
    check_version(pkg_paths)
    create_pypi_readme(ReadmeType.BACKLOGOPS_API,
                       pkg_paths['backlogops_api'].readme)
    create_pypi_readme(ReadmeType.BACKLOGOPS_CLI,
                       pkg_paths['backlogops_cli'].readme)
    create_pypi_readme(ReadmeType.BACKLOGOPS_GUI,
                       pkg_paths['backlogops_gui'].readme)


if __name__ == '__main__':
    create_pypi_readmes()
