# hud_renderer.py

# --- Encargado de dibujar todo en la ventana ---

import os
import pygame
from utils import get_ui_font

from config import (
    JOYSTICK_CENTER,
    JOYSTICK_RADIUS,
    JOYSTICK_STICK_LENGTH,
    BUTTON_RADIUS,
    get_hud_scale,
    get_icon_paths,
    get_button_positions,
    get_button_positions_hitbox_mixbox,
    get_system_button_positions,
    COLOR_STICK,
    COLOR_STICK_KNOB,
    COLOR_BUTTON_ACTIVE,
    COLOR_BUTTON_INACTIVE,
    COLOR_TEXT,
    get_button_labels,
    get_hud_fallback_text,
    normalize_controller_style,
)
from profiles.hud_layout import compute_direction_centers_screen

icons = []
system_icon_select = None
system_icon_start = None
current_controller_style = "default"
current_render_mode = "normal"
current_input_layout = "stick"
current_hitbox_alt_layout = False
current_stick_knob_color = COLOR_STICK_KNOB
current_stick_bar_color = (0, 0, 0)
current_stick_ring_color = (255, 255, 255)
current_button_inactive_color = COLOR_BUTTON_INACTIVE
current_button_active_color = COLOR_BUTTON_ACTIVE


def _normalize_color(color_value, fallback):
    if isinstance(color_value, list) and len(color_value) == 3:
        return tuple(color_value)
    if isinstance(color_value, tuple) and len(color_value) == 3:
        return color_value
    return fallback


def load_icons(button_count, custom_icon_paths=None, enable_icons=True):
    global icons
    icons = []
    labels = get_button_labels(button_count)
    if not enable_icons:
        icons = [None for _ in labels]
        return

    default_paths = get_icon_paths(button_count)
    icon_paths = []
    for index, label in enumerate(labels):
        path = default_paths[index]
        if custom_icon_paths and label in custom_icon_paths:
            custom_path = custom_icon_paths[label]
            if custom_path is None:
                icon_paths.append(None)
                continue
            path = custom_path
        icon_paths.append(path)

    for path in icon_paths:
        if path is None:
            icons.append(None)
            continue
        if os.path.exists(path):
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(
                image, (BUTTON_RADIUS * 2, BUTTON_RADIUS * 2)
            )
            icons.append(image)
        else:
            print(f"[WARN] Ícono no encontrado: {path}")
            icons.append(None)


def load_system_icons(profile):
    """Carga iconos Select/Start desde el icon_pack del perfil."""
    global system_icon_select, system_icon_start
    system_icon_select = None
    system_icon_start = None
    if not isinstance(profile, dict):
        return
    from core.assets_resolver import resolve_system_button_paths_from_profile_dict

    sel_path, start_path = resolve_system_button_paths_from_profile_dict(profile)
    size = max(16, int(BUTTON_RADIUS * 2 * 0.72))

    def _load(path):
        if not path or not os.path.exists(path):
            return None
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, (size, size))

    system_icon_select = _load(sel_path)
    system_icon_start = _load(start_path)


