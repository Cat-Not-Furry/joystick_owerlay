"""Win32: maps importable sin evdev; map_keys firma de 5 argumentos."""

from __future__ import annotations

import inspect
import os
import sys

import pytest

ENGINE_ROOT = os.path.join(os.path.dirname(__file__), "..", "arcade", "engine")
if ENGINE_ROOT not in sys.path:
	sys.path.insert(0, ENGINE_ROOT)

from maps.keymapper import map_keys  # noqa: E402


def test_map_keys_signature_requires_profile_and_format():
	sig = inspect.signature(map_keys)
	params = list(sig.parameters.keys())
	assert params[:5] == ["screen", "button_count", "profile_id", "format_key", "input_mode"]


@pytest.mark.skipif(os.name != "nt", reason="política import Win32")
def test_joystick_mapper_import_without_evdev():
	import importlib

	jm = importlib.import_module("maps.joystick_mapper")
	assert not hasattr(jm, "InputDevice") or os.name != "nt"
