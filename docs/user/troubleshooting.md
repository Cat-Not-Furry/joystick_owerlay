# Solución de problemas (Windows)

**Qué cubre esta guía:** incidencias habituales en Windows (ventana fija, captura OBS, rutas de datos, actualización). **Audiencia:** usuarios del HUD y de *Configurar perfiles*. **Prerrequisitos:** [inicio rápido](quick_start.md), [índice de documentación](../README.md).

## Ventana fija (Win32)

En Windows la ventana del HUD y del menú de configuración **no es redimensionable** por el usuario. Esto evita parpadeos y comportamientos inconsistentes con captura OBS. No hay opciones de «ventana flotante» ni «ignorar VIDEORESIZE» en *Configurar perfiles* — la política es fija en Win32.

Si necesitas otro tamaño, ajusta el layout HUD desde *Editar posición HUD*; el tamaño de ventana de la aplicación sigue siendo el definido por el runtime.

## Captura OBS

Use el modo **Captura | OBS** en *Configurar perfiles* si su escena requiere chroma key verde. El HUD mantiene tamaño estable para la fuente de ventana en OBS.

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
