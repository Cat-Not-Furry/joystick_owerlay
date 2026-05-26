# Solución de problemas

**Qué cubre esta guía:** incidencias habituales en Linux (WM tiling, redimensionado de ventana, permisos de entrada, rutas de datos). **Audiencia:** usuarios del HUD y de *Configurar perfiles*. **Prerrequisitos:** [inicio rápido](quick_start.md), [índice de documentación](../README.md). Referencias técnicas del stack: [Fuentes externas verificables](../reference/external_sources.md).

Las secciones siguientes describen **comportamiento observado** con Pygame y WMs comunes; no sustituyen el manual de tu distribución.

## Window managers (tiling)

En i3, bspwm, sway, Hyprland, etc., el WM puede forzar tamaños o ignorar el tamaño inicial de Pygame. Marca la ventana como **flotante** si necesitas tamaño y posición estables.

## Anti-parpadeo (VIDEORESIZE)

Si la ventana parpadea o el WM no deja flotar bien, activa **«Ignorar VIDEORESIZE (anti-parpadeo)»** en *Configurar perfiles*. Prueba rápida sin menú:

```bash
JOYSTICK_IGNORE_VIDEORESIZE=1 python3 main.py
```

El subsistema de **ventana y vídeo** de SDL (usado por Pygame) documenta APIs de ventana y eventos en la wiki de SDL2; sirve como contexto cuando un WM genera redimensionados agresivos.

## Teclado global (`evdev`)

En *Configurar perfiles* puedes elegir **Teclado global**: se lee un teclado con `evdev` aunque la ventana no tenga foco. Si el dispositivo falla, hay fallback al modo con foco (`pygame`). Con **ninguno (solo con foco)** solo se usa Pygame.

Si hay error de permisos al leer dispositivos, lo habitual en Linux es pertenecer al grupo `input` (el comando `joystick-overlay doctor` lo indica). El siguiente comando amplía permisos de **todo** `event*` y puede degradar seguridad; úsalo solo como medida temporal consciente:

```bash
sudo chmod a+r /dev/input/event*
```

## Rutas de datos y legado

Tras migraciones, pueden existir `user/legacy_bindings.json` y `user/legacy_joystick_bindings.json`. Iconos por defecto: `arcade/assets/icon_packs/`; sustituciones por perfil en `user/profiles/<id>/icons/`. Resolución: `arcade/engine/core/assets_resolver.py`.

**Más detalles:** [contrato de datos](../developer/data_contract_v1.md), [README raíz](../../README.md).

## Referencias (externas)

1. [Linux kernel: Input documentation](https://www.kernel.org/doc/html/latest/input/input.html) — subsistema de entrada y dispositivos `evdev`.
2. [python-evdev: documentación](https://python-evdev.readthedocs.io/en/stable/) — API Python sobre el interfaz de eventos de Linux.
3. [SDL2: CategoryVideo](https://wiki.libsdl.org/SDL2/CategoryVideo) — subsistema de vídeo/ventana de SDL2 (base de Pygame).
4. [Pygame: documentación](https://www.pygame.org/docs/) — capa de alto nivel usada por el HUD.
5. [Índice de fuentes del proyecto](../reference/external_sources.md) — tabla consolidada.
