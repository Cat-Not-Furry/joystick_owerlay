# main.py - Archivo principal (Windows)

import engine_sys_path  # noqa: F401, E402

import os
import pygame
import threading
import sys
import subprocess
import tempfile
import json
import time
import argparse
from datetime import datetime


def _debug_menu(msg):
	if os.environ.get("HUD_DEBUG_MENU") == "1":
		ts = (
			time.strftime("%H:%M:%S", time.localtime())
			+ f".{int((time.time() % 1) * 1000):03d}"
		)
		print(f"[HUD_DEBUG] {ts} | {msg}")


_debug_videoresize_count = 0
_debug_set_mode_count = 0
_debug_stats_last_sec = 0.0


def _debug_count_videoresize():
	global _debug_videoresize_count
	_debug_videoresize_count += 1


def _debug_count_set_mode():
	global _debug_set_mode_count
	_debug_set_mode_count += 1


def _debug_report_videoresize_stats():
	if os.environ.get("HUD_DEBUG_MENU") != "1":
		return
	global _debug_videoresize_count, _debug_set_mode_count, _debug_stats_last_sec
	now = time.time()
	if now - _debug_stats_last_sec >= 1.0 and (_debug_videoresize_count > 0 or _debug_set_mode_count > 0):
		elapsed = now - _debug_stats_last_sec
		vr_per_sec = _debug_videoresize_count / elapsed
		sm_per_sec = _debug_set_mode_count / elapsed
		print(f"[HUD_DEBUG] stats | VIDEORESIZE/s: {vr_per_sec:.1f} | set_mode/s: {sm_per_sec:.1f}")
		_debug_videoresize_count = 0
		_debug_set_mode_count = 0
		_debug_stats_last_sec = now
	elif _debug_stats_last_sec == 0.0:
		_debug_stats_last_sec = now


from config import (
	SCREEN_WIDTH,
	SCREEN_HEIGHT,
	FPS,
	TOURNAMENT_FPS,
	get_button_labels,
	get_background_color,
	MIN_WINDOW_WIDTH,
	MIN_WINDOW_HEIGHT,
	VIDEORESIZE_COOLDOWN_MS,
	VIDEORESIZE_TOLERANCE_PX,
	EASTEREGG_ENABLE_MULTI_INSTANCE,
	EASTEREGG_MULTI_INSTANCE_KEY,
	EASTEREGG_MAX_INSTANCES,
	APP_ID,
	JSON_DIR,
	USER_DIR,
	RESET_LOG_PATH,
	ASSETS_VERSION_PATH,
	HUD_VERSION_PATH,
	get_assets_version,
	get_data_version,
	get_runtime_version,
	ensure_contract_dirs,
	write_data_version,
)
from render import choose_button_format, choose_input_mode, open_profile_config_menu
from render import draw_hud, load_icons, set_stick_color, set_stick_colors, set_button_colors
from render import (
	set_controller_style,
	set_render_mode,
	set_input_layout,
	set_hitbox_alt_layout,
)
from maps import (
	map_keys,
	map_joystick_buttons,
	run_joystick_diagnostic,
	start_input_listener,
)
from profiles import (
	load_profiles_data,
	save_profiles_data,
	get_active_profile,
	sync_active_profile_to_legacy_files,
)
from utils import (
	draw_centered_text,
	build_responsive_font,
	fit_text_to_width,
	list_keyboard_devices_by_capabilities,
	set_ui_font_family,
	track_set_mode,
	get_last_set_mode_time_ms,
	get_project_version,
	get_installed_version,
)
from maps.input_reader import poll_pygame_keyboard_if_needed
from core.assets_resolver import resolve_icons_map, clear_cache as clear_assets_cache
from core.data_migrations import CURRENT_DATA_VERSION, migrate_if_needed
from training import (
	create_training_state,
	start_recording,
	stop_recording,
	clear_sequence,
	start_playback,
	snapshot_if_recording,
	update_playback,
	has_sequence,
	sequence_to_dict,
)
from application_context import ApplicationContext
from core.state_manager import (
	StateManager,
	STOP,
	BootState,
	MainMenuState,
	ModalState,
	ProfileConfigState,
	HudSetupState,
	HudRunState,
)

MENU_WIDTH = 320
MENU_HEIGHT = 180
SELECTOR_WINDOW_SIZE = (500, 300)
MAPPER_WINDOW_SIZE = (620, 380)
CONFIRM_WINDOW_SIZE = (420, 230)

# Ventana única de sesión: mismo surface para MainMenuState, ProfileConfigState, HudSetupState y HudRunState.
# Evita pygame.display.set_mode al cambiar de estado (pérdida de foco al capturar con OBS, etc.).
APP_WINDOW_WIDTH = max(SCREEN_WIDTH, MENU_WIDTH, 460)
APP_WINDOW_HEIGHT = max(SCREEN_HEIGHT, MENU_HEIGHT, 320)

_current_window_mode = "normal"


