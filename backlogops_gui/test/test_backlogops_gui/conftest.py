#! /usr/bin/env python3
"""Pytest configuration for backlogops_gui tests."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import gc
from typing import Iterator
import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom pytest markers for backlogops_gui tests."""
    config.addinivalue_line(
        'markers',
        'focus_sensitive: test requires a focused window and unlocked '
        'display; run manually under controlled conditions')


@pytest.fixture(autouse=True, scope='module')
def collect_tk_garbage() -> Iterator[None]:
    """Free what the tests leave in reference cycles, on the main thread.

    A Tk variable held in a reference cycle, such as the status line of
    an application whose widgets call back into it, is freed only by the
    cyclic garbage collector, which runs in whichever thread happens to
    allocate. Freed in another thread, such as a stream pump thread of
    GitPython in a later test, the finalizer of the variable calls Tcl
    from the wrong thread and fails with "main thread is not in main
    loop". Collecting after each test module frees it here, in the
    thread that created it. The GUI tests start no threads of their own,
    so once per module is enough, and it costs far less than once per
    test.
    """
    yield
    gc.collect()
