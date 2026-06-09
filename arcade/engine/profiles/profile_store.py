import json
import os
import shutil
import tempfile
from datetime import datetime

from .hud_layout import normalize_hud_layout_section
from core.assets_resolver import invalidate_profile_cache
from core.data_migrations import migrate_if_needed

_RUNTIME_BACKUPS_ENABLED = True
from config import (
	PROFILES_PATH,
	PROFILES_DIR,
	USER_DIR,
	BINDINGS_PATH,
	JOYSTICK_BINDINGS_PATH,
	SUPPORTED_BUTTON_COUNTS,
	SUPPORTED_CONTROLLER_STYLES,
	SUPPORTED_INPUT_MODES,
	SUPPORTED_CAPTURE_MODES,
	SUPPORTED_MONO_FONT_FAMILIES,
	DEFAULT_MONO_FONT_FAMILY,
	JOYSTICK_COLOR_PRESETS,
	get_button_labels,
	get_bindings_format_key,
	get_active_bindings_format_key,
	DEFAULT_ICON_PACK,
	ensure_contract_dirs,
	ICON_PACKS_DIR,
	BACKUP_PROFILES_ROOT,
	MIRROR_PROFILES_INDEX_PATH,
	USER_BACKUPS_DIR,
	CANONICAL_CONTROLLER_STYLES,
	normalize_controller_style,
)
from .bindings_storage import (
	ensure_binding_templates,
	copy_profile_binding_files_from_base,
	migrate_inline_bindings_from_profile_json,
	hydrate_profile_bindings,
	persist_profile_bindings_to_files,
	persist_format_extras_to_bindings_file,
	mirror_keyboard_hud_hitbox_mixbox,
	profile_public_json_dict,
	load_bindings_tree,
	get_slice,
	path_key_bindings,
	path_hitbox_bindings,
	path_mixbox_bindings,
	path_joystick_bindings,
)


def _read_json_file(path, default):
	if not os.path.exists(path):
		return default

	try:
		with open(path, "r") as file:
			content = file.read().strip()
			if content == "":
				return default
			return json.loads(content)
	except Exception:
		return default


def _write_json_file(path, data):
	_write_json_atomic(path, data)


def _write_json_atomic(path, data):
	dir_path = os.path.dirname(path)
	if dir_path:
		os.makedirs(dir_path, exist_ok=True)
	fd, tmp_path = tempfile.mkstemp(prefix=".joystick_", suffix=".json", dir=dir_path, text=True)
	try:
		with os.fdopen(fd, "w", encoding="utf-8") as fh:
			json.dump(data, fh, indent=4)
			fh.flush()
			os.fsync(fh.fileno())
		os.replace(tmp_path, path)
	except Exception:
		try:
			if os.path.exists(tmp_path):
				os.unlink(tmp_path)
		except Exception:
			pass
		raise


def _default_button_icons(button_count):
	return {label: None for label in get_button_labels(button_count)}


def _default_profile(profile_id, name, button_count=6):
	color_values = list(JOYSTICK_COLOR_PRESETS.values())
	return {
		"id": profile_id,
		"name": name,
		"button_count": button_count,
		"input_mode": "teclado",
		"preferred_joystick_path": None,
		"preferred_keyboard_path": None,
		"tournament_mode": False,
		"hitbox_alt_layout": False,
		"controller_style": "default",
		"joystick_bindings_style": None,
		"joystick_color": list(color_values[0]),
		"joystick_knob_color": list(color_values[0]),
		"joystick_bar_color": [0, 0, 0],
		"joystick_ring_color": [255, 255, 255],
		"button_color_inactive": [80, 80, 80],
		"button_color_active": [255, 0, 0],
		"icon_pack": DEFAULT_ICON_PACK,
		"icon_pack_locked": False,
		"button_icons": _default_button_icons(button_count),
		"key_bindings": {},
		"joystick_bindings": {},
		"layout_four_variant_4a": False,
	}

def _default_window_mode():
	return "normal"


