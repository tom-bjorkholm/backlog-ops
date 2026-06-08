"""Pytest configuration for custom build tools tests."""

from pathlib import Path
import sys

COMMON_SRC = Path(__file__).resolve().parents[2] / 'common_build_tools' / 'src'
CUSTOM_SRC = Path(__file__).resolve().parents[1] / 'src'
if str(COMMON_SRC) not in sys.path:
    sys.path.insert(0, str(COMMON_SRC))
if str(CUSTOM_SRC) not in sys.path:
    sys.path.insert(0, str(CUSTOM_SRC))
