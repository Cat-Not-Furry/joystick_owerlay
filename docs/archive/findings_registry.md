# Registro global de hallazgos — Joystick Overlay

**Fuente de verdad** para IDs `SEC-*`, `REL-*`, `ARCH-*`, `OPS-*`, `DOC-*` compartidos entre `hud_overlay` y `hud_owerlay`. Normas: [audit_contract_v1.md](../developer/audit_contract_v1.md). Vista sistema × plataforma: [parity_matrix.md](parity_matrix.md).

```
last_sync_linux: a19edb8 (0.3.2, 2026-05-26)
last_sync_windows: e924195 (hud_owerlay, Fase 2, 2026-05-26)
```

## Índice rápido

| ID | P | global_status | PAR |
|----|---|---------------|-----|
| [SEC-001](#sec-001--pipeline-zip-inconsistente) | P0 | PARCIAL | PAR-005A |
| [SEC-002](#sec-002--input_state-sin-sincronización) | P0 | PARCIAL | — |
| [SEC-003](#sec-003--lock-de-migración-no-atómico) | P1 | PARCIAL | PAR-001 |
| [REL-001](#rel-001--versión-runtime--metadatos) | P1 | PARCIAL | PAR-002 |
| [ARCH-001](#arch-001--monolitos-entrypoints-linux) | P2 | PARCIAL | — |
| [ARCH-002](#arch-002--deuda-mantenibilidad-windows) | P2 | PARCIAL | — |
| [OPS-001](#ops-001--sin-cicd) | P1 | PARCIAL | — |
| [OPS-002](#ops-002--canal-release--changelog) | P2 | PARCIAL | PAR-005B |
| [OPS-003](#ops-003--higiene-repo--tooling) | P3 | PARCIAL | — |
| [DOC-001](#doc-001--drift-repository_layout-windows) | P2 | PARCIAL | — |

### Migración desde informes locales

| Origen Linux | Origen Windows | ID global |
|--------------|----------------|-----------|
| Top-5 P0 ZIP / `update.sh` | AUD-2-001 | SEC-001 |
| Top-5 P0 `input_state` | — | SEC-002 |
| P1 migration lock | — | SEC-003 |
| — | AUD-2-002 | REL-001 |
| Q-01, Q-02 | — | ARCH-001 |
| — | AUD-1-002 | ARCH-002 |
| Sin `.github/workflows` | — | OPS-001 |
| PAR-005B / sin CHANGELOG | — | OPS-002 |
| Sin ruff/radon | AUD-6-001 | OPS-003 |
| — | AUD-3-001 | DOC-001 |

---

### SEC-001 — Pipeline ZIP inconsistente

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P0 |
| causality | Confirmado (Linux); Confirmado (Windows, Fase 2) |
| linked_par | PAR-005A |
| parity_layer | Prohibida |
| drift_permitido | No |
| linux_manifestation | `scripts/update.sh` usa `scripts/safe_zip_update_extract.py` (SEC-001 mitigado 2026-05-26) |
| windows_manifestation | `install/windows/install_ops.py` usa `safe_zip_extract`; runtime `cli.py` + `profile_export.py` alineados (SEC-001 mitigado W 2026-05-26) |
| impact_runtime | Alto |
| impact_release | Alto |
| impact_maintainability | Bajo |
| impact_security | Alto |
| evidence | Estática |
| reproducible | Desconocido |
| confidence | 0.90 |
| last_verified | L `a19edb8` / W `e924195` / 2026-05-26 |

---

### SEC-002 — input_state sin sincronización

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P0 |
| causality | Confirmado |
| linked_par | — |
| parity_layer | Canónica (concurrencia) |
| drift_permitido | No |
| linux_manifestation | `core/input_state_sync.py` + lock en `maps/input_reader.py`; snapshot en `main.py` (SEC-002 mitigado 2026-05-26) |
| windows_manifestation | N/E (backend distinto; no equivaler a evdev) |
| impact_runtime | Alto |
| impact_release | Medio |
| impact_maintainability | Medio |
| impact_security | Alto |
| evidence | Estática |
| reproducible | Desconocido |
| confidence | 0.85 |
| last_verified | L `a19edb8` / 2026-05-26 |

---

### SEC-003 — Lock de migración no atómico

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P1 |
| causality | Confirmado |
| linked_par | PAR-001 |
| parity_layer | Canónica |
| drift_permitido | No |
| linux_manifestation | `data_migrations._acquire_migration_lock`: `fcntl.flock` exclusivo (SEC-003 mitigado 2026-05-26) |
| windows_manifestation | `data_migrations._acquire_migration_lock`: `msvcrt.locking` / `fcntl` NB exclusivo (SEC-003 mitigado W 2026-05-26) |
| impact_runtime | Medio |
| impact_release | Medio |
| impact_maintainability | Bajo |
| impact_security | Medio |
| evidence | Estática |
| reproducible | No |
| confidence | 0.88 |
| last_verified | L `a19edb8` / W `e924195` / 2026-05-26 |

---

### REL-001 — Versión runtime / metadatos

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P1 |
| causality | Confirmado (Linux); Confirmado (Windows, Fase 2) |
| linked_par | PAR-002 |
| parity_layer | Canónica |
| drift_permitido | No |
| linux_manifestation | `.joystick_version` + `pyproject.toml` alineados 0.3.2 en `a19edb8` |
| windows_manifestation | `.joystick_version` + `pyproject.toml` + `version.txt` alineados **0.3.2**; `check_version_alignment.py` en CI (REL-001 mitigado W 2026-05-26) |
| impact_runtime | Bajo |
| impact_release | Medio |
| impact_maintainability | Bajo |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.90 |
| last_verified | L `a19edb8` / W `e924195` / 2026-05-26 |

---

### ARCH-001 — Monolitos entrypoints (Linux)

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P2 |
| causality | Confirmado |
| linked_par | — |
| parity_layer | — (mantenibilidad) |
| drift_permitido | Sí |
| linux_manifestation | `main.py` ~140 LOC (ARCH-001 Fases A–D); `arcade/engine/app/` orquestación + `app/profile_config/` (handlers por sección); shim `render/profile_config_menu.py` ~15 LOC; CC radon: `run_hud_layout_editor` era CC=100 (2026-05-26), refactorizado a CC≤10 en `1b0eaf2` — ver [audit_cc_menu.md](audit_cc_menu.md) |
| windows_manifestation | N/E |
| impact_runtime | Bajo |
| impact_release | Bajo |
| impact_maintainability | Alto |
| impact_security | Bajo |
| evidence | Estática + Runtime (pytest, radon post-refactor) |
| reproducible | Sí |
| confidence | 0.95 |
| last_verified | hud_overlay ARCH-001 + profile_config / 2026-05-26 |

---

### ARCH-002 — Deuda mantenibilidad (Windows)

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P2 |
| causality | Confirmado (Windows) |
| linked_par | — |
| parity_layer | — (mantenibilidad) |
| drift_permitido | Sí |
| linux_manifestation | N/E |
| windows_manifestation | `render/profile_config/` handlers por sección (ARCH-002 B); `hud_layout_editor_hit.py` hit-test extraído; `main.py` fachada estable (PARCIAL 2026-05-26) |
| impact_runtime | Bajo |
| impact_release | Bajo |
| impact_maintainability | Alto |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.90 |
| last_verified | hud_owerlay `e924195` / 2026-05-26 |

---

### OPS-001 — Sin CI/CD

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P1 |
| causality | Confirmado |
| linked_par | — |
| parity_layer | Canónica (release) |
| drift_permitido | No |
| linux_manifestation | `.github/workflows/ci.yml` pytest+doc links+version check (OPS-001 PARCIAL Linux 2026-05-26) |
| windows_manifestation | `.github/workflows/ci.yml` pytest + doc links + version check (OPS-001 PARCIAL W 2026-05-26) |
| impact_runtime | — |
| impact_release | Alto |
| impact_maintainability | Medio |
| impact_security | Medio |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.99 |
| last_verified | L `a19edb8` / W `e924195` / 2026-05-26 |

---

### OPS-002 — Canal release / CHANGELOG

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P2 |
| causality | Confirmado |
| linked_par | PAR-005B |
| parity_layer | Canónica (release) |
| drift_permitido | No |
| linux_manifestation | `CHANGELOG.md` desde 0.3.2 (OPS-002 mitigado Linux 2026-05-26); paridad release Windows PENDIENTE |
| windows_manifestation | `CHANGELOG.md` con subsecciones Linux/Windows (0.3.2); `constructor.md` + `docs/user/installation.md` parciales |
| impact_runtime | — |
| impact_release | Alto |
| impact_maintainability | Bajo |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.90 |
| last_verified | L `a19edb8` / W `e924195` / 2026-05-26 |

---

### OPS-003 — Higiene repo / tooling

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P3 |
| causality | Confirmado |
| linked_par | — |
| parity_layer | — (higiene) |
| drift_permitido | Sí |
| linux_manifestation | `[tool.ruff]` + ruff/radon/CBO en CI modo warn (OPS-003 PARCIAL Linux 2026-05-26); gate CC global pendiente |
| windows_manifestation | Port `arcade/` y `docs/` mayormente untracked vs HEAD; `.gitignore` incompleto (AUD-6-001) |
| impact_runtime | — |
| impact_release | Bajo |
| impact_maintainability | Medio |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.92 |
| last_verified | L `a19edb8` / W `e924195` / 2026-05-26 |

---

### DOC-001 — Drift repository_layout (Windows)

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P2 |
| causality | Confirmado (Windows) |
| linked_par | — |
| parity_layer | Canónica (docs) |
| drift_permitido | No |
| linux_manifestation | N/E |
| windows_manifestation | `docs/developer/repository_layout.md` cita `scripts/` raíz inexistente; `CONTRIBUTING.md` ausente (AUD-3-001) |
| impact_runtime | — |
| impact_release | Bajo |
| impact_maintainability | Medio |
| impact_security | — |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.95 |
| last_verified | hud_owerlay `e924195` / 2026-05-26 |
