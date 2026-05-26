# Inicio rápido

Tras [instalar](installation.md) con `venv` activo:

```bash
python3 main.py
```

- **Configurar perfiles:** desde el menú o `python3 configure.py` / `joystick-overlay config`.
- **Modo torneo:** `python3 tournament.py` o `joystick-overlay tournament`.
- **Diagnóstico:** `joystick-overlay doctor`.

### Modo entrenamiento (HUD activo)

**TAB** / **ENTER** / **BACKSPACE** controlan grabación y reproducción. **Más detalles:** [Modo entrenamiento](training_mode.md).

### Multinstancia (easteregg)

En el menú principal o durante el HUD, **=** abre otra instancia (límite de seguridad: 3 simultáneas).

**Más detalles:** [README raíz](../../README.md), [contrato de datos](../developer/data_contract_v1.md).

## Editor de posición HUD

1. *Configurar perfiles* → **Editar posición HUD**.
2. **TAB**: alterna ancla de direccionales/stick (cyan) y grupo de botones (naranja).
3. Arrastra con el ratón o **flechas** (**Shift** = paso 10 px en coordenadas base).
4. **G** snap; **1** rejilla 4 px; **2** rejilla 8 px.
5. **S** guarda; **Esc** cancela; **R** restablece. Solapamiento fuerte muestra aviso en rojo.

Lógica en [arcade/engine/profiles/hud_layout.py](../../arcade/engine/profiles/hud_layout.py); estado en [arcade/engine/core/state_manager.py](../../arcade/engine/core/state_manager.py). Coordenadas base de referencia: **375×175** (escalado en ejecución).

## Checklist manual sugerido

1. `./install.sh` flujo `n` y flujo `s` (global y/o usuario).
2. Comprobar `joystick-overlay`, `config`, `tournament`, `doctor`, `--help`.
3. Abrir desde el menú de aplicaciones las tres entradas si se generaron `.desktop`.
4. Desde configuración, **Actualizar overlay** y revisar `user/update.log` si falla.
5. Verificar HUD sin hooks registrados.

**Más detalles:** [referencia de layout](../reference/layout_reference.md).
