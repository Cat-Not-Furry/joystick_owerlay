# render/hud_layout_editor.py
# Editor visual de posicion HUD (stick + cada boton en coords base).

import pygame

from config import (
	SCREEN_WIDTH,
	SCREEN_HEIGHT,
	get_hud_scale,
	get_button_labels,
	get_hud_layout_variant_key,
	normalize_controller_style,
	layout_four_variant_4a_from_profile,
)
from profiles.hud_layout import (
	default_dirs_ref_base,
	default_buttons_ref_base,
	default_system_base_by_label,
	default_direction_centers_base,
	normalize_hud_layout_section,
	resolve_hud_layout_offsets,
	merge_hud_layout_variant,
	hud_layout_dict_for_editor,
	_merged_elements,
	_default_button_base_by_label,
)

_DIR_EDIT_ORDER = ("LEFT", "UP", "DOWN", "RIGHT")
from utils import draw_centered_text, build_responsive_font
from core.assets_resolver import resolve_icons_map_from_profile_dict
from render.hud_renderer import (
	draw_hud,
	load_icons,
	load_system_icons,
	set_stick_color,
	set_stick_colors,
	set_button_colors,
	set_controller_style,
	set_render_mode,
	set_input_layout,
	set_hitbox_alt_layout,
)


def _profile_layout_key(profile):
	mode = profile.get("input_mode", "teclado")
	if mode == "mixbox":
		return "mixbox"
	if mode == "hitbox":
		return "hitbox"
	return "stick"


def _apply_profile_visual(profile, button_count):
	resolved = resolve_icons_map_from_profile_dict(profile, button_count)
	load_icons(button_count, resolved, enable_icons=True)
	load_system_icons(profile)
	set_stick_color(profile.get("joystick_color", [0, 255, 0]))
	set_stick_colors(
		profile.get("joystick_knob_color", profile.get("joystick_color", [0, 255, 0])),
		profile.get("joystick_bar_color", [0, 0, 0]),
		profile.get("joystick_ring_color", [255, 255, 255]),
	)
	set_button_colors(
		profile.get("button_color_inactive", [80, 80, 80]),
		profile.get("button_color_active", [255, 0, 0]),
	)
	set_controller_style(profile.get("controller_style", "default"))
	set_render_mode("normal")
	layout = (
		"mixbox"
		if profile.get("input_mode") == "mixbox"
		else ("hitbox" if profile.get("input_mode") == "hitbox" else "stick")
	)
	set_input_layout(layout)
	set_hitbox_alt_layout(profile.get("hitbox_alt_layout", False))


def _working_hud_layout_dict(
	layout_key, button_count, dirs_xy, button_xy_map, sys_xy_map, dir_xy_map=None
):
	els = {
		"dirs_group": {"x": int(dirs_xy[0]), "y": int(dirs_xy[1])},
		"button_positions": {
			lbl: {"x": int(button_xy_map[lbl][0]), "y": int(button_xy_map[lbl][1])}
			for lbl in button_xy_map
		},
		"system_button_positions": {
			sl: {"x": int(sys_xy_map[sl][0]), "y": int(sys_xy_map[sl][1])}
			for sl in ("SELECT", "START")
		},
	}
	if dir_xy_map:
		els["direction_positions"] = {
			k: {"x": int(dir_xy_map[k][0]), "y": int(dir_xy_map[k][1])}
			for k in _DIR_EDIT_ORDER
		}
	out = {
		"version": 1,
		"base_resolution": [SCREEN_WIDTH, SCREEN_HEIGHT],
		"elements": els,
		"mode_overrides": {},
	}
	if layout_key != "stick":
		out["mode_overrides"][layout_key] = dict(els)
	return out


def _screen_to_base(pos, scale):
	return (float(pos[0]) / scale, float(pos[1]) / scale)


