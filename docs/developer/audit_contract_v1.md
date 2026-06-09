# Contrato de auditoría v1 — Joystick Overlay (cross-repo)

**Qué cubre:** semántica isomórfica para hallazgos, paridad y readiness de release entre `hud_overlay` (Linux) y `hud_owerlay` (Windows). **No** sustituye [data_contract_v1.md](data_contract_v1.md) (Linux), el contrato de datos Windows en `hud_owerlay` (`data_contract_windows_v1.md`) ni [security_model.md](../security/security_model.md).

```
version: 1.1
fecha_congelado: 2026-05-18
parity_layers: 2026-05-18
```

## Jerarquía documental

| Capa | Documento | Rol |
|------|-----------|-----|
| 1 Norma | Este contrato | Severidad, estados, causalidad, plantilla, ladder |
| 2 Estado cross-repo | [parity_matrix.md](../archive/parity_matrix.md), [findings_registry.md](../archive/findings_registry.md) | Sistema × plataforma; IDs globales SEC/REL/ARCH/OPS/DOC |
| 3 Operativo | [bitacora.md](../archive/bitacora.md) | Tablero PAR, colas, historial |
| 4 Instantánea | [audit_report.md](../archive/audit_report.md) | Foto por commit; no sobrescribe registry ni PAR |
| 5 Invariantes | Contratos datos, security_model, README | Rutas, ZIP, procedimientos |

## Alcance de auditoría (metodología)

- Lectura estática / inventario por defecto.
- **Exclusión habitual** salvo autorización explícita: `venv/` de usuario, ejecución de `scripts/`, `tests/`.
- Con autorización B–D, el agente usa los entornos documentados en [agent_runtime_v1.md](agent_runtime_v1.md) (`.venv/`, `tests/.tvenv/`); no sustituyen `venv/` de `install.sh`.
- Hallazgos en registry con `evidence: Estática` cuando no hubo runtime.

### Ejecución autorizada (niveles B–E)

| Nivel | Uso | Entorno |
|-------|-----|---------|
| B | pytest selectivo | `tests/.tvenv` |
| C | scripts métricas / `check_doc_links` | `tests/.tvenv` |
| D | smoke runtime (FPS, menú, `cli.py doctor`) | `.venv` o `tests/.tvenv` |
| E | `install.sh` / instalación real | `venv/` |

En informes con ejecución, incluir `execution_level`, `venv_used`, comando y `exit_code` (ver [agent_runtime_v1.md](agent_runtime_v1.md)).

## Familias de ID

| Prefijo | Uso |
|---------|-----|
| `PAR-NNN` | Paridad de **producto** (bitácora + parity_matrix) |
| `SEC-NNN` | Seguridad / integridad / ZIP / concurrencia (**global**, manifestaciones L/W) |
| `REL-NNN` | Drift versión runtime / metadatos release |
| `ARCH-NNN` | Estructura, monolitos, funciones muy grandes |
| `OPS-NNN` | CI, higiene Git, canal release, tooling |
| `DOC-NNN` | Documentación desalineada del árbol real |

`L-*` y `W-*` en la bitácora = **evidencia local o ítem de cola**, no IDs de hallazgo global.

## Modelo de paridad por capas

### Definición

**Paridad** = equivalencia **funcional y contractual observable**. No implica equivalencia interna de implementación.

Pregunta de auditoría preferida: «¿el **contrato observable** diverge?» — no «¿el código es distinto?».

### Roles entre repos

- **`hud_overlay` (Linux):** upstream de **invariantes** (contrato datos, CLI pública, ZIP, reset, versionado).
- **`hud_owerlay` (Windows):** **adaptación contractual** del mismo producto; no subordinación ni clon línea a línea de código.

### Capa 1 — Canónica (debe coincidir)

| Área |
|------|
| Contrato datos |
| CLI pública |
| Flags |
| Persistencia lógica |
| Flujo usuario |
| Semántica reset |
| Versionado |
| Seguridad ZIP (política; no el mismo binario) |

### Capa 2 — Adaptable (puede variar implementación)

| Área |
|------|
| Backend input |
| AppData vs `user/` |
| Installer |
| APIs OS |
| Event loop interno |
| Hooks sistema |

### Capa 3 — Prohibida (drift no permitido)

| Drift prohibido | Motivo |
|-----------------|--------|
| Contratos datos incompatibles | Rompe migraciones |
| Reset distinto | Riesgo datos |
| Update semánticamente distinto | Riesgo corrupción |
| Versiones runtime incoherentes | Drift release |
| Config incompatible | Ruptura UX |

Violación → `drift_permitido: No`; registrar o enlazar `SEC-*` / `REL-*` / `PAR-*` en [findings_registry.md](../archive/findings_registry.md) y [parity_matrix.md](../archive/parity_matrix.md).

### Campos en parity_matrix (ortogonales al semáforo PAR)

| Campo | Valores |
|-------|---------|
| `tipo` | `Canonical` \| `Adapted` \| `Transitional` |
| `paridad` | `Exacta` \| `Funcional` \| `Pendiente` |
| `drift_permitido` | `Sí` \| `No` |
| `motivo_plataforma` | `evdev` \| `AppData` \| `Win32` \| `installer` \| `—` |