def _now_str():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_temp_reset_log_path():
	return RESET_LOG_PATH


def _safe_write_log(base_path, message):
	try:
		os.makedirs(base_path, exist_ok=True)
		log_file = os.path.join(base_path, "reset.log")
		with open(log_file, "a", encoding="utf-8") as handle:
			handle.write(message + "\n")
	except Exception:
		pass


def _safe_write_temp_log(message):
	try:
		os.makedirs(os.path.dirname(get_temp_reset_log_path()), exist_ok=True)
		with open(get_temp_reset_log_path(), "a", encoding="utf-8") as handle:
			handle.write(message + "\n")
	except Exception:
		pass


def _backup_and_clear_data():
	base = USER_DIR
	if not os.path.exists(base):
		msg = f"[{_now_str()}][reset] Solicitud de reset sin datos existentes."
		print(msg)
		_safe_write_temp_log(msg)
		return

	ts = int(time.time())
	backup = f"{base}_backup_{ts}"
	counter = 1
	while os.path.exists(backup):
		backup = f"{base}_backup_{ts}_{counter}"
		counter += 1

	try:
		os.rename(base, backup)
		msg = f"[{_now_str()}][reset] Backup creado en: {backup}"
		print(msg)
		_safe_write_log(backup, msg)
		_safe_write_log(USER_DIR, msg)
	except Exception as err:
		error_message = f"[{_now_str()}][reset][ERROR] Fallo en reset: {type(err).__name__}: {repr(err)}"
		print(error_message)
		if os.path.exists(base):
			_safe_write_log(base, error_message)
		if os.path.exists(backup):
			_safe_write_log(backup, error_message)
		_safe_write_temp_log(error_message)


def _confirm_reset_interactive():
	if sys.stdin and sys.stdin.isatty():
		print(f"Se borrará el directorio de datos de usuario: {USER_DIR}")
		print("Confirma reset de datos? [y/N]: ", end="")
		return input().strip().lower() in ("y", "yes", "s", "si")
	try:
		import tkinter as tk
		from tkinter import messagebox

		root = tk.Tk()
		root.withdraw()
		result = messagebox.askyesno(
			"HUD Owerlay",
			f"Se borrará el directorio de datos de usuario:\n{USER_DIR}\n\n¿Deseas continuar?",
		)
		root.destroy()
		return result
	except Exception:
		print("No se pudo mostrar confirmacion. Ejecuta desde terminal.")
		return False


def _build_worker_command():
	if getattr(sys, "frozen", False):
		return [sys.executable, "--do-reset-data", "--no-ui"]
	return [sys.executable, sys.argv[0], "--do-reset-data", "--no-ui"]


def _handle_reset_interactive():
	if not _confirm_reset_interactive():
		print("Cancelado.")
		return True
	subprocess.Popen(_build_worker_command())
	print("Reset en progreso... la aplicacion se cerrara.")
	sys.exit(0)


def _parse_early_args(argv):
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("--show-reset-log", action="store_true")
	parser.add_argument("--reset-data", action="store_true")
	parser.add_argument("--do-reset-data", action="store_true")
	parser.add_argument("--no-ui", action="store_true")
	parser.add_argument("--version", action="store_true")
	parser.add_argument("--doctor", action="store_true")
	return parser.parse_known_args(argv[1:])[0]


def _run_doctor():
	doctor_path = os.path.join(os.path.dirname(__file__), "doctor.py")
	return subprocess.call([sys.executable, doctor_path]) == 0


def _early_cli(argv):
	args = _parse_early_args(argv)
	if args.show_reset_log:
		print(get_temp_reset_log_path())
		return True
	if args.reset_data:
		return _handle_reset_interactive()
	if args.do_reset_data:
		_backup_and_clear_data()
		write_data_version(CURRENT_DATA_VERSION)
		return True
	if args.version:
		print(f"project={get_project_version()} installed={get_installed_version()}")
		return True
	if args.doctor:
		_run_doctor()
		return True
	return False


def _preflight_startup():
	ensure_contract_dirs()
	assets_version = get_assets_version()
	if not assets_version:
		print(f"[ERR] assets inválidos: falta {ASSETS_VERSION_PATH}")
		return False
	runtime_version = get_runtime_version()
	if not runtime_version:
		print(f"[ERR] runtime inválido: falta {HUD_VERSION_PATH}")
		return False
	data_version_raw = get_data_version(default_version="0")
	try:
		data_version = int(data_version_raw)
	except Exception:
		data_version = 0
	if data_version < CURRENT_DATA_VERSION:
		result = migrate_if_needed()
		print(f"[INFO] Migración de datos: {result}")
		clear_assets_cache()
	elif data_version > CURRENT_DATA_VERSION:
		print(f"[ERR] data_version ({data_version}) mayor que soportado ({CURRENT_DATA_VERSION}).")
		return False
	return True


def _set_window_size(width, height, title):
	_debug_menu(f"_set_window_size({width}x{height})")
	screen = pygame.display.set_mode((width, height))
	pygame.display.set_caption(title)
	track_set_mode()
	return screen


