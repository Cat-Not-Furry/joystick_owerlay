# Modo entrenamiento (HUD)

Grabación y reproducción de secuencias de entrada **desde el HUD en ejecución**, para practicar o revisar inputs sin depender de un juego concreto.

## Cómo activarlo

1. Arranca el HUD como siempre: `python3 main.py` o `joystick-overlay` / `joystick-overlay run`.
2. Con el HUD visible y enfocado, usa las teclas siguientes.

No hay subcomando CLI dedicado: el flujo vive en el bucle principal ([`main.py`](../../main.py)) y en [`arcade/engine/training/recorder.py`](../../arcade/engine/training/recorder.py) (el entrypoint en raíz importa el paquete `training` vía `engine_sys_path`).

## Controles

| Tecla | Acción |
| ----- | ------ |
| **TAB** | Inicia grabación si estabas en reposo; si ya grababas, **detiene** la grabación. |
| **ENTER** | Si hay secuencia: si **BACKSPACE** está pulsado, abre la **ventana de entrenamiento** con la secuencia; si no, **inicia reproducción** (o detiene grabación antes si aplica). |
| **BACKSPACE** | Borra la secuencia guardada. |
| **Esc** / pérdida de foco | Cierra la ventana hija de entrenamiento. |

Comportamiento detallado de **ENTER** + secuencia: ver [`_handle_hud_return_key`](../../main.py) y [`_handle_hud_tab_key`](../../main.py).

## Límites (código)

Definidos en [`arcade/engine/training/recorder.py`](../../arcade/engine/training/recorder.py):

- Máximo **30** snapshots en ventana de tiempo.
- Máximo **30 s** de grabación acumulada.
- Intervalo de muestreo **0,1 s** entre snapshots candidatos.
- Hasta **500** eventos en la secuencia.
- Stick: tolerancia **0,01** para considerar dos estados iguales (no duplicar eventos triviales).

## Ventana independiente

Si lanzas la ventana de entrenamiento, se escribe un JSON temporal y se ejecuta el script bajo [`arcade/engine/training/standalone.py`](../../arcade/engine/training/standalone.py) (misma semántica de teclas en esa ventana). El arranque resuelve la raíz del proyecto y usa el mismo render HUD.

**Más detalles:** [Inicio rápido](quick_start.md) (checklist general), [contrato de datos](../developer/data_contract_v1.md).
