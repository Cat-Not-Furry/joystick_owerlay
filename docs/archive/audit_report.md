# Informe de auditoría — Joystick Owerlay (Windows)

**Schema:** [audit_contract_v1](../developer/audit_contract_v1.md) v1.1 — hallazgos canónicos en [findings_registry.md](findings_registry.md); paridad en [parity_matrix.md](parity_matrix.md) (`matrix_version: 2`).

- **Estados de producto y cierres por eje (E1–E4):** [bitácora § Matriz de cierre](bitacora.md#matriz-de-cierre-windows-checkout-actual) y [§ Contratos cerrados](bitacora.md#contratos-cerrados-en-este-checkout-windows). Este informe no sustituye el tablero PAR ni el registry.
- **`hecho` (W-*) ≠ `OK` (PAR-*):** ver regla de oro en bitácora antes de inferir cierre desde este documento.

| Campo | Valor |
|-------|--------|
| **Fecha** | 2026-05-18 |
| **Repositorio** | `hud_owerlay` (checkout local) |
| **Alcance** | Dimensiones 1, 2, 3, 5, 6, 7, 8 (dimensión 4 excluida por mandato) |
| **Paridad Linux** | [bitacora.md](bitacora.md), [findings_registry.md](findings_registry.md) (Linux `b31d5d7`) |

---

## 1. Resumen ejecutivo

| Dim | Tema | Puntuación (0–100) |
|-----|------|-------------------|
| 1 | Calidad del código | **52** |
| 2 | Seguridad y dependencias | **68** |
| 3 | Documentación | **62** |
| 4 | Pruebas y QA | **N/A** |
| 5 | Configuración y automatización | **38** |
| 6 | Estructura e higiene Git | **58** |
| 7 | Checklist pre-release GitHub | **48** |
| 8 | Paridad Windows (docs vs código) | **56** |

**Puntuación global ponderada** (dims 1–3, 5–8, pesos iguales): **≈ 55/100**

**Estado release (ladder):** [`LOCAL_READY`](../developer/audit_contract_v1.md) — desarrollo y clon de confianza con precaución en ZIP de terceros. **No** `OSS_READY` ni `RELEASE_READY` (SEC-001, REL-001, OPS-003, W-OPS-001).

### Índice de migración AUD → SEC

| AUD (este informe) | ID global |
|--------------------|-----------|
| AUD-2-001 | [SEC-001](findings_registry.md#sec-001--pipeline-zip-inconsistente) |
| AUD-2-002 | [REL-001](findings_registry.md#rel-001--versión-runtime--metadatos) |
| AUD-1-002 | [ARCH-002](findings_registry.md#arch-002--deuda-mantenibilidad-windows) |
| AUD-6-001 | [OPS-003](findings_registry.md#ops-003--higiene-repo--tooling) |
| AUD-3-001 | [DOC-001](findings_registry.md#doc-001--drift-repository_layout-windows) |

---

## 2. Metodología y restricciones

### Mandatos aplicados

- Sin crear ni usar `venv/`, sin `pip install` del proyecto.
- Sin ejecutar `tests/`, `scripts/`, `body/scripts/`, `main.py`, `cli.py`, instaladores ni `.bat`.
- Sin modificar código fuente del producto (solo este informe y fila en `docs/README.md`).

### Herramientas

| Herramienta | Estado |
|-------------|--------|
| `ruff` | No en PATH — no ejecutada |
| `bandit` | No en PATH — no ejecutada |
| `radon` | No en PATH — no ejecutada |
| `pip-audit` | No en PATH — no ejecutada |
| `mypy` | No en PATH — no ejecutada |
| Análisis AST (`python3 -c …`) | Ejecutado sobre `arcade/engine/`, `main.py`, `cli.py` |
| `grep`, lectura estática, `git status`, `git log -S` | Ejecutados |

---

## 3. Hallazgos por dimensión

### Dimensión 1 — Calidad del código

| ID | Sev. | Hallazgo | Evidencia | Recomendación |
|----|------|----------|-----------|---------------|
| AUD-1-001 | Alta | Cobertura de type hints ~**1,9%** (8/425 funciones en `arcade/engine/`). | Análisis AST 2026-05-18 | Introducir hints en APIs públicas (`profile_store`, `safe_paths`, `config`) de forma incremental. |
| AUD-1-002 | Alta | Función monolítica **`run_hud_layout_editor`** ~409 líneas. | `arcade/engine/render/hud_layout_editor.py` L190 | Extraer submódulos por responsabilidad (input, dibujo, persistencia). |
| AUD-1-003 | Media | Otras funciones >50 líneas: `profile_config_menu._run_update_modal` (112), `hud_layout.resolve_hud_layout_offsets` (99), `extract_zip_safely` (86). | AST | Refactor por fases; umbral CC≤10 de bitácora no verificado (sin radon). |
| AUD-1-004 | Media | **`main.py`** ~1265 líneas; mezcla menú, reset, workers, bucle HUD. | `main.py` | Separar orquestación y bucle Pygame (alineado a SRP). |
| AUD-1-005 | Baja | Sin `TODO`/`FIXME` en `arcade/`; sin `eval`/`exec` en canon. | `grep` | Mantener política. |
| AUD-1-006 | Baja | Sin configuración `[tool.ruff]` / formatter en `pyproject.toml`. | `pyproject.toml` | Añadir Ruff/Black en dev deps (fuera de alcance de esta auditoría). |

### Dimensión 2 — Seguridad y dependencias

| ID | Sev. | Hallazgo | Evidencia | Recomendación |
|----|------|----------|-----------|---------------|
| AUD-2-001 → **SEC-001** | **Crítica** | **`install_ops.extract_payload_archive`** usa `zipfile.ZipFile.extractall` sin `safe_zip_extract`. | `install/windows/install_ops.py` L56–57 | Reutilizar `extract_zip_safely` o validar payload firmado pre-extraído; documentar confianza del canal. |
| AUD-2-002 | Alta | Desalineación de **versión**: `pyproject.toml` **0.3.1** vs `.joystick_version` **1.0.0**; CLI usa `get_runtime_version()` del archivo. | `pyproject.toml` L7, `.joystick_version`, `config.get_runtime_version` | Una sola fuente de verdad (p. ej. `.joystick_version` + sync en build). |
| AUD-2-003 | Media | **`UPDATE_WHITELIST`** en `cli.py` no incluye `pyproject.toml`, `LICENSE`, `MANIFEST.in`, `.joystick_version`, `requirements.txt`. | `cli.py` L25–36 | Ampliar whitelist o documentar omisión intencional. |
| AUD-2-004 | Media | Dependencia **`keyboard`** (hooks globales Win) — superficie de privilegios y AV. | `pyproject.toml`, `requirements.txt` | Documentar requisitos admin/UAC en `docs/user/troubleshooting.md`; evaluar alternativas en roadmap. |
| AUD-2-005 | Baja | **`safe_zip_extract`** y **`profile_export`** import usan extracción segura; **`cli --update`** valida `.assets_version` e `icon_packs`. | `safe_zip_extract.py`, `cli.py` L67–74 | Mantener; añadir test de regresión cuando se rehabilite dim 4. |
| AUD-2-006 | Baja | **`resolve_under_root`** solo devuelve ruta si el fichero **existe** — puede limitar resolución anticipada. | `safe_paths.py` L37–38 | Revisar si `assets_resolver` necesita `path_is_under_root` para rutas nuevas. |
| AUD-2-007 | Baja | `git log -S "password"` devolvió commit histórico `0e87b67`; sin secretos obvios en árbol actual. | `git log` | Muestreo manual del commit si se publica repo. |
| AUD-2-008 | Info | Sin `eval`/`exec`/`pickle`/`shell=True` en `arcade/engine/`. `subprocess` en `main.py`, `cli.py`, menú, instalador — revisado estático. | `grep` | Mantener lista blanca de comandos en instalador. |

### Dimensión 3 — Documentación

| ID | Sev. | Hallazgo | Evidencia | Recomendación |
|----|------|----------|-----------|---------------|
| AUD-3-001 | Alta | **[repository_layout.md](developer/repository_layout.md)** referencia `scripts/` en raíz y `CONTRIBUTING.md` / `tests/README.md` — **no existen** en este checkout Windows. | `docs/developer/repository_layout.md` L18–19, L35 | Actualizar layout Windows (`install/windows/`, sin `scripts/` raíz). |
| AUD-3-002 | Media | **Bitácora** tabla W-20260426-001 aún lista **Inno** como evidencia principal; historial 2026-05-18 dice sustitución por Python. | `docs/archive/bitacora.md` L130 vs L378 | Actualizar fila A.1 W-20260426-001 a `install/windows/`. |
| AUD-3-003 | Media | Sin **`CHANGELOG.md`** ni **`CONTRIBUTING.md`** en raíz. | `glob` | Añadir CHANGELOG (Keep a Changelog) y CONTRIBUTING mínimo. |
| AUD-3-004 | Baja | README funcional pero sin badges, capturas ni sección Contributing. | `README.md` | Opcional pre-release. |
| AUD-3-005 | Baja | **`docs/security/security_model.md`** § verificación local cita ejecutar tests — coherente con producto pero contradice mandato de auditoría sin tests. | `security_model.md` L42–46 | Aclarar “operador / CI” vs auditoría estática. |
| AUD-3-006 | Info | Contrato **[data_contract_windows_v1.md](developer/data_contract_windows_v1.md)** alineado con `config.py` (`APP_ID`, manifiesto, `data_version` 5). | Lectura cruzada | Mantener sincronía en cambios de rutas. |

### Dimensión 4 — Pruebas y QA

**No evaluada** (mandato). Confianza en regresiones depende de **QA manual VM (W-OPS-001)**.

Inventario documental (sin ejecutar):

| Fichero | Intención declarada |
|---------|---------------------|
| `tests/test_zip_security.py` | Política `safe_zip_extract` |
| `tests/test_config_paths.py` | Rutas `get_user_dir` / backup |
| `tests/test_hud_layout.py` | Layout MVS / rejilla |
| `tests/test_keyboard_backend.py` | Backend teclado |
| `tests/test_state_navigation.py` | Navegación menú |

---

### Dimensión 5 — Configuración y automatización

| ID | Sev. | Hallazgo | Evidencia | Recomendación |
|----|------|----------|-----------|---------------|
| AUD-5-001 | Alta | Sin **`.github/workflows/`**, Dependabot ni CodeQL. | `glob .github/**` vacío | Workflow mínimo: lint + (opcional) tests en runner Windows. |
| AUD-5-002 | Media | `pyproject.toml` sin `[project.optional-dependencies]` dev, sin `[tool.ruff]`/`mypy`. | `pyproject.toml` | Sección `dev` con ruff, pytest, bandit. |
| AUD-5-003 | Media | **`requirements.txt`** incluye `pyinstaller==6.11.1`; **`pyproject.toml`** no — divergencia build vs runtime. | Ambos ficheros | Unificar: runtime en pyproject; build en `requirements-build.txt` o extra. |
| AUD-5-004 | Baja | Entry point `joystick-overlay = cli:run` declarado. | `pyproject.toml` L17–18 | Verificar en build PyInstaller (`constructor.md`). |

**Checklist “listo para CI mínimo” (recomendación):**

1. `ruff check` en `arcade/engine` + entrypoints  
2. `bandit -r arcade/engine install/windows`  
3. `pytest` en runner (cuando dim 4 se rehabilite)  
4. Job Windows opcional para `doctor` smoke (sin GUI en CI — limitado)

---

### Dimensión 6 — Estructura e higiene Git

| ID | Sev. | Hallazgo | Evidencia | Recomendación |
|----|------|----------|-----------|---------------|
| AUD-6-001 | Alta | **Árbol Git muy sucio**: muchos `D` (paquetes legacy borrados) y `??` masivos (`arcade/`, `docs/`, `LICENSE`, …) sin commit de port. | `git status` 2026-05-18 | Commit atómico del port o ramas claras antes de release. |
| AUD-6-002 | Media | Handoff Linux en **`body/`** consumido (Fase 2); carpeta retirada tras fusionar docs. | Historial bitácora 2026-05-18 | No reintroducir `body/` como runtime. |
| AUD-6-003 | Media | **`.gitignore`** no ignora `.pytest_cache/`, `.ruff_cache/`, `user/` (datos locales). | `.gitignore` | Ampliar plantilla Python/Windows. |
| AUD-6-004 | Baja | Carpeta **`json/profiles.json`** legacy en raíz (986 B). | `json/profiles.json` | Mover a docs o eliminar si migración completa. |
| AUD-6-005 | Baja | **`.pytest_cache/`** presente en disco. | `find` | Añadir a `.gitignore` y borrar del working tree. |
| AUD-6-006 | Info | Canon activo: `arcade/engine/` + entrypoints; paquetes raíz `config/`, `core/`, etc. **eliminados** del working tree (solo en historial Git como `D`). | `git status` | Tras commit, verificar que no queden imports rotos. |

### Tabla canon / legacy / basura

| Clasificación | Rutas |
|---------------|--------|
| **Canon** | `arcade/engine/`, `arcade/assets/`, `configs/`, entrypoints raíz, `install/windows/`, `docs/`, `engine_sys_path.py` |
| **Legacy documentado** | `install/installer.iss`, `install/*.bat`, `json/profiles.json` |
| **Basura local** | `.pytest_cache/`, `__pycache__/`, posible `user/` dev |
| **Handoff consumido** | `body/` (retirada post-Fase 2); paquetes Python legacy en raíz eliminados del working tree |

---

### Dimensión 7 — Checklist pre-release GitHub

| Ítem | Estado |
|------|--------|
| README render y enlaces principales | **Parcial** — enlaces a `docs/` OK; sin badges/capturas |
| LICENSE + pyproject | **Cumple** — GPL-3 + `license = { file = "LICENSE" }` |
| CHANGELOG en raíz | **No** |
| PII en historial | **Parcial** — sin hallazgos en árbol; un commit con `-S password` a revisar |
| Instalación documentada | **Parcial** — `docs/user/installation.md`, `constructor.md`; build no verificado en VM |
| CI verde | **N/A** — sin CI |
| Issues críticos abiertos | **N/A** — no consultado remoto |
| Tests automatizados | **N/A** — excluidos |

---

### Dimensión 8 — Paridad Windows (local)

| Referencia | Estado código | Notas |
|------------|---------------|-------|
| W-20260425-001 Persistencia AppData | **Cumple** | `config.py` `APP_ID=joystick_owerlay`, manifiesto, `get_user_dir()` |
| W-20260425-002 CLI | **Cumple** | `cli.py` run/config/tournament/doctor/version/reset-log/update |
| W-20260425-003 Reset dos fases | **Cumple** | `main.py` `--reset-data`, `--do-reset-data` |
| W-20260425-004 Input history / extensions | **Cumple** | `arcade/engine/core/input_history.py`, `extensions_runtime.py` |
| W-20260426-001 Instalación | **Parcial** | `install/windows/` + legacy `.iss`/`.bat`; bitácora desactualizada |
| W-UPD-ZIP-001 Update ZIP | **Cumple** | `cli.py` + `safe_zip_extract`; whitelist acotada (AUD-2-003) |
| W-OPS-001 VM | **Pendiente** | Documentado en bitácora |
| Checklist rebranding #1 `joystick-overlay` | **Parcial** | `pyproject` scripts sí; ejecutable `.exe` no verificado en árbol |
| Checklist #2 `%LOCALAPPDATA%\joystick_owerlay` | **Cumple** | Contrato y `install_ops` usan `joystick_owerlay` (no `joystick_overlay` del checklist antiguo) |
| Checklist #3 `.joystick_version` | **Parcial** | Existe; desalineado con pyproject (AUD-2-002) |
| Checklist #4 `JOYSTICK_*` | **Parcial** | `JOYSTICK_STORAGE_MODE` sí; persisten `HUD_DEBUG_*`, `HUD_IGNORE_VIDEORESIZE` en `main.py` |
| Checklist #5 UI / accesos | **Parcial** | `install/windows/`; no validado en VM |
| Handoff `body/` consumido | **Cumple** | Artefactos en `docs/`; `body/` retirada |

---

## 4. Plan de acción priorizado

| Prioridad | ID | Acción |
|-----------|-----|--------|
| **P0** | AUD-2-001 | Sustituir `extractall` en instalador por extracción segura o payload pre-validado firmado. |
| **P0** | AUD-6-001 | Commit/organización del port completo antes de tag de release. |
| **P1** | AUD-2-002 | Unificar versiones (`0.3.1` vs `1.0.0`). |
| **P1** | AUD-3-001, AUD-3-002 | Corregir docs obsoletos (layout, bitácora Inno). |
| **P1** | W-OPS-001 | Validación VM: instalar, HUD, config, torneo, update ZIP, desinstalar. |
| **P2** | AUD-5-001, AUD-5-002 | CI mínimo + herramientas dev en pyproject. |
| **P2** | AUD-1-002, AUD-1-004 | Refactor `hud_layout_editor` y `main.py`. |
| **P3** | AUD-3-003, AUD-6-003 | CHANGELOG, CONTRIBUTING, `.gitignore`. |

---

## 5. Métricas

| Métrica | Valor |
|---------|--------|
| Hallazgos totales | 28 |
| Crítica | 1 |
| Alta | 6 |
| Media | 11 |
| Baja | 8 |
| Info | 2 |
| `TODO`/`FIXME` en `arcade/` | 0 |
| `eval`/`exec` en canon | 0 |
| Type hints (funciones `arcade/engine`) | ~1,9% |
| Funciones >50 líneas (muestra top) | ≥8 |
| Ficheros en `tests/` (no ejecutados) | 5 |
| Herramientas automatizadas ejecutadas | 0 (no en PATH) |

---

## 6. Anexo — Comandos

```bash
# Ejecutados
git status --short
git tag -l
git log -S "password" --oneline
git log -S "api_key" --oneline
python3 -c "<AST análisis longitud funciones y type hints>"

# No ejecutados (mandato / no en PATH)
# python -m venv ...
# pip install -r requirements.txt
# pytest tests/
# scripts/* body/scripts/*
# ruff check .
# bandit -r arcade/engine
# radon cc arcade/engine -a
# pip-audit -r requirements.txt
```

---

*Fin del informe. Próxima revisión recomendada tras commit del port y cierre W-OPS-001.*