def _normalize_window_policy(window_mode):
	"""Win32: sin floating_hint en UI; perfiles Linux se normalizan al cargar."""
	if os.name == "nt":
		return "normal"
	return _validate_choice(
		window_mode,
		["floating_hint", "normal"],
		_default_window_mode(),
	)


def _normalize_ignore_videoresize(value):
	"""Win32: resize permitido en runtime; campo no expuesto en UI (coherencia JSON)."""
	if os.name == "nt":
		return False
	return bool(value)

def _default_capture_mode():
	return "normal"

def _default_ui_font_family():
	return DEFAULT_MONO_FONT_FAMILY


def _default_extensions_config():
	return {
		"plugin_standby_enabled": True,
		"input_history_max_events": 1000,
	}


def _normalize_extensions_config(raw):
	default_cfg = _default_extensions_config()
	if not isinstance(raw, dict):
		return dict(default_cfg)
	enabled = raw.get("plugin_standby_enabled", default_cfg["plugin_standby_enabled"])
	max_events = raw.get("input_history_max_events", default_cfg["input_history_max_events"])
	try:
		max_events = int(max_events)
	except Exception:
		max_events = default_cfg["input_history_max_events"]
	max_events = max(100, min(10000, max_events))
	return {
		"plugin_standby_enabled": bool(enabled),
		"input_history_max_events": max_events,
	}


def _validate_choice(value, allowed, default):
	"""Retorna value si esta en allowed, sino default."""
	return value if value in allowed else default


def _validate_color(value, default):
	"""Valida que value sea lista de 3 ints. Retorna default si no."""
	if not isinstance(value, list) or len(value) != 3:
		return default
	return list(value)


def _validate_icon_pack(name):
	p = os.path.join(ICON_PACKS_DIR, str(name or ""), "buttons")
	if os.path.isdir(p):
		return str(name)
	return DEFAULT_ICON_PACK


def _normalize_profile_identity(profile, fallback_index):
	profile_id = profile.get("id") or f"perfil_{fallback_index}"
	profile_name = profile.get("name") or f"Perfil {fallback_index}"
	button_count = _validate_choice(
		profile.get("button_count", 6), SUPPORTED_BUTTON_COUNTS, 6
	)
	input_mode = _validate_choice(
		profile.get("input_mode", "teclado"), SUPPORTED_INPUT_MODES, "teclado"
	)
	st_raw = profile.get("controller_style", "default")
	controller_style = normalize_controller_style(st_raw)
	if controller_style not in CANONICAL_CONTROLLER_STYLES:
		controller_style = "default"
	jbs = profile.get("joystick_bindings_style")
	if jbs is not None and isinstance(jbs, str):
		jbs = normalize_controller_style(jbs)
		if jbs not in CANONICAL_CONTROLLER_STYLES:
			jbs = None
	joystick_bindings_style = jbs
	preferred_joystick_path = profile.get("preferred_joystick_path")
	if preferred_joystick_path is not None and not isinstance(preferred_joystick_path, str):
		preferred_joystick_path = None
	preferred_keyboard_path = profile.get("preferred_keyboard_path")
	if preferred_keyboard_path is not None and not isinstance(preferred_keyboard_path, str):
		preferred_keyboard_path = None
	tournament_mode = profile.get("tournament_mode", False)
	if not isinstance(tournament_mode, bool):
		tournament_mode = False
	hitbox_alt_layout = profile.get("hitbox_alt_layout", False)
	if not isinstance(hitbox_alt_layout, bool):
		hitbox_alt_layout = False
	return {
		"id": profile_id,
		"name": profile_name,
		"button_count": button_count,
		"input_mode": input_mode,
		"controller_style": controller_style,
		"hitbox_alt_layout": hitbox_alt_layout,
		"joystick_bindings_style": joystick_bindings_style,
		"preferred_joystick_path": preferred_joystick_path,
		"preferred_keyboard_path": preferred_keyboard_path,
		"tournament_mode": tournament_mode,
	}