def _clamp_base(xy):
	return (
		max(0, min(SCREEN_WIDTH, xy[0])),
		max(0, min(SCREEN_HEIGHT, xy[1])),
	)


def _snap_val(v, grid):
	if grid <= 0:
		return v
	return round(v / grid) * grid


def _init_editor_state(layout_key, button_count, raw_profile_hud, active_profile=None):
	ap = active_profile if isinstance(active_profile, dict) else {}
	ctrl = normalize_controller_style(ap.get("controller_style"))
	four_a = layout_four_variant_4a_from_profile(ap)
	d_def = default_dirs_ref_base(layout_key)
	b_def = default_buttons_ref_base(
		button_count, layout_key, ctrl, layout_four_variant_4a=four_a
	)
	base_by = _default_button_base_by_label(
		button_count, layout_key, ctrl, layout_four_variant_4a=four_a
	)
	dsys = default_system_base_by_label(
		button_count, layout_key, ctrl, layout_four_variant_4a=four_a
	)
	labels = get_button_labels(button_count)
	btn_xy = {lbl: (base_by[lbl][0], base_by[lbl][1]) for lbl in labels}
	sys_xy = {
		"SELECT": (dsys["SELECT"][0], dsys["SELECT"][1]),
		"START": (dsys["START"][0], dsys["START"][1]),
	}
	dirs_xy = (d_def[0], d_def[1])
	norm = normalize_hud_layout_section(raw_profile_hud) if raw_profile_hud is not None else None
	merged = None
	if norm and norm.get("elements"):
		merged = _merged_elements(norm, layout_key)
		dg = merged.get("dirs_group")
		if dg:
			dirs_xy = (float(dg["x"]), float(dg["y"]))
		bp = merged.get("button_positions") or {}
		bg = merged.get("buttons_group")
		if isinstance(bp, dict) and bp:
			for lbl in labels:
				if lbl in bp:
					btn_xy[lbl] = (float(bp[lbl]["x"]), float(bp[lbl]["y"]))
		elif bg:
			dx = float(bg["x"]) - b_def[0]
			dy = float(bg["y"]) - b_def[1]
			for lbl in labels:
				btn_xy[lbl] = (base_by[lbl][0] + dx, base_by[lbl][1] + dy)
		sp = merged.get("system_button_positions") or {}
		for sl in ("SELECT", "START"):
			pt = sp.get(sl)
			if isinstance(pt, dict):
				x, y = pt.get("x"), pt.get("y")
				if isinstance(x, (int, float)) and isinstance(y, (int, float)):
					sys_xy[sl] = (float(x), float(y))
	dir_xy = None
	if layout_key in ("hitbox", "mixbox"):
		hit_alt_i = bool(ap.get("hitbox_alt_layout", False))
		dcb = default_direction_centers_base(
			dirs_xy[0], dirs_xy[1], layout_key, hit_alt_i
		)
		dir_xy = {k: (dcb[k][0], dcb[k][1]) for k in _DIR_EDIT_ORDER}
		if merged:
			dp = merged.get("direction_positions") or {}
			for dk in dir_xy:
				pt = dp.get(dk)
				if isinstance(pt, dict):
					x, y = pt.get("x"), pt.get("y")
					if isinstance(x, (int, float)) and isinstance(y, (int, float)):
						dir_xy[dk] = (float(x), float(y))
	return dirs_xy, btn_xy, sys_xy, dir_xy


