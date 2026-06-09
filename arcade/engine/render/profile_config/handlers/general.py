from config import SUPPORTED_CAPTURE_MODES, SUPPORTED_MONO_FONT_FAMILIES
from profiles import save_profiles_data
from render.profile_config.modals import _run_choice_menu
from utils import set_ui_font_family


def _h_choice(menu, active_profile, window_mode, title, options, get_current, set_value):
	cur = get_current(active_profile, menu.profile_data)
	idx = options.index(cur) if cur in options else 0
	chosen = _run_choice_menu(menu.screen, title, options, idx, window_mode=window_mode)
	if chosen is not None:
		set_value(active_profile, menu.profile_data, options[chosen])
	return None


def _h_capture_mode(menu, active_profile, window_mode):
	pd = menu.profile_data
	idx = SUPPORTED_CAPTURE_MODES.index(pd.get("capture_mode", "normal")) if pd.get("capture_mode") in SUPPORTED_CAPTURE_MODES else 0
	pd["capture_mode"] = SUPPORTED_CAPTURE_MODES[(idx + 1) % len(SUPPORTED_CAPTURE_MODES)]
	return None


def _h_mono_font(menu, active_profile, window_mode):
	def get(ap, pd): return pd.get("ui_font_family", "JetBrainsMono")
	def set_val(ap, pd, v): pd["ui_font_family"] = v; set_ui_font_family(v)
	return _h_choice(menu, active_profile, window_mode, "Fuente mono", SUPPORTED_MONO_FONT_FAMILIES, get, set_val)


def _h_toggle_local_backups(menu, active_profile, window_mode):
	pd = menu.profile_data
	pd["backups_enabled"] = not bool(pd.get("backups_enabled", True))
	save_profiles_data(pd)
	return None


def _h_toggle_mirror_xdg(menu, active_profile, window_mode):
	pd = menu.profile_data
	pd["xdg_mirror_enabled"] = not bool(pd.get("xdg_mirror_enabled", True))
	save_profiles_data(pd)
	return None


def _h_cancel(menu, active_profile, window_mode):
	pd = menu.profile_data
	snap = menu.snapshot
	pd["active_profile"] = snap["active_profile"]
	pd["window_mode"] = snap["window_mode"]
	pd["ignore_videoresize"] = snap["ignore_videoresize"]
	pd["capture_mode"] = snap["capture_mode"]
	pd["ui_font_family"] = snap["ui_font_family"]
	pd["backups_enabled"] = snap.get("backups_enabled", True)
	pd["xdg_mirror_enabled"] = snap.get("xdg_mirror_enabled", True)
	pd["backup_prompt_completed"] = snap.get("backup_prompt_completed", True)
	pd["profiles"] = snap["profiles"]
	set_ui_font_family(pd["ui_font_family"])
	return "cancel"


def _h_save_and_back(menu, active_profile, window_mode):
	return "save"
