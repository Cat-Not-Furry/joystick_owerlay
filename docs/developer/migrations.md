# Migraciones de datos (manifiestos)

El producto versiona el árbol bajo `user/` con **`user/.data_version`** (entero). Las transiciones entre versiones conocidas se declaran en **`configs/migrations/`** y las ejecuta el runtime Python.

## Ficheros

| Ruta | Rol |
|------|-----|
| [`configs/migrations/index.json`](../../configs/migrations/index.json) | Cadena ordenada: `from_data_version` → `to_data_version`, `migration_id`, ruta relativa del manifiesto, `data_version_current_product` esperado por el árbol de manifiestos. |
| [`configs/migrations/manifests/*.json`](../../configs/migrations/manifests/) | Cada manifiesto describe alcance, `safety` (p. ej. backup antes de escribir) y **`implementation.function`**: nombre de función registrada en el motor de migración. |
| `user/migrations_applied.jsonl` | Líneas JSON append-only con resultado de cada migración aplicada (vía `_append_migration_log`). |
| `user/.migration_lock` | Lock de archivo durante una migración (política en `index.json`: `require_lockfile`). |

El código fuente vive en [`arcade/engine/core/data_migrations.py`](../../arcade/engine/core/data_migrations.py). La constante **`CURRENT_DATA_VERSION`** (p. ej. `5`) debe alinearse con el producto final de la cadena y con [`get_data_version` / `write_data_version`](../../arcade/engine/config/config.py) en `user/.data_version`.

## Cuándo se ejecutan

1. **Arranque del HUD** — [`main.py`](../../main.py) `_preflight_startup()`: si `data_version < CURRENT_DATA_VERSION`, llama a `migrate_if_needed()` e imprime el resultado.
2. **Carga de perfiles** — [`load_profiles_data()`](../../arcade/engine/profiles/profile_store.py) en `profile_store.py` invoca `migrate_if_needed()` antes de leer `profiles_index.json`, de modo que configuración y HUD comparten el mismo camino de migración temprana.

Dentro de `migrate_if_needed()` también se resuelve **copia desde XDG legado** al canon `PROJECT_ROOT/user/` si falta el índice en proyecto pero existe espejo bajo datos de usuario; tras eso se encadenan los manifiestos.

## Import ZIP de perfil (sin migración dedicada en esa función)

La importación de un perfil desde un archivo ZIP (`import_profile_from_zip` en [`profile_export.py`](../../arcade/engine/profiles/profile_export.py)) **no** llama a `migrate_if_needed()`. Esa función escribe en `user/profiles/…`, actualiza el dict en memoria y llama a `save_profiles_data()`.

En la práctica:

- Si el proceso ya pasó por **`load_profiles_data()`** (p. ej. abriste *Configurar perfiles* o el HUD tras arranque), las migraciones por manifiesto **ya se aplicaron** en esa carga o en el **preflight** de [`main.py`](../../main.py) (`_preflight_startup` → `migrate_if_needed` cuando `data_version < CURRENT_DATA_VERSION`).
- No asumas que “cada ZIP importado” dispara por sí solo la cadena de manifiestos; depende del orden de arranque y de que el disco ya estuviera en una `data_version` coherente con el código en ejecución.

## Algoritmo de manifiestos (`apply_config_manifest_migrations`)

- Lee el índice; en bucle, busca la entrada cuyo **`from_data_version`** coincide con la versión actual en disco.
- Carga el JSON del manifiesto, obtiene `implementation.function` y la ejecuta si está en el mapa interno **`_MIGRATION_FUNCTIONS`** (p. ej. `migrate_semantic_binding_v3_to_v4`, `migrate_profile_bindings_sidecars_v4_to_v5`).
- Opcionalmente crea backup bajo `user/backups/` si el manifiesto pide `backup_before_write`.
- Escribe la nueva versión con `write_data_version(to_data_version)` y registra en el log JSONL.
- Usa lock para evitar dos procesos aplicando la misma cadena a la vez.

Si falta manifiesto, handler desconocido o lock ocupado, la función devuelve `reason` descriptivo y **no** avanza la versión de forma inconsistente.

## Cadena actual (referencia)

Según el índice en repo (sujeto a cambios en releases):

- **3 → 4** — `2026-05-13_semantic_binding_v4`: asegura `semantic_binding: {}` en cada `profile.json` si faltaba.
- **4 → 5** — `2026-05-12_bindings_sidecars_v5`: vuelca bindings a sidecars y retira mapas inline embebidos donde aplique (ver manifiesto y `migrate_profile_bindings_sidecars_v4_to_v5`).

## Relación con reset y contrato

- El [contrato de datos v1](data_contract_v1.md) fija rutas y semántica de `data_version`.
- La [matriz de reset](reset_matrix.md) documenta borrado controlado; tras reset, una instalación nueva puede volver a subir de versión con la misma cadena de manifiestos si el código lo permite.

**Política futura:** si `data_version` en disco es **mayor** que `CURRENT_DATA_VERSION`, el preflight en `main.py` **aborta** con error explícito (no borra datos).
