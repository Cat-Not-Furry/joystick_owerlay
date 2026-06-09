import os

import pygame

from config import PROFILES_DIR, get_button_labels, get_default_icon_path
from core.assets_resolver import invalidate_profile_cache
from profiles import get_active_profile
from render.profile_config.constants import _SECTION_KEYS
from render.profile_config.handlers import _OPTION_HANDLERS
from render.profile_config.modals import (
	_available_icon_paths,
	_button_color_preset_name,
	_color_name_from_values,
	_run_choice_menu,
	_run_message_modal,
)
from utils import draw_centered_text, draw_text_left, fit_text_to_width, set_ui_font_family
from utils.image_file_picker import pick_image_file_with_validation
from utils.safe_paths import path_is_under_root


class ProfileConfigMenu:
	TABLE_CELLS = [
		["local_backups", "capture_mode"],
		["mirror_xdg_profiles", "mono_font"],
		["active_profile", "button_count"],
		["controller_style", "default_input"],
		["joystick_color", "button_color"],
		["global_keyboard", "tournament_mode"],
	]
	ACTIONS_ROW = [
		"hitbox_alt_layout",
		"change_icon",
		"create_profile",
		"rename_profile",
		"toggle_icon_pack_lock",
		"joystick_color_hex",
		"edit_hud_layout",
		"export_profile",
		"import_profile",
		"update_overlay",
		"save_and_back",
		"cancel",
	]

	@property
	def OPTION_KEYS(self):
		flat = []
		for row in self.TABLE_CELLS:
			flat.extend(row)
		flat.extend(self.ACTIONS_ROW)
		return flat

	def __init__(self, screen, profile_data):
		self.screen = screen
		self.profile_data = profile_data
		self.selected = 0
		self.snapshot = self._make_snapshot()

	def _make_snapshot(self):
		return {
			"active_profile": self.profile_data["active_profile"],
			"window_mode": "normal",
			"ignore_videoresize": False,
			"capture_mode": self.profile_data.get("capture_mode", "normal"),
			"ui_font_family": self.profile_data.get("ui_font_family", "JetBrainsMono"),
			"backups_enabled": bool(self.profile_data.get("backups_enabled", True)),
			"xdg_mirror_enabled": bool(self.profile_data.get("xdg_mirror_enabled", True)),
			"backup_prompt_completed": bool(
				self.profile_data.get("backup_prompt_completed", True)
			),
			"profiles": [
				{
					**p,
					"joystick_color": list(p["joystick_color"]),
					"button_icons": dict(p["button_icons"]),
					"key_bindings": dict(p.get("key_bindings") or {}),
					"joystick_bindings": dict(p.get("joystick_bindings") or {}),
					"button_color_inactive": list(p.get("button_color_inactive", [80, 80, 80])),
					"button_color_active": list(p.get("button_color_active", [255, 0, 0])),
				}
				for p in self.profile_data["profiles"]
			],
		}

	def _get_option_labels(self, active_profile, window_mode, ui_font_family, keyboard_label):
		tournament_text = "On" if active_profile.get("tournament_mode", False) else "Off"
		alt_text = "On" if active_profile.get("hitbox_alt_layout", False) else "Off"
		btn_inactive = active_profile.get("button_color_inactive", [80, 80, 80])
		btn_active = active_profile.get("button_color_active", [255, 0, 0])
		btn_color_name = _button_color_preset_name(btn_inactive, btn_active)
		return {
			"tournament_mode": f"Torneo | {tournament_text}",
			"hitbox_alt_layout": f"Pos. Hitbox | {alt_text}",
			"local_backups": (
				f"Backups locales | {'Si' if self.profile_data.get('backups_enabled', True) else 'No'}"
			),
			"mirror_xdg_profiles": (
				f"Espejo datos sistema | {'Si' if self.profile_data.get('xdg_mirror_enabled', True) else 'No'}"
			),
			"capture_mode": f"Captura | {'OBS' if self.profile_data.get('capture_mode') == 'obs_green' else 'Normal'}",
			"mono_font": f"Fuente | {ui_font_family}",
			"controller_style": f"Control | {active_profile.get('controller_style', 'default')}",
			"active_profile": f"Perfil | {active_profile['name']}",
			"button_count": (
				f"Botones | {active_profile['button_count']}"
				+ (
					" (4A)"
					if active_profile.get("button_count") == 4
					and bool(active_profile.get("layout_four_variant_4a", False))
					else ""
				)
			),
			"default_input": f"Entrada | {active_profile['input_mode']}",
			"global_keyboard": f"Teclado | {'ninguno' if not active_profile.get('preferred_keyboard_path') else 'dispositivo'}",
			"joystick_color": f"Color stick | {_color_name_from_values(active_profile['joystick_color'])}",
			"joystick_color_hex": "Color joystick hexa",
			"button_color": f"Color botones | {btn_color_name}",
			"change_icon": "Cambiar icono",
			"create_profile": "Crear perfil",
			"rename_profile": "Renombrar perfil",
			"toggle_icon_pack_lock": (
				f"Pack iconos fijo | {'Si' if active_profile.get('icon_pack_locked') else 'No'}"
			),
			"edit_hud_layout": "Editar posicion HUD",
			"export_profile": "Exportar perfil",
			"import_profile": "Importar perfil",
			"update_overlay": "Actualizar overlay",
			"extensions_info": "Extensiones (informacion)",
			"save_and_back": "Guardar y volver",
			"cancel": "Cancelar",
		}

	def _render(self, active_profile, option_labels, font, line_gap):
		screen = self.screen
		screen.fill((0, 0, 0))
		padding_x = 12
		screen_width = screen.get_width()
		col_width = screen_width // 2
		title_y = max(20, line_gap)
		draw_centered_text(screen, font, "Configuracion de perfiles", y=title_y)
		table_y = title_y + line_gap + 4
		for row_idx, row_keys in enumerate(self.TABLE_CELLS):
			row_y = table_y + row_idx * line_gap
			for col_idx, key in enumerate(row_keys):
				x = padding_x + col_idx * col_width
				label = option_labels.get(key, key)
				trimmed = fit_text_to_width(font, f"{label}", col_width - 20)
				prefix = ">" if self._key_to_index(key) == self.selected else " "
				draw_text_left(screen, font, f"{prefix}{trimmed}", x, row_y)
		actions_y = table_y + len(self.TABLE_CELLS) * line_gap + 8
		for vi, key in enumerate(self.ACTIONS_ROW):
			idx = self._key_to_index(key)
			prefix = ">" if idx == self.selected else " "
			label = fit_text_to_width(font, option_labels[key], col_width - 20)
			draw_text_left(screen, font, f"{prefix}{label}", padding_x + (vi % 2) * col_width, actions_y + (vi // 2) * line_gap)
		draw_centered_text(screen, font, "Flechas + Enter | Esc", y=screen.get_height() - 16)

	def _key_to_index(self, key):
		for i, k in enumerate(self.OPTION_KEYS):
			if k == key:
				return i
		return -1

	def _handle_option(self, key, active_profile, window_mode):
		handler = _OPTION_HANDLERS.get(key)
		if handler is None:
			return None
		return handler(self, active_profile, window_mode)

	def _handle_change_icon(self, active_profile, window_mode):
		labels = get_button_labels(active_profile["button_count"])
		label_choice = _run_choice_menu(self.screen, "Selecciona boton", labels, 0, window_mode=window_mode)
		if label_choice is None:
			return
		label = labels[label_choice]
		icon_opts = _available_icon_paths(labels, active_profile["id"])
		cur_icon = active_profile["button_icons"].get(label, get_default_icon_path(label))
		if cur_icon and cur_icon not in icon_opts:
			icon_opts.append(cur_icon)
		try:
			icon_idx = icon_opts.index(cur_icon)
		except ValueError:
			icon_idx = 0
		icon_choice = _run_choice_menu(self.screen, f"Icono para {label}", icon_opts, icon_idx, window_mode=window_mode)
		if icon_choice is None:
			return
		sel = icon_opts[icon_choice]
		if sel == "ninguno":
			active_profile["button_icons"][label] = None
		elif sel == "Seleccionar...":
			prof_root = os.path.join(PROFILES_DIR, str(active_profile["id"]))
			icons_dir = os.path.join(prof_root, "icons")
			os.makedirs(icons_dir, exist_ok=True)
			chosen_file, err = pick_image_file_with_validation(
				initial_dir=icons_dir, max_width=512, max_height=512
			)
			if chosen_file and path_is_under_root(prof_root, chosen_file):
				active_profile["button_icons"][label] = os.path.relpath(chosen_file, prof_root)
			elif err:
				_run_message_modal(
					self.screen,
					"Icono invalido",
					[err, "Solo se permiten imagenes <= 512x512."],
					window_mode=window_mode,
				)
		else:
			active_profile["button_icons"][label] = sel

	def _process_config_keydown(self, event, selected, n, cols):
		"""Procesa KEYDOWN del menu config. Retorna (new_selected, action) con action en (None, 'quit', 'save', 'cancel')."""
		if event.key == pygame.K_ESCAPE:
			return selected, "quit"
		if event.key == pygame.K_RETURN:
			return selected, "enter"
		if event.key not in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
			return selected, None
		row, col = selected // cols, selected % cols
		if event.key == pygame.K_UP:
			row = max(0, row - 1)
		elif event.key == pygame.K_DOWN:
			row = min((n - 1) // cols, row + 1)
		elif event.key == pygame.K_LEFT:
			col = max(0, col - 1)
		else:
			col = min(cols - 1, col + 1)
		return min(row * cols + col, n - 1), None

	def run(self):
		clock = pygame.time.Clock()
		section_titles = list(_SECTION_KEYS.keys()) + ["Guardar y volver"]
		while True:
			sec_idx = _run_choice_menu(
				self.screen,
				"Preferencias (secciones)",
				section_titles,
				0,
				window_mode="normal",
			)
			if sec_idx is None:
				return None
			if sec_idx == len(_SECTION_KEYS):
				return self.profile_data
			section_name = list(_SECTION_KEYS.keys())[sec_idx]
			keys = _SECTION_KEYS[section_name]
			while True:
				set_ui_font_family(self.profile_data.get("ui_font_family", "JetBrainsMono"))
				active_profile = get_active_profile(self.profile_data)
				window_mode = "normal"
				ui_font_family = self.profile_data.get("ui_font_family", "JetBrainsMono")
				keyboard_path = active_profile.get("preferred_keyboard_path")
				keyboard_label = "ninguno (foco)" if not keyboard_path else keyboard_path
				option_labels = self._get_option_labels(active_profile, window_mode, ui_font_family, keyboard_label)
				sub_labels = [option_labels[k] for k in keys] + ["Volver"]
				if section_name == "Dispositivos":

					def _refresh_dispositivos_options():
						ap = get_active_profile(self.profile_data)
						kp = ap.get("preferred_keyboard_path")
						kbl = "ninguno (foco)" if not kp else kp
						wm = "normal"
						ff = self.profile_data.get("ui_font_family", "JetBrainsMono")
						ol = self._get_option_labels(ap, wm, ff, kbl)
						return [ol[k] for k in keys] + ["Volver"]

					def _on_tab_dispositivos(sel):
						if sel < 0 or sel >= len(keys):
							return
						if keys[sel] != "button_count":
							return
						ap = get_active_profile(self.profile_data)
						if ap.get("button_count") != 4:
							return
						ap["layout_four_variant_4a"] = not bool(ap.get("layout_four_variant_4a", False))
						invalidate_profile_cache(ap.get("id"))

					footer_dispositivos = "Flechas + Enter | Esc | Tab en Botones (solo 4): alternar 4A"
					sub_idx = _run_choice_menu(
						self.screen,
						f"Seccion: {section_name}",
						sub_labels,
						0,
						window_mode=window_mode,
						refresh_options=_refresh_dispositivos_options,
						on_tab=_on_tab_dispositivos,
						footer_extra=footer_dispositivos,
					)
				else:
					sub_idx = _run_choice_menu(
						self.screen,
						f"Seccion: {section_name}",
						sub_labels,
						0,
						window_mode=window_mode,
					)
				if sub_idx is None:
					return None
				if sub_idx == len(keys):
					break
				key = keys[sub_idx]
				result = self._handle_option(key, active_profile, window_mode)
				if result == "save":
					return self.profile_data
				if result == "cancel":
					return None
			clock.tick(60)


def open_profile_config_menu(screen, profile_data):
	menu = ProfileConfigMenu(screen, profile_data)
	return menu.run()
