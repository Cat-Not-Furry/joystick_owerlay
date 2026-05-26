# Matriz de pruebas — reset de datos (Windows)

Herramienta operativa para **PAR-003**. Contrato: [data_contract_windows_v1.md](data_contract_windows_v1.md).

| Caso | Variante | Input / comando | Esperado | Bloqueante | Resultado | Evidencia |
|------|----------|-----------------|----------|-------------|-----------|-----------|
| Confirmación CLI | W | `joystick-overlay.exe --reset-data` | Pide confirmación antes de tocar disco | Sí | | |
| Worker sin UI | W | `--do-reset-data` | Reset sin HUD interactivo | Sí | | |
| Cancelación | W | `n` ante confirmación | No borra datos | Sí | | |
| Idempotencia | W | dos `--do-reset-data` seguidos | Exit estable; disco coherente | Sí | | |
| Logs | W | post reset | `USER_DIR/reset.log` actualizado | Sí | | |
| Sin TTY | W | pipe / tarea programada | Mensaje claro o `--do-reset-data` documentado | Sí | | |

## Criterio de éxito global

- `USER_DIR` coherente con manifiesto o modo portable tras cada caso bloqueante.
- `profiles_index.json` reconciliable con carpetas.
- Códigos de salida: `0` éxito; distinto de cero en fallo esperado.
