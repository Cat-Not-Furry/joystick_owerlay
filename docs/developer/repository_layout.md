# Estructura del repositorio (Windows — `hud_owerlay`)

Joystick Owerlay se distribuye como paquete Python con **entrypoints en la raíz** del clon y el **código importable** bajo `arcade/engine/`.

## Raíz del clon

| Fichero / directorio | Rol |
| -------------------- | --- |
| [`main.py`](../../main.py) | Menú principal, HUD, bucle Pygame. |
| [`cli.py`](../../cli.py) | Comando `joystick-overlay` (`run`, `config`, `tournament`, `doctor`, `--update --zip`, …). |
| [`configure.py`](../../configure.py), [`tournament.py`](../../tournament.py), [`doctor.py`](../../doctor.py) | Puntos de entrada usados por la CLI. |
| [`engine_sys_path.py`](../../engine_sys_path.py) | Inserta `arcade/engine` al inicio de `sys.path`. |
| [`pyproject.toml`](../../pyproject.toml) | Metadatos del proyecto, dependencias de runtime, script console `joystick-overlay`. |
| [`requirements.txt`](../../requirements.txt) | Instalación mínima + build (p. ej. PyInstaller). |
| [`configs/`](../../configs/) | Valores por defecto, esquemas JSON, **migraciones** declarativas. |
| [`docs/`](../../docs/) | Documentación versionada (contrato datos, auditoría, bitácora). |
| [`install/`](../../install/) | Iconos, plantillas, legado `.iss`/`.bat`; **canon instalador:** [`install/windows/`](../../install/windows/). |
| [`tests/`](../../tests/) | Pruebas (no ejecutar como sustituto del producto). |
| [`user/`](../../user/) | Datos de usuario en desarrollo (canon portable; no versionar contenido personal). |
| [`.joystick_version`](../../.joystick_version) | Versión runtime (`joystick-overlay --version`). |
| [`scripts/`](../../scripts/) | Utilidades CI: `check_version_alignment.py`, `check_doc_links.py`. |

## Paquete bajo `arcade/engine/`

Setuptools declara paquetes con origen en [`arcade/engine`](../../arcade/engine). Ahí viven `config`, `profiles`, `render`, `maps`, `core`, `training`, `utils`.

Dentro de `render/`, el menú de configuración de perfiles vive en el paquete [`render/profile_config/`](../../arcade/engine/render/profile_config/) (handlers por sección, modales, constantes). El módulo [`render/profile_config_menu.py`](../../arcade/engine/render/profile_config_menu.py) es un shim fino que reexporta la API pública.

## Assets

Iconos, plantillas de bindings y presets: [`arcade/assets/`](../../arcade/assets) (versionado en [`arcade/assets/.assets_version`](../../arcade/assets/.assets_version)).

## Resumen

- **No duplicar** lógica entre raíz y `arcade/engine/`.
- Gobernanza y paridad: [bitácora](../archive/bitacora.md), [findings_registry](../archive/findings_registry.md).

**Más detalles:** [contrato datos Windows](data_contract_windows_v1.md), [contrato Linux (referencia)](data_contract_v1.md), [modelo de seguridad](../security/security_model.md).
