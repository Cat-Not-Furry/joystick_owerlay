# Plan Fase 2 — Agente en `hud_owerlay` (Windows)

Ejecutar **después** de que `hud_overlay` tenga [audit_contract_v1.md](../developer/audit_contract_v1.md) **v1.1** (§ Modelo de paridad por capas), [findings_registry.md](findings_registry.md) y [parity_matrix.md](parity_matrix.md) **`matrix_version: 2`** (Fase 1 + capas completadas).

**Repositorio objetivo:** `hud_owerlay` (Windows). **No** modificar `hud_overlay` en esta fase salvo sincronización acordada.

## Prerrequisitos

- Checkout local de `hud_owerlay` con acceso de lectura al código y `docs/`.
- Misma exclusión habitual de auditoría: sin `venv` obligatorio, sin ejecutar `scripts/` ni `tests/` salvo autorización explícita.
- Referencia Linux: commit `b31d5d7` y artefactos en `hud_overlay/docs/archive/` y `docs/developer/audit_contract_v1.md`.

## Criterio de cierre

Un auditor puede comparar Linux vs Windows usando solo **parity_matrix** + **findings_registry**, respondiendo «¿diverge el **contrato observable**?» (no «¿el código es distinto?»).

---

## Paso 0 — Modelo de capas (leer antes de copiar)

En Linux, el contrato incluye tres capas: **canónica** (debe coincidir), **adaptable** (p. ej. evdev vs keyboard, AppData vs `user/`), **prohibida** (ZIP/reset/versionado incoherente → `drift_permitido: No`).

- Windows = **adaptación contractual upstream**, no clon de código Linux.
- Al copiar docs, conservar § Modelo de paridad por capas y `matrix_version: 2`.

---

## Paso 1 — Contrato normativo

Copiar [audit_contract_v1.md](../developer/audit_contract_v1.md) a `hud_owerlay/docs/developer/audit_contract_v1.md`.

- Mantener el texto idéntico salvo rutas de ejemplo si el árbol difiere.
- En la jerarquía, enlazar `data_contract_windows_v1.md` en capa 5 (invariantes), **no** confundir con este contrato de auditoría.

## Paso 2 — Registro global de hallazgos

Copiar [findings_registry.md](findings_registry.md) y **completar** manifestaciones Windows:

| ID | Acción en Windows |
|----|-------------------|
| SEC-001 | Ruta exacta de `extractall` / ZIP en `install/windows/` (AUD-2-001); `confidence` ≥ 0.90 |
| SEC-002 | Confirmar `N/E` o manifestación si aplica |
| SEC-003 | Verificar lock en `core/data_migrations.py` o equivalente |
| REL-001 | Completar AUD-2-002 (versión runtime) |
| ARCH-002 | Ruta de función ~409 líneas (AUD-1-002) |
| OPS-001 | Estado CI/workflows en Windows |
| OPS-003 | Detalle AUD-6-001 (Git/port) |
| DOC-001 | Detalle AUD-3-001 (`repository_layout`) |

Actualizar encabezado `last_sync_windows` con commit y fecha.

## Paso 3 — Matriz de paridad (`matrix_version: 2`)

Copiar [parity_matrix.md](parity_matrix.md) (v2, con columnas `tipo`, `paridad`, `drift_permitido`, `motivo_plataforma`).

- Rellenar columna **Windows** verificada en código (no solo bitácora).
- Reclasificar cada fila en Windows (ejemplos obligatorios):
  - **Input backend:** `Adapted`, `Funcional`, `drift_permitido: Sí`, `motivo_plataforma: Win32`
  - **SEC-001 / Update ZIP:** `Transitional`, `Pendiente`, `drift_permitido: No`, `motivo_plataforma: installer` si install sigue con `extractall`
  - **Persistencia:** `Adapted`, `Funcional`, `Sí`, `AppData`
- Actualizar `windows_ref` en el encabezado.