def _normalize_profile_colors(profile):
	joystick_color = _validate_color(
		profile.get("joystick_color", [0, 255, 0]), [0, 255, 0]
	)
	joystick_knob_color = _validate_color(
		profile.get("joystick_knob_color", joystick_color), list(joystick_color)
	)
	joystick_bar_color = _validate_color(
		profile.get("joystick_bar_color", [0, 0, 0]), [0, 0, 0]
	)
	joystick_ring_color = _validate_color(
		profile.get("joystick_ring_color", [255, 255, 255]), [255, 255, 255]
	)
	btn_inactive = _validate_color(
		profile.get("button_color_inactive", [80, 80, 80]), [80, 80, 80]
	)
	btn_active = _validate_color(
		profile.get("button_color_active", [255, 0, 0]), [255, 0, 0]
	)
	return joystick_color, joystick_knob_color, joystick_bar_color, joystick_ring_color, btn_inactive, btn_active


def _normalize_bindings_for_format_8(bindings_dict, button_count):
	if not isinstance(bindings_dict, dict):
		bindings_dict = {}
	if button_count != 8:
		return dict(bindings_dict)
	result = dict(bindings_dict)
	if "PPP" in result and "TR" not in result:
		result["TR"] = result["PPP"]
	if "KKK" in result and "BR" not in result:
		result["BR"] = result["KKK"]
	return result


def _normalize_profile(profile, fallback_index):
	identity = _normalize_profile_identity(profile, fallback_index)
	button_count = identity["button_count"]
	joystick_color, knob, bar, ring, btn_inactive, btn_active = _normalize_profile_colors(profile)

	button_icons = _normalize_bindings_for_format_8(profile.get("button_icons", {}), button_count)
	for label in get_button_labels(button_count):
		if label not in button_icons:
			button_icons[label] = None

	layout_four_variant_4a = bool(profile.get("layout_four_variant_4a", False))
	if button_count != 4:
		layout_four_variant_4a = False

	icon_locked = profile.get("icon_pack_locked", False)
	if not isinstance(icon_locked, bool):
		icon_locked = False
	ip = _validate_icon_pack(profile.get("icon_pack", DEFAULT_ICON_PACK))

	sb = profile.get("semantic_binding")
	if isinstance(sb, dict):
		semantic_binding = {
			str(k).strip(): str(v).strip().upper()
			for k, v in sb.items()
			if isinstance(k, str) and isinstance(v, str) and str(k).strip() and str(v).strip()
		}
	else:
		semantic_binding = {}

	result = {
		**identity,
		"joystick_color": joystick_color,
		"joystick_knob_color": knob,
		"joystick_bar_color": bar,
		"joystick_ring_color": ring,
		"button_color_inactive": btn_inactive,
		"button_color_active": btn_active,
		"icon_pack": ip,
		"icon_pack_locked": icon_locked,
		"semantic_binding": semantic_binding,
		"button_icons": button_icons,
		"layout_four_variant_4a": layout_four_variant_4a,
	}
	if "hud_layout" in profile:
		hl = normalize_hud_layout_section(profile.get("hud_layout"))
		if hl is not None:
			result["hud_layout"] = hl

	ensure_binding_templates()
	migrate_inline_bindings_from_profile_json(
		result["id"], profile, button_count, layout_four_variant_4a
	)
	hydrate_profile_bindings(result)
	return result


def _profile_path_from_id(profile_id):
	return os.path.join(PROFILES_DIR, str(profile_id), "profile.json")


def _load_profile_file(profile_id):
	return _read_json_file(_profile_path_from_id(profile_id), {})


def _filesystem_profile_ids():
	if not os.path.isdir(PROFILES_DIR):
		return []
	out = []
	for name in os.listdir(PROFILES_DIR):
		p = os.path.join(PROFILES_DIR, name, "profile.json")
		if os.path.isfile(p):
			out.append(str(name))
	return sorted(out, key=lambda x: str(x))


