# Referencia de layout HUD (UX frente a datos)

Los diagramas ASCII de modos MVS, CPS, Xbox, PS o Switch son **material de referencia de producto**: muestran *cómo debería verse* el overlay en pantalla.

**No son la fuente de verdad de la lógica.** El motor debe basarse en:

- JSON de layout por perfil (`hud_layout` en `profile.json` o equivalente),
- tablas **slot físico** (`BTN_1` … `BTN_8`, `START`, `SELECT`) alineadas con `get_button_labels`,
- `semantic_binding` opcional (opción B) y resolución de iconos por pack.

Cualquier dibujo en documentación o issues sirve para alinear expectativas visuales; los cambios de comportamiento se versionan con `data_version`, manifiestos en `configs/migrations/` y tests cuando correspondan.
