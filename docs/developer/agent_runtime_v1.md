# Runtime del agente v1 — Joystick Overlay (Windows)

**Qué cubre:** qué entorno virtual usar cuando el agente ejecuta tests, scripts o smoke runtime en `hud_owerlay`. Complementa [audit_contract_v1.md](audit_contract_v1.md) § Alcance; **no** sustituye la instalación de usuario (`install/windows/`, build PyInstaller).

```
version: 1
fecha: 2026-05-26
repo: hud_owerlay
release: 0.3.2
```

## Política de entornos permitidos

| Ruta | Rol | Uso por el agente |
|------|-----|-------------------|
| `tests/.tvenv/` | Tests, pytest, scripts de check | **Permitido** (niveles B/C). **Única** ruta canónica bajo `tests/`. |
| `.venv/` | Runtime editable del desarrollador | Fuera del contrato del agente; válido para smoke humano (nivel D) |
| `venv/` | Desarrollo local / instalador empaquetado | Solo con autorización explícita **nivel E** |

**Regla:** el agente y CI usan **exclusivamente** `tests/.tvenv`. No crear `tests/tvenv` ni variantes. La validación WM en máquina Windows del mantenedor puede usar `.venv`, entorno global o build instalado; no se documenta como ruta canónica del agente.

Los directorios `.venv/` y `tests/.tvenv/` deben estar en `.gitignore`. El agente **no** debe reinstalar dependencias salvo que la tarea lo autorice.

## Matriz: autorización → entorno → comando

| Nivel | Nombre | ¿Ejecutar? | Entorno | Ejemplos |
|-------|--------|------------|---------|----------|
| A | Estática | No (por defecto) | — | `rg`, lectura de código, `git status` |
| B | Pytest selectivo | Sí | `tests/.tvenv` | `pytest tests/test_zip_security.py` |
| C | Scripts controlados | Sí | `tests/.tvenv` | `scripts/check_doc_links.py`, `scripts/check_version_alignment.py` |
| D | Smoke runtime | Sí | `tests/.tvenv` o `.venv` humano | `python cli.py doctor`, `python main.py` (humano WM) |
| E | Instalación real | Sí | instalador / VM Windows | `joystick-overlay-setup.exe`, validación AppData |

## Plantillas de comando (canónicas)

Desde la raíz del repositorio:

```bat
REM Crear entorno (una vez)
python -m venv tests\.tvenv
tests\.tvenv\Scripts\pip install -r requirements.txt
tests\.tvenv\Scripts\pip install pytest

REM Nivel B — pytest
set SDL_VIDEODRIVER=dummy
tests\.tvenv\Scripts\python -m pytest tests/ -q

REM Nivel C — checks
tests\.tvenv\Scripts\python scripts\check_doc_links.py
tests\.tvenv\Scripts\python scripts\check_version_alignment.py

REM Nivel D — smoke (humano o agente con display)
tests\.tvenv\Scripts\python cli.py doctor
tests\.tvenv\Scripts\python cli.py --version
```

En Linux (desarrollo cross-repo del agente), equivalente:

```bash
SDL_VIDEODRIVER=dummy tests/.tvenv/bin/python3 -m pytest tests/ -q
tests/.tvenv/bin/python3 scripts/check_doc_links.py
tests/.tvenv/bin/python3 scripts/check_version_alignment.py
```

## CI (GitHub Actions)

| Paso | Comportamiento |
|------|----------------|
| Pytest | **Fail** el job |
| `check_doc_links.py` | **Fail** |
| `check_version_alignment.py` | **Fail** |

Entorno CI: `tests/.tvenv` exclusivamente.

## Reglas obligatorias para el agente

1. **Nunca** usar `python3` del sistema si existe `tests/.tvenv` al nivel autorizado.
2. **Nunca** `pip install` sin autorización explícita.
3. **No** modificar instalador ni AppData del usuario salvo tarea explícita nivel E.
4. En informes, documentar: `execution_level`, `venv_used`, comando, `exit_code`.
5. Tests sin display: `SDL_VIDEODRIVER=dummy`.

## Actualización Windows (nivel E / producto)

En Windows **no** existe `scripts/update.sh`. Canal correcto:

- `cli.py --update --zip <ruta>` o `joystick-overlay.exe --update --zip`
- Menú Configurar → Actualizar overlay (debe invocar el mismo mecanismo)

## Referencias

- [audit_contract_v1.md](audit_contract_v1.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [data_contract_windows_v1.md](data_contract_windows_v1.md)
- [installation.md](../user/installation.md)
