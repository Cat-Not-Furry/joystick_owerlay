import subprocess
import sys

from render.profile_config.modals import (
	_repo_root,
	_run_message_modal,
	_run_update_modal,
)
from utils.file_picker import pick_zip_file


def _h_update_overlay(menu, active_profile, window_mode):
	zip_path = pick_zip_file(title="Seleccionar ZIP de actualizacion")
	if not zip_path:
		return None
	result = _run_update_modal(menu.screen, zip_path, window_mode=window_mode)
	if result == "open_hud":
		main_path = str(_repo_root() / "main.py")
		try:
			subprocess.Popen(
				[sys.executable, main_path],
				cwd=str(_repo_root()),
				start_new_session=True,
			)
		except Exception as error:
			_run_message_modal(
				menu.screen,
				"Abrir HUD",
				[f"No se pudo abrir HUD: {error}"],
				window_mode=window_mode,
			)
	return None
