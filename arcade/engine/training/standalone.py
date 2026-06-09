# training/standalone.py
# Ventana de entrenamiento independiente. Recibe secuencia por archivo temporal.
# Cierra con Esc o WINDOWFOCUSLOST.

import json
import os
import sys
import time

def _find_project_root():
	path = os.path.dirname(os.path.abspath(__file__))
	while path and path != "/":
		if os.path.exists(os.path.join(path, "main.py")):
			return path
		path = os.path.dirname(path)
	return os.getcwd()


def run_training_window(sequence_path):
	"""Ejecuta ventana de entrenamiento con la secuencia cargada desde sequence_path."""
	root = _find_project_root()
	sys.path.insert(0, root)
	os.chdir(root)

	import pygame
	from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, get_button_labels, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, VIDEORESIZE_COOLDOWN_MS, VIDEORESIZE_TOLERANCE_PX
	from render import draw_hud, load_icons, load_system_icons, set_stick_color, set_stick_colors, set_button_colors, set_controller_style, set_render_mode, set_input_layout
	from utils import track_set_mode, get_last_set_mode_time_ms
	from training.recorder import (
		create_training_state,
		start_recording,
		stop_recording,
		start_playback,
		clear_sequence,
		snapshot_if_recording,
		update_playback,
		has_sequence,
		dict_to_sequence,
	)

	def _process_training_events(events, keys, training_state):
		running = True
		pending_resize = None
		enter_backspace = keys[pygame.K_RETURN] and keys[pygame.K_BACKSPACE]
		for event in events:
			if event.type == pygame.VIDEORESIZE:
				pending_resize = (event.w, event.h)
			elif event.type == pygame.QUIT:
				running = False
				break
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
					break
				if event.key == pygame.K_TAB and not enter_backspace:
					if training_state["status"] == "recording":
						stop_recording(training_state)
					else:
						start_recording(training_state)
				elif event.key == pygame.K_RETURN and not keys[pygame.K_BACKSPACE]:
					if training_state["status"] == "recording":
						stop_recording(training_state)
					if has_sequence(training_state):
						start_playback(training_state)
				elif event.key == pygame.K_BACKSPACE and not keys[pygame.K_RETURN]:
					clear_sequence(training_state)
			elif event.type == pygame.WINDOWFOCUSLOST:
				running = False
				break
		return running, pending_resize

	def _apply_training_resize(screen, pending_resize):
		return screen

	with open(sequence_path, "r") as f:
		data = json.load(f)
	try:
		os.unlink(sequence_path)
	except Exception:
		pass
	sequence = dict_to_sequence(data)
	if not sequence:
		print("[WARN] Secuencia vacía o inválida.")
		return

	button_count = len(sequence[0]["buttons"]) if sequence else 6
	labels = get_button_labels(button_count)
	if button_count != len(labels):
		button_count = 6

	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption("Joystick Overlay — Modo entrenamiento")
	track_set_mode()

	training_state = create_training_state()
	training_state["sequence"] = sequence

	input_state = {
		"stick": [0, 0],
		"buttons": [False] * len(labels),
		"select": False,
		"start": False,
	}
	load_icons(button_count, {}, enable_icons=False)
	load_system_icons({"icon_pack": "default", "id": ""})
	set_stick_color([0, 255, 0])
	set_stick_colors([0, 255, 0], [0, 0, 0], [255, 255, 255])
	set_button_colors([80, 80, 80], [255, 0, 0])
	set_controller_style("default")
	set_render_mode("normal")
	set_input_layout("stick")

	clock = pygame.time.Clock()
	running = True
	bg = (0, 0, 0)

	while running:
		keys = pygame.key.get_pressed()
		events = pygame.event.get()
		running, pending_resize = _process_training_events(events, keys, training_state)
		screen = _apply_training_resize(screen, pending_resize)
		snapshot_if_recording(training_state, input_state)
		if training_state["status"] == "playing":
			update_playback(training_state, input_state)
		screen.fill(bg)
		draw_hud(screen, input_state, button_count)
		pygame.display.flip()
		clock.tick(FPS)

	pygame.quit()


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Uso: python -m training.standalone <ruta_secuencia.json>")
		sys.exit(1)
	run_training_window(sys.argv[1])
