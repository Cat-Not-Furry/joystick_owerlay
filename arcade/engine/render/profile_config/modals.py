import os
import subprocess
import sys
from pathlib import Path

import pygame

from config import (
	BUTTON_COLOR_PRESETS,
	JOYSTICK_COLOR_PRESETS,
	PROFILES_DIR,
	UPDATE_LOG_PATH,
	get_default_icon_path,
)
from utils import (
	MenuArrowRepeater,
	build_responsive_font,
	draw_centered_text,
	fit_text_to_width,
	list_keyboard_devices_by_capabilities,
	run_modal_child_window,
)


def _repo_root():
	"""Raíz del repositorio (render -> engine -> arcade -> root)."""
	return Path(__file__).resolve().parent.parent.parent.parent.parent


def _color_name_from_values(values):
	for name, preset_values in JOYSTICK_COLOR_PRESETS.items():
		if list(preset_values) == list(values):
			return name
	return "personalizado"


def _button_color_preset_name(inactive, active):
	for name, preset in BUTTON_COLOR_PRESETS.items():
		if (list(preset["inactive"]) == list(inactive) and
				list(preset["active"]) == list(active)):
			return name
	return "personalizado"


def _available_icon_paths(labels, profile_id):
	options = []
	icons_dir = os.path.join(PROFILES_DIR, str(profile_id), "icons")
	if os.path.isdir(icons_dir):
		for filename in sorted(os.listdir(icons_dir)):
			if filename.lower().endswith(".png"):
				options.append(os.path.join("icons", filename))
	for label in labels:
		default_path = get_default_icon_path(label)
		if default_path not in options:
			options.append(default_path)
	if "ninguno" not in options:
		options.insert(0, "ninguno")
	if "Seleccionar..." not in options:
		options.insert(1, "Seleccionar...")
	return options


def _keyboard_device_options():
	options = [("ninguno (solo con foco)", None)]
	devices = list_keyboard_devices_by_capabilities()
	for device in devices:
		options.append((f"{device.name} | {device.path}", device.path))
	for device in devices:
		device.close()
	return options


def _run_text_input(screen, title, initial_value="", window_mode="normal"):
	def _runner(secondary):
		typed = str(initial_value)
		clock = pygame.time.Clock()

		while True:
			lines = [title, typed or "...", "Enter confirmar | Backspace | Esc cancelar"]
			font, line_gap = build_responsive_font(
				secondary,
				lines,
				base_size=26,
				min_size=14,
				max_size=34,
				base_resolution=(560, 300),
			)
			secondary.fill((0, 0, 0))
			title_y = max(28, line_gap)
			draw_centered_text(secondary, font, title, y=title_y)
			draw_centered_text(secondary, font, typed or "...", y=title_y + line_gap)
			draw_centered_text(secondary, font, "Enter confirmar | Backspace | Esc cancelar", y=secondary.get_height() - max(22, line_gap))
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						return None
					if event.key == pygame.K_BACKSPACE:
						typed = typed[:-1]
					elif event.key == pygame.K_RETURN:
						return typed
					elif event.unicode and event.unicode.isprintable():
						typed += event.unicode
			clock.tick(60)

	return run_modal_child_window(
		title=title,
		size=(560, 300),
		window_mode=window_mode,
		runner=_runner,
		screen=screen,
	)


def _run_choice_menu(
	screen,
	title,
	options,
	initial_index=0,
	window_mode="normal",
	*,
	refresh_options=None,
	on_tab=None,
	footer_extra=None,
):
	def _runner(secondary):
		selected = max(0, min(initial_index, len(options) - 1))
		clock = pygame.time.Clock()
		repeater = MenuArrowRepeater()

		while True:
			if refresh_options is not None:
				opts = refresh_options()
				if not opts:
					opts = list(options)
			else:
				opts = list(options)
			selected = max(0, min(selected, len(opts) - 1))
			footer = footer_extra if footer_extra is not None else "Flechas + Enter | Esc"
			lines_for_fit = [title] + [str(option) for option in opts[:8]] + [footer]
			font, line_gap = build_responsive_font(
				secondary,
				lines_for_fit,
				base_size=26,
				min_size=14,
				max_size=34,
				base_resolution=(540, 320),
				max_height_ratio=0.84,
			)
			secondary.fill((0, 0, 0))
			draw_centered_text(secondary, font, title, y=max(28, line_gap))
			start_y = max(28, line_gap) + line_gap
			for index, option in enumerate(opts):
				prefix = ">" if index == selected else " "
				draw_centered_text(secondary, font, f"{prefix} {option}", y=start_y + index * line_gap)
			draw_centered_text(secondary, font, footer, y=secondary.get_height() - max(20, line_gap))
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN:
					if event.key not in (
						pygame.K_UP,
						pygame.K_DOWN,
						pygame.K_LEFT,
						pygame.K_RIGHT,
					):
						repeater.reset()
					dnav = repeater.consume_keydown(event)
					if dnav is not None:
						selected = (selected + dnav) % len(opts)
					elif event.key == pygame.K_TAB and on_tab is not None and not getattr(event, "repeat", False):
						on_tab(selected)
					elif event.key == pygame.K_RETURN:
						return selected
					elif event.key == pygame.K_ESCAPE:
						return None
			d2 = repeater.tick_held()
			if d2 is not None:
				selected = (selected + d2) % len(opts)
			clock.tick(60)

	return run_modal_child_window(
		title=title,
		size=(540, 320),
		window_mode=window_mode,
		runner=_runner,
		screen=screen,
	)