def _reconcile_index_entries(index_data):
	if not isinstance(index_data, dict):
		index_data = {}
	fs_ids = _filesystem_profile_ids()
	idx_list = index_data.get("profiles")
	if not isinstance(idx_list, list):
		idx_list = []
	idx_by_id = {}
	for it in idx_list:
		if isinstance(it, dict) and it.get("id"):
			pid = str(it["id"])
			if pid in fs_ids:
				idx_by_id[pid] = str(it.get("name") or pid)
	for pid in fs_ids:
		if pid not in idx_by_id:
			raw = _load_profile_file(pid)
			if isinstance(raw, dict) and raw.get("name"):
				idx_by_id[pid] = str(raw["name"])
			else:
				idx_by_id[pid] = pid
	ordered = sorted(idx_by_id.keys(), key=lambda x: str(x))
	index_data["profiles"] = [{"id": pid, "name": idx_by_id[pid]} for pid in ordered]
	ap = str(index_data.get("active_profile", "") or "")
	if ap not in idx_by_id:
		if ordered:
			index_data["active_profile"] = ordered[0]
		else:
			index_data["active_profile"] = ""
	return index_data


def _backup_profile_json_before_overwrite(profile_id):
	if not _RUNTIME_BACKUPS_ENABLED:
		return
	src = _profile_path_from_id(profile_id)
	if not os.path.isfile(src):
		return
	os.makedirs(USER_BACKUPS_DIR, exist_ok=True)
	ts = datetime.now().strftime("%Y%m%d_%H%M%S")
	dst = os.path.join(USER_BACKUPS_DIR, f"profile_{profile_id}_{ts}.json")
	try:
		shutil.copy2(src, dst)
	except Exception:
		return
	prefix = f"profile_{profile_id}_"
	try:
		files = [
			os.path.join(USER_BACKUPS_DIR, f)
			for f in os.listdir(USER_BACKUPS_DIR)
			if f.startswith(prefix) and f.endswith(".json")
		]
		files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
		for old in files[5:]:
			try:
				os.unlink(old)
			except Exception:
				pass
	except Exception:
		pass


def _mirror_one_profile_to_xdg(profile):
	try:
		dst_dir = os.path.join(BACKUP_PROFILES_ROOT, str(profile["id"]))
		os.makedirs(dst_dir, exist_ok=True)
		src = _profile_path_from_id(profile["id"])
		dst = os.path.join(dst_dir, "profile.json")
		if os.path.isfile(src):
			shutil.copy2(src, dst)
	except Exception as ex:
		print(f"[WARN] Espejo XDG perfil {profile.get('id')}: {ex}")


def _mirror_index_to_xdg():
	try:
		os.makedirs(os.path.dirname(MIRROR_PROFILES_INDEX_PATH), exist_ok=True)
		if os.path.isfile(PROFILES_PATH):
			shutil.copy2(PROFILES_PATH, MIRROR_PROFILES_INDEX_PATH)
	except Exception as ex:
		print(f"[WARN] Espejo XDG profiles_index: {ex}")


def _save_profile_file(profile):
	path = _profile_path_from_id(profile["id"])
	_backup_profile_json_before_overwrite(profile["id"])
	persist_profile_bindings_to_files(profile)
	persist_format_extras_to_bindings_file(profile)
	mirror_keyboard_hud_hitbox_mixbox(profile)
	public_doc = profile_public_json_dict(profile)
	_write_json_atomic(path, public_doc)


def _load_profiles_from_index(index_data):
	if not isinstance(index_data, dict):
		index_data = {}
	_reconcile_index_entries(index_data)
	result = []
	raw_profiles = index_data.get("profiles", [])
	for idx, item in enumerate(raw_profiles, start=1):
		if not isinstance(item, dict):
			continue
		if "button_count" in item or "key_bindings" in item:
			profile_id = str(item.get("id") or f"perfil_{idx}")
			raw_profile = dict(item)
		else:
			profile_id = item.get("id")
			if not profile_id:
				continue
			profile_id = str(profile_id)
			raw_profile = _load_profile_file(profile_id)
			if not raw_profile:
				raw_profile = _default_profile(profile_id, item.get("name") or f"Perfil {idx}", 6)
		normalized = _normalize_profile(raw_profile, idx)
		normalized["id"] = profile_id
		if item.get("name") and not raw_profile.get("name"):
			normalized["name"] = str(item["name"])
		result.append(normalized)
	if not result:
		result = [_default_profile("perfil_1", "Perfil principal", 6)]
	return result


