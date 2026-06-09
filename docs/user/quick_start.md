# Inicio rápido (Windows)

Tras [instalar](installation.md):

```bat
python main.py
```

o con la CLI unificada:

```bat
python cli.py run
python cli.py config
python cli.py tournament
python cli.py doctor
```

- **Configurar perfiles:** desde el menú o `python cli.py config`.
- **Modo torneo:** `python cli.py tournament`.
- **Diagnóstico:** `python cli.py doctor`.

### Modo entrenamiento (HUD activo)

**TAB** / **ENTER** / **BACKSPACE** controlan grabación y reproducción. **Más detalles:** [Modo entrenamiento](training_mode.md).

### Multinstancia (easteregg)

En el menú principal o durante el HUD, **=** abre otra instancia (límite de seguridad: 3 simultáneas).

**Más detalles:** [README raíz](../../README.md), [contrato de datos Windows](../developer/data_contract_windows_v1.md).

## Editor de posición HUD

1. *Configurar perfiles* → **Editar posición HUD**.
2. **TAB**: alterna ancla de direccionales/stick (cyan) y grupo de botones (naranja).
3. Arrastra con el ratón o **flechas** (**Shift** = paso 10 px en coordenadas base).
4. **G** snap; **1** rejilla 4 px; **2** rejilla 8 px.
5. **S** guarda; **Esc** cancela; **R** restablece. Solapamiento fuerte muestra aviso en rojo.

Lógica en [arcade/engine/profiles/hud_layout.py](../../arcade/engine/profiles/hud_layout.py). Coordenadas base de referencia: **375×175** (escalado en ejecución).

## Checklist manual sugerido

1. Instalador o ZIP portable según [instalación](installation.md).
2. Comprobar `cli.py run`, `config`, `tournament`, `doctor`, `--help`.
3. Desde configuración, **Actualizar overlay** (ZIP de release) y revisar `user\update.log` si falla.
4. Verificar HUD estable sin parpadeo (ventana fija Win32).
5. Confirmar que *Configurar perfiles* **no** muestra opciones de ventana flotante ni videoresize.

**Más detalles:** [referencia de layout](../reference/layout_reference.md).