def _count_running_overlay_instances():
	"""Windows: usa tasklist para contar instancias de main.py."""
	try:
		result = subprocess.run(
			["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV", "/V"],
			capture_output=True,
			text=True,
			timeout=5,
		)
		if result.returncode != 0:
			return 0
		lines = result.stdout.strip().split("\n")
		count = 0
		project_dir = os.path.dirname(os.path.abspath(__file__)).lower()
		for line in lines[1:]:
			if "main.py" in line.lower() and "hud" in line.lower():
				count += 1
			elif "main.py" in line.lower() and project_dir in line.lower():
				count += 1
		return max(0, count - 1)
	except Exception:
		return 0


def _launch_training_window(sequence_data):
	fd, path = tempfile.mkstemp(suffix=".json", prefix="hud_training_")
	try:
		with os.fdopen(fd, "w") as f:
			json.dump(sequence_data, f, indent=2)
		standalone_path = os.path.join(
			os.path.dirname(__file__), "training", "standalone.py"
		)
		subprocess.Popen(
			[sys.executable, standalone_path, path],
			cwd=os.path.dirname(__file__),
			start_new_session=True,
		)
	except Exception as err:
		print(f"[WARN] No se pudo abrir ventana de entrenamiento: {err}")
		try:
			os.unlink(path)
		except Exception:
			pass


def _launch_easteregg_instance():
	if not EASTEREGG_ENABLE_MULTI_INSTANCE:
		return False
	if _count_running_overlay_instances() + 1 >= EASTEREGG_MAX_INSTANCES:
		print(f"[WARN] Limite de instancias alcanzado ({EASTEREGG_MAX_INSTANCES}).")
		return False

	main_path = os.path.join(os.path.dirname(__file__), "main.py")
	try:
		subprocess.Popen(
			[sys.executable, main_path],
			cwd=os.path.dirname(__file__),
			start_new_session=True,
		)
		print("[INFO] Easteregg activado: nueva instancia iniciada.")
		return True
	except Exception as error:
		print(f"[WARN] No se pudo abrir una nueva instancia: {error}")
		return False


def _run_secondary_selector(title, size, runner):
	"""Ventana única: ejecuta el selector en la superficie actual sin cambiar set_mode."""
	screen = pygame.display.get_surface()
	if screen is None:
		return None, None
	result = runner(screen)
	return result, screen


def select_profile_secondary(profile_data, title="Selecciona perfil"):
	def _runner(screen):
		clock = pygame.time.Clock()
		profiles = profile_data["profiles"]
		selected = 0
		for index, profile in enumerate(profiles):
			if profile["id"] == profile_data.get("active_profile"):
				selected = index
				break

		while True:
			profile_names = [profile["name"] for profile in profiles]
			lines = [title] + profile_names[:6] + ["Flechas + Enter | Esc"]
			font, line_gap = build_responsive_font(
				screen,
				lines,
				base_size=28,
				min_size=14,
				max_size=34,
				base_resolution=SELECTOR_WINDOW_SIZE,
				max_height_ratio=0.82,
			)
			screen.fill((0, 0, 0))
			title_y = max(28, line_gap)
			draw_centered_text(screen, font, title, y=title_y)
			start_index = max(0, selected - 2)
			end_index = min(len(profiles), start_index + 5)
			visible = profiles[start_index:end_index]
			start_y = title_y + line_gap
			for visible_index, profile in enumerate(visible):
				option_index = start_index + visible_index
				prefix = ">" if option_index == selected else " "
				draw_centered_text(
					screen,
					font,
					f"{prefix} {profile['name']}",
					y=start_y + visible_index * line_gap,
				)
			draw_centered_text(
				screen,
				font,
				"Flechas + Enter | Esc",
				y=screen.get_height() - max(20, line_gap),
			)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN:
					if event.key in (pygame.K_UP, pygame.K_LEFT):
						selected = (selected - 1) % len(profiles)
					elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
						selected = (selected + 1) % len(profiles)
					elif event.key == pygame.K_ESCAPE:
						return None
					elif event.key == pygame.K_RETURN:
						return profiles[selected]["id"]
			clock.tick(FPS)

	selected_id, screen = _run_secondary_selector(title, SELECTOR_WINDOW_SIZE, _runner)
	return selected_id, screen