def _save_profiles_files(data):
	for profile in data["profiles"]:
		_save_profile_file(profile)
	profiles_sorted = sorted(data["profiles"], key=lambda p: str(p["id"]))
	index_data = {
		"active_profile": data["active_profile"],
		"window_mode": data.get("window_mode", _default_window_mode()),
		"ignore_videoresize": bool(data.get("ignore_videoresize", False)),
		"capture_mode": data.get("capture_mode", _default_capture_mode()),
		"ui_font_family": data.get("ui_font_family", _default_ui_font_family()),
		"extensions": _normalize_extensions_config(data.get("extensions", {})),
		"backups_enabled": bool(data.get("backups_enabled", True)),
		"backup_prompt_completed": bool(data.get("backup_prompt_completed", True)),
		"xdg_mirror_enabled": bool(data.get("xdg_mirror_enabled", True)),
		"profiles": [{"id": p["id"], "name": p.get("name", p["id"])} for p in profiles_sorted],
	}
	_write_json_atomic(PROFILES_PATH, index_data)
	if bool(data.get("xdg_mirror_enabled", True)):
		for profile in data["profiles"]:
			_mirror_one_profile_to_xdg(profile)
		_mirror_index_to_xdg()


def _acquire_index_lock(lock_fh):
	if os.name == "nt":
		import msvcrt

		lock_fh.seek(0)
		msvcrt.locking(lock_fh.fileno(), msvcrt.LK_LOCK, 1)
		return
	import fcntl

	fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)


def _release_index_lock(lock_fh):
	if os.name == "nt":
		import msvcrt

		lock_fh.seek(0)
		msvcrt.locking(lock_fh.fileno(), msvcrt.LK_UNLCK, 1)
		return
	import fcntl

	fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)


def _save_profiles_files_with_flock(data):
	lock_path = os.path.join(USER_DIR, "profiles_index.lock")
	with open(lock_path, "a+", encoding="utf-8") as lock_fh:
		_acquire_index_lock(lock_fh)
		try:
			_save_profiles_files(data)
		finally:
			_release_index_lock(lock_fh)


def migrate_legacy_bindings():
	ensure_contract_dirs()
	old_keyboard = _read_json_file(BINDINGS_PATH, {})
	old_joystick = _read_json_file(JOYSTICK_BINDINGS_PATH, {})

	profiles = []
	profile_index = 1
	for button_count in [4, 6]:
		format_key = get_bindings_format_key(button_count)
		key_bindings = old_keyboard.get(format_key, {}) if isinstance(old_keyboard, dict) else {}
		joy_bindings = old_joystick.get(format_key, {}) if isinstance(old_joystick, dict) else {}

		if key_bindings or joy_bindings:
			profile = _default_profile(
				profile_id=f"perfil_{profile_index}",
				name=f"Perfil {button_count} botones",
				button_count=button_count,
			)
			profile["key_bindings"] = key_bindings
			profile["joystick_bindings"] = joy_bindings
			if joy_bindings:
				profile["input_mode"] = "joystick"
			profiles.append(profile)
			profile_index += 1

	if len(profiles) == 0:
		profiles.append(_default_profile("perfil_1", "Perfil principal", 6))

	data = {
		"active_profile": profiles[0]["id"],
		"window_mode": _default_window_mode(),
		"capture_mode": _default_capture_mode(),
		"ui_font_family": _default_ui_font_family(),
		"extensions": _default_extensions_config(),
		"backups_enabled": True,
		"backup_prompt_completed": True,
		"xdg_mirror_enabled": True,
		"profiles": profiles,
	}
	_save_profiles_files_with_flock(data)
	return data


