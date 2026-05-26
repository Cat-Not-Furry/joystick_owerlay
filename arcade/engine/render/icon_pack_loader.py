"""Carga metadatos opcionales de icon pack (sin interpretar input)."""

import json
import os

from config import DEFAULT_ICON_PACK, ICON_PACKS_DIR


def load_pack_meta(icon_pack):
	"""Lee icon_packs/<pack>/pack.json si existe; retorna dict o {}."""
	pack_id = str(icon_pack or DEFAULT_ICON_PACK).strip() or DEFAULT_ICON_PACK
	path = os.path.join(ICON_PACKS_DIR, pack_id, "pack.json")
	if not os.path.isfile(path):
		return {}
	try:
		with open(path, "r", encoding="utf-8") as f:
			data = json.loads(f.read().strip() or "{}")
		return data if isinstance(data, dict) else {}
	except Exception:
		return {}