def _confirm_exit_secondary():
	def _runner(screen):
		clock = pygame.time.Clock()
		selected = 1
		options = ["No", "Si"]
		while True:
			render_lines = (
				["Confirmar salida", "Deseas cerrar el HUD?"]
				+ options
				+ ["Flechas + Enter | Esc"]
			)
			font, line_gap = build_responsive_font(
				screen,
				render_lines,
				base_size=30,
				min_size=14,
				max_size=34,
				base_resolution=(420, 220),
			)
			screen.fill((0, 0, 0))
			title_y = max(28, line_gap)
			draw_centered_text(screen, font, "Confirmar salida", y=title_y)
			draw_centered_text(
				screen, font, "Deseas cerrar el HUD?", y=title_y + line_gap
			)
			for index, option in enumerate(options):
				prefix = ">" if index == selected else " "
				draw_centered_text(
					screen,
					font,
					f"{prefix} {option}",
					y=title_y + line_gap * (3 + index),
				)
			draw_centered_text(
				screen,
				font,
				"Flechas + Enter | Esc",
				y=screen.get_height() - max(20, line_gap),
			)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return False
				if event.type == pygame.KEYDOWN:
					if event.key in (
						pygame.K_UP,
						pygame.K_LEFT,
						pygame.K_DOWN,
						pygame.K_RIGHT,
					):
						selected = (selected + 1) % len(options)
					elif event.key == pygame.K_ESCAPE:
						return False
					elif event.key == pygame.K_RETURN:
						return options[selected] == "Si"
			clock.tick(FPS)

	confirmed, restored = _run_secondary_selector(
		"Confirmar salida", CONFIRM_WINDOW_SIZE, _runner
	)
	return confirmed, restored


def _confirm_keyboard_remap_secondary():
	def _runner(screen):
		clock = pygame.time.Clock()
		selected = 0
		options = ["No", "Si", "Cancelar y volver"]
		while True:
			render_lines = (
				["Modo teclado", "Quieres remapear teclas?"]
				+ options
				+ ["Flechas + Enter | Esc"]
			)
			font, line_gap = build_responsive_font(
				screen,
				render_lines,
				base_size=30,
				min_size=14,
				max_size=34,
				base_resolution=(420, 220),
			)
			screen.fill((0, 0, 0))
			title_y = max(28, line_gap)
			draw_centered_text(screen, font, "Modo teclado", y=title_y)
			draw_centered_text(
				screen, font, "Quieres remapear teclas?", y=title_y + line_gap
			)
			for index, option in enumerate(options):
				prefix = ">" if index == selected else " "
				draw_centered_text(
					screen,
					font,
					f"{prefix} {option}",
					y=title_y + line_gap * (3 + index),
				)
			draw_centered_text(
				screen,
				font,
				"Flechas + Enter | Esc",
				y=screen.get_height() - max(20, line_gap),
			)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return False
				if event.type == pygame.KEYDOWN:
					if event.key in (
						pygame.K_UP,
						pygame.K_LEFT,
						pygame.K_DOWN,
						pygame.K_RIGHT,
					):
						if event.key in (pygame.K_UP, pygame.K_LEFT):
							selected = (selected - 1) % len(options)
						else:
							selected = (selected + 1) % len(options)
					elif event.key == pygame.K_ESCAPE:
						return "cancelar"
					elif event.key == pygame.K_RETURN:
						if options[selected] == "Si":
							return "si"
						if options[selected] == "No":
							return "no"
						return "cancelar"
			clock.tick(FPS)

	confirmed, restored = _run_secondary_selector(
		"Remapeo teclado", CONFIRM_WINDOW_SIZE, _runner
	)
	return confirmed, restored


def _choose_keyboard_device_secondary(current_path):
	def _runner(screen):
		clock = pygame.time.Clock()
		devices = list_keyboard_devices_by_capabilities()
		options = [("Ninguno (solo con foco)", None)]
		for device in devices:
			options.append((f"{device.name} | {device.path}", device.path))
		for device in devices:
			device.close()

		selected = 0
		for index, option in enumerate(options):
			if option[1] == current_path:
				selected = index
				break

		while True:
			lines_for_fit = (
				["Teclado global (sin foco)"]
				+ [label for label, _ in options[:6]]
				+ ["Flechas + Enter | Esc"]
			)
			font, line_gap = build_responsive_font(
				screen,
				lines_for_fit,
				base_size=28,
				min_size=14,
				max_size=34,
				base_resolution=SELECTOR_WINDOW_SIZE,
				max_height_ratio=0.82,
			)
			screen.fill((0, 0, 0))
			title_y = max(28, line_gap)
			draw_centered_text(screen, font, "Teclado global (sin foco)", y=title_y)

			start_index = max(0, selected - 2)
			end_index = min(len(options), start_index + 5)
			visible = options[start_index:end_index]
			start_y = title_y + line_gap
			for visible_index, (label, _) in enumerate(visible):
				option_index = start_index + visible_index
				prefix = ">" if option_index == selected else " "
				trimmed = fit_text_to_width(font, label, int(screen.get_width() * 0.90))
				draw_centered_text(
					screen,
					font,
					f"{prefix} {trimmed}",
					y=start_y + visible_index * line_gap,
				)

			draw_centered_text(
				screen,
				font,
				"Flechas + Enter | Esc",
				y=screen.get_height() - max(20, line_gap),
			)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return "cancelar", current_path
				if event.type == pygame.KEYDOWN:
					if event.key in (pygame.K_UP, pygame.K_LEFT):
						selected = (selected - 1) % len(options)
					elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
						selected = (selected + 1) % len(options)
					elif event.key == pygame.K_ESCAPE:
						return "cancelar", current_path
					elif event.key == pygame.K_RETURN:
						return "ok", options[selected][1]
			clock.tick(FPS)

	result, restored = _run_secondary_selector(
		"Teclado global", SELECTOR_WINDOW_SIZE, _runner
	)
	return result, restored


