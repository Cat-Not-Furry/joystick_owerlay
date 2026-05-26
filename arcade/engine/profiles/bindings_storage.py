# profiles/bindings_storage.py
# Archivos JSON de bindings por perfil (teclado / hitbox / mixbox / joystick) por formato.

import json
import os
import shutil
import tempfile
from copy import deepcopy

from config import (
	PROFILES_DIR,
	BINDING_TEMPLATES_DIR,
	PROFILE_KEY_BINDINGS_FILENAME,
	PROFILE_HITBOX_BINDINGS_FILENAME,
	PROFILE_MIXBOX_BINDINGS_FILENAME,
	PROFILE_JOYSTICK_BINDINGS_FILENAME,
	get_button_labels,
	get_bindings_format_key,
	get_active_bindings_format_key,
)
from profiles.hud_layout import (
	effective_hud_layout_elements_for_variant,
	merge_hud_layout_variant,
	normalize_hud_layout_section,
)

ALL_FORMAT_KEYS = ("formato_4", "formato_4a", "formato_6", "formato_8")

_BINDING_VALUE_KEYS = frozenset(
	{
		"Arriba",
		"Abajo",
		"Izquierda",
		"Derecha",
		"SELECT",
		"START",
		"LP",
		"LK",
		"HP",
		"HK",
		"MP",
		"MK",
		"TR",
		"BR",
		"PPP",
		"KKK",
	}
)


def _is_binding_scalar(v):
	return v is None or isinstance(v, (int, float, bool))


def _is_flat_binding_map(d):
	if not isinstance(d, dict) or not d:
		return False
	if "bindings" in d:
		return False
	for k, v in d.items():
		if str(k) not in _BINDING_VALUE_KEYS:
			return False
		if not _is_binding_scalar(v):
			return False
	return True


def unpack_format_slab(slab):
	"""Un formato_* puede ser mapa plano (legacy) o {bindings, hud_layout?, button_icons?}."""
	if not isinstance(slab, dict):
		return {}, None, {}
	bind = slab.get("bindings")
	if isinstance(bind, dict):
		hud = slab.get("hud_layout")
		icons = slab.get("button_icons")
		if not isinstance(icons, dict):
			icons = {}
		return dict(bind), hud if isinstance(hud, dict) else None, dict(icons)
	if _is_flat_binding_map(slab):
		return dict(slab), None, {}
	return {}, None, {}


def pack_format_slab(bindings_flat, hud_layout=None, button_icons=None):
	"""Serializa un slot formato_*; si hay HUD o iconos extra, usa objeto anidado."""
	flat = dict(bindings_flat or {})
	hud_fragment = None
	if isinstance(hud_layout, dict):
		els = hud_layout.get("elements") or {}
		mo = hud_layout.get("mode_overrides") or {}
		if els or mo:
			hud_fragment = {"elements": dict(els), "mode_overrides": dict(mo)}
	icons_out = {}
	if isinstance(button_icons, dict):
		for k, v in button_icons.items():
			if v is not None and str(v).strip():
				icons_out[str(k).strip().upper()] = v
	if not hud_fragment and not icons_out:
		return flat
	out = {"bindings": flat}
	if hud_fragment:
		out["hud_layout"] = hud_fragment
	if icons_out:
		out["button_icons"] = icons_out
	return out


def labels_for_format_key(fk):
	if fk in ("formato_4", "formato_4a"):
		return get_button_labels(4)
	if fk == "formato_6":
		return get_button_labels(6)
	return get_button_labels(8)


def bindings_visual_storage_path(profile):
	im = profile.get("input_mode", "teclado")
	pid = str(profile.get("id") or "")
	if im == "joystick":
		return path_joystick_bindings(pid)
	if im == "hitbox":
		return path_hitbox_bindings(pid)
	if im == "mixbox":
		return path_mixbox_bindings(pid)
	return path_key_bindings(pid)


def _bindings_paths_for_augment(profile_id, input_mode):
	pid = str(profile_id)
	out = [path_key_bindings(pid)]
	im = input_mode or "teclado"
	if im == "hitbox":
		out.append(path_hitbox_bindings(pid))
	elif im == "mixbox":
		out.append(path_mixbox_bindings(pid))
	elif im == "joystick":
		out.append(path_joystick_bindings(pid))
	return out


