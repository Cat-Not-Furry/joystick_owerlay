# Doctor de entorno (`joystick-overlay doctor`)

Comando de diagnóstico **sin ventana Pygame**: imprime comprobaciones en la terminal. Útil cuando el HUD falla al arrancar o tras una actualización.

## Cómo ejecutarlo

```bat
python cli.py doctor
```

o:

```bat
python doctor.py
```

Implementación: [`doctor.py`](../../doctor.py) (la CLI delega en el mismo módulo vía [`cli.py`](../../cli.py)).

## Qué comprueba

| Comprobación | Significado |
| ------------ | ----------- |
| **Ruta de datos** | Directorio de usuario canónico (`get_user_dir()`) y rutas de respaldo si aplican. |
| **`pygame`** | Importación del módulo; errores suelen indicar `venv` roto o dependencias no instaladas. |
| **Versión runtime** | Alineación con `.joystick_version`. |

No modifica disco ni perfiles; solo lectura e imports.

**Más detalles:** [Inicio rápido](quick_start.md), [solución de problemas](troubleshooting.md), [README raíz](../../README.md).
