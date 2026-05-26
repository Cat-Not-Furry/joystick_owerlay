# maps/input_reader.py - Lee entradas de teclado/joystick (Windows: keyboard + pygame)

import json
import threading
import time
import pygame

from config import BINDINGS_PATH, JOYSTICK_BINDINGS_PATH, get_button_labels, get_bindings_format_key
from maps import keyboard_backend
from core import get_extensions_runtime, get_input_history

_use_pygame_poll = False
_poll_bindings = {}
_poll_button_count = 6


def _record_input_event(mode, stick, buttons):
	event = {
		"ts_ms": int(time.time() * 1000),
		"mode": mode,
		"stick": [float(stick[0]), float(stick[1])],
		"buttons": [bool(value) for value in buttons],
	}
	get_input_history().append(event)
	get_extensions_runtime().emit("on_input_event", event)


def uses_pygame_keyboard_poll():
	return _use_pygame_poll


def poll_pygame_keyboard_if_needed(input_state, keys_pressed):
	if not _use_pygame_poll:
		return
	keyboard_backend.poll_keyboard_pygame(
		input_state, _poll_bindings, _poll_button_count, keys_pressed
	)
	_record_input_event("keyboard_focus", input_state["stick"], input_state["buttons"])


def _load_keyboard_bindings(button_count):
	try:
		with open(BINDINGS_PATH, "r") as f:
			bindings_all = json.load(f)
	except Exception:
		bindings_all = {}
	formato = get_bindings_format_key(button_count)
	return bindings_all.get(formato, {}) if isinstance(bindings_all, dict) else {}


def listen_keyboard_global(input_state, button_count, bindings_map):
	import keyboard

	labels = get_button_labels(button_count)
	print("[INFO] Escuchando teclado global (keyboard)...")

	while True:
		dx = int(keyboard.is_pressed(bindings_map.get("Derecha", ""))) - int(
			keyboard.is_pressed(bindings_map.get("Izquierda", ""))
		)
		dy = int(keyboard.is_pressed(bindings_map.get("Abajo", ""))) - int(
			keyboard.is_pressed(bindings_map.get("Arriba", ""))
		)
		if dx != 0 and dy != 0:
			dx *= 0.7
			dy *= 0.7
		input_state["stick"] = [dx, dy]

		for index, label in enumerate(labels):
			keyname = bindings_map.get(label, "")
			input_state["buttons"][index] = (
				keyboard.is_pressed(keyname) if keyname else False
			)
		_record_input_event("keyboard_global", input_state["stick"], input_state["buttons"])

		time.sleep(0.01)


def start_input_listener(
	mode,
	button_count,
	input_state,
	preferred_device_path=None,
	preferred_keyboard_path=None,
):
	global _use_pygame_poll, _poll_bindings, _poll_button_count

	keyboard_backend.reset_backend_state()
	_use_pygame_poll = False
	_poll_bindings = {}
	_poll_button_count = button_count

	if mode in ["teclado", "hitbox", "mixbox"]:
		local_bindings = _load_keyboard_bindings(button_count)
		want_global = keyboard_backend.should_attempt_global_hook(preferred_keyboard_path)
		if want_global and keyboard_backend.try_init_global_keyboard():
			threading.Thread(
				target=listen_keyboard_global,
				args=(input_state, button_count, local_bindings),
				daemon=True,
			).start()
		else:
			_use_pygame_poll = True
			_poll_bindings = local_bindings
			_poll_button_count = button_count
			print(
				"[INFO] Teclado con foco: la ventana del HUD debe estar enfocada para leer teclas."
			)
	elif mode == "joystick":
		try:
			with open(JOYSTICK_BINDINGS_PATH, "r") as f:
				all_bindings = json.load(f)
		except Exception:
			all_bindings = {}
		formato = get_bindings_format_key(button_count)
		local_bindings = all_bindings.get(formato, {})
		threading.Thread(
			target=listen_joystick,
			args=(input_state, button_count, local_bindings, preferred_device_path),
			daemon=True,
		).start()


def _get_joystick_by_path(preferred_device_path):
	pygame.joystick.init()
	count = pygame.joystick.get_count()
	if count == 0:
		return None
	if preferred_device_path is not None:
		try:
			idx = int(preferred_device_path)
			if 0 <= idx < count:
				return pygame.joystick.Joystick(idx)
		except (ValueError, TypeError):
			pass
	return pygame.joystick.Joystick(0)


def listen_joystick(input_state, button_count, bindings_map, preferred_device_path=None):
	joystick = _get_joystick_by_path(preferred_device_path)
	if joystick is None:
		print("[ERROR] No se detectó joystick compatible.")
		labels = get_button_labels(button_count)
		input_state["stick"] = [0, 0]
		input_state["buttons"] = [False] * len(labels)
		return

	joystick.init()
	labels = get_button_labels(button_count)
	print(f"[INFO] Leyendo entradas desde: {joystick.get_name()}")

	while True:
		pygame.event.pump()

		axis_x = joystick.get_axis(0) if joystick.get_numaxes() > 0 else 0
		axis_y = joystick.get_axis(1) if joystick.get_numaxes() > 1 else 0
		input_state["stick"] = [axis_x, axis_y]

		for i, label in enumerate(labels):
			btn = bindings_map.get(label, -1)
			if isinstance(btn, int) and btn >= 0 and btn < joystick.get_numbuttons():
				input_state["buttons"][i] = bool(joystick.get_button(btn))
		_record_input_event("joystick", input_state["stick"], input_state["buttons"])

		time.sleep(0.01)