def _run_message_modal(screen, title, message_lines, window_mode="normal"):
	lines = [title] + list(message_lines) + ["Enter/Esc para continuar"]

	def _runner(secondary):
		clock = pygame.time.Clock()
		while True:
			font, line_gap = build_responsive_font(
				secondary,
				lines,
				base_size=24,
				min_size=14,
				max_size=34,
				base_resolution=(560, 280),
			)
			secondary.fill((0, 0, 0))
			start_y = max(24, (secondary.get_height() - line_gap * len(lines)) // 2)
			for index, line in enumerate(lines):
				trimmed = fit_text_to_width(font, line, int(secondary.get_width() * 0.92))
				draw_centered_text(secondary, font, trimmed, y=start_y + index * line_gap)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
					return None
			clock.tick(60)

	return run_modal_child_window(
		title=title,
		size=(560, 280),
		window_mode=window_mode,
		runner=_runner,
		screen=screen,
	)


def _run_update_modal(screen, zip_path, window_mode="normal"):
	log_path = UPDATE_LOG_PATH
	cli_path = str(_repo_root() / "cli.py")

	def _terminate_process(process):
		try:
			process.terminate()
			process.wait(timeout=2.0)
		except subprocess.TimeoutExpired:
			try:
				process.kill()
				process.wait()
			except Exception:
				pass
		except Exception:
			pass

	def _runner(secondary):
		try:
			log_file = open(log_path, "w")
		except Exception:
			log_file = None
		process = None
		try:
			stdout_target = log_file if log_file is not None else subprocess.DEVNULL
			process = subprocess.Popen(
				[sys.executable, cli_path, "--update", "--zip", zip_path],
				stdout=stdout_target,
				stderr=subprocess.STDOUT,
				text=True,
				cwd=str(_repo_root()),
			)
		except Exception as error:
			if log_file is not None:
				log_file.close()
			_run_message_modal(
				screen,
				"Actualizar overlay",
				[f"No se pudo iniciar actualizacion: {error}"],
				window_mode=window_mode,
			)
			return "error"

		clock = pygame.time.Clock()
		while True:
			running = process.poll() is None
			if running:
				dots = "." * ((pygame.time.get_ticks() // 500) % 4)
				lines = [
					f"Actualizando{dots}",
					"No cierres esta ventana",
					f"Log: {log_path}",
					"Esc para volver",
				]
			else:
				ok = process.returncode == 0
				if ok:
					lines = [
						"Actualizacion completada",
						"Enter para abrir HUD",
						"Esc para volver",
					]
				else:
					lines = [
						"Error al actualizar",
						f"Revisa log: {log_path}",
						"Esc para volver",
					]
			font, line_gap = build_responsive_font(
				secondary,
				lines,
				base_size=24,
				min_size=14,
				max_size=34,
				base_resolution=(620, 320),
			)
			secondary.fill((0, 0, 0))
			start_y = max(24, (secondary.get_height() - line_gap * len(lines)) // 2)
			for index, line in enumerate(lines):
				trimmed = fit_text_to_width(font, line, int(secondary.get_width() * 0.92))
				draw_centered_text(secondary, font, trimmed, y=start_y + index * line_gap)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					if running:
						_terminate_process(process)
					if log_file is not None:
						log_file.close()
					return "error"
				if event.type == pygame.KEYDOWN:
					if running and event.key == pygame.K_ESCAPE:
						_terminate_process(process)
						if log_file is not None:
							log_file.close()
						return "cancel"
					if not running and event.key == pygame.K_RETURN and process.returncode == 0:
						if log_file is not None:
							log_file.close()
						return "open_hud"
					if not running and event.key == pygame.K_ESCAPE:
						if log_file is not None:
							log_file.close()
						return "done"
			clock.tick(60)

	result = run_modal_child_window(
		title="Actualizar overlay",
		size=(620, 320),
		window_mode=window_mode,
		runner=_runner,
		screen=screen,
	)
	return result
