# joystick_mapper.py

# --- Encargado de mapear el joystick si se escogio en el selector

import os
import pygame
import json
import select
from evdev import InputDevice, ecodes
from config import (
	get_button_labels,
	JOYSTICK_BINDINGS_PATH,
	DEVICE_NAME_FILTER,
	get_bindings_format_key,
	get_hud_fallback_text,
)
from profiles.bindings_storage import (
	load_bindings_tree,
	save_bindings_tree,
	set_slice,
	path_joystick_bindings,
	normalize_flat_bindings_for_format_8,
)
from utils import (
	draw_centered_text, show_error_and_exit, get_first_joystick_device,
	list_gamepad_devices_by_capabilities, find_gamepad_by_name,
	build_responsive_font, fit_text_to_width, run_modal_child_window
)

def _process_device_choice_event(event, selected, count):
	"""Procesa evento del selector de dispositivo. Retorna (new_selected, result). result=None sigue, device o None para salir."""
	if event.type == pygame.QUIT:
		return selected, "quit"
	if event.type != pygame.KEYDOWN:
		return selected, None
	key = event.key
	if key in (pygame.K_UP, pygame.K_LEFT):
		return (selected - 1) % count, None
	if key in (pygame.K_DOWN, pygame.K_RIGHT):
		return (selected + 1) % count, None
	if key == pygame.K_ESCAPE:
		return selected, "quit"
	if key == pygame.K_RETURN:
		return selected, "select"
	return selected, None


def _choose_device_from_candidates(screen, candidates):
	selected = 0
	clock = pygame.time.Clock()
	count = len(candidates)

	while True:
		lines = ["Selecciona dispositivo"] + [device.name for device in candidates[:6]] + ["Enter confirmar | Esc volver"]
		font, line_gap = build_responsive_font(
			screen,
			lines,
			base_size=28,
			min_size=14,
			max_size=34,
			base_resolution=(620, 360),
		)
		screen.fill((0, 0, 0))
		title_y = max(28, line_gap)
		draw_centered_text(screen, font, "Selecciona dispositivo", y=title_y)
		for index, device in enumerate(candidates[:6]):
			prefix = ">" if index == selected else " "
			device_text = fit_text_to_width(font, device.name, int(screen.get_width() * 0.88))
			draw_centered_text(screen, font, f"{prefix} {device_text}", y=title_y + line_gap + index * line_gap)
		draw_centered_text(screen, font, "Enter confirmar | Esc volver", y=screen.get_height() - max(20, line_gap))
		pygame.display.flip()

		for event in pygame.event.get():
			selected, result = _process_device_choice_event(event, selected, count)
			if result == "quit":
				return None
			if result == "select":
				return candidates[selected]
		clock.tick(60)

def _prompt_manual_device_name(screen, window_mode="floating_hint"):
	def _runner(secondary):
		typed = ""
		clock = pygame.time.Clock()

		while True:
			lines = ["Escribe nombre del dispositivo", typed or "...", "Enter buscar | Borrar | Esc"]
			font, line_gap = build_responsive_font(
				secondary,
				lines,
				base_size=30,
				min_size=14,
				max_size=34,
				base_resolution=(460, 260),
			)
			secondary.fill((0, 0, 0))
			title_y = max(28, line_gap)
			draw_centered_text(secondary, font, "Escribe nombre del dispositivo", y=title_y)
			draw_centered_text(secondary, font, typed or "...", y=title_y + line_gap)
			draw_centered_text(secondary, font, "Enter buscar | Borrar | Esc", y=title_y + line_gap * 2)
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
						device = find_gamepad_by_name(typed)
						if device:
							selected_path = device.path
							device.close()
							return selected_path
						secondary.fill((20, 0, 0))
						draw_centered_text(secondary, font, "No se encontro dispositivo valido", y=95)
						pygame.display.flip()
						pygame.time.wait(900)
						typed = ""
					elif event.unicode and event.unicode.isprintable():
						typed += event.unicode
			clock.tick(60)

	return run_modal_child_window(
		title="Ingreso manual de dispositivo",
		size=(460, 260),
		window_mode=window_mode,
		runner=_runner,
		screen=screen,
	)

def _wait_for_single_button(dev, screen, label, controller_style, button_count):
	"""Espera a que el usuario presione un boton. Retorna event.code o None si cancela."""
	display_name = get_hud_fallback_text(label, controller_style, button_count)
	prompt = f"Presiona boton {display_name} ({label})"
	while True:
		lines = [prompt, "Esc para cancelar"]
		font, line_gap = build_responsive_font(
			screen,
			lines,
			base_size=32,
			min_size=14,
			max_size=36,
			base_resolution=(620, 360),
		)
		screen.fill((0, 0, 0))
		title_y = max(32, line_gap)
		draw_centered_text(screen, font, prompt, y=title_y)
		draw_centered_text(screen, font, "Esc para cancelar", y=title_y + line_gap)
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				return None

		r, _, _ = select.select([dev], [], [], 0.01)
		if dev in r:
			for event in dev.read():
				if event.type == ecodes.EV_KEY and event.value == 1:
					return event.code
	return None


def _save_joystick_bindings_legacy(formato, bindings):
	try:
		with open(JOYSTICK_BINDINGS_PATH, "r", encoding="utf-8") as f:
			all_bindings = json.load(f)
	except Exception:
		all_bindings = {}
	if not isinstance(all_bindings, dict):
		all_bindings = {}
	all_bindings[formato] = bindings
	dir_path = os.path.dirname(JOYSTICK_BINDINGS_PATH)
	if dir_path:
		os.makedirs(dir_path, exist_ok=True)
	with open(JOYSTICK_BINDINGS_PATH, "w", encoding="utf-8") as f:
		json.dump(all_bindings, f, indent=4)


