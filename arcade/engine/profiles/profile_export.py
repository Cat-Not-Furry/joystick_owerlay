# profiles/profile_export.py
# Exportar e importar perfiles en formato ZIP

import json
import os
import re
import shutil
import tempfile
import zipfile

from config import (
	get_button_labels,
	get_default_icon_path,
	PROFILES_DIR,
	BINDING_TEMPLATES_DIR,
	PROFILE_KEY_BINDINGS_FILENAME,
	PROFILE_HITBOX_BINDINGS_FILENAME,
	PROFILE_MIXBOX_BINDINGS_FILENAME,
	PROFILE_JOYSTICK_BINDINGS_FILENAME,
)
from utils.safe_zip_extract import extract_zip_safely

from .bindings_storage import ensure_binding_templates, hydrate_profile_bindings
from .profile_store import _normalize_profile, save_profiles_data


_ALLOWED_IMPORT_ICON_EXT = frozenset({".png", ".jpg", ".jpeg", ".webp"})


def _is_safe_import_icon_basename(filename):
	if not isinstance(filename, str) or not filename:
		return False
	if os.sep in filename or (os.altsep and os.altsep in filename):
		return False
	if filename.startswith(".") or ".." in filename:
		return False
	ext = os.path.splitext(filename)[1].lower()
	if ext not in _ALLOWED_IMPORT_ICON_EXT:
		return False
	stem = os.path.splitext(filename)[0]
	return bool(stem and re.match(r"^[\w\-. ]+$", stem))


def _sanitize_filename(name):
	"""Sanitiza el nombre para usarlo como nombre de archivo."""
	safe = re.sub(r"[^\w\s\-]", "", str(name))
	safe = re.sub(r"\s+", "_", safe.strip())
	return safe or "perfil"


def _binding_filenames():
	return (
		PROFILE_KEY_BINDINGS_FILENAME,
		PROFILE_HITBOX_BINDINGS_FILENAME,
		PROFILE_MIXBOX_BINDINGS_FILENAME,
		PROFILE_JOYSTICK_BINDINGS_FILENAME,
	)


def _copy_profile_bindings_to_zip_tmp(profile_id, tmpdir):
	"""Copia los cuatro JSON de bindings del perfil a tmpdir/bindings/."""
	bind_dir = os.path.join(tmpdir, "bindings")
	os.makedirs(bind_dir, exist_ok=True)
	pid = str(profile_id)
	prof_dir = os.path.join(PROFILES_DIR, pid)
	ensure_binding_templates()
	for name in _binding_filenames():
		src = os.path.join(prof_dir, name)
		dst = os.path.join(bind_dir, name)
		if os.path.isfile(src):
			shutil.copy2(src, dst)
		else:
			tpl = os.path.join(BINDING_TEMPLATES_DIR, name)
			if os.path.isfile(tpl):
				shutil.copy2(tpl, dst)
			else:
				with open(dst, "w", encoding="utf-8") as fh:
					fh.write("{}")


def _import_bindings_from_zip_tmp(tmpdir, profile_id):
	"""Restaura bindings desde ZIP a PROFILES_DIR/<id>/."""
	bind_src = os.path.join(tmpdir, "bindings")
	if not os.path.isdir(bind_src):
		return
	pdir = os.path.join(PROFILES_DIR, str(profile_id))
	os.makedirs(pdir, exist_ok=True)
	allowed = frozenset(_binding_filenames())
	for name in os.listdir(bind_src):
		if name not in allowed:
			continue
		fp = os.path.join(bind_src, name)
		if os.path.isfile(fp) and not os.path.islink(fp):
			shutil.copy2(fp, os.path.join(pdir, name))


def export_profile_to_zip(profile, dest_dir):
	"""
	Exporta un perfil a un archivo ZIP.
	Retorna la ruta del ZIP creado o None si falla.
	"""
	try:
		name = profile.get("name", "perfil")
		safe_name = _sanitize_filename(name)
		zip_filename = f"{safe_name}.zip"
		zip_path = os.path.join(dest_dir, zip_filename)

		with tempfile.TemporaryDirectory() as tmpdir:
			profile_path = os.path.join(tmpdir, "profile.json")
			export_data = dict(profile)
			export_data["profile_version"] = 2
			with open(profile_path, "w", encoding="utf-8") as f:
				json.dump(export_data, f, indent=2, ensure_ascii=False)

			_copy_profile_bindings_to_zip_tmp(profile.get("id"), tmpdir)

			icons_dir = os.path.join(tmpdir, "icons")
			os.makedirs(icons_dir, exist_ok=True)
			button_icons = profile.get("button_icons", {})
			labels = get_button_labels(profile.get("button_count", 6))
			for label in labels:
				path = button_icons.get(label)
				if not path or path == get_default_icon_path(label):
					continue
				if os.path.exists(path):
					dest = os.path.join(icons_dir, os.path.basename(path))
					shutil.copy2(path, dest)

			with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
				for root, _, files in os.walk(tmpdir):
					for file in files:
						full_path = os.path.join(root, file)
						arcname = os.path.relpath(full_path, tmpdir)
						zipf.write(full_path, arcname)

		return zip_path
	except Exception:
		return None


