# Contrato de datos v1 — Joystick Owerlay (Windows)

```
version: 1
fecha_congelado: 2026-05-18
plataforma: Windows
```

Implementación: [`arcade/engine/config/config.py`](../../arcade/engine/config/config.py). Paridad conceptual con Linux: [`data_contract_v1.md`](data_contract_v1.md) (repo `hud_overlay`).

## 1. Modos de instalación

| Modo | Binarios | `USER_DIR` (datos operativos) |
|------|----------|-------------------------------|
| **installed** | `C:\Program Files\Joystick Owerlay\` (típico) | `%LOCALAPPDATA%\joystick_owerlay\user\` |
| **portable** | Carpeta elegida por el usuario | `<install_root>\user\` |

La política se fija en **`install_manifest.json`** junto a `joystick-overlay.exe` (ver [`install/templates/install_manifest.schema.json`](../../install/templates/install_manifest.schema.json)).

Desarrollo sin manifiesto: `PROJECT_ROOT/user/` (portable de facto).

Variable opcional de desarrollo: `JOYSTICK_STORAGE_MODE=portable|userdir` (no se pregunta en consola en flujo normal).

## 2. Directorios canónicos

| Concepto | Ruta |
|---------|------|
| Perfiles | `USER_DIR/profiles/` |
| Índice | `USER_DIR/profiles_index.json` |
| Exportaciones | `USER_DIR/exports/` |
| Backups locales | `USER_DIR/backups/` |
| Versión datos | `USER_DIR/.data_version` |
| Reset log | `USER_DIR/reset.log` |
| Update log | `USER_DIR/update.log` |
| Assets (inmutables en runtime) | `arcade/assets/` |

**Espejo opcional** (flag JSON `xdg_mirror_enabled`, nombre por paridad Linux): copia bajo `%LOCALAPPDATA%\joystick_owerlay\user\` cuando el usuario lo activa.

## 3. Versionado

| Archivo | Rol |
|---------|-----|
| `PROJECT_ROOT/.joystick_version` | Versión runtime (`joystick-overlay --version`) |
| `arcade/assets/.assets_version` | Versión del paquete de assets |
| `user/.data_version` | Esquema de datos (`CURRENT_DATA_VERSION` en migraciones) |

Cadena declarativa: [`configs/migrations/`](../../configs/migrations/), [`migrations.md`](migrations.md).

## 4. Reglas duras

- El **FS** (`user/profiles/<id>/`) es fuente de verdad; el índice es reconciliable.
- Resolver de iconos con **caché**; invalidación al guardar perfil.
- Escritura **atómica** en datos críticos; **lock** al guardar índice en Windows.
- ZIP de perfil y de actualización: **entrada no confiable** ([`security_model.md`](../security/security_model.md)).

## 5. Legacy / no soportado

- **`%APPDATA%\hud_owerlay`**, **`%LOCALAPPDATA%\hud_overlay`**, **`.hud_version`**: no son contrato v1.
- **Migración en instalación**: solo si el wizard **detecta** datos en rutas `hud_owerlay` y el usuario confirma.
- Sin rescate automático desde `hud_overlay` al arranque.

## 6. Política Win32 (ventana y WM)

Capa **Adapted** frente a Linux (`motivo_plataforma: Win32`, `drift_permitido: Sí`).

| Campo / comportamiento | Linux | Windows |
|------------------------|-------|---------|
| `window_mode` (`floating_hint` / `normal`) | Configurable en menú | **No expuesto en UI**; normalizar a `normal` al cargar |
| `ignore_videoresize` | Toggle en menú | **No expuesto en UI**; normalizar a `false` al cargar; runtime procesa `VIDEORESIZE` con cooldown |
| Ventana redimensionable (`pygame.RESIZABLE`) | Sí (WM tiling) | **Sí** — marco Win32 (maximizar/minimizar/redimensionar); sin toggles en menú |

Los campos pueden persistir en `profiles_index.json` por compatibilidad de import desde Linux; el runtime Windows los sobrescribe al cargar. No validar `floating_hint` como opción activa en W.

## 7. JSON antiguo

- `json/profiles.json`: solo importación histórica; no es runtime v1.
