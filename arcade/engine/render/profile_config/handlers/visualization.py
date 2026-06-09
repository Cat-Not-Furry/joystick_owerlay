from config import (
	BUTTON_COLOR_PRESETS,
	DEFAULT_ICON_PACK,
	JOYSTICK_COLOR_PRESETS,
	SUPPORTED_CONTROLLER_STYLES,
	parse_hex_color,
	rgb_to_hex,
	suggested_icon_pack_for_style,
)
from core.assets_resolver import invalidate_profile_cache
from render.hud_layout_editor import run_hud_layout_editor
from render.profile_config.handlers.general import _h_choice
from render.profile_config.modals import (
	_button_color_preset_name,
	_color_name_from_values,
	_run_choice_menu,
	_run_text_input,
)


def _h_controller_style(menu, active_profile, window_mode):
	def get(p, _): return p.get("controller_style", "default")
	def set_val(p, _, v):
		old_pack = str(p.get("icon_pack", DEFAULT_ICON_PACK))
		p["controller_style"] = v
		if not p.get("icon_pack_locked", False):
			p["icon_pack"] = suggested_icon_pack_for_style(v)
		new_pack = str(p.get("icon_pack", DEFAULT_ICON_PACK))
		if old_pack != new_pack and isinstance(p.get("button_icons"), dict):
			for lbl, val in list(p["button_icons"].items()):
				if isinstance(val, str) and "icon_packs" in val.replace("\\", "/"):
					p["button_icons"][lbl] = None
		invalidate_profile_cache(p.get("id"))
	return _h_choice(menu, active_profile, window_mode, "Estilo de control", SUPPORTED_CONTROLLER_STYLES, get, set_val)


def _h_change_icon(menu, active_profile, window_mode):
	menu._handle_change_icon(active_profile, window_mode)
	return None


def _h_toggle_icon_pack_lock(menu, active_profile, window_mode):
	active_profile["icon_pack_locked"] = not bool(active_profile.get("icon_pack_locked", False))
	invalidate_profile_cache(active_profile.get("id"))
	return None


def _h_joystick_color(menu, active_profile, window_mode):
	names = list(JOYSTICK_COLOR_PRESETS.keys())
	try:
		idx = names.index(_color_name_from_values(active_profile["joystick_color"]))
	except ValueError:
		idx = 0
	chosen = _run_choice_menu(menu.screen, "Color joystick", names, idx, window_mode=window_mode)
	if chosen is not None:
		col = list(JOYSTICK_COLOR_PRESETS[names[chosen]])
		active_profile["joystick_color"] = col
		active_profile["joystick_knob_color"] = list(col)
	return None


def _h_button_color(menu, active_profile, window_mode):
	names = list(BUTTON_COLOR_PRESETS.keys())
	try:
		idx = names.index(_button_color_preset_name(
			active_profile.get("button_color_inactive", [80, 80, 80]),
			active_profile.get("button_color_active", [255, 0, 0]),
		))
	except ValueError:
		idx = 0
	chosen = _run_choice_menu(menu.screen, "Color de botones", names, idx, window_mode=window_mode)
	if chosen is not None:
		preset = BUTTON_COLOR_PRESETS[names[chosen]]
		active_profile["button_color_inactive"] = list(preset["inactive"])
		active_profile["button_color_active"] = list(preset["active"])
	return None


def _h_joystick_color_hex(menu, active_profile, window_mode):
	knob_hex = rgb_to_hex(active_profile.get("joystick_knob_color", active_profile.get("joystick_color", [0, 255, 0])))
	bar_hex = rgb_to_hex(active_profile.get("joystick_bar_color", [0, 0, 0]))
	ring_hex = rgb_to_hex(active_profile.get("joystick_ring_color", [255, 255, 255]))
	knob_t = _run_text_input(menu.screen, "Hex joystick (knob)", knob_hex, window_mode=window_mode)
	if knob_t is None:
		return None
	bar_t = _run_text_input(menu.screen, "Hex barra (stick)", bar_hex, window_mode=window_mode)
	if bar_t is None:
		return None
	ring_t = _run_text_input(menu.screen, "Hex anillo", ring_hex, window_mode=window_mode)
	if ring_t is None:
		return None
	knob_c = parse_hex_color(knob_t)
	bar_c = parse_hex_color(bar_t)
	ring_c = parse_hex_color(ring_t)
	if knob_c and bar_c and ring_c:
		active_profile["joystick_knob_color"] = knob_c
		active_profile["joystick_bar_color"] = bar_c
		active_profile["joystick_ring_color"] = ring_c
		active_profile["joystick_color"] = list(knob_c)
	return None


def _h_edit_hud_layout(menu, active_profile, window_mode):
	run_hud_layout_editor(menu.screen, active_profile, window_mode=window_mode)
	invalidate_profile_cache(active_profile.get("id"))
	return None