_MAIN_MENU_ACTION_BY_INDEX = ["iniciar", "configurar", "salir"]


def _handle_main_menu_key(event, selected, options_len):
	key = event.key
	if key in (pygame.K_UP, pygame.K_LEFT):
		return (selected - 1) % options_len, None
	if key in (pygame.K_DOWN, pygame.K_RIGHT):
		return (selected + 1) % options_len, None
	if key == pygame.K_ESCAPE:
		return selected, "salir"
	if (
		not getattr(event, "repeat", False)
		and key == pygame.K_EQUALS
		and selected == 0
		and EASTEREGG_MULTI_INSTANCE_KEY == "equals"
	):
		_launch_easteregg_instance()
		return selected, None
	if key == pygame.K_RETURN:
		action = _MAIN_MENU_ACTION_BY_INDEX[min(selected, len(_MAIN_MENU_ACTION_BY_INDEX) - 1)]
		return selected, action
	return selected, None


def _draw_main_menu(screen, options, selected):
	_debug_menu("_draw_main_menu")
	lines = (
		["HUD Overlay"]
		+ options
		+ ["Flechas + Enter"]
		+ ["= en Iniciar HUD: nueva instancia"]
	)
	font, line_gap = build_responsive_font(
		screen,
		lines,
		base_size=30,
		min_size=14,
		max_size=36,
		base_resolution=(MENU_WIDTH, MENU_HEIGHT),
		max_height_ratio=0.88,
	)
	screen.fill((0, 0, 0))
	title_y = max(28, line_gap)
	base_y = title_y + line_gap
	for index, option in enumerate(options):
		prefix = ">" if index == selected else " "
		draw_centered_text(
			screen, font, f"{prefix} {option}", y=base_y + index * line_gap
		)
	draw_centered_text(screen, font, "HUD Overlay", y=title_y)
	draw_centered_text(
		screen, font, "Flechas + Enter", y=base_y + len(options) * line_gap
	)
	if selected == 0 and EASTEREGG_ENABLE_MULTI_INSTANCE:
		draw_centered_text(
			screen,
			font,
			"=: instancia extra",
			y=screen.get_height() - max(18, line_gap),
		)
	pygame.display.flip()


def _process_main_menu_event(event, selected, len_options, ignore_videoresize):
	_debug_menu(
		f"evento {pygame.event.event_name(event.type) if hasattr(pygame.event, 'event_name') else event.type} ({getattr(event, 'w', '')}x{getattr(event, 'h', '')})"
	)
	if event.type == pygame.QUIT:
		_debug_menu("show_main_menu FIN -> salir")
		return selected, "salir", None
	if event.type == pygame.VIDEORESIZE:
		if ignore_videoresize:
			_debug_report_videoresize_stats()
			return selected, None, None
		_debug_count_videoresize()
		return selected, None, (event.w, event.h)
	if event.type == pygame.KEYDOWN and not getattr(event, "repeat", False):
		new_selected, action = _handle_main_menu_key(event, selected, len_options)
		if action:
			_debug_menu(f"show_main_menu FIN -> {action}")
		return new_selected, action, None
	return selected, None, None


def _apply_main_menu_resize(screen, pending_resize, ignore_videoresize):
	if pending_resize is None or ignore_videoresize:
		return screen
	now_ms = time.time() * 1000
	if now_ms - get_last_set_mode_time_ms() < VIDEORESIZE_COOLDOWN_MS:
		return screen
	new_w = max(MIN_WINDOW_WIDTH, pending_resize[0])
	new_h = max(MIN_WINDOW_HEIGHT, pending_resize[1])
	cur_w, cur_h = screen.get_size()
	if abs(new_w - cur_w) <= VIDEORESIZE_TOLERANCE_PX and abs(new_h - cur_h) <= VIDEORESIZE_TOLERANCE_PX:
		return screen
	return screen


def show_main_menu(screen, profile_data=None):
	_debug_menu("show_main_menu INICIO")
	options = ["Iniciar HUD", "Configurar perfiles", "Salir"]
	selected = 0
	ignore_videoresize = True
	clock = pygame.time.Clock()

	while True:
		events = pygame.event.get()
		pending_resize = None
		for event in events:
			new_selected, action, pr = _process_main_menu_event(
				event, selected, len(options), ignore_videoresize
			)
			selected = new_selected
			if pr is not None:
				pending_resize = pr
			if action:
				return action
		screen = _apply_main_menu_resize(screen, pending_resize, ignore_videoresize)
		_debug_report_videoresize_stats()
		_draw_main_menu(screen, options, selected)
		time.sleep(0.005)
		clock.tick(60)


