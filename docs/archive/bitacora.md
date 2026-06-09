# Bitácora de variantes HUD / Joystick Overlay

## Nota de checkout (leer primero)

- **Ubicación canon (Windows):** [`docs/archive/bitacora.md`](bitacora.md) en `hud_owerlay`. No usar copias bajo `body/` como fuente operativa.
- **`hud_owerlay` (Windows)** y **`hud_overlay` (Linux, slug Git)** son **repositorios Git distintos**; el **nombre de producto** orientado al usuario es **Joystick Overlay**. Esta bitácora puede vivir en ambos repos como contrato de paridad.
- En **`hud_owerlay` (Windows)**: la **Parte A** es el inventario verificable en el árbol actual (`arcade/engine/`, entrypoints raíz); la **Parte B** resume Linux (commit de referencia en [findings_registry.md](findings_registry.md)).
- Al copiar esta bitácora desde Linux, **no invertir los IDs** (`PAR-*`, `L-*`, `W-*`): solo invertir qué parte es verificable localmente y completar la evidencia Windows.
- Handoff Linux (2026-05-25): correcciones de traslado fusionadas a `docs/`; `body/` retirado tras verificación.

## Jerarquía de contratos y ejes de cierre

| Contrato | Documento | Qué obliga |
|----------|-----------|------------|
| Datos Windows | [data_contract_windows_v1.md](../developer/data_contract_windows_v1.md) | Rutas, manifiesto, `data_version`, modos portable/instalado |
| Datos Linux (ref.) | [data_contract_v1.md](../developer/data_contract_v1.md) | Invariantes upstream |
| Auditoría / estados | [audit_contract_v1.md](../developer/audit_contract_v1.md) v1.1 | P0–P3, capas, ladder, semáforo |
| Paridad producto | Tabla **PAR-*** + [parity_matrix.md](parity_matrix.md) | Equivalencia observable cross-repo |
| Seguridad operativa | [security_model.md](../security/security_model.md) + SEC en registry | ZIP, locks, rutas |
| Instantánea | [audit_report.md](audit_report.md) | Foto por commit; no gana a PAR/registry |

### Cuatro ejes de cierre (léxico obligatorio)

| Eje | Símbolos | Significa «cerrado» cuando… |
|-----|----------|----------------------------|
| **E1 — Implementación local** | `W-*` / `L-*`: `hecho`, `pendiente`, `Confirmado estático` | Código/artefacto presente y verificado en árbol (estático) |
| **E2 — Contrato de paridad** | `PAR-*`: `OK`, `PARCIAL`, `ROTO` | Ambos repos cumplen **resultado de producto** acordado (puede ser Adapted + drift Sí) |
| **E3 — Hallazgo técnico global** | `SEC-*` / `REL-*` …: `global_status` en registry | Mitigación verificada en **todas** manifestaciones aplicables |
| **E4 — Release / ops** | Ladder: `LOCAL_READY` → `OSS_READY` → … | Política de [audit_contract_v1.md](../developer/audit_contract_v1.md); VM, CI, canal |

**Regla de oro:** `hecho` en E1 **no implica** `OK` en E2 ni cierre en E3. Un ítem puede estar **cerrado en contrato local** y **PARCIAL en paridad** a la vez.

### Matriz de cierre (Windows, checkout actual)

