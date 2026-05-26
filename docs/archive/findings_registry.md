# Registro global de hallazgos — Joystick Overlay

**Fuente de verdad** para IDs `SEC-*`, `REL-*`, `ARCH-*`, `OPS-*`, `DOC-*` compartidos entre `hud_overlay` y `hud_owerlay`. Normas: [audit_contract_v1.md](../developer/audit_contract_v1.md). Vista sistema × plataforma: [parity_matrix.md](parity_matrix.md).

```
last_sync_linux: b31d5d7 (2026-05-14)
last_sync_windows: 5dd784e+port (2026-05-22, capas v1.1 / matrix v2)
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
| linux_manifestation | `scripts/update.sh` ~132: `unzip` sin cuotas equivalentes a `arcade/engine/utils/safe_zip_extract.py` |
| windows_manifestation | `install/windows/install_ops.py` L56–57: `ZipFile.extractall`; runtime `cli.py` + `profile_export.py` usan `safe_zip_extract` (PARCIAL) |
| impact_runtime | Alto |
| impact_release | Alto |
| impact_maintainability | Bajo |
| impact_security | Alto |
| evidence | Estática |
| reproducible | Desconocido |
| confidence | 0.95 |
| last_verified | hud_owerlay Fase 2 / 2026-05-18 |

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
| linux_manifestation | `main.py` ~1046 + `arcade/engine/input/input_reader.py`: mutación en hilo daemon, lectura en bucle principal sin lock (CWE-362) |
| windows_manifestation | N/E (backend distinto; no equivaler a evdev) |
| impact_runtime | Alto |
| impact_release | Medio |
| impact_maintainability | Medio |
| impact_security | Alto |
| evidence | Estática |
| reproducible | Desconocido |
| confidence | 0.85 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

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
| linux_manifestation | `arcade/engine/core/data_migrations.py` `_acquire_migration_lock`: `isfile` + `open`, sin `fcntl`/`O_EXCL` |
| windows_manifestation | `arcade/engine/core/data_migrations.py` `_acquire_migration_lock`: `isfile` + `open`, sin `fcntl`/`O_EXCL` (mismo patrón) |
| impact_runtime | Medio |
| impact_release | Medio |
| impact_maintainability | Bajo |
| impact_security | Medio |
| evidence | Estática |
| reproducible | No |
| confidence | 0.88 |
| last_verified | hud_owerlay Fase 2 / 2026-05-18 |

---

### REL-001 — Versión runtime / metadatos

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P1 |
| causality | Confirmado (ambas plataformas) |
| linked_par | PAR-002 |
| parity_layer | Canónica |
| drift_permitido | No |
| linux_manifestation | `.joystick_version` en raíz vs `pyproject.toml` — alineados en `b31d5d7`; vigilar drift en portes |
| windows_manifestation | `.joystick_version` **1.0.0** vs `pyproject.toml` **0.3.1**; CLI usa `get_runtime_version()` |
| impact_runtime | Bajo |
| impact_release | Medio |
| impact_maintainability | Bajo |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.92 |
| last_verified | hud_owerlay Fase 2 / 2026-05-18 |

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
| linux_manifestation | `main.py` 1359 LOC; `arcade/engine/render/profile_config_menu.py` 1038 LOC (Q-01, Q-02) |
| windows_manifestation | N/E |
| impact_runtime | Bajo |
| impact_release | Bajo |
| impact_maintainability | Alto |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.95 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

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
| windows_manifestation | `arcade/engine/render/hud_layout_editor.py` `run_hud_layout_editor` ~409 LOC (AUD-1-002) |
| impact_runtime | Bajo |
| impact_release | Bajo |
| impact_maintainability | Alto |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Desconocido |
| confidence | 0.90 |
| last_verified | hud_owerlay Fase 2 / 2026-05-18 |

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
| linux_manifestation | Ausencia de `.github/workflows` |
| windows_manifestation | Sin `.github/workflows` (Confirmado) |
| impact_runtime | — |
| impact_release | Alto |
| impact_maintainability | Medio |
| impact_security | Medio |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.99 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

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
| linux_manifestation | Sin CHANGELOG; política de actualización en campo incompleta (L-OPS-003-P) |
| windows_manifestation | Sin `CHANGELOG.md` raíz; `constructor.md` + `docs/user/installation.md` parciales |
| impact_runtime | — |
| impact_release | Alto |
| impact_maintainability | Bajo |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.90 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

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
| linux_manifestation | Sin `[tool.ruff]` / `radon` en `pyproject.toml` (Q-04 ámbito tooling) |
| windows_manifestation | Port `arcade/` y `docs/` mayormente untracked vs HEAD `5dd784e`; `.gitignore` incompleto |
| impact_runtime | — |
| impact_release | Bajo |
| impact_maintainability | Medio |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.92 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

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
| windows_manifestation | `docs/developer/repository_layout.md` cita `scripts/` raíz inexistente; CONTRIBUTING ausente (AUD-3-001) |
| impact_runtime | — |
| impact_release | Bajo |
| impact_maintainability | Medio |
| impact_security | — |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.95 |
| last_verified | hud_owerlay Fase 2 / 2026-05-18 |
