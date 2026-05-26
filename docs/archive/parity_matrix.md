# Matriz de paridad técnica — Linux ↔ Windows

Complementa el tablero `PAR-*` de [bitacora.md](bitacora.md). Hallazgos globales: [findings_registry.md](findings_registry.md). Normas: [audit_contract_v1.md](../developer/audit_contract_v1.md) (§ Modelo de paridad por capas).

```
matrix_version: 2
parity_layers: 2026-05-18
linux_ref: b31d5d7 (2026-05-14)
windows_ref: 5dd784e+port (2026-05-22, capas v1.1)
```

## Leyenda de columnas

| Columna | Significado |
|---------|-------------|
| Sistema | Tema técnico o de producto |
| Linux / Windows | Estado en esa plataforma (`OK`, `PARCIAL`, `PENDIENTE`, `DRIFT`, `N/E`) |
| Estado | Lectura cross-repo |
| `tipo` | `Canonical` \| `Adapted` \| `Transitional` ([audit_contract_v1](../developer/audit_contract_v1.md)) |
| `paridad` | `Exacta` \| `Funcional` \| `Pendiente` |
| `drift_permitido` | `Sí` \| `No` — drift de **plataforma** permitido o prohibido |
| `motivo_plataforma` | `evdev` \| `AppData` \| `Win32` \| `installer` \| `—` |
| linked_par / linked_sec | IDs de seguimiento |

## Matriz

| Sistema | Linux | Windows | Estado | tipo | paridad | drift_permitido | motivo_plataforma | linked_par | linked_sec | Notas |
|---------|-------|---------|--------|------|---------|-----------------|-------------------|------------|------------|-------|
| Update ZIP (runtime) | OK (mecánica PAR-005A) | PARCIAL (cli seguro; install `extractall`) | Transicional | Transitional | Pendiente | No | installer | PAR-005A, PAR-005B | SEC-001 | W: `cli.py` + `safe_zip_extract`; `install/windows/install_ops.py` L56–57 |
| Versión runtime | OK | DRIFT | Divergencia contractual | Canonical | Pendiente | No | — | PAR-002 | REL-001 | W: `.joystick_version` 1.0.0 vs `pyproject.toml` 0.3.1 |
| Input backend | evdev | keyboard | Adaptado válido | Adapted | Funcional | Sí | Win32 | — | — | No es deuda; backends distintos |
| Persistencia canon `user/` | OK | OK (código) | Adaptado válido | Adapted | Funcional | Sí | AppData | PAR-001 | — | W: `%LOCALAPPDATA%\joystick_owerlay\user\` + portable |
| Reset dos fases | implementado | implementado (VM pendiente) | PARCIAL | Canonical | Pendiente | No | — | PAR-003 | — | W: `main.py` `--reset-data` / `--do-reset-data`; validación W-OPS-001 |
| Hooks / input history | OK | OK | Igual | Canonical | Exacta | No | — | PAR-004 | — | |
| CLI soporte | OK | OK (flags); ops PARCIAL | PARCIAL | Canonical | Funcional | No | — | PAR-002 | — | Área tablero «CLI» = VM/doc; flags canónicos OK |
| Instalación / accesos | install.sh | install/windows | PARCIAL | Adapted | Funcional | Sí | installer | PAR-006 | SEC-001 | Evidencia W: `install/windows/`; Inno legado en `install/` |
| Preflight UX | PARCIAL | PARCIAL | PARCIAL | Canonical | Pendiente | No | — | PAR-007 | — | |
| CI / QA automatizado | ausente | ausente | PARCIAL | Canonical | Pendiente | No | — | — | OPS-001 | |
| ZIP perfil (import) | OK | OK | Igual | Canonical | Exacta | No | — | — | — | W: `profile_export.py` → `extract_zip_safely` |
| Monolitos / deuda LOC | PARCIAL | PARCIAL | PARCIAL | Canonical | Pendiente | Sí | — | — | ARCH-001, ARCH-002 | W: `hud_layout_editor` ~409 LOC |
| Canal release usuario | PARCIAL | PARCIAL | PARCIAL | Canonical | Pendiente | No | — | PAR-005B | OPS-002 | |
| Tooling / higiene Git | PARCIAL | PARCIAL | PARCIAL | Canonical | Funcional | Sí | — | — | OPS-003 | Port sin commit vs HEAD |
| Docs layout vs árbol | OK | PARCIAL | PARCIAL | Canonical | Pendiente | No | — | — | DOC-001 | `repository_layout.md` vs árbol real |

## Capa prohibida activa (violaciones `drift_permitido: No`)

- **SEC-001** — Pipeline ZIP/update semánticamente incoherente (L: `unzip` en update; W: `install_ops.extractall` + cli seguro).
- **SEC-002** — Concurrencia `input_state` sin lock (Linux; manifestación Windows N/E).
- **SEC-003** — Lock de migración no atómico (canónica datos).
- **REL-001** — Drift versión runtime / metadatos release.

## Tablero PAR (resumen; detalle en bitácora)

| PAR | Linux | Windows (bitácora) | Impacto |
|-----|-------|-------------------|---------|
| PAR-001 | PARCIAL | PARCIAL | CRÍTICO |
| PAR-002 | OK | OK | MEDIO |
| PAR-003 | PARCIAL | PARCIAL | CRÍTICO |
| PAR-004 | OK | OK | CRÍTICO |
| PAR-005A | OK | PARCIAL | CRÍTICO |
| PAR-005B | PARCIAL | PARCIAL | CRÍTICO |
| PAR-006 | PARCIAL | PARCIAL | MEDIO |
| PAR-007 | PARCIAL | PARCIAL | BAJO |

## Sincronización

- **Fase A (Linux):** `matrix_version: 2` + reclasificación por capas.
- **Fase B (`hud_owerlay`):** [windows_parity_rollout.md](windows_parity_rollout.md) — columna Windows verificada 2026-05-22.
