#! /usr/local/bin/python3
"""Tests for what the application reads from the loaded configuration.

Each accessor returns a part of the loaded configuration, or a fallback
when no configuration is loaded.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from backlogops import GuiDisplayConfig
from .app_test_helpers import FakeConfig, make_app as _app


def test_presets_from_config() -> None:
    """Test the presets come from the current configuration."""
    config = FakeConfig()
    app = _app(config)
    assert app.in_presets() == config.input_configs
    assert app.out_presets() == config.output_configs


def test_no_cfg_no_presets() -> None:
    """Test there are no presets when no configuration is loaded."""
    app = _app()
    assert app.in_presets() is None
    assert app.out_presets() is None


def test_available_teams() -> None:
    """Test the available teams come from the loaded configuration."""
    config = FakeConfig()
    assert _app(config).available_teams() is config.available_teams
    assert _app().available_teams() is None


def test_levels_from_config() -> None:
    """Test the levels come from the loaded configuration, or None."""
    config = FakeConfig()
    assert _app(config).levels() == config.get_levels()
    assert _app().levels() is None


def test_def_points() -> None:
    """Test the unestimated-item guess comes from the config, or None."""
    config = FakeConfig()
    assert _app(config).def_points() is config.default_story_points
    assert _app().def_points() is None


def test_rt_config() -> None:
    """Test the remaining time configuration comes from the config."""
    config = FakeConfig()
    assert _app(config).rt_config() is config.remaining_time
    assert _app().rt_config() is None


def test_gui_display_none() -> None:
    """Test the GUI display falls back to a fresh default with no config."""
    assert isinstance(_app().gui_display(), GuiDisplayConfig)


def test_gui_display_cfg() -> None:
    """Test the GUI display comes from the loaded configuration."""
    config = FakeConfig()
    assert _app(config).gui_display() is config.gui_display
