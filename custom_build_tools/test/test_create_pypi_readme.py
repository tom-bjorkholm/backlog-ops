"""Tests for custom_build_tools.src.create_pypi_readme."""

from pathlib import Path
import subprocess

import pytest

from build_spec import BuildInformation
import create_pypi_readme
import create_pypi_readme_venv


def _build_information(project_root: Path) -> BuildInformation:
    """Return build information with only project root populated."""
    return BuildInformation(project_root=project_root, package_information=[],
                            package_install_order=[], flake8_folders=[],
                            pylint_folders=[], mypy_folders=[],
                            pytest_folders=[], mypy_path_folders=[])


def test_runs_venv_python(monkeypatch: pytest.MonkeyPatch,
                          tmp_path: Path) -> None:
    """Test build hook delegates README generation to venv Python."""
    calls: list[tuple[list[str], bool, Path]] = []

    def fake_run(command: list[str], check: bool, cwd: Path) -> None:
        """Store subprocess.run call arguments for assertions."""
        calls.append((command, check, cwd))

    monkeypatch.setattr(subprocess, 'run', fake_run)
    create_pypi_readme.create_pypi_readme_cmd(
        build_information=_build_information(tmp_path))
    assert calls == [(
        [
            str(tmp_path / 'venv' / 'bin' / 'python'),
            str(create_pypi_readme.get_generator_path())
        ],
        True,
        tmp_path
    )]


def test_uses_windows_python(tmp_path: Path) -> None:
    """Test Windows venv Python path is used when present."""
    python_path = tmp_path / 'venv' / 'Scripts' / 'python.exe'
    python_path.parent.mkdir(parents=True)
    python_path.touch()
    assert create_pypi_readme.get_venv_python(tmp_path) == python_path


def test_api_title() -> None:
    """Test API README title uses the package name."""
    assert create_pypi_readme_venv.TITLES[
        create_pypi_readme_venv.ReadmeType.BACKLOGOPS_API] == 'backlogops'
