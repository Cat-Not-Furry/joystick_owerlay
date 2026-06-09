# Changelog — Joystick Overlay

Cambios notables del producto **Joystick Overlay** en ambos repositorios (`hud_overlay` Linux, `hud_owerlay` Windows).

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado: [SemVer](https://semver.org/lang/es/).

## [Unreleased]

### Cross-repo / contrato

- Validación humana Windows (Fase 4 checklist) pendiente de mantenedor.

## [0.3.2] - 2026-05-26

### Linux (`hud_overlay`)

#### Added

- CI en `.github/workflows/ci.yml`: pytest, `check_doc_links`, `check_version_alignment`.
- [docs/developer/agent_runtime_v1.md](docs/developer/agent_runtime_v1.md): política `.venv` / `tests/.tvenv`.
- Extracción ZIP segura en actualizaciones: `scripts/safe_zip_update_extract.py`.
- Lock de migraciones con `fcntl.flock`.

#### Security

- **SEC-001** (Linux): `update.sh` sin `unzip` directo.
- **SEC-002** (Linux): race `input_state` mitigada.
- **SEC-003** (Linux): lock de migración atómico.

### Windows (`hud_owerlay`)

#### Added

- [docs/developer/agent_runtime_v1.md](docs/developer/agent_runtime_v1.md) adaptado a Win32.
- `scripts/check_version_alignment.py`, `scripts/check_doc_links.py`.
- CI mínima en `.github/workflows/ci.yml`.
- Política Win32: sin opciones `window_mode` / `ignore_videoresize` en menú; ventana fija.

#### Changed

- Versión alineada a **0.3.2** (`.joystick_version`, `pyproject.toml`).
- `install/windows/install_ops.py`: extracción ZIP con `safe_zip_extract`.
- Lock de migración Win32 (`msvcrt` / exclusivo).
- Actualización desde menú: `cli.py --update --zip` (no `scripts/update.sh`).
- Menú configuración troceado en `render/profile_config/` (ARCH-002 B).

#### Security

- **SEC-001** (Windows): install payload sin `extractall`.
- **SEC-003** (Windows): lock de migración atómico.

### Cross-repo

- `findings_registry.md` y `parity_matrix.md` sincronizados; `linux_ref: a19edb8`, `windows_ref: 0.3.2`.