def run_hud_layout_editor(screen, active_profile, window_mode="floating_hint"):
	"""
	Editor de layout HUD. Guarda en active_profile['hud_layout'] con S.
	Tab: ancla direccional, cada tecla L U D R (hitbox/mixbox), botones de accion, Select y Start.
	"""
	button_count = active_profile.get("button_count", 6)
	layout_key = _profile_layout_key(active_profile)
	variant_key = get_hud_layout_variant_key(
		button_count, layout_four_variant_4a_from_profile(active_profile)
	)
	labels = get_button_labels(button_count)
	ctrl = normalize_controller_style(active_profile.get("controller_style"))
	four_a = layout_four_variant_4a_from_profile(active_profile)
	d_def = default_dirs_ref_base(layout_key)
	b_def = default_buttons_ref_base(
		button_count, layout_key, ctrl, layout_four_variant_4a=four_a
	)
	base_by = _default_button_base_by_label(
		button_count, layout_key, ctrl, layout_four_variant_4a=four_a
	)
	dsys_default = default_system_base_by_label(
		button_count, layout_key, ctrl, layout_four_variant_4a=four_a
	)
	editor_hud = hud_layout_dict_for_editor(
		active_profile.get("hud_layout"), variant_key
	)
	dirs_xy, btn_xy, sys_xy, dir_xy = _init_editor_state(
		layout_key, button_count, editor_hud, active_profile
	)
	hit_alt_ed = bool(active_profile.get("hitbox_alt_layout", False))
	snap_on = False
	snap_grid = 4
	nlab = len(labels)
	n_dir = 4 if layout_key in ("hitbox", "mixbox") else 0
	idx_first_btn = 1 + n_dir
	idx_sys_select = idx_first_btn + nlab
	idx_sys_start = idx_first_btn + nlab + 1
	n_handles = 1 + n_dir + nlab + 2
	# Hitbox/mixbox: 0 ancla, 1-4 = L U D R, luego botones, Sel, St. Stick: 0 stick, botones, Sel, St.
	active_handle = 0
	dragging = None
	clock = pygame.time.Clock()
	preview_state = {
		"stick": [0.0, 0.0],
		"buttons": [False] * nlab,
		"select": False,
		"start": False,
	}
	_apply_profile_visual(active_profile, button_count)

	def _preview_profile():
		p = dict(active_profile)
		w = _working_hud_layout_dict(
			layout_key,
			button_count,
			dirs_xy,
			btn_xy,
			sys_xy,
			dir_xy if layout_key in ("hitbox", "mixbox") else None,
		)
		p["hud_layout"] = merge_hud_layout_variant(
			active_profile.get("hud_layout"),
			variant_key,
			w.get("elements", {}),
			w.get("mode_overrides", {}),
		)
		return p

	def _layout_offsets_for_preview():
		return resolve_hud_layout_offsets(
			_preview_profile(),
			screen.get_width(),
			screen.get_height(),
			layout_key,
			button_count,
		)

	def _dirs_screen(scale):
		return (int(dirs_xy[0] * scale), int(dirs_xy[1] * scale))

	def _button_screen(lbl, scale):
		x, y = btn_xy[lbl]
		return (int(x * scale), int(y * scale))

	def _sys_screen(sl, scale):
		x, y = sys_xy[sl]
		return (int(x * scale), int(y * scale))

	def _dir_screen(dk, scale):
		if dir_xy is None:
			return (0, 0)
		x, y = dir_xy[dk]
		return (int(x * scale), int(y * scale))

	while True:
		sw, sh = screen.get_width(), screen.get_height()
		scale = get_hud_scale(sw, sh)
		dsx, dsy = _dirs_screen(scale)
		btn_screen = {lbl: _button_screen(lbl, scale) for lbl in labels}
		ssel_x, ssel_y = _sys_screen("SELECT", scale)
		ssta_x, ssta_y = _sys_screen("START", scale)
		r = max(10, int(14 * scale))

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return False
				if event.key == pygame.K_s:
					w = _working_hud_layout_dict(
						layout_key,
						button_count,
						dirs_xy,
						btn_xy,
						sys_xy,
						dir_xy if layout_key in ("hitbox", "mixbox") else None,
					)
					active_profile["hud_layout"] = merge_hud_layout_variant(
						active_profile.get("hud_layout"),
						variant_key,
						w.get("elements", {}),
						w.get("mode_overrides", {}),
					)
					return True
				if event.key == pygame.K_r:
					dirs_xy = (d_def[0], d_def[1])
					btn_xy = {lbl: (base_by[lbl][0], base_by[lbl][1]) for lbl in labels}
					sys_xy = {
						"SELECT": (
							dsys_default["SELECT"][0],
							dsys_default["SELECT"][1],
						),
						"START": (
							dsys_default["START"][0],
							dsys_default["START"][1],
						),
					}
					if dir_xy is not None:
						dcb = default_direction_centers_base(
							d_def[0], d_def[1], layout_key, hit_alt_ed
						)
						for dk in _DIR_EDIT_ORDER:
							dir_xy[dk] = (dcb[dk][0], dcb[dk][1])
				if event.key == pygame.K_TAB:
					active_handle = (active_handle + 1) % n_handles
				if event.key == pygame.K_g:
					snap_on = not snap_on
				if event.key == pygame.K_1:
					snap_grid = 4
				if event.key == pygame.K_2:
					snap_grid = 8
				step = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
				if event.key == pygame.K_LEFT:
					if active_handle == 0:
						if dir_xy is not None:
							for dk in dir_xy:
								dir_xy[dk] = (dir_xy[dk][0] - step, dir_xy[dk][1])
						dirs_xy = (dirs_xy[0] - step, dirs_xy[1])
					elif n_dir and 1 <= active_handle <= n_dir:
						dk = _DIR_EDIT_ORDER[active_handle - 1]
						dir_xy[dk] = (dir_xy[dk][0] - step, dir_xy[dk][1])
					elif idx_first_btn <= active_handle < idx_first_btn + nlab:
						lb = labels[active_handle - idx_first_btn]
						btn_xy[lb] = (btn_xy[lb][0] - step, btn_xy[lb][1])
					elif active_handle == idx_sys_select:
						sys_xy["SELECT"] = (
							sys_xy["SELECT"][0] - step,
							sys_xy["SELECT"][1],
						)
					elif active_handle == idx_sys_start:
						sys_xy["START"] = (
							sys_xy["START"][0] - step,
							sys_xy["START"][1],
						)
				elif event.key == pygame.K_RIGHT:
					if active_handle == 0:
						if dir_xy is not None:
							for dk in dir_xy:
								dir_xy[dk] = (dir_xy[dk][0] + step, dir_xy[dk][1])
						dirs_xy = (dirs_xy[0] + step, dirs_xy[1])
					elif n_dir and 1 <= active_handle <= n_dir:
						dk = _DIR_EDIT_ORDER[active_handle - 1]
						dir_xy[dk] = (dir_xy[dk][0] + step, dir_xy[dk][1])
					elif idx_first_btn <= active_handle < idx_first_btn + nlab:
						lb = labels[active_handle - idx_first_btn]
						btn_xy[lb] = (btn_xy[lb][0] + step, btn_xy[lb][1])
					elif active_handle == idx_sys_select:
						sys_xy["SELECT"] = (
							sys_xy["SELECT"][0] + step,
							sys_xy["SELECT"][1],
						)
					elif active_handle == idx_sys_start:
						sys_xy["START"] = (
							sys_xy["START"][0] + step,
							sys_xy["START"][1],
						)
				elif event.key == pygame.K_UP:
					if active_handle == 0:
						if dir_xy is not None:
							for dk in dir_xy:
								dir_xy[dk] = (dir_xy[dk][0], dir_xy[dk][1] - step)
						dirs_xy = (dirs_xy[0], dirs_xy[1] - step)
					elif n_dir and 1 <= active_handle <= n_dir:
						dk = _DIR_EDIT_ORDER[active_handle - 1]
						dir_xy[dk] = (dir_xy[dk][0], dir_xy[dk][1] - step)
					elif idx_first_btn <= active_handle < idx_first_btn + nlab:
						lb = labels[active_handle - idx_first_btn]
						btn_xy[lb] = (btn_xy[lb][0], btn_xy[lb][1] - step)
					elif active_handle == idx_sys_select:
						sys_xy["SELECT"] = (
							sys_xy["SELECT"][0],
							sys_xy["SELECT"][1] - step,
						)
					elif active_handle == idx_sys_start:
						sys_xy["START"] = (
							sys_xy["START"][0],
							sys_xy["START"][1] - step,
						)
				elif event.key == pygame.K_DOWN:
					if active_handle == 0:
						if dir_xy is not None:
							for dk in dir_xy:
								dir_xy[dk] = (dir_xy[dk][0], dir_xy[dk][1] + step)
						dirs_xy = (dirs_xy[0], dirs_xy[1] + step)
					elif n_dir and 1 <= active_handle <= n_dir:
						dk = _DIR_EDIT_ORDER[active_handle - 1]
						dir_xy[dk] = (dir_xy[dk][0], dir_xy[dk][1] + step)
					elif idx_first_btn <= active_handle < idx_first_btn + nlab:
						lb = labels[active_handle - idx_first_btn]
						btn_xy[lb] = (btn_xy[lb][0], btn_xy[lb][1] + step)
					elif active_handle == idx_sys_select:
						sys_xy["SELECT"] = (
							sys_xy["SELECT"][0],
							sys_xy["SELECT"][1] + step,
						)
					elif active_handle == idx_sys_start:
						sys_xy["START"] = (
							sys_xy["START"][0],
							sys_xy["START"][1] + step,
						)
				dirs_xy = _clamp_base(dirs_xy)
				for lb in labels:
					btn_xy[lb] = _clamp_base(btn_xy[lb])
				sys_xy["SELECT"] = _clamp_base(sys_xy["SELECT"])
				sys_xy["START"] = _clamp_base(sys_xy["START"])
				if dir_xy is not None:
					for dk in dir_xy:
						dir_xy[dk] = _clamp_base(dir_xy[dk])
				if snap_on:
					dirs_xy = (_snap_val(dirs_xy[0], snap_grid), _snap_val(dirs_xy[1], snap_grid))
					for lb in labels:
						btn_xy[lb] = (
							_snap_val(btn_xy[lb][0], snap_grid),
							_snap_val(btn_xy[lb][1], snap_grid),
						)
					sys_xy["SELECT"] = (
						_snap_val(sys_xy["SELECT"][0], snap_grid),
						_snap_val(sys_xy["SELECT"][1], snap_grid),
					)
					sys_xy["START"] = (
						_snap_val(sys_xy["START"][0], snap_grid),
						_snap_val(sys_xy["START"][1], snap_grid),
					)
					if dir_xy is not None:
						for dk in dir_xy:
							dir_xy[dk] = (
								_snap_val(dir_xy[dk][0], snap_grid),
								_snap_val(dir_xy[dk][1], snap_grid),
							)
					dirs_xy = _clamp_base(dirs_xy)
					for lb in labels:
						btn_xy[lb] = _clamp_base(btn_xy[lb])
					sys_xy["SELECT"] = _clamp_base(sys_xy["SELECT"])
					sys_xy["START"] = _clamp_base(sys_xy["START"])
					if dir_xy is not None:
						for dk in dir_xy:
							dir_xy[dk] = _clamp_base(dir_xy[dk])
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				mx, my = event.pos
				if (mx - dsx) ** 2 + (my - dsy) ** 2 <= r * r:
					dragging = "dirs"
					active_handle = 0
				else:
					hit_dir = False
					if dir_xy is not None:
						for i, dk in enumerate(_DIR_EDIT_ORDER):
							dcx, dcy = _dir_screen(dk, scale)
							if (mx - dcx) ** 2 + (my - dcy) ** 2 <= r * r:
								dragging = dk
								active_handle = 1 + i
								hit_dir = True
								break
					if not hit_dir:
						hit_btn = False
						for i, lb in enumerate(labels):
							bx, by = btn_screen[lb]
							if (mx - bx) ** 2 + (my - by) ** 2 <= r * r:
								dragging = lb
								active_handle = idx_first_btn + i
								hit_btn = True
								break
						if not hit_btn:
							for sl, (sx, sy) in (
								("SELECT", _sys_screen("SELECT", scale)),
								("START", _sys_screen("START", scale)),
							):
								if (mx - sx) ** 2 + (my - sy) ** 2 <= r * r:
									dragging = sl
									active_handle = (
										idx_sys_select if sl == "SELECT" else idx_sys_start
									)
									break
			elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				dragging = None
			elif event.type == pygame.MOUSEMOTION and dragging:
				bx, by = _screen_to_base(event.pos, scale)
				bx, by = _clamp_base((bx, by))
				if snap_on:
					bx = _snap_val(bx, snap_grid)
					by = _snap_val(by, snap_grid)
					bx, by = _clamp_base((bx, by))
				if dragging == "dirs":
					if dir_xy is not None:
						dax = bx - dirs_xy[0]
						day = by - dirs_xy[1]
						for dk in dir_xy:
							dir_xy[dk] = (dir_xy[dk][0] + dax, dir_xy[dk][1] + day)
					dirs_xy = (bx, by)
				elif dragging in btn_xy:
					btn_xy[dragging] = (bx, by)
				elif dir_xy is not None and dragging in dir_xy:
					dir_xy[dragging] = (bx, by)
				elif dragging in sys_xy:
					sys_xy[dragging] = (bx, by)

		lo = _layout_offsets_for_preview()
		bg = (20, 20, 30)
		screen.fill(bg)
		draw_hud(screen, preview_state, button_count, layout_offsets=lo)

		pygame.draw.circle(
			screen,
			(0, 200, 255) if active_handle == 0 else (100, 100, 120),
			(dsx, dsy),
			r,
			2,
		)
		for i, lb in enumerate(labels):
			bx, by = btn_screen[lb]
			pygame.draw.circle(
				screen,
				(255, 180, 0) if active_handle == idx_first_btn + i else (100, 100, 120),
				(bx, by),
				r,
				2,
			)
		if dir_xy is not None:
			dir_colors = (
				(180, 220, 255),
				(255, 200, 120),
				(200, 255, 180),
				(255, 180, 220),
			)
			for i, dk in enumerate(_DIR_EDIT_ORDER):
				dcx, dcy = _dir_screen(dk, scale)
				pygame.draw.circle(
					screen,
					dir_colors[i] if active_handle == 1 + i else (100, 100, 120),
					(dcx, dcy),
					r,
					2,
				)
		pygame.draw.circle(
			screen,
			(200, 120, 255) if active_handle == idx_sys_select else (100, 100, 120),
			(ssel_x, ssel_y),
			r,
			2,
		)
		pygame.draw.circle(
			screen,
			(120, 255, 200) if active_handle == idx_sys_start else (100, 100, 120),
			(ssta_x, ssta_y),
			r,
			2,
		)

		hud_lines = [
			"Editor posicion HUD",
			"Tab: ancla / (L U D R si hitbox-mixbox) / botones / Sel / St | Flechas | Shift: 10",
			"G: snap | 1: rejilla 4 | 2: rejilla 8",
			"S: guardar | Esc: cancelar | R: restablecer",
			f"Snap: {'on' if snap_on else 'off'} ({snap_grid}px)",
		]
		font, line_gap = build_responsive_font(
			screen,
			hud_lines,
			base_size=14,
			min_size=10,
			max_size=18,
			base_resolution=(460, 320),
			max_height_ratio=0.25,
		)
		ly = 6
		for i, line in enumerate(hud_lines):
			draw_centered_text(screen, font, line, y=ly + i * line_gap)

		pygame.display.flip()
		clock.tick(60)
