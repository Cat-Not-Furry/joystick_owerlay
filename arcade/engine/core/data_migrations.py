import json
import os
import shutil
from datetime import datetime

from config import (
	CONFIGS_DIR,
	PROFILES_DIR,
	PROFILES_INDEX_PATH,
	USER_DIR,
	USER_BACKUPS_DIR,
	LEGACY_XDG_USER_ROOT,
	get_data_version,
	write_data_version,
)


CURRENT_DATA_VERSION = 5
LEGACY_PROFILES_PATH = "json/profiles.json"


def _safe_name(value, fallback):
	text = str(value or "").strip()
	if not text:
		return fallback
	return "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in text)


def _read_json(path, default):
	if not os.path.exists(path):
		return default
	try:
		with open(path, "r", encoding="utf-8") as file:
			return json.loads(file.read().strip() or "{}")
	except Exception:
		return default


def _write_json(path, data):
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as file:
		json.dump(data, file, indent=4, ensure_ascii=True)


def _legacy_user_index_path():
	return os.path.join(LEGACY_XDG_USER_ROOT, "profiles_index.json")


def _migrate_xdg_user_tree_to_project():
	"""
	Si el canon (proyecto/user) no tiene índice pero existe legado en XDG,
	copia el árbol user/ legado al canon (backup previo si hace falta).
	Idempotente si ya existe índice en canon.
	"""
	if os.path.exists(PROFILES_INDEX_PATH):
		return {"migrated": False, "reason": "canon_index_exists"}
	legacy_index = _legacy_user_index_path()
	if not os.path.exists(legacy_index):
		return {"migrated": False, "reason": "no_legacy_xdg_index"}
	os.makedirs(USER_BACKUPS_DIR, exist_ok=True)
	ts = datetime.now().strftime("%Y%m%d_%H%M%S")
	pre = os.path.join(USER_BACKUPS_DIR, f"pre_xdg_import_{ts}")
	try:
		if os.path.isdir(USER_DIR) and os.listdir(USER_DIR):
			shutil.copytree(USER_DIR, pre, dirs_exist_ok=False)
	except Exception:
		pass
	try:
		for root, dirs, files in os.walk(LEGACY_XDG_USER_ROOT):
			rel = os.path.relpath(root, LEGACY_XDG_USER_ROOT)
			dest_root = os.path.join(USER_DIR, rel) if rel != "." else USER_DIR
			os.makedirs(dest_root, exist_ok=True)
			for name in files:
				src_f = os.path.join(root, name)
				dst_f = os.path.join(dest_root, name)
				shutil.copy2(src_f, dst_f)
	except Exception as ex:
		return {"migrated": False, "reason": f"xdg_copy_failed:{ex}"}
	return {"migrated": True, "reason": "xdg_user_tree_copied"}


def _build_migration_plan():
	plan = {
		"needs_migration": False,
		"already_migrated": os.path.exists(PROFILES_INDEX_PATH),
		"legacy_profiles_exists": os.path.exists(LEGACY_PROFILES_PATH),
		"moves": [],
	}
	if os.path.exists(PROFILES_INDEX_PATH):
		return plan
	legacy = _read_json(LEGACY_PROFILES_PATH, {})
	raw_profiles = legacy.get("profiles", []) if isinstance(legacy, dict) else []
	if not isinstance(raw_profiles, list) or not raw_profiles:
		return plan
	plan["needs_migration"] = True
	for index, profile in enumerate(raw_profiles, start=1):
		profile_name = _safe_name(profile.get("id"), f"perfil_{index}") if isinstance(profile, dict) else f"perfil_{index}"
		plan["moves"].append(
			{
				"from": LEGACY_PROFILES_PATH,
				"to": os.path.join(PROFILES_DIR, profile_name, "profile.json"),
			}
		)
	return plan


def dry_run_migration():
	return _build_migration_plan()


def _create_backup():
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	backup_dir = os.path.join(USER_BACKUPS_DIR, f"migration_{timestamp}")
	os.makedirs(backup_dir, exist_ok=True)
	if os.path.exists(LEGACY_PROFILES_PATH):
		shutil.copy2(LEGACY_PROFILES_PATH, os.path.join(backup_dir, "profiles.json"))
	return backup_dir


