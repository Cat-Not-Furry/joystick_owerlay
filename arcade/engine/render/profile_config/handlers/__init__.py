from render.profile_config.handlers.advanced import _h_update_overlay
from render.profile_config.handlers.devices import (
	_h_active_profile,
	_h_button_count,
	_h_default_input,
	_h_global_keyboard,
	_h_toggle_profile,
)
from render.profile_config.handlers.extensions import _h_extensions_info
from render.profile_config.handlers.general import (
	_h_cancel,
	_h_capture_mode,
	_h_mono_font,
	_h_save_and_back,
	_h_toggle_local_backups,
	_h_toggle_mirror_xdg,
)
from render.profile_config.handlers.profiles import (
	_h_create_profile,
	_h_export_profile,
	_h_import_profile,
	_h_rename_profile,
)
from render.profile_config.handlers.visualization import (
	_h_button_color,
	_h_change_icon,
	_h_controller_style,
	_h_edit_hud_layout,
	_h_joystick_color,
	_h_joystick_color_hex,
	_h_toggle_icon_pack_lock,
)

_OPTION_HANDLERS = {
	"tournament_mode": lambda m, p, w: _h_toggle_profile(m, p, w, "tournament_mode"),
	"hitbox_alt_layout": lambda m, p, w: _h_toggle_profile(m, p, w, "hitbox_alt_layout"),
	"local_backups": _h_toggle_local_backups,
	"mirror_xdg_profiles": _h_toggle_mirror_xdg,
	"capture_mode": _h_capture_mode,
	"mono_font": _h_mono_font,
	"controller_style": _h_controller_style,
	"active_profile": _h_active_profile,
	"button_count": _h_button_count,
	"default_input": _h_default_input,
	"global_keyboard": _h_global_keyboard,
	"joystick_color": _h_joystick_color,
	"button_color": _h_button_color,
	"joystick_color_hex": _h_joystick_color_hex,
	"change_icon": _h_change_icon,
	"create_profile": _h_create_profile,
	"rename_profile": _h_rename_profile,
	"toggle_icon_pack_lock": _h_toggle_icon_pack_lock,
	"edit_hud_layout": _h_edit_hud_layout,
	"export_profile": _h_export_profile,
	"import_profile": _h_import_profile,
	"update_overlay": _h_update_overlay,
	"extensions_info": _h_extensions_info,
	"save_and_back": _h_save_and_back,
	"cancel": _h_cancel,
}