Puente entre inventario `W-*`, tablero `PAR-*` y registry. Ver también § [Contratos cerrados en este checkout](#contratos-cerrados-en-este-checkout-windows).

| ID | Contrato | E1 impl. | E2 PAR | E3 SEC/REL | Condición pendiente | Evidencia |
|----|----------|----------|--------|------------|---------------------|-----------|
| W-20260425-001 | Datos v1 | hecho | PARCIAL (PAR-001) | SEC-003, REL-001 | Cierre cross-repo persistencia; versionado | `arcade/engine/config/config.py`, [data_contract_windows_v1.md](../developer/data_contract_windows_v1.md) |
| W-20260425-002 | CLI flags | hecho | OK (PAR-002) | — | Área tablero «CLI» PARCIAL = VM/doc, no flags | `cli.py`, `doctor.py` |
| W-20260425-003 | Reset dos fases | hecho | PARCIAL (PAR-003) | — | Validación UX en VM (**W-OPS-001**) | `main.py` |
| W-20260425-004 | Hooks / historial | hecho | OK (PAR-004) | — | — | `input_history.py`, `extensions_runtime.py` |
| W-UPD-ZIP-001 | Update runtime ZIP | hecho | PARCIAL (PAR-005A) | SEC-001 | **No confundir:** E1 cerrado en `cli`; E2 bloqueado por `install_ops.extractall` | `cli.py`, `safe_zip_extract.py` vs `install/windows/install_ops.py` L56–57 |
| W-20260426-001 | Instalación | hecho | PARCIAL (PAR-006) | SEC-001 (payload install) | Revisión cruzada accesos; Inno legado no es evidencia única | `install/windows/` |
| W-OPS-003 | Producto en campo | pendiente | PARCIAL (PAR-005B) | OPS-002 | Canal release / comunicación usuario | `cli.py --update`, `constructor.md` |

## Propósito y límites del documento

- Registra **qué** se hace o debe hacerse, **por qué** importa y **en qué estado** está respecto a la paridad entre variantes.
- **No** describe procedimientos largos (comandos, pasos de build). Eso vive en la documentación de cada repo (p. ej. `README.md` en Linux; empaquetado Windows en `constructor.md` cuando exista en `hud_owerlay`).
- **Paridad** = equivalencia **funcional y contractual observable** (no equivalencia interna de implementación). Ver [audit_contract_v1.md](../developer/audit_contract_v1.md) § Modelo de paridad por capas.
- Linux (`hud_overlay`) define **invariantes** upstream; Windows (`hud_owerlay`) hace **adaptación contractual** del mismo producto (no «copiar Linux» línea a línea).
- Clasificación por sistema: [parity_matrix.md](parity_matrix.md) (`tipo`, `paridad`, `drift_permitido`, `motivo_plataforma`).

## Registro por bloques (antes / después / motivo)

Para mejoras alineadas al plan unificado y para que el historial sea auditable:

- Cada **bloque** de trabajo cerrado (o cada entrega lógica equivalente a un PR) debe quedar anotado con **cuatro columnas**: **Bloque** (nombre corto), **Antes**, **Después**, **Motivo** (una sola línea de texto).
- Si el cambio toca paridad entre repos: en la misma fila o justo debajo, indicar **PAR-*** afectado y, si aplica, **transición de estado** del tablero (p. ej. `ROTO → PARCIAL`).
- Las filas pueden vivir **aquí** (tabla acumulativa) y/o repetirse como línea en **Historial de sincronización** con el mismo criterio.

### Plantilla (copiar y rellenar)

| Bloque | Antes | Después | Motivo |
|--------|-------|---------|--------|
| | | | |

### Ejemplo de redacción (formato; no afirma un hecho concreto hasta fechar la implementación)

| Bloque | Antes | Después | Motivo |
|--------|-------|---------|--------|
| Datos canon + espejo perfiles | Un solo `USER_DIR` bajo `~/.local/share/...` para perfiles operativos. | Perfiles operativos bajo `PROJECT_ROOT/user/profiles/`; copia de respaldo en `~/.local/share/joystick_overlay/user/profiles/` tras cada guardado. | Portable + recuperación si se borra el árbol del proyecto. |

### Bloques previstos por el plan fusionado (rellenar al implementar)

| Bloque | Antes | Después | Motivo |
|--------|-------|---------|--------|
| Estilos e iconos (`mvs` / `cps` / `ns` / `ps` / `xbox`, `icon_pack_locked`) | `playstation`/`switch`/`xbox` sin packs dedicados. | Estilos canónicos + `icon_stem_for_label` / mapeos en `config`; menú sincroniza pack si no fijado. | PAR-001 estética HUD alineada a packs en disco. |
| Resolver y caché sin I/O en caliente | `resolve_icon` releía JSON en cada botón. | Caché de metadatos por perfil + rutas resueltas; invalidación en guardado. | Cumplir A.5 sin I/O repetida. |
| Índice de perfiles (FS fuente de verdad, esquema mínimo) | Índice con `path`; entradas huérfanas. | `profiles_index.json` solo `id`+`name`; reconciliación con carpetas bajo `user/profiles/`. | A.1: FS autoridad. |
| Nombre libre de perfil + menú Renombrar | Solo `name` implícito al crear. | Acción «Renombrar perfil» edita `name`; `id` sigue siendo carpeta. | A.2 UI sin tocar rutas. |
| Editor HUD: joystick y cada botón independientes (A.12) | Grupos `dirs_group` / `buttons_group` en `hud_layout_editor`. | `button_positions` por label + stick; `button_pixel_offsets` en render. | A.12 granularidad en pantalla. |
| Migración / reset / CLI / preflight | `USER_DIR` solo XDG; reset borraba todo. | Canon `PROJECT_ROOT/user/`; copia XDG→proyecto si falta índice; reset con `pre_reset_*`; bump `data_version` 3. | Híbrido C + A.7/A.8. |
| Pantalla «Backups locales» (bienvenida + menú) | Copias siempre antes de sobrescribir perfil. | Primera ejecución pregunta Si/No; si No avisa que puede activar en Configuración; `backups_enabled` en índice y toggle «Backups locales». | Consentimiento y control del usuario (PAR-UX backups). |
| Espejo XDG `.../joystick_overlay/user/profiles/` (opcional) | Espejo siempre tras cada guardado. | Misma bienvenida + toggle «Espejo datos sistema»; `xdg_mirror_enabled` en índice; si No no se escribe bajo `~/.local/share/...` (paridad ruta Windows en `%LOCALAPPDATA%\joystick_overlay\...`). | No romper convención XDG como ubicación posible; no obligar escritura fuera del proyecto. |
| README + ZIP perfiles (`bindings/`) | README y notas viejas: ZIP con `profile.json` + `icons/`; `hud_layout` solo en `profile.json`. | README documenta ZIP con `bindings/*.json` (cuatro nombres canónicos), metadato `profile_version` en export; HUD/iconos por formato en sidecars (`arcade/engine/profiles/`). | Documentación única para import/export y portado Windows. |
| Seguridad ZIP / FS / updater | `extractall` + chequeo debil; resolver con cwd; `cp -a` en update; sin lock al guardar indice. | `safe_zip_extract`; iconos import bajo `user/profiles/<id>/icons/`; `safe_paths` + resolver endurecido; `update.sh` scan + `cp -rL` + `flock`; `profiles_index.lock` al guardar; [security_model.md](../security/security_model.md). | Reducir ZIP slip / symlinks / traversal y carreras en datos de usuario. |
| Licencia GPLv3 + metadatos paquete | Sin `LICENSE` en raíz o sin `license` en `pyproject.toml`. | Archivo `LICENSE` (texto GPL-3) en raíz; `license = { file = "LICENSE" }` en `pyproject.toml`; `MANIFEST.in` incluye `LICENSE`; README enlaza a [LICENSE](../../LICENSE). | Redistribución y sdist completos para clones y Windows. |

## Ámbitos

| Variante | Repositorio / árbol | Rol de esta bitácora en cada checkout |
|----------|---------------------|----------------------------------------|
| Windows | `hud_owerlay`; producto **Joystick Overlay** | Inventario principal Windows; cola hacia Linux. |
| Linux | `hud_overlay` (slug Git); producto **Joystick Overlay**; rutas externas `joystick_overlay` | Inventario principal Linux; cola hacia Windows como adaptación contractual. |

---

## Gobernanza de auditoría y hallazgos técnicos

Normas y estado cross-repo (no sustituyen este documento):

| Documento | Rol |
|-----------|-----|
| [audit_contract_v1.md](../developer/audit_contract_v1.md) | Severidad P0–P3, capas canónica/adaptable/prohibida, ladder, plantilla |
| [findings_registry.md](findings_registry.md) | IDs globales SEC/REL/ARCH/OPS/DOC |
| [parity_matrix.md](parity_matrix.md) | Sistema × Linux × Windows (`matrix_version: 2`, columnas de capa) |
| [audit_report.md](audit_report.md) | Instantánea por commit (no sobrescribe PAR ni registry) |

**Reglas:**

- **`PAR-*`** = paridad de producto (tablero y pares más abajo).
- **`SEC-*` / `REL-*` / `ARCH-*` / `OPS-*` / `DOC-*`** = hallazgos técnicos globales; la bitácora solo **referencia** el ID, no redefine el problema.
- **`L-*` / `W-*`** = evidencia local o ítem de cola, no IDs de hallazgo global.
- Reclasificación **por sistema** (no por diff de código): [parity_matrix.md](parity_matrix.md) — campos `tipo` / `drift_permitido`.

### Hallazgos globales referenciados (activos en este checkout)

| ID | P | global_status | Aplica Windows | Registry |
|----|---|---------------|----------------|----------|
| SEC-001 | P0 | PARCIAL | Sí (`cli` seguro; `install_ops` con `extractall`) | [SEC-001](findings_registry.md#sec-001--pipeline-zip-inconsistente) |
| SEC-002 | P0 | PARCIAL | N/E (backend `keyboard`) | [SEC-002](findings_registry.md#sec-002--input_state-sin-sincronización) |
| SEC-003 | P1 | PARCIAL | Sí (mismo patrón lock migración) | [SEC-003](findings_registry.md#sec-003--lock-de-migración-no-atómico) |
| REL-001 | P1 | PARCIAL | Sí (`.joystick_version` vs `pyproject.toml`) | [REL-001](findings_registry.md#rel-001--versión-runtime--metadatos) |
| ARCH-002 | P2 | PARCIAL | Sí (`hud_layout_editor`) | [ARCH-002](findings_registry.md#arch-002--deuda-mantenibilidad-windows) |
| OPS-001 | P1 | PARCIAL | Sí (sin CI) | [OPS-001](findings_registry.md#ops-001--sin-cicd) |
| OPS-002 | P2 | PARCIAL | Sí (sin CHANGELOG raíz) | [OPS-002](findings_registry.md#ops-002--canal-release--changelog) |
| OPS-003 | P3 | PARCIAL | Sí (port sin commit) | [OPS-003](findings_registry.md#ops-003--higiene-repo--tooling) |
| DOC-001 | P2 | PARCIAL | Sí (layout docs) | [DOC-001](findings_registry.md#doc-001--drift-repository_layout-windows) |
| ARCH-001 | P2 | PARCIAL | N/E (monolitos Linux) | [ARCH-001](findings_registry.md#arch-001--monolitos-entrypoints-linux) |

### Anexo isomórfico (8 secciones)

Resumen → Restricciones → Hallazgos (registry) → Riesgo residual → Paridad (matrix) → Plan P0–P3 → Confianza → Estado release. Detalle en [audit_contract_v1.md](../developer/audit_contract_v1.md) § Estructura isomórfica.

---

## Estado global de paridad (tablero ejecutivo)

Lectura rápida para decidir prioridades de implementación y evitar desviaciones entre repos.

| Área | Estado | Impacto |
|------|--------|---------|
| Core (input history + hooks) | OK | CRÍTICO |
| Datos de usuario y versionado runtime | PARCIAL | CRÍTICO |
| Reset de datos en dos fases | PARCIAL | CRÍTICO |
| Actualización en campo (política de producto / PAR-005B) | PARCIAL | CRÍTICO |
| CLI de soporte | PARCIAL | MEDIO |
| Instalación y accesos de entrada | PARCIAL | MEDIO |
| Preflight UX (mensajes preventivos) | PARCIAL | BAJO |

### Semáforo de estados (obligatorio)

- `OK`: ambas variantes cumplen el mismo resultado de producto.
- `PARCIAL`: existe implementación en ambos lados, pero falta equivalencia funcional o cierre de producto.
- `ROTO`: solo una variante cumple, o la diferencia afecta directamente al usuario.

Para auditorías técnicas y dimensiones no evaluadas, usar además `PENDIENTE`, `N/E` y `DRIFT` según [audit_contract_v1.md](../developer/audit_contract_v1.md). El release readiness se expresa con el ladder (`LOCAL_READY` … `HARDENED`), no con veredictos sueltos («Condicionado», «no listo»).

**Tablero ejecutivo vs `PAR-*`:** el tablero por **área** es agregado (p. ej. «CLI de soporte» puede ser PARCIAL por VM/documentación aunque **PAR-002** esté OK en flags canónicos). No sustituye la tabla PAR ni la [Matriz de cierre](#matriz-de-cierre-windows-checkout-actual).

### Clasificación de impacto (obligatoria)

- `CRÍTICO` (Core parity): rompe comportamiento visible, soporte o continuidad del producto.
- `MEDIO` (Operational parity): afecta operación diaria (CLI, instalación, actualización básica).
- `BAJO` (Nice-to-have): mejoras de UX o robustez que no rompen el flujo principal.

## Pares de paridad (contrato ejecutable)

Esta tabla es la fuente de verdad para decidir trabajo cross-repo. Si un `PAR-*` está `ROTO`, no debe cerrarse sprint de paridad sin plan activo para ese par.

| ID | Windows | Linux | Estado | Impacto | tipo | drift_permitido | Nota |
|----|---------|-------|--------|---------|------|-----------------|------|
| PAR-001 | `W-20260425-001` | `L-20260425-001-P` | PARCIAL | CRÍTICO | Adapted | Sí | Persistencia lógica alineada; rutas AppData vs `user/` — ver matrix fila Persistencia. |
| PAR-002 | `W-20260425-002` | `L-20260425-002-P` | OK | MEDIO | Canonical | No | `--version`, `--show-reset-log` (E2 cerrado; área CLI tablero puede seguir PARCIAL por ops). |
| PAR-003 | `W-20260425-003` | `L-20260425-003-P` | PARCIAL | CRÍTICO | Canonical | No | Reset dos fases en código (E1); validación cruzada UX Windows pendiente (**W-OPS-001**). |
| PAR-004 | `W-20260425-004` | `L-20260425-004` | OK | CRÍTICO | Canonical | No | Contrato de eventos/hooks alineado (E1+E2 cerrados). |
| PAR-005A | `W-UPD-ZIP-001` / `cli --update` | `L-OPS-003-P-mechanics` | PARCIAL | CRÍTICO | Transitional | No | E1: cli + perfil seguros; E2: install `extractall` — **SEC-001**. No marcar OK hasta mitigar install. |
| PAR-005B | `W-OPS-003` (producto en campo) | `L-OPS-003-P-product` | PARCIAL | CRÍTICO | Canonical | No | Canal release / comunicación usuario (**OPS-002**). |
| PAR-006 | `W-20260426-001` | `L-20260426-001` | PARCIAL | MEDIO | Adapted | Sí | Instalación: `install/windows/` (Inno/`.bat` en `install/` = legado). |
| PAR-007 | `W-PAR-L004` | `L-PREFLIGHT` | PARCIAL | BAJO | Canonical | No | Preflight y mensajes preventivos. |

### Regla de ejecución de paridad

- Prioridad operativa fija: primero `CRÍTICO`, luego `MEDIO`, después `BAJO`.
- No cerrar iteración de paridad con `PAR-*` críticos en `ROTO` sin registrar decisión explícita en historial.
- Cada cambio en un repo debe actualizar, en la misma sesión, al menos: `PAR-*` afectado + estado de la cola cruzada (`A.3` o `B.3`).

### Regla de área PAR-005

- **PAR-005A** (mecánica) y **PAR-005B** (producto / actualización en campo) se evalúan por separado.
- El estado del área «Actualización en campo (política de producto)» sigue **PAR-005B**.
- PAR-005A debe estar **OK** antes de considerar cerrar PAR-005B en **OK**.

---

## Parte A — Windows (`hud_owerlay`)

### Contratos cerrados en este checkout (Windows)

Resumen ejecutivo (detalle en [Matriz de cierre](#matriz-de-cierre-windows-checkout-actual)). «Cerrado» aquí indica el **eje** cumplido, no cierre global del producto.

| Contrato | Estado declarado | Bloqueador único |
|----------|------------------|------------------|
| PAR-002 CLI flags | **Cerrado (E2 paridad)** | — |
| PAR-004 hooks / historial | **Cerrado (E1+E2)** | — |
| PAR-005A mecánica runtime ZIP | **E1 cerrado / E2 PARCIAL** | **SEC-001** (`install_ops.extractall`) |
| W-UPD-ZIP-001 (cli update) | **E1 cerrado** (no implica PAR-005A OK) | install sin `safe_zip_extract` |
| PAR-003 reset (código) | **E1 cerrado / E2 PARCIAL** | **W-OPS-001** (VM UX) |
| ZIP perfil import | **E1 cerrado** (política canónica) | — (`profile_export` → `extract_zip_safely`) |
| Acta 2026-04-27 bloques Linux | **Entrega histórica cerrada** | **SEC-001**, **REL-001** siguen abiertos en registry |

### A.1 Inventario por estado (solo qué)

En checkout **`hud_owerlay`**, la tabla siguiente es el inventario **Windows** en eje **E1** (`hecho` = implementado aquí; `pendiente` = ops, release o paridad frente a la cola L→W de la Parte B). Columna **E2** enlaza al tablero PAR. En Linux, esta Parte A es evidencia externa pendiente de contrastar.

**E1 — Hecho en repo (código y artefactos presentes)**

| ID | Qué | E2 PAR | Evidencia en `hud_owerlay` |
|----|-----|--------|----------------------------|
| W-20260425-001 | Persistencia Windows v1: `%LOCALAPPDATA%\joystick_owerlay\user\` (estado actual) o `user\` portable; manifiesto `install_manifest.json`; migración condicional desde `hud_owerlay`. El contrato observable debe alinearse con el branding **Joystick Overlay** sin confundir repositorio, `APP_ID` y ruta externa Linux. | PARCIAL (PAR-001) | `arcade/engine/config/config.py`, [data_contract_windows_v1.md](../developer/data_contract_windows_v1.md), `.joystick_version` |
| W-20260425-002 | CLI única: `run`, `config`, `tournament`, `doctor`, `--version`, `--show-reset-log`, `--update --zip`. | OK (PAR-002) | `cli.py`, `doctor.py` |
| W-20260425-003 | Reset de datos en dos fases: `--reset-data` (interactivo) y `--do-reset-data` (worker). | PARCIAL (PAR-003) | `main.py` (parser y rutas tempranas) |
| W-20260425-004 | Historial de input y runtime de extensiones con hook de evento integrado al lector de input. | OK (PAR-004) | `arcade/engine/core/input_history.py`, `extensions_runtime.py`, `maps/input_reader.py` |
| W-20260426-001 | Instalación Python bajo `install/windows/` (setup/uninstall/install_ops); legado Inno/`.bat` en `install/` solo referencia histórica. | PARCIAL (PAR-006) | `install/windows/`, `install/joystick_overlay.ico`; [parity_matrix](parity_matrix.md); **SEC-001** en payload install |
| W-UPD-ZIP-001 | Actualización desde ZIP con `safe_zip_extract` y whitelist; preserva `user/`. | PARCIAL (PAR-005A) | `cli.py`, `arcade/engine/utils/safe_zip_extract.py`, `arcade/engine/profiles/profile_export.py` |

**E1 — Pendiente ops/paridad**

| ID | Qué |
|----|-----|
| W-OPS-001 | Validación completa en VM Windows: build, instalación, desinstalación, reset y diagnóstico. |
| W-OPS-002 | Cierre de release: GUID del instalador, versión alineada instalador ↔ runtime, política AV si aplica. |
| W-OPS-003 | Política y UX de actualización **en campo** para quien no desarrolla (documentación, canal de ZIP/build, comprobaciones post-update); el script ZIP existe pero falta el cierre de producto. |
| W-PAR-L001 | Paridad **instalación**: revisión cruzada de accesos claros a HUD / config / torneo tras instalar (objetivo L-20260426-001). |
| W-PAR-L002 | Paridad **CLI / documentación**: revisión documental hecha 2026-05-18 (superficie CLI alineada); cierre con VM/documentación instalador pendiente. |
| W-PAR-L003 | Paridad **actualización**: alinear intención operativa entre `update_windows.bat`, instalador y lo documentado para Linux (objetivo L-20260426-003). |
| W-PAR-L004 | Opcional: **preflight** de instalación con mensajes claros si el entorno no es apto (espíritu de validación gráfica en Linux, sin copiar APIs). |

### A.2 Registro de ítems (plantilla largo plazo)

```text
[ID]  Estado: hecho | pendiente | descartado
      Cierre: E1-only | E1+E2 | bloqueado por SEC-NNN / REL-NNN
      Fecha: YYYY-MM-DD
      Qué: (una frase, resultado observable)
      Por qué: (negocio / riesgo / paridad)
      Portabilidad Linux: pendiente | en_progreso | portado | n/a | descartado
      Evidencia si hecho: ruta o módulo (no comandos)
```

**W-20260425-001** — Estado: `hecho` (Windows, Confirmado estático)  
Cierre: `E1-only` (PAR-001 PARCIAL; SEC-003 / REL-001 abiertos)  
Fecha: 2026-04-25; revisado 2026-05-18  
Qué: Persistencia de perfiles y metadatos bajo contrato Windows v1 (`APP_ID=joystick_owerlay`, manifiesto, `data_version` 5), con branding de producto **Joystick Overlay** como contrato visible.  
Por qué: Instalación en `Program Files` no debe requerir escritura en runtime.  
Portabilidad Linux: `portado` (Linux: `PROJECT_ROOT/user/` + espejo XDG opcional).  
Evidencia Windows: `arcade/engine/config/config.py`, [data_contract_windows_v1.md](../developer/data_contract_windows_v1.md), `.joystick_version`.

**W-20260425-002** — Estado: `hecho` (Windows, Confirmado estático)  
Cierre: `E1+E2` (PAR-002 OK)  
Fecha: 2026-04-25; revisado 2026-05-18  
Qué: Diagnóstico y utilidades CLI (`run`, `config`, `tournament`, `doctor`, `--version`, `--show-reset-log`, `--update --zip`).  
Por qué: Soporte y reproducibilidad.  
Portabilidad Linux: `portado` (`cli.py` con `run|config|tournament|doctor`, `--help`, `--version`, `--show-reset-log`; `doctor.py` orientado a `/dev/input` y sesión gráfica).  
Evidencia Windows: `cli.py`, `doctor.py`.

**W-20260425-003** — Estado: `hecho` (código); validación UX `pendiente` (VM)  
Cierre: `E1-only` (PAR-003 PARCIAL hasta W-OPS-001)  
Fecha: 2026-04-25; revisado 2026-05-18  
Qué: Borrado seguro de datos con `--reset-data` y worker `--do-reset-data`.  
Por qué: Evitar bloqueos de archivos y pérdida de foco en captura.  
Portabilidad Linux: `portado` (`main.py`: `--reset-data`, `--do-reset-data`; ver matriz [`reset_matrix.md`](../developer/reset_matrix.md)).  
Evidencia Windows: `main.py` (parser temprano). Cierre PAR-003: W-OPS-001.

**W-20260425-004** — Estado: `hecho` (Windows, Confirmado estático)  
Cierre: `E1+E2` (PAR-004 OK)  
Fecha: 2026-04-25; revisado 2026-05-18  
Qué: Trazabilidad de input y extensión por hooks sin acoplar a la UI.  
Por qué: Base para análisis y extensiones.  
Portabilidad Linux: `portado`.  
Evidencia Windows: `arcade/engine/core/input_history.py`, `extensions_runtime.py`, `maps/input_reader.py`.

**W-20260426-001** — Estado: `hecho` (Windows, Confirmado estático)  
Cierre: `E1-only` — **bloqueado por SEC-001** en payload install; PAR-006 PARCIAL  
Fecha: 2026-04-26; revisado 2026-05-18  
Qué: Instalador Python (`install/windows/`: setup, uninstall, install_ops); legado Inno/`.bat` en `install/` no es evidencia primaria.  
Por qué: Un solo lugar para empaquetado Windows acorde al port.  
Portabilidad Linux: `n/a` (`install.sh` + `.desktop` en Linux).  
Evidencia Windows: `install/windows/`, `install/joystick_overlay.ico`. Riesgo: **SEC-001** en extracción payload install.

**W-UPD-ZIP-001** — Estado: `hecho` (Windows, Confirmado estático)  
Cierre: `E1-only` — **bloqueado por SEC-001** en install; PAR-005A PARCIAL (no confundir con cierre global de update)  
Fecha: 2026-04-26; revisado 2026-05-18  
Qué: Actualización desde ZIP con `extract_zip_safely`, whitelist y preservación de `user/`.  
Por qué: Base técnica PAR-005A en runtime; W-OPS-003 cubre política de producto.  
Portabilidad Linux: mecánica distinta (`update.sh`; ver SEC-001 Linux).  
Evidencia Windows: `cli.py`, `arcade/engine/utils/safe_zip_extract.py`.

**W-PAR-L001** — Estado: `pendiente`  
Fecha: —  
Qué: Revisión cruzada post-instalación: usuario localiza HUD, config y torneo con la misma claridad relativa que en Linux.  
Por qué: Paridad de producto entre repos.  
Portabilidad Linux: ver cola B.3 (`L-20260426-001`).  
Evidencia: — (checklist / notas de release).

**W-PAR-L002** — Estado: `revisión documental hecha` (VM instalador pendiente)  
Fecha: 2026-05-18  
Qué: Superficie CLI alineada con Linux (`run`, `config`, `tournament`, `doctor`, flags documentados).  
Por qué: PAR-002 OK en tablero; cierre operativo con README/instalador en VM.  
Portabilidad Linux: ver cola B.3 (`L-20260426-002`).  
Evidencia Windows: `cli.py`, `README.md`, `docs/user/`.

**W-PAR-L003** — Estado: `pendiente`  
Fecha: —  
Qué: Revisión cruzada del flujo operativo de actualización (ZIP, instalador, mensajes al usuario).  
Por qué: Paridad de intención con `update.sh` / UI Linux.  
Portabilidad Linux: ver cola B.3 (`L-20260426-003`).  
Evidencia: —

**W-PAR-L004** — Estado: `pendiente` (opcional)  
Fecha: —  
Qué: Preflight de instalación o primer arranque con mensajes claros si el entorno no es apto.  
Por qué: Reducir soporte silencioso.  
Portabilidad Linux: ver B.3 (`L-PREFLIGHT`).  
Evidencia: —

**W-OPS-001** — Estado: `pendiente` (código listo; requiere build nuevo en VM)  
Fecha: 2026-05-26  
Qué: Cierre de validación manual en entorno Windows real tras correcciones reportadas por testers.  
Por qué: Garantía antes de distribución.  
Hallazgos testers (2026-05): crash `evdev` al arranque; crash `map_keys` sin `profile_id`/`format_key`; ventana no redimensionable.  
Criterios de cierre: `python main.py` sin `evdev`; mapeo teclado/joystick completo; ventana maximiza/redimensiona (sin toggles WM en Config); `pytest tests/` verde.  
Acción release: nuevo `release.zip` según `constructor.md` §2–3 (reemplaza copia `joystick_owerlay` anterior).  
Portabilidad Linux: `n/a`.  
Evidencia: `CHANGELOG.md` [Unreleased] Windows; `tests/test_maps_import_win32.py`.

**W-OPS-002** — Estado: `en_progreso`  
Fecha: 2026-05-26  
Qué: Identidad de instalación y versión publicada alineadas con política de release.  
Por qué: Upgrades y soporte.  
Portabilidad Linux: `n/a`.  
Evidencia: `.joystick_version` / `pyproject.toml` / `version.txt` → 0.3.2; `check_version_alignment.py` en CI.

**W-GATE-032** — Estado: `en_progreso` (código; Fase 4 humano pendiente)  
Fecha: 2026-05-26  
Qué: Gate release Windows 0.3.2 — SEC-001 install, SEC-003 lock, REL-001, CI, `update_overlay` vía `cli --update --zip`, política Win32 sin WM tiling, ARCH-002 B (`render/profile_config/`).  
Por qué: Paridad contractual Adapted frente a Linux `a19edb8`.  
Evidencia: `findings_registry.md`, `parity_matrix.md`, `CHANGELOG.md` [0.3.2] Windows.

**W-OPS-003** — Estado: `pendiente` (producto en campo; PAR-005B)  
Fecha: —  
Qué: Política de actualización para usuarios finales (canal ZIP/build, comunicación, post-update).  
Por qué: W-UPD-ZIP-001 cubre mecánica runtime; PAR-005B sigue PARCIAL.  
Portabilidad Linux: `en_progreso` (L-OPS-003-P).  
Evidencia Windows: `cli.py --update --zip`, `constructor.md`, `docs/user/installation.md`.

### A.3 Cola Windows → Linux (qué portar; sin cómo)

*Criterios de cierre, verificación y fechas: ver cola inversa **B.3** (Linux → Windows). Esta tabla resume intención W→L sin duplicar columnas.*

| ID origen | Qué debe existir en Linux | Estado cola |
|-----------|---------------------------|-------------|
| W-20260425-001 | Misma política de datos de usuario y versión coherente con instalación Linux. | En progreso (PAR-001; ver B.3) |
| W-20260425-002 | Misma superficie de diagnóstico y flags de soporte acordados donde aplique. | Portado (Linux); revisión doc Windows — PAR-002 OK |
| W-20260425-003 | Misma semántica de reset en dos fases. | Portado (Linux); validación cruzada Windows — PAR-003 / B.3 |
| W-20260425-004 | Mismo contrato de evento e historial + hooks. | Portado |
| W-20260426-001 | — | n/a |
| W-UPD-ZIP-001 | Equivalente funcional de aplicar ZIP acotado (si aplica al modelo de release Linux). | PARCIAL mecánica Windows (SEC-001 install); PAR-005B pendiente |
| W-OPS-003 | Equivalente funcional de actualización operativa para usuarios finales. | En progreso (PAR-005B; ver B.3) |

---

## Parte B — Linux (`joystick_overlay`)

### B.1 Inventario por estado (solo qué; verificado en este árbol)

Esta sección es la **base Linux** que se pasa a Windows como contrato observable. En `hud_owerlay`, no debe leerse como instrucciones para copiar implementación, sino como lista de invariantes y evidencias Linux a contrastar con la adaptación Windows.

**Hecho**

| ID | Qué |
|----|-----|
| L-20260426-001 | Instalación orientada a usuario: `install.sh` (venv, launcher **`joystick-overlay`**, `.desktop`, icono `joystick_overlay.ico`, variables `JOYSTICK_OVERLAY_ASSUME_GRAPHICS` / `JOYSTICK_DESKTOP_TERMINAL`). |
| L-20260426-002 | Lanzamiento unificado: `run.sh` → `cli.py` con comandos `run`, `config`, `tournament`, `doctor`, `-h`/`--help`. |
| L-20260426-003 | Actualización: `update.sh` (git y modo ZIP con whitelist); desde UI «Actualizar overlay» (`render/profile_config_menu.py`). |
| L-20260425-004 | Historial de input y hooks (`core/input_history.py`, `core/extensions_runtime.py`, integración en `main.py`). |
| L-RUNTIME-V | Archivo `.joystick_version` en raíz como referencia de versión runtime (contrato [`../developer/data_contract_v1.md`](../developer/data_contract_v1.md); README raíz). |

**Pendiente / parcial (paridad con Windows u ops)**

| ID | Qué |
|----|-----|
| L-20260425-001-P | Linux: canon `PROJECT_ROOT/user/` + `.data_version` y migraciones cerrados; pendiente cierre PAR-001 cross-repo (Windows: rebranding + espejo `%LOCALAPPDATA%`). |
| L-20260425-002-P | Resuelto en Linux: `cli.py` ya incluye `--version` y `--show-reset-log`; validar espejo documental en Windows. |
| L-20260425-003-P | Hecho en código Linux (reset dos fases); validación cruzada Windows pendiente (PAR-003). |
| L-OPS-003-P | Política de actualización en campo para usuarios sin git (ZIP documentado; falta cierre ops tipo W-OPS-003). |

### B.2 Registro de ítems Linux (plantilla)

**L-20260426-001** — Estado: `hecho`  
Fecha: 2026-04-26  
Qué: Instalación accesible (launcher + menú + comprobaciones de entorno gráfico).  
Por qué: Paridad funcional con «instalado y localizable» en Windows.  
Portabilidad Windows: `pendiente` (revisión cruzada de accesos equivalentes).  
Evidencia: `install.sh`, `install/joystick-overlay.desktop`, `install/joystick-overlay-config.desktop`, `install/joystick-overlay-tournament.desktop`, `install/joystick_overlay.ico`.

**L-20260426-002** — Estado: `hecho`  
Fecha: 2026-04-26  
Qué: Punto de entrada CLI para ejecutar HUD, config, torneo y doctor.  
Por qué: Paridad con superficie operativa Windows.  
Portabilidad Windows: `n/a` (misma idea, otra forma).  
Evidencia: `run.sh`, `cli.py`, `doctor.py`.

**L-20260426-003** — Estado: `hecho`  
Fecha: 2026-04-26  
Qué: Actualización del código sin mezclar datos sensibles por defecto (whitelist / git).  
Por qué: Paridad de intención con W-OPS-003.  
Portabilidad Windows: `pendiente` (alinear política con `update_windows.bat` / instalador).  
Evidencia: `update.sh`, `render/profile_config_menu.py`.

**L-20260425-004** — Estado: `hecho`  
Fecha: 2026-04-25  
Qué: Historial estructurado y hooks de extensión en el loop de input.  
Por qué: Paridad con W-20260425-004.  
Portabilidad Windows: `portado` (origen Windows; mantener contrato).  
Evidencia: `core/input_history.py`, `core/extensions_runtime.py`, `main.py`, `maps/input_reader.py`.

**L-20260425-001-P** — Estado: `hecho (Linux); paridad cross-repo pendiente`  
Fecha: 2026-05-03 (canon Linux); — (cierre PAR-001)  
Qué: Canon operativo bajo `PROJECT_ROOT/user/`, versionado (`data_version`, `.joystick_version`), migraciones y espejo opcional XDG; equivalente funcional a W-20260425-001.  
Por qué: Contrato portable + recuperación; PAR-001 sigue PARCIAL hasta rebranding y espejo AppData en Windows.  
Portabilidad Windows: `pendiente` (rebranding checklist § «Checklist rebranding»).  
Evidencia Linux: `config/config.py`, `core/data_migrations.py`, `profiles/profile_store.py`, acta 2026-04-27.

**L-20260425-002-P** — Estado: `hecho (cerrado en código)`  
Fecha: 2026-05-03  
Qué: Flags CLI `--version` y `--show-reset-log` alineados con Windows.  
Por qué: Soporte homogéneo entre variantes.  
Portabilidad Windows: `hecho` (asumido en Windows).  
Evidencia: `cli.py` (`get_runtime_version`, `RESET_LOG_PATH`).  
Nota histórica: [OBSOLETO] Texto anterior afirmaba «ausencia en cli.py»; corregido por verificación de código.

**L-20260425-003-P** — Estado: `hecho (cerrado en código)`  
Fecha: 2026-05-03  
Qué: Reset de datos en dos fases (`--reset-data` / `--do-reset-data`).  
Por qué: Misma semántica de seguridad operativa.  
Portabilidad Windows: `hecho` (asumido en Windows); **pendiente validación cruzada Windows** para PAR-003.  
Evidencia: `main.py` (parser temprano y `_do_reset_data`).  
Nota histórica: [OBSOLETO] Texto anterior afirmaba ausencia de `reset-data` en `main.py`; corregido por verificación de código.

**L-OPS-003-P** — Estado: `en_progreso`  
Fecha: —  
Qué: Cierre de política de actualización para usuarios finales (más allá de git/zip en repo).  
Por qué: Paridad con W-OPS-003.  
Portabilidad Windows: `pendiente`.  
Evidencia: `update.sh`, UI de actualización; falta definición de release Linux.

### B.3 Cola Linux → Windows (qué revisar en Windows; sin cómo)

*Ningún ítem sin **criterio de cierre** explícito.*

| ID / objetivo | Qué revisar en Windows | Criterio de cierre | Verificación | Estado cola | Fecha |
|---------------|------------------------|--------------------|--------------|-------------|-------|
| L-20260426-001 | Accesos HUD / config / torneo tras instalación. | Menú/accesos visibles **Joystick Overlay**: abrir ejecutable principal, configuración y torneo sin línea de comandos | Instalador + acceso directos | Pendiente revisión cruzada | — |
| L-20260426-002 | CLI / entradas de producto. | Misma superficie observable: comandos equivalentes **`joystick-overlay`** y subcomandos documentados (`config`, `tournament`, `doctor`, `--version`, `--help`) | Lista en README instalador vs `doctor` | Pendiente revisión cruzada | — |
| L-20260426-003 | Update + logs desde UI donde exista. | `Actualizar overlay` no borra `USER_DIR` del proyecto; log en `user/update.log` o ruta documentada | Prueba manual + lectura log | Pendiente revisión cruzada | — |
| L-20260426-002 (install UX) | Preflight instalación. | Mensaje claro si no hay sesión gráfica (equivalente funcional a `install.sh`, no igualdad API) | Instalador en máquina headless-safe | Pendiente revisión cruzada | — |
| L-PREFLIGHT | Validación previa arranque. | Equivalente espíritu `install.sh` / doctor | Lista smoke | Opcional | — |

---

## Historial de sincronización (solo hitos)

| Fecha | Qué |
|-------|-----|
| 2026-04-26 | Definición de bitácora solo-QUÉ; inventario Windows; colas explícitas. |
| 2026-04-26 | Ajuste por checkout: Parte B inventariada desde `hud_overlay`; colas W↔L alineadas a evidencia de código; ítems paridad CLI/reset/datos. |
| 2026-04-26 | Parte A Windows: tablas hecho/pendiente con evidencia en `hud_owerlay`; ítems W-UPD-ZIP-001 y W-PAR-L*; repos explícitos como árboles distintos. |
| 2026-04-26 | Impacto: PAR-001 \| Transición: ROTO -> PARCIAL \| Evidencia: `config/config.py`, `core/data_migrations.py`, `profiles/profile_store.py`. |
| 2026-04-26 | Impacto: PAR-002 \| Transición: PARCIAL -> OK \| Evidencia: `cli.py`. |
| 2026-04-26 | Impacto: PAR-003 \| Transición: ROTO -> PARCIAL \| Evidencia: `main.py`, `cli.py`. |
| 2026-04-26 | Impacto: PAR-005 \| Transición: ROTO -> PARCIAL \| Evidencia: `update.sh`, `render/profile_config_menu.py`. *(Histórico; ver 2026-05-13 para desglose PAR-005A/B.)* |
| 2026-04-27 | Bloque: gobernanza de bitácora \| Antes: solo ítems narrativos y tablero PAR \| Después: sección «Registro por bloques» con plantilla antes/después/motivo y tabla de bloques previstos del plan fusionado \| Motivo: trazabilidad por entrega y alineación con `control_estilo_e_iconos_736cb9a6.plan.md`. |
| 2026-05-13 | Impacto: PAR-005 \| Transición: mecánica ROTO→**OK** (**PAR-005A**); producto en campo sigue **PARCIAL** (**PAR-005B**). Tablero «Actualización en campo» = PAR-005B, no ROTO global. Evidencia: `update.sh`, `safe_zip_extract`, `profiles_index.lock`, [security_model.md](../security/security_model.md). |
| 2026-04-27 | Acta auditoría híbrida (`auditoría_todos_híbridos`): cierre de brechas shell/docs + tests de rutas; ver tabla siguiente. |
| 2026-05-03 | Rebranding producto **Joystick Overlay** en Linux canon: ejecutable/lanzador **`joystick-overlay`**, rutas externas `joystick_overlay`, archivo **`.joystick_version`**, variables **`JOYSTICK_*`**, `.desktop`/icono instalación; docs en **`docs/`** (contrato, matriz reset, esta bitácora). **Sin** migración automatizada desde rutas `hud_overlay`/`hud-overlay`/`HUD_*`; ver `docs/developer/data_contract_v1.md` §6. |
| 2026-05-03 | Seguimiento Windows (`hud_owerlay`): adaptar branding al contrato observable (binario **`joystick-overlay`**, rutas **`%LOCALAPPDATA%\joystick_overlay`** o equivalente acordado, instalador, iconos `.ico`, texto UI). Lista de chequeo técnico mínimo: (1) grep sin `hud-overlay` residual en lanzadores; (2) contrato datos Windows alineado donde aplique; (3) no reintroducir rescate desde árboles antiguos `hud_overlay` si el contrato vetado así. |
| 2026-05-13 | README reestructurado (hitos, usuario/streamer, ZIP **`bindings/`**); endurecimiento seguridad (ZIP perfil, resolver, `update.sh`, `flock`); sección README «Seguridad y archivos no confiables»; [security_model.md](../security/security_model.md); `tests/test_zip_security.py`; hitos narrativos archivados en [Archivo README (hitos antiguos)](#archivo-readme-hitos-antiguos). |
| 2026-05-14 | `LICENSE` (GPL-3) en raíz; `pyproject.toml` declara licencia vía archivo `LICENSE`; `MANIFEST.in` incluye `LICENSE`; README enlaza a licencia y corrige markdown (`bindings/`, modos de captura, `XDG_*` / `JOYSTICK_*`, tabla de entrypoints). |
| 2026-05-18 | Gobernanza auditoría isomórfica (Linux `b31d5d7`) \| Antes: PAR + informe con vocabulario propio \| Después: `audit_contract_v1`, `findings_registry`, `parity_matrix` en `docs/` \| Motivo: IDs SEC globales y comparación sin sesgo. |
| 2026-05-18 | **Port Windows** en `hud_owerlay`: `arcade/engine/`, `data_contract_windows_v1`, instalador `install/windows/`, CLI `joystick-overlay`. |
| 2026-05-18 | **Fase 2 handoff:** bitácora fusionada desde Linux; Parte A revisada contra árbol Windows; `body/` consumida y retirada. |
| 2026-05-22 | Bloque: contratos y cierres explícitos \| Antes: mezcla `hecho`/`OK`/SEC sin ejes \| Después: audit_contract **v1.1**, parity_matrix **v2**, § Jerarquía + Matriz de cierre + columnas PAR `tipo`/`drift` \| Motivo: cerrados mal interpretados (p. ej. W-UPD-ZIP-001 vs PAR-005A). Commit ref. `5dd784e`. |
| 2026-05-25 | Corrección para traslado a Windows \| Antes: mezcla de slug real, rutas externas y producto en la Parte Linux/Windows \| Después: `hud_overlay`/`hud_owerlay` como repos, `joystick_overlay` como ruta externa Linux, Parte B marcada como base Linux verificable \| Motivo: copiar bitácora a Windows sin invertir IDs ni confundir implementación con contrato. |
| 2026-05-26 | **Fase 2 cierre documental** \| `linux_ref` → `a19edb8` (0.3.2); repos en `windows_parity_rollout.md`; `parity_matrix` + `findings_registry` sincronizados desde Linux \| Evidencia W: SEC-001 `install_ops.extractall` L56–57; SEC-003 lock no atómico; REL-001 drift versión; ARCH-002 `run_hud_layout_editor` ~409 LOC \| Gate documental: comparación L↔W solo matrix+registry OK. |

---

## Checklist rebranding para Windows (`hud_owerlay`)

Aplicar en el repo Windows al adaptar el canon observable Linux:

1. Exponer ejecutable/lanzador visible **`joystick-overlay`** y actualizar instalador/bat con semántica equivalente a Linux, no implementación idéntica.
2. Rutas AppData alineadas al contrato Windows vigente; si se cambia a `joystick_overlay`, actualizar [`data_contract_windows_v1.md`](../developer/data_contract_windows_v1.md), `APP_ID`, instalador y migración en la misma entrega.
3. Archivo/o versión runtime **`.joystick_version`** (sin depender de `.hud_version`).
4. Prefijos **`JOYSTICK_`** para variables entorno públicas instalador/doctor.
5. Íconos y `.desktop`/accesos con nombre visible **Joystick Overlay**.

---

## Acta: auditoría `config-hybrid-storage` y `migrations-main-cli-tests` (2026-04-27)

Referencia: criterios del plan de auditoría (todos híbridos); el acta vive aquí para no duplicar el fichero del plan.

| Todo / ámbito | Veredicto | Evidencia | Seguimiento |
|---------------|-----------|-----------|---------------|
| **config-hybrid-storage** (runtime) | Completado | `config/config.py`: `PROJECT_USER_DIR`, `USER_DIR`, `get_user_dir`, `BACKUP_PROFILES_ROOT`, `ensure_contract_dirs`. Consumidores sin canon XDG hardcodeado como operativo. | Ninguno. |
| **config-hybrid-storage** (shell/docs) | Cerrado en esta entrega | `update.sh`: `USER_DIR="$BASE_DIR/user"`, `UPDATE_LOG` bajo ese árbol (alineado con `UPDATE_LOG_PATH`). `README.md`: ruta de log de actualización documentada como `user/update.log` + nota de espejo XDG. | Revisar si otros `.md` fuera del repo deben reflejar lo mismo. |
| **migrations-main-cli-tests** (Python) | Completado | `core/data_migrations.py`, `main.py`, `cli.py`, `doctor.py`, `configure.py`, `tournament.py` usan constantes de `config`. | Ninguno. |
| **migrations-main-cli-tests** (tests) | Completado | `tests/test_config_paths.py`: `get_user_dir` resuelve a `PROJECT_ROOT/user`; distinto de `BACKUP_PROFILES_ROOT`. `tests/test_hud_layout.py` incluye layout y rejilla MVS 8. | Ejecutar `python tests/test_config_paths.py` y `python tests/test_hud_layout.py` en CI o local al cambiar rutas. |
| Rutas legacy en código | Sin canon XDG como `USER_DIR` en `.py` / `.sh` | `_external_data_root()` usa **`joystick_overlay`** (espejo). Sin rescate automatizado rutas HUD antiguas (contrato v1 §6). | Ver `README.md` + [`data_contract_v1.md`](../developer/data_contract_v1.md). |
| UI menú + layout 4A (2026-05) | Renombre in-game **Joystick Overlay** / **Configuración** / **Salir**; caption `WINDOW_CAPTION_APP`; perfil `layout_four_variant_4a` (TAB en Dispositivos con 4 botones). | Agente no ejecuta pytest ni overlay; validar menú, TAB y HUD 4 vs 4A en local. | `main.py`, `config.py`, `profile_config_menu.py`, `hud_layout.py`. |

---

## Archivo README (hitos antiguos)

Texto conservado del README anterior (referencia histórica; el estado operativo está en Parte B y en el Historial).

### (Junio 2025) Cosas arregladas

Se redimensionó el tamaño de la ventana del fightstick. Se corrigió el tamaño de las letras y la interfaz acorde al tamaño de la ventana. Se corrigió el error de `main.py` (no cargaba `key_bindings.json`); ya no era necesario remapear en la opción del teclado salvo que se eliminara el archivo, igual que `joystick_bindings.json` (ambos en `json/` en esa época).

### (Agosto 2025) Cosas arregladas

Se arregló parcialmente la transparencia (necesita filtros como en OBS). Se mejoró el código: cada ventana se puede cerrar con el foco o con Esc. Se dio utilidad a `utils.py` para configuraciones repetidas. Se implementó un entorno virtual y `requirements.txt`.

### (Marzo 2026) Actualización

Apartado de fuente monoespaciada (`JetBrainsMono`, `FiraCode`, `Hack`; por defecto JetBrainsMono). UI en regular y etiquetas de botones en negrita. Fallback de fuente si falta el archivo local. Estilo PlayStation sin icono: abreviaciones (SQ, TRI, O, X, R1, L1, etc.). Opción «Seleccionar…» para icono con selector nativo Linux y validación máx. 512×512.

**Layout Hitbox y perfiles ZIP (marzo 2026 en README):** direccionales en curva descendente y botones de acción en curva ascendente; exportar/importar ZIP desde configuración con resolución de conflictos. Análisis de complejidad con `python tests/run_cyclomatic.py` (umbral CC≤10).

---

## Referencia «cómo» (fuera de esta bitácora)

- Linux: `README.md` (instalación, doctor, actualización, **Para el streamer** / OBS, tabla de hitos, [LICENSE](../../LICENSE)); contrato datos [`data_contract_v1.md`](../developer/data_contract_v1.md); índice [`README` de esta carpeta](../README.md) (antes `docs/INDEX.md`).
- Windows: [`README.md`](../../README.md), [`constructor.md`](../../constructor.md), contrato [`data_contract_windows_v1.md`](../developer/data_contract_windows_v1.md); índice [`docs/README.md`](../README.md).