def merge_hud_from_bindings_tree(base_hud, tree):
	if not isinstance(tree, dict):
		return base_hud
	out = normalize_hud_layout_section(base_hud)
	for fk in ALL_FORMAT_KEYS:
		_, frag, _ = unpack_format_slab(tree.get(fk))
		if not isinstance(frag, dict):
			continue
		els = frag.get("elements") or {}
		mo = frag.get("mode_overrides") or {}
		if not els and not mo:
			continue
		out = merge_hud_layout_variant(out, fk, els, mo)
	return out


def augment_profile_dict_with_bindings_sidecar(profile_dict):
	"""Fusiona hud_layout y button_icons desde JSON de bindings (tras leer profile.json)."""
	if not isinstance(profile_dict, dict):
		return
	pid = str(profile_dict.get("id") or "").strip()
	if not pid:
		return
	copy_binding_templates_to_profile(pid)
	base_hud = profile_dict.get("hud_layout")
	merged = None
	for path in _bindings_paths_for_augment(pid, profile_dict.get("input_mode", "teclado")):
		tree = load_bindings_tree(path)
		merged = merge_hud_from_bindings_tree(merged if merged is not None else base_hud, tree)
	if merged is not None:
		profile_dict["hud_layout"] = merged
	fmt = get_active_bindings_format_key(profile_dict)
	icons = dict(profile_dict.get("button_icons") or {})
	for path in _bindings_paths_for_augment(pid, profile_dict.get("input_mode", "teclado")):
		tree = load_bindings_tree(path)
		_, _, ic = unpack_format_slab(tree.get(fmt))
		if isinstance(ic, dict):
			for k, v in ic.items():
				if v is not None and str(v).strip():
					icons[str(k).strip().upper()] = v
	profile_dict["button_icons"] = icons


def persist_format_extras_to_bindings_file(profile):
	"""Escribe HUD por variante e iconos del formato activo en el JSON de bindings del modo."""
	pid = str(profile.get("id") or "")
	if not pid:
		return
	path = bindings_visual_storage_path(profile)
	tree = load_bindings_tree(path)
	norm = normalize_hud_layout_section(profile.get("hud_layout"))
	fmt_active = get_active_bindings_format_key(profile)
	p_icons = profile.get("button_icons") if isinstance(profile.get("button_icons"), dict) else {}
	for fk in ALL_FORMAT_KEYS:
		slab = tree.get(fk)
		flat, old_hud, old_icons = unpack_format_slab(slab if isinstance(slab, dict) else None)
		hud_fragment = None
		if norm:
			eff = effective_hud_layout_elements_for_variant(norm, fk)
			if eff.get("elements") or eff.get("mode_overrides"):
				hud_fragment = {
					"elements": dict(eff.get("elements") or {}),
					"mode_overrides": dict(eff.get("mode_overrides") or {}),
				}
		icons_out = dict(old_icons) if isinstance(old_icons, dict) else {}
		if fk == fmt_active:
			for lbl in labels_for_format_key(fk):
				lu = str(lbl).strip().upper()
				if lu in p_icons:
					icons_out[lu] = p_icons.get(lu)
		tree[fk] = pack_format_slab(flat, hud_fragment, icons_out)
	save_bindings_tree(path, tree)


def mirror_keyboard_hud_hitbox_mixbox(profile):
	"""Copia solo hud_layout/button_icons desde key_bindings a hitbox y mixbox (no toca bindings)."""
	pid = str(profile.get("id") or "")
	if not pid:
		return
	src_tree = load_bindings_tree(path_key_bindings(pid))
	for dst_path in (path_hitbox_bindings(pid), path_mixbox_bindings(pid)):
		dst_tree = load_bindings_tree(dst_path)
		for fk in ALL_FORMAT_KEYS:
			_, hud_s, icon_s = unpack_format_slab(src_tree.get(fk))
			if not hud_s and not (icon_s and any(icon_s.values())):
				continue
			flat, _, _ = unpack_format_slab(dst_tree.get(fk))
			dst_tree[fk] = pack_format_slab(flat, hud_s, icon_s)
		save_bindings_tree(dst_path, dst_tree)

# pygame/SDL2 keycodes (Linux): flechas + letras F,D,S,A,V,C,X,Z
_K_UP = 1073741906
_K_DOWN = 1073741905
_K_LEFT = 1073741904
_K_RIGHT = 1073741908
_KEY_F = 102
_KEY_D = 100
_KEY_S = 115
_KEY_A = 97
_KEY_V = 118
_KEY_C = 99
_KEY_X = 120
_KEY_Z = 122


