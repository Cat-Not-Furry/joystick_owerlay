# utils/safe_paths.py — rutas bajo raíz permitida (anti path traversal)

from __future__ import annotations

import os
from pathlib import Path


def resolve_under_root(root: str | os.PathLike[str], rel_or_abs: str | os.PathLike[str]) -> str | None:
	"""
	Resuelve rel_or_abs bajo root canonico.

	- rel_or_abs relativo: join(root, ...) y resolve; debe quedar bajo root.
	- rel_or_abs absoluto: resolve; debe quedar bajo root.
	- Rechaza componentes .. en la cadena de entrada antes de resolver.
	"""
	if rel_or_abs is None:
		return None
	s = os.fsdecode(rel_or_abs).strip()
	if not s or s == ".":
		return None
	try:
		root_p = Path(root).resolve(strict=False)
	except OSError:
		return None
	parts = Path(s).parts
	if any(p == ".." for p in parts):
		return None
	if os.path.isabs(s):
		cand = Path(s).resolve(strict=False)
	else:
		cand = (root_p / s).resolve(strict=False)
	try:
		cand.relative_to(root_p)
	except ValueError:
		return None
	if cand.exists() and cand.is_file():
		return str(cand)
	return None


def path_is_under_root(root: str | os.PathLike[str], candidate: str | os.PathLike[str]) -> bool:
	"""True si candidate resuelto esta bajo root resuelto."""
	try:
		root_p = Path(root).resolve(strict=False)
		cand_p = Path(candidate).resolve(strict=False)
		cand_p.relative_to(root_p)
		return True
	except (ValueError, OSError):
		return False
