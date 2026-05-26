# Checklist OBS (Joystick Overlay)

**Qué cubre esta guía:** pasos para capturar la ventana del overlay en **OBS Studio** y aplicar croma con el modo `obs_green`. **Audiencia:** streamers. **Prerrequisitos:** [modos de captura](capture_modes.md), [índice de documentación](../README.md). La documentación **oficial** de OBS enlazada al final sustituye a tutoriales de terceros.

Pasos concretos para componer el HUD en **OBS Studio** con ventana y chroma. Los modos `normal` / `obs_green` se describen en [Modos de captura y OBS](capture_modes.md).

## Antes de capturar

1. En **Configurar perfiles**, elige **Modo de captura** del perfil activo (`normal` u `obs_green`).
2. Arranca el HUD con ese perfil para que el fondo sea el esperado.

## Fuente de ventana

1. Añade una fuente **Captura de ventana** (o equivalente en tu idioma).
2. Selecciona la ventana de **Joystick Overlay** (el título puede incluir «Torneo» si usas modo torneo).

En Linux, OBS suele usar **Window Capture (Xcomposite)** o **PipeWire** según entorno; la guía oficial de OBS describe propiedades y notas por plataforma.

## Croma con `obs_green`

1. Con el modo `obs_green` (fondo **RGB 0, 255, 0**), añade a esa fuente un filtro **Chroma Key** / **Clave de croma**.
2. Color clave: **verde puro (0, 255, 0)**.
3. Ajusta **similaridad** y reducción de **spill** según iluminación y si hay reflejos verdes en stick o texto.

La guía oficial de **filtros** de OBS enumera tipos de filtros (incluidos los de efecto para croma / color).

## Orden de capas

- Coloca el HUD **encima** del juego o escena que quieras mostrar, o debajo según el efecto deseado; el chroma deja transparente el verde solo en esa fuente.
- Si usas `normal` sin croma, el fondo del overlay no es clave uniforme: compón con máscaras o recorte si necesitas aislar elementos.

## Si algo falla

- Comprueba que capturas la **ventana correcta** (no el escritorio entero salvo que quieras).
- Ver [Solución de problemas](../user/troubleshooting.md) (VIDEORESIZE, tiling).

**Más detalles:** [Modos de captura](capture_modes.md), [referencia de layout](../reference/layout_reference.md).

## Referencias (externas)

1. [OBS KB: Window Capture Sources](https://obsproject.com/kb/window-capture-sources) — captura de ventana (incl. Linux Xcomposite / PipeWire).
2. [OBS KB: Filters Guide](https://obsproject.com/kb/filters-guide) — tipos de filtros (efecto / audio-vídeo).
3. [OBS KB: Sources Guide](https://obsproject.com/kb/sources-guide) — visión general de fuentes y escenas.
4. [Índice de fuentes del proyecto](../reference/external_sources.md) — tabla consolidada.