def profile_dir(profile_id):
	return os.path.join(PROFILES_DIR, str(profile_id))


def path_key_bindings(profile_id):
	return os.path.join(profile_dir(profile_id), PROFILE_KEY_BINDINGS_FILENAME)


def path_hitbox_bindings(profile_id):
	return os.path.join(profile_dir(profile_id), PROFILE_HITBOX_BINDINGS_FILENAME)


def path_mixbox_bindings(profile_id):
	return os.path.join(profile_dir(profile_id), PROFILE_MIXBOX_BINDINGS_FILENAME)


def path_joystick_bindings(profile_id):
	return os.path.join(profile_dir(profile_id), PROFILE_JOYSTICK_BINDINGS_FILENAME)


def path_keyboard_family_file(profile_id, input_mode):
	if input_mode == "hitbox":
		return path_hitbox_bindings(profile_id)
	if input_mode == "mixbox":
		return path_mixbox_bindings(profile_id)
	return path_key_bindings(profile_id)


def _template_src(name):
	return os.path.join(BINDING_TEMPLATES_DIR, name)


def _write_json_atomic(path, data):
	d = os.path.dirname(path)
	if d:
		os.makedirs(d, exist_ok=True)
	fd, tmp = tempfile.mkstemp(prefix=".jb_", suffix=".json", dir=d or ".", text=True)
	try:
		with os.fdopen(fd, "w", encoding="utf-8") as fh:
			json.dump(data, fh, indent=4, ensure_ascii=True)
			fh.flush()
			os.fsync(fh.fileno())
		os.replace(tmp, path)
	except Exception:
		try:
			if os.path.exists(tmp):
				os.unlink(tmp)
		except Exception:
			pass
		raise


def _read_json(path, default):
	if not os.path.isfile(path):
		return default
	try:
		with open(path, "r", encoding="utf-8") as fh:
			raw = fh.read().strip()
			if not raw:
				return default
			return json.loads(raw)
	except Exception:
		return default


def _default_direction_keys():
	return {
		"Arriba": _K_UP,
		"Abajo": _K_DOWN,
		"Izquierda": _K_LEFT,
		"Derecha": _K_RIGHT,
	}


def _pack_keyboard_format(labels, letter_codes):
	m = dict(_default_direction_keys())
	for lbl, code in zip(labels, letter_codes):
		m[lbl] = code
	m["SELECT"] = None
	m["START"] = None
	return m


def build_default_keyboard_tree():
	"""Arbol completo formato_* -> mapa teclas (misma forma para key/hitbox/mixbox)."""
	l4 = get_button_labels(4)
	l6 = get_button_labels(6)
	l8 = get_button_labels(8)
	c4 = [_KEY_F, _KEY_D, _KEY_S, _KEY_A]
	c6 = [_KEY_F, _KEY_D, _KEY_S, _KEY_A, _KEY_V, _KEY_C]
	c8 = [_KEY_F, _KEY_D, _KEY_S, _KEY_A, _KEY_V, _KEY_C, _KEY_X, _KEY_Z]
	return {
		"formato_4": _pack_keyboard_format(l4, c4),
		"formato_4a": _pack_keyboard_format(l4, c4),
		"formato_6": _pack_keyboard_format(l6, c6),
		"formato_8": _pack_keyboard_format(l8, c8),
	}


def build_empty_joystick_tree():
	"""Cada formato: mismas claves que mapeo joystick, valores null."""
	out = {}
	for fk in ALL_FORMAT_KEYS:
		if fk in ("formato_4", "formato_4a"):
			labels = get_button_labels(4)
		elif fk == "formato_6":
			labels = get_button_labels(6)
		else:
			labels = get_button_labels(8)
		m = {lbl: None for lbl in labels}
		m["SELECT"] = None
		m["START"] = None
		out[fk] = m
	return out


def ensure_binding_templates():
	"""Escribe plantillas inmutables en ASSETS si faltan."""
	os.makedirs(BINDING_TEMPLATES_DIR, exist_ok=True)
	kt = build_default_keyboard_tree()
	jt = build_empty_joystick_tree()
	pairs = [
		(PROFILE_KEY_BINDINGS_FILENAME, kt),
		(PROFILE_HITBOX_BINDINGS_FILENAME, deepcopy(kt)),
		(PROFILE_MIXBOX_BINDINGS_FILENAME, deepcopy(kt)),
		(PROFILE_JOYSTICK_BINDINGS_FILENAME, jt),
	]
	for name, data in pairs:
		p = _template_src(name)
		if not os.path.isfile(p):
			_write_json_atomic(p, data)


