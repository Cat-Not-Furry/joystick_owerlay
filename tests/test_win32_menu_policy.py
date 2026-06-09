"""Win32: menú config no expone opciones WM tiling."""

from __future__ import annotations

import os
import sys

import pytest

ENGINE_ROOT = os.path.join(os.path.dirname(__file__), "..", "arcade", "engine")
if ENGINE_ROOT not in sys.path:
	sys.path.insert(0, ENGINE_ROOT)

from render.profile_config_menu import ProfileConfigMenu, _SECTION_KEYS, _OPTION_HANDLERS  # noqa: E402


@pytest.mark.skipif(os.name != "nt", reason="política Win32")
def test_section_keys_exclude_wm_options():
	for keys in _SECTION_KEYS.values():
		assert "window_mode" not in keys
		assert "ignore_videoresize" not in keys


@pytest.mark.skipif(os.name != "nt", reason="política Win32")
def test_table_cells_exclude_wm_options():
	for row in ProfileConfigMenu.TABLE_CELLS:
		for key in row:
			assert key not in ("window_mode", "ignore_videoresize")


@pytest.mark.skipif(os.name != "nt", reason="política Win32")
def test_option_handlers_exclude_wm():
	assert "window_mode" not in _OPTION_HANDLERS
	assert "ignore_videoresize" not in _OPTION_HANDLERS


def test_section_keys_exclude_wm_on_linux_ci():
	"""En CI (Linux) validamos la misma política del repo Windows."""
	for keys in _SECTION_KEYS.values():
		assert "window_mode" not in keys
		assert "ignore_videoresize" not in keys
