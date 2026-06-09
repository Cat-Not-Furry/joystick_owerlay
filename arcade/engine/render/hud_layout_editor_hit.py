# render/hud_layout_editor_hit.py — hit-test de handles del editor HUD (ARCH-002 A)

_DIR_EDIT_ORDER = ("LEFT", "UP", "DOWN", "RIGHT")


def pick_drag_target(
	mx,
	my,
	dsx,
	dsy,
	btn_screen,
	labels,
	dir_xy,
	scale,
	r,
	idx_first_btn,
	idx_sys_select,
	idx_sys_start,
	dir_screen_fn,
	sys_screen_fn,
):
	"""Retorna (dragging_key, active_handle) o (None, None) si no hay hit."""
	if (mx - dsx) ** 2 + (my - dsy) ** 2 <= r * r:
		return "dirs", 0
	if dir_xy is not None:
		for i, dk in enumerate(_DIR_EDIT_ORDER):
			dcx, dcy = dir_screen_fn(dk, scale)
			if (mx - dcx) ** 2 + (my - dcy) ** 2 <= r * r:
				return dk, 1 + i
	for i, lb in enumerate(labels):
		bx, by = btn_screen[lb]
		if (mx - bx) ** 2 + (my - by) ** 2 <= r * r:
			return lb, idx_first_btn + i
	for sl in ("SELECT", "START"):
		sx, sy = sys_screen_fn(sl, scale)
		if (mx - sx) ** 2 + (my - sy) ** 2 <= r * r:
			handle = idx_sys_select if sl == "SELECT" else idx_sys_start
			return sl, handle
	return None, None