def draw_select_start(
    screen,
    input_state,
    button_count,
    layout_offsets=None,
    text_only=False,
):
    """Dibuja Select y Start bajo la rejilla de acción."""
    global system_icon_select, system_icon_start
    scale = _get_scale(screen)
    sox, soy = (0, 0)
    sys_pair = None
    if layout_offsets:
        sox, soy = layout_offsets.get("system_offset", (0, 0))
        sys_pair = layout_offsets.get("system_button_pixel_offsets")
    four_a = (
        bool(layout_offsets.get("layout_four_variant_4a"))
        if layout_offsets
        else False
    )
    pos_sel, pos_sta = get_system_button_positions(
        button_count,
        screen.get_width(),
        screen.get_height(),
        current_input_layout,
        controller_style=current_controller_style,
        layout_four_variant_4a=four_a,
    )
    if (
        sys_pair
        and isinstance(sys_pair, (list, tuple))
        and len(sys_pair) >= 2
        and isinstance(sys_pair[0], (list, tuple))
        and isinstance(sys_pair[1], (list, tuple))
        and len(sys_pair[0]) >= 2
        and len(sys_pair[1]) >= 2
    ):
        dsx, dsy = int(sys_pair[0][0]), int(sys_pair[0][1])
        dax, day = int(sys_pair[1][0]), int(sys_pair[1][1])
        pos_sel = (pos_sel[0] + dsx + sox, pos_sel[1] + dsy + soy)
        pos_sta = (pos_sta[0] + dax + sox, pos_sta[1] + day + soy)
    else:
        pos_sel = (pos_sel[0] + sox, pos_sel[1] + soy)
        pos_sta = (pos_sta[0] + sox, pos_sta[1] + soy)
    sel_on = bool(input_state.get("select", False))
    start_on = bool(input_state.get("start", False))
    radius = max(6, int(BUTTON_RADIUS * scale * 0.62))
    icon_sz = int(BUTTON_RADIUS * 2 * scale * 0.62)
    font = get_ui_font(max(9, int(14 * scale)), variant="bold")

    def _draw_one(center, pressed, surf, label_txt):
        if surf is not None and not text_only:
            sc = pygame.transform.smoothscale(surf, (icon_sz, icon_sz))
            rct = sc.get_rect(center=center)
            screen.blit(sc, rct)
            if pressed:
                pygame.draw.circle(
                    screen,
                    current_button_active_color,
                    center,
                    radius,
                    max(1, int(2 * scale)),
                )
            return
        col = current_button_active_color if pressed else current_button_inactive_color
        pygame.draw.circle(screen, col, center, radius)
        t = font.render(label_txt, True, COLOR_TEXT)
        screen.blit(t, t.get_rect(center=center))

    _draw_one(pos_sel, sel_on, system_icon_select, "Sel")
    _draw_one(pos_sta, start_on, system_icon_start, "St")


def set_stick_color(color):
    global current_stick_knob_color
    current_stick_knob_color = _normalize_color(color, COLOR_STICK_KNOB)


def set_stick_colors(knob_color, bar_color, ring_color):
    global current_stick_knob_color, current_stick_bar_color, current_stick_ring_color
    current_stick_knob_color = _normalize_color(knob_color, COLOR_STICK_KNOB)
    current_stick_bar_color = _normalize_color(bar_color, (0, 0, 0))
    current_stick_ring_color = _normalize_color(ring_color, (255, 255, 255))


def set_controller_style(style):
    global current_controller_style
    current_controller_style = normalize_controller_style(style or "default")


def set_render_mode(render_mode):
    global current_render_mode
    current_render_mode = (
        render_mode if render_mode in ["normal", "tournament"] else "normal"
    )


def set_input_layout(layout_mode):
    global current_input_layout
    prev = current_input_layout
    current_input_layout = (
        layout_mode if layout_mode in ["stick", "hitbox", "mixbox"] else "stick"
    )
    if current_input_layout != prev:
        print(f"[INFO] Modo overlay: {current_input_layout}.")


def set_hitbox_alt_layout(alt):
    global current_hitbox_alt_layout
    prev = current_hitbox_alt_layout
    current_hitbox_alt_layout = bool(alt)
    if current_hitbox_alt_layout != prev:
        print(
            f"[INFO] Posicion Hitbox alternativa: {'On' if current_hitbox_alt_layout else 'Off'}."
        )


def set_button_colors(inactive_color, active_color):
    global current_button_inactive_color, current_button_active_color
    current_button_inactive_color = _normalize_color(
        inactive_color, COLOR_BUTTON_INACTIVE
    )
    current_button_active_color = _normalize_color(active_color, COLOR_BUTTON_ACTIVE)


def draw_hud(screen, state, button_count, layout_offsets=None):
    if layout_offsets is None:
        labels = get_button_labels(button_count)
        layout_offsets = {
            "dirs_offset": (0, 0),
            "buttons_offset": (0, 0),
            "button_pixel_offsets": [(0, 0)] * len(labels),
            "layout_four_variant_4a": False,
            "system_offset": (0, 0),
        }
    if current_render_mode == "tournament":
        draw_tournament_mode(screen, state, button_count, layout_offsets=layout_offsets)
        return

    do = layout_offsets.get("dirs_offset", (0, 0))
    bo = layout_offsets.get("buttons_offset", (0, 0))
    if current_input_layout == "mixbox":
        draw_mixbox_direction_pad(
            screen, state["stick"], dirs_offset=do, layout_offsets=layout_offsets
        )
    elif current_input_layout == "hitbox":
        draw_hitbox_direction_pad(
            screen, state["stick"], dirs_offset=do, layout_offsets=layout_offsets
        )
    else:
        draw_stick(screen, state["stick"], dirs_offset=do)
    draw_buttons(
        screen,
        state["buttons"],
        button_count,
        text_only=False,
        layout_offsets=layout_offsets,
    )
    draw_select_start(
        screen, state, button_count, layout_offsets=layout_offsets, text_only=False
    )


