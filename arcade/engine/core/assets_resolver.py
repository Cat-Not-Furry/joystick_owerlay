import json
import os
from copy import deepcopy
from pathlib import Path

from config import (
	ASSETS_DIR,
	DEFAULT_ICON_PACK,
	ICON_PACKS_DIR,
	PROFILES_DIR,
	PROJECT_ROOT,
	USER_DIR,
	get_button_labels,
	icon_stem_for_label,
)
from profiles.bindings_storage import augment_profile_dict_with_bindings_sidecar
from profiles.semantic_resolver import resolve_semantic_for_physical
from utils.safe_paths import resolve_under_root


_META_CACHE = {}
_PATH_CACHE = {}


def clear_cache():
	_META_CACHE.clear()
	_PATH_CACHE.clear()


def invalidate_profile_cache(profile_name=None):
	if profile_name is None:
		clear_cache()
		return
	key = str(profile_name)
	_META_CACHE.pop(key, None)
	keys_to_drop = [k for k in _PATH_CACHE if k[0] == key]
	for k in keys_to_drop:
		_PATH_CACHE.pop(k, None)


def _profile_dir(profile_name):
	return os.path.join(PROFILES_DIR, str(profile_name))


def _profile_json_path(profile_name):
	return os.path.join(_profile_dir(profile_name), "profile.json")


def _load_profile_meta(profile_name):
	"""Lee profile.json una vez por perfil hasta invalidación."""
	key = str(profile_name)
	if key in _META_CACHE:
		return _META_CACHE[key]
	path = _profile_json_path(profile_name)
	if not os.path.exists(path):
		_META_CACHE[key] = {}
		return _META_CACHE[key]
	try:
		with open(path, "r", encoding="utf-8") as file:
			data = json.loads(file.read().strip() or "{}")
	except Exception:
		data = {}
	if not isinstance(data, dict):
		data = {}
	augment_profile_dict_with_bindings_sidecar(data)
	_META_CACHE[key] = data
	return data


def _button_file_candidates_from_stem(stem):
	st = str(stem).strip().lower()
	return [f"{st}.png"]


def _normalize_icon_pack_id(icon_pack):
	name = str(icon_pack or "").strip()
	if not name or ".." in name or "/" in name or "\\" in name:
		return DEFAULT_ICON_PACK
	btn = os.path.join(ICON_PACKS_DIR, name, "buttons")
	return name if os.path.isdir(btn) else DEFAULT_ICON_PACK


def _resolve_pack_stem_path(icon_pack, stem):
	pack = _normalize_icon_pack_id(icon_pack)
	for candidate in _button_file_candidates_from_stem(stem):
		path = os.path.join(ICON_PACKS_DIR, pack, "buttons", candidate)
		if os.path.isfile(path) and not os.path.islink(path):
			return path
	return None


def _resolve_default_pack_stem(stem):
	return _resolve_pack_stem_path(DEFAULT_ICON_PACK, stem)


def _profile_button_count(profile, button_count_fallback):
	try:
		return int(profile.get("button_count", button_count_fallback) or button_count_fallback)
	except Exception:
		return button_count_fallback


def _resolve_icon_path_loaded(profile, profile_name, button, bc):
	"""
	Ruta de PNG para un slot semántico usando un dict de perfil ya cargado.
	profile_name: id de perfil (carpeta bajo PROFILES_DIR) para rutas relativas.
	"""
	button_name = str(button).strip().lower()
	label_upper = str(button).strip().upper()
	overrides = profile.get("button_icons", {})
	if not isinstance(overrides, dict):
		overrides = {}
	override_value = overrides.get(label_upper) or overrides.get(button_name)
	if isinstance(override_value, str) and override_value.strip():
		override_path = override_value.strip()
		prof_root = _profile_dir(profile_name)
		resolved = resolve_under_root(prof_root, override_path)
		if resolved:
			return resolved
		if os.path.isabs(override_path):
			try:
				ap = Path(override_path).resolve(strict=False)
			except OSError:
				ap = None
			if ap is not None and ap.is_file() and not ap.is_symlink():
				for base_str in (USER_DIR, ASSETS_DIR):
					try:
						ap.relative_to(Path(base_str).resolve(strict=False))
						return str(ap)
					except ValueError:
						continue

	icon_pack = _normalize_icon_pack_id(profile.get("icon_pack", DEFAULT_ICON_PACK))
	stem = icon_stem_for_label(icon_pack, label_upper, bc)
	path = _resolve_pack_stem_path(icon_pack, stem)
	if path:
		return path
	path = _resolve_default_pack_stem(icon_stem_for_label(DEFAULT_ICON_PACK, label_upper, bc))
	if path:
		return path
	return None


