# Exportar e importar perfil (ZIP)

**Qué cubre esta guía:** flujo de usuario para empaquetar y restaurar perfiles en `.zip`, riesgos de seguridad y enlaces al código. **Audiencia:** usuarios que comparten perfiles o hacen copias de seguridad. **Prerrequisitos:** [instalación](installation.md), [índice de documentación](../README.md). Referencias del sector: [Fuentes externas verificables](../reference/external_sources.md).

Los perfiles se pueden **empaquetar en ZIP** para copiar de máquina en máquina o hacer copia de seguridad. El flujo habitual es desde **Configurar perfiles** en la aplicación.

## Desde la interfaz

1. Abre *Configurar perfiles* (`joystick-overlay config` o `python3 configure.py`).
2. **Exportar:** usa la acción de exportar del menú; se genera un `.zip` con `profile.json`, carpeta `bindings/` con los JSON de teclas/hitbox/mixbox/joystick según corresponda, e iconos personalizados si los hay.
3. **Importar:** elige el `.zip`; si hay conflicto de nombre, el comportamiento por defecto es **renombrar** el importado (también puede sobrescribir o cancelar según el diálogo).

Lógica principal: [`export_profile_to_zip` / `import_profile_from_zip`](../../arcade/engine/profiles/profile_export.py); selección de fichero: [`profile_config_menu.py`](../../arcade/engine/render/profile_config_menu.py).

## Seguridad

Trata cualquier ZIP de perfil como **contenido no confiable**: solo importa desde fuentes que confíes. El código usa extracción acotada (no `extractall` ingenuo) y validaciones de rutas; el modelo de amenazas y límites están en **[Modelo de confianza](../security/security_model.md)**.

## Datos en disco

Tras importar, los ficheros viven bajo `user/profiles/<id>/` según el [contrato de datos](../developer/data_contract_v1.md).

**Más detalles:** [Migraciones y ZIP](../developer/migrations.md) (cuándo corre `migrate_if_needed` vs import), [instalación](installation.md).

## Referencias (externas)

1. [OWASP: Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal) — contexto de rutas maliciosas en ficheros y archivos.
2. [Snyk: Zip Slip vulnerability](https://security.snyk.io/research/zip-slip-vulnerability) — patrón Zip slip en archivos comprimidos.
3. [Modelo de confianza del proyecto](../security/security_model.md) — políticas concretas implementadas en este código.
4. [Índice de fuentes del proyecto](../reference/external_sources.md) — tabla consolidada.