def _get_scale(screen):
    return get_hud_scale(screen.get_width(), screen.get_height())


def draw_stick(screen, vec, dirs_offset=(0, 0)):
    scale = _get_scale(screen)
    ox, oy = dirs_offset
    center_x = int(JOYSTICK_CENTER[0] * scale) + ox
    center_y = int(JOYSTICK_CENTER[1] * scale) + oy
    stick_len = int(JOYSTICK_STICK_LENGTH * scale)
    radius = int(JOYSTICK_RADIUS * scale)
    knob_radius = max(4, int(12 * scale))
    ring_radius = max(6, int(16 * scale))
    line_width = max(2, int(6 * scale))

    end_x = int(center_x + vec[0] * stick_len)
    end_y = int(center_y + vec[1] * stick_len)

    pygame.draw.circle(screen, COLOR_STICK, (center_x, center_y), radius)
    pygame.draw.line(
        screen,
        current_stick_bar_color,
        (center_x, center_y),
        (end_x, end_y),
        line_width,
    )
    pygame.draw.circle(screen, current_stick_knob_color, (end_x, end_y), knob_radius)

    if abs(vec[0]) > 0.2 or abs(vec[1]) > 0.2:
        pygame.draw.circle(
            screen,
            current_stick_ring_color,
            (end_x, end_y),
            ring_radius,
            max(1, int(2 * scale)),
        )


def draw_hitbox_direction_pad(screen, vec, dirs_offset=(0, 0), layout_offsets=None):
    """Hitbox: botones circulares (arcade). Layout L-U-D | R o posición alternativa L-U-D en fila. Mismo radio que botones de impacto."""
    scale = _get_scale(screen)
    sw, sh = screen.get_width(), screen.get_height()
    centers = compute_direction_centers_screen(
        sw, sh, "hitbox", current_hitbox_alt_layout, dirs_offset
    )
    dpo = {}
    if layout_offsets:
        raw = layout_offsets.get("direction_button_pixel_offsets")
        if isinstance(raw, dict):
            dpo = raw
    radius = max(8, int(BUTTON_RADIUS * scale))
    font_size = max(10, int(18 * scale))

    up = vec[1] < -0.3
    down = vec[1] > 0.3
    left = vec[0] < -0.3
    right = vec[0] > 0.3

    def _off(k):
        p = dpo.get(k, (0, 0))
        return int(p[0]), int(p[1])

    def _draw_circle_key(k, label, pressed):
        cx, cy = centers[k]
        ox, oy = _off(k)
        color = (
            current_button_active_color if pressed else current_button_inactive_color
        )
        center = (cx + ox, cy + oy)
        pygame.draw.circle(screen, color, center, radius)
        font = get_ui_font(font_size, variant="bold")
        text = font.render(label, True, COLOR_TEXT)
        screen.blit(text, text.get_rect(center=center))

    _draw_circle_key("LEFT", "L", left)
    _draw_circle_key("UP", "U", up)
    _draw_circle_key("DOWN", "D", down)
    _draw_circle_key("RIGHT", "R", right)


def draw_mixbox_direction_pad(screen, vec, dirs_offset=(0, 0), layout_offsets=None):
    """Mixbox: teclas rectangulares (estilo teclado). Layout ↑ arriba; ←↓→ en fila. Direccionales a la izquierda."""
    scale = _get_scale(screen)
    sw, sh = screen.get_width(), screen.get_height()
    centers = compute_direction_centers_screen(
        sw, sh, "mixbox", False, dirs_offset
    )
    dpo = {}
    if layout_offsets:
        raw = layout_offsets.get("direction_button_pixel_offsets")
        if isinstance(raw, dict):
            dpo = raw
    w = max(24, int(36 * scale))
    h = max(20, int(28 * scale))
    gap = max(4, int(6 * scale))
    font_size = max(10, int(18 * scale))
    border_radius = max(2, int(6 * scale))

    up = vec[1] < -0.3
    down = vec[1] > 0.3
    left = vec[0] < -0.3
    right = vec[0] > 0.3

    def _off(k):
        p = dpo.get(k, (0, 0))
        return int(p[0]), int(p[1])

    def _draw_rect_key(k, label, pressed):
        cx, cy = centers[k]
        ox, oy = _off(k)
        color = (
            current_button_active_color if pressed else current_button_inactive_color
        )
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (cx + ox, cy + oy)
        pygame.draw.rect(screen, color, rect, border_radius=border_radius)
        font = get_ui_font(font_size, variant="bold")
        text = font.render(label, True, COLOR_TEXT)
        screen.blit(text, text.get_rect(center=rect.center))

    _draw_rect_key("UP", "\u2191", up)
    _draw_rect_key("LEFT", "\u2190", left)
    _draw_rect_key("DOWN", "\u2193", down)
    _draw_rect_key("RIGHT", "\u2192", right)