def _normalize_profiles_data(data):
	"""Normaliza datos de perfiles. Retorna None si se requiere migracion."""
	if not isinstance(data, dict):
		return None
	raw_profiles = data.get("profiles", [])
	if not isinstance(raw_profiles, list) or len(raw_profiles) == 0:
		return None
	profiles = []
	for index, profile in enumerate(raw_profiles, start=1):
		if isinstance(profile, dict):
			profiles.append(_normalize_profile(profile, index))
	if len(profiles) == 0:
		return None
	active_profile = _validate_choice(
		data.get("active_profile", profiles[0]["id"]),
		[p["id"] for p in profiles],
		profiles[0]["id"],
	)
	window_mode = _normalize_window_policy(data.get("window_mode", _default_window_mode()))
	capture_mode = _validate_choice(
		data.get("capture_mode", _default_capture_mode()),
		SUPPORTED_CAPTURE_MODES,
		_default_capture_mode(),
	)
	ui_font_family = _validate_choice(
		data.get("ui_font_family", _default_ui_font_family()),
		SUPPORTED_MONO_FONT_FAMILIES,
		_default_ui_font_family(),
	)
	ignore_videoresize = _normalize_ignore_videoresize(data.get("ignore_videoresize", False))
	extensions = _normalize_extensions_config(data.get("extensions"))
	return {
		"active_profile": active_profile,
		"window_mode": window_mode,
		"ignore_videoresize": ignore_videoresize,
		"capture_mode": capture_mode,
		"ui_font_family": ui_font_family,
		"extensions": extensions,
		"profiles": profiles,
	}


def load_profiles_data():
	ensure_contract_dirs()
	index_existed_pre_migrate = os.path.isfile(PROFILES_PATH)
	migrate_if_needed()
	index_data = _read_json_file(PROFILES_PATH, {})
	profiles = _load_profiles_from_index(index_data)
	active_profile = _validate_choice(
		index_data.get("active_profile", profiles[0]["id"]),
		[p["id"] for p in profiles],
		profiles[0]["id"],
	)
	data = {
		"active_profile": active_profile,
		"window_mode": _normalize_window_policy(
			index_data.get("window_mode", _default_window_mode())
		),
		"ignore_videoresize": _normalize_ignore_videoresize(
			index_data.get("ignore_videoresize", False)
		),
		"capture_mode": _validate_choice(
			index_data.get("capture_mode", _default_capture_mode()),
			SUPPORTED_CAPTURE_MODES,
			_default_capture_mode(),
		),
		"ui_font_family": _validate_choice(
			index_data.get("ui_font_family", _default_ui_font_family()),
			SUPPORTED_MONO_FONT_FAMILIES,
			_default_ui_font_family(),
		),
		"extensions": _normalize_extensions_config(index_data.get("extensions", {})),
		"profiles": profiles,
	}
	if index_data.get("backup_prompt_completed") is not None:
		prompt_done = bool(index_data["backup_prompt_completed"])
	else:
		has_disk = len(_filesystem_profile_ids()) > 0
		prompt_done = bool(index_existed_pre_migrate or has_disk)
	data["backups_enabled"] = bool(index_data.get("backups_enabled", True))
	data["backup_prompt_completed"] = prompt_done
	if index_data.get("xdg_mirror_enabled") is not None:
		data["xdg_mirror_enabled"] = bool(index_data["xdg_mirror_enabled"])
	else:
		data["xdg_mirror_enabled"] = bool(prompt_done)
	save_profiles_data(data)
	return data


def save_profiles_data(data):
	global _RUNTIME_BACKUPS_ENABLED
	ensure_contract_dirs()
	_RUNTIME_BACKUPS_ENABLED = bool(data.get("backups_enabled", True))
	_save_profiles_files_with_flock(data)
	invalidate_profile_cache()


