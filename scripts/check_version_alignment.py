#!/usr/bin/env python3
"""REL-001: .joystick_version debe coincidir con pyproject.toml."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read_joystick_version() -> str:
	path = ROOT / ".joystick_version"
	return path.read_text(encoding="utf-8").strip()


def _read_pyproject_version() -> str:
	text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
	match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
	if not match:
		raise ValueError("no se encontro version en pyproject.toml")
	return match.group(1).strip()


def main() -> int:
	try:
		jv = _read_joystick_version()
		pv = _read_pyproject_version()
	except Exception as exc:
		print(f"ERROR: {exc}")
		return 1
	if jv != pv:
		print(f"ERROR: version drift .joystick_version={jv!r} pyproject.toml={pv!r}")
		return 1
	print(f"OK: version alineada ({jv})")
	return 0


if __name__ == "__main__":
	sys.exit(main())
