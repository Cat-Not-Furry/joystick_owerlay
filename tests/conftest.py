"""Configuración pytest: sys.path para arcade/engine y raíz del clon."""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENGINE = os.path.join(ROOT, "arcade", "engine")
for path in (ROOT, ENGINE):
	if path not in sys.path:
		sys.path.insert(0, path)