def copy_binding_templates_to_profile(profile_id):
	"""Copia las 4 plantillas al directorio del perfil."""
	os.makedirs(profile_dir(profile_id), exist_ok=True)
	ensure_binding_templates()
	for name in (
		PROFILE_KEY_BINDINGS_FILENAME,
		PROFILE_HITBOX_BINDINGS_FILENAME,
		PROFILE_MIXBOX_BINDINGS_FILENAME,
		PROFILE_JOYSTICK_BINDINGS_FILENAME,
	):
		src = _template_src(name)
		dst = os.path.join(profile_dir(profile_id), name)
		if not os.path.isfile(dst) and os.path.isfile(src):
			shutil.copy2(src, dst)
		elif not os.path.isfile(dst):
			if name == PROFILE_JOYSTICK_BINDINGS_FILENAME:
				_write_json_atomic(dst, build_empty_joystick_tree())
			else:
				_write_json_atomic(dst, build_default_keyboard_tree())


def load_bindings_tree(path):
	data = _read_json(path, {})
	if not isinstance(data, dict):
		return {}
	# Aceptar archivo plano legacy (un solo mapa) -> tratar como formato_6 por defecto
	if any(k in data for k in ALL_FORMAT_KEYS):
		return data
	if data and all(isinstance(v, (int, type(None))) or isinstance(v, bool) for v in data.values()):
		return {"formato_6": data}
	return {}


def save_bindings_tree(path, tree):
	if not isinstance(tree, dict):
		tree = {}
	_write_json_atomic(path, tree)


def get_slice(tree, format_key):
	"""Solo mapa plano de bindings (compatible con legacy y con slabs anidados)."""
	if not isinstance(tree, dict):
		return {}
	slab = tree.get(format_key)
	bind, _, _ = unpack_format_slab(slab if isinstance(slab, dict) else None)
	return dict(bind) if isinstance(bind, dict) else {}


def set_slice(tree, format_key, flat_map):
	"""Sustituye bindings del formato; conserva hud_layout y button_icons del slab anterior."""
	if not isinstance(tree, dict):
		tree = {}
	if not isinstance(flat_map, dict):
		flat_map = {}
	slab = tree.get(format_key)
	_, hud, icons = unpack_format_slab(slab if isinstance(slab, dict) else None)
	tree[format_key] = pack_format_slab(flat_map, hud, icons)
	return tree


def migrate_inline_keyboard_into_tree(tree, inline_map, button_count):
	"""Inserta mapa plano legado en el slot del formato deducido por button_count."""
	if not isinstance(inline_map, dict) or not inline_map:
		return tree
	if not isinstance(tree, dict):
		tree = {}
	fk = get_bindings_format_key(button_count)
	return set_slice(tree, fk, inline_map)


def migrate_inline_joystick_into_tree(tree, inline_map, button_count):
	if not isinstance(inline_map, dict) or not inline_map:
		return tree
	if not isinstance(tree, dict):
		tree = {}
	fk = get_bindings_format_key(button_count)
	return set_slice(tree, fk, inline_map)


def normalize_flat_bindings_for_format_8(bindings_dict, button_count):
	"""Misma regla PPP/KKK -> TR/BR que profile_store."""
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


def _ensure_select_start(flat):
	out = dict(flat) if isinstance(flat, dict) else {}
	for k in ("SELECT", "START"):
		if k not in out:
			out[k] = None
	return out


def copy_profile_binding_files_from_base(src_profile_id, dst_profile_id):
	"""Copia los 4 JSON de bindings del perfil base al nuevo; si falta origen, plantillas."""
	ensure_binding_templates()
	os.makedirs(profile_dir(dst_profile_id), exist_ok=True)
	for name in (
		PROFILE_KEY_BINDINGS_FILENAME,
		PROFILE_HITBOX_BINDINGS_FILENAME,
		PROFILE_MIXBOX_BINDINGS_FILENAME,
		PROFILE_JOYSTICK_BINDINGS_FILENAME,
	):
		src = os.path.join(profile_dir(src_profile_id), name)
		dst = os.path.join(profile_dir(dst_profile_id), name)
		if os.path.isfile(src):
			shutil.copy2(src, dst)
		elif os.path.isfile(_template_src(name)):
			shutil.copy2(_template_src(name), dst)
		elif name == PROFILE_JOYSTICK_BINDINGS_FILENAME:
			_write_json_atomic(dst, build_empty_joystick_tree())
		else:
			_write_json_atomic(dst, build_default_keyboard_tree())


