"""Asistente mínimo de primer arranque (sin i18n)."""

import os

import pygame

from config import USER_DIR
from utils import draw_centered_text, build_responsive_font, fit_text_to_width, run_modal_child_window


_FIRST_RUN_FLAG = os.path.join(USER_DIR, ".first_run_wizard_done")


def first_run_wizard_needed():
	return not os.path.isfile(_FIRST_RUN_FLAG)


def _mark_first_run_done():
	os.makedirs(USER_DIR, exist_ok=True)
	try:
		with open(_FIRST_RUN_FLAG, "w", encoding="utf-8") as fh:
			fh.write("1\n")
	except Exception:
		pass


def run_first_run_wizard_if_needed(screen, profile_data, window_mode="floating_hint"):
	"""Muestra bienvenida breve y marca wizard completado."""
	if not first_run_wizard_needed():
		return profile_data

	def _runner(secondary):
		clock = pygame.time.Clock()
		while True:
			lines = [
				"Bienvenida a Joystick Overlay",
				"Usa el menu para dispositivo, HUD y perfiles.",
				"Enter: continuar",
			]
			font, line_gap = build_responsive_font(
				secondary,
				lines,
				base_size=22,
				min_size=12,
				max_size=28,
				base_resolution=(520, 280),
			)
			secondary.fill((0, 0, 0))
			y = max(24, line_gap)
			for line in lines:
				t = fit_text_to_width(font, line, int(secondary.get_width() * 0.9))
				draw_centered_text(secondary, font, t, y=y)
				y += line_gap
			pygame.display.flip()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
					return True
			clock.tick(60)

	run_modal_child_window(
		title="Bienvenida",
		size=(520, 280),
		window_mode=window_mode,
		runner=_runner,
		screen=screen,
	)
	_mark_first_run_done()
	return profile_data