def _formato_to_button_count(formato):
	if formato == "formato_8":
		return 8
	if formato == "formato_6":
		return 6
	return 4


def _save_joystick_bindings_profile(profile_id, formato, bindings):
	bindings = normalize_flat_bindings_for_format_8(
		dict(bindings), _formato_to_button_count(formato)
	)
	path = path_joystick_bindings(profile_id)
	tree = load_bindings_tree(path)
	save_bindings_tree(path, set_slice(tree, formato, bindings))
	_save_joystick_bindings_legacy(formato, bindings)


def map_joystick_buttons(
	screen,
	button_count,
	show_error=True,
	device_path=None,
	controller_style="default",
	profile_id=None,
	format_key=None,
):
	labels = get_button_labels(button_count)

	dev = None
	if device_path:
		try:
			dev = InputDevice(device_path)
		except Exception:
			dev = None

	if dev is None:
		dev = get_first_joystick_device(DEVICE_NAME_FILTER)
	if dev:
		dev.grab()

	if not dev:
		if show_error:
			show_error_and_exit(screen, "Error\nNo se encontro ningun joystick.")
		return None

	print(f"[INFO] Usando joystick: {dev.name}")
	bindings = {}
	try:
		for label in labels:
			code = _wait_for_single_button(dev, screen, label, controller_style, button_count)
			if code is None:
				return None
			bindings[label] = code
		for extra in ("SELECT", "START"):
			code = _wait_for_single_button(dev, screen, extra, controller_style, button_count)
			if code is None:
				return None
			bindings[extra] = code
	finally:
		dev.ungrab()
		dev.close()

	formato = format_key or get_bindings_format_key(button_count)
	if profile_id:
		_save_joystick_bindings_profile(profile_id, formato, bindings)
	else:
		_save_joystick_bindings_legacy(formato, bindings)
	return bindings

def _handle_diagnostic_option(option_index, screen, selected_path, button_count, controller_style):
	"""Despacha la opcion seleccionada del menu de diagnostico. Retorna resultado o None si no aplica."""
	if option_index == 0:
		return {"status": "selected", "device_path": selected_path}
	if option_index == 1:
		mapped = map_joystick_buttons(
			screen,
			button_count,
			show_error=False,
			device_path=selected_path,
			controller_style=controller_style,
		)
		if mapped:
			return {"status": "mapped", "device_path": selected_path, "bindings": mapped}
	return {"status": "back_to_input"}


def _process_diagnostic_menu_event(event, selected, options, screen, selected_path, button_count, controller_style):
	"""Procesa evento del menu diagnostico. Retorna (new_selected, result). result=None sigue, dict para retornar."""
	if event.type == pygame.QUIT:
		return selected, {"status": "back_to_input"}
	if event.type != pygame.KEYDOWN:
		return selected, None
	key = event.key
	if key in (pygame.K_UP, pygame.K_LEFT):
		return (selected - 1) % len(options), None
	if key in (pygame.K_DOWN, pygame.K_RIGHT):
		return (selected + 1) % len(options), None
	if key == pygame.K_ESCAPE:
		return selected, {"status": "back_to_input"}
	if key == pygame.K_RETURN:
		return selected, _handle_diagnostic_option(
			selected, screen, selected_path, button_count, controller_style
		)
	return selected, None


def _render_diagnostic_menu(screen, options, selected, selected_path):
	"""Dibuja el menu de diagnostico."""
	lines = ["Diagnostico de joystick", selected_path] + options
	font, line_gap = build_responsive_font(
		screen, lines, base_size=28, min_size=14, max_size=34, base_resolution=(620, 360),
	)
	screen.fill((0, 0, 0))
	title_y = max(28, line_gap)
	draw_centered_text(screen, font, "Diagnostico de joystick", y=title_y)
	device_line = fit_text_to_width(font, f"Dispositivo: {selected_path}", int(screen.get_width() * 0.90))
	draw_centered_text(screen, font, device_line, y=title_y + line_gap)
	for index, option in enumerate(options):
		prefix = ">" if index == selected else " "
		draw_centered_text(screen, font, f"{prefix} {option}", y=title_y + line_gap * (2 + index))
	pygame.display.flip()


def run_joystick_diagnostic(screen, button_count, window_mode="floating_hint", controller_style="default"):
	candidates = list_gamepad_devices_by_capabilities()
	if len(candidates) == 0:
		manual_path = _prompt_manual_device_name(screen, window_mode=window_mode)
		if manual_path:
			return {"status": "selected", "device_path": manual_path}
		return {"status": "back_to_input"}

	selected_device = _choose_device_from_candidates(screen, candidates)
	for device in candidates:
		if selected_device is None or device.path != selected_device.path:
			device.close()

	if selected_device is None:
		return {"status": "back_to_input"}

	selected_path = selected_device.path
	selected_device.close()

	options = ["Usar dispositivo", "Mapear botones", "Volver al menu de entrada"]
	selected = 0
	clock = pygame.time.Clock()
	while True:
		_render_diagnostic_menu(screen, options, selected, selected_path)
		for event in pygame.event.get():
			selected, result = _process_diagnostic_menu_event(
				event, selected, options, screen, selected_path, button_count, controller_style
			)
			if result is not None:
				return result
		clock.tick(60)

