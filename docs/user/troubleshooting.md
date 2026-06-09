# Solución de problemas (Windows)

**Qué cubre esta guía:** incidencias habituales en Windows (ventana, captura OBS, rutas de datos, actualización). **Audiencia:** usuarios del HUD y de *Configurar perfiles*. **Prerrequisitos:** [inicio rápido](quick_start.md), [índice de documentación](../README.md).

## Ventana (Win32)

La ventana del HUD y del menú se puede **maximizar, minimizar y redimensionar** con el marco estándar de Windows. No hay opciones de «ventana flotante» ni «ignorar VIDEORESIZE» en *Configurar perfiles* — el comportamiento es fijo en el producto.

Si al redimensionar notas parpadeo breve (p. ej. con captura OBS), es normal: el runtime limita la frecuencia de ajuste de tamaño para estabilizar la imagen.

## Captura OBS

Use el modo **Captura | OBS** en *Configurar perfiles* si su escena requiere chroma key verde. Prefiera tamaño de ventana estable durante la transmisión; evite redimensionar en vivo si la fuente parpadea.

## Rutas de datos y legado

- **Instalado:** `%LOCALAPPDATA%\joystick_owerlay\user\`
- **Portable:** carpeta `user\` junto al ejecutable

Tras migraciones pueden existir `user/legacy_bindings.json` y `user/legacy_joystick_bindings.json`. Iconos por defecto: `arcade/assets/icon_packs/`; sustituciones por perfil en `user/profiles/<id>/icons/`.

**Más detalles:** [contrato de datos Windows](../developer/data_contract_windows_v1.md), [README raíz](../../README.md).

## Actualización fallida

Revise `user\update.log`. Desde *Configurar perfiles → Actualizar overlay* seleccione el ZIP de release, o en terminal:

```bat
python cli.py --update --zip ruta\release.zip
```

No se sobrescribe `user/`.

## Diagnóstico

```bat
python cli.py doctor
```

**Más detalles:** [doctor](doctor.md).

## Referencias (externas)

1. [SDL2: CategoryVideo](https://wiki.libsdl.org/SDL2/CategoryVideo) — subsistema de vídeo/ventana de SDL2 (base de Pygame).
2. [Pygame: documentación](https://www.pygame.org/docs/) — capa de alto nivel usada por el HUD.
3. [Índice de fuentes del proyecto](../reference/external_sources.md) — tabla consolidada.