## Paso 4 — Bitácora

En `docs/archive/bitacora.md`:

1. **Nota de checkout:** Parte A = inventario verificable local; Parte B = espejo Linux.
2. **§ Propósito:** párrafo «adaptación contractual upstream» (mismo texto que Linux en Propósito y límites).
3. Insertar sección **Gobernanza de auditoría** (misma estructura que Linux), incl. viñeta parity_matrix v2.
4. Tabla **PAR-*** críticos con columnas `tipo` y `drift_permitido` (como Linux).
5. **Parche DRIFT `W-20260426-001`:** evidencia primaria `install/windows/`; dejar de citar solo Inno como fuente única. Si `install/installer.iss` sigue existiendo, marcarlo como legado en nota, no como única evidencia.
6. Tabla «Hallazgos globales referenciados» con SEC activos en Windows.
7. **Historial:** fila de sincronización con commit Windows + «matrix_version 2 / capas v1.1».

Regla: `W-*` = evidencia/cola; hallazgos = `SEC-*` / `REL-*` / etc.

## Paso 5 — Informe de auditoría Windows

En `docs/archive/audit_report.md` (existente 2026-05-18):

1. Banner `schema: audit_contract_v1`.
2. Sección **Índice de migración AUD → SEC** (tabla del plan; no reescribir cuerpo dimensional entero).
3. Top hallazgos y plan con IDs globales y P0–P3.
4. Sustituir veredictos sueltos («Condicionado — no listo») por escalón ladder (`LOCAL_READY`, etc.).
5. Enlazar [findings_registry.md](findings_registry.md) y [parity_matrix.md](parity_matrix.md).

## Paso 6 — Índice de documentación Windows

En `docs/README.md` de `hud_owerlay`, añadir filas equivalentes a Linux:

- Contrato de auditoría v1
- Registry, parity matrix, audit report, este plan (opcional)

## Paso 7 — Vincular AUD en texto

En el cuerpo del informe, donde aparezca **AUD-2-001**, añadir referencia `(→ SEC-001)` sin duplicar el análisis completo.

Igual para AUD-2-002 → REL-001, AUD-1-002 → ARCH-002, AUD-6-001 → OPS-003, AUD-3-001 → DOC-001.

## Paso 8 — Revisar PAR vs SEC

Si **SEC-001** queda `PARCIAL` global:

- Revisar **PAR-005A** (mecánica) vs **PAR-005B** (producto) en tablero bitácora.
- No marcar PAR-005A como OK si install Windows sigue con `extractall` sin mitigación equivalente a `safe_zip_extract`.

## Paso 9 — Historial y verificación

1. Fila en historial de bitácora con fecha y commit Windows.
2. `rg` local: enlaces a `audit_contract`, `findings_registry`, `SEC-00`, `drift_permitido`, `matrix_version: 2`.
3. Coherencia: cada SEC abierto en registry aparece en bitácora (tabla resumen) y en índice migración del audit_report.

## Paso 10 — Capas de paridad (cierre)

1. Verificar que ningún ítem **Adapted** + `drift_permitido: Sí` figure como AUD «Crítica» solo por código distinto (p. ej. keyboard vs evdev).
2. Verificar **SEC-001** en matrix: `Transitional`, `drift_permitido: No`.
3. Completar `parity_layer` / `drift_permitido` en registry para manifestaciones Windows.

---

## Mapeo AUD → SEC (referencia rápida)

| AUD (Windows) | ID global |
|---------------|-----------|
| AUD-2-001 | SEC-001 |
| AUD-2-002 | REL-001 |
| AUD-6-001 | OPS-003 |
| AUD-1-002 | ARCH-002 |
| AUD-3-001 | DOC-001 |

## Fuera de alcance Fase 2

- Cerrar hallazgos en código (mitigar SEC-001, etc.).
- Crear CI ni ejecutar tests masivos.
- Commit/push salvo petición explícita del mantenedor.