def _safe_extract_zip(zip_path, dest_dir):
	"""Extrae ZIP con validacion estricta (sin extractall)."""
	extract_zip_safely(zip_path, dest_dir)


def _resolve_import_conflict(normalized, existing, conflict_resolver, next_index):
	"""
	Resuelve conflicto de nombre al importar.
	Retorna (normalized, existing). Si cancel, retorna (None, None).
	"""
	if existing is None:
		return (normalized, None)
	choice = conflict_resolver(normalized["name"]) if conflict_resolver else "rename"
	if choice == "cancel":
		return (None, None)
	if choice == "rename":
		normalized["name"] = f"{normalized['name']}_importado"
		normalized["id"] = f"perfil_{next_index}"
		return (normalized, None)
	return (normalized, existing)


def _copy_icons_from_zip(tmpdir, icons_dest):
	"""Copia tmpdir/icons/ a icons_dest si existe."""
	icons_src = os.path.join(tmpdir, "icons")
	if not os.path.isdir(icons_src):
		return
	os.makedirs(icons_dest, exist_ok=True)
	for filename in os.listdir(icons_src):
		if not _is_safe_import_icon_basename(filename):
			continue
		src_file = os.path.join(icons_src, filename)
		if os.path.isfile(src_file) and not os.path.islink(src_file):
			dest_file = os.path.join(icons_dest, filename)
			shutil.copy2(src_file, dest_file)


def _update_button_icon_paths(button_icons, icons_dest):
	"""Actualiza rutas en button_icons a icons/basename cuando el archivo existe."""
	for label, path in list(button_icons.items()):
		if path and not os.path.isabs(path):
			basename = os.path.basename(path)
			if os.path.exists(os.path.join(icons_dest, basename)):
				button_icons[label] = os.path.join("icons", basename)


def _apply_imported_profile(profiles, normalized, existing):
	"""Reemplaza existing o añade normalized a profiles."""
	if existing is not None:
		idx = profiles.index(existing)
		profiles[idx] = normalized
	else:
		profiles.append(normalized)


def import_profile_from_zip(zip_path, profile_data, conflict_resolver=None):
	"""
	Importa un perfil desde un archivo ZIP.
	- zip_path: ruta del archivo ZIP
	- profile_data: dict con active_profile, profiles, etc. (se modifica in-place)
	- conflict_resolver: callable(imported_name) -> "overwrite"|"rename"|"cancel". Si None, usa "rename".

	Retorna el perfil importado o None si se cancela o hay error.
	"""
	try:
		with tempfile.TemporaryDirectory() as tmpdir:
			_safe_extract_zip(zip_path, tmpdir)
			profile_path = os.path.join(tmpdir, "profile.json")
			if not os.path.exists(profile_path):
				raise ValueError("El ZIP no contiene profile.json")

			with open(profile_path, "r", encoding="utf-8") as f:
				raw = json.load(f)

			if not isinstance(raw, dict) or "name" not in raw:
				raise ValueError("profile.json no tiene estructura valida")

			profiles = profile_data.get("profiles", [])
			next_index = len(profiles) + 1
			normalized = _normalize_profile(raw, next_index)
			existing = next((p for p in profiles if p["name"] == normalized["name"]), None)

			normalized, existing = _resolve_import_conflict(
				normalized, existing, conflict_resolver, next_index
			)
			if normalized is None:
				return None

			icons_dest = os.path.join(PROFILES_DIR, str(normalized["id"]), "icons")
			_copy_icons_from_zip(tmpdir, icons_dest)
			_update_button_icon_paths(normalized.get("button_icons", {}), icons_dest)

			_import_bindings_from_zip_tmp(tmpdir, normalized["id"])
			hydrate_profile_bindings(normalized)

			_apply_imported_profile(profiles, normalized, existing)

			save_profiles_data(profile_data)

			from core.assets_resolver import invalidate_profile_cache

			invalidate_profile_cache(normalized["id"])
			return normalized

	except zipfile.BadZipFile:
		raise ValueError("El archivo no es un ZIP valido")
	except json.JSONDecodeError as e:
		raise ValueError(f"profile.json invalido: {e}")
