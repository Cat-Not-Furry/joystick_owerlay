#!/usr/bin/env python3
"""
Comprueba enlaces relativos en ficheros .md del repositorio.
Uso: python scripts/check_doc_links.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "venv", ".venv", "tests/.tvenv", "__pycache__", "node_modules"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def iter_markdown_files(root: Path) -> list[Path]:
	out: list[Path] = []
	for p in root.rglob("*.md"):
		if any(part in SKIP_DIRS for part in p.parts):
			continue
		out.append(p)
	return sorted(out)


def resolve_link(md_path: Path, href: str, root: Path) -> Path | None:
	href = href.strip()
	if not href or href.startswith(("#", "http://", "https://", "mailto:")):
		return None
	if href.startswith("javascript:"):
		return None
	path_part = href.split("#", 1)[0]
	if not path_part or path_part.startswith("//"):
		return None
	target = (md_path.parent / path_part).resolve()
	try:
		target.relative_to(root)
	except ValueError:
		return None
	return target


def main() -> int:
	root = Path(__file__).resolve().parents[1]
	broken: list[tuple[Path, str, str]] = []
	for md in iter_markdown_files(root):
		text = md.read_text(encoding="utf-8", errors="replace")
		for m in LINK_RE.finditer(text):
			raw = m.group(1).strip()
			if raw.startswith("<") and raw.endswith(">"):
				raw = raw[1:-1].strip()
			target = resolve_link(md, raw, root)
			if target is None:
				continue
			if not target.exists():
				broken.append((md, raw, str(target.relative_to(root))))
	if not broken:
		print("check_doc_links: OK (sin enlaces relativos rotos en .md)")
		return 0
	print("check_doc_links: enlaces rotos\n", file=sys.stderr)
	for src, href, resolved in broken:
		print(f"  {src.relative_to(root)}  ->  {href!r}  (esperado: {resolved})", file=sys.stderr)
	return 1


if __name__ == "__main__":
	sys.exit(main())