def migrate_inline_bindings_from_profile_json(profile_id, raw_profile, button_count, layout_four_variant_4a):
	"""
	Si profile.json trae key_bindings/joystick_bindings planos y el arbol en disco esta vacio
	en ese slot, copia al archivo por perfil.
	"""
	copy_binding_templates_to_profile(profile_id)
	key_inline = raw_profile.get("key_bindings") if isinstance(raw_profile, dict) else {}
	joy_inline = raw_profile.get("joystick_bindings") if isinstance(raw_profile, dict) else {}

	fk = get_bindings_format_key(button_count)
	kpath = path_key_bindings(profile_id)
	kt = load_bindings_tree(kpath)
	if isinstance(key_inline, dict) and key_inline:
		slot = get_slice(kt, fk)
		if not slot or not any(v is not None for v in slot.values()):
			kt = set_slice(kt, fk, key_inline)
		if button_count == 4 and layout_four_variant_4a:
			s4a = get_slice(kt, "formato_4a")
			if not s4a or not any(v is not None for v in s4a.values()):
				kt = set_slice(kt, "formato_4a", dict(key_inline))
		save_bindings_tree(kpath, kt)

	jpath = path_joystick_bindings(profile_id)
	jt = load_bindings_tree(jpath)
	if isinstance(joy_inline, dict) and joy_inline and any(v is not None for v in joy_inline.values()):
		slot = get_slice(jt, fk)
		if not slot or not any(v is not None for v in slot.values()):
			jt = set_slice(jt, fk, joy_inline)
		save_bindings_tree(jpath, jt)


def hydrate_profile_bindings(profile):
	"""Rellena profile['key_bindings'] y profile['joystick_bindings'] desde archivos (formato activo)."""
	pid = profile["id"]
	copy_binding_templates_to_profile(pid)
	fmt = get_active_bindings_format_key(profile)
	im = profile.get("input_mode", "teclado")
	bc = int(profile.get("button_count", 6) or 6)

	joy_tree = load_bindings_tree(path_joystick_bindings(pid))
	jflat = normalize_flat_bindings_for_format_8(get_slice(joy_tree, fmt), bc)
	profile["joystick_bindings"] = _ensure_select_start(jflat)

	if im == "hitbox":
		ktree = load_bindings_tree(path_hitbox_bindings(pid))
	elif im == "mixbox":
		ktree = load_bindings_tree(path_mixbox_bindings(pid))
	else:
		ktree = load_bindings_tree(path_key_bindings(pid))
	kflat = normalize_flat_bindings_for_format_8(get_slice(ktree, fmt), bc)
	profile["key_bindings"] = _ensure_select_start(kflat)
	augment_profile_dict_with_bindings_sidecar(profile)


def persist_profile_bindings_to_files(profile):
	"""Persiste los mapas planos del perfil en los JSON por formato activo."""
	pid = profile["id"]
	fmt = get_active_bindings_format_key(profile)
	im = profile.get("input_mode", "teclado")
	bc = int(profile.get("button_count", 6) or 6)

	js_flat = normalize_flat_bindings_for_format_8(dict(profile.get("joystick_bindings") or {}), bc)
	js_flat = _ensure_select_start(js_flat)
	jpath = path_joystick_bindings(pid)
	jt = load_bindings_tree(jpath)
	save_bindings_tree(jpath, set_slice(jt, fmt, js_flat))

	if im == "joystick":
		return
	kb_flat = normalize_flat_bindings_for_format_8(dict(profile.get("key_bindings") or {}), bc)
	kb_flat = _ensure_select_start(kb_flat)
	p = path_keyboard_family_file(pid, im)
	tree = load_bindings_tree(p)
	save_bindings_tree(p, set_slice(tree, fmt, kb_flat))


def profile_public_json_dict(profile):
	"""Copia del perfil para serializar en profile.json: sin bindings ni HUD/iconos en disco."""
	d = dict(profile)
	d.pop("key_bindings", None)
	d.pop("joystick_bindings", None)
	d.pop("hud_layout", None)
	d.pop("button_icons", None)
	return d
