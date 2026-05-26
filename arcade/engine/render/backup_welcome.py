# render/backup_welcome.py
# Bienvenida: preferencias de copias locales y espejo bajo datos de aplicacion (XDG / equivalente).

import pygame

from config import BACKUP_PROFILES_ROOT
from profiles import save_profiles_data
from render.profile_config_menu import _run_message_modal
from utils import draw_centered_text, build_responsive_font, run_modal_child_window


def _yes_no_modal(surface, body_lines, default_no_on_escape=True):
	"""Arriba/Abajo elige Si o No; Enter confirma; Esc = No si default_no_on_escape."""
	selected = 1 if default_no_on_escape else 0
	clock = pygame.time.Clock()
	while True:
		lines = list(body_lines)
		lines.append("")
		lines.append(
			("> Si" if selected == 0 else "  Si")
			+ "     "
			+ ("> No" if selected == 1 else "  No")
		)
		lines.append("")
		lines.append("Enter: confirmar | Arriba/Abajo | Esc = No")
		font, line_gap = build_responsive_font(
			surface,
			lines,
			base_size=17,
			min_size=11,
			max_size=20,
			base_resolution=(560, 340),
			max_height_ratio=0.88,
		)
		surface.fill((0, 0, 0))
		y0 = max(18, line_gap)
		for i, line in enumerate(lines):
			draw_centered_text(surface, font, line, y=y0 + i * line_gap)
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return False
				if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
					selected = 1 - selected
				elif event.key == pygame.K_RETURN:
					return selected == 0
		clock.tick(60)


def run_backup_welcome_if_needed(screen, profile_data):
	"""
	Si backup_prompt_completed es False, pregunta por:
	1) copias en user/backups/ antes de sobrescribir perfiles;
	2) espejo opcional en BACKUP_PROFILES_ROOT (no se lee en runtime).
	"""
	if profile_data.get("backup_prompt_completed", True):
		return profile_data
	wm = profile_data.get("window_mode", "floating_hint")
	mirror_path = BACKUP_PROFILES_ROOT

	def _runner_local(s):
		return _yes_no_modal(
			s,
			[
				"Copias de seguridad locales (proyecto)",
				"¿Desea guardar copias en user/backups/ antes de",
				"cada sobrescritura de profile.json?",
			],
			default_no_on_escape=True,
		)

	wants_local = run_modal_child_window(
		title="Backups en proyecto",
		size=(560, 320),
		window_mode=wm,
		runner=_runner_local,
		screen=screen,
	)
	if wants_local is None:
		wants_local = False

	def _runner_xdg(s):
		return _yes_no_modal(
			s,
			[
				"Espejo en AppData (Windows)",
				"Opcional: copiar perfiles tras cada guardado a:",
				mirror_path,
				"",
				"Solo respaldo; el HUD no lee esa ruta.",
				"Solo escribe si usted elige Si.",
			],
			default_no_on_escape=True,
		)

	wants_xdg = run_modal_child_window(
		title="Espejo de perfiles",
		size=(560, 360),
		window_mode=wm,
		runner=_runner_xdg,
		screen=screen,
	)
	if wants_xdg is None:
		wants_xdg = False

	profile_data["backups_enabled"] = bool(wants_local)
	profile_data["xdg_mirror_enabled"] = bool(wants_xdg)
	profile_data["backup_prompt_completed"] = True
	save_profiles_data(profile_data)

	if not wants_local:
		_run_message_modal(
			screen,
			"Backups locales desactivados",
			[
				"Puede activar las copias en user/backups/ desde Configuracion:",
				"opcion «Backups locales» (Si/No).",
			],
			window_mode=wm,
		)
	if not wants_xdg:
		_run_message_modal(
			screen,
			"Espejo desactivado",
			[
				"Puede activar la copia bajo la carpeta de datos del sistema",
				"desde Configuracion: opcion «Espejo datos sistema» (Si/No).",
			],
			window_mode=wm,
		)
	return profile_data