def _open_config_on_main_window(profile_data):
	screen = pygame.display.get_surface()
	if screen is None:
		return None, None
	updated = open_profile_config_menu(screen, profile_data)
	return updated, screen


def _run_hud_setup_interactive(profile, profile_data):
	button_count, screen = _run_secondary_selector(
		"Formato de botones",
		SELECTOR_WINDOW_SIZE,
		lambda s: choose_button_format(s, profile["button_count"]),
	)
	if button_count is None:
		return None
	input_mode = None
	selected_device_path = profile.get("preferred_joystick_path")
	wants_keyboard_remap = False
	while input_mode is None:
		mode_choice, screen = _run_secondary_selector(
			"Modo de entrada",
			SELECTOR_WINDOW_SIZE,
			lambda s: choose_input_mode(s, profile["input_mode"]),
		)
		if mode_choice is None:
			return None
		if mode_choice in ["teclado", "hitbox", "mixbox"]:
			keyboard_action, screen = _confirm_keyboard_remap_secondary()
			if keyboard_action == "cancelar":
				continue
			select_status, screen = _choose_keyboard_device_secondary(
				profile.get("preferred_keyboard_path")
			)
			if select_status[0] == "cancelar":
				continue
			profile["preferred_keyboard_path"] = select_status[1]
			wants_keyboard_remap = keyboard_action == "si"
			input_mode = mode_choice
			break
		diagnostic, screen = _run_secondary_selector(
			"Diagnostico joystick",
			MAPPER_WINDOW_SIZE,
			lambda s: run_joystick_diagnostic(
				s,
				button_count,
				window_mode="normal",
				controller_style=profile.get("controller_style", "default"),
			),
		)
		if diagnostic.get("status") == "back_to_input":
			continue
		selected_device_path = diagnostic.get("device_path")
		if diagnostic.get("status") == "mapped":
			profile["joystick_bindings"] = diagnostic.get("bindings", {})
			profile["joystick_bindings_style"] = profile.get(
				"controller_style", "default"
			)
		input_mode = "joystick"
	return (
		button_count,
		input_mode,
		selected_device_path,
		wants_keyboard_remap,
		screen,
	)


def _run_hud_setup_non_interactive(profile):
	return (
		profile.get("button_count", 6),
		profile.get("input_mode", "teclado"),
		profile.get("preferred_joystick_path"),
		False,
		None,
	)


def _run_keyboard_mapping_flow(screen, profile, button_count, interactive_setup):
	if profile["key_bindings"] and any(
		k not in profile["key_bindings"]
		for k in ["Arriba", "Abajo", "Izquierda", "Derecha"]
		+ get_button_labels(button_count)
	):
		profile["key_bindings"] = {}
	if not profile["key_bindings"]:
		if not interactive_setup:
			print("[WARN] Perfil sin key_bindings en modo no interactivo.")
			return False, screen
		mapped, new_screen = _run_secondary_selector(
			"Mapeo teclado", MAPPER_WINDOW_SIZE, lambda s: map_keys(s, button_count)
		)
		if mapped:
			profile["key_bindings"] = mapped
		screen = new_screen
	return True, screen


def _run_joystick_mapping_flow(screen, profile, button_count, selected_device_path):
	if profile.get("joystick_bindings_style") != profile.get(
		"controller_style", "default"
	):
		profile["joystick_bindings"] = {}
	if not profile["joystick_bindings"]:
		mapped, new_screen = _run_secondary_selector(
			"Mapeo joystick",
			MAPPER_WINDOW_SIZE,
			lambda s: map_joystick_buttons(
				s,
				button_count,
				show_error=False,
				device_path=selected_device_path,
				controller_style=profile.get("controller_style", "default"),
			),
		)
		if not mapped:
			return False, screen
		profile["joystick_bindings"] = mapped
		profile["joystick_bindings_style"] = profile.get("controller_style", "default")
		screen = new_screen
	return True, screen


def _handle_hud_return_key(keys, training_state):
	if keys[pygame.K_BACKSPACE]:
		if has_sequence(training_state):
			_launch_training_window(sequence_to_dict(training_state))
		return
	if training_state["status"] == "recording":
		stop_recording(training_state)
	if has_sequence(training_state):
		start_playback(training_state)


def _handle_hud_tab_key(training_state):
	if training_state["status"] == "recording":
		stop_recording(training_state)
	else:
		start_recording(training_state)


def _process_hud_keydown(event, keys, training_state):
	key = event.key
	if key == pygame.K_ESCAPE:
		return False, training_state
	if (
		not getattr(event, "repeat", False)
		and key == pygame.K_EQUALS
		and EASTEREGG_MULTI_INSTANCE_KEY == "equals"
	):
		_launch_easteregg_instance()
		return True, training_state
	if key == pygame.K_TAB:
		_handle_hud_tab_key(training_state)
		return True, training_state
	if key == pygame.K_RETURN:
		_handle_hud_return_key(keys, training_state)
		return True, training_state
	if key == pygame.K_BACKSPACE and not keys[pygame.K_RETURN]:
		clear_sequence(training_state)
	return True, training_state


