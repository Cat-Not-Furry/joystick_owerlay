# Alcance del producto y límites explícitos

Este documento fija qué **no** forma parte de la filosofía o del alcance inmediato del proyecto, para evitar expectativas erróneas en documentación y menús.

## Fuera de alcance (por ahora)

- **Bandeja del sistema (tray)**: no hay integración con icono ni menú contextual en la bandeja del escritorio.
- **Lanzador u OBS integrado**: el producto no abre ni configura OBS; el uso con captura es responsabilidad del usuario y su flujo de ventanas.
- **pytest-qt / pruebas de UI automatizadas**: las pruebas son principalmente de rutas, datos y lógica; no hay suite Qt/pytest-qt obligatoria.
- **Internacionalización (i18n)**: la interfaz y los mensajes de consola/menú están en un idioma base; traducciones quedan diferidas.

## Qué sí es núcleo

- Overlay HUD configurable, perfiles bajo `user/profiles/`, assets versionados bajo `arcade/assets/`, contrato de datos y migraciones bajo `configs/migrations/` y `core/data_migrations.py`.

Para la relación entre layouts ASCII (referencia UX) y datos canónicos, ver [layout_reference.md](../reference/layout_reference.md).
