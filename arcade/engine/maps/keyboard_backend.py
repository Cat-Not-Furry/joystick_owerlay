# maps/keyboard_backend.py - Aislamiento de teclado global (keyboard) vs pygame

import sys

import pygame

_global_keyboard_ready = False
_init_attempted = False


def reset_backend_state():
	global _global_keyboard_ready, _init_attempted
	_global_keyboard_ready = False
	_init_attempted = False


def should_attempt_global_hook(preferred_keyboard_path):
	"""En Windows se intenta hook global salvo que el perfil fuerce solo foco."""
	if preferred_keyboard_path is not None:
		return True
	import os
	return os.environ.get("HUD_KEYBOARD_GLOBAL", "1") != "0"


def try_init_global_keyboard():
	"""
	Inicializa uso de la librería keyboard (Windows).
	Retorna True si keyboard.is_pressed es usable desde un hilo.
	"""
	global _global_keyboard_ready, _init_attempted
	if _init_attempted:
		return _global_keyboard_ready
	_init_attempted = True
	try:
		import keyboard as kb_module
		kb_module.is_pressed("shift")
		_global_keyboard_ready = True
	except Exception:
		_global_keyboard_ready = False
	return _global_keyboard_ready


def is_pressed_key_name(key_name):
	if not _global_keyboard_ready or not key_name:
		return False
	try:
		import keyboard as kb_module
		return bool(kb_module.is_pressed(key_name))
	except Exception:
		return False


def pygame_key_from_name(key_name):
	if not key_name:
		return None
	try:
		return pygame.key.key_code(str(key_name))
	except Exception:
		return None


def poll_keyboard_pygame(input_state, bindings_map, button_count, keys_pressed):
	from config import get_button_labels

	labels = get_button_labels(button_count)

	def _down(kn):
		pk = pygame_key_from_name(kn) if kn else None
		if pk is None:
			return False
		try:
			return bool(keys_pressed[pk])
		except Exception:
			return False

	dx = int(_down(bindings_map.get("Derecha", ""))) - int(_down(bindings_map.get("Izquierda", "")))
	dy = int(_down(bindings_map.get("Abajo", ""))) - int(_down(bindings_map.get("Arriba", "")))
	if dx != 0 and dy != 0:
		dx *= 0.7
		dy *= 0.7
	input_state["stick"] = [dx, dy]

	for index, label in enumerate(labels):
		kn = bindings_map.get(label, "")
		input_state["buttons"][index] = _down(kn)