def _process_hud_events(events, keys, training_state):
	running = True
	pending_resize = None
	for event in events:
		if event.type == pygame.VIDEORESIZE:
			_debug_count_videoresize()
			pending_resize = (event.w, event.h)
		elif event.type == pygame.QUIT:
			running = False
			break
		elif event.type == pygame.KEYDOWN:
			running, training_state = _process_hud_keydown(event, keys, training_state)
			if not running:
				break
	return running, pending_resize


def _apply_hud_resize(screen, pending_resize, ignore_videoresize):
	if pending_resize is None or ignore_videoresize:
		return screen
	now_ms = time.time() * 1000
	if now_ms - get_last_set_mode_time_ms() < VIDEORESIZE_COOLDOWN_MS:
		return screen
	new_w = max(MIN_WINDOW_WIDTH, pending_resize[0])
	new_h = max(MIN_WINDOW_HEIGHT, pending_resize[1])
	cur_w, cur_h = screen.get_size()
	return screen


def _run_hud_main_loop(
	screen,
	input_state,
	button_count,
	profile_data,
	input_mode,
	selected_device_path,
	profile,
	force_tournament,
):
	labels = get_button_labels(button_count)
	tournament_mode = bool(force_tournament)
	resolved_icons = resolve_icons_map(profile["id"], button_count)
	load_icons(button_count, resolved_icons, enable_icons=not tournament_mode)
	set_stick_color(profile["joystick_color"])
	set_stick_colors(
		profile.get("joystick_knob_color", profile["joystick_color"]),
		profile.get("joystick_bar_color", [0, 0, 0]),
		profile.get("joystick_ring_color", [255, 255, 255]),
	)
	set_button_colors(
		profile.get("button_color_inactive", [80, 80, 80]),
		profile.get("button_color_active", [255, 0, 0]),
	)
	set_controller_style(profile.get("controller_style", "default"))
	set_render_mode("tournament" if tournament_mode else "normal")
	layout = (
		"mixbox"
		if input_mode == "mixbox"
		else ("hitbox" if input_mode == "hitbox" else "stick")
	)
	set_input_layout(layout)
	set_hitbox_alt_layout(profile.get("hitbox_alt_layout", False))
	threading.Thread(
		target=start_input_listener,
		args=(
			input_mode,
			button_count,
			input_state,
			selected_device_path,
			profile.get("preferred_keyboard_path"),
		),
		daemon=True,
	).start()
	clock = pygame.time.Clock()
	running = True
	bg = get_background_color(profile_data.get("capture_mode", "normal"))
	target_fps = TOURNAMENT_FPS if tournament_mode else FPS
	training_state = create_training_state()
	ignore_videoresize = True
	while running:
		keys = pygame.key.get_pressed()
		if input_mode in ("teclado", "hitbox", "mixbox"):
			poll_pygame_keyboard_if_needed(input_state, keys)
		events = pygame.event.get()
		running, pending_resize = _process_hud_events(events, keys, training_state)
		snapshot_if_recording(training_state, input_state)
		if training_state["status"] == "playing":
			update_playback(training_state, input_state)
		screen.fill(bg)
		draw_hud(screen, input_state, button_count, profile)
		pygame.display.flip()
		screen = _apply_hud_resize(screen, pending_resize, ignore_videoresize)
		_debug_report_videoresize_stats()
		time.sleep(0.005)
		clock.tick(target_fps)


def _run_hud_setup(profile, profile_data, interactive_setup):
	if interactive_setup:
		result = _run_hud_setup_interactive(profile, profile_data)
		if result is None:
			return None
		bc, im, sdp, wkr, setup_screen = result
		return bc, im, sdp, wkr, setup_screen
	bc, im, sdp, wkr, _ = _run_hud_setup_non_interactive(profile)
	return bc, im, sdp, wkr, None


def _apply_session_profile(profile, button_count, input_mode, selected_device_path, labels, wants_keyboard_remap):
	profile["button_count"] = button_count
	profile["input_mode"] = input_mode
	profile["preferred_joystick_path"] = selected_device_path
	profile["button_icons"] = {lbl: profile["button_icons"].get(lbl) for lbl in labels}
	if profile["joystick_bindings"] and any(lbl not in profile["joystick_bindings"] for lbl in labels):
		profile["joystick_bindings"] = {}
	if input_mode in ["teclado", "hitbox", "mixbox"] and wants_keyboard_remap:
		profile["key_bindings"] = {}


def _run_input_mapping_flows(screen, profile, button_count, input_mode, selected_device_path, interactive_setup):
	if input_mode in ["teclado", "hitbox", "mixbox"]:
		ok, screen = _run_keyboard_mapping_flow(screen, profile, button_count, interactive_setup)
		if not ok:
			return False, screen
	if input_mode == "joystick":
		ok, screen = _run_joystick_mapping_flow(screen, profile, button_count, selected_device_path)
		if not ok:
			return False, screen
	return True, screen


