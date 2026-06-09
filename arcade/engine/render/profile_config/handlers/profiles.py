from core.assets_resolver import invalidate_profile_cache
from profiles import create_profile, get_active_profile
from profiles.profile_export import export_profile_to_zip, import_profile_from_zip
from render.profile_config.modals import (
	_run_choice_menu,
	_run_message_modal,
	_run_text_input,
)
from utils.file_picker import pick_directory, pick_zip_file


def _h_create_profile(menu, active_profile, window_mode):
	create_profile(menu.profile_data, get_active_profile(menu.profile_data))
	return None


def _h_rename_profile(menu, active_profile, window_mode):
	t = _run_text_input(
		menu.screen,
		"Nombre del perfil (solo interfaz)",
		active_profile.get("name", ""),
		window_mode=window_mode,
	)
	if t is None:
		return None
	name = (t or "").strip()
	if not name:
		_run_message_modal(
			menu.screen,
			"Nombre",
			["El nombre no puede estar vacio."],
			window_mode=window_mode,
		)
		return None
	active_profile["name"] = name
	invalidate_profile_cache(active_profile.get("id"))
	return None


def _h_export_profile(menu, active_profile, window_mode):
	dest_dir = pick_directory(title="Guardar perfil en...")
	if not dest_dir:
		return None
	zip_path = export_profile_to_zip(active_profile, dest_dir)
	if zip_path:
		_run_message_modal(
			menu.screen,
			"Exportado",
			[f"Perfil guardado en {zip_path}"],
			window_mode=window_mode,
		)
	else:
		_run_message_modal(
			menu.screen,
			"Error",
			["No se pudo exportar el perfil."],
			window_mode=window_mode,
		)
	return None


def _h_import_profile(menu, active_profile, window_mode):
	zip_path = pick_zip_file(title="Seleccionar perfil ZIP")
	if not zip_path:
		return None

	def conflict_resolver(imported_name):
		choice = _run_choice_menu(
			menu.screen,
			f"Perfil '{imported_name}' ya existe",
			["Sobrescribir", "Renombrar (_importado)", "Cancelar"],
			0,
			window_mode=window_mode,
		)
		if choice is None or choice == 2:
			return "cancel"
		if choice == 0:
			return "overwrite"
		return "rename"

	try:
		imported = import_profile_from_zip(
			zip_path, menu.profile_data, conflict_resolver=conflict_resolver
		)
		if imported:
			_run_message_modal(
				menu.screen,
				"Importado",
				[f"Perfil '{imported['name']}' importado correctamente."],
				window_mode=window_mode,
			)
	except ValueError as e:
		_run_message_modal(menu.screen, "Error", [str(e)], window_mode=window_mode)
	return None
