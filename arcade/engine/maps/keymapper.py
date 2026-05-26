# keymapper.py

# --- El encargado de mappear el teclado para su uso en main.py ---

import json
import os

from utils import draw_centered_text, build_responsive_font
import pygame

from config import BINDINGS_PATH, get_button_labels
from profiles.bindings_storage import (
	load_bindings_tree,
	save_bindings_tree,
	set_slice,
	path_keyboard_family_file,
	normalize_flat_bindings_for_format_8,
)

# Declara las direcciones

DIRECTIONS = ["Arriba", "Abajo", "Izquierda", "Derecha"]


def map_keys(screen, button_count, profile_id, format_key, input_mode="teclado"):
	"""
	Mapea teclado y guarda en el JSON del perfil (teclado/hitbox/mixbox) bajo format_key.
	Mantiene legacy_bindings.json alineado con ese slice (misma clave).
	"""
	bindings = {}

	print(f"[INFO] Configurando bindings para: {format_key}")

	for name in DIRECTIONS + list(get_button_labels(button_count)) + ["SELECT", "START"]:
		key = wait_for_keypress(screen, f"Presiona una tecla para: {name}")
		bindings[name] = key

	bindings = normalize_flat_bindings_for_format_8(bindings, button_count)

	path = path_keyboard_family_file(profile_id, input_mode)
	tree = load_bindings_tree(path)
	tree = set_slice(tree, format_key, bindings)
	save_bindings_tree(path, tree)

	if os.path.exists(BINDINGS_PATH):
		with open(BINDINGS_PATH, "r", encoding="utf-8") as f:
			all_bindings = json.load(f)
	else:
		all_bindings = {}
	if not isinstance(all_bindings, dict):
		all_bindings = {}
	all_bindings[format_key] = bindings
	dir_path = os.path.dirname(BINDINGS_PATH)
	if dir_path:
		os.makedirs(dir_path, exist_ok=True)
	with open(BINDINGS_PATH, "w", encoding="utf-8") as f:
		json.dump(all_bindings, f, indent=4)

	return bindings


def wait_for_keypress(screen, message):
	waiting = True
	while waiting:
		font, line_gap = build_responsive_font(
			screen,
			[message, "Esc para cancelar"],
			base_size=28,
			min_size=14,
			max_size=34,
			base_resolution=(620, 360),
		)
		screen.fill((0, 0, 0))
		title_y = max(32, line_gap)
		draw_centered_text(screen, font, message, y=title_y)
		draw_centered_text(screen, font, "Esc para cancelar", y=title_y + line_gap)
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					exit()
				return event.key
