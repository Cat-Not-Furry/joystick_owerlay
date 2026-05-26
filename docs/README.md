# Documentación — Joystick Owerlay (Windows)

Índice por audiencia. Entrada rápida: [README raíz](../README.md).

## Jerarquía de contratos (gobernanza)

| Contrato | Documento | Rol |
|----------|-----------|-----|
| Datos Windows | [data_contract_windows_v1.md](developer/data_contract_windows_v1.md) | Rutas, manifiesto, modos |
| Auditoría v1.1 | [audit_contract_v1.md](developer/audit_contract_v1.md) | Severidad, **capas de paridad**, ladder |
| Hallazgos globales | [findings_registry.md](archive/findings_registry.md) | SEC/REL/ARCH/OPS/DOC |
| Paridad por sistema | [parity_matrix.md](archive/parity_matrix.md) | **v2** — `tipo`, `drift_permitido`, `motivo_plataforma` |
| Operativo | [bitacora.md](archive/bitacora.md) | Tablero PAR, **matriz de cierre** (ejes E1–E4), colas |
| Instantánea | [audit_report.md](archive/audit_report.md) | Foto por commit |

La bitácora registra **qué** y **en qué eje está cerrado**; no sustituye procedimientos de build (ver README raíz y `constructor.md`).

## Usuarios

| Documento | Contenido |
|-----------|-----------|
| [Instalación](user/installation.md) | `joystick-overlay-setup.exe`, portable, accesos directos |
| [Inicio rápido](user/quick_start.md) | HUD y atajos |
| [Doctor](user/doctor.md) | `joystick-overlay doctor` |
| [ZIP de perfil](user/profile_zip.md) | Export/import, riesgos ZIP |
| [Modo entrenamiento](user/training_mode.md) | Grabación/reproducción |
| [Modo torneo](user/tournament_mode.md) | Torneo, FPS |
| [Solución de problemas](user/troubleshooting.md) | Teclado global, rutas, OBS |

## Streamers

| Documento | Contenido |
|-----------|-----------|
| [Modos de captura](streamer/capture_modes.md) | OBS, chroma |
| [Checklist OBS](streamer/obs_setup.md) | Fuente ventana |

## Desarrollo

| Documento | Contenido |
|-----------|-----------|
| [Contrato Windows v1](developer/data_contract_windows_v1.md) | Rutas, manifiesto, modos |
| [Contrato Linux (referencia)](developer/data_contract_v1.md) | Paridad con `hud_overlay` |
| [Matriz reset](developer/reset_matrix.md) | PAR-003 |
| [Migraciones](developer/migrations.md) | `configs/migrations/` |
| [Estructura del repo](developer/repository_layout.md) | `arcade/engine/` |
| [Contrato de auditoría v1.1](developer/audit_contract_v1.md) | Severidad, capas canónica/adaptable/prohibida, ladder |
| [Modelo de seguridad](security/security_model.md) | ZIP, locks, rutas |

## Archivo e historial

| Documento | Contenido |
|-----------|-----------|
| [Bitácora](archive/bitacora.md) | PAR, matriz de cierre E1–E4, colas Linux ↔ Windows |
| [Registro de hallazgos](archive/findings_registry.md) | IDs globales SEC/REL/ARCH/OPS/DOC |
| [Matriz de paridad](archive/parity_matrix.md) | v2 — sistema × Linux × Windows + capas |
| [Informe de auditoría](archive/audit_report.md) | Instantánea 2026-05-18 (schema audit_contract v1.1) |
| [Plan Fase 2 (referencia)](archive/windows_parity_rollout.md) | Fusión handoff Linux → Windows |

## Tests

```bat
set PYTHONPATH=arcade\engine
python tests\test_zip_security.py
```
