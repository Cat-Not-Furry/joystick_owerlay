# Constructor de empaquetado e instalador (Windows)

Producto: **Joystick Owerlay**. Estructura: `arcade/engine/` + entrypoints en raíz. Contrato de datos: [docs/developer/data_contract_windows_v1.md](docs/developer/data_contract_windows_v1.md).

## 1) Prerrequisitos

- Python 3.9+ (misma versión que `requirements.txt`)
- `pip install -r requirements.txt`
- `pip install pyinstaller==6.11.1`
- tkinter (incluido en CPython Windows)

## 2) Build aplicación (PyInstaller)

```bat
pyinstaller main.py ^
  --name joystick-overlay ^
  --onedir --noconsole --clean ^
  --paths arcade\engine ^
  --add-data "arcade\assets;arcade\assets" ^
  --add-data "configs;configs" ^
  --hidden-import=tkinter ^
  --hidden-import=keyboard
```

Salida: `dist\joystick-overlay\joystick-overlay.exe`

Incluir en la carpeta de distribución: `.joystick_version`, `install\joystick_overlay.ico`

## 3) Payload para instalador

Empaquetar el contenido de `dist\joystick-overlay\` más el árbol de proyecto necesario en `release.zip` (whitelist alineada a `cli.py --update`):

- `arcade/`, `configs/`, `main.py`, `cli.py`, `configure.py`, `tournament.py`, `doctor.py`, `engine_sys_path.py`, `install/`, `docs/`, `README.md`

## 4) Instalador Python (sustituye Inno)

**LEGACY:** `install\installer.iss` (Inno) — no usar salvo referencia.

Instalador gráfico: `install\windows\setup_wizard.py`

```bat
pyinstaller install\windows\setup_wizard.py --name joystick-overlay-setup --onefile --noconsole
```

Desinstalador:

```bat
pyinstaller install\windows\uninstall_wizard.py --name joystick-overlay-uninstall --onefile --noconsole
```

Copiar `joystick-overlay-uninstall.exe` junto a la app en el payload.

Uso:

```bat
joystick-overlay-setup.exe --zip release.zip
joystick-overlay-setup.exe --register-only
```

## 5) Rutas runtime

| Modo | Programa | Datos |
|------|----------|-------|
| Instalado | `C:\Program Files\Joystick Owerlay\` | `%LOCALAPPDATA%\joystick_owerlay\user\` |
| Portable | carpeta elegida | `<carpeta>\user\` |

Manifiesto: `install_manifest.json` junto al `.exe`.

## 6) CLI y soporte

```bat
joystick-overlay.exe
joystick-overlay.exe config
joystick-overlay.exe tournament
joystick-overlay.exe doctor
joystick-overlay.exe --version
joystick-overlay.exe --update --zip release.zip
```

Reset: `--reset-data`, `--do-reset-data` (ver [docs/developer/reset_matrix.md](docs/developer/reset_matrix.md)).

## 7) Verificación local (desarrollo)

```bat
set PYTHONPATH=arcade\engine
python tests\test_zip_security.py
python tests\test_config_paths.py
python doctor.py
```

Validación en VM (B.3): instalación, 3 accesos, update ZIP, desinstalación, portable + `setup --register-only`.
