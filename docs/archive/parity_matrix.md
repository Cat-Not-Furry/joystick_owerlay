# Matriz de paridad técnica — Linux ↔ Windows

Complementa el tablero `PAR-*` de [bitacora.md](bitacora.md). Hallazgos globales: [findings_registry.md](findings_registry.md). Normas: [audit_contract_v1.md](../developer/audit_contract_v1.md) (§ Modelo de paridad por capas).

```
matrix_version: 2
parity_layers: 2026-05-18
linux_ref: a19edb8 (0.3.2, 2026-05-26)
windows_ref: 0.3.2 (2026-05-26, gate P0/P1/P2)
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
| Update ZIP (runtime) | OK (mecánica PAR-005A) | OK (cli + install `safe_zip_extract`) | PARCIAL | Canonical | Funcional | No | installer | PAR-005A, PAR-005B | SEC-001 | L: `safe_zip_update_extract`; W: `cli.py` + `install_ops` alineados |
| Versión runtime | OK | OK | Igual | Canonical | Exacta | No | — | PAR-002 | REL-001 | W: 0.3.2 alineado; CI `check_version_alignment` |
| Input backend | evdev | keyboard | Adaptado válido | Adapted | Funcional | Sí | Win32 | — | — | No es deuda; backends distintos |
| Persistencia canon `user/` | OK | OK (código) | Adaptado válido | Adapted | Funcional | Sí | AppData | PAR-001 | — | W: `%LOCALAPPDATA%\joystick_owerlay\user\` + portable |
| Reset dos fases | implementado | implementado (VM pendiente) | PARCIAL | Canonical | Pendiente | No | — | PAR-003 | SEC-003 | L/W: lock migración exclusivo (`fcntl` / `msvcrt`) |
| Hooks / input history | OK | OK | Igual | Canonical | Exacta | No | — | PAR-004 | — | |
| CLI soporte | OK | OK (flags); ops PARCIAL | PARCIAL | Canonical | Funcional | No | — | PAR-002 | — | |
| Instalación / accesos | install.sh | install/windows | PARCIAL | Adapted | Funcional | Sí | installer | PAR-006 | SEC-001 | Evidencia W: `install/windows/` |
| Preflight UX | PARCIAL | PARCIAL | PARCIAL | Canonical | Pendiente | No | — | PAR-007 | — | |
| CI / QA automatizado | PARCIAL (ci.yml) | PARCIAL (ci.yml) | PARCIAL | Canonical | Funcional | No | — | — | OPS-001 | L/W: pytest + version + doc links |
| ZIP perfil (import) | OK | OK | Igual | Canonical | Exacta | No | — | — | — | W: `profile_export.py` → `extract_zip_safely` |
| Monolitos / deuda LOC | PARCIAL | PARCIAL | PARCIAL | Canonical | Pendiente | Sí | — | — | ARCH-001, ARCH-002 | L: `main.py` ~140 LOC; W: `profile_config/` + hit-test editor (PARCIAL) |
| Política ventana Win32 | N/E (WM tiling) | OK (resize SO, sin WM opts) | Adaptado válido | Adapted | Funcional | Sí | Win32 | — | — | W: sin `window_mode`/`ignore_videoresize` en UI; `RESIZABLE` + cooldown VIDEORESIZE |
| Canal release usuario | PARCIAL | PARCIAL | PARCIAL | Canonical | Pendiente | No | — | PAR-005B | OPS-002 | L/W: `CHANGELOG.md` 0.3.2 con subsecciones por plataforma |
| Tooling / higiene Git | PARCIAL | PARCIAL | PARCIAL | Canonical | Funcional | Sí | — | — | OPS-003 | L: ruff/radon warn CI; W: port vs HEAD |
| Docs layout vs árbol | OK | PARCIAL | PARCIAL | Canonical | Pendiente | No | — | — | DOC-001 | W: `repository_layout.md` vs árbol real |

## Capa prohibida activa (violaciones `drift_permitido: No`)

- **SEC-002** — Concurrencia `input_state` (L mitigado; W N/E backend distinto).

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
- **Fase 2 (`hud_owerlay`):** columna Windows verificada 2026-05-26; `linux_ref` → `a19edb8`.
