# Contrato de datos v1 — Joystick Overlay

**Qué cubre esta guía:** rutas canónicas de datos, versionado (`data_version`, assets), reglas duras y exclusiones de legado. **Audiencia:** desarrolladores y operadores. **Prerrequisitos:** [índice de documentación](../README.md), [migrations.md](migrations.md). Para el estándar de directorios bajo el HOME en Linux, véase la **especificación XDG Base Directory** en [Referencias (externas)](#referencias-externas) y [Fuentes externas verificables](../reference/external_sources.md).

```
version: 1
fecha_congelado: 2026-05-03
```

Concepto de contrato; la implementación debe alinearse con [`arcade/engine/config/config.py`](../../arcade/engine/config/config.py).

## 1. Modo de almacenamiento (storage)

| Valor | Significado | Ruta efectiva `USER_DIR` (canon) |
|-------|-------------|-----------------------------------|
| portable | Datos operativos dentro del clon | `PROJECT_ROOT/user/` |
| userdir | Solo documentado para espejo/legajo OS (*no sustituye* el canon portable en Linux actual) | `…/joystick_overlay/user/` bajo datos de aplicación del SO |

**Persistencia opcional del modo**: si en el futuro se persiste, usar `PROJECT_ROOT/.storage_mode` (no bajo `user/`) para no crear bucle «leer modo → ubicar USER_DIR».

## 2. Directorios canónicos (portable)

| Concepto | Ruta (`config`) |
|---------|----------------|
| Canon datos | `USER_DIR` = `PROJECT_ROOT/user` |
| Perfiles | `USER_DIR/profiles/` |
| Índice | `USER_DIR/profiles_index.json` |
| Exportaciones | `USER_DIR/exports/` |
| Backups locales | `USER_DIR/backups/` |
| Versión datos | `USER_DIR/.data_version` |
| Reset log | `USER_DIR/reset.log` |
| Update log | `USER_DIR/update.log` |

**Espejo / backup externo**: `LEGACY_XDG_USER_ROOT` y derivados bajo **`…/joystick_overlay/user/`** en Linux (`~/.local/share/joystick_overlay/user`) — ver código; no forma parte del único lugar de trabajo del desarrollador bajo proyecto. Esa convención de subárbol bajo `~/.local/share` se alinea con el espíritu de la **especificación XDG Base Directory** para datos de usuario (`XDG_DATA_HOME`, por defecto `~/.local/share`); el nombre `joystick_overlay` es específico de este producto.

## 3. Versionado

| Archivo | Rol |
|---------|-----|
| `PROJECT_ROOT/.joystick_version` | Versión de release / artefacto (runtime legible desde CLI `--version`). |
| `arcade/assets/.assets_version` | Versión del paquete de assets. |
| `user/.data_version` | Versión del esquema/contrato de datos en `user/`. |

La cadena declarativa de migraciones (`configs/migrations/`, manifiestos, lock y log) está descrita en **[migrations.md](migrations.md)**. Implementación: [`arcade/engine/core/data_migrations.py`](../../arcade/engine/core/data_migrations.py).

**Reglas recomendadas en producto**

- Discordancia fuerte `data_version` → migraciones controladas ([migrations.md](migrations.md), [`arcade/engine/core/data_migrations.py`](../../arcade/engine/core/data_migrations.py)).
- Discordancia `assets_version` → advertencia/documentación según política de arranque.
- **`hud_overlay` y `.hud_version`**: no cubiertos por este contrato (ver §6).

## 4. Reglas duras

- El **sistema de archivos** (`user/profiles/…`) es fuente de verdad para inventario real de perfiles; el índice JSON debe ser **reconstruible** desde disco.
- El **resolver de iconos**/assets debe evitar **I/O repetido** en caliente (caché en runtime).
- **Escritura atómica** donde el producto garantice rollbacks coherentes para datos críticos.
- **`arcade/assets/`** tratado como **inmutable** respecto al usuario final (salvo flujos de actualización autorizados).

## 5. Compatibilidad futura / abortar

Si en el futuro `data_version` del disco **mayor que** las migraciones conocidas → **abortar** con mensaje claro **sin borrar datos** hasta intervención explícita (reset/manual).

## 6. Legacy / no soportado

- **`~/.local/share/hud_overlay`**, **`%LOCALAPPDATA%\hud_overlay`**, archivo **`.hud_version`**, y nombre de producto HUD en rutas ejecutables antiguos **no** forman parte del contrato runtime v1.
- **No hay recuperación automatizada**: datos que existan sólo en esas rutas no son importados ni migrados por el código conforme a v1.

## 7. JSON antiguo

- `json/profiles.json`: solo rutas históricas de importación; **no** es ubicación runtime en v1.

## Referencias (externas)

1. [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) — define `XDG_DATA_HOME` y el uso de `~/.local/share` para datos de aplicación.
2. [Índice de fuentes del proyecto](../reference/external_sources.md) — tabla consolidada.