def resolve_icon(profile_name, button, button_count=6):
	"""
	Resuelve ruta de icono. Sin lectura de disco en aciertos de caché
	(tras primera carga de metadatos del perfil).
	"""
	profile = _load_profile_meta(profile_name)
	bc = _profile_button_count(profile, button_count)
	sem_u = str(button).strip().upper()
	icon_pack = str(profile.get("icon_pack", DEFAULT_ICON_PACK) or DEFAULT_ICON_PACK)
	ov = profile.get("button_icons", {})
	override_s = ""
	if isinstance(ov, dict):
		raw = ov.get(sem_u) or ov.get(sem_u.lower())
		if isinstance(raw, str) and raw.strip():
			override_s = raw.strip()
	key = (str(profile_name), sem_u, icon_pack, bc, override_s)
	if key in _PATH_CACHE:
		return _PATH_CACHE[key]
	path = _resolve_icon_path_loaded(profile, profile_name, button, bc)
	_PATH_CACHE[key] = path
	return path


def resolve_background(profile_name):
	profile = deepcopy(_load_profile_meta(profile_name))
	override_value = profile.get("background")
	if isinstance(override_value, str) and override_value.strip():
		path_s = override_value.strip()
		r = resolve_under_root(_profile_dir(profile_name), path_s)
		if r:
			return r
		if os.path.isabs(path_s):
			try:
				ap = Path(path_s).resolve(strict=False)
			except OSError:
				ap = None
			if ap is not None and ap.is_file() and not ap.is_symlink():
				for base_str in (USER_DIR, ASSETS_DIR):
					try:
						ap.relative_to(Path(base_str).resolve(strict=False))
						return str(ap)
					except ValueError:
						continue
	pack = _normalize_icon_pack_id(profile.get("icon_pack", DEFAULT_ICON_PACK))
	path = os.path.join(ICON_PACKS_DIR, pack, "background.png")
	if os.path.isfile(path) and not os.path.islink(path):
		return path
	return None


def resolve_asset(path):
	if not isinstance(path, str) or not path.strip():
		return None
	candidate = path.strip()
	for root in (USER_DIR, ASSETS_DIR, PROJECT_ROOT):
		r = resolve_under_root(root, candidate)
		if r:
			return r
	return None


def resolve_icons_map(profile_name, button_count):
	labels = get_button_labels(button_count)
	profile = _load_profile_meta(profile_name)
	result = {}
	for idx, label in enumerate(labels):
		physical_id = f"BTN_{idx + 1}"
		semantic = resolve_semantic_for_physical(profile, physical_id, label)
		result[label] = resolve_icon(profile_name, semantic, button_count=button_count)
	return result


def resolve_icons_map_from_profile_dict(profile, button_count=None):
	"""
	Resuelve mapa label -> ruta usando el dict de perfil en memoria (sin depender
	de que profile.json en disco esté guardado). Útil para el editor HUD.
	"""
	if not isinstance(profile, dict):
		return {}
	if button_count is None:
		button_count = _profile_button_count(profile, 6)
	labels = get_button_labels(button_count)
	pid = str(profile.get("id", ""))
	result = {}
	for idx, label in enumerate(labels):
		physical_id = f"BTN_{idx + 1}"
		semantic = resolve_semantic_for_physical(profile, physical_id, label)
		result[label] = _resolve_icon_path_loaded(profile, pid, semantic, button_count)
	return result


def resolve_system_button_paths_from_profile_dict(profile):
	"""Rutas select.png / start.png del icon_pack del perfil (fallback al pack default)."""
	if not isinstance(profile, dict):
		return None, None
	pack = str(profile.get("icon_pack", DEFAULT_ICON_PACK) or DEFAULT_ICON_PACK)
	sel = _resolve_pack_stem_path(pack, "select") or _resolve_default_pack_stem("select")
	start = _resolve_pack_stem_path(pack, "start") or _resolve_default_pack_stem("start")
	return sel, start