def draw_buttons(
    screen, button_states, button_count, text_only=False, layout_offsets=None
):
    scale = _get_scale(screen)
    if layout_offsets is None:
        layout_offsets = {}
    bx, by = layout_offsets.get("buttons_offset", (0, 0))
    per = layout_offsets.get("button_pixel_offsets")
    four_a = bool(layout_offsets.get("layout_four_variant_4a"))
    if current_input_layout in ("hitbox", "mixbox"):
        positions = get_button_positions_hitbox_mixbox(
            button_count,
            screen.get_width(),
            screen.get_height(),
            controller_style=current_controller_style,
            layout_four_variant_4a=four_a,
        )
    else:
        positions = get_button_positions(
            button_count,
            screen.get_width(),
            screen.get_height(),
            controller_style=current_controller_style,
            layout_four_variant_4a=four_a,
        )
    labels = get_button_labels(button_count)
    if isinstance(per, list) and len(per) == len(labels):
        positions = [
            (positions[i][0] + per[i][0], positions[i][1] + per[i][1])
            for i in range(len(labels))
        ]
    else:
        positions = [(p[0] + bx, p[1] + by) for p in positions]
    label_font_size = max(10, int(18 * scale))
    label_font = get_ui_font(label_font_size, variant="bold")
    radius = int(BUTTON_RADIUS * scale)
    icon_size = int(BUTTON_RADIUS * 2 * scale)

    for index, pos in enumerate(positions):
        icon = icons[index] if index < len(icons) else None
        pressed = button_states[index]

        if icon and not text_only:
            scaled_icon = pygame.transform.smoothscale(icon, (icon_size, icon_size))
            rect = scaled_icon.get_rect(center=pos)
            screen.blit(scaled_icon, rect)
            if pressed:
                pygame.draw.circle(
                    screen,
                    current_button_active_color,
                    pos,
                    radius,
                    max(1, int(3 * scale)),
                )
            continue

        color = (
            current_button_active_color if pressed else current_button_inactive_color
        )
        pygame.draw.circle(screen, color, pos, radius)
        label = get_hud_fallback_text(
            labels[index], current_controller_style, button_count
        )
        label_surface = label_font.render(label, True, COLOR_TEXT)
        label_rect = label_surface.get_rect(center=pos)
        screen.blit(label_surface, label_rect)


def draw_tournament_mode(screen, state, button_count, layout_offsets=None):
    # Render minimalista para reducir costo de CPU y mantener legibilidad.
    if layout_offsets is None:
        labels = get_button_labels(button_count)
        layout_offsets = {
            "dirs_offset": (0, 0),
            "buttons_offset": (0, 0),
            "button_pixel_offsets": [(0, 0)] * len(labels),
            "layout_four_variant_4a": False,
            "system_offset": (0, 0),
        }
    do = layout_offsets.get("dirs_offset", (0, 0))
    if current_input_layout == "mixbox":
        draw_mixbox_direction_pad(
            screen, state["stick"], dirs_offset=do, layout_offsets=layout_offsets
        )
    elif current_input_layout == "hitbox":
        draw_hitbox_direction_pad(
            screen, state["stick"], dirs_offset=do, layout_offsets=layout_offsets
        )
    else:
        draw_stick(screen, state["stick"], dirs_offset=do)
    draw_buttons(
        screen,
        state["buttons"],
        button_count,
        text_only=True,
        layout_offsets=layout_offsets,
    )
    draw_select_start(
        screen, state, button_count, layout_offsets=layout_offsets, text_only=True
    )
