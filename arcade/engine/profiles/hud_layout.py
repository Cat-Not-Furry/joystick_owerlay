# profiles/hud_layout.py
# Normalizacion y resolucion de offsets HUD (coords base + escala).

from copy import deepcopy

from config import (
	SCREEN_WIDTH,
	SCREEN_HEIGHT,
	JOYSTICK_CENTER,
	BUTTON_RADIUS,
	HITBOX_MIXBOX_DIRECTION_LEFT,
	HUD_SYSTEM_ROW_Y,
	HUD_SYSTEM_PAIR_SPREAD,
	get_hud_scale,
	get_button_positions,
	get_button_positions_hitbox_mixbox,
	get_button_labels,
	get_hud_layout_variant_key,
	normalize_controller_style,
	layout_four_variant_4a_from_profile,
)

HUD_LAYOUT_VARIANT_KEYS = (
	"formato_4",
	"formato_4a",
	"formato_6",
	"formato_8",
)

_SUPPORTED_LAYOUTS = frozenset({"stick", "hitbox", "mixbox"})
_SUPPORTED_POINT_KEYS = frozenset({"dirs_group", "buttons_group"})
_ALL_BUTTON_LABELS = frozenset(
	{"LP", "LK", "HP", "HK", "MP", "MK", "TR", "BR"}
)
_SYSTEM_BUTTON_LABELS = frozenset({"SELECT", "START"})
_DIRECTION_PAD_KEYS = ("LEFT", "UP", "DOWN", "RIGHT")
_DIRECTION_PAD_LABELS = frozenset(_DIRECTION_PAD_KEYS)


def _is_num(v):
	return isinstance(v, (int, float))


def _clamp(v, lo, hi):
	return max(lo, min(hi, v))


def _default_base_resolution():
	return [SCREEN_WIDTH, SCREEN_HEIGHT]


def default_dirs_ref_base(input_layout):
	if input_layout in ("hitbox", "mixbox"):
		return (float(HITBOX_MIXBOX_DIRECTION_LEFT), 85.0)
	return (float(JOYSTICK_CENTER[0]), float(JOYSTICK_CENTER[1]))


def default_system_base_by_label(
	button_count, input_layout, controller_style=None, layout_four_variant_4a=False
):
	"""Centros Select/Start en coords base (misma lógica que get_system_button_positions sin escalar)."""
	style = normalize_controller_style(controller_style)
	if input_layout in ("hitbox", "mixbox"):
		pts = get_button_positions_hitbox_mixbox(
			button_count,
			SCREEN_WIDTH,
			SCREEN_HEIGHT,
			controller_style=style,
			layout_four_variant_4a=layout_four_variant_4a,
		)
	else:
		pts = get_button_positions(
			button_count,
			SCREEN_WIDTH,
			SCREEN_HEIGHT,
			controller_style=style,
			layout_four_variant_4a=layout_four_variant_4a,
		)
	if not pts:
		mid = 260.0
	else:
		mid = sum(p[0] for p in pts) / len(pts)
	yb = int(HUD_SYSTEM_ROW_Y)
	sx = int(mid - HUD_SYSTEM_PAIR_SPREAD)
	dx = int(mid + HUD_SYSTEM_PAIR_SPREAD)
	return {
		"SELECT": (float(sx), float(yb)),
		"START": (float(dx), float(yb)),
	}


def default_buttons_ref_base(
	button_count, input_layout, controller_style=None, layout_four_variant_4a=False
):
	style = normalize_controller_style(controller_style)
	if input_layout in ("hitbox", "mixbox"):
		pts = get_button_positions_hitbox_mixbox(
			button_count,
			SCREEN_WIDTH,
			SCREEN_HEIGHT,
			controller_style=style,
			layout_four_variant_4a=layout_four_variant_4a,
		)
	else:
		pts = get_button_positions(
			button_count,
			SCREEN_WIDTH,
			SCREEN_HEIGHT,
			controller_style=style,
			layout_four_variant_4a=layout_four_variant_4a,
		)
	if not pts:
		return (195.0, 90.0)
	sx = sum(p[0] for p in pts) / len(pts)
	sy = sum(p[1] for p in pts) / len(pts)
	return (float(sx), float(sy))


