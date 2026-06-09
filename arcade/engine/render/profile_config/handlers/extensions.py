from render.profile_config.modals import _run_message_modal


def _h_extensions_info(menu, active_profile, window_mode):
	_run_message_modal(
		menu.screen,
		"Extensiones",
		[
			"Hooks en core/extensions_runtime.py.",
			"Opcion B: semantic_binding en perfil para plugins.",
		],
		window_mode=window_mode,
	)
	return None