**Reglas:**

- `Adapted` + `drift_permitido: Sí` + `paridad: Funcional` → no elevar severidad solo porque la implementación difiere (p. ej. evdev vs keyboard).
- `Transitional` → diferencia temporal con plan de cierre hacia canónico; típico con SEC-001 y PAR-005A.
- `DRIFT` en estados de cumplimiento (§ abajo) = doc ≠ código; distinto de drift **permitido** por plataforma en capa adaptable.

## Severidad global (P0–P3)

| Nivel | Alias | Criterio operativo |
|-------|-------|-------------------|
| P0 | Crítica | Corrupción de datos, RCE plausible, pipeline ZIP/update inseguro **confirmado** |
| P1 | Alta | Integridad o concurrencia alta; bloquea release amplio |
| P2 | Media | Deuda de mantenibilidad, gaps CI/docs planificables |
| P3 | Baja | Cosmético, higiene, herramientas ausentes **sin** impacto runtime relevante |

**Regla:** la severidad global **no** se infiere del peor impacto por eje. Ejemplo: ausencia de `ruff` → impacto mantenibilidad/release bajo, severidad **P3**, no P0.

## Impacto por eje (independiente de P0–P3)

Por hallazgo en el registry, valorar cada eje: `Alto` | `Medio` | `Bajo` | `—` (no aplica).

| Eje | Pregunta |
|-----|----------|
| Runtime | ¿Afecta ejecución local o datos en caliente? |
| Release | ¿Bloquea distribución OSS / canal PAR-005B? |
| Mantenibilidad | ¿Dificulta cambios seguros sin regresión? |
| Seguridad | ¿Superficie de ataque o integridad comprometida? |

## Estados de cumplimiento

`OK` | `PARCIAL` | `PENDIENTE` | `N/E` | `DRIFT`

- **Prohibido** en informes y tablas: «Parcial», «Condicionado», «no listo» sin mapear a este conjunto o a un escalón del ladder (§ Release readiness).
- `DRIFT`: la evidencia citada en doc ≠ código verificado; cerrar actualizando bitácora o [findings_registry.md](../archive/findings_registry.md).

## Causalidad (por manifestación)

`Confirmado` | `Inferido` | `Hipótesis` | `Cosmético`

## Release readiness (ladder)

Sustituye veredictos sueltos («listo para release», `OSS_READY`, «Condicionado — no listo»).

| Escalón | Criterio mínimo |
|---------|-----------------|
| `LOCAL_READY` | Uso local / clon de confianza; riesgos P0 documentados y aceptados |
| `DOC_ALIGNED` | Docs e índices enlazan contrato + registry + matrix |
| `CI_MIN` | CI mínima verde (ZIP, smoke, enlaces doc) |
| `PARITY_CORE` | PAR críticos OK o PARCIAL con plan; SEC P0 mitigados o aceptados |
| `HARDENED` | Sin P0/P1 abiertos; supply chain y paridad cerradas |

## Plantilla de hallazgo (registry)

Cada entrada en [findings_registry.md](../archive/findings_registry.md) debe incluir:

| Campo | Obligatorio |
|-------|-------------|
| `global_status` | Sí |
| `severity_global` | P0–P3 |
| `causality` | Por manifestación |
| `linked_par` | Si aplica |
| `linux_manifestation` | Ruta + una línea (o `N/E`) |
| `windows_manifestation` | Ruta + una línea (o `PENDIENTE` / `N/E`) |
| `impact_runtime` … `impact_security` | Cuatro ejes |
| `evidence` | `Estática` \| `Runtime` \| `No` |
| `reproducible` | `Sí` \| `No` \| `Desconocido` |
| `confidence` | 0.00–1.00 (obligatorio en hallazgos nuevos; recomendado al migrar) |
| `last_verified` | commit / fecha / repo |
| `parity_layer` | Recomendado: `Canónica` \| `Adaptable` \| `Prohibida` \| `—` |
| `drift_permitido` | Recomendado si aplica capa prohibida: `Sí` \| `No` |

## Estructura isomórfica de informes (8 secciones)

1. Resumen  
2. Restricciones  
3. Hallazgos (IDs del registry; plantilla única)  
4. Riesgo residual  
5. Paridad (enlace a parity_matrix)  
6. Plan de acción (P0–P3)  
7. Confianza  
8. Estado release (escalón del ladder)

La bitácora conserva Parte A/B; puede enlazar este anexo sin reescribir el inventario entero.

## Referencias

- [Runtime del agente v1](agent_runtime_v1.md) — entornos `.venv` / `tests/.tvenv` y niveles B–E
- [Modelo de seguridad](../security/security_model.md) — políticas ZIP/FS (no redefinir aquí)
- [Contrato de datos v1](data_contract_v1.md)
- [Bitácora](../archive/bitacora.md) · [Registry](../archive/findings_registry.md) · [Parity matrix](../archive/parity_matrix.md)