def _prepare_hud_session(ctx, interactive_setup=True, force_tournament=False):
	"""Rellena ctx.hud tras setup y mapeos. Retorna False si el usuario cancela."""
	profile = get_active_profile(ctx.profile_data)
	setup_result = _run_hud_setup(profile, ctx.profile_data, interactive_setup)
	if setup_result is None:
		return False
	button_count, input_mode, selected_device_path, wants_keyboard_remap, setup_screen = setup_result
	if setup_screen is not None:
		ctx.screen = setup_screen

	labels = get_button_labels(button_count)
	_apply_session_profile(profile, button_count, input_mode, selected_device_path, labels, wants_keyboard_remap)

	ok, ctx.screen = _run_input_mapping_flows(
		ctx.screen,
		profile,
		button_count,
		input_mode,
		selected_device_path,
		interactive_setup,
	)
	if not ok:
		return False

	sync_active_profile_to_legacy_files(ctx.profile_data)
	save_profiles_data(ctx.profile_data)
	ctx.hud = {
		"profile": profile,
		"button_count": button_count,
		"input_mode": input_mode,
		"selected_device_path": selected_device_path,
		"force_tournament": force_tournament,
		"input_state": {"stick": [0, 0], "buttons": [False] * len(labels)},
	}
	return True


def _run_hud_main_loop_from_ctx(ctx):
	h = ctx.hud
	_run_hud_main_loop(
		ctx.screen,
		h["input_state"],
		h["button_count"],
		ctx.profile_data,
		h["input_mode"],
		h["selected_device_path"],
		h["profile"],
		h["force_tournament"],
	)


def run_hud_session(
	screen, profile_data, interactive_setup=True, force_tournament=False
):
	ctx = ApplicationContext(screen)
	ctx.profile_data = profile_data
	ctx.screen = screen
	if not _prepare_hud_session(ctx, interactive_setup, force_tournament):
		return False
	_run_hud_main_loop_from_ctx(ctx)
	return True


def _handle_boot_state(ctx):
	global _current_window_mode
	ctx.profile_data = load_profiles_data()
	_current_window_mode = "normal"
	set_ui_font_family(ctx.profile_data.get("ui_font_family", "JetBrainsMono"))
	return MainMenuState


def _handle_main_menu_state(ctx):
	global _current_window_mode
	_current_window_mode = "normal"
	set_ui_font_family(ctx.profile_data.get("ui_font_family", "JetBrainsMono"))
	action = show_main_menu(ctx.screen, ctx.profile_data)
	_debug_menu(f"state MainMenu action={action}")
	if action == "salir":
		return ModalState
	if action == "configurar":
		return ProfileConfigState
	if action == "iniciar":
		return HudSetupState
	return MainMenuState


def _handle_modal_state(ctx):
	confirmed, ctx.screen = _confirm_exit_secondary()
	if confirmed:
		ctx.running = False
		return STOP
	_debug_menu("ModalState: salida cancelada")
	return MainMenuState


def _handle_profile_config_state(ctx):
	updated, ctx.screen = _open_config_on_main_window(ctx.profile_data)
	if updated:
		ctx.profile_data = updated
		save_profiles_data(ctx.profile_data)
		set_ui_font_family(ctx.profile_data.get("ui_font_family", "JetBrainsMono"))
	_debug_menu("state ProfileConfig -> MainMenu")
	return MainMenuState


def _handle_hud_setup_state(ctx):
	# Misma ventana que el menú principal: no se llama set_mode aquí.
	if not _prepare_hud_session(ctx, interactive_setup=True, force_tournament=False):
		return MainMenuState
	return HudRunState


def _handle_hud_run_state(ctx):
	_run_hud_main_loop_from_ctx(ctx)
	ctx.clear_hud()
	return MainMenuState


_STATE_HANDLERS = {
	BootState: _handle_boot_state,
	MainMenuState: _handle_main_menu_state,
	ModalState: _handle_modal_state,
	ProfileConfigState: _handle_profile_config_state,
	HudSetupState: _handle_hud_setup_state,
	HudRunState: _handle_hud_run_state,
}


def main():
	global _current_window_mode
	if _early_cli(sys.argv):
		sys.exit(0)
	if not _preflight_startup():
		sys.exit(1)
	pygame.init()
	os.environ["SDL_VIDEO_WINDOW_POS"] = "100,100"
	_current_window_mode = "normal"
	screen = _set_window_size(APP_WINDOW_WIDTH, APP_WINDOW_HEIGHT, "Arcade HUD Overlay")

	ctx = ApplicationContext(screen)
	sm = StateManager(BootState)
	while ctx.running:
		handler = _STATE_HANDLERS[sm.current]
		next_state = handler(ctx)
		if next_state is STOP:
			break
		sm.set_state(next_state)

	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()
