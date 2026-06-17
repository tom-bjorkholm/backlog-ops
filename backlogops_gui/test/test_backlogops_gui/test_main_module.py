#! /usr/local/bin/python3
"""Tests for the backlogops_gui __main__ entry point module."""

# Copyright (c) 2026, Tom Björkholm
# MIT License

import importlib


def test_main_module_imports() -> None:
    """Test the entry-point module imports and exposes main."""
    module = importlib.import_module('backlogops_gui.__main__')
    assert callable(module.main)
