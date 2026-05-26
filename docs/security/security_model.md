# Modelo de confianza y seguridad (Joystick Owerlay, Windows)

**Audiencia:** usuarios avanzados y colaboradores. **Prerrequisitos:** [README](../../README.md), [índice](../README.md).

## Raíces de datos

| Área | Ruta típica | Mutable |
|------|-------------|--------|
| Datos (instalado) | `%LOCALAPPDATA%\joystick_owerlay\user\` | Sí |
| Datos (portable) | `<install_root>\user\` | Sí |
| Perfiles | `user/profiles/<id>/` | Sí |
| Assets | `arcade/assets/` | Actualización vía ZIP autorizado |

ZIP de **perfil** y de **actualización** (menú Config / `joystick-overlay --update --zip`) = **no confiables**.

## Políticas implementadas

### Importación de perfil

- [`arcade/engine/utils/safe_zip_extract.py`](../../arcade/engine/utils/safe_zip_extract.py): sin `extractall` ciego; límites de miembros y tamaño.
- Iconos bajo `user/profiles/<id>/icons/` con extensiones permitidas.
- Bindings solo con nombres canónicos en sidecars.

### Resolución de rutas

- [`safe_paths.py`](../../arcade/engine/utils/safe_paths.py): contención bajo perfil, `user/` o `arcade/assets/`.
- Icon packs solo bajo `arcade/assets/icon_packs/`.

### Actualización por ZIP

- Python (`cli.py` / menú Config): whitelist de carpetas; **no** sobrescribe `user/`.
- Log en `USER_DIR/update.log`.
- Lock de índice al guardar perfiles (Windows: `msvcrt` / archivo lock).

### Instalador

- Payload firmado por canal de release del mantenedor (sin firma Authenticode en alcance inicial).
- `install_manifest.json` junto al ejecutable para desinstalación coherente si se mueve la carpeta portable.

## Verificación local

```bat
set PYTHONPATH=arcade\engine
python tests\test_zip_security.py
python tests\test_config_paths.py
```

## Qué no está en alcance

- Firma Authenticode obligatoria en builds locales.
- Confianza ciega en ZIP de terceros (supply chain).