def _normalize_point(pt, bw, bh):
	if not isinstance(pt, dict):
		return None
	x, y = pt.get("x"), pt.get("y")
	if not _is_num(x) or not _is_num(y):
		return None
	return {
		"x": int(_clamp(int(x), 0, bw)),
		"y": int(_clamp(int(y), 0, bh)),
	}


def _normalize_button_positions(raw_bp, bw, bh):
	if not isinstance(raw_bp, dict):
		return {}
	out = {}
	for lbl, pt in raw_bp.items():
		ul = str(lbl).strip().upper()
		if ul not in _ALL_BUTTON_LABELS:
			continue
		n = _normalize_point(pt, bw, bh)
		if n:
			out[ul] = n
	return out


def _normalize_system_button_positions(raw_bp, bw, bh):
	if not isinstance(raw_bp, dict):
		return {}
	out = {}
	for lbl, pt in raw_bp.items():
		ul = str(lbl).strip().upper()
		if ul not in _SYSTEM_BUTTON_LABELS:
			continue
		n = _normalize_point(pt, bw, bh)
		if n:
			out[ul] = n
	return out


def _normalize_direction_positions(raw_dp, bw, bh):
	if not isinstance(raw_dp, dict):
		return {}
	out = {}
	for lbl, pt in raw_dp.items():
		ul = str(lbl).strip().upper()
		if ul not in _DIRECTION_PAD_LABELS:
			continue
		n = _normalize_point(pt, bw, bh)
		if n:
			out[ul] = n
	return out


