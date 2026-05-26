# Doctor de entorno (`joystick-overlay doctor`)

Comando de diagnóstico **sin ventana Pygame**: imprime comprobaciones en la terminal. Útil antes de instalar menús o cuando el HUD falla al arrancar.

## Cómo ejecutarlo

```bash
joystick-overlay doctor
```

o, desde el clon con `venv` activo:

```bash
python3 doctor.py
```

Implementación: [`doctor.py`](../../doctor.py) (la CLI delega en el mismo módulo vía [`cli.py`](../../cli.py)).

## Qué comprueba

| Comprobación | Significado |
| ------------ | ----------- |
| **Ruta de datos** | Muestra el directorio de usuario canónico (`get_user_dir()`) y la ruta de espejo opcional (`BACKUP_PROFILES_ROOT`). |
| **Sesión gráfica** | Variables `WAYLAND_DISPLAY`, `DISPLAY`, `XDG_SESSION_TYPE`, `XDG_CURRENT_DESKTOP`. Si no hay Wayland ni X11, avisa que el HUD necesita sesión gráfica. |
| **`/dev/input`** | Existe el directorio; cuenta dispositivos `event*`. |
| **Grupo `input`** | Si tu usuario no está en el grupo `input`, puede faltar acceso a evdev; el doctor sugiere `sudo usermod -aG input $USER` (requiere cerrar sesión o relogin). |
| **`pygame` / `evdev`** | Importación de módulos; errores aquí suelen indicar `venv` roto o dependencias no instaladas. |

No modifica disco ni perfiles; solo lectura e imports.

**Más detalles:** [Inicio rápido](quick_start.md), [solución de problemas](troubleshooting.md), [README raíz](../../README.md).
