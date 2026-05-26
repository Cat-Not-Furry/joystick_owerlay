# Modos de captura y OBS

En **Configurar perfiles**, **Modo de captura** del perfil activo controla el fondo del HUD:

| Modo | Uso típico |
| ---- | ---------- |
| `normal` | Fondo oscuro; adecuado si compones encima o capturas la ventana tal cual. |
| `obs_green` | Fondo verde sólido **RGB (0, 255, 0)** pensado para **chroma key** en OBS u otro software que filtre por color. |

El valor se guarda con el perfil y se aplica al arrancar el HUD.

## Integración en OBS

Pasos detallados (fuente ventana, chroma, capas): **[Checklist OBS](obs_setup.md)**.

## Otros sistemas de grabación

La idea es la misma que en OBS: **capturar la ventana del overlay** y, si necesitas aislar el HUD del fondo, usar **croma** u otra técnica de composición que tu software soporte (nombre del filtro y menús varían). No damos por probada cada suite; prueba con una fuente de ventana y revisa la documentación de tu grabador para chroma key o mezcla alfa.

**Más detalles:** [obs_setup.md](obs_setup.md), [referencia de layout](../reference/layout_reference.md), [README raíz](../../README.md).