def _migrate_profiles_index():
	legacy = _read_json(LEGACY_PROFILES_PATH, {})
	if not isinstance(legacy, dict):
		return {"active_profile": "perfil_1", "profiles": []}
	raw_profiles = legacy.get("profiles", [])
	if not isinstance(raw_profiles, list):
		raw_profiles = []
	index_profiles = []
	for idx, profile in enumerate(raw_profiles, start=1):
		if not isinstance(profile, dict):
			continue
		profile_id = _safe_name(profile.get("id"), f"perfil_{idx}")
		profile_dir = os.path.join(PROFILES_DIR, profile_id)
		os.makedirs(profile_dir, exist_ok=True)
		_write_json(os.path.join(profile_dir, "profile.json"), profile)
		index_profiles.append({"id": profile_id, "name": profile.get("name", profile_id)})
	if not index_profiles:
		profile_id = "perfil_1"
		profile_dir = os.path.join(PROFILES_DIR, profile_id)
		os.makedirs(profile_dir, exist_ok=True)
		_write_json(
			os.path.join(profile_dir, "profile.json"),
			{
				"id": profile_id,
				"name": "Perfil principal",
				"button_count": 6,
				"input_mode": "teclado",
				"button_icons": {},
				"key_bindings": {},
				"joystick_bindings": {},
				"icon_pack": "default",
			},
		)
		index_profiles = [{"id": profile_id, "name": "Perfil principal"}]
	active_profile = _safe_name(legacy.get("active_profile"), index_profiles[0]["id"])
	index_profiles.sort(key=lambda x: str(x["id"]))
	return {
		"active_profile": active_profile,
		"profiles": index_profiles,
		"window_mode": legacy.get("window_mode", "normal"),
		"capture_mode": legacy.get("capture_mode", "normal"),
		"ignore_videoresize": bool(legacy.get("ignore_videoresize", False)),
		"ui_font_family": legacy.get("ui_font_family", "JetBrainsMono"),
		"extensions": legacy.get("extensions", {"plugin_standby_enabled": True, "input_history_max_events": 1000}),
		"backups_enabled": True,
		"backup_prompt_completed": True,
		"xdg_mirror_enabled": True,
	}


def migrate_semantic_binding_v3_to_v4():
	"""Manifiesto v3->v4: asegura clave semantic_binding en cada profile.json."""
	changed = 0
	if not os.path.isdir(PROFILES_DIR):
		return {"changed": 0, "reason": "no_profiles_dir"}
	for name in os.listdir(PROFILES_DIR):
		pdir = os.path.join(PROFILES_DIR, name)
		pjson = os.path.join(pdir, "profile.json")
		if not os.path.isfile(pjson):
			continue
		data = _read_json(pjson, {})
		if not isinstance(data, dict):
			continue
		sb = data.get("semantic_binding")
		if isinstance(sb, dict):
			continue
		data["semantic_binding"] = {}
		_write_json(pjson, data)
		changed += 1
	return {"changed": changed}


def migrate_profile_bindings_sidecars_v4_to_v5():
	"""
	v4->v5: bindings en JSON por perfil; quita key_bindings/joystick_bindings embebidos
	tras volcar a sidecars (migrate_inline_bindings_from_profile_json).
	"""
	from profiles.bindings_storage import (
		ensure_binding_templates,
		migrate_inline_bindings_from_profile_json,
	)

	ensure_binding_templates()
	processed = 0
	stripped = 0
	if not os.path.isdir(PROFILES_DIR):
		return {"processed": 0, "stripped": 0, "reason": "no_profiles_dir"}
	for name in os.listdir(PROFILES_DIR):
		pdir = os.path.join(PROFILES_DIR, name)
		pjson = os.path.join(pdir, "profile.json")
		if not os.path.isfile(pjson):
			continue
		raw = _read_json(pjson, {})
		if not isinstance(raw, dict):
			continue
		pid = str(raw.get("id") or name)
		try:
			bc = int(raw.get("button_count", 6) or 6)
		except Exception:
			bc = 6
		four_a = bool(raw.get("layout_four_variant_4a")) and bc == 4
		migrate_inline_bindings_from_profile_json(pid, raw, bc, four_a)
		processed += 1
		if "key_bindings" in raw or "joystick_bindings" in raw:
			raw.pop("key_bindings", None)
			raw.pop("joystick_bindings", None)
			_write_json(pjson, raw)
			stripped += 1
	return {"processed": processed, "stripped": stripped}


_MIGRATION_FUNCTIONS = {
	"migrate_semantic_binding_v3_to_v4": migrate_semantic_binding_v3_to_v4,
	"migrate_profile_bindings_sidecars_v4_to_v5": migrate_profile_bindings_sidecars_v4_to_v5,
}


def _append_migration_log(line_obj):
	log_path = os.path.join(USER_DIR, "migrations_applied.jsonl")
	os.makedirs(USER_DIR, exist_ok=True)
	try:
		with open(log_path, "a", encoding="utf-8") as fh:
			fh.write(json.dumps(line_obj, ensure_ascii=True) + "\n")
	except Exception:
		pass


def _load_migration_index():
	idx_path = os.path.join(CONFIGS_DIR, "migrations", "index.json")
	if not os.path.isfile(idx_path):
		return None
	try:
		with open(idx_path, "r", encoding="utf-8") as fh:
			return json.loads(fh.read().strip() or "{}")
	except Exception:
		return None


def _acquire_migration_lock(migration_id):
	lock_path = os.path.join(USER_DIR, ".migration_lock")
	os.makedirs(USER_DIR, exist_ok=True)
	try:
		if os.path.isfile(lock_path):
			return False
		with open(lock_path, "w", encoding="utf-8") as fh:
			json.dump({"pid": os.getpid(), "migration_id": migration_id}, fh)
		return True
	except Exception:
		return False


