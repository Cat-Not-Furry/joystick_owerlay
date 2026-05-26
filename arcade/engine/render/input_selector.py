# input_selector.py

# --- Pregunta por el metodo de entrada ---

from utils import draw_centered_text, build_responsive_font, MenuArrowRepeater
import pygame

KEY_TO_MODE = {pygame.K_t: "teclado", pygame.K_j: "joystick", pygame.K_h: "hitbox", pygame.K_m: "mixbox"}

_ESC_SENTINEL = object()


def _process_input_mode_event(event, selected, options):
	"""Procesa KEYDOWN. Retorna (new_selected, value). value=str para retornar, _ESC_SENTINEL para cancelar, None para seguir."""
	key = event.key
	if key in (pygame.K_UP, pygame.K_LEFT):
		return (selected - 1) % len(options), None
	if key in (pygame.K_DOWN, pygame.K_RIGHT):
		return (selected + 1) % len(options), None
	if key == pygame.K_RETURN:
		return selected, options[selected]
	if key in KEY_TO_MODE:
		return selected, KEY_TO_MODE[key]
	if key == pygame.K_ESCAPE:
		return selected, _ESC_SENTINEL
	return selected, None


def _render_input_mode_options(screen, font, line_gap, options, selected, prompt):
	screen.fill((0, 0, 0))
	title_y = max(28, line_gap)
	start_y = title_y + line_gap
	draw_centered_text(screen, font, prompt, y=title_y)
	for index, option in enumerate(options):
		prefix = ">" if index == selected else " "
		draw_centered_text(screen, font, f"{prefix} {option.upper()}", y=start_y + index * line_gap)
	draw_centered_text(screen, font, "Esc para volver", y=screen.get_height() - max(20, line_gap))


def choose_input_mode(screen, initial_mode="teclado"):
	options = ["teclado", "joystick", "hitbox", "mixbox"]
	prompt = "Selecciona entrada (flechas + Enter):"
	selected = options.index(initial_mode) if initial_mode in options else 0
	clock = pygame.time.Clock()
	repeater = MenuArrowRepeater()

	while True:
		lines = [prompt] + [o.upper() for o in options]
		font, line_gap = build_responsive_font(screen, lines, base_size=28, min_size=14, max_size=34, base_resolution=(500, 280))
		_render_input_mode_options(screen, font, line_gap, options, selected, prompt)
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return None
			if event.type == pygame.KEYDOWN:
				if event.key in (
					pygame.K_UP,
					pygame.K_DOWN,
					pygame.K_LEFT,
					pygame.K_RIGHT,
				):
					dnav = repeater.consume_keydown(event)
					if dnav is not None:
						selected = (selected + dnav) % len(options)
				else:
					repeater.reset()
					selected, value = _process_input_mode_event(event, selected, options)
					if value is _ESC_SENTINEL:
						return None
					if value is not None:
						return value
		d2 = repeater.tick_held()
		if d2 is not None:
			selected = (selected + d2) % len(options)
		clock.tick(60)