def get_active_profile(data):
	active_id = data["active_profile"]
	for profile in data["profiles"]:
		if profile["id"] == active_id:
			return profile
	return data["profiles"][0]


def set_active_profile(data, profile_id):
	for profile in data["profiles"]:
		if profile["id"] == profile_id:
			data["active_profile"] = profile_id
			invalidate_profile_cache(profile_id)
			return


def create_profile(data, base_profile):
	new_id = f"perfil_{len(data['profiles']) + 1}"
	new_profile = {
		"id": new_id,
		"name": f"Perfil {len(data['profiles']) + 1}",
		"button_count": base_profile["button_count"],
		"input_mode": base_profile["input_mode"],
		"preferred_joystick_path": base_profile.get("preferred_joystick_path"),
		"preferred_keyboard_path": base_profile.get("preferred_keyboard_path"),
		"tournament_mode": base_profile.get("tournament_mode", False),
		"hitbox_alt_layout": base_profile.get("hitbox_alt_layout", False),
		"controller_style": base_profile.get("controller_style", "default"),
		"joystick_bindings_style": base_profile.get("joystick_bindings_style"),
		"joystick_color": list(base_profile["joystick_color"]),
		"joystick_knob_color": list(base_profile.get("joystick_knob_color", base_profile["joystick_color"])),
		"joystick_bar_color": list(base_profile.get("joystick_bar_color", [0, 0, 0])),
		"joystick_ring_color": list(base_profile.get("joystick_ring_color", [255, 255, 255])),
		"button_color_inactive": list(base_profile.get("button_color_inactive", [80, 80, 80])),
		"button_color_active": list(base_profile.get("button_color_active", [255, 0, 0])),
		"icon_pack": _validate_icon_pack(
			str(base_profile.get("icon_pack", DEFAULT_ICON_PACK) or DEFAULT_ICON_PACK)
		),
		"icon_pack_locked": bool(base_profile.get("icon_pack_locked", False)),
		"button_icons": dict(base_profile["button_icons"]),
		"layout_four_variant_4a": (
			bool(base_profile.get("layout_four_variant_4a", False))
			if base_profile.get("button_count") == 4
			else False
		),
	}
	if "hud_layout" in base_profile:
		hl = normalize_hud_layout_section(base_profile.get("hud_layout"))
		if hl is not None:
			new_profile["hud_layout"] = hl
	os.makedirs(os.path.join(PROFILES_DIR, new_id), exist_ok=True)
	copy_profile_binding_files_from_base(base_profile["id"], new_id)
	new_profile = _normalize_profile(new_profile, len(data["profiles"]) + 1)
	data["profiles"].append(new_profile)
	data["active_profile"] = new_id
	invalidate_profile_cache()
	return new_profile


def sync_active_profile_to_legacy_files(data):
	profile = get_active_profile(data)
	persist_profile_bindings_to_files(profile)
	fmt = get_active_bindings_format_key(profile)
	pid = profile["id"]
	im = profile.get("input_mode", "teclado")

	keyboard_data = _read_json_file(BINDINGS_PATH, {})
	if not isinstance(keyboard_data, dict):
		keyboard_data = {}
	if im == "hitbox":
		kb_slice = get_slice(load_bindings_tree(path_hitbox_bindings(pid)), fmt)
	elif im == "mixbox":
		kb_slice = get_slice(load_bindings_tree(path_mixbox_bindings(pid)), fmt)
	else:
		kb_slice = get_slice(load_bindings_tree(path_key_bindings(pid)), fmt)
	keyboard_data[fmt] = kb_slice
	_write_json_file(BINDINGS_PATH, keyboard_data)

	joystick_data = _read_json_file(JOYSTICK_BINDINGS_PATH, {})
	if not isinstance(joystick_data, dict):
		joystick_data = {}
	joy_slice = get_slice(load_bindings_tree(path_joystick_bindings(pid)), fmt)
	joystick_data[fmt] = joy_slice
	_write_json_file(JOYSTICK_BINDINGS_PATH, joystick_data)