def _release_migration_lock():
	try:
		lp = os.path.join(USER_DIR, ".migration_lock")
		if os.path.isfile(lp):
			os.remove(lp)
	except Exception:
		pass


def apply_config_manifest_migrations():
	"""Aplica cadena de manifiestos cuyo from_data_version coincide con el actual."""
	index = _load_migration_index()
	if not index or not isinstance(index, dict):
		return {"applied": False, "reason": "no_index"}
	migrations = index.get("migrations") or []
	if not isinstance(migrations, list) or not migrations:
		return {"applied": False, "reason": "empty_chain"}
	applied_any = False
	while True:
		try:
			current = int(get_data_version("0"))
		except Exception:
			current = 0
		next_entry = None
		for m in migrations:
			if not isinstance(m, dict):
				continue
			try:
				fv = int(m.get("from_data_version", -1))
			except Exception:
				continue
			if fv == current:
				next_entry = m
				break
		if next_entry is None:
			break
		mid = str(next_entry.get("migration_id", "unknown"))
		manifest_rel = next_entry.get("manifest")
		if not manifest_rel:
			break
		manifest_path = os.path.join(CONFIGS_DIR, "migrations", str(manifest_rel).lstrip("/"))
		if not os.path.isfile(manifest_path):
			return {"applied": False, "reason": f"missing_manifest:{manifest_path}"}
		try:
			with open(manifest_path, "r", encoding="utf-8") as fh:
				manifest = json.loads(fh.read().strip() or "{}")
		except Exception as ex:
			return {"applied": False, "reason": f"bad_manifest:{ex}"}
		impl = manifest.get("implementation") or {}
		fn_name = impl.get("function")
		if not fn_name or fn_name not in _MIGRATION_FUNCTIONS:
			return {"applied": False, "reason": f"no_handler:{fn_name}"}
		if not _acquire_migration_lock(mid):
			return {"applied": False, "reason": "lock_busy"}
		backup_dir = None
		try:
			safety = manifest.get("safety") or {}
			if safety.get("backup_before_write"):
				backup_dir = _create_backup()
			result = _MIGRATION_FUNCTIONS[fn_name]()
			to_ver = str(manifest.get("to_data_version", "")).strip()
			if to_ver:
				write_data_version(to_ver)
			_append_migration_log(
				{
					"migration_id": mid,
					"from": str(manifest.get("from_data_version")),
					"to": to_ver,
					"result": "ok",
					"detail": result,
					"backup_dir": backup_dir,
				}
			)
			applied_any = True
		finally:
			_release_migration_lock()
	return {"applied": applied_any}


def migrate_if_needed():
	os.makedirs(USER_DIR, exist_ok=True)
	os.makedirs(PROFILES_DIR, exist_ok=True)
	os.makedirs(USER_BACKUPS_DIR, exist_ok=True)

	xdg_result = _migrate_xdg_user_tree_to_project()
	if xdg_result.get("migrated"):
		manifest_result = apply_config_manifest_migrations()
		try:
			if int(get_data_version("0")) < CURRENT_DATA_VERSION:
				write_data_version(CURRENT_DATA_VERSION)
		except Exception:
			write_data_version(CURRENT_DATA_VERSION)
		return {
			"migrated": True,
			"step": "xdg_to_project",
			"detail": xdg_result,
			"manifests": manifest_result,
		}

	if os.path.exists(PROFILES_INDEX_PATH):
		try:
			dv = int(get_data_version("0"))
		except Exception:
			dv = 0
		if dv < CURRENT_DATA_VERSION:
			manifest_result = apply_config_manifest_migrations()
			try:
				dv2 = int(get_data_version("0"))
			except Exception:
				dv2 = 0
			if dv2 < CURRENT_DATA_VERSION:
				write_data_version(CURRENT_DATA_VERSION)
			return {
				"migrated": True,
				"reason": "data_version_bump",
				"manifests": manifest_result,
			}
		return {"migrated": False, "reason": "already_migrated"}
	plan = _build_migration_plan()
	if not plan["needs_migration"]:
		apply_config_manifest_migrations()
		try:
			if int(get_data_version("0")) < CURRENT_DATA_VERSION:
				write_data_version(CURRENT_DATA_VERSION)
		except Exception:
			write_data_version(CURRENT_DATA_VERSION)
		return {"migrated": False, "reason": "nothing_to_migrate"}
	backup_dir = _create_backup()
	index_data = _migrate_profiles_index()
	_write_json(PROFILES_INDEX_PATH, index_data)
	apply_config_manifest_migrations()
	try:
		if int(get_data_version("0")) < CURRENT_DATA_VERSION:
			write_data_version(CURRENT_DATA_VERSION)
	except Exception:
		write_data_version(CURRENT_DATA_VERSION)
	return {"migrated": True, "backup_dir": backup_dir, "items": len(index_data.get("profiles", []))}