def compute_direction_centers_screen(
	screen_w, screen_h, input_layout, hitbox_alt_layout, dirs_offset
):
	"""
	Centros en pixeles de pantalla de cada direccional (LEFT/UP/DOWN/RIGHT).
	Misma geometria que draw_hitbox_direction_pad / draw_mixbox_direction_pad.
	"""
	if input_layout not in ("hitbox", "mixbox"):
		return {}
	ox, oy = int(dirs_offset[0]), int(dirs_offset[1])
	scale = get_hud_scale(screen_w, screen_h)
	base_x = int(HITBOX_MIXBOX_DIRECTION_LEFT * scale) + ox
	base_y = int(85 * scale) + oy
	if input_layout == "hitbox":
		radius = max(8, int(BUTTON_RADIUS * scale))
		gap = max(4, int(8 * scale))
		sh = int(screen_h)
		max_d_vertical = min(base_y - radius, sh - base_y - radius)
		d = min(radius * 2 + gap, max(max_d_vertical, radius))
		if hitbox_alt_layout:
			return {
				"LEFT": (base_x, base_y),
				"UP": (base_x + d, base_y),
				"DOWN": (base_x + d * 2, base_y),
				"RIGHT": (base_x + d * 3, base_y),
			}
		offset_v = d
		return {
			"LEFT": (base_x, base_y - offset_v),
			"UP": (base_x + d, base_y - offset_v // 2),
			"DOWN": (base_x + d * 2, base_y + offset_v // 2),
			"RIGHT": (base_x + d * 3, base_y + offset_v),
		}
	w = max(24, int(36 * scale))
	h = max(20, int(28 * scale))
	gap = max(4, int(6 * scale))

	def _rect_center(tlx, tly):
		return (int(tlx + w // 2), int(tly + h // 2))

	return {
		"UP": _rect_center(base_x + w + gap, base_y - (h + gap)),
		"LEFT": _rect_center(base_x, base_y),
		"DOWN": _rect_center(base_x + w + gap, base_y),
		"RIGHT": _rect_center(base_x + (w + gap) * 2, base_y),
	}


def default_direction_centers_base(
	anchor_x, anchor_y, input_layout, hitbox_alt_layout
):
	"""Centros direccionales en coords base (pantalla base 375x175, escala 1)."""
	if input_layout not in ("hitbox", "mixbox"):
		return {}
	sc = get_hud_scale(SCREEN_WIDTH, SCREEN_HEIGHT)
	doff = (
		int((float(anchor_x) - float(HITBOX_MIXBOX_DIRECTION_LEFT)) * sc),
		int((float(anchor_y) - 85.0) * sc),
	)
	centers = compute_direction_centers_screen(
		SCREEN_WIDTH, SCREEN_HEIGHT, input_layout, hitbox_alt_layout, doff
	)
	inv = 1.0 / sc if sc else 1.0
	return {k: (float(centers[k][0]) * inv, float(centers[k][1]) * inv) for k in centers}


def _normalize_elements_dict(els, bw, bh):
	out = {}
	if not isinstance(els, dict):
		return out
	for k, pt in els.items():
		if k in _SUPPORTED_POINT_KEYS:
			n = _normalize_point(pt, bw, bh)
			if n:
				out[k] = n
		elif k == "button_positions":
			bp = _normalize_button_positions(pt, bw, bh)
			if bp:
				out["button_positions"] = bp
		elif k == "system_button_positions":
			sp = _normalize_system_button_positions(pt, bw, bh)
			if sp:
				out["system_button_positions"] = sp
		elif k == "direction_positions":
			dp = _normalize_direction_positions(pt, bw, bh)
			if dp:
				out["direction_positions"] = dp
	return out


def _normalize_mode_overrides_dict(mo, bw, bh):
	out = {}
	if not isinstance(mo, dict):
		return out
	for mode, sub in mo.items():
		if mode not in _SUPPORTED_LAYOUTS or not isinstance(sub, dict):
			continue
		mode_out = _normalize_elements_dict(sub, bw, bh)
		if mode_out:
			out[mode] = mode_out
	return out


def _normalize_variant_block(raw, bw, bh):
	if not isinstance(raw, dict):
		raw = {}
	return {
		"elements": _normalize_elements_dict(raw.get("elements", {}), bw, bh),
		"mode_overrides": _normalize_mode_overrides_dict(
			raw.get("mode_overrides", {}), bw, bh
		),
	}


def normalize_hud_layout_section(raw):
	"""Normaliza dict hud_layout del perfil. Retorna dict seguro o None."""
	if raw is None:
		return None
	if not isinstance(raw, dict):
		return None
	br = raw.get("base_resolution", _default_base_resolution())
	if (
		not isinstance(br, (list, tuple))
		or len(br) != 2
		or not _is_num(br[0])
		or not _is_num(br[1])
	):
		bw, bh = _default_base_resolution()
	else:
		bw = int(max(1, br[0]))
		bh = int(max(1, br[1]))
	out = {
		"version": int(raw.get("version", 1)),
		"base_resolution": [bw, bh],
		"elements": {},
		"mode_overrides": {},
		"variants": {},
	}
	out["elements"] = _normalize_elements_dict(raw.get("elements", {}), bw, bh)
	out["mode_overrides"] = _normalize_mode_overrides_dict(
		raw.get("mode_overrides", {}), bw, bh
	)
	variants_out = {}
	vraw = raw.get("variants")
	if isinstance(vraw, dict):
		for vk in HUD_LAYOUT_VARIANT_KEYS:
			if vk not in vraw:
				continue
			nb = _normalize_variant_block(vraw[vk], bw, bh)
			if nb["elements"] or nb["mode_overrides"]:
				variants_out[vk] = nb
	out["variants"] = variants_out
	return out


def effective_hud_layout_elements_for_variant(normalized_hud, variant_key):
	"""Slice elements + mode_overrides para un formato (o legado en raíz)."""
	if not normalized_hud:
		return {"elements": {}, "mode_overrides": {}}
	v = normalized_hud.get("variants") or {}
	if variant_key in v and isinstance(v[variant_key], dict):
		block = v[variant_key]
		return {
			"elements": dict(block.get("elements") or {}),
			"mode_overrides": dict(block.get("mode_overrides") or {}),
		}
	return {
		"elements": dict(normalized_hud.get("elements") or {}),
		"mode_overrides": dict(normalized_hud.get("mode_overrides") or {}),
	}


def hud_layout_dict_for_editor(profile_hud, variant_key):
	"""Documento mínimo que entiende el editor (una variante activa)."""
	n = normalize_hud_layout_section(profile_hud)
	if not n:
		return None
	eff = effective_hud_layout_elements_for_variant(n, variant_key)
	return {
		"version": int(n.get("version", 1)),
		"base_resolution": list(n.get("base_resolution", _default_base_resolution())),
		"elements": eff["elements"],
		"mode_overrides": eff["mode_overrides"],
	}


def merge_hud_layout_variant(profile_hud, variant_key, elements, mode_overrides):
	"""Inserta o sustituye variants[variant_key]; devuelve hud_layout normalizado."""
	base = normalize_hud_layout_section(profile_hud)
	bw, bh = _default_base_resolution()
	if base is None:
		base = {
			"version": 1,
			"base_resolution": [bw, bh],
			"elements": {},
			"mode_overrides": {},
			"variants": {},
		}
	else:
		bw, bh = int(base["base_resolution"][0]), int(base["base_resolution"][1])
	variants = dict(base.get("variants") or {})
	variants[str(variant_key)] = _normalize_variant_block(
		{"elements": elements, "mode_overrides": mode_overrides},
		bw,
		bh,
	)
	rebuilt = {**base, "variants": variants}
	return normalize_hud_layout_section(rebuilt)


def _merged_elements(normalized, input_layout):
	if not normalized:
		return {}
	merged = deepcopy(normalized.get("elements", {}))
	ov = normalized.get("mode_overrides", {}).get(input_layout, {})
	for k, v in ov.items():
		if k == "button_positions" and isinstance(v, dict):
			base_bp = merged.get("button_positions", {})
			if not isinstance(base_bp, dict):
				base_bp = {}
			merged["button_positions"] = {**base_bp, **deepcopy(v)}
		elif k == "system_button_positions" and isinstance(v, dict):
			base_sp = merged.get("system_button_positions", {})
			if not isinstance(base_sp, dict):
				base_sp = {}
			merged["system_button_positions"] = {**base_sp, **deepcopy(v)}
		elif k == "direction_positions" and isinstance(v, dict):
			base_dp = merged.get("direction_positions", {})
			if not isinstance(base_dp, dict):
				base_dp = {}
			merged["direction_positions"] = {**base_dp, **deepcopy(v)}
		else:
			merged[k] = dict(v) if isinstance(v, dict) else v
	return merged


def _default_button_base_by_label(
	button_count, input_layout, controller_style=None, layout_four_variant_4a=False
):
	style = normalize_controller_style(controller_style)
	if input_layout in ("hitbox", "mixbox"):
		pts = get_button_positions_hitbox_mixbox(
			button_count,
			SCREEN_WIDTH,
			SCREEN_HEIGHT,
			controller_style=style,
			layout_four_variant_4a=layout_four_variant_4a,
		)
	else:
		pts = get_button_positions(
			button_count,
			SCREEN_WIDTH,
			SCREEN_HEIGHT,
			controller_style=style,
			layout_four_variant_4a=layout_four_variant_4a,
		)
	labels = get_button_labels(button_count)
	return {labels[i]: (float(pts[i][0]), float(pts[i][1])) for i in range(len(labels))}


def resolve_hud_layout_offsets(profile, screen_w, screen_h, input_layout, button_count):
	"""
	Retorna offsets en pixeles de pantalla para dirs, botones y Select/Start.
	input_layout: stick | hitbox | mixbox
	button_pixel_offsets: lista paralela a labels, offset total por boton (uniforme + granular).
	system_button_pixel_offsets: [(dx,dy) select, (dx,dy) start] respecto a posicion por defecto.
	direction_button_pixel_offsets: dict LEFT/UP/DOWN/RIGHT -> (dx,dy) en hitbox/mixbox, opcional.
	"""
	if input_layout not in _SUPPORTED_LAYOUTS:
		input_layout = "stick"
	controller_style = normalize_controller_style(
		profile.get("controller_style") if isinstance(profile, dict) else None
	)
	four_a = button_count == 4 and layout_four_variant_4a_from_profile(profile)
	variant_key = get_hud_layout_variant_key(button_count, four_a)
	scale = get_hud_scale(screen_w, screen_h)
	d_def = default_dirs_ref_base(input_layout)
	b_def = default_buttons_ref_base(
		button_count, input_layout, controller_style, layout_four_variant_4a=four_a
	)
	dx_off, dy_off = 0, 0
	bx_off, by_off = 0, 0
	raw = None
	if isinstance(profile, dict):
		raw = profile.get("hud_layout")
	norm = normalize_hud_layout_section(raw)
	labels = get_button_labels(button_count)
	base_by = _default_button_base_by_label(
		button_count, input_layout, controller_style, layout_four_variant_4a=four_a
	)
	per_button = None
	sys_pixel = [(0, 0), (0, 0)]
	dir_pixel = {}
	hit_alt = bool(profile.get("hitbox_alt_layout")) if isinstance(profile, dict) else False
	merged = {}
	if norm:
		eff = effective_hud_layout_elements_for_variant(norm, variant_key)
		pseudo = {"elements": eff["elements"], "mode_overrides": eff["mode_overrides"]}
		merged = _merged_elements(pseudo, input_layout)
		dg = merged.get("dirs_group")
		bg = merged.get("buttons_group")
		if dg:
			dx_off = int((dg["x"] - d_def[0]) * scale)
			dy_off = int((dg["y"] - d_def[1]) * scale)
		if bg:
			bx_off = int((bg["x"] - b_def[0]) * scale)
			by_off = int((bg["y"] - b_def[1]) * scale)
		bp = merged.get("button_positions") or {}
		if isinstance(bp, dict) and bp:
			per_button = []
			for lbl in labels:
				db = base_by.get(lbl, (0.0, 0.0))
				ex = bx_off
				ey = by_off
				if lbl in bp:
					ex += int((bp[lbl]["x"] - db[0]) * scale)
					ey += int((bp[lbl]["y"] - db[1]) * scale)
				per_button.append((ex, ey))
		sys_def = default_system_base_by_label(
			button_count, input_layout, controller_style, layout_four_variant_4a=four_a
		)
		sp = merged.get("system_button_positions") or {}
		if isinstance(sp, dict):
			for i, lbl in enumerate(("SELECT", "START")):
				db = sys_def[lbl]
				if lbl in sp:
					sx = float(sp[lbl]["x"])
					sy = float(sp[lbl]["y"])
					sys_pixel[i] = (
						int((sx - db[0]) * scale),
						int((sy - db[1]) * scale),
					)
	if input_layout in ("hitbox", "mixbox"):
		def_dirs_screen = compute_direction_centers_screen(
			screen_w, screen_h, input_layout, hit_alt, (dx_off, dy_off)
		)
		dp = merged.get("direction_positions") or {}
		if isinstance(dp, dict):
			for k in _DIRECTION_PAD_KEYS:
				sx0, sy0 = def_dirs_screen.get(k, (0, 0))
				if k in dp:
					ux = float(dp[k]["x"])
					uy = float(dp[k]["y"])
					sux = int(ux * scale)
					suy = int(uy * scale)
					dir_pixel[k] = (sux - sx0, suy - sy0)
				else:
					dir_pixel[k] = (0, 0)
	if per_button is None:
		per_button = [(bx_off, by_off) for _ in labels]
	return {
		"dirs_offset": (dx_off, dy_off),
		"buttons_offset": (bx_off, by_off),
		"button_pixel_offsets": per_button,
		"scale": scale,
		"layout_four_variant_4a": four_a,
		"system_offset": (0, 0),
		"system_button_pixel_offsets": sys_pixel,
		"direction_button_pixel_offsets": dir_pixel,
	}
