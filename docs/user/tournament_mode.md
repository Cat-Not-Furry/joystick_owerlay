# Modo torneo

Flujo pensado para **mostrar inputs en competición** con menos adornos y un **FPS objetivo más bajo** que el modo normal, para aligerar carga en máquinas modestas o escenas con muchas capturas.

## Cómo arrancarlo

```bash
python3 tournament.py
```

o, con el CLI instalado:

```bash
joystick-overlay tournament
```

Implementación: [`tournament.py`](../../tournament.py) carga perfiles, abre el selector **«Perfil para torneo»**, guarda el perfil activo y llama a `run_hud_session(..., interactive_setup=False, force_tournament=True)` en [`main.py`](../../main.py).

## Diferencias respecto al modo normal (`run`)

| Aspecto | Modo normal | Modo torneo (`force_tournament=True`) |
| ------- | ----------- | ------------------------------------- |
| FPS objetivo | `FPS` (p. ej. 60 en config) | `TOURNAMENT_FPS` (**30** en [`arcade/engine/config/config.py`](../../arcade/engine/config/config.py)) |
| Iconos de botones | Cargados según perfil | **Desactivados** (`enable_icons=False`) para un HUD más simple |
| Modo de render | `normal` | `tournament` (vía `set_render_mode`) |
| Configuración previa | Puede incluir flujos interactivos según entrada | `interactive_setup=False`: va directo al HUD tras elegir perfil |

El título de ventana incluye el sufijo **«— Torneo»** ([`tournament.py`](../../tournament.py)).

## Rendimiento y pruebas

Los tests de FPS consideran ambos modos: objetivo **60** FPS en normal y **30** en torneo; el umbral de aceptación relativo se documenta en [`tests/README.md`](../../tests/README.md) (p. ej. ≥ 75 % del objetivo, mínimo orientativo ~45 FPS en normal).

**Más detalles:** [Inicio rápido](quick_start.md), [alcance del producto](../developer/product_scope.md).
